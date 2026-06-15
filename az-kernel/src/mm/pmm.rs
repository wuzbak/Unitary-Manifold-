// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/mm/pmm.rs — Physical Memory Manager
//!
//! Bitmap-based physical page allocator.  Consumes the UEFI memory map
//! at boot to build a bitmap of available 4 KiB pages.  Thread-safe via
//! a spinlock (Sprint 0/1: single-core; Sprint 3: SMP-ready).

use spin::Mutex;
use uefi::table::boot::{MemoryDescriptor, MemoryMap, MemoryType};
use super::PAGE_SIZE;

const MAX_PAGES: usize = 1024 * 1024; // 4 GiB addressable at 4 KiB granularity

/// Physical Memory Manager.
///
/// Maintains a bitmap of physical 4 KiB frames.  Bit = 0 → free; 1 → used.
pub struct PhysicalMemoryManager {
    bitmap: [u64; MAX_PAGES / 64],
    total_pages: usize,
    free_pages: usize,
    total_bytes: usize,
}

impl PhysicalMemoryManager {
    /// Build from UEFI memory map.  Marks conventional memory as free;
    /// everything else (firmware, MMIO, reserved) as used.
    pub fn from_uefi_map(mmap: &MemoryMap) -> Self {
        let mut pmm = Self {
            bitmap: [!0u64; MAX_PAGES / 64], // all used initially
            total_pages: 0,
            free_pages: 0,
            total_bytes: 0,
        };
        for desc in mmap.entries() {
            pmm.total_bytes += desc.page_count as usize * PAGE_SIZE;
            if desc.ty == MemoryType::CONVENTIONAL {
                let start = desc.phys_start as usize / PAGE_SIZE;
                let count = desc.page_count as usize;
                for page in start..(start + count).min(MAX_PAGES) {
                    pmm.clear_bit(page);
                    pmm.free_pages += 1;
                }
                pmm.total_pages += count;
            }
        }
        pmm
    }

    /// Allocate `n` contiguous physical pages.  Returns base physical address.
    pub fn alloc(&mut self, n: usize) -> Option<usize> {
        // First-fit scan over the bitmap.
        let mut run = 0usize;
        let mut run_start = 0usize;
        for page in 0..MAX_PAGES {
            if !self.test_bit(page) {
                if run == 0 { run_start = page; }
                run += 1;
                if run >= n {
                    for p in run_start..(run_start + n) {
                        self.set_bit(p);
                    }
                    self.free_pages -= n;
                    return Some(run_start * PAGE_SIZE);
                }
            } else {
                run = 0;
            }
        }
        None
    }

    /// Free `n` pages starting at physical address `paddr`.
    pub fn free(&mut self, paddr: usize, n: usize) {
        let start = paddr / PAGE_SIZE;
        for page in start..(start + n).min(MAX_PAGES) {
            self.clear_bit(page);
        }
        self.free_pages += n;
    }

    pub fn free_count(&self) -> usize { self.free_pages }
    pub fn total_bytes(&self) -> usize { self.total_bytes }

    // ------------------------------------------------------------------
    // Bit manipulation
    // ------------------------------------------------------------------

    fn test_bit(&self, page: usize) -> bool {
        let word = page / 64;
        let bit  = page % 64;
        (self.bitmap[word] >> bit) & 1 == 1
    }

    fn set_bit(&mut self, page: usize) {
        let word = page / 64;
        let bit  = page % 64;
        self.bitmap[word] |= 1u64 << bit;
    }

    fn clear_bit(&mut self, page: usize) {
        let word = page / 64;
        let bit  = page % 64;
        self.bitmap[word] &= !(1u64 << bit);
    }
}
