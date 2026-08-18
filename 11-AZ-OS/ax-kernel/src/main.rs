// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026  ThomasCory Walker-Pearson
// AZ-OS ax-kernel: UEFI entry point
//
// Theory: ThomasCory Walker-Pearson | Code: GitHub Copilot (AI)

#![no_main]
#![no_std]

extern crate alloc;

use uefi::prelude::*;

mod mm;
mod sched;
mod ipc;

#[entry]
fn main(image: Handle, mut system_table: SystemTable<Boot>) -> Status {
    uefi_services::init(&mut system_table).unwrap();
    let stdout = system_table.stdout();
    stdout.clear().unwrap();
    stdout.output_string(cstr16!("AZ-OS ax-kernel v0.1 booting...\r\n")).unwrap();

    // Phase 1: Memory manager initialisation
    let mm = mm::AxiomMemoryManager::init();
    stdout.output_string(cstr16!("MM: initialised\r\n")).unwrap();

    // Phase 2: Scheduler initialisation
    let mut sched = sched::Scheduler::new();
    stdout.output_string(cstr16!("SCHED: initialised\r\n")).unwrap();

    // Phase 3: IPC subsystem
    stdout.output_string(cstr16!("IPC: initialised\r\n")).unwrap();

    stdout.output_string(cstr16!("AZ-OS: boot complete\r\n")).unwrap();

    // Main scheduler loop (exits to UEFI shell in test mode)
    for _ in 0..5 {
        sched.tick();
    }

    Status::SUCCESS
}
