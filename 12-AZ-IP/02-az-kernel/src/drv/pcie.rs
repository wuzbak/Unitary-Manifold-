// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/drv/pcie.rs — PCI Express Bus Driver (Sprint 3)
//!
//! Sprint 1: Stubs.  Sprint 3: Full ECAM MMIO enumeration.
//!
//! PCI Express in AxiomZero is an "adjacent-track" interface — hardware is 4D
//! and cannot make claims about the 5D geometry.  The PCI-E driver runs at
//! KK ring 1 (system services) and requests resources via the kernel boundary.

/// PCI device header (type 0 — endpoint device).
#[derive(Debug, Clone, Copy)]
pub struct PciHeader {
    pub vendor_id: u16,
    pub device_id: u16,
    pub class_code: u8,
    pub subclass: u8,
    pub prog_if: u8,
    pub bar: [u32; 6],
}

/// Sprint 3: ECAM base address from ACPI MCFG table.
const PCIE_ECAM_BASE: usize = 0xB000_0000; // QEMU virt default

/// Read a 16-bit word from PCI config space.
/// Sprint 1: returns zeroed stub.  Sprint 3: real MMIO read.
pub fn config_read_u16(_bus: u8, _dev: u8, _func: u8, _offset: u16) -> u16 {
    // Sprint 3 implementation:
    // let addr = PCIE_ECAM_BASE
    //     + ((bus as usize) << 20)
    //     + ((dev as usize) << 15)
    //     + ((func as usize) << 12)
    //     + (offset as usize);
    // unsafe { (addr as *const u16).read_volatile() }
    0 // Sprint 1 stub
}

/// Enumerate all PCI devices on the first bus.  Returns device headers found.
pub fn enumerate() -> heapless::Vec<PciHeader, 32> {
    heapless::Vec::new() // Sprint 1 stub; Sprint 3: walks bus 0
}

/// Initialise the NVIDIA GPU (Sprint 3 — Nouveau-compatible MMIO interface).
///
/// Required for Ollama local model inference directly on AZ-KERNEL.
pub fn init_gpu() -> bool {
    // Sprint 3: scan PCI, find NVIDIA vendor (0x10DE), enable MMIO BAR,
    // load firmware blob, initialise command ring.
    false // not available in Sprint 1
}
