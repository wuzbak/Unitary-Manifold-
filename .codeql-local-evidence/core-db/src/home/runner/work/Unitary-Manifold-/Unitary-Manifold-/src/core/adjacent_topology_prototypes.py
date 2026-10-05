# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Adjacent-track topology prototypes (non-hardgate exploratory lane)."""

from __future__ import annotations

from typing import Iterable

import numpy as np


def truncated_path_signature(path: Iterable[float], depth: int = 2) -> dict[str, float]:
    """Compute a minimal truncated 1D path signature proxy up to depth 2."""
    values = np.asarray(list(path), dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("path must contain at least two scalar samples")
    increments = np.diff(values)
    s1 = float(np.sum(increments))
    s2 = float(0.5 * (s1 ** 2))
    out = {"S1": s1}
    if depth >= 2:
        out["S2"] = s2
    return out


def braid_word_winding_index(word: str) -> dict[str, int]:
    """Estimate winding index from a braid-generator word (+/- crossings)."""
    tokens = [token.strip() for token in str(word or "").split() if token.strip()]
    if not tokens:
        return {"crossings": 0, "positive": 0, "negative": 0, "winding_index": 0}
    positive = sum(1 for token in tokens if not token.startswith("-"))
    negative = len(tokens) - positive
    return {
        "crossings": len(tokens),
        "positive": positive,
        "negative": negative,
        "winding_index": positive - negative,
    }


def commutator_frobenius_norm(a: np.ndarray, b: np.ndarray) -> float:
    """Return ||AB - BA||_F as a non-commutativity indicator."""
    a_np = np.asarray(a, dtype=float)
    b_np = np.asarray(b, dtype=float)
    if a_np.ndim != 2 or b_np.ndim != 2 or a_np.shape != b_np.shape:
        raise ValueError("a and b must be same-shape 2D arrays")
    comm = a_np @ b_np - b_np @ a_np
    return float(np.linalg.norm(comm, ord="fro"))


def topology_adjacent_summary() -> dict[str, object]:
    """Provide explicit lane boundary metadata for topology experiments."""
    return {
        "lane": "ADJACENT_TRACK",
        "hardgate_physics_claim": False,
        "modules": [
            "truncated_path_signature",
            "braid_word_winding_index",
            "commutator_frobenius_norm",
        ],
        "boundary_note": (
            "These operators are exploratory topology tools and do not, by themselves, "
            "upgrade hardgate physics claim status."
        ),
    }
