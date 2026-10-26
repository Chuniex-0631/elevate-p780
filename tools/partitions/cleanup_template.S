/*
 * P780 init-domain /metadata cleanup (aarch64, raw syscalls).
 * Gate: gettid()==1 && getuid()==0 && getpid()==1.
 * Rendered by gen_clean.py: the leftover dump artefacts are unlinked so that a
 * real chunk fits into the 11 MiB /metadata filesystem.
 */
    .text
    .global p780_stub_prod
    .type   p780_stub_prod, %function
    .balign 16
p780_stub_prod:
    stp     x0, x1, [sp, #-48]!
    stp     x2, x3, [sp, #16]
    stp     x29, x30, [sp, #32]

    mov     x8, #178
    svc     #0
    cmp     x0, #1
    b.ne    9f
    mov     x8, #174
    svc     #0
    cbnz    x0, 9f
    mov     x8, #172
    svc     #0
    cmp     x0, #1
    b.ne    9f

    movn    x0, #99
    adr     x1, p_lock
    movz    x2, #0x0c1
    movz    x3, #0x1a4
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, 9f
    mov     x9, x0
    mov     x0, x9
    mov     x8, #57
    svc     #0

__UNLINKS__

9:
    ldp     x29, x30, [sp, #32]
    ldp     x2, x3, [sp, #16]
    ldp     x0, x1, [sp], #48
    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f
    .inst   0x90000009
    .inst   0x91000129
    .inst   0xd61f0120

do_unlink:
    mov     x9, x1
    movn    x0, #99
    mov     x1, x9
    mov     x2, #0
    mov     x8, #35
    svc     #0
    ret

    .balign 8
p_lock:
    .asciz  "/dev/p780_clean"
__STRINGS__

    .global p780_stub_test
    .type   p780_stub_test, %function
    .balign 16
p780_stub_test:
    stp     x0, x1, [sp, #-32]!
    stp     x2, x3, [sp, #16]
    movn    x0, #99
    adr     x1, p_test_path
    movz    x2, #0x441
    movz    x3, #0x1a4
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, 5f
    mov     x9, x0
    mov     x0, x9
    adr     x1, p_test_msg
    mov     x2, #8
    mov     x8, #64
    svc     #0
    mov     x0, x9
    mov     x8, #57
    svc     #0
5:  ldp     x2, x3, [sp, #16]
    ldp     x0, x1, [sp], #32
    ret
p_test_path:
    .asciz  "/data/local/tmp/p780_stub_marker"
    .balign 8
p_test_msg:
    .ascii  "STUBTEST"
