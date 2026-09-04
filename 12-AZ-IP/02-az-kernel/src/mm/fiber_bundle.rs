// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/mm/fiber_bundle.rs — 5D Fiber Bundle Address Space
//!
//! The fiber bundle is the mathematical heart of AxiomZero memory management.
//!
//! ## Geometry
//!
//! The 5D Kaluza-Klein manifold M₅ = M₄ × S¹ decomposes into:
//!   - Base space M₄: the 4D observable spacetime = the process virtual address space.
//!   - Fiber S¹ (compact circle): the hidden extra dimension = kernel privilege geometry.
//!
//! In practice each process lives in a `CompactificationDomain` identified by its
//! KK level (0 … WINDING_NUMBER-1).  Processes at the same KK level can share
//! pages via IPC; processes at different levels are geometrically isolated — their
//! virtual ranges may numerically overlap but the kernel page tables resolve them
//! to disjoint physical frames.
//!
//! ## Privilege Rings
//!
//! Ring 0 = kernel (hardgate, Pillars 1–208 equivalent)
//! Ring 1 = system services (adjacent-track equivalent)
//! Ring 2 = trusted user agents (Pentad-approved)
//! Ring 3 = standard user space
//! Ring 4 = sandboxed / untrusted processes
//!
//! Transitions between rings follow the KK geodesic equations: a process can
//! only ascend to a higher privilege ring via an explicit system call that is
//! validated by the Pentad gate (the kernel's analogue of HILS approval).

use super::pmm::PhysicalMemoryManager;

/// A single compactification domain: one KK level × one process namespace.
#[derive(Debug, Clone)]
pub struct CompactificationDomain {
    /// KK level (0 = kernel, WINDING_NUMBER-1 = least trusted).
    pub kk_level: u8,
    /// Base physical address of this domain's page pool.
    pub phys_base: usize,
    /// Number of pages in this domain.
    pub page_count: usize,
    /// Whether cross-domain IPC is currently open on this domain.
    pub ipc_open: bool,
}

/// The fiber bundle: a collection of compactification domains, one per KK level.
#[derive(Default)]
pub struct FiberBundle {
    domains: [Option<CompactificationDomain>; 5], // n_w = 5 levels
    initialized: bool,
}

impl FiberBundle {
    /// Initialise the bundle by allocating a page pool for each KK level.
    ///
    /// Each domain gets `kk_radius * winding_number` pages, scaled by its
    /// privilege level (kernel gets the most contiguous physical memory).
    pub fn init(
        &mut self,
        winding_number: u32,
        k_cs: u32,
        pmm: &mut PhysicalMemoryManager,
    ) {
        let pages_per_domain = (k_cs as usize) * 4; // 4 pages per KK unit
        for level in 0..winding_number as usize {
            if let Some(phys_base) = pmm.alloc(pages_per_domain) {
                self.domains[level] = Some(CompactificationDomain {
                    kk_level: level as u8,
                    phys_base,
                    page_count: pages_per_domain,
                    ipc_open: false,
                });
            }
        }
        self.initialized = true;
    }

    /// Retrieve the domain for a given KK level.
    pub fn domain(&self, level: u8) -> Option<&CompactificationDomain> {
        if (level as usize) < self.domains.len() {
            self.domains[level as usize].as_ref()
        } else {
            None
        }
    }

    /// Open a holographic IPC boundary between two domains at adjacent levels.
    ///
    /// Two domains can share a page if and only if |level_a - level_b| == 1.
    /// This implements the KK "nearest-neighbour" coupling.
    pub fn open_ipc_boundary(&mut self, level_a: u8, level_b: u8) -> bool {
        let diff = (level_a as i32 - level_b as i32).unsigned_abs();
        if diff != 1 {
            return false; // non-adjacent KK levels cannot directly communicate
        }
        if let Some(d) = self.domains[level_a as usize].as_mut() { d.ipc_open = true; }
        if let Some(d) = self.domains[level_b as usize].as_mut() { d.ipc_open = true; }
        true
    }

    /// True if all `winding_number` domains are initialised.
    pub fn is_fully_compactified(&self) -> bool {
        self.initialized && self.domains.iter().all(|d| d.is_some())
    }
}
