// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/mm/vmm.rs — Virtual Memory Manager
//!
//! Maps physical frames into the 64-bit virtual address space using the
//! x86-64 4-level page table hierarchy (PML4 → PDPT → PD → PT).
//!
//! The 5D fiber bundle topology is enforced here: each KK privilege ring
//! occupies a dedicated region of the virtual address space, and page table
//! entries carry an AZ-extended protection bit in the OS-available bits.

use super::PAGE_SIZE;

/// Virtual address space layout (Sprint 1 draft).
///
/// Ring 0 (kernel):  0xFFFF_8000_0000_0000 – 0xFFFF_FFFF_FFFF_FFFF  (top 128 TiB)
/// Ring 1–3 (user):  0x0000_0000_0000_0000 – 0x0000_7FFF_FFFF_FFFF  (low 128 TiB)
/// Ring 4 (sandbox): 0x0000_4000_0000_0000 – 0x0000_7FFF_FFFF_FFFF  (top half of user)
pub struct VirtualMemoryManager {
    // In Sprint 1 this is a simplified record-keeping structure.
    // Sprint 2 replaces it with real CR3-switching and TLB management.
    mappings: heapless::Vec<(usize, usize, u8), 4096>, // (phys, virt, ring)
}

impl VirtualMemoryManager {
    pub fn new() -> Self {
        Self { mappings: heapless::Vec::new() }
    }

    /// Map `n` pages at `paddr` into the ring's virtual range.
    /// Returns the virtual base address.
    pub fn map(&mut self, paddr: usize, _n: usize, ring: u8) -> usize {
        let vaddr = Self::ring_base(ring) + self.mappings.len() * PAGE_SIZE;
        // Record the mapping (actual page table writes happen in Sprint 2).
        let _ = self.mappings.push((paddr, vaddr, ring));
        vaddr
    }

    /// Unmap pages at the given physical address.
    pub fn unmap(&mut self, paddr: usize, _n: usize) {
        self.mappings.retain(|(p, _, _)| *p != paddr);
    }

    /// Base virtual address for each ring.
    fn ring_base(ring: u8) -> usize {
        match ring {
            0 => 0xFFFF_8000_0000_0000usize, // kernel
            1 => 0x0000_0001_0000_0000usize, // system services
            2 => 0x0000_0010_0000_0000usize, // trusted agent
            3 => 0x0000_0040_0000_0000usize, // user space
            4 => 0x0000_4000_0000_0000usize, // sandbox
            _ => 0x0000_0000_1000_0000usize, // fallback
        }
    }
}
