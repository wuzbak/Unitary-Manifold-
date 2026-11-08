// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/lib.rs — Host-Testable Kernel Logic Library
//!
//! The kernel binary (`main.rs`) is `#![no_std] #![no_main]` and targets
//! `x86_64-unknown-uefi` exclusively — it cannot be unit-tested with the
//! normal host `cargo test` harness, since there is no OS loader to run a
//! UEFI binary on the host and no `std` test runner inside `no_main`.
//!
//! This crate factors every hardware-independent subsystem (the heap
//! allocator, physical/virtual memory bookkeeping, the φ-debt RAM
//! filesystem, the IPC ring buffers and channel table, and the scheduler's
//! pure-logic pieces) into a library that is `no_std` for the real kernel
//! build but compiles with `std` under `cargo test`, so its unit tests run
//! natively on the host with full `cargo test` tooling (panics, assertions,
//! `#[should_panic]`, etc. all work normally).
//!
//! Run with: `cargo test --lib` (the `[[bin]]` target is UEFI-only and is
//! intentionally not part of the default host test build; see README.md).
#![cfg_attr(not(test), no_std)]

extern crate alloc;

pub mod drv;
pub mod fs;
pub mod framebuffer;
pub mod ipc;
pub mod mm;
pub mod sched;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_ramfs_starts_empty_with_first_inode_one() {
        // The fixed-capacity inline inode table exceeds the test harness's stack.
        std::thread::Builder::new()
            .stack_size(32 * 1024 * 1024)
            .spawn(|| {
                let mut fs = fs::ramfs::RamFs::default();
                assert_eq!(fs.file_count(), 0);
                assert_eq!(fs.create("first"), Some(1));
                assert_eq!(fs.write(1, b"hello"), 5);
                let mut buf = [0; 5];
                assert_eq!(fs.read(1, &mut buf), 5);
                assert_eq!(&buf, b"hello");
            })
            .unwrap()
            .join()
            .unwrap();
    }

    #[test]
    fn default_holographic_boundary_starts_with_zero_counters() {
        let boundary = ipc::holographic::HolographicBoundary::default();
        assert_eq!(boundary.channel_count, 0);
        assert_eq!(boundary.total_messages, 0);
    }

    #[test]
    fn default_kk_channel_starts_empty_with_sequence_zero() {
        let mut channel = ipc::kk_channel::KKChannel::<0, 1, 4>::default();
        assert!(channel.is_empty());
        assert!(channel.recv().is_none());
        assert_eq!(channel.send(74), Ok(()));
        let message = channel.recv().unwrap();
        assert_eq!((message.from_ring, message.to_ring), (0, 1));
        assert_eq!((message.payload, message.seq), (74, 0));
    }

    #[test]
    fn default_ring_buffer_starts_empty_and_round_trips() {
        let mut ring = ipc::ring_buffer::RingBuffer::<2, 4>::default();
        assert!(ring.is_empty());
        assert!(!ring.is_full());
        assert_eq!(ring.pop(), None);
        assert!(ring.push([5, 7]));
        assert_eq!(ring.pop(), Some([5, 7]));
        assert!(ring.is_empty());
    }

    #[test]
    fn default_virtual_memory_manager_starts_at_ring_base() {
        let mut manager = mm::vmm::VirtualMemoryManager::default();
        let mut original = mm::vmm::VirtualMemoryManager::new();
        assert_eq!(manager.map(0x1000, 1, 1), original.map(0x1000, 1, 1));
        assert_eq!(manager.map(0x2000, 1, 1), original.map(0x2000, 1, 1));
    }

    #[test]
    fn default_phi_debt_accounting_has_no_reclaim_candidates() {
        let mut accounting = mm::phi_debt::PhiDebtAccounting::default();
        assert!(accounting.reclaim_candidates().is_empty());
        accounting.record_alloc(0x1000, 1);
        accounting.record_write(0x1000);
        accounting.record_read(0x1000);
        assert!(accounting.reclaim_candidates().is_empty());
    }

    #[test]
    fn default_geodesic_cache_matches_new_cache() {
        let mut cache = sched::geodesic::GeodesicCache::default();
        let mut original = sched::geodesic::GeodesicCache::new();
        let pid = sched::process::ProcessId(0);
        assert_eq!(cache.geodesic_distance(pid), f32::MAX);
        cache.register(pid, 1, 100, 4);
        original.register(pid, 1, 100, 4);
        assert_eq!(cache.geodesic_distance(pid), original.geodesic_distance(pid));
    }
}
