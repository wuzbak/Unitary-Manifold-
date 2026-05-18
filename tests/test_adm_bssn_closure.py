# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/adm_bssn_closure.py."""
from __future__ import annotations

from src.core.adm_bssn_closure import (
    ADJACENCY_TRACK_LABEL,
    bssn_evolution_step,
    constraint_verdict,
    t3_closure_assessment,
)


def test_bssn_evolution_step_updates_fields():
    out = bssn_evolution_step(alpha=1.0, k_trace=0.003, beta=0.0, b_driver=0.002, dt=0.1)
    assert out["alpha_new"] != 1.0
    assert out["beta_new"] != 0.0


def test_constraint_verdict_states():
    assert constraint_verdict(0.001, 0.001) == "PASS"
    assert constraint_verdict(0.015, 0.005) == "TENSION"
    assert constraint_verdict(0.04, 0.01) == "FALSIFIED"


def test_t3_closure_assessment_shape():
    report = t3_closure_assessment()
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["dynamical_verdict"] in {"PASS", "TENSION", "FALSIFIED"}
    assert report["status"] in {"PARTIALLY_CLOSED", "OPEN"}
    assert report["full_bssn_open"] is True
