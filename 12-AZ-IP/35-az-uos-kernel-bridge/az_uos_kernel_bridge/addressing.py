# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Winding-aware addressing scheme — Phase 1 of article-354 direction #8.

`12-AZ-IP/02-az-kernel/src/ipc/kk_channel.rs` already enforces a ring
adjacency rule at compile time (ring i may talk only to ring i±1, mod 5
rings, wrapping 0↔4). This module gives that rule an explicit, winding-
number-aware Python reference implementation and a parser that extracts
the actual adjacency pairs out of the Rust source, so the two
representations can be cross-checked against each other rather than
trusted independently.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet, Tuple

from ._repo import ensure_repo_on_path

_REPO_ROOT = ensure_repo_on_path()

KK_CHANNEL_RS_PATH = _REPO_ROOT / "12-AZ-IP" / "02-az-kernel" / "src" / "ipc" / "kk_channel.rs"

#: Number of rings in the toroidal KK topology (matches WINDING_NUMBER = 5).
N_RINGS = 5

_ADJACENCY_IMPL_RE = re.compile(
    r"impl\s+KKAdjacent<Ring<(\d+)>,\s*Ring<(\d+)>>\s+for\s+\(\)\s*\{\}"
)


def parse_rust_adjacency_pairs(rust_source: str | None = None) -> FrozenSet[Tuple[int, int]]:
    """Extract every ``impl KKAdjacent<Ring<A>, Ring<B>> for ()`` pair from
    `kk_channel.rs`. Returns a frozenset of ``(from_ring, to_ring)`` tuples,
    exactly as declared in the Rust source — no normalization applied."""
    if rust_source is None:
        rust_source = KK_CHANNEL_RS_PATH.read_text(encoding="utf-8")
    return frozenset(
        (int(a), int(b)) for a, b in _ADJACENCY_IMPL_RE.findall(rust_source)
    )


@dataclass(frozen=True)
class WindingAddress:
    """A ring address in the toroidal, winding-number-aware KK topology."""

    ring: int

    def __post_init__(self) -> None:
        if not 0 <= self.ring < N_RINGS:
            raise ValueError(f"ring must be in [0, {N_RINGS}), got {self.ring}")

    def is_adjacent_to(self, other: "WindingAddress") -> bool:
        """Two rings are adjacent iff they differ by 1 modulo N_RINGS —
        the winding-aware addressing rule, independent of any particular
        implementation. Reproduces the wraparound 0<->4 adjacency that
        `kk_channel.rs` declares explicitly."""
        diff = abs(self.ring - other.ring) % N_RINGS
        return diff == 1 or diff == N_RINGS - 1

    def neighbors(self) -> Tuple["WindingAddress", "WindingAddress"]:
        return (
            WindingAddress((self.ring - 1) % N_RINGS),
            WindingAddress((self.ring + 1) % N_RINGS),
        )


def winding_adjacency_pairs() -> FrozenSet[Tuple[int, int]]:
    """Every adjacent (from_ring, to_ring) pair the winding-aware
    addressing rule predicts, in both directions."""
    pairs = set()
    for i in range(N_RINGS):
        for j in range(N_RINGS):
            if i != j and WindingAddress(i).is_adjacent_to(WindingAddress(j)):
                pairs.add((i, j))
    return frozenset(pairs)


def validate_against_kk_channel_rs() -> dict:
    """Cross-check the Python winding-aware addressing rule against the
    actual adjacency pairs declared in `kk_channel.rs`."""
    rust_pairs = parse_rust_adjacency_pairs()
    python_pairs = winding_adjacency_pairs()
    return {
        "rust_pairs": sorted(rust_pairs),
        "python_pairs": sorted(python_pairs),
        "matches": rust_pairs == python_pairs,
        "rust_only": sorted(rust_pairs - python_pairs),
        "python_only": sorted(python_pairs - rust_pairs),
    }
