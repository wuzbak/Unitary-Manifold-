// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/fs/ramfs.rs — In-Memory RAM Filesystem

use super::inode::Inode;

const MAX_INODES: usize = 1024;

/// Simple in-memory filesystem backed by a fixed-capacity inode table.
pub struct RamFs {
    inodes: heapless::Vec<Inode, MAX_INODES>,
    next_ino: u64,
}

impl RamFs {
    pub fn new() -> Self {
        Self { inodes: heapless::Vec::new(), next_ino: 1 }
    }

    /// Create a new file.  Returns its inode number.
    pub fn create(&mut self, name: &str) -> Option<u64> {
        if self.inodes.is_full() { return None; }
        let ino = self.next_ino;
        self.next_ino += 1;
        let _ = self.inodes.push(Inode::new(ino, name));
        Some(ino)
    }

    /// Write data to the inode with the given number.
    pub fn write(&mut self, ino: u64, data: &[u8]) -> usize {
        self.inodes.iter_mut()
            .find(|i| i.ino == ino)
            .map(|i| i.write(data))
            .unwrap_or(0)
    }

    /// Read data from the inode with the given number.
    pub fn read(&mut self, ino: u64, buf: &mut [u8]) -> usize {
        self.inodes.iter_mut()
            .find(|i| i.ino == ino)
            .map(|i| i.read(buf))
            .unwrap_or(0)
    }

    /// Delete a file (φ-debt resolved: inode removed from table).
    pub fn delete(&mut self, ino: u64) -> bool {
        if let Some(pos) = self.inodes.iter().position(|i| i.ino == ino) {
            self.inodes.swap_remove(pos);
            true
        } else {
            false
        }
    }

    /// Run the φ-debt eviction sweep.
    pub fn evict_phi_debt(&mut self) {
        self.inodes.retain(|i| !i.should_evict());
    }

    pub fn file_count(&self) -> usize { self.inodes.len() }
}
