# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ UOS/AZ-KERNEL Bridge — Product 35.

Phases 0-1 of article-354 direction #8 ("UOS on AZ-KERNEL"): Phase 0 is the
written interface contract between UOS's Python-prototyped scheduling
primitives and a Rust trait implementation callable from `kk_channel.rs`.
Phase 1 is the winding-aware addressing scheme for `kk_channel.rs`'s ring
IPC primitive, with a cross-check against the actual Rust source.

Epistemic status: Phase 2 (a minimal geometric scheduler ported to real
QEMU boot semantics) and Phase 3 (honest TRL reassessment of both products)
are **not** part of this product — they require porting work inside
`02-az-kernel`'s own Rust codebase and a real QEMU run.
"""

from .interface_contract import (
    GeodesicSchedulable,
    RustTraitFieldSpec,
    GEODESIC_SCHEDULABLE_RUST_CONTRACT,
    validate_schedulable,
)
from .addressing import (
    N_RINGS,
    WindingAddress,
    parse_rust_adjacency_pairs,
    winding_adjacency_pairs,
    validate_against_kk_channel_rs,
)

__all__ = [
    "GeodesicSchedulable",
    "RustTraitFieldSpec",
    "GEODESIC_SCHEDULABLE_RUST_CONTRACT",
    "validate_schedulable",
    "N_RINGS",
    "WindingAddress",
    "parse_rust_adjacency_pairs",
    "winding_adjacency_pairs",
    "validate_against_kk_channel_rs",
]

__version__ = "1.0.0"
