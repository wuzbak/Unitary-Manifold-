# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 306 — Jarlskog Layer 2 Flavor Constraint + n_w χ² Tracker."""
import math
import pytest
from src.core.pillar306_jarlskog_nw_flavor_hardening import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N1_CANONICAL,
    N2_CANONICAL,
    K_CS,
    J_PDG,
    J_GEO_LAYER1,
    J_MASS_FACTOR,
    THETA_BRAID_RAD,
    CABIBBO_ANGLE_GEOMETRIC_SIN,
    CABIBBO_ANGLE_PDG_SIN,
    CABIBBO_RESIDUAL_FRACTION,
    JARLSKOG_LAYER2_STATUS,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
    N_W_CANDIDATES,
    NW_CHI2_TRACKER_STATUS,
    NW_5_NS,
    NW_7_NS,
    NW_5_CHI2,
    NW_7_CHI2,
    DELTA_CHI2,
    LIKELIHOOD_RATIO,
    separation_guard,
    braid_cabibbo_angle_geometric,
    jarlskog_layer2_constraint,
    nw_ns_prediction,
    nw_chi2_residual_scan,
    nw_chi2_preference_summary,
    pillar306_report,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 306

def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

def test_pillar_title_contains_jarlskog():
    assert "Jarlskog" in PILLAR_TITLE

def test_pillar_title_contains_nw():
    assert "n_w" in PILLAR_TITLE or "χ²" in PILLAR_TITLE

def test_jarlskog_layer2_status():
    assert "CONSTRAINT" in JARLSKOG_LAYER2_STATUS
    assert "ARCHITECTURE_LIMIT" in JARLSKOG_LAYER2_STATUS

def test_nw_chi2_tracker_status():
    assert "QUANTIFIED" in NW_CHI2_TRACKER_STATUS


# ── Constants ──────────────────────────────────────────────────────────────────

def test_canonical_braid_pair():
    assert N1_CANONICAL == 5
    assert N2_CANONICAL == 7

def test_k_cs_value():
    assert K_CS == 74
    assert K_CS == N1_CANONICAL ** 2 + N2_CANONICAL ** 2

def test_j_pdg_order():
    assert 1e-6 < J_PDG < 1e-4

def test_j_geo_layer1_order():
    assert 0.01 < J_GEO_LAYER1 < 0.05

def test_j_mass_factor():
    assert abs(J_MASS_FACTOR - J_PDG / J_GEO_LAYER1) < 1e-12

def test_theta_braid_range():
    assert 0 < THETA_BRAID_RAD < math.pi / 2

def test_theta_braid_value():
    assert abs(THETA_BRAID_RAD - math.atan(5 / 7)) < 1e-10

def test_cabibbo_geometric_sin():
    # sin(θ_C)_geo = 1 - n1/n2 = 2/7
    expected = 2.0 / 7.0
    assert abs(CABIBBO_ANGLE_GEOMETRIC_SIN - expected) < 1e-10

def test_cabibbo_pdg_sin():
    # PDG |V_us| ≈ 0.2253
    assert 0.20 < CABIBBO_ANGLE_PDG_SIN < 0.24

def test_cabibbo_residual_positive():
    assert CABIBBO_RESIDUAL_FRACTION > 0

def test_cabibbo_residual_is_27_percent():
    # Should be ~27% = (2/7 - 0.2253) / 0.2253
    expected = abs(2.0 / 7.0 - 0.2253) / 0.2253
    assert abs(CABIBBO_RESIDUAL_FRACTION - expected) < 0.01

def test_planck_ns_central():
    assert abs(PLANCK_NS_CENTRAL - 0.9649) < 1e-4

def test_planck_ns_sigma():
    assert abs(PLANCK_NS_SIGMA - 0.0042) < 1e-4

def test_nw_candidates():
    assert 5 in N_W_CANDIDATES
    assert 7 in N_W_CANDIDATES

def test_nw5_ns_near_0963():
    # n_w=5: n_s ≈ 0.9635
    assert abs(NW_5_NS - 0.9635) < 0.001

def test_nw7_ns_near_0981():
    # n_w=7: n_s = 1 - 36/(14π)² ≈ 0.9814
    assert abs(NW_7_NS - 0.9814) < 0.001

def test_nw5_chi2_small():
    # n_w=5 is close to Planck
    assert NW_5_CHI2 < 1.0

def test_nw7_chi2_larger():
    # n_w=7 is further from Planck
    assert NW_7_CHI2 > NW_5_CHI2

def test_delta_chi2_positive():
    # n_w=7 has larger χ²
    assert DELTA_CHI2 > 0

def test_likelihood_ratio_less_than_one():
    # n_w=7 less likely than n_w=5
    assert 0 < LIKELIHOOD_RATIO < 1.0


# ── separation_guard ──────────────────────────────────────────────────────────

def test_separation_guard_returns_dict():
    sg = separation_guard()
    assert isinstance(sg, dict)

def test_separation_guard_no_hardgate():
    sg = separation_guard()
    assert sg["hardgate_impact"] == "NONE"
    assert sg["toe_score_impact"] == "NONE"
    assert sg["claim_labels_changed"] == "NONE"


# ── braid_cabibbo_angle_geometric ─────────────────────────────────────────────

def test_cabibbo_geometric_canonical():
    res = braid_cabibbo_angle_geometric()
    assert res["n1"] == 5
    assert res["n2"] == 7
    assert 0 < res["sin_cabibbo_geometric"] < 1
    assert 0 < res["residual_fraction"] < 1

def test_cabibbo_geometric_sin_value():
    res = braid_cabibbo_angle_geometric()
    assert abs(res["sin_cabibbo_geometric"] - 2.0 / 7.0) < 1e-10

def test_cabibbo_geometric_status_constraint():
    res = braid_cabibbo_angle_geometric()
    assert res["status"] == "CONSTRAINT"

def test_cabibbo_geometric_symmetric_braid_zero():
    # n1=n2 → sin_cabibbo_geo = 0
    res = braid_cabibbo_angle_geometric(n1=5, n2=5)
    assert abs(res["sin_cabibbo_geometric"]) < 1e-10

def test_cabibbo_geometric_invalid_raises():
    with pytest.raises(ValueError):
        braid_cabibbo_angle_geometric(n1=0, n2=7)

def test_cabibbo_geometric_theta_braid_deg():
    res = braid_cabibbo_angle_geometric()
    assert 30 < res["theta_braid_deg"] < 50


# ── jarlskog_layer2_constraint ────────────────────────────────────────────────

def test_jarlskog_layer2_returns_dict():
    res = jarlskog_layer2_constraint()
    assert isinstance(res, dict)

def test_jarlskog_layer2_has_status():
    res = jarlskog_layer2_constraint()
    assert "layer2_status" in res
    assert "CONSTRAINT" in res["layer2_status"]

def test_jarlskog_layer2_j_pdg():
    res = jarlskog_layer2_constraint()
    assert abs(res["j_pdg"] - J_PDG) < 1e-12

def test_jarlskog_layer2_architecture_limit():
    res = jarlskog_layer2_constraint()
    assert "architecture_limit" in res
    assert "5D-EFT" in res["architecture_limit"] or "string" in res["architecture_limit"]

def test_jarlskog_layer2_gap_name():
    res = jarlskog_layer2_constraint()
    assert "layer2_gap_name" in res
    assert "JARLSKOG" in res["layer2_gap_name"]

def test_jarlskog_layer1_status_closed():
    res = jarlskog_layer2_constraint()
    assert "CLOSED" in res["layer1_status"] or "Pillar 145" in res["layer1_status"]


# ── nw_ns_prediction ──────────────────────────────────────────────────────────

def test_nw_ns_5():
    ns = nw_ns_prediction(5)
    assert abs(ns - 0.9635) < 0.001

def test_nw_ns_7():
    ns = nw_ns_prediction(7)
    assert 0.975 < ns < 0.990

def test_nw_ns_invalid():
    with pytest.raises(ValueError):
        nw_ns_prediction(0)

def test_nw_ns_large():
    ns = nw_ns_prediction(100)
    assert 0.99 < ns < 1.0

def test_nw_ns_increases_with_nw():
    assert nw_ns_prediction(3) < nw_ns_prediction(5) < nw_ns_prediction(7)


# ── nw_chi2_residual_scan ─────────────────────────────────────────────────────

def test_nw_chi2_scan_default():
    results = nw_chi2_residual_scan()
    assert len(results) == 2
    nws = [r["n_w"] for r in results]
    assert 5 in nws
    assert 7 in nws

def test_nw_chi2_scan_5_consistent():
    results = nw_chi2_residual_scan([5])
    assert len(results) == 1
    assert results[0]["planck_status"] == "CONSISTENT"

def test_nw_chi2_scan_7_disfavoured():
    results = nw_chi2_residual_scan([7])
    assert len(results) == 1
    # n_w=7 should be mildly disfavoured or disfavoured
    assert results[0]["planck_status"] in ("MILDLY_DISFAVOURED", "DISFAVOURED")

def test_nw_chi2_scan_chi2_positive():
    results = nw_chi2_residual_scan([5, 7])
    for r in results:
        assert r["chi2"] >= 0

def test_nw_chi2_scan_5_has_smaller_chi2():
    results = nw_chi2_residual_scan([5, 7])
    chi2_5 = next(r["chi2"] for r in results if r["n_w"] == 5)
    chi2_7 = next(r["chi2"] for r in results if r["n_w"] == 7)
    assert chi2_5 < chi2_7

def test_nw_chi2_full_scan():
    results = nw_chi2_residual_scan(list(range(1, 11)))
    assert len(results) == 10
    # All chi2 are non-negative
    assert all(r["chi2"] >= 0 for r in results)


# ── nw_chi2_preference_summary ────────────────────────────────────────────────

def test_nw_chi2_summary_returns_dict():
    summary = nw_chi2_preference_summary()
    assert isinstance(summary, dict)

def test_nw_chi2_summary_has_both_candidates():
    summary = nw_chi2_preference_summary()
    assert "n_w_5" in summary
    assert "n_w_7" in summary

def test_nw_chi2_delta_positive():
    summary = nw_chi2_preference_summary()
    assert summary["delta_chi2_7_minus_5"] > 0

def test_nw_chi2_likelihood_ratio_less_than_1():
    summary = nw_chi2_preference_summary()
    # n_w=7 is less likely
    lr = summary["likelihood_ratio_nw5_over_nw7"]
    # This ratio > 1 means n_w=5 more likely than n_w=7
    assert lr > 1.0

def test_nw_chi2_combined_preference_mentions_5():
    summary = nw_chi2_preference_summary()
    assert "n_w=5" in summary["combined_preference"] or "5" in summary["combined_preference"]

def test_nw_chi2_tracker_status_present():
    summary = nw_chi2_preference_summary()
    assert "tracker_status" in summary
    assert "QUANTIFIED" in summary["tracker_status"]

def test_nw_chi2_remaining_gap_mentions_uniqueness():
    summary = nw_chi2_preference_summary()
    assert "uniqueness" in summary["remaining_gap"].lower() or "proof" in summary["remaining_gap"].lower()

def test_nw_chi2_aps_discriminator_mentioned():
    summary = nw_chi2_preference_summary()
    assert "APS" in summary["aps_discriminator"] or "Pillar 302" in summary["aps_discriminator"]


# ── pillar306_report ──────────────────────────────────────────────────────────

def test_pillar306_report_returns_dict():
    rpt = pillar306_report()
    assert isinstance(rpt, dict)

def test_pillar306_report_pillar_number():
    rpt = pillar306_report()
    assert rpt["pillar"] == 306

def test_pillar306_report_has_combined_status():
    rpt = pillar306_report()
    cs = rpt["combined_status"]
    assert "JARLSKOG_LAYER2_GEOMETRIC_CONSTRAINT" in cs
    assert "NW_CHI2_TRACKER_STATUS" in cs
    assert "PILLAR_306_STATUS" in cs

def test_pillar306_report_status_complete():
    rpt = pillar306_report()
    assert "COMPLETE" in rpt["combined_status"]["PILLAR_306_STATUS"]

def test_pillar306_report_what_closes_nonempty():
    rpt = pillar306_report()
    assert len(rpt["what_this_closes"]) >= 2

def test_pillar306_report_what_remains_nonempty():
    rpt = pillar306_report()
    assert len(rpt["what_remains_open"]) >= 2

def test_pillar306_report_item_a_present():
    rpt = pillar306_report()
    assert "item_a_jarlskog_layer2" in rpt

def test_pillar306_report_item_b_present():
    rpt = pillar306_report()
    assert "item_b_nw_chi2_tracker" in rpt

def test_pillar306_report_separation_guard_present():
    rpt = pillar306_report()
    assert "separation_guard" in rpt
