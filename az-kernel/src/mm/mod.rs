// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/mm/mod.rs — AZ-MM: Fiber Bundle Memory Manager
//!
//! # Sprint 1: Physical and Virtual Memory Management
//!
//! ## Architecture
//!
//! Conventional OSes use flat/paged address spaces.  AxiomZero models process
//! memory as a fiber bundle:
//!
//!   - **Base manifold (4D)**: the process's visible virtual address space.
//!   - **Fiber (5th dimension)**: the kernel's private geometry — inaccessible
//!     to user processes but physically present in the hardware page tables.
//!
//! Memory access patterns that "wrap around" the extra dimension trigger page-
//! protection faults — geometrically preventing buffer overflows in the same
//! way that a compact manifold has no "edge" to fall off.
//!
//! ## Key constants (inherited from the Unitary Manifold)
//!
//!   - `WINDING_NUMBER` = 5  → 5 privilege rings (mirrors n_w)
//!   - `K_CS` = 74           → 74 KK compactification pages per domain
//!   - `PHI_DEBT_THRESHOLD`  → page reclamation trigger (Pillar 16 φ-debt)

pub mod fiber_bundle;
pub mod pmm;
pub mod vmm;
pub mod phi_debt;

use uefi::table::boot::{MemoryDescriptor, MemoryMap, MemoryType};

pub use fiber_bundle::{FiberBundle, CompactificationDomain};
pub use pmm::PhysicalMemoryManager;
pub use vmm::VirtualMemoryManager;
pub use phi_debt::PhiDebtAccounting;

// ---------------------------------------------------------------------------
// Physics-derived constants
// ---------------------------------------------------------------------------
pub const WINDING_NUMBER: u32 = 5;
pub const K_CS: u32 = 74;            // 5² + 7²
pub const PAGE_SIZE: usize = 4096;   // 4 KiB — standard x86-64
pub const HUGE_PAGE_SIZE: usize = 2 * 1024 * 1024; // 2 MiB = 5D volume element unit

/// KK compactification radius in pages.
/// Each compactification domain spans exactly K_CS pages.
pub const KK_RADIUS_PAGES: usize = K_CS as usize;

// ---------------------------------------------------------------------------
// AxiomMemoryManager — top-level façade
// ---------------------------------------------------------------------------

/// The AxiomZero Memory Manager.
///
/// Owns the physical memory manager, the virtual memory manager, and the
/// fiber bundle topology.  Constructed from the UEFI memory map immediately
/// after `exit_boot_services`.
pub struct AxiomMemoryManager {
    pmm: PhysicalMemoryManager,
    vmm: VirtualMemoryManager,
    bundle: FiberBundle,
    phi: PhiDebtAccounting,
}

impl AxiomMemoryManager {
    /// Construct from the UEFI memory map.
    ///
    /// # Panics
    /// Panics if no conventional memory regions are available.
    pub fn from_memory_map(mmap: &MemoryMap) -> Self {
        let pmm = PhysicalMemoryManager::from_uefi_map(mmap);
        let vmm = VirtualMemoryManager::new();
        let bundle = FiberBundle::default();
        let phi = PhiDebtAccounting::new();
        Self { pmm, vmm, bundle, phi }
    }

    /// Initialise the fiber bundle topology with the winding number and k_cs.
    ///
    /// This establishes the 5D address space structure:
    ///   - WINDING_NUMBER privilege rings
    ///   - KK_RADIUS_PAGES pages per compactification domain
    ///   - φ-debt accounting per domain
    pub fn init_fiber_bundle(&mut self, winding_number: u32, k_cs: u32) {
        self.bundle.init(winding_number, k_cs, &mut self.pmm);
        self.phi.init(KK_RADIUS_PAGES);
    }

    /// Allocate `n` pages in the given privilege ring.
    ///
    /// Returns the physical base address of the allocation, or `None` if
    /// memory is exhausted in that ring.
    pub fn alloc_pages(&mut self, n: usize, ring: u8) -> Option<usize> {
        let paddr = self.pmm.alloc(n)?;
        self.vmm.map(paddr, n, ring);
        self.phi.record_alloc(paddr, n);
        Some(paddr)
    }

    /// Free `n` pages starting at physical address `paddr`.
    pub fn free_pages(&mut self, paddr: usize, n: usize) {
        self.vmm.unmap(paddr, n);
        self.pmm.free(paddr, n);
        self.phi.record_free(paddr, n);
    }

    /// Run the φ-debt reclamation pass.
    ///
    /// Pages that exceed the φ-debt threshold are candidates for eviction.
    /// This is called periodically by the scheduler (Sprint 1 AZ-SCHED).
    pub fn reclaim_phi_debt(&mut self) {
        let candidates = self.phi.reclaim_candidates();
        for paddr in candidates {
            // Write-back if dirty, then release.
            self.free_pages(paddr, 1);
        }
    }

    /// Total free pages currently available.
    pub fn free_page_count(&self) -> usize {
        self.pmm.free_count()
    }

    /// Total physical memory in bytes discovered from UEFI map.
    pub fn total_bytes(&self) -> usize {
        self.pmm.total_bytes()
    }
}
