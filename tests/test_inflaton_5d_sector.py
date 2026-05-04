# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 161 — 5D Inflaton Sector A_s Normalization."""

import math
import pytest

from src.core.inflaton_5d_sector import (
    inflaton_4d_potential,
    slow_roll_parameters,
    hubble_inf_from_as,
    gw_alpha_parameter,
    as_normalization_status,
    inflaton_sector_admission2_update,
    pillar161_summary,
)

_NS_UM = 0.9635
_R_UM = 0.0315
_AS_PLANCK = 2.100e-9


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sr():
    return slow_roll_parameters()


@pytest.fixture(scope="module")
def h_info():
    return hubble_inf_from_as()


@pytest.fixture(scope="module")
def alpha_info():
    return gw_alpha_parameter()


@pytest.fixture(scope="module")
def norm_status():
    return as_normalization_status()


@pytest.fixture(scope="module")
def admission2():
    return inflaton_sector_admission2_update()


@pytest.fixture(scope="module")
def summary():
    return pillar161_summary()


# ---------------------------------------------------------------------------
# inflaton_4d_potential
# ---------------------------------------------------------------------------

def test_potential_at_minimum():
    """At φ=0 (minimum) with α=1, p=2: V_eff = V₀."""
    v = inflaton_4d_potential(v0_mpl4=1.0, phi_over_mpl=0.0, alpha=1.0, p=2)
    assert abs(v - 1.0) < 1e-10


def test_potential_quadratic():
    """Quadratic potential: V(φ) = V₀(1 + α φ²/M_Pl²)."""
    v = inflaton_4d_potential(v0_mpl4=1.0, phi_over_mpl=0.1, alpha=1.0, p=2)
    expected = 1.0 * (1.0 + 1.0 * 0.1**2)
    assert abs(v - expected) < 1e-10


def test_potential_positive():
    """Potential should always be positive near minimum."""
    for phi in [0.0, 0.01, 0.1, 0.5]:
        v = inflaton_4d_potential(v0_mpl4=1.0, phi_over_mpl=phi, alpha=1.0, p=2)
        assert v > 0.0


def test_potential_scales_with_v0():
    """V_eff scales linearly with V₀."""
    v1 = inflaton_4d_potential(v0_mpl4=1.0, phi_over_mpl=0.1, alpha=1.0, p=2)
    v2 = inflaton_4d_potential(v0_mpl4=2.0, phi_over_mpl=0.1, alpha=1.0, p=2)
    assert abs(v2 / v1 - 2.0) < 1e-10


# ---------------------------------------------------------------------------
# slow_roll_parameters
# ---------------------------------------------------------------------------

def test_sr_returns_dict(sr):
    assert isinstance(sr, dict)


def test_sr_has_epsilon(sr):
    assert "epsilon" in sr


def test_sr_has_eta(sr):
    assert "eta" in sr


def test_sr_epsilon_correct(sr):
    """ε = r/16 ≈ 0.00197 for r = 0.0315."""
    expected = _R_UM / 16.0
    assert abs(sr["epsilon"] - expected) < 1e-6


def test_sr_slow_roll_valid(sr):
    """ε << 1 and |η| << 1 must hold."""
    assert sr["slow_roll_valid"] is True


def test_sr_eta_negative(sr):
    """η_V < 0 for red-tilted spectrum: n_s=1-6ε+2η → η=(n_s-1+6ε)/2 < 0."""
    assert sr["eta"] < 0


def test_sr_eta_magnitude_small(sr):
    """|η| should be small (< 0.1) for slow-roll."""
    assert abs(sr["eta"]) < 0.1


def test_sr_ns_stored(sr):
    assert abs(sr["n_s"] - _NS_UM) < 1e-6


def test_sr_r_stored(sr):
    assert abs(sr["r_tensor"] - _R_UM) < 1e-6


def test_sr_custom_ns():
    """Larger n_s → η_V less negative (n_s=1-6ε+2η → η=(n_s-1+6ε)/2, increases with n_s)."""
    r1 = slow_roll_parameters(n_s=0.96, r_tensor=0.03)
    r2 = slow_roll_parameters(n_s=0.97, r_tensor=0.03)
    assert r2["eta"] > r1["eta"]  # larger n_s → η less negative


# ---------------------------------------------------------------------------
# hubble_inf_from_as
# ---------------------------------------------------------------------------

def test_h_info_returns_dict(h_info):
    assert isinstance(h_info, dict)


def test_h_info_has_h_inf_over_mpl(h_info):
    assert "h_inf_over_mpl" in h_info


def test_h_info_h_over_mpl_small(h_info):
    """H_inf/M_Pl should be ~1.81×10⁻⁵ for Planck A_s."""
    h = h_info["h_inf_over_mpl"]
    assert 1e-6 < h < 1e-4, f"Expected ~1.8e-5, got {h:.3e}"


def test_h_info_h_inf_gev_reasonable(h_info):
    """H_inf should be ~10¹⁴ GeV (matching Planck A_s)."""
    h_gev = h_info["h_inf_gev"]
    assert 1e12 < h_gev < 1e15, f"Expected ~2e14 GeV, got {h_gev:.2e}"


def test_h_info_formula(h_info):
    """Verify formula: (H/M_Pl)² = 8π² ε A_s."""
    expected_sq = 8.0 * math.pi**2 * (_R_UM / 16.0) * _AS_PLANCK
    expected = math.sqrt(expected_sq)
    assert abs(h_info["h_inf_over_mpl"] - expected) < 1e-10


def test_h_info_log10_suppression(h_info):
    """Required suppression should be ~4-5 orders below naive RS1 (H/M_Pl ~ 0.6)."""
    log = h_info["log10_suppression_needed"]
    assert log > 3.0, f"Expected >3 orders suppression, got {log:.1f}"


def test_h_info_interpretation_non_empty(h_info):
    assert len(h_info["interpretation"]) > 0


# ---------------------------------------------------------------------------
# gw_alpha_parameter
# ---------------------------------------------------------------------------

def test_alpha_returns_dict(alpha_info):
    assert isinstance(alpha_info, dict)


def test_alpha_not_derivable(alpha_info):
    """α is not derivable from UM topology alone."""
    assert alpha_info["derivable_from_um_topology"] is False


def test_alpha_very_small(alpha_info):
    """α_eff = V₀/M_Pl⁴ should be ~10⁻¹⁰ (extremely small)."""
    alpha = alpha_info["alpha_eff_V0_over_mpl4"]
    assert alpha < 1e-8, f"Expected ~1e-10, got {alpha:.3e}"


def test_alpha_log10_below_minus_9(alpha_info):
    """log₁₀(α_eff) should be < −8."""
    log = alpha_info["log10_alpha_eff"]
    assert log < -8.0, f"Expected < -8, got {log:.1f}"


def test_alpha_status_mentions_not_derivable(alpha_info):
    s = alpha_info["status"].lower()
    assert "not" in s or "open" in s


def test_alpha_formula_h_over_mpl():
    """α_eff = 3 × (H_inf/M_Pl)²."""
    h = hubble_inf_from_as()
    h_over_mpl = h["h_inf_over_mpl"]
    a = gw_alpha_parameter(h_inf_over_mpl=h_over_mpl)
    expected_alpha = 3.0 * h_over_mpl**2
    assert abs(a["alpha_eff_V0_over_mpl4"] - expected_alpha) < 1e-20


# ---------------------------------------------------------------------------
# as_normalization_status
# ---------------------------------------------------------------------------

def test_norm_returns_dict(norm_status):
    assert isinstance(norm_status, dict)


def test_norm_status_open(norm_status):
    assert "OPEN" in norm_status["status"].upper()


def test_norm_a_s_planck_stored(norm_status):
    assert abs(norm_status["a_s_planck"] - _AS_PLANCK) < 1e-12


def test_norm_ns_derived(norm_status):
    assert norm_status["what_is_derived"]["n_s"]["status"] == "DERIVED ✅"


def test_norm_r_derived(norm_status):
    assert norm_status["what_is_derived"]["r_tensor"]["status"] == "DERIVED ✅"


def test_norm_epsilon_derived(norm_status):
    assert norm_status["what_is_derived"]["epsilon"]["status"] == "DERIVED ✅"


def test_norm_as_not_derived(norm_status):
    assert "OPEN" in norm_status["what_is_not_derived"]["a_s"]["status"].upper()


def test_norm_cmb_suppression_documented(norm_status):
    suppression = norm_status["what_is_not_derived"]["cmb_peak_amplitudes"]["suppression"]
    assert "×" in suppression or "x" in suppression.lower()


def test_norm_rs_correction_wrong_direction(norm_status):
    verdict = norm_status["rs_correction_verdict"].lower()
    assert "wrong direction" in verdict or "enhance" in verdict or "cannot" in verdict


def test_norm_resolution_path_non_empty(norm_status):
    assert len(norm_status["resolution_path"]) > 0


# ---------------------------------------------------------------------------
# inflaton_sector_admission2_update
# ---------------------------------------------------------------------------

def test_admission2_returns_dict(admission2):
    assert isinstance(admission2, dict)


def test_admission2_number_2(admission2):
    assert admission2["admission_number"] == 2


def test_admission2_not_closed(admission2):
    assert admission2["closed"] is False


def test_admission2_has_updated_statement(admission2):
    assert "updated_statement" in admission2
    assert len(admission2["updated_statement"]) > 0


def test_admission2_ns_r_derived_listed(admission2):
    derived = admission2["what_is_derived"]
    assert "n_s" in derived
    assert "r" in derived


def test_admission2_as_not_derived_listed(admission2):
    not_derived = admission2["what_is_not_derived"]
    assert "A_s" in not_derived or "a_s" in not_derived


def test_admission2_root_cause_mentions_alpha(admission2):
    rc = admission2["root_cause"].lower()
    assert "α" in admission2["root_cause"] or "alpha" in rc


def test_admission2_suppression_range_documented(admission2):
    assert "cmb_suppression_range" in admission2
    assert "×" in admission2["cmb_suppression_range"]


# ---------------------------------------------------------------------------
# pillar161_summary
# ---------------------------------------------------------------------------

def test_summary_returns_dict(summary):
    assert isinstance(summary, dict)


def test_summary_pillar_161(summary):
    assert summary["pillar"] == 161


def test_summary_status_open(summary):
    assert "OPEN" in summary["status"].upper() or \
           "SCOPED" in summary["status"].upper()


def test_summary_key_findings(summary):
    kf = summary["key_findings"]
    assert kf["ns_r_derived"] is True
    assert kf["a_s_derived"] is False


def test_summary_rs_correction_wrong_direction(summary):
    direction = summary["key_findings"]["rs_correction_direction"].upper()
    assert "WRONG" in direction or "ENHANCEMENT" in direction


def test_summary_has_slow_roll(summary):
    assert "slow_roll" in summary
    assert summary["slow_roll"]["slow_roll_valid"] is True


def test_summary_has_hubble_inf(summary):
    assert "hubble_inf" in summary
    h = summary["hubble_inf"]["h_inf_over_mpl"]
    assert 1e-6 < h < 1e-4


def test_summary_has_alpha_gw(summary):
    assert "alpha_gw" in summary
    assert summary["alpha_gw"]["derivable_from_um_topology"] is False


def test_summary_open_issues_non_empty(summary):
    assert len(summary["open_issues"]) > 0


def test_summary_verdict_non_empty(summary):
    assert len(summary["verdict"]) > 0


def test_summary_verdict_mentions_a_s(summary):
    v = summary["verdict"].lower()
    assert "a_s" in v or "normali" in v
