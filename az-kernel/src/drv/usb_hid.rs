// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/drv/usb_hid.rs — USB HID (Keyboard/Mouse) Driver (Sprint 3)
//!
//! Sprint 1: Stubs.  Sprint 3: xHCI + HID boot protocol.

/// A raw HID event (keyboard or mouse).
#[derive(Debug, Clone, Copy)]
pub struct HidEvent {
    pub kind: HidEventKind,
    pub code: u16,
    pub value: i32,
}

#[derive(Debug, Clone, Copy)]
pub enum HidEventKind { Key, MouseMove, MouseButton, Scroll }

/// Sprint 1 stub: always empty.  Sprint 3: polls xHCI event ring.
pub fn poll_events() -> heapless::Vec<HidEvent, 16> {
    heapless::Vec::new()
}
