# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/biology/centrosome_integer_kernels.py
=========================================
Exact centrosome count identities separated from the stronger curvature-reader
mechanism claim.

This module promotes only the clean integer kernels:

- triplet count      = n₁ + n₂ − 3 = 9
- B/C protofilaments = 2 × n_w     = 10

The stronger claim that the centrosome reads ``R_{i5j5}`` remains outside the
scope of this file and is intentionally left as a falsifiable mechanism lane.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = [
    "N_W",
    "N_1",
    "N_2",
    "centriole_triplet_count",
    "bc_protofilament_count",
    "curvature_tensor_component_count",
    "centrosome_integer_kernel_report",
]

N_W: int = 5
N_1: int = 5
N_2: int = 7


def centriole_triplet_count(n_1: int = N_1, n_2: int = N_2, spatial_dims: int = 3) -> int:
    """Return the integer kernel n₁+n₂−3 for centrosome triplets."""
    if n_1 < 0 or n_2 < 0:
        raise ValueError("winding inputs must be non-negative")
    if spatial_dims < 0:
        raise ValueError("spatial_dims must be non-negative")
    value = n_1 + n_2 - spatial_dims
    if value < 0:
        raise ValueError("derived triplet count must be non-negative")
    return value


def bc_protofilament_count(n_w: int = N_W) -> int:
    """Return the information-carrying B/C protofilament count 2×n_w."""
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    return 2 * n_w


def curvature_tensor_component_count(spatial_dims: int = 3) -> int:
    """Return the number of spatial curvature components in an s×s block."""
    if spatial_dims < 1:
        raise ValueError(f"spatial_dims must be ≥ 1, got {spatial_dims!r}")
    return spatial_dims * spatial_dims


def centrosome_integer_kernel_report() -> Dict[str, Any]:
    """Return the promotion-safe centrosome integer bundle."""
    return {
        "triplet_kernel_status": "DERIVED_STRUCTURAL",
        "protofilament_kernel_status": "DERIVED_STRUCTURAL",
        "triplet_count": centriole_triplet_count(),
        "bc_protofilaments": bc_protofilament_count(),
        "curvature_component_count": curvature_tensor_component_count(),
        "mechanism_status": "FALSIFIABLE_PREDICTION",
        "mechanism_note": (
            "Only the count identities are promoted here. The stronger claim that "
            "specific triplets read specific curvature components remains a distinct "
            "mechanism / experiment lane."
        ),
    }
