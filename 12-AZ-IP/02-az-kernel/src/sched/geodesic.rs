// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/sched/geodesic.rs — Geodesic Distance Cache
//!
//! Pre-computes and caches geodesic distances in process-state space.
//!
//! ## Metric
//!
//!   g = diag(w_cpu, w_mem, w_io, w_age, w_phi)
//!
//! where the weights are derived from the KK metric projection:
//!   w_cpu  = 1.0      (primary work component)
//!   w_mem  = 0.5      (resource consumption)
//!   w_io   = 2.0      (I/O dominates when present)
//!   w_age  = 0.01     (prevents starvation)
//!   w_phi  = 0.618    (φ-debt component = φ⁻¹)
//!
//! Geodesic distance:
//!   d(proc) = √( w_cpu×cpu² + w_mem×mem² + w_io×io² + w_age×age² + w_phi×φ² )

use super::process::{Process, ProcessId};

const W_CPU:  f32 = 1.0;
const W_MEM:  f32 = 0.5;
const W_IO:   f32 = 2.0;
const W_AGE:  f32 = 0.01;
const W_PHI:  f32 = 0.618_034; // φ⁻¹

#[derive(Clone, Copy, Default)]
struct CacheEntry {
    pid: u32,
    distance: f32,
}

const CACHE_SIZE: usize = 64;

pub struct GeodesicCache {
    entries: heapless::Vec<CacheEntry, CACHE_SIZE>,
    rings: u32,
}

impl GeodesicCache {
    pub fn new() -> Self {
        Self { entries: heapless::Vec::new(), rings: 5 }
    }

    pub fn init(&mut self, rings: u32) {
        self.rings = rings;
    }

    /// Register a new process in the cache.
    pub fn register(&mut self, pid: ProcessId, _priority: u8, cpu_budget: u32, mem_pages: u32) {
        let entry = CacheEntry {
            pid: pid.0,
            distance: Self::compute(cpu_budget as f32, mem_pages as f32, 0.0, 0.0, 0.0),
        };
        let _ = self.entries.push(entry);
    }

    /// Return the cached geodesic distance for a process.
    pub fn geodesic_distance(&self, pid: ProcessId) -> f32 {
        self.entries.iter()
            .find(|e| e.pid == pid.0)
            .map(|e| e.distance)
            .unwrap_or(f32::MAX)
    }

    /// Update all cache entries from the current process list.
    pub fn update_all(&mut self, processes: &heapless::Vec<Process, 64>) {
        for entry in self.entries.iter_mut() {
            if let Some(proc) = processes.iter().find(|p| p.pid.0 == entry.pid) {
                entry.distance = Self::compute(
                    proc.cpu_remaining as f32,
                    proc.mem_pages as f32,
                    proc.io_pending as f32,
                    proc.age_ticks as f32,
                    proc.phi_debt,
                );
            }
        }
    }

    fn compute(cpu: f32, mem: f32, io: f32, age: f32, phi: f32) -> f32 {
        let d2 = W_CPU * cpu * cpu
                + W_MEM * mem * mem
                + W_IO  * io  * io
                + W_AGE * age * age
                + W_PHI * phi * phi;
        libm::sqrtf(d2)
    }
}
