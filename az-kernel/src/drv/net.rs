// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/drv/net.rs — Network Driver (Sprint 3)
//!
//! Sprint 1: Stubs.  Sprint 3: virtio-net (QEMU) + e1000 (physical NIC).

/// Sprint 3: initialise the virtio-net or e1000 NIC.
pub fn init() -> bool { false }

/// Transmit a raw Ethernet frame.  Sprint 1: no-op.
pub fn transmit(frame: &[u8]) -> bool { false }

/// Receive a raw Ethernet frame.  Sprint 1: always empty.
pub fn receive(buf: &mut [u8]) -> Option<usize> { None }
