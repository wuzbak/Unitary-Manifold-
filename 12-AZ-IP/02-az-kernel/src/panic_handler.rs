// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/panic_handler.rs — Bare-Metal Panic Handler
//!
//! On a bare-metal kernel, a panic cannot unwind.  Instead it:
//!   1. Displays a red "KERNEL PANIC" screen with the location and message.
//!   2. Halts the CPU with a CLI + HLT loop (x86-64).
//!
//! This is the AxiomZero equivalent of a kernel oops — explicit, visible,
//! and never silent.  Epistemic transparency extends to the kernel level.

use core::panic::PanicInfo;

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    // Attempt to write to the serial port 0x3F8 (COM1) for headless debugging.
    // This works even if the framebuffer is not yet initialised.
    serial_write_str("\r\n\r\n!!! AXIOMZERO KERNEL PANIC !!!\r\n");
    if let Some(loc) = info.location() {
        serial_write_str(loc.file());
        serial_write_str(":");
        // minimal u32→str without alloc
        serial_write_u32(loc.line());
        serial_write_str("\r\n");
    }
    // Halt the CPU.
    loop {
        #[cfg(target_arch = "x86_64")]
        unsafe {
            core::arch::asm!("cli; hlt", options(nomem, nostack));
        }
        #[cfg(target_arch = "aarch64")]
        unsafe {
            core::arch::asm!("wfe", options(nomem, nostack));
        }
    }
}

// ---------------------------------------------------------------------------
// Minimal COM1 serial writer (no dependencies, no alloc)
// ---------------------------------------------------------------------------

#[cfg(target_arch = "x86_64")]
fn serial_write_byte(b: u8) {
    unsafe {
        // Wait for transmit holding register empty (bit 5 of LSR = 0x3FD)
        loop {
            let lsr: u8;
            core::arch::asm!(
                "in al, dx",
                in("dx") 0x3FDu16,
                out("al") lsr,
                options(nomem, nostack)
            );
            if lsr & 0x20 != 0 { break; }
        }
        core::arch::asm!(
            "out dx, al",
            in("dx") 0x3F8u16,
            in("al") b,
            options(nomem, nostack)
        );
    }
}

#[cfg(target_arch = "aarch64")]
fn serial_write_byte(b: u8) {
    // PL011 UART base address — correct for QEMU virt machine.
    const UART0: *mut u8 = 0x0900_0000 as *mut u8;
    unsafe { UART0.write_volatile(b); }
}

fn serial_write_str(s: &str) {
    for b in s.bytes() { serial_write_byte(b); }
}

fn serial_write_u32(mut n: u32) {
    if n == 0 { serial_write_byte(b'0'); return; }
    let mut buf = [0u8; 10];
    let mut i = 10usize;
    while n > 0 {
        i -= 1;
        buf[i] = b'0' + (n % 10) as u8;
        n /= 10;
    }
    for b in &buf[i..] { serial_write_byte(*b); }
}
