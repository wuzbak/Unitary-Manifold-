# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 988 — Fully coupled KK backreaction engine."""

from __future__ import annotations

from src.core.evolution import FieldState
from src.core.pillar988_fully_coupled_kk_backreaction_engine import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    coupled_kk_step,
    fully_coupled_kk_backreaction_summary,
    run_fully_coupled_kk_backreaction,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 988
    assert PILLAR_STATUS == "FULLY_COUPLED_KK_BACKREACTION_ENGINE_COMPLETE"
    assert PILLAR_VALID is True


def test_single_coupled_step() -> None:
    s0 = FieldState.initialize_dynamic_braid(N=64, n_w_initial=5, dx=0.1, amplitude=0.3, phi_offset=1.3)
    s1, rec = coupled_kk_step(s0, dt=1e-3, max_modes=8, coupling=1.0)
    assert s1.n_kk_modes >= 1
    assert rec.t55_kk > 0
    assert rec.mean_phi_after > 0


def test_coupled_run_records() -> None:
    report = run_fully_coupled_kk_backreaction(steps=8)
    assert report["steps"] == 8
    assert len(report["records"]) == 8
    assert report["status"] in {"FULLY_COUPLED_CONVERGED", "FULLY_COUPLED_ACTIVE"}


def test_summary_shape() -> None:
    summary = fully_coupled_kk_backreaction_summary()
    assert summary["valid"] is True
    assert summary["steps"] >= 1
