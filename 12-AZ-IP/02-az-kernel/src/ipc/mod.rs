// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/ipc/mod.rs — AZ-IPC: Holographic Boundary IPC
//!
//! ## Architecture (Pillar 4 — Holographic Boundary)
//!
//! Processes communicate through "holographic boundary" channels.  Two processes
//! that share a holographic boundary can exchange messages; processes in different
//! compactification domains cannot (enforced by the kernel's fiber bundle geometry).
//!
//! A channel exists at the boundary between two adjacent KK levels.  This directly
//! maps the AdS/CFT correspondence: the lower-dimensional (KK-level n) process
//! can see everything the higher-dimensional (KK-level n+1) process puts on the
//! shared boundary, but not the interior.
//!
//! ## IPC primitives
//!   - `Channel`: a pair of ring buffers (one per direction) with holographic metadata.
//!   - `Message`: a fixed-size envelope (64 bytes header + up to 4 KiB payload).
//!   - `Endpoint`: a process's handle to one side of a channel.

pub mod holographic;
pub mod kk_channel;
pub mod ring_buffer;

pub use holographic::{Channel, Endpoint, HolographicBoundary};
pub use kk_channel::{KKAdjacent, KKChannel, KKMessage, Ring};
pub use ring_buffer::RingBuffer;

use spin::Mutex;

const MAX_CHANNELS: usize = 64;

static CHANNEL_TABLE: Mutex<heapless::Vec<Channel, MAX_CHANNELS>> =
    Mutex::new(heapless::Vec::new());

/// Initialise the IPC subsystem.  Called once during kernel boot.
pub fn init() {
    // Pre-allocate channel table — nothing to do for now; table starts empty.
}

/// Create a new IPC channel between two KK levels.
///
/// Returns `(Endpoint, Endpoint)` — one for each side — or `None` if the
/// channel table is full or the KK levels are not adjacent.
pub fn create_channel(level_a: u8, level_b: u8) -> Option<(Endpoint, Endpoint)> {
    if (level_a as i32 - level_b as i32).unsigned_abs() != 1 {
        return None; // non-adjacent KK levels cannot directly communicate
    }
    let mut table = CHANNEL_TABLE.lock();
    if table.is_full() { return None; }
    let channel_id = table.len() as u32;
    let channel = Channel::new(channel_id, level_a, level_b);
    let ep_a = Endpoint::new(channel_id, level_a);
    let ep_b = Endpoint::new(channel_id, level_b);
    let _ = table.push(channel);
    Some((ep_a, ep_b))
}
