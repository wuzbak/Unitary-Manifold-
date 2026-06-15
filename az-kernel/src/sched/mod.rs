// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/sched/mod.rs — AZ-SCHED: Geodesic Process Scheduler
//!
//! # Sprint 1: Physics-Derived Scheduling
//!
//! ## Geodesic Scheduling
//!
//! The scheduler solves the geodesic equation in process-state space to
//! determine which process to run next.  The geodesic is the "shortest path"
//! between the current process state and its completion, under the constraint
//! that CPU time is the metric tensor's temporal component.
//!
//! ## Metric Tensor
//!
//! In process-state space, the effective metric is:
//!
//!   g_μν = diag(cpu_weight, mem_weight, io_weight, age_weight, priority_weight)
//!
//! where the weights are the 5 components of the KK metric projections.  The
//! geodesic distance from a process to completion is approximated by:
//!
//!   d = √( Σᵢ gᵢᵢ × (remaining_work_i)² )
//!
//! Processes with the smallest geodesic distance are scheduled first — they
//! are "geometrically closest" to completion in process-state space.
//!
//! ## Interrupt Rings
//!
//! The n_w = 5 winding number maps to 5 interrupt priority rings:
//!   Ring 0: Non-Maskable Interrupts (NMI) — kernel fault, watchdog
//!   Ring 1: Timer / scheduler tick
//!   Ring 2: Device interrupts (Sprint 3: PCI-E, USB)
//!   Ring 3: Syscall / software interrupts
//!   Ring 4: Idle / background agents

pub mod process;
pub mod geodesic;

pub use process::{Process, ProcessState, ProcessId};
pub use geodesic::GeodesicCache;

use crate::framebuffer::AxiomFramebuffer;

const MAX_PROCESSES: usize = 64;
const TICK_HZ: u32 = 1000; // 1 ms scheduling tick

/// The AxiomZero Geodesic Scheduler.
pub struct AxiomScheduler {
    processes: heapless::Vec<Process, MAX_PROCESSES>,
    geo_cache: GeodesicCache,
    interrupt_rings: u32,
    tick_count: u64,
    current_pid: Option<ProcessId>,
}

impl AxiomScheduler {
    pub fn new(interrupt_rings: u32) -> Self {
        Self {
            processes: heapless::Vec::new(),
            geo_cache: GeodesicCache::new(),
            interrupt_rings,
            tick_count: 0,
            current_pid: None,
        }
    }

    /// Pre-compute the geodesic cache for all process classes.
    /// Called once at boot (Sprint 1).  Updated incrementally as processes spawn.
    pub fn init_geodesic_cache(&mut self) {
        self.geo_cache.init(self.interrupt_rings);
    }

    /// Spawn a new process and add it to the ready queue.
    pub fn spawn(&mut self, priority: u8, cpu_budget: u32, mem_pages: u32) -> Option<ProcessId> {
        if self.processes.is_full() { return None; }
        let pid = ProcessId(self.processes.len() as u32);
        let proc = Process::new(pid, priority, cpu_budget, mem_pages);
        let _ = self.processes.push(proc);
        self.geo_cache.register(pid, priority, cpu_budget, mem_pages);
        Some(pid)
    }

    /// Select the next process to run using the geodesic distance metric.
    ///
    /// Returns the PID of the process with the smallest geodesic distance to
    /// completion (i.e., the "most ready" process in 5D process-state space).
    pub fn select_next(&mut self) -> Option<ProcessId> {
        let mut best_pid: Option<ProcessId> = None;
        let mut best_dist = f32::MAX;
        for proc in self.processes.iter() {
            if proc.state != ProcessState::Ready { continue; }
            let dist = self.geo_cache.geodesic_distance(proc.pid);
            if dist < best_dist {
                best_dist = dist;
                best_pid = Some(proc.pid);
            }
        }
        best_pid
    }

    /// Advance the scheduler by one tick.  Called from the timer interrupt handler.
    pub fn tick(&mut self) {
        self.tick_count += 1;
        // Preempt the current process if its quantum is exhausted.
        if let Some(pid) = self.current_pid {
            if let Some(proc) = self.processes.iter_mut().find(|p| p.pid == pid) {
                proc.remaining_quantum = proc.remaining_quantum.saturating_sub(1);
                if proc.remaining_quantum == 0 {
                    proc.state = ProcessState::Ready;
                    proc.remaining_quantum = proc.initial_quantum;
                    self.current_pid = None;
                }
            }
        }
        // Select the next process.
        if self.current_pid.is_none() {
            if let Some(next) = self.select_next() {
                if let Some(proc) = self.processes.iter_mut().find(|p| p.pid == next) {
                    proc.state = ProcessState::Running;
                    self.current_pid = Some(next);
                }
            }
        }
        // Update geodesic cache periodically (every 100 ticks).
        if self.tick_count % 100 == 0 {
            self.geo_cache.update_all(&self.processes);
        }
    }

    /// The main kernel event loop (Sprint 0: spins; Sprint 1: runs processes).
    pub fn run_event_loop(&mut self, fb: &mut AxiomFramebuffer) -> ! {
        loop {
            self.tick();
            // In Sprint 0/1: display tick counter every 1000 ticks.
            if self.tick_count % 1000 == 0 {
                // Status update — minimise framebuffer writes (expensive).
                extern crate alloc;
                use alloc::format;
                let msg = format!("AZ-SCHED tick: {}  |  procs: {}",
                    self.tick_count, self.processes.len());
                fb.draw_status_line(&msg);
            }
            // Sprint 3: HLT between ticks to conserve power.
            #[cfg(target_arch = "x86_64")]
            unsafe { core::arch::asm!("hlt", options(nomem, nostack)); }
        }
    }
}
