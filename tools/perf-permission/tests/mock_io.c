/* Host-only diagnostic classification tests. Never linked into delivered ARM64 binary. */
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <linux/perf_event.h>
static const char *mode(void) { const char *p=getenv("MOCK_MODE"); return p?p:"pass"; }
uid_t __wrap_getuid(void) { return !strcmp(mode(),"context")?0:2000; }
uid_t __wrap_geteuid(void) { return __wrap_getuid(); }
long __wrap_syscall(long nr, ...) {
    (void)nr;
    if (!strcmp(mode(),"denied")) { errno=EACCES; return -1; }
    if (!strcmp(mode(),"unsupported")) { errno=ENOSYS; return -1; }
    return 99;
}
int __wrap_ioctl(int fd, unsigned long req, ...) {
    (void)fd;
    if (!strcmp(mode(),"enable") && req==PERF_EVENT_IOC_ENABLE) {errno=EPERM;return -1;}
    return 0;
}
ssize_t __wrap_read(int fd, void *p, size_t n) {
    (void)fd;
    uint64_t v[3]={10000000,20000000,20000000};
    if (!strcmp(mode(),"zero")) v[0]=0;
    if (!strcmp(mode(),"readerror")) {errno=EIO;return -1;}
    memcpy(p,v,n<sizeof(v)?n:sizeof(v));
    return !strcmp(mode(),"short")?8:24;
}
int __wrap_close(int fd) { (void)fd; return 0; }
