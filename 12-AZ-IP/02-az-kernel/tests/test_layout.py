# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
from pathlib import Path

def test_kernel_merge_preserved_unique_files():
    root = Path(__file__).resolve().parents[1]
    assert (root / '.cargo/config.toml').exists()
    assert (root / 'src/ipc/kk_channel.rs').exists()
    assert (root / 'assets/font8x16.bin').exists()
    assert (root / 'scripts/build.sh').exists()
