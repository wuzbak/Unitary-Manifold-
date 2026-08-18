// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/ipc/ring_buffer.rs — Lock-Free Ring Buffer
//!
//! A single-producer, single-consumer ring buffer for IPC messages.
//! Fixed-capacity, no-alloc.  Uses atomic indices for SPSC safety.
//!
//! MSG_SIZE: bytes per message slot.
//! CAPACITY: number of message slots.

use core::sync::atomic::{AtomicUsize, Ordering};

pub struct RingBuffer<const MSG_SIZE: usize, const CAPACITY: usize> {
    buffer: [[u8; MSG_SIZE]; CAPACITY],
    head: AtomicUsize, // producer writes here
    tail: AtomicUsize, // consumer reads here
}

impl<const MSG_SIZE: usize, const CAPACITY: usize> RingBuffer<MSG_SIZE, CAPACITY> {
    pub const fn new() -> Self {
        Self {
            buffer: [[0u8; MSG_SIZE]; CAPACITY],
            head: AtomicUsize::new(0),
            tail: AtomicUsize::new(0),
        }
    }

    /// Push a message.  Returns false if the buffer is full.
    pub fn push(&mut self, msg: [u8; MSG_SIZE]) -> bool {
        let head = self.head.load(Ordering::Relaxed);
        let next = (head + 1) % CAPACITY;
        if next == self.tail.load(Ordering::Acquire) {
            return false; // full
        }
        self.buffer[head] = msg;
        self.head.store(next, Ordering::Release);
        true
    }

    /// Pop a message.  Returns None if the buffer is empty.
    pub fn pop(&mut self) -> Option<[u8; MSG_SIZE]> {
        let tail = self.tail.load(Ordering::Relaxed);
        if tail == self.head.load(Ordering::Acquire) {
            return None; // empty
        }
        let msg = self.buffer[tail];
        self.tail.store((tail + 1) % CAPACITY, Ordering::Release);
        Some(msg)
    }

    pub fn is_empty(&self) -> bool {
        self.head.load(Ordering::Relaxed) == self.tail.load(Ordering::Relaxed)
    }

    pub fn is_full(&self) -> bool {
        let head = self.head.load(Ordering::Relaxed);
        (head + 1) % CAPACITY == self.tail.load(Ordering::Relaxed)
    }
}
