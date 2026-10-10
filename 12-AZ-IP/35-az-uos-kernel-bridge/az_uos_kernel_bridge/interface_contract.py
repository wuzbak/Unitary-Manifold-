# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Phase-0 interface contract: what UOS's Python-prototyped
`GeodesicScheduler` primitives would need to look like as Rust trait
implementations callable from `kk_channel.rs`.

This is design-only — a typed Python ``Protocol`` describing the contract,
not a Rust trait definition. It exists so the contract can be written down,
reviewed, and tested against UOS's actual scheduler shape before any Rust
code is written (Phase 0, per article-354 direction #8).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable


@runtime_checkable
class GeodesicSchedulable(Protocol):
    """The minimal contract a process descriptor must satisfy to be
    scheduled by a geometric, winding-aware scheduler — mirrors
    `UOS.scheduler.ProcessGeodesic`'s public shape field-for-field."""

    pid: int
    priority: float
    phi_weight: float
    state_vector: Sequence[float]

    def affinity_score(self, phi_gradient: Sequence[float]) -> float:
        ...


@dataclass(frozen=True)
class RustTraitFieldSpec:
    """One field or method a Rust trait implementation would need."""

    name: str
    rust_type: str
    description: str


#: The explicit interface contract: every field/method a Rust
#: `GeodesicSchedulable`-equivalent trait would need, with Rust-side types.
GEODESIC_SCHEDULABLE_RUST_CONTRACT = (
    RustTraitFieldSpec("pid", "u64", "Unique process identifier"),
    RustTraitFieldSpec("priority", "f32", "Scheduling weight, clamped to [0.0, 1.0]"),
    RustTraitFieldSpec("phi_weight", "f32", "Radion-field affinity weight"),
    RustTraitFieldSpec("state_vector", "[f32; 5]", "Position in 5D phase space (PHASE_DIM = WINDING_NUMBER = 5)"),
    RustTraitFieldSpec(
        "affinity_score",
        "fn(&self, phi_gradient: &[f32; 5]) -> f32",
        "priority * phi_weight * (1.0 + dot(state_vector, phi_gradient))",
    ),
)


def validate_schedulable(candidate: object) -> bool:
    """Check whether a Python object satisfies the `GeodesicSchedulable`
    contract — the same contract a Rust trait implementation would need to
    satisfy, expressed here so it can be checked before porting."""
    return isinstance(candidate, GeodesicSchedulable)
