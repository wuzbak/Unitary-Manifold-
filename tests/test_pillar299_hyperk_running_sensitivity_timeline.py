# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 299 — Hyper-Kamiokande Running Sensitivity Timeline."""
import math
import pytest
from src.core.pillar299_hyperk_running_sensitivity_timeline import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    HK_FIDUCIAL_KTON,
    HK_EFFICIENCY_EPLUS_PI0,
    HK_EFFICIENCY_NUBAR_KPLUS,
    HK_START_YEAR,
    HK_SENSITIVITY_1YR_EPLUS_PI0_YR,
    HK_SENSITIVITY_10YR_EPLUS_PI0_YR,
    SK_LIMIT_EPLUS_PI0_YR,
    MATRIX_ELEMENT_UNCERTAINTY,
    separation_guard,
    hk_year_sensitivity,
    hk_timeline,
    matrix_element_sensitivity_band,
    gut_model_comparison,
    hk_yearly_routing,
    proton_decay_timeline_report,
)


# ── Constants ──────────────────────────────────────────────────────────────


def test_pillar_number():
    assert PILLAR_NUMBER == 299


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_hk_fiducial_kton():
    assert HK_FIDUCIAL_KTON > 100.0


def test_hk_efficiency_eplus_pi0():
    assert 0.0 < HK_EFFICIENCY_EPLUS_PI0 <= 1.0


def test_hk_efficiency_nubar_kplus():
    assert 0.0 < HK_EFFICIENCY_NUBAR_KPLUS <= 1.0


def test_hk_start_year():
    assert HK_START_YEAR >= 2024


def test_hk_1yr_sensitivity_positive():
    assert HK_SENSITIVITY_1YR_EPLUS_PI0_YR > 0.0


def test_hk_10yr_greater_than_1yr():
    assert HK_SENSITIVITY_10YR_EPLUS_PI0_YR > HK_SENSITIVITY_1YR_EPLUS_PI0_YR


def test_sk_limit_below_hk_1yr():
    # SK limit should be below HK Year-1 sensitivity
    assert SK_LIMIT_EPLUS_PI0_YR < HK_SENSITIVITY_1YR_EPLUS_PI0_YR


def test_matrix_element_uncertainty():
    assert 0.0 < MATRIX_ELEMENT_UNCERTAINTY < 1.0


# ── separation_guard ────────────────────────────────────────────────────────


def test_separation_guard_pillar():
    g = separation_guard()
    assert g["pillar"] == 299


def test_separation_guard_not_hardgate():
    g = separation_guard()
    assert g["is_hardgate"] is False


def test_separation_guard_extends():
    g = separation_guard()
    assert g["extends_pillar"] == 293


def test_separation_guard_experiment():
    g = separation_guard()
    assert "Hyper" in g["experiment"]


# ── hk_year_sensitivity ─────────────────────────────────────────────────────


def test_year_sensitivity_year1():
    s = hk_year_sensitivity(1, mode="eplus_pi0")
    assert abs(s - HK_SENSITIVITY_1YR_EPLUS_PI0_YR) < 1e10


def test_year_sensitivity_year10():
    s = hk_year_sensitivity(10, mode="eplus_pi0")
    # Linear model: 10× Year-1 sensitivity
    expected = HK_SENSITIVITY_1YR_EPLUS_PI0_YR * 10.0
    assert abs(s / expected - 1.0) < 0.01


def test_year_sensitivity_linear():
    s1 = hk_year_sensitivity(1)
    s5 = hk_year_sensitivity(5)
    assert abs(s5 / s1 - 5.0) < 0.01


def test_year_sensitivity_nubar_mode():
    s = hk_year_sensitivity(10, mode="nubar_kplus")
    assert s > 0.0


def test_year_sensitivity_bad_year():
    with pytest.raises(ValueError):
        hk_year_sensitivity(0)


def test_year_sensitivity_bad_mode():
    with pytest.raises(ValueError):
        hk_year_sensitivity(1, mode="invalid")


# ── hk_timeline ─────────────────────────────────────────────────────────────


def test_timeline_length():
    tl = hk_timeline(tau_um_central=5e34, years=10)
    assert len(tl) == 10


def test_timeline_keys():
    tl = hk_timeline(tau_um_central=5e34)
    for entry in tl:
        for key in ("hk_year", "calendar_year", "sensitivity_yr",
                    "tau_um_yr", "um_above_sensitivity", "status",
                    "routing", "action"):
            assert key in entry, f"Missing key {key!r} in year {entry.get('hk_year')}"


def test_timeline_calendar_years():
    tl = hk_timeline(tau_um_central=5e34)
    for entry in tl:
        assert entry["calendar_year"] >= HK_START_YEAR


def test_timeline_sensitivity_grows():
    tl = hk_timeline(tau_um_central=5e34)
    sens = [e["sensitivity_yr"] for e in tl]
    assert all(sens[i] < sens[i + 1] for i in range(len(sens) - 1))


def test_timeline_um_above_initially():
    # If τ_um is large enough, should be above sensitivity in Year 1
    tl = hk_timeline(tau_um_central=1e36)
    assert tl[0]["um_above_sensitivity"] is True


def test_timeline_um_below_eventually():
    # If τ_um is small, should be inside sensitivity window by Year 10
    tl = hk_timeline(tau_um_central=1e33)
    assert tl[-1]["um_above_sensitivity"] is False


# ── matrix_element_sensitivity_band ─────────────────────────────────────────


def test_band_keys():
    b = matrix_element_sensitivity_band(5e34)
    for key in ("tau_central_yr", "matrix_element_uncertainty_pct",
                "tau_upper_yr", "tau_lower_yr", "band_factor"):
        assert key in b


def test_band_upper_gt_central():
    b = matrix_element_sensitivity_band(5e34)
    assert b["tau_upper_yr"] > b["tau_central_yr"]


def test_band_lower_lt_central():
    b = matrix_element_sensitivity_band(5e34)
    assert b["tau_lower_yr"] < b["tau_central_yr"]


def test_band_factor_formula():
    tau = 5e34
    b = matrix_element_sensitivity_band(tau)
    expected_upper = tau * (1 + MATRIX_ELEMENT_UNCERTAINTY) ** 2
    expected_lower = tau * (1 - MATRIX_ELEMENT_UNCERTAINTY) ** 2
    assert abs(b["tau_upper_yr"] - expected_upper) < 1e25
    assert abs(b["tau_lower_yr"] - expected_lower) < 1e25


def test_band_log10():
    tau = 5e34
    b = matrix_element_sensitivity_band(tau)
    assert abs(b["log10_tau_central"] - math.log10(tau)) < 1e-6


# ── gut_model_comparison ────────────────────────────────────────────────────


def test_gut_comparison_is_list():
    g = gut_model_comparison(5e34)
    assert isinstance(g, list)


def test_gut_comparison_has_um():
    g = gut_model_comparison(5e34)
    um_entries = [e for e in g if "Unitary" in e["theory"]]
    assert len(um_entries) == 1


def test_gut_comparison_um_viable():
    # With τ_um > SK limit, UM should be viable vs SK
    tau_um = 5e34
    g = gut_model_comparison(tau_um)
    um_entry = [e for e in g if "Unitary" in e["theory"]][0]
    assert um_entry["status_vs_sk"] == "VIABLE"


def test_gut_comparison_nonsusy_excluded():
    g = gut_model_comparison(5e34)
    minimal_su5 = [e for e in g if "Non-SUSY SU(5)" in e["theory"]]
    assert len(minimal_su5) == 1
    assert minimal_su5[0]["status_vs_sk"] == "EXCLUDED"


def test_gut_comparison_um_alpha_gut():
    g = gut_model_comparison(5e34)
    um_entry = [e for e in g if "Unitary" in e["theory"]][0]
    assert abs(um_entry["alpha_gut"] - 3.0 / 74.0) < 1e-10


def test_gut_comparison_all_have_required_fields():
    g = gut_model_comparison(5e34)
    for entry in g:
        for key in ("theory", "tau_range_yr", "status_vs_sk", "note"):
            assert key in entry, f"Missing {key!r} in {entry['theory']}"


# ── hk_yearly_routing ────────────────────────────────────────────────────────


def test_yearly_routing_keys():
    r = hk_yearly_routing(5e34)
    for key in ("tau_um_central_yr", "mode", "sk_limit_yr",
                "hk_1yr_sensitivity", "hk_10yr_sensitivity",
                "first_year_entering_window", "first_year_non_observation_tension",
                "matrix_element_band", "timeline", "preregistration_version"):
        assert key in r


def test_yearly_routing_preregistration_version():
    r = hk_yearly_routing(5e34)
    assert r["preregistration_version"] == "v11.10"


def test_yearly_routing_timeline_10_years():
    r = hk_yearly_routing(5e34)
    assert len(r["timeline"]) == 10


def test_yearly_routing_entering_window_positive():
    r = hk_yearly_routing(5e34)
    fw = r["first_year_entering_window"]
    assert fw is not None and fw >= 1


def test_yearly_routing_excluded_year_positive():
    r = hk_yearly_routing(5e34)
    fe = r["first_year_non_observation_tension"]
    assert fe is not None and fe >= 1


def test_yearly_routing_excluded_year_after_window():
    r = hk_yearly_routing(5e34)
    fw = r["first_year_entering_window"]
    fe = r["first_year_non_observation_tension"]
    assert fe >= fw


# ── proton_decay_timeline_report ─────────────────────────────────────────────


def test_report_keys():
    r = proton_decay_timeline_report()
    for key in ("pillar", "title", "adjacency_guard", "tau_um_central_yr",
                "eplus_pi0_routing", "nubar_kplus_routing",
                "gut_model_comparison", "summary", "status", "label"):
        assert key in r


def test_report_pillar():
    r = proton_decay_timeline_report()
    assert r["pillar"] == 299


def test_report_status():
    r = proton_decay_timeline_report()
    assert r["status"] == "TIMELINE_PREREGISTERED"


def test_report_label():
    r = proton_decay_timeline_report()
    assert r["label"] == "ADJACENT_TRACK"


def test_report_gut_comparison_present():
    r = proton_decay_timeline_report()
    guts = r["gut_model_comparison"]
    assert isinstance(guts, list)
    assert len(guts) >= 4


def test_report_default_tau():
    r = proton_decay_timeline_report()
    # Default tau_um_central should be in reasonable lifetime range
    tau = r["tau_um_central_yr"]
    assert 1e33 < tau < 1e37
