// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/main.rs — AxiomZero Bare-Metal UEFI Entry Point
//!
//! # Sprint 0: UEFI Boot → Framebuffer → "Hello from AxiomZero"
//!
//! This is the single entry point for the AxiomZero kernel on x86-64 UEFI
//! hardware.  The UEFI firmware hands control here after POST and secure-boot
//! attestation.  From this point forward, every byte of execution is AxiomZero.
//!
//! The boot sequence mirrors Kaluza-Klein geometry:
//!   Phase 1 — Identify the metric (initialise UEFI services, discover memory)
//!   Phase 2 — Solve the geodesic (hand off from UEFI to AZ-kernel runtime)
//!   Phase 3 — Uncompactify (launch the cognitive layer and 7-manager network)
//!
//! Theory and scientific direction: ThomasCory Walker-Pearson.
//! Code architecture, kernel engineering: GitHub Copilot (AI).

#![no_std]
#![no_main]
#![feature(abi_efiapi)]
// Lints: bare-metal code never uses std; clippy must be aware.
#![warn(clippy::all)]
#![allow(clippy::empty_loop)]

extern crate alloc;

use alloc::format;
use uefi::prelude::*;
use uefi::proto::console::gop::{GraphicsOutput, PixelFormat};
use uefi::table::boot::{MemoryDescriptor, MemoryMap, MemoryType};

mod framebuffer;
mod mm;
mod sched;
mod ipc;
mod fs;
mod drv;
mod panic_handler;

use framebuffer::{AxiomFramebuffer, Color};
use mm::AxiomMemoryManager;
use sched::AxiomScheduler;

// ---------------------------------------------------------------------------
// Kernel version constants (from the Unitary Manifold framework)
// ---------------------------------------------------------------------------
const AZ_VERSION_MAJOR: u32 = 0;
const AZ_VERSION_MINOR: u32 = 1;
const AZ_VERSION_PATCH: u32 = 0;
const AZ_WINDING_NUMBER: u32 = 5;   // n_w; selected by Planck nₛ data
const AZ_K_CS: u32 = 74;            // k_cs = 5² + 7²; birefringence datum
const AZ_INTERRUPT_RINGS: u32 = 5;  // mirrors the winding number — topological

/// UEFI entry point.  Called by firmware with system table access.
///
/// # Safety
/// This is called by UEFI firmware.  The handle and system table are valid
/// for the duration of boot services.  After `exit_boot_services` the memory
/// map becomes authoritative and boot services are no longer callable.
#[entry]
fn kernel_main(image: Handle, mut st: SystemTable<Boot>) -> Status {
    // -----------------------------------------------------------------------
    // Phase 1 — Metric Initialisation
    // Identify the hardware topology (memory, framebuffer, CPU topology).
    // -----------------------------------------------------------------------
    uefi_services::init(&mut st).expect("UEFI services init failed");
    let bs = st.boot_services();

    // Acquire the Graphics Output Protocol (GOP) framebuffer.
    // This is the kernel's sole output channel until a proper VT subsystem
    // is initialised (Sprint 3).
    let gop_handle = bs
        .get_handle_for_protocol::<GraphicsOutput>()
        .expect("GOP not available — verify UEFI firmware supports GOP");
    let mut gop = bs
        .open_protocol_exclusive::<GraphicsOutput>(gop_handle)
        .expect("Failed to open GOP protocol");

    // Construct the AZ framebuffer abstraction over the GOP linear buffer.
    let mut fb = AxiomFramebuffer::from_gop(&mut gop);
    fb.clear(Color::AXIOMZERO_BLACK);

    // -----------------------------------------------------------------------
    // Phase 2 — Geodesic Resolution
    // Exit UEFI boot services and take ownership of the machine.
    // After this call, UEFI runtime services are still available but
    // boot services (memory allocation, protocol access) are gone forever.
    // -----------------------------------------------------------------------
    fb.draw_status_line("AZ-BOOT: Exiting UEFI boot services — crossing the geodesic...");

    let mut mmap_buf = [0u8; 16 * 1024]; // 16 KB for memory map
    let (st_runtime, memory_map) = st
        .exit_boot_services(image, &mut mmap_buf)
        .expect("exit_boot_services failed");

    // From this point: no heap, no alloc, no panics until AZ-MM is live.
    // We have: framebuffer, memory map, runtime services.

    // -----------------------------------------------------------------------
    // Phase 3 — Uncompactification
    // Bootstrap the kernel subsystems in dependency order.
    // -----------------------------------------------------------------------

    // AZ-MM: Physical memory manager over the UEFI memory map.
    // The fiber bundle address space model is established here.
    let mut mm = AxiomMemoryManager::from_memory_map(&memory_map);
    mm.init_fiber_bundle(AZ_WINDING_NUMBER, AZ_K_CS);

    // AZ-SCHED: Geodesic scheduler with n_w = 5 interrupt rings.
    let mut scheduler = AxiomScheduler::new(AZ_INTERRUPT_RINGS);
    scheduler.init_geodesic_cache();

    // AZ-IPC: Holographic boundary inter-process channels.
    ipc::init();

    // AZ-FS: Phi-debt RAM filesystem.
    fs::init();

    // AZ-DRV: Driver boundary (adjacent-track, 4D interface).
    drv::init();

    // -----------------------------------------------------------------------
    // Sprint 0 milestone: render "Hello from AxiomZero" on the framebuffer.
    // This is the first visual proof that the kernel owns the machine.
    // -----------------------------------------------------------------------
    fb.clear(Color::AXIOMZERO_BLACK);
    fb.draw_banner(AZ_VERSION_MAJOR, AZ_VERSION_MINOR, AZ_VERSION_PATCH);
    fb.draw_text(2, 4, "5D Kaluza-Klein Bare-Metal Kernel", Color::AXIOMZERO_GOLD);
    fb.draw_text(2, 5, &format!(
        "Winding number n_w = {}  |  k_cs = {}  |  Interrupt rings = {}",
        AZ_WINDING_NUMBER, AZ_K_CS, AZ_INTERRUPT_RINGS
    ), Color::AXIOMZERO_CYAN);
    fb.draw_text(2, 7, "AZ-MM:   fiber bundle address space ONLINE", Color::AXIOMZERO_GREEN);
    fb.draw_text(2, 8, "AZ-SCHED: geodesic scheduler ONLINE", Color::AXIOMZERO_GREEN);
    fb.draw_text(2, 9, "AZ-IPC:  holographic boundary channels ONLINE", Color::AXIOMZERO_GREEN);
    fb.draw_text(2, 10, "AZ-FS:   phi-debt RAM filesystem ONLINE", Color::AXIOMZERO_GREEN);
    fb.draw_text(2, 11, "AZ-DRV:  driver boundary layer ONLINE", Color::AXIOMZERO_GREEN);
    fb.draw_text(2, 13, "COGNITIVE LAYER: spawning 7-manager agent network...", Color::AXIOMZERO_WHITE);
    fb.draw_text(2, 14, "(Python cognitive layer requires x86-64 CPU + Ollama on first boot)", Color::AXIOMZERO_GREY);
    fb.draw_text(2, 16, "Hello from AxiomZero.", Color::AXIOMZERO_WHITE);
    fb.draw_text(2, 17, "Theory: ThomasCory Walker-Pearson  |  Kernel: GitHub Copilot (AI)", Color::AXIOMZERO_GREY);

    // -----------------------------------------------------------------------
    // Main kernel loop: the scheduler takes over from here.
    // In Sprint 0 this spins; in Sprint 1 the geodesic scheduler runs real
    // processes; in Sprint 2 the Python cognitive layer is the primary process.
    // -----------------------------------------------------------------------
    scheduler.run_event_loop(&mut fb);

    // Unreachable in production; UEFI runtime requires a non-EFI_SUCCESS only
    // on catastrophic failure.
    Status::SUCCESS
}
