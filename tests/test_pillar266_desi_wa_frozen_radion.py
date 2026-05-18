# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 266 — DESI wₐ frozen-radion quantitative EoS bound."""

import math
import pytest

from src.core.pillar266_desi_wa_frozen_radion import (
    H0_GEV,
    M_KK_REFERENCE_GEV,
    M_RADION_FRACTION,
    DESI_WA_CENTRAL_BAO,
    DESI_WA_SIGMA_BAO,
    DESI_WA_CENTRAL_COMBINED,
    DESI_WA_SIGMA_COMBINED,
    FALSIFICATION_SIGMA,
    WA_KK,
    W0_KK,
    radion_mass_gev,
    radion_hubble_ratio,
    frozen_wa_upper_bound,
    desi_tension_sigma,
    desi_y5_projection,
    wa_falsification_threshold,
    desi_wa_frozen_radion_report,
)

# ── radion_mass_gev ───────────────────────────────────────────────────────────

def test_radion_mass_default_fraction():
    """m_r = 0.1 · M_KK for default ε_GW = 0.01."""
    m_r = radion_mass_gev(M_KK_REFERENCE_GEV)
    expected = M_RADION_FRACTION * M_KK_REFERENCE_GEV
    assert math.isclose(m_r, expected, rel_tol=1e-9)


def test_radion_mass_physical_range():
    """Radion mass should be in GeV–TeV range for M_KK = 1 TeV."""
    m_r = radion_mass_gev(M_KK_REFERENCE_GEV)
    assert 1e1 <= m_r <= 1e9, f"m_r = {m_r} GeV outside GeV–PeV range"


def test_radion_mass_scales_with_mkk():
    """m_r is proportional to M_KK for fixed ε_GW."""
    m1 = radion_mass_gev(1e4)
    m2 = radion_mass_gev(2e4)
    assert math.isclose(m2 / m1, 2.0, rel_tol=1e-9)


def test_radion_mass_raises_nonpositive_mkk():
    with pytest.raises(ValueError):
        radion_mass_gev(-1e6)


def test_radion_mass_raises_bad_epsilon():
    with pytest.raises(ValueError):
        radion_mass_gev(1e6, epsilon_gw=0.0)
    with pytest.raises(ValueError):
        radion_mass_gev(1e6, epsilon_gw=1.5)


# ── radion_hubble_ratio ───────────────────────────────────────────────────────

def test_radion_hubble_ratio_frozen_condition():
    """m_r / H₀ >> 1 — the frozen-field condition must be overwhelmingly satisfied."""
    ratio = radion_hubble_ratio(M_KK_REFERENCE_GEV)
    assert ratio > 1e40, f"ratio = {ratio} — frozen condition not satisfied"


def test_radion_hubble_ratio_value():
    """For m_r = 1e5 GeV (100 TeV), ratio ≈ 6.9e46."""
    m_r = radion_mass_gev(M_KK_REFERENCE_GEV)
    expected = m_r / H0_GEV
    ratio = radion_hubble_ratio(M_KK_REFERENCE_GEV)
    assert math.isclose(ratio, expected, rel_tol=1e-9)


def test_radion_hubble_ratio_monotone_with_mkk():
    """Higher M_KK → larger ratio (more frozen)."""
    r1 = radion_hubble_ratio(1e5)
    r2 = radion_hubble_ratio(1e6)
    assert r2 > r1


# ── frozen_wa_upper_bound ─────────────────────────────────────────────────────

def test_wa_upper_bound_extremely_small():
    """|wₐ|_max must be negligibly small (< 10^{-90}) for TeV radion."""
    bound = frozen_wa_upper_bound(M_KK_REFERENCE_GEV)
    assert bound < 1e-90, f"|wₐ|_max = {bound} — not small enough"


def test_wa_upper_bound_much_less_than_one():
    """Basic sanity: |wₐ|_max << 1."""
    bound = frozen_wa_upper_bound(M_KK_REFERENCE_GEV)
    assert bound < 1.0


def test_wa_upper_bound_monotone_with_mkk():
    """Higher M_KK → smaller upper bound (more suppressed)."""
    b1 = frozen_wa_upper_bound(1e5)
    b2 = frozen_wa_upper_bound(1e6)
    assert b2 < b1


def test_wa_upper_bound_scales_with_f_radion():
    """Upper bound proportional to f_radion."""
    b1 = frozen_wa_upper_bound(M_KK_REFERENCE_GEV, f_radion=0.5)
    b2 = frozen_wa_upper_bound(M_KK_REFERENCE_GEV, f_radion=1.0)
    assert math.isclose(b2 / b1, 2.0, rel_tol=1e-9)


def test_wa_upper_bound_raises_bad_f_radion():
    with pytest.raises(ValueError):
        frozen_wa_upper_bound(M_KK_REFERENCE_GEV, f_radion=0.0)
    with pytest.raises(ValueError):
        frozen_wa_upper_bound(M_KK_REFERENCE_GEV, f_radion=1.5)


# ── desi_tension_sigma ────────────────────────────────────────────────────────

def test_desi_tension_bao_approx_2_07():
    """BAO-only tension: |0 - (-0.62)| / 0.30 ≈ 2.07σ."""
    sigma = desi_tension_sigma(WA_KK, DESI_WA_CENTRAL_BAO, DESI_WA_SIGMA_BAO)
    assert math.isclose(sigma, abs(DESI_WA_CENTRAL_BAO) / DESI_WA_SIGMA_BAO, rel_tol=1e-9)
    assert 2.0 < sigma < 2.2


def test_desi_tension_combined_approx_2_75():
    """Combined tension: |0 - (-0.55)| / 0.20 = 2.75σ."""
    sigma = desi_tension_sigma(WA_KK, DESI_WA_CENTRAL_COMBINED, DESI_WA_SIGMA_COMBINED)
    assert math.isclose(sigma, abs(DESI_WA_CENTRAL_COMBINED) / DESI_WA_SIGMA_COMBINED, rel_tol=1e-9)
    assert 2.7 < sigma < 2.8


def test_desi_tension_raises_nonpositive_sigma():
    with pytest.raises(ValueError):
        desi_tension_sigma(0.0, -0.5, -0.1)


def test_desi_tension_zero_when_equal():
    assert desi_tension_sigma(0.5, 0.5, 0.1) == 0.0


# ── wa_falsification_threshold ────────────────────────────────────────────────

def test_falsification_threshold_bao():
    """Critical |wₐ| for 3σ falsification with BAO σ = 0.30 is 0.90."""
    crit = wa_falsification_threshold(FALSIFICATION_SIGMA, DESI_WA_SIGMA_BAO)
    assert math.isclose(crit, 0.90, rel_tol=1e-9)


def test_falsification_threshold_combined():
    """Critical |wₐ| for 3σ with combined σ = 0.20 is 0.60."""
    crit = wa_falsification_threshold(FALSIFICATION_SIGMA, DESI_WA_SIGMA_COMBINED)
    assert math.isclose(crit, 0.60, rel_tol=1e-9)


# ── desi_y5_projection ────────────────────────────────────────────────────────

def test_y5_projection_will_falsify_if_central_persists():
    """If wₐ ≈ -0.62 persists to Y5 (σ=0.15), tension ≈ 4.1σ → will_falsify=True."""
    proj = desi_y5_projection(DESI_WA_CENTRAL_BAO)
    assert proj["will_falsify"] is True
    assert proj["tension_y5_sigma"] > 3.0


def test_y5_projection_returns_required_keys():
    proj = desi_y5_projection(DESI_WA_CENTRAL_BAO)
    for key in ("wa_central", "sigma_y5", "tension_y5_sigma", "will_falsify"):
        assert key in proj


def test_y5_projection_no_falsify_if_central_near_zero():
    """If wₐ = -0.10 (central shifts to near zero), no falsification."""
    proj = desi_y5_projection(-0.10)
    assert proj["will_falsify"] is False


# ── desi_wa_frozen_radion_report ──────────────────────────────────────────────

def test_report_has_required_keys():
    report = desi_wa_frozen_radion_report()
    required = [
        "m_radion_gev", "m_radion_over_hubble", "wa_upper_bound",
        "wa_prediction", "desi_tension_bao_sigma", "desi_tension_combined_sigma",
        "verdict", "desi_y5_falsification_risk", "closure_note",
    ]
    for key in required:
        assert key in report, f"Missing key: {key}"


def test_report_verdict_high_tension():
    """With current ~2.75σ max tension, verdict must be HIGH_TENSION."""
    report = desi_wa_frozen_radion_report()
    assert report["verdict"] == "HIGH_TENSION"


def test_report_wa_prediction_is_zero():
    report = desi_wa_frozen_radion_report()
    assert report["wa_prediction"] == 0.0


def test_report_y5_risk_is_true():
    """Y5 falsification risk should be True given current central values."""
    report = desi_wa_frozen_radion_report()
    assert report["desi_y5_falsification_risk"] is True


def test_report_monotone_bound_with_higher_mkk():
    """Higher M_KK → smaller wa_upper_bound."""
    r1 = desi_wa_frozen_radion_report(M_KK_gev=1e5)
    r2 = desi_wa_frozen_radion_report(M_KK_gev=1e6)
    assert r2["wa_upper_bound"] < r1["wa_upper_bound"]
