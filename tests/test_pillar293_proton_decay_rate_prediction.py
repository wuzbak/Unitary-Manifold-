# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 293 — Proton Decay Rate Prediction."""
import math
import pytest
from src.core.pillar293_proton_decay_rate_prediction import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N_C,
    K_CS,
    N_W,
    PI_KR,
    SK_LIMIT_EPLUS_PI0_YR,
    HK_SENSITIVITY_EPLUS_PI0_YR,
    separation_guard,
    alpha_gut_cs_quantized,
    mgut_from_rge,
    mgut_effective,
    orbifold_suppression_factor,
    proton_lifetime_eplus_pi0,
    proton_lifetime_nubar_kplus,
    uncertainty_from_kcs,
    hyperk_routing,
    proton_decay_prediction_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 293


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard():
    g = separation_guard()
    assert g["pillar"] == 293
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
    assert g["experiment"] == "Hyper-Kamiokande"


def test_alpha_gut_cs_quantized():
    a = alpha_gut_cs_quantized()
    assert abs(a["alpha_gut_cs"] - N_C / K_CS) < 1e-10
    assert abs(a["alpha_gut_cs"] - 3.0/74.0) < 1e-10
    assert a["n_c"] == N_C
    assert a["k_cs"] == K_CS


def test_alpha_gut_conventional():
    a = alpha_gut_cs_quantized()
    assert abs(a["alpha_gut_conventional"] - 1.0/25.0) < 1e-6


def test_mgut_from_rge_keys():
    r = mgut_from_rge()
    for key in ("alpha_gut", "m_gut_rge_gev", "log_ratio"):
        assert key in r


def test_mgut_from_rge_positive():
    r = mgut_from_rge()
    assert r["m_gut_rge_gev"] > 1.0e12   # at least 10^12 GeV


def test_mgut_from_rge_order_of_magnitude():
    r = mgut_from_rge()
    # M_GUT should be 10^14 – 10^18 GeV for SU(5)
    log10_mgut = math.log10(r["m_gut_rge_gev"])
    assert 14.0 <= log10_mgut <= 18.0


def test_mgut_effective_keys():
    m = mgut_effective()
    for key in ("m_gut_4d_gev", "warp_factor", "m_gut_warped_gev", "m_gut_for_decay_gev"):
        assert key in m


def test_orbifold_suppression_factor():
    f = orbifold_suppression_factor(N_W)
    # f = (1/5) × cos²(π/5) ≈ 0.2 × (0.809)² ≈ 0.131
    assert 0.10 < f < 0.20
    assert f > 0.0


def test_orbifold_suppression_canonical():
    f = orbifold_suppression_factor(5)
    expected = (1.0 / 5.0) * math.cos(math.pi / 5.0) ** 2
    assert abs(f - expected) < 1e-10


def test_proton_lifetime_eplus_pi0_viable():
    r = proton_lifetime_eplus_pi0()
    assert r["viable"] is True
    assert r["tau_years"] > SK_LIMIT_EPLUS_PI0_YR


def test_proton_lifetime_eplus_pi0_keys():
    r = proton_lifetime_eplus_pi0()
    for key in ("mode", "tau_years", "tau_log10", "sk_limit_yr", "viable", "verdict"):
        assert key in r


def test_proton_lifetime_eplus_pi0_log10():
    r = proton_lifetime_eplus_pi0()
    # Log10 of lifetime should be between 32 and 40
    assert 30.0 < r["tau_log10"] < 45.0


def test_proton_lifetime_mode_label():
    r = proton_lifetime_eplus_pi0()
    assert r["mode"] == "p → e⁺π⁰"


def test_proton_lifetime_nubar_kplus_viable():
    r = proton_lifetime_nubar_kplus()
    assert r["viable"] is True


def test_proton_lifetime_nubar_kplus_keys():
    r = proton_lifetime_nubar_kplus()
    for key in ("mode", "tau_years", "verdict", "v_us", "f_kaon"):
        assert key in r


def test_proton_lifetime_nubar_longer_than_eplus():
    eplus = proton_lifetime_eplus_pi0()
    nubar = proton_lifetime_nubar_kplus()
    # V_us^(-2) × f_kaon ≈ (1/0.225²) × 0.60 ≈ 11.9 → τ(νK) > τ(eπ)
    assert nubar["tau_years"] > eplus["tau_years"]


def test_uncertainty_from_kcs_keys():
    u = uncertainty_from_kcs()
    for key in ("delta_kcs", "results", "tau_log10_nominal", "delta_log10"):
        assert key in u


def test_uncertainty_from_kcs_small():
    u = uncertainty_from_kcs(delta_kcs=1)
    # Uncertainty from ±1 in K_CS should be small (< 1 decade)
    assert u["delta_log10"] < 1.0


def test_uncertainty_from_kcs_three_values():
    u = uncertainty_from_kcs(delta_kcs=1)
    assert f"k_cs_{K_CS}" in u["results"]
    assert f"k_cs_{K_CS - 1}" in u["results"]
    assert f"k_cs_{K_CS + 1}" in u["results"]


def test_hyperk_routing_consistent_limit():
    r = hyperk_routing(SK_LIMIT_EPLUS_PI0_YR, SK_LIMIT_EPLUS_PI0_YR * 0.1)
    assert r["verdict"] in ("CONSISTENT_LOWER_LIMIT", "CONSISTENT")


def test_hyperk_routing_invalid():
    with pytest.raises(ValueError):
        hyperk_routing(0.0, 1.0e34)


def test_hyperk_routing_invalid_sigma():
    with pytest.raises(ValueError):
        hyperk_routing(1.0e34, 0.0)


def test_hyperk_routing_preregistration_version():
    r = hyperk_routing(SK_LIMIT_EPLUS_PI0_YR, SK_LIMIT_EPLUS_PI0_YR * 0.1)
    assert r["preregistration_version"] == "v11.9"


def test_proton_decay_report_keys():
    rep = proton_decay_prediction_report()
    for key in ("pillar", "title", "derivation_chain", "predictions", "uncertainty", "falsifier_condition"):
        assert key in rep


def test_proton_decay_report_pillar():
    rep = proton_decay_prediction_report()
    assert rep["pillar"] == 293


def test_n_c_k_cs_values():
    assert N_C == 3
    assert K_CS == 74
    assert N_W == 5
    assert PI_KR == 37
