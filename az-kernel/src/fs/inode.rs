// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/fs/inode.rs — Inode with φ-Debt Accounting

const MAX_INLINE_DATA: usize = 4096; // 4 KiB inline data per inode (Sprint 1)
const PHI_INV: f32 = 0.618_033_988;
const PHI_DEBT_EVICT: f32 = 12.0;

/// An inode representing a file in AZ-FS.
#[derive(Clone)]
pub struct Inode {
    pub ino: u64,
    pub size: usize,
    pub phi_debt: f32,
    pub write_count: u64,
    pub read_count: u64,
    pub name: heapless::String<256>,
    pub data: heapless::Vec<u8, MAX_INLINE_DATA>,
}

impl Inode {
    pub fn new(ino: u64, name: &str) -> Self {
        let mut n = heapless::String::new();
        let _ = n.push_str(name);
        Self {
            ino,
            size: 0,
            phi_debt: 0.0,
            write_count: 0,
            read_count: 0,
            name: n,
            data: heapless::Vec::new(),
        }
    }

    /// Write data into the inode's inline data buffer.
    pub fn write(&mut self, data: &[u8]) -> usize {
        self.data.clear();
        let n = data.len().min(MAX_INLINE_DATA);
        let _ = self.data.extend_from_slice(&data[..n]);
        self.size = n;
        self.write_count += 1;
        self.phi_debt = self.phi_debt * PHI_INV + 1.0; // entropy production
        n
    }

    /// Read data from the inode.
    pub fn read(&mut self, buf: &mut [u8]) -> usize {
        let n = buf.len().min(self.size);
        buf[..n].copy_from_slice(&self.data[..n]);
        self.read_count += 1;
        self.phi_debt = (self.phi_debt * PHI_INV - 0.5).max(0.0); // entropy consumption
        n
    }

    /// True if this inode should be evicted by the φ-debt sweep.
    pub fn should_evict(&self) -> bool {
        self.phi_debt >= PHI_DEBT_EVICT
    }
}
