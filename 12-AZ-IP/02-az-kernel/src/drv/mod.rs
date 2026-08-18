// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/drv/mod.rs — AZ-DRV: Driver Boundary Layer
//!
//! ## Epistemic Separation (SEPARATION.md applied to hardware)
//!
//! Drivers are "adjacent-track" modules.  They interface with physical hardware
//! (which is 4D, not 5D) and must explicitly cross the kernel boundary to
//! interact with the 5D kernel space.  This mirrors the epistemic separation
//! between hardgate physics claims and adjacent research tracks.
//!
//! A driver that attempts to make hardgate kernel calls without the correct
//! Pentad clearance bits will be rejected by the kernel boundary check.
//!
//! Sprint 1: Placeholder registration (real drivers in Sprint 3).
//! Sprint 3: PCI-E bus driver, USB HID, Ethernet (virtio-net / e1000).

pub mod pcie;
pub mod usb_hid;
pub mod net;

use heapless::Vec;

const MAX_DRIVERS: usize = 32;

/// A registered hardware driver descriptor.
#[derive(Clone)]
pub struct DriverDescriptor {
    pub name: heapless::String<64>,
    pub device_class: DeviceClass,
    pub kk_ring: u8,        // which privilege ring this driver runs at
    pub pentad_bits: u8,    // required Pentad clearance
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum DeviceClass {
    Display,
    Storage,
    Network,
    Input,
    Compute, // GPU — Sprint 3: NVIDIA via Nouveau-compatible interface
    Audio,
    Unknown,
}

static mut DRIVER_TABLE: Vec<DriverDescriptor, MAX_DRIVERS> = Vec::new();

/// Initialise the driver subsystem.  Registers built-in drivers.
pub fn init() {
    // Register the framebuffer display driver (already active from Sprint 0).
    register(DriverDescriptor {
        name: {
            let mut s = heapless::String::new();
            let _ = s.push_str("az-framebuffer");
            s
        },
        device_class: DeviceClass::Display,
        kk_ring: 1,   // system services ring
        pentad_bits: 0b00010,
    });
}

/// Register a new driver.  Returns false if the driver table is full.
pub fn register(desc: DriverDescriptor) -> bool {
    // SAFETY: single-threaded during boot init.
    unsafe { DRIVER_TABLE.push(desc).is_ok() }
}

/// Find a driver by device class.
pub fn find(class: DeviceClass) -> Option<&'static DriverDescriptor> {
    // SAFETY: read-only after init.
    unsafe { DRIVER_TABLE.iter().find(|d| d.device_class == class) }
}
