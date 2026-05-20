# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 292 — ACT DR6 Tensor Ratio Deep Analysis."""
import math
import pytest
from src.core.pillar292_act_dr6_tensor_ratio_deep_analysis import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    UM_R_LEAD,
    ACT_DR6_R_UPPER_95,
    P2_FALSIFIER_THRESHOLD,
    CMBS4_CONSISTENT_THRESHOLD,
    CMBS4_FALSIFIED_THRESHOLD,
    N_W, M_W, K_CS,
    C_NLO,
    separation_guard,
    um_r_leading,
    nlo_braid_correction,
    nonminimal_kk_coupling_correction,
    combined_minimum_r,
    act_dr6_tension_verdict,
    cmbs4_preregistered_routing,
    deep_analysis_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 292


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard():
    g = separation_guard()
    assert g["pillar"] == 292
    assert g["is_hardgate"] is False
    assert g["modifies_hardgate_module"] is False
    assert g["alters_falsifier_window"] is False
    assert g["extends_pillar"] == 288


def test_um_r_lead():
    assert abs(UM_R_LEAD - 0.0315) < 1e-6


def test_act_dr6_upper_95():
    assert abs(ACT_DR6_R_UPPER_95 - 0.016) < 1e-6


def test_p2_falsifier_threshold():
    assert abs(P2_FALSIFIER_THRESHOLD - 0.010) < 1e-6


def test_um_r_leading_keys():
    r = um_r_leading()
    for key in ("phi0_eff", "epsilon_leading", "braid_factor", "r_analytic", "r_hardgated"):
        assert key in r


def test_um_r_leading_positive():
    r = um_r_leading()
    assert r["r_analytic"] > 0.0
    assert r["r_hardgated"] > 0.0


def test_nlo_braid_correction_keys():
    c = nlo_braid_correction()
    for key in ("k_eff_lead", "k_eff_nlo", "delta_r", "r_nlo_corrected", "verdict"):
        assert key in c


def test_nlo_braid_correction_negative():
    c = nlo_braid_correction()
    assert c["delta_r"] < 0.0   # NLO correction reduces r


def test_nlo_braid_correction_small():
    c = nlo_braid_correction()
    # NLO correction should be < 5% of r_lead
    assert abs(c["delta_r"]) < 0.05 * UM_R_LEAD


def test_nlo_corrected_still_above_act_limit():
    c = nlo_braid_correction()
    assert c["r_nlo_corrected"] > ACT_DR6_R_UPPER_95


def test_nlo_verdict_insufficient():
    c = nlo_braid_correction()
    assert c["verdict"] == "INSUFFICIENT_TO_REACH_ACT_LIMIT"


def test_nonminimal_kk_coupling_zero():
    c = nonminimal_kk_coupling_correction(xi=0.0)
    assert abs(c["delta_r"]) < 1e-10


def test_nonminimal_kk_coupling_conformal():
    c = nonminimal_kk_coupling_correction(xi=1.0 / 6.0)
    assert c["delta_r"] < 0.0  # reduces r
    assert c["verdict"] == "INSUFFICIENT_TO_REACH_ACT_LIMIT"


def test_nonminimal_kk_invalid_xi():
    with pytest.raises(ValueError):
        nonminimal_kk_coupling_correction(xi=-0.1)


def test_combined_minimum_r_keys():
    m = combined_minimum_r()
    for key in ("r_lead", "r_minimum_5d_eft", "tension_irreducible_in_5d_eft", "verdict"):
        assert key in m


def test_combined_minimum_r_above_act_limit():
    m = combined_minimum_r()
    assert m["r_minimum_5d_eft"] > ACT_DR6_R_UPPER_95


def test_combined_minimum_r_irreducible():
    m = combined_minimum_r()
    assert m["tension_irreducible_in_5d_eft"] is True
    assert m["verdict"] == "TENSION_IRREDUCIBLE_IN_5D_EFT"


def test_act_dr6_tension_verdict_high_tension():
    v = act_dr6_tension_verdict()
    assert v["verdict"] == "HIGH_TENSION"


def test_act_dr6_tension_verdict_p2_not_triggered():
    v = act_dr6_tension_verdict()
    assert v["p2_falsifier_triggered"] is False


def test_act_dr6_tension_verdict_conclusion():
    v = act_dr6_tension_verdict()
    assert isinstance(v["conclusion"], str)
    assert len(v["conclusion"]) > 20


def test_cmbs4_routing_consistent():
    r = cmbs4_preregistered_routing(r_measured=0.030, sigma=0.005, detection_sigma=3.0)
    assert r["verdict"] == "CONSISTENT"
    assert r["p2_falsifier_triggered"] is False


def test_cmbs4_routing_falsified():
    r = cmbs4_preregistered_routing(r_measured=0.006, sigma=0.002, detection_sigma=4.0)
    assert r["verdict"] == "FALSIFIED"
    assert r["p2_falsifier_triggered"] is True


def test_cmbs4_routing_tension():
    r = cmbs4_preregistered_routing(r_measured=0.012, sigma=0.004, detection_sigma=0.0)
    assert r["verdict"] in ("TENSION_SHARPENED", "INCONCLUSIVE")


def test_cmbs4_routing_invalid_sigma():
    with pytest.raises(ValueError):
        cmbs4_preregistered_routing(r_measured=0.02, sigma=0.0)


def test_cmbs4_routing_preregistration_version():
    r = cmbs4_preregistered_routing(r_measured=0.030, sigma=0.005, detection_sigma=3.0)
    assert r["preregistration_version"] == "v11.9"


def test_deep_analysis_report_keys():
    rep = deep_analysis_report()
    for key in ("pillar", "title", "tension_verdict", "minimum_achievable_r", "cmbs4_preregistration"):
        assert key in rep


def test_deep_analysis_report_pillar():
    rep = deep_analysis_report()
    assert rep["pillar"] == 292


def test_deep_analysis_report_summary():
    rep = deep_analysis_report()
    assert isinstance(rep["summary"], str)
    assert "HIGH_TENSION" in rep["summary"]


def test_k_cs_value():
    assert K_CS == 74


def test_nw_mw_values():
    assert N_W == 5
    assert M_W == 7
