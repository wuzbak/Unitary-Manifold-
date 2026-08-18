// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026  ThomasCory Walker-Pearson
// AZ-OS ax-kernel: φ-debt page eviction tracker
//
// k_cs = 74 pages per compactification domain.
// Each page accumulates φ-debt; on eviction, select the page with
// the lowest (phi_debt × lru_age) composite score.
//
// Theory: ThomasCory Walker-Pearson | Code: GitHub Copilot (AI)

use heapless::Vec;

/// Pages per KK compactification domain (k_cs = 5² + 7² = 74)
pub const PAGES_PER_DOMAIN: usize = 74;

/// φ⁻¹ in fixed-point (×10000): φ⁻¹ ≈ 0.6180
const PHI_INV_FP: u32 = 6180;

/// A single tracked page
#[derive(Debug, Clone, Copy)]
pub struct PageEntry {
    pub frame: u32,
    /// φ-debt score (0..=10000 fixed-point)
    pub phi_debt: u16,
    /// LRU age counter (incremented on every tick when page not accessed)
    pub lru_age: u32,
}

impl PageEntry {
    pub fn new(frame: u32) -> Self {
        Self { frame, phi_debt: 0, lru_age: 0 }
    }

    /// Composite eviction score: lower = more evictable.
    /// score = phi_debt × (1 + lru_age)
    pub fn eviction_score(&self) -> u64 {
        (self.phi_debt as u64 + 1) * (self.lru_age as u64 + 1)
    }

    /// Decay φ-debt by φ⁻¹ on each tick
    pub fn tick_decay(&mut self) {
        self.phi_debt = (self.phi_debt as u32 * PHI_INV_FP / 10000) as u16;
        self.lru_age = self.lru_age.saturating_add(1);
    }

    /// Access this page: reset LRU age, increase φ-debt
    pub fn access(&mut self, delta_debt: u16) {
        self.lru_age = 0;
        self.phi_debt = self.phi_debt.saturating_add(delta_debt);
    }
}

/// Tracks pages within a single KK compactification domain.
pub struct PhiDebtPageTracker {
    pages: Vec<PageEntry, PAGES_PER_DOMAIN>,
    pub tick: u64,
}

impl PhiDebtPageTracker {
    pub fn new() -> Self {
        Self { pages: Vec::new(), tick: 0 }
    }

    /// Register a page frame for tracking.
    pub fn add_page(&mut self, frame: u32) -> bool {
        self.pages.push(PageEntry::new(frame)).is_ok()
    }

    /// Advance all page scores by one tick.
    pub fn tick(&mut self) {
        self.tick += 1;
        for page in self.pages.iter_mut() {
            page.tick_decay();
        }
    }

    /// Record an access to a specific frame.
    pub fn access(&mut self, frame: u32, delta_debt: u16) {
        if let Some(page) = self.pages.iter_mut().find(|p| p.frame == frame) {
            page.access(delta_debt);
        }
    }

    /// Select the best page to evict (lowest eviction score).
    /// Returns the frame number, or None if no pages tracked.
    pub fn evict_candidate(&self) -> Option<u32> {
        self.pages.iter()
            .min_by_key(|p| p.eviction_score())
            .map(|p| p.frame)
    }

    /// Evict the best candidate and return its frame.
    pub fn evict(&mut self) -> Option<u32> {
        let candidate = self.evict_candidate()?;
        let pos = self.pages.iter().position(|p| p.frame == candidate)?;
        Some(self.pages.remove(pos).frame)
    }

    pub fn page_count(&self) -> usize {
        self.pages.len()
    }
}
