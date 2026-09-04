// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026  ThomasCory Walker-Pearson
// AZ-OS ax-kernel: KK-Channel IPC with type-state adjacency enforcement
//
// KK adjacency rule: ring i may communicate only with rings i±1.
// This is enforced at COMPILE TIME via Rust newtypes and const generics.
// Cross-ring violations (e.g. Ring0 → Ring3) are a TYPE ERROR.
//
// Theory: ThomasCory Walker-Pearson | Code: GitHub Copilot (AI)

use heapless::spsc::Queue;

/// Type-level ring-level constants
pub struct Ring<const N: usize>;

/// KK adjacency rule: rings N and M may communicate iff |N - M| == 1 (mod 5).
///
/// This trait is only implemented for adjacent ring pairs.
/// Attempting to create a channel between non-adjacent rings causes a
/// compile-time error: "no implementation for KKAdjacent<Ring<0>, Ring<2>>".
pub trait KKAdjacent<A, B> {}

// Adjacent ring pairs (both directions)
impl KKAdjacent<Ring<0>, Ring<1>> for () {}
impl KKAdjacent<Ring<1>, Ring<0>> for () {}
impl KKAdjacent<Ring<1>, Ring<2>> for () {}
impl KKAdjacent<Ring<2>, Ring<1>> for () {}
impl KKAdjacent<Ring<2>, Ring<3>> for () {}
impl KKAdjacent<Ring<3>, Ring<2>> for () {}
impl KKAdjacent<Ring<3>, Ring<4>> for () {}
impl KKAdjacent<Ring<4>, Ring<3>> for () {}
// Ring 0 and Ring 4 are adjacent in the toroidal KK topology
impl KKAdjacent<Ring<0>, Ring<4>> for () {}
impl KKAdjacent<Ring<4>, Ring<0>> for () {}

/// An IPC message
#[derive(Debug, Clone)]
pub struct KKMessage {
    pub from_ring: usize,
    pub to_ring: usize,
    pub payload: u64,
    pub seq: u32,
}

/// A typed IPC channel between adjacent KK rings.
///
/// # Type parameters
/// - `FROM`: source ring level (e.g. `Ring<1>`)
/// - `TO`:   destination ring level (e.g. `Ring<2>`)
///
/// The channel is only constructable when `(): KKAdjacent<FROM, TO>`.
pub struct KKChannel<const FROM: usize, const TO: usize, const CAP: usize>
where
    (): KKAdjacent<Ring<FROM>, Ring<TO>>,
{
    queue: Queue<KKMessage, CAP>,
    seq: u32,
}

impl<const FROM: usize, const TO: usize, const CAP: usize>
    KKChannel<FROM, TO, CAP>
where
    (): KKAdjacent<Ring<FROM>, Ring<TO>>,
{
    pub const fn new() -> Self {
        Self {
            queue: Queue::new(),
            seq: 0,
        }
    }

    /// Send a message from ring FROM to ring TO.
    pub fn send(&mut self, payload: u64) -> Result<(), u64> {
        let msg = KKMessage {
            from_ring: FROM,
            to_ring: TO,
            payload,
            seq: self.seq,
        };
        self.seq = self.seq.wrapping_add(1);
        // Use unsafe split for single-producer / single-consumer
        // In a real kernel this would use lock-free queues per-CPU
        self.queue.enqueue(msg).map_err(|m| m.payload)
    }

    /// Receive the next message.
    pub fn recv(&mut self) -> Option<KKMessage> {
        self.queue.dequeue()
    }

    pub fn is_empty(&self) -> bool {
        self.queue.is_empty()
    }
}

pub mod ipc {
    #[allow(unused_imports)]
    pub use super::{KKChannel, KKMessage, Ring, KKAdjacent};
}
