// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/sched/process.rs — Process Descriptor

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct ProcessId(pub u32);

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum ProcessState {
    Ready,
    Running,
    Blocked,
    Zombie,
}

/// Process Control Block (PCB) — the kernel's representation of a process.
///
/// The 5 metric components mirror the 5D KK metric tensor components.
/// Each component contributes to the geodesic distance calculation in AZ-SCHED.
#[derive(Clone, Debug)]
pub struct Process {
    pub pid: ProcessId,
    pub state: ProcessState,
    pub priority: u8,           // 0 (highest) to 4 (lowest) — mirrors KK ring
    pub initial_quantum: u32,   // initial time slice in scheduler ticks
    pub remaining_quantum: u32,
    // 5D metric components for geodesic computation
    pub cpu_remaining: u32,     // estimated CPU ticks to completion
    pub mem_pages: u32,         // memory footprint (pages)
    pub io_pending: u32,        // outstanding I/O operations
    pub age_ticks: u64,         // age since creation (prevents starvation)
    pub phi_debt: f32,          // φ-debt accumulated by this process
    // Pentad clearance bits (5 bits, one per axiom)
    pub pentad_clearance: u8,
}

impl Process {
    pub fn new(pid: ProcessId, priority: u8, cpu_budget: u32, mem_pages: u32) -> Self {
        let quantum = match priority {
            0 => 100, // kernel: large quantum
            1 => 50,
            2 => 25,
            3 => 10,
            4 => 5,   // sandbox: short quantum
            _ => 10,
        };
        Self {
            pid,
            state: ProcessState::Ready,
            priority,
            initial_quantum: quantum,
            remaining_quantum: quantum,
            cpu_remaining: cpu_budget,
            mem_pages,
            io_pending: 0,
            age_ticks: 0,
            phi_debt: 0.0,
            pentad_clearance: 0b00001 << (4 - priority.min(4)), // ring 0 gets all bits
        }
    }
}
