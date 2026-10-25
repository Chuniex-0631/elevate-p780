/*
 * M1 probe: build a PI waiter chain and read the kernel stack of a blocked thread.
 *
 * Three threads on three PI mutexes:
 *   T1 holds M1
 *   T2 holds M2 and blocks on M1
 *   T3 holds M3 and blocks on M2
 * Then /proc/<pid>/task/<tid>/stack for T3 should show rt_mutex frames,
 * proving pi_blocked_on is set and the chain exists.
 *
 * Build (NDK, static, arm64):
 *   aarch64-linux-android30-clang -O2 -static -pthread m1_pi_chain.c -o m1_pi_chain
 * Run as the installd-domain shell:
 *   ./m1_pi_chain > /data/local/tmp/m1.log 2>&1
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

static pthread_mutex_t m1, m2, m3;

static void die(const char *what) {
    fprintf(stderr, "%s: %s\n", what, strerror(errno));
    exit(1);
}

static void dump_stack(const char *label, pid_t tid) {
    char path[128];
    snprintf(path, sizeof path, "/proc/self/task/%d/stack", tid);
    int fd = open(path, O_RDONLY);
    printf("=== %s (tid %d) ===\n", label, tid);
    if (fd < 0) {
        printf("  open failed: %s\n", strerror(errno));
        return;
    }
    char buf[4096];
    ssize_t n = read(fd, buf, sizeof buf - 1);
    if (n <= 0) {
        printf("  read failed: %s\n", strerror(errno));
    } else {
        buf[n] = 0;
        printf("%s", buf);
    }
    close(fd);
}

static void *holder(void *arg) {
    pthread_mutex_t *m = arg;
    pthread_mutex_lock(m);
    printf("holder: locked %p\n", (void *)m);
    sleep(30);
    return NULL;
}

int main(void) {
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
    pthread_mutex_init(&m1, &attr);
    pthread_mutex_init(&m2, &attr);
    pthread_mutex_init(&m3, &attr);

    pthread_t t1, t2, t3;
    if (pthread_create(&t1, NULL, holder, &m1)) die("create t1");
    sleep(1);
    printf("m1 held by tid %ld\n", (long)syscall(SYS_gettid));

    /* main thread takes m1's slot as the owner for the chain, then blocks t2/t3 */
    if (pthread_create(&t2, NULL, holder, &m2)) die("create t2");
    sleep(1);
    if (pthread_create(&t3, NULL, holder, &m3)) die("create t3");
    sleep(1);

    /* main thread blocks on m1 (held by t1), then t2/t3 are queued behind it */
    pthread_mutex_lock(&m1); /* blocks here while t1 sleeps */
    printf("unreachable\n");
    return 0;
}
