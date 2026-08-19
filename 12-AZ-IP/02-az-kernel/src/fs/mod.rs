// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/fs/mod.rs — AZ-FS: φ-Debt RAM Filesystem
//!
//! ## Architecture
//!
//! AZ-FS is a log-structured in-memory filesystem where the journal uses the
//! φ-debt entropy accounting from Pillar 16 (`recycling/`).
//!
//! ### File ↔ Pillar Mapping
//!   - File creation   = pillar addition operation (hardgate validated)
//!   - File deletion   = φ-debt resolution
//!   - File write      = φ-debt accrual (entropy production)
//!   - File read       = φ-debt consumption (entropy reduction)
//!
//! ### Inode structure
//! Each inode carries a φ-debt score.  The filesystem background task
//! periodically sweeps inodes with debt above the threshold and evicts
//! their pages from the page cache (calling back into AZ-MM).
//!
//! Sprint 1: RAM filesystem only (data in physical pages).
//! Sprint 3: NVMe driver integration for persistent storage.

pub mod ramfs;
pub mod inode;

pub use ramfs::RamFs;
pub use inode::Inode;

use spin::Mutex;

static FS: Mutex<Option<RamFs>> = Mutex::new(None);

/// Initialise the root RAM filesystem.  Called once during kernel boot.
pub fn init() {
    let mut guard = FS.lock();
    *guard = Some(RamFs::new());
}

/// Create a file at the given path.  Returns the inode number or None.
pub fn create_file(path: &str) -> Option<u64> {
    FS.lock().as_mut()?.create(path)
}

/// Write bytes to a file.  Returns bytes written.
pub fn write_file(ino: u64, data: &[u8]) -> usize {
    FS.lock().as_mut().map(|fs| fs.write(ino, data)).unwrap_or(0)
}

/// Read bytes from a file.  Returns bytes read.
pub fn read_file(ino: u64, buf: &mut [u8]) -> usize {
    FS.lock().as_mut().map(|fs| fs.read(ino, buf)).unwrap_or(0)
}

/// Delete a file.  Resolves its φ-debt.
pub fn delete_file(ino: u64) -> bool {
    FS.lock().as_mut().map(|fs| fs.delete(ino)).unwrap_or(false)
}
