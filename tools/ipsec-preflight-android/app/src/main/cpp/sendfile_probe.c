#define _GNU_SOURCE
#include <jni.h>
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <netinet/in.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/sendfile.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

#define PAYLOAD_SIZE 1024

static void appendf(char *buffer, size_t capacity, size_t *used,
                    const char *format, ...) {
    if (*used >= capacity) return;
    va_list args;
    va_start(args, format);
    int written = vsnprintf(buffer + *used, capacity - *used, format, args);
    va_end(args);
    if (written < 0) return;
    size_t remaining = capacity - *used;
    if ((size_t)written >= remaining) {
        *used = capacity - 1;
    } else {
        *used += (size_t)written;
    }
}

static int write_all(int fd, const uint8_t *data, size_t length) {
    size_t done = 0;
    while (done < length) {
        ssize_t n = write(fd, data + done, length - done);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) return -1;
        done += (size_t)n;
    }
    return 0;
}

static int pread_all(int fd, uint8_t *data, size_t length) {
    size_t done = 0;
    while (done < length) {
        ssize_t n = pread(fd, data + done, length - done, (off_t)done);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) return -1;
        done += (size_t)n;
    }
    return 0;
}

JNIEXPORT jstring JNICALL
Java_top_dcmqht_p780ipsec_MainActivity_runFileBackedUdpProbe(
        JNIEnv *env, jobject thiz, jstring cache_dir_path) {
    (void)thiz;
    char report[4096] = {0};
    size_t used = 0;
    const char *cache_dir = (*env)->GetStringUTFChars(env, cache_dir_path, NULL);
    if (cache_dir == NULL) return NULL;

    char path[PATH_MAX] = {0};
    int path_created = 0;
    int write_fd = -1;
    int file_fd = -1;
    int rx_fd = -1;
    int tx_fd = -1;
    int probe_ok = 0;
    int cleanup_ok = 1;
    uint8_t expected[PAYLOAD_SIZE];
    uint8_t before[PAYLOAD_SIZE];
    uint8_t after[PAYLOAD_SIZE];
    uint8_t received[PAYLOAD_SIZE + 1];

    for (size_t i = 0; i < sizeof(expected); ++i) {
        expected[i] = (uint8_t)((i * 37U + 11U) & 0xffU);
    }

    int path_len = snprintf(path, sizeof(path), "%s/p780-sendfile-probe-%ld.tmp",
                            cache_dir, (long)getpid());
    if (path_len < 0 || (size_t)path_len >= sizeof(path)) {
        appendf(report, sizeof(report), &used, "FAIL: temporary path is too long.\n");
        goto cleanup;
    }

    write_fd = open(path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    if (write_fd < 0) {
        appendf(report, sizeof(report), &used,
                "1. Create app-private temporary file: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    path_created = 1;

    if (write_all(write_fd, expected, sizeof(expected)) != 0) {
        appendf(report, sizeof(report), &used,
                "1. Write temporary file: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    if (fsync(write_fd) != 0) {
        appendf(report, sizeof(report), &used,
                "1. Sync temporary file: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    if (close(write_fd) != 0) {
        write_fd = -1;
        appendf(report, sizeof(report), &used,
                "1. Close temporary file writer: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    write_fd = -1;

    file_fd = open(path, O_RDONLY | O_CLOEXEC);
    if (file_fd < 0 || pread_all(file_fd, before, sizeof(before)) != 0
            || memcmp(before, expected, sizeof(expected)) != 0) {
        appendf(report, sizeof(report), &used,
                "1. Create/read app-private temporary file: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "1. Create app-private temporary file: PASS; %d bytes\n",
            PAYLOAD_SIZE);

    rx_fd = socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, IPPROTO_UDP);
    if (rx_fd < 0) {
        appendf(report, sizeof(report), &used,
                "2. Create loopback UDP receiver: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }

    struct timeval timeout = {2, 0};
    if (setsockopt(rx_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) != 0) {
        appendf(report, sizeof(report), &used,
                "2. Set receive timeout: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }

    struct sockaddr_in receiver = {0};
    receiver.sin_family = AF_INET;
    receiver.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    receiver.sin_port = 0;
    if (bind(rx_fd, (struct sockaddr *)&receiver, sizeof(receiver)) != 0) {
        appendf(report, sizeof(report), &used,
                "2. Bind loopback UDP receiver: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }

    socklen_t receiver_len = sizeof(receiver);
    if (getsockname(rx_fd, (struct sockaddr *)&receiver, &receiver_len) != 0) {
        appendf(report, sizeof(report), &used,
                "2. Read loopback UDP port: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }

    tx_fd = socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, IPPROTO_UDP);
    if (tx_fd < 0) {
        appendf(report, sizeof(report), &used,
                "2. Create loopback UDP sender: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    if (connect(tx_fd, (struct sockaddr *)&receiver, sizeof(receiver)) != 0) {
        appendf(report, sizeof(report), &used,
                "2. Connect loopback UDP sender: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }

    off_t offset = 0;
    ssize_t sent = sendfile(tx_fd, file_fd, &offset, sizeof(expected));
    if (sent < 0) {
        appendf(report, sizeof(report), &used,
                "3. sendfile(file -> UDP loopback): FAIL; errno=%d (%s); no retry\n",
                errno, strerror(errno));
        goto cleanup;
    }
    if (sent != (ssize_t)sizeof(expected)) {
        appendf(report, sizeof(report), &used,
                "3. sendfile(file -> UDP loopback): FAIL; sent %zd/%d bytes; no retry\n",
                sent, PAYLOAD_SIZE);
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "3. sendfile(file -> UDP loopback): PASS; one call returned %zd bytes\n", sent);

    ssize_t received_len = recvfrom(rx_fd, received, sizeof(received), 0, NULL, NULL);
    if (received_len < 0) {
        appendf(report, sizeof(report), &used,
                "4. Receive UDP datagram: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    if (received_len != (ssize_t)sizeof(expected)
            || memcmp(received, expected, sizeof(expected)) != 0) {
        appendf(report, sizeof(report), &used,
                "4. Receive/compare UDP datagram: FAIL; received %zd bytes or payload mismatch\n",
                received_len);
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "4. Receive/compare UDP datagram: PASS; one %zd-byte datagram matched\n",
            received_len);

    if (pread_all(file_fd, after, sizeof(after)) != 0
            || memcmp(before, after, sizeof(before)) != 0
            || memcmp(after, expected, sizeof(expected)) != 0) {
        appendf(report, sizeof(report), &used,
                "5. Source file integrity: FAIL; bytes changed or read failed\n");
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "5. Source file integrity: PASS; pre/post bytes identical\n");
    probe_ok = 1;

cleanup:
    if (write_fd >= 0 && close(write_fd) != 0) cleanup_ok = 0;
    if (file_fd >= 0 && close(file_fd) != 0) cleanup_ok = 0;
    if (rx_fd >= 0 && close(rx_fd) != 0) cleanup_ok = 0;
    if (tx_fd >= 0 && close(tx_fd) != 0) cleanup_ok = 0;
    if (path_created && unlink(path) != 0) {
        cleanup_ok = 0;
        appendf(report, sizeof(report), &used,
                "Cleanup warning: temporary file unlink failed; errno=%d (%s)\n",
                errno, strerror(errno));
    } else if (path_created) {
        appendf(report, sizeof(report), &used, "Cleanup: temporary file removed.\n");
    }
    appendf(report, sizeof(report), &used,
            "No IPsec transform or ESP packet was used; no exploit-style page-cache manipulation was attempted.\n");
    if (probe_ok && cleanup_ok) {
        appendf(report, sizeof(report), &used,
                "PASS indicates file-backed sendfile-to-UDP loopback only; NOT DirtyFrag.\n");
    } else {
        appendf(report, sizeof(report), &used,
                "Probe did not fully pass; this is not a DirtyFrag vulnerability verdict.\n");
    }

    jstring result = (*env)->NewStringUTF(env, report);
    (*env)->ReleaseStringUTFChars(env, cache_dir_path, cache_dir);
    return result;
}
