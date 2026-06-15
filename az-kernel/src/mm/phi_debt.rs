// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/mm/phi_debt.rs — φ-Debt Entropy Accounting for Memory
//!
//! ## Pillar 16 — φ-Debt Recycling Applied to Memory Management
//!
//! Pages accumulate "entropy debt" based on their access and modification
//! patterns.  A page that is:
//!   - Written frequently but rarely read → high debt (producer without consumer)
//!   - Read frequently but never written  → zero debt (pure consumer)
//!   - Neither read nor written in N ticks → accumulates age debt
//!
//! When a page's φ-debt exceeds `PHI_DEBT_THRESHOLD`, it becomes a
//! reclamation candidate.  This replaces conventional LRU aging with an
//! information-theoretically grounded algorithm derived from Pillar 16.
//!
//! ## Formula
//!
//!   φ_debt(t+1) = φ_debt(t) × φ⁻¹ + Δwrite(t) − Δread(t)
//!
//! where φ = (1 + √5) / 2 ≈ 1.618 (golden ratio) and the decay term
//! φ⁻¹ ≈ 0.618 ensures debt naturally diminishes when not stimulated.

const PHI_INV: f32 = 0.618_033_988; // φ⁻¹ = 2/(1+√5)
const PHI_DEBT_THRESHOLD: f32 = 8.0; // pages above this are reclamation candidates
const MAX_TRACKED_PAGES: usize = 8192;

/// Per-page φ-debt accounting entry.
#[derive(Clone, Copy, Default)]
pub struct PageDebt {
    pub phys_addr: usize,
    pub debt: f32,
    pub age_ticks: u32,
}

/// φ-Debt Accounting subsystem.
pub struct PhiDebtAccounting {
    pages: heapless::Vec<PageDebt, MAX_TRACKED_PAGES>,
    kk_radius: usize,
}

impl PhiDebtAccounting {
    pub fn new() -> Self {
        Self { pages: heapless::Vec::new(), kk_radius: 0 }
    }

    pub fn init(&mut self, kk_radius: usize) {
        self.kk_radius = kk_radius;
    }

    /// Record a new allocation.  New pages start with zero debt.
    pub fn record_alloc(&mut self, paddr: usize, n_pages: usize) {
        for i in 0..n_pages {
            let _ = self.pages.push(PageDebt {
                phys_addr: paddr + i * super::PAGE_SIZE,
                debt: 0.0,
                age_ticks: 0,
            });
        }
    }

    /// Record a free.  Remove the entry from the table.
    pub fn record_free(&mut self, paddr: usize, n_pages: usize) {
        for i in 0..n_pages {
            let addr = paddr + i * super::PAGE_SIZE;
            self.pages.retain(|p| p.phys_addr != addr);
        }
    }

    /// Update debt for a write access.
    pub fn record_write(&mut self, paddr: usize) {
        if let Some(p) = self.find_mut(paddr) {
            p.debt = p.debt * PHI_INV + 1.0;
        }
    }

    /// Update debt for a read access (debt decreases).
    pub fn record_read(&mut self, paddr: usize) {
        if let Some(p) = self.find_mut(paddr) {
            p.debt = (p.debt * PHI_INV - 0.5).max(0.0);
        }
    }

    /// Advance the clock by one scheduler tick.  All pages age; orphan debt grows.
    pub fn tick(&mut self) {
        for p in self.pages.iter_mut() {
            p.age_ticks += 1;
            // Orphan aging: pages untouched for many ticks accumulate age debt.
            if p.age_ticks % 64 == 0 {
                p.debt += 0.1;
            }
        }
    }

    /// Return physical addresses of pages whose φ-debt exceeds the threshold.
    pub fn reclaim_candidates(&self) -> heapless::Vec<usize, 256> {
        let mut out = heapless::Vec::new();
        for p in self.pages.iter() {
            if p.debt >= PHI_DEBT_THRESHOLD {
                let _ = out.push(p.phys_addr);
            }
        }
        out
    }

    fn find_mut(&mut self, paddr: usize) -> Option<&mut PageDebt> {
        self.pages.iter_mut().find(|p| p.phys_addr == paddr)
    }
}
