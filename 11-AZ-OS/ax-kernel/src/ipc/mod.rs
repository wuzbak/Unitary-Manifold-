// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026  ThomasCory Walker-Pearson
// AZ-OS ax-kernel/src/ipc/mod.rs

pub mod kk_channel;
pub use kk_channel::{KKChannel, KKMessage, Ring, KKAdjacent};
