#define _GNU_SOURCE
/* P780 perf permission probe 0.1.0. Counting ONLY, self thread, user mode.
 * No sampling, mmap, address output, futex operations, or privilege changes.
 * SPDX-License-Identifier: MIT
 */
#include <errno.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <sys/utsname.h>
#include <time.h>
#include <unistd.h>

static uint64_t ns(clockid_t clock) {
    struct timespec t;
    if (clock_gettime(clock, &t) != 0) return 0;
    return (uint64_t)t.tv_sec * UINT64_C(1000000000) + (uint64_t)t.tv_nsec;
}
static void failure(const char *stage, int err) {
    printf("failure_stage=%s\nerrno=%d\nerror=%s\n", stage, err, strerror(err));
}
int main(int argc, char **argv) {
    (void)argv;
    setvbuf(stdout, NULL, _IONBF, 0);
    puts("P780 perf permission probe 0.1.0");
    puts("scope=self-thread user-only software CPU clock counting");
    puts("sampling=off\nkernel_addresses=not_collected\nprivilege_changes=none");
    puts("NOT a vulnerability test; NOT root; NOT a GhostLock compatibility test.");
    if (argc != 1) { puts("result=INVALID_ARGUMENTS"); return 64; }
    printf("uid=%u\neuid=%u\n", (unsigned)getuid(), (unsigned)geteuid());
    struct utsname u;
    if (uname(&u) == 0) printf("machine=%s\nkernel=%s\n", u.machine, u.release);
    if (getuid() != 2000 || geteuid() != 2000) {
        puts("result=WRONG_CONTEXT\nexpected=Android ADB shell uid 2000; no root execution");
        return 65;
    }
    /* Hard process lifetime bound; process exit automatically closes perf FD. */
    alarm(4);
    struct perf_event_attr attr;
    memset(&attr, 0, sizeof(attr));
    attr.type = PERF_TYPE_SOFTWARE;
    /* ABI v0: 64 bytes, supported by Linux 5.4. All newer fields stay zero. */
    attr.size = PERF_ATTR_SIZE_VER0;
    attr.config = PERF_COUNT_SW_CPU_CLOCK;
    attr.disabled = 1;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.read_format = PERF_FORMAT_TOTAL_TIME_ENABLED | PERF_FORMAT_TOTAL_TIME_RUNNING;
    puts("event=PERF_COUNT_SW_CPU_CLOCK\npid_argument=0\ncpu_argument=-1\nattr_size=64");
    errno = 0;
    int fd = (int)syscall(SYS_perf_event_open, &attr, 0, -1, -1, PERF_FLAG_FD_CLOEXEC);
    if (fd < 0) {
        int e = errno;
        failure("perf_event_open", e);
        puts((e == EACCES || e == EPERM) ? "result=OPEN_DENIED" : "result=OPEN_ERROR");
        puts("cause=not_determined; no retry or permission workaround");
        return 10;
    }
    puts("open=PASS");
    if (ioctl(fd, PERF_EVENT_IOC_RESET, 0) != 0) {
        int e = errno; failure("reset", e); close(fd); puts("result=CONTROL_ERROR"); return 11;
    }
    if (ioctl(fd, PERF_EVENT_IOC_ENABLE, 0) != 0) {
        int e = errno; failure("enable", e); close(fd); puts("result=CONTROL_ERROR"); return 11;
    }
    uint64_t wall0 = ns(CLOCK_MONOTONIC), cpu0 = ns(CLOCK_THREAD_CPUTIME_ID);
    volatile uint64_t accumulator = 1;
    unsigned iterations = 0;
    int clock_error = !wall0 || !cpu0;
    while (!clock_error && iterations < 20000) {
        for (unsigned j = 0; j < 10000; ++j)
            accumulator = accumulator * UINT64_C(6364136223846793005) + 1;
        ++iterations;
        uint64_t wall = ns(CLOCK_MONOTONIC), cpu = ns(CLOCK_THREAD_CPUTIME_ID);
        if (!wall || !cpu) { clock_error = 1; break; }
        if (cpu - cpu0 >= UINT64_C(200000000) || wall - wall0 >= UINT64_C(1000000000)) break;
    }
    if (ioctl(fd, PERF_EVENT_IOC_DISABLE, 0) != 0) {
        int e = errno; failure("disable", e); close(fd); puts("result=CONTROL_ERROR"); return 11;
    }
    struct { uint64_t count, time_enabled, time_running; } values = {0};
    ssize_t n = read(fd, &values, sizeof(values));
    int e = errno;
    int close_rc = close(fd);
    int close_errno = errno;
    alarm(0);
    if (close_rc != 0) {
        failure("close", close_errno); puts("result=CLOSE_ERROR"); return 14;
    }
    puts("close=PASS");
    if (n != (ssize_t)sizeof(values)) {
        if (n < 0) failure("read", e);
        printf("read_bytes=%ld\nresult=READ_ERROR\n", (long)n); return 12;
    }
    printf("counter_ns=%" PRIu64 "\ntime_enabled_ns=%" PRIu64
           "\ntime_running_ns=%" PRIu64 "\n", values.count, values.time_enabled, values.time_running);
    if (clock_error) { puts("result=WORKLOAD_CLOCK_ERROR"); return 13; }
    if (!values.count || !values.time_enabled || !values.time_running) {
        puts("result=OPEN_OK_COUNT_INCONCLUSIVE"); return 13;
    }
    puts("result=USER_COUNT_PASS");
    puts("meaning=self-thread user-only counting worked for this run");
    puts("kernel_sampling=UNTESTED\nregister_sampling=UNTESTED\nGhostLock=UNDETERMINED");
    return 0;
}
