# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 987 — UV completion compactification layer."""

from __future__ import annotations

from src.core.pillar987_uv_completion_compactification_layer import (
    CY4_INTERSECTION_RING_4X4,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    intersection_pairing,
    moduli_observables,
    solve_uv_moduli_point,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 987
    assert PILLAR_STATUS == "UV_COMPLETION_COMPACTIFICATION_LAYER_COMPLETE"
    assert PILLAR_VALID is True


def test_ring_shape() -> None:
    assert len(CY4_INTERSECTION_RING_4X4) == 4
    assert all(len(row) == 4 for row in CY4_INTERSECTION_RING_4X4)


def test_pairing_symmetric_on_equal_vector() -> None:
    v = (1.0, -1.0, 0.5, 0.2)
    assert intersection_pairing(v, v) == intersection_pairing(v, v)


def test_moduli_observables_positive_domains() -> None:
    obs = moduli_observables(1.0, 0.8)
    assert obs["g4_norm"] > 0
    assert obs["n_d3_model"] >= 0


def test_solver_returns_best_point() -> None:
    out = solve_uv_moduli_point()
    assert out["status"] in {"UV_COMPACTIFICATION_POINT_DERIVED", "UV_COMPACTIFICATION_POINT_PARTIAL"}
    assert out["best_point"]["score"] >= 0
    assert out["best_point"]["tau"] > 0
    assert out["best_point"]["rho"] > 0
