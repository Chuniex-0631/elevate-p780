/* Standalone PAGE_FAULTS perf event count test. */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef __NR_perf_event_open
#define __NR_perf_event_open 241
#endif
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
int main(void) {
    struct attr_min a;
    memset(&a, 0, sizeof(a));
    a.type = 1;        /* SOFTWARE */
    a.size = 112;
    a.config = 2;      /* PAGE_FAULTS */
    int fd = (int)syscall(__NR_perf_event_open, &a, 0, -1, -1, 0);
    printf("fd=%d errno=%d %s\n", fd, errno, strerror(errno));
    if (fd < 0)
        return 1;
    int pages = 1888;
    size_t len = (size_t)pages * 4096;
    char *p = mmap(NULL, len, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    madvise(p, len, MADV_NOHUGEPAGE);
    for (int i = 0; i < pages; i++) p[(size_t)i * 4096] = 1;
    madvise(p, len, MADV_DONTNEED);
    uint64_t before = 0;
    read(fd, &before, 8);
    for (int i = 0; i < pages; i++) p[(size_t)i * 4096] = 2;
    uint64_t after = 0;
    ssize_t r = read(fd, &after, 8);
    printf("before=%llu after=%llu delta=%llu r=%zd\n",
           (unsigned long long)before, (unsigned long long)after,
           (unsigned long long)(after - before), r);
    return 0;
}
