/*
 * Minimal no-op stub: executes the displaced prologue and returns to entry+16.
 * Used to prove the trampoline mechanism itself is transparent before adding
 * any payload.
 */
    .text

    .global p780_stub_prod
    .type   p780_stub_prod, %function
    .balign 16
p780_stub_prod:
    /* four displaced instructions, filled by the patcher */
    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f
    .word   0xd503201f

    /* return to entry+16 (PC-relative, rewritten per blob address) */
    .inst   0x90000009
    .inst   0x91000129
    .inst   0xd61f0120

    .balign 16
    .global p780_stub_test
    .type   p780_stub_test, %function
p780_stub_test:
    ret
