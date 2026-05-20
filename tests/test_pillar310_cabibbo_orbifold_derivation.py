# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 310 — Cabibbo Orbifold Derivation Attempt."""
from __future__ import annotations

import math
import pytest

from src.core.pillar310_cabibbo_orbifold_derivation import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N_W,
    N2_BRAID,
    K_CS,
    SIN_THETA_C_PDG,
    THETA_C_PDG_RAD,
    SIN_THETA_C_BRAID_LAYER1,
    SIN_THETA_C_Z14_ORBIFOLD,
    THETA_C_Z14_RAD,
    COINCIDENCE_RESIDUAL_PCT,
    DERIVATION_STATUS,
    NAMED_GAP,
    orbifold_order_from_braid,
    cabibbo_angle_braid_layer1,
    cabibbo_angle_z14_orbifold,
    cabibbo_residual_accounting,
    layer2_architecture_limit_cert,
    pillar310_report,
)


# ── Identity ───────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 310


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_pillar_title_contains_cabibbo():
    assert "Cabibbo" in PILLAR_TITLE or "Orbifold" in PILLAR_TITLE


def test_derivation_status_is_partial():
    assert DERIVATION_STATUS == "PARTIAL_DERIVATION"


def test_named_gap_present():
    assert "CABIBBO" in NAMED_GAP or "OVERLAP" in NAMED_GAP


# ── Braid constants ────────────────────────────────────────────────────────────

def test_braid_constants():
    assert N_W == 5
    assert N2_BRAID == 7
    assert K_CS == 74
    assert K_CS == N_W**2 + N2_BRAID**2


def test_pdg_sin_theta_C_in_range():
    """PDG Cabibbo sin(θ_C) should be ~0.225."""
    assert 0.22 < SIN_THETA_C_PDG < 0.23


def test_pdg_theta_C_in_radians():
    assert abs(THETA_C_PDG_RAD - math.asin(SIN_THETA_C_PDG)) < 1e-10


# ── orbifold_order_from_braid ──────────────────────────────────────────────────

def test_orbifold_order_canonical():
    """Z₁₄ order from (5,7) braid should be 14."""
    z14 = orbifold_order_from_braid(N_W, N2_BRAID)
    assert z14 == 14


def test_orbifold_order_positive():
    assert orbifold_order_from_braid(N_W, N2_BRAID) > 0


def test_orbifold_order_integer():
    result = orbifold_order_from_braid(N_W, N2_BRAID)
    assert isinstance(result, int)


# ── cabibbo_angle_braid_layer1 ─────────────────────────────────────────────────

def test_braid_layer1_formula():
    r = cabibbo_angle_braid_layer1(N_W, N2_BRAID)
    assert abs(r["sin_theta_C"] - round(1.0 - N_W / N2_BRAID, 6)) < 1e-8


def test_braid_layer1_residual_is_large():
    """Layer 1 braid residual should be >20% (ARCHITECTURE_LIMIT)."""
    r = cabibbo_angle_braid_layer1(N_W, N2_BRAID)
    assert r["residual_vs_pdg_pct"] > 20.0


def test_braid_layer1_status_is_architecture_limit():
    r = cabibbo_angle_braid_layer1(N_W, N2_BRAID)
    assert r["status"] == "ARCHITECTURE_LIMIT"


def test_braid_layer1_sin_theta_matches_module_constant():
    assert abs(SIN_THETA_C_BRAID_LAYER1 - cabibbo_angle_braid_layer1()["sin_theta_C"]) < 1e-10


def test_braid_layer1_keys_complete():
    r = cabibbo_angle_braid_layer1()
    for key in ("formula", "n_w", "n2", "sin_theta_C", "theta_C_deg",
                "residual_vs_pdg_pct", "status", "note"):
        assert key in r


# ── cabibbo_angle_z14_orbifold ─────────────────────────────────────────────────

def test_z14_orbifold_theta_rad():
    """θ_Z14 = π/14 should be ≈ 0.2244."""
    r = cabibbo_angle_z14_orbifold()
    assert abs(r["theta_Z14_rad"] - math.pi / 14) < 1e-8


def test_z14_orbifold_sin_approx():
    """sin(π/14) should be ≈ 0.2225."""
    r = cabibbo_angle_z14_orbifold()
    assert abs(r["sin_theta_Z14"] - math.sin(math.pi / 14)) < 1e-5


def test_z14_coincidence_residual_small():
    """π/14 radian value vs PDG sin(θ_C) should be < 1% (the 0.40% coincidence)."""
    r = cabibbo_angle_z14_orbifold()
    assert r["coincidence_residual_vs_pdg_pct"] < 1.0


def test_z14_coincidence_residual_very_small():
    """π/14 vs PDG should be < 0.5%."""
    r = cabibbo_angle_z14_orbifold()
    assert r["coincidence_residual_vs_pdg_pct"] < 0.5


def test_z14_sin_residual_present():
    """Self-consistent sin(π/14) vs PDG comparison should be in result."""
    r = cabibbo_angle_z14_orbifold()
    assert "sin_residual_vs_pdg_pct" in r
    # sin(π/14) gives ~1.25% residual — larger than the radian coincidence
    assert r["sin_residual_vs_pdg_pct"] > 0.5


def test_z14_orbifold_status_is_partial_derivation():
    r = cabibbo_angle_z14_orbifold()
    assert r["status"] == "PARTIAL_DERIVATION"


def test_z14_orbifold_has_honest_caveat():
    r = cabibbo_angle_z14_orbifold()
    assert len(r["honest_caveat"]) > 50


def test_z14_orbifold_has_derivation_steps():
    r = cabibbo_angle_z14_orbifold()
    assert len(r["derivation_steps"]) >= 5


def test_z14_orbifold_matches_module_constants():
    r = cabibbo_angle_z14_orbifold()
    assert abs(SIN_THETA_C_Z14_ORBIFOLD - r["sin_theta_Z14"]) < 1e-10
    assert abs(THETA_C_Z14_RAD - r["theta_Z14_rad"]) < 1e-10
    assert abs(COINCIDENCE_RESIDUAL_PCT - r["coincidence_residual_vs_pdg_pct"]) < 1e-8


def test_z14_orbifold_z14_order_is_14():
    r = cabibbo_angle_z14_orbifold()
    assert r["z14_order"] == 14


# ── cabibbo_residual_accounting ────────────────────────────────────────────────

def test_residual_accounting_structure():
    acct = cabibbo_residual_accounting()
    for key in ("pillar", "n_w", "n2", "k_cs", "pdg_reference",
                "layer1_braid", "z14_orbifold", "coincidence_residual_improvement_pct",
                "verdict", "named_gap", "derivation_status"):
        assert key in acct


def test_residual_accounting_improvement_is_positive():
    """Z₁₄ coincidence (0.40%) is much closer to PDG than Layer 1 braid (26.8%)."""
    acct = cabibbo_residual_accounting()
    assert acct["coincidence_residual_improvement_pct"] > 20.0


def test_residual_accounting_verdict_contains_improvement():
    acct = cabibbo_residual_accounting()
    assert "PARTIAL_DERIVATION" in acct["verdict"] or "improvement" in acct["verdict"].lower()


def test_residual_accounting_k_cs_consistent():
    acct = cabibbo_residual_accounting()
    assert acct["k_cs"] == N_W**2 + N2_BRAID**2


# ── layer2_architecture_limit_cert ────────────────────────────────────────────

def test_architecture_limit_cert_structure():
    cert = layer2_architecture_limit_cert()
    for key in ("named_limit", "j_pdg", "cabibbo_layer1_residual_pct",
                "cabibbo_z14_residual_pct", "achievable_in_5d_eft",
                "not_achievable_in_5d_eft", "upgrade_path", "status"):
        assert key in cert


def test_architecture_limit_status():
    cert = layer2_architecture_limit_cert()
    assert cert["status"] == "CERTIFIED_ARCHITECTURE_LIMIT"


def test_architecture_limit_j_pdg():
    cert = layer2_architecture_limit_cert()
    assert abs(cert["j_pdg"] - 3.08e-5) < 1e-8


def test_architecture_limit_z14_residual_small():
    cert = layer2_architecture_limit_cert()
    assert cert["cabibbo_z14_residual_pct"] < 1.0, (
        f"cabibbo_z14_residual_pct={cert['cabibbo_z14_residual_pct']:.3f} "
        "should be < 1.0% (π/14 radian value vs PDG sin coincidence)"
    )


# ── pillar310_report ───────────────────────────────────────────────────────────

def test_report_structure():
    report = pillar310_report()
    for key in ("pillar", "title", "track", "derivation_status", "named_gap",
                "residual_accounting", "architecture_limit_cert", "summary",
                "no_hardgate_impact", "toe_score_impact"):
        assert key in report


def test_report_pillar_number():
    assert pillar310_report()["pillar"] == 310


def test_report_no_hardgate_impact():
    report = pillar310_report()
    assert report["no_hardgate_impact"] is True


def test_report_summary_mentions_partial_derivation():
    report = pillar310_report()
    assert "PARTIAL_DERIVATION" in report["summary"]
