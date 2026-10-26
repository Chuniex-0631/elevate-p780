/* What kernel surfaces can the adb shell domain reach? (C probe, run as shell) */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/perf_event.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <unistd.h>

static void show(const char *name, long rc, int err) {
    printf("%-22s -> %ld errno=%d (%s)\n", name, rc, err, strerror(err));
}

int main(void) {
    int err;

    errno = 0; long r1 = syscall(198, 16, 3, 0); /* netlink route */
    err = errno; show("netlink", r1, err);

    errno = 0; long r2 = syscall(198, 17, 3, 0x0300); /* packet */
    err = errno; show("packet", r2, err);

    errno = 0; long r3 = syscall(198, 2, 3, 1); /* raw ip */
    err = errno; show("rawip", r3, err);

    errno = 0; long r4 = syscall(241, NULL, 0, -1, -1, 0); /* perf_event_open */
    err = errno; show("perf_event_open(NULL)", r4, err);

    struct perf_event_attr attr;
    memset(&attr, 0, sizeof attr);
    attr.type = PERF_TYPE_SOFTWARE;
    attr.size = sizeof attr;
    attr.config = PERF_COUNT_SW_CPU_CLOCK;
    errno = 0; long r5 = syscall(241, &attr, 0, -1, -1, 0);
    err = errno; show("perf_event_open(sw)", r5, err);

    unsigned char bpf_attr[64];
    memset(bpf_attr, 0, sizeof bpf_attr);
    errno = 0; long r6 = syscall(280, 0 /* BPF_MAP_CREATE */, bpf_attr, sizeof bpf_attr);
    err = errno; show("bpf(map_create)", r6, err);

    errno = 0; long r7 = syscall(425, 8, NULL); /* io_uring_setup bad params */
    err = errno; show("io_uring_setup(NULL)", r7, err);

    const char *devs[] = {"/dev/kgsl-3d0", "/dev/ion", "/dev/dma_heap/system", "/dev/binder", "/dev/tun", NULL};
    for (int i = 0; devs[i]; i++) {
        errno = 0;
        long fd = open(devs[i], O_RDONLY);
        err = errno;
        show(devs[i], fd, err);
        if (fd >= 0) close((int)fd);
    }
    return 0;
}
