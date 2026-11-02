// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/lib.rs — Host-Testable Kernel Logic Library
//!
//! The kernel binary (`main.rs`) is `#![no_std] #![no_main]` and targets
//! `x86_64-unknown-uefi` exclusively — it cannot be unit-tested with the
//! normal host `cargo test` harness, since there is no OS loader to run a
//! UEFI binary on the host and no `std` test runner inside `no_main`.
//!
//! This crate factors every hardware-independent subsystem (the heap
//! allocator, physical/virtual memory bookkeeping, the φ-debt RAM
//! filesystem, the IPC ring buffers and channel table, and the scheduler's
//! pure-logic pieces) into a library that is `no_std` for the real kernel
//! build but compiles with `std` under `cargo test`, so its unit tests run
//! natively on the host with full `cargo test` tooling (panics, assertions,
//! `#[should_panic]`, etc. all work normally).
//!
//! Run with: `cargo test --lib` (the `[[bin]]` target is UEFI-only and is
//! intentionally not part of the default host test build; see README.md).
#![cfg_attr(not(test), no_std)]

extern crate alloc;

pub mod drv;
pub mod fs;
pub mod framebuffer;
pub mod ipc;
pub mod mm;
pub mod sched;
