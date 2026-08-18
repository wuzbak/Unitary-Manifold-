// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026  ThomasCory Walker-Pearson
// AZ-OS ax-kernel: Weighted Round-Robin Scheduler
//
// Physics mapping:
//   KK level 0 (kernel) → highest priority (weight = 5)
//   KK level 4 (user)   → lowest priority  (weight = 1)
//   Weights = KK_LEVELS + 1 - level
//
// Theory: ThomasCory Walker-Pearson | Code: GitHub Copilot (AI)

use heapless::Vec;

/// Number of KK privilege rings (= winding number n_w = 5)
pub const KK_LEVELS: usize = 5;

/// Weight for each KK level: level 0 → 5, level 4 → 1
pub const fn kk_weight(level: usize) -> usize {
    KK_LEVELS - level
}

/// Process state machine
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProcessState {
    Ready,
    Running,
    Blocked,
    Preempted,
    Terminated,
}

/// φ-debt entropy score (0.0 = no debt; 1.0 = full entropy)
/// Stored as fixed-point u16 (0..=10000 maps to 0.0..=1.0)
#[derive(Debug, Clone, Copy)]
pub struct PhiDebt(pub u16);

impl PhiDebt {
    pub const ZERO: Self = PhiDebt(0);
    pub const MAX: Self = PhiDebt(10000);

    /// Decay φ-debt by the golden-ratio inverse (φ⁻¹ ≈ 0.618)
    pub fn decay(&mut self) {
        // φ⁻¹ ≈ 6180/10000
        self.0 = (self.0 as u32 * 6180 / 10000) as u16;
    }
}

/// A process control block
#[derive(Debug, Clone)]
pub struct Process {
    pub pid: u32,
    pub kk_level: usize,
    pub state: ProcessState,
    pub phi_debt: PhiDebt,
    /// Remaining time-slice ticks in the current quantum
    pub remaining_ticks: usize,
    /// Total accumulated ticks
    pub accumulated: u64,
}

impl Process {
    pub fn new(pid: u32, kk_level: usize) -> Self {
        let level = kk_level.min(KK_LEVELS - 1);
        Self {
            pid,
            kk_level: level,
            state: ProcessState::Ready,
            phi_debt: PhiDebt::ZERO,
            remaining_ticks: kk_weight(level),
            accumulated: 0,
        }
    }
}

/// Weighted Round-Robin Scheduler
///
/// Each process gets a time quantum proportional to its KK weight.
/// Higher KK level → lower priority → shorter quantum.
/// Preemption occurs when a lower-level (higher-priority) process becomes ready
/// while a higher-level process is running.
pub struct Scheduler {
    /// Ready queue: indexed by KK level (0 = highest priority)
    queues: [Vec<Process, 32>; KK_LEVELS],
    /// Currently running process (if any)
    running: Option<Process>,
    /// Total tick counter
    pub tick_count: u64,
}

impl Scheduler {
    pub fn new() -> Self {
        Self {
            queues: Default::default(),
            running: None,
            tick_count: 0,
        }
    }

    /// Add a process to the ready queue.
    pub fn add_process(&mut self, proc: Process) {
        let level = proc.kk_level.min(KK_LEVELS - 1);
        let _ = self.queues[level].push(proc);
    }

    /// Execute one scheduler tick.
    /// Returns the PID of the running process, or None if idle.
    pub fn tick(&mut self) -> Option<u32> {
        self.tick_count += 1;

        // Preemption check: if a higher-priority process is ready while a
        // lower-priority process is running, preempt.
        if let Some(ref running) = self.running {
            let running_level = running.kk_level;
            for higher in 0..running_level {
                if !self.queues[higher].is_empty() {
                    // Preempt: move running back to its queue
                    let mut preempted = self.running.take().unwrap();
                    preempted.state = ProcessState::Preempted;
                    preempted.remaining_ticks = kk_weight(preempted.kk_level);
                    let _ = self.queues[preempted.kk_level].push(preempted);
                    break;
                }
            }
        }

        // If no process is running, pick the next one
        if self.running.is_none() {
            'outer: for level in 0..KK_LEVELS {
                if !self.queues[level].is_empty() {
                    let mut proc = self.queues[level].remove(0);
                    proc.state = ProcessState::Running;
                    proc.phi_debt.decay();
                    self.running = Some(proc);
                    break 'outer;
                }
            }
        }

        // Advance the running process
        if let Some(ref mut proc) = self.running {
            proc.accumulated += 1;
            proc.remaining_ticks = proc.remaining_ticks.saturating_sub(1);
            let pid = proc.pid;

            if proc.remaining_ticks == 0 {
                // Quantum expired: re-queue
                let mut done = self.running.take().unwrap();
                done.state = ProcessState::Ready;
                done.remaining_ticks = kk_weight(done.kk_level);
                let _ = self.queues[done.kk_level].push(done);
            }

            return Some(pid);
        }

        None
    }

    /// Preempt a specific process by PID.
    pub fn preempt(&mut self, pid: u32) -> bool {
        if let Some(ref proc) = self.running {
            if proc.pid == pid {
                let mut preempted = self.running.take().unwrap();
                preempted.state = ProcessState::Preempted;
                preempted.remaining_ticks = kk_weight(preempted.kk_level);
                let _ = self.queues[preempted.kk_level].push(preempted);
                return true;
            }
        }
        false
    }

    /// Terminate a process by PID, removing it from queues or running slot.
    pub fn terminate(&mut self, pid: u32) -> bool {
        if let Some(ref proc) = self.running {
            if proc.pid == pid {
                self.running = None;
                return true;
            }
        }
        for level in 0..KK_LEVELS {
            if let Some(pos) = self.queues[level].iter().position(|p| p.pid == pid) {
                self.queues[level].remove(pos);
                return true;
            }
        }
        false
    }
}
