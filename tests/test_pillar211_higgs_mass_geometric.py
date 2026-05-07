# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Pillar 211 — Higgs Mass Geometric Derivation (Best Effort).

Covers:
  1. gauge_higgs_unification_lambda_H()  — dict structure, values, status
  2. dilaton_higgs_mixing()              — dict structure, negligible correction
  3. cw_kk_loop_mH()                    — dict structure, hierarchy problem
  4. higgs_mass_audit()                 — aggregation, honest P5 status
  5. pillar211_summary()                — top-level summary
  6. Physical consistency and honesty checks
"""
from __future__ import annotations

import math

import pytest

from src.core.pillar211_higgs_mass_geometric import (
    K_CS,
    LAMBDA_H_PDG,
    M_HIGGS_PDG,
    M_RADION_GEV,
    N_C,
    N_W,
    PI_KR,
    V_HIGGS_GW,
    V_HIGGS_PDG,
    __provenance__,
    cw_kk_loop_mH,
    dilaton_higgs_mixing,
    gauge_higgs_unification_lambda_H,
    higgs_mass_audit,
    pillar211_summary,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────


def test_constants_n_w():
    assert N_W == 5


def test_constants_k_cs():
    assert K_CS == 74


def test_constants_pi_kr():
    assert PI_KR == pytest.approx(37.0, rel=1e-10)


def test_constants_n_c():
    assert N_C == 3


def test_constants_m_higgs_pdg():
    assert M_HIGGS_PDG == pytest.approx(125.25, rel=1e-6)


def test_constants_v_higgs_pdg():
    assert V_HIGGS_PDG == pytest.approx(246.22, rel=1e-6)


def test_constants_v_higgs_gw():
    # Pillar 201 GW-derived VEV is ~4.6% high
    assert V_HIGGS_GW == pytest.approx(257.6, rel=1e-4)


def test_constants_lambda_h_pdg():
    expected = 125.25**2 / (2.0 * 246.22**2)
    assert LAMBDA_H_PDG == pytest.approx(expected, rel=1e-6)
    assert 0.12 < LAMBDA_H_PDG < 0.14


def test_constants_m_radion_gev():
    # 110 meV in GeV
    assert M_RADION_GEV == pytest.approx(1.10e-10, rel=1e-3)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE 1: GAUGE-HIGGS UNIFICATION
# ─────────────────────────────────────────────────────────────────────────────


def test_ghu_returns_dict():
    result = gauge_higgs_unification_lambda_H()
    assert isinstance(result, dict)


def test_ghu_has_required_keys():
    result = gauge_higgs_unification_lambda_H()
    for key in ("g5D_sq", "g4D_sq", "lambda_H_geo", "lambda_H_pdg", "pct_err", "status", "status_detail", "architecture_note", "route"):
        assert key in result, f"Missing key: {key}"


def test_ghu_g5D_sq():
    result = gauge_higgs_unification_lambda_H()
    expected = 4.0 * math.pi / 74.0
    assert result["g5D_sq"] == pytest.approx(expected, rel=1e-10)


def test_ghu_g4D_sq():
    result = gauge_higgs_unification_lambda_H()
    expected = (4.0 * math.pi / 74.0) / 37.0
    assert result["g4D_sq"] == pytest.approx(expected, rel=1e-10)


def test_ghu_lambda_H_geo():
    result = gauge_higgs_unification_lambda_H()
    expected = (4.0 * math.pi / 74.0) / 37.0 / 8.0
    assert result["lambda_H_geo"] == pytest.approx(expected, rel=1e-10)
    # Should be small — suppressed by 1/πkR
    assert result["lambda_H_geo"] < 0.01


def test_ghu_lambda_H_pdg_matches_constant():
    result = gauge_higgs_unification_lambda_H()
    assert result["lambda_H_pdg"] == pytest.approx(LAMBDA_H_PDG, rel=1e-10)


def test_ghu_pct_err_is_float():
    result = gauge_higgs_unification_lambda_H()
    assert isinstance(result["pct_err"], float)
    assert result["pct_err"] > 0.0


def test_ghu_pct_err_is_large():
    # The naive GHU gives >50% error — the hierarchy problem
    result = gauge_higgs_unification_lambda_H()
    assert result["pct_err"] > 50.0


def test_ghu_status_is_open():
    # Route 1 does not achieve <15% at tree level → OPEN
    result = gauge_higgs_unification_lambda_H()
    assert result["status"] == "OPEN"


def test_ghu_status_not_false_claim():
    result = gauge_higgs_unification_lambda_H()
    # Must not falsely claim a geometric prediction when error is large
    if result["pct_err"] >= 5.0:
        assert result["status"] != "GEOMETRIC PREDICTION"
    if result["pct_err"] >= 15.0:
        assert result["status"] not in ("GEOMETRIC PREDICTION", "GEOMETRIC ESTIMATE")


def test_ghu_status_detail_is_string():
    result = gauge_higgs_unification_lambda_H()
    assert isinstance(result["status_detail"], str)
    assert len(result["status_detail"]) > 20


def test_ghu_architecture_note_is_string():
    result = gauge_higgs_unification_lambda_H()
    assert isinstance(result["architecture_note"], str)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE 2: DILATON / RADION-HIGGS MIXING
# ─────────────────────────────────────────────────────────────────────────────


def test_rdm_returns_dict():
    result = dilaton_higgs_mixing()
    assert isinstance(result, dict)


def test_rdm_has_required_keys():
    result = dilaton_higgs_mixing()
    for key in ("f_r_gev", "xi_rH", "delta_mH_over_mH", "pct_shift", "status", "status_detail", "route"):
        assert key in result, f"Missing key: {key}"


def test_rdm_f_r_gev_is_positive():
    result = dilaton_higgs_mixing()
    assert result["f_r_gev"] > 0.0


def test_rdm_f_r_gev_is_tev_scale():
    # f_r ~ √6 × M_Pl × exp(-37) ≈ 2552 GeV  (TeV scale)
    result = dilaton_higgs_mixing()
    assert result["f_r_gev"] > 100.0   # definitely TeV-scale
    assert result["f_r_gev"] < 1.0e6  # well below 10^6 GeV


def test_rdm_xi_rH_is_small():
    result = dilaton_higgs_mixing()
    # Mixing angle can be O(0.01) but must be < 1
    assert 0.0 < result["xi_rH"] < 1.0


def test_rdm_delta_mH_is_negligible():
    result = dilaton_higgs_mixing()
    # Correction must be < 1% of m_H
    assert result["delta_mH_over_mH"] < 0.01


def test_rdm_pct_shift_less_than_1():
    result = dilaton_higgs_mixing()
    assert result["pct_shift"] < 1.0


def test_rdm_status_cannot_close():
    result = dilaton_higgs_mixing()
    assert result["status"] == "CANNOT CLOSE"


def test_rdm_status_detail_is_string():
    result = dilaton_higgs_mixing()
    assert isinstance(result["status_detail"], str)
    assert len(result["status_detail"]) > 20


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE 3: COLEMAN-WEINBERG KK LOOP
# ─────────────────────────────────────────────────────────────────────────────


def test_cwkk_returns_dict():
    result = cw_kk_loop_mH()
    assert isinstance(result, dict)


def test_cwkk_has_required_keys():
    result = cw_kk_loop_mH()
    for key in ("g5D_sq", "M_KK_1_gev", "delta_lambda_H_low", "delta_lambda_H_planck",
                "hierarchy_problem_documented", "status", "status_detail", "route"):
        assert key in result, f"Missing key: {key}"


def test_cwkk_hierarchy_problem_documented():
    result = cw_kk_loop_mH()
    assert result["hierarchy_problem_documented"] is True


def test_cwkk_delta_low_is_order_of_lambda():
    result = cw_kk_loop_mH()
    # M_KK_1 ~ 1 TeV → δλ_H_low ~ 0.06, order of λ_H_PDG but not matching
    assert result["delta_lambda_H_low"] > 1e-5   # non-negligible
    assert result["delta_lambda_H_low"] < 10.0   # not astronomically large


def test_cwkk_delta_planck_is_enormous():
    result = cw_kk_loop_mH()
    # Planck-regime gives huge correction — hierarchy problem
    assert result["delta_lambda_H_planck"] > 1e30


def test_cwkk_status_cannot_close():
    result = cw_kk_loop_mH()
    assert result["status"] == "CANNOT CLOSE"


def test_cwkk_status_detail_is_string():
    result = cw_kk_loop_mH()
    assert isinstance(result["status_detail"], str)
    assert len(result["status_detail"]) > 20


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT
# ─────────────────────────────────────────────────────────────────────────────


def test_audit_returns_dict():
    result = higgs_mass_audit()
    assert isinstance(result, dict)


def test_audit_has_required_keys():
    result = higgs_mass_audit()
    for key in ("route1", "route2", "route3", "best_pct_err", "p5_status",
                "overall_status", "overall_note", "architecture_limit", "pillar"):
        assert key in result, f"Missing key: {key}"


def test_audit_p5_status_is_open():
    result = higgs_mass_audit()
    # P5 should be OPEN unless Route 1 miraculously achieves <5%
    r1 = result["route1"]
    if r1["pct_err"] >= 5.0:
        assert result["p5_status"] == "OPEN"


def test_audit_architecture_limit():
    result = higgs_mass_audit()
    assert result["architecture_limit"] is True


def test_audit_overall_note_is_string():
    result = higgs_mass_audit()
    assert isinstance(result["overall_note"], str)
    assert len(result["overall_note"]) > 30


def test_audit_best_pct_err_matches_route1():
    result = higgs_mass_audit()
    assert result["best_pct_err"] == pytest.approx(result["route1"]["pct_err"], rel=1e-10)


def test_audit_pillar_is_211():
    result = higgs_mass_audit()
    assert result["pillar"] == "211"


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────


def test_summary_returns_dict():
    result = pillar211_summary()
    assert isinstance(result, dict)


def test_summary_pillar_is_211():
    result = pillar211_summary()
    assert result["pillar"] == "211"


def test_summary_routes_evaluated():
    result = pillar211_summary()
    assert result["routes_evaluated"] == 3


def test_summary_lambda_h_pdg():
    result = pillar211_summary()
    assert result["lambda_H_pdg"] == pytest.approx(LAMBDA_H_PDG, rel=1e-6)


def test_summary_architecture_limit():
    result = pillar211_summary()
    assert result["architecture_limit"] is True


def test_summary_provenance():
    result = pillar211_summary()
    prov = result["provenance"]
    assert prov["pillar"] == "211"
    assert prov["fingerprint"] == "(5, 7, 74)"


def test_summary_p5_status_open_when_large_error():
    result = pillar211_summary()
    if result["best_pct_err"] >= 5.0:
        assert result["p5_status"] == "OPEN"


# ─────────────────────────────────────────────────────────────────────────────
# PROVENANCE
# ─────────────────────────────────────────────────────────────────────────────


def test_provenance_dict_exists():
    assert isinstance(__provenance__, dict)


def test_provenance_pillar():
    assert __provenance__["pillar"] == "211"


def test_provenance_author():
    assert "Walker-Pearson" in __provenance__["author"]


def test_provenance_license():
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"
