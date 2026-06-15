// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/ipc/holographic.rs — Holographic Boundary Channel

use super::ring_buffer::RingBuffer;

const MSG_SIZE: usize = 64;        // bytes per IPC message slot
const RING_CAPACITY: usize = 64;   // messages per ring buffer

/// An IPC channel between two processes at adjacent KK levels.
///
/// The channel is a pair of ring buffers (one in each direction), forming the
/// "holographic boundary" between two compactification domains.
pub struct Channel {
    pub id: u32,
    pub level_low: u8,      // lower KK level
    pub level_high: u8,     // higher KK level
    pub ring_low_to_high: RingBuffer<MSG_SIZE, RING_CAPACITY>,
    pub ring_high_to_low: RingBuffer<MSG_SIZE, RING_CAPACITY>,
    pub message_count: u64, // total messages exchanged (diagnostic)
}

impl Channel {
    pub fn new(id: u32, level_a: u8, level_b: u8) -> Self {
        let (low, high) = if level_a < level_b { (level_a, level_b) } else { (level_b, level_a) };
        Self {
            id,
            level_low: low,
            level_high: high,
            ring_low_to_high: RingBuffer::new(),
            ring_high_to_low: RingBuffer::new(),
            message_count: 0,
        }
    }

    /// Send a message from the low KK level to the high KK level.
    pub fn send_upward(&mut self, msg: [u8; MSG_SIZE]) -> bool {
        let ok = self.ring_low_to_high.push(msg);
        if ok { self.message_count += 1; }
        ok
    }

    /// Send a message from the high KK level to the low KK level.
    pub fn send_downward(&mut self, msg: [u8; MSG_SIZE]) -> bool {
        let ok = self.ring_high_to_low.push(msg);
        if ok { self.message_count += 1; }
        ok
    }

    /// Receive a message at the high KK level (from low).
    pub fn recv_at_high(&mut self) -> Option<[u8; MSG_SIZE]> {
        self.ring_low_to_high.pop()
    }

    /// Receive a message at the low KK level (from high).
    pub fn recv_at_low(&mut self) -> Option<[u8; MSG_SIZE]> {
        self.ring_high_to_low.pop()
    }
}

/// A process's handle to one end of a holographic IPC channel.
#[derive(Clone, Copy, Debug)]
pub struct Endpoint {
    pub channel_id: u32,
    pub kk_level: u8,
}

impl Endpoint {
    pub fn new(channel_id: u32, kk_level: u8) -> Self {
        Self { channel_id, kk_level }
    }
}

/// Metadata about the holographic boundary (diagnostic / governance layer).
pub struct HolographicBoundary {
    pub channel_count: u32,
    pub total_messages: u64,
}

impl HolographicBoundary {
    pub fn new() -> Self { Self { channel_count: 0, total_messages: 0 } }
}
