# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 160 — KK Axion Tower as Quintessence."""

import math
import pytest

from src.core.kk_axion_quintessence import (
    kk_axion_mass_tower,
    fifth_force_constraint_de_axion,
    multi_mode_wa_estimate,
    roman_telescope_falsification,
    pillar160_summary,
    de_open_declaration,
)

_H0_GEV = 1.445e-42
_M_KK_GEV = 1040.0


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def tower():
    return kk_axion_mass_tower()


@pytest.fixture(scope="module")
def fifth_force():
    return fifth_force_constraint_de_axion()


@pytest.fixture(scope="module")
def multi():
    return multi_mode_wa_estimate()


@pytest.fixture(scope="module")
def roman():
    return roman_telescope_falsification()


@pytest.fixture(scope="module")
def summary():
    return pillar160_summary()


# ---------------------------------------------------------------------------
# kk_axion_mass_tower
# ---------------------------------------------------------------------------

def test_tower_returns_dict(tower):
    assert isinstance(tower, dict)


def test_tower_has_modes(tower):
    assert "modes" in tower
    assert isinstance(tower["modes"], list)


def test_tower_default_n_modes(tower):
    assert len(tower["modes"]) == 10


def test_tower_lightest_mode_gev(tower):
    """m_1 = M_KK / π ≈ 331 GeV."""
    m1 = tower["lightest_mode_gev"]
    expected = _M_KK_GEV / math.pi
    assert abs(m1 - expected) < 1.0, f"Expected {expected:.1f} GeV, got {m1:.1f} GeV"


def test_tower_lightest_much_heavier_than_h0(tower):
    """m_1 must be many orders of magnitude heavier than H₀."""
    ratio = tower["lightest_over_H0"]
    assert ratio > 1e40, f"Expected >> H₀, got {ratio:.2e}"


def test_tower_no_quintessence_viable(tower):
    """No KK axion mode from the EW sector can serve as quintessence."""
    assert tower["any_quintessence_viable"] is False


def test_tower_wa_zero(tower):
    assert tower["wa_from_tower"] == 0.0


def test_tower_status_eliminated(tower):
    assert "ELIMINATED" in tower["status"].upper() or \
           "eliminated" in tower["status"].lower()


def test_tower_modes_ascending_mass(tower):
    """Modes should be ordered: m_n = n × M_KK / π, increasing with n."""
    masses = [m["m_n_gev"] for m in tower["modes"]]
    for i in range(1, len(masses)):
        assert masses[i] > masses[i - 1]


def test_tower_mode_mass_formula(tower):
    """Each mode mass should be n × M_KK / π."""
    for mode in tower["modes"]:
        n = mode["n"]
        expected = n * _M_KK_GEV / math.pi
        assert abs(mode["m_n_gev"] - expected) < 0.01


def test_tower_custom_n_max():
    t = kk_axion_mass_tower(n_max=3)
    assert len(t["modes"]) == 3


def test_tower_verdict_non_empty(tower):
    assert len(tower["verdict"]) > 0


# ---------------------------------------------------------------------------
# fifth_force_constraint_de_axion
# ---------------------------------------------------------------------------

def test_fifth_force_returns_dict(fifth_force):
    assert isinstance(fifth_force, dict)


def test_fifth_force_violates_cassini(fifth_force):
    """A gravitational-strength scalar violates Cassini by many orders."""
    assert fifth_force["violates_cassini"] is True


def test_fifth_force_delta_gamma_large(fifth_force):
    """|Δγ| for gravitational coupling should be ~2, far above limit 2.3e-5."""
    dg = fifth_force["delta_gamma_ppn"]
    assert dg >= 1.0


def test_fifth_force_violation_factor_huge(fifth_force):
    """Violation factor should be >> 10^4."""
    vf = fifth_force["violation_factor"]
    assert vf > 1e4


def test_fifth_force_de_mass_long_range(fifth_force):
    """A Hubble-mass axion has a solar-system-scale Compton wavelength."""
    assert fifth_force["is_solar_system_long_range"] is True


def test_fifth_force_eliminated(fifth_force):
    assert "ELIMINATED" in fifth_force["verdict"].upper() or \
           "eliminated" in fifth_force["verdict"].lower()


def test_fifth_force_uncoupled_passes():
    """Zero-coupling scalar has no fifth force."""
    r = fifth_force_constraint_de_axion(alpha_coupling=0.0)
    assert r["violates_cassini"] is False
    assert r["delta_gamma_ppn"] == 0.0


def test_fifth_force_weak_coupling_passes():
    """Extremely weak coupling (alpha=1e-10) passes Cassini."""
    r = fifth_force_constraint_de_axion(alpha_coupling=1e-10)
    dg = r["delta_gamma_ppn"]
    assert dg < 2.3e-5


# ---------------------------------------------------------------------------
# multi_mode_wa_estimate
# ---------------------------------------------------------------------------

def test_multi_returns_dict(multi):
    assert isinstance(multi, dict)


def test_multi_wa_approximately_zero(multi):
    """Multi-mode sum from frozen EW KK modes should give wₐ ≈ 0."""
    wa = multi["wa_aggregate"]
    assert abs(wa) < 1e-80, f"Expected wₐ ≈ 0, got {wa:.3e}"


def test_multi_tension_not_resolved(multi):
    """wₐ ≈ 0 should NOT match DESI wₐ ≈ −0.62."""
    assert multi["wa_tension_resolved"] is False


def test_multi_desi_central_correct(multi):
    assert abs(multi["wa_desi_central"] - (-0.62)) < 0.01


def test_multi_status_open(multi):
    assert "OPEN" in multi["status"].upper()


def test_multi_modes_count(multi):
    """Default 5 modes."""
    assert multi["n_modes"] == 5
    assert len(multi["mode_contributions"]) == 5


def test_multi_custom_modes():
    r = multi_mode_wa_estimate(n_modes=3)
    assert r["n_modes"] == 3
    assert len(r["mode_contributions"]) == 3


# ---------------------------------------------------------------------------
# roman_telescope_falsification
# ---------------------------------------------------------------------------

def test_roman_returns_dict(roman):
    assert isinstance(roman, dict)


def test_roman_has_experiment(roman):
    assert "experiment" in roman
    assert "roman" in roman["experiment"].lower() or \
           "Roman" in roman["experiment"]


def test_roman_sigma_w0(roman):
    """Roman σ(w₀) ≈ 0.02."""
    assert abs(roman["sigma_w0_roman"] - 0.02) < 1e-6


def test_roman_sigma_wa(roman):
    """Roman σ(wₐ) ≈ 0.10."""
    assert abs(roman["sigma_wa_roman"] - 0.10) < 1e-6


def test_roman_um_w0_prediction(roman):
    assert abs(roman["um_predictions"]["w0"] - (-0.9302)) < 1e-4


def test_roman_um_wa_prediction_zero(roman):
    assert roman["um_predictions"]["wa"] == 0.0


def test_roman_has_current_tensions(roman):
    assert "current_tensions" in roman
    ct = roman["current_tensions"]
    assert "w0_planck_bao_sigma" in ct
    assert "wa_desi_sigma" in ct


def test_roman_w0_tension_above_3sigma(roman):
    """Planck+BAO w₀ tension should be > 3σ."""
    sigma = roman["current_tensions"]["w0_planck_bao_sigma"]
    assert sigma > 3.0


def test_roman_wa_tension_above_1sigma(roman):
    """DESI wₐ tension should be > 1σ."""
    sigma = roman["current_tensions"]["wa_desi_sigma"]
    assert sigma > 1.0


def test_roman_falsification_conditions(roman):
    fc = roman["falsification_conditions"]
    assert "survive" in fc
    assert "falsify_w0" in fc
    assert "falsify_wa" in fc


def test_roman_status_open(roman):
    assert "OPEN" in roman["status"].upper()


def test_roman_has_formal_declaration(roman):
    assert "formal_declaration" in roman
    assert len(roman["formal_declaration"]) > 0


# ---------------------------------------------------------------------------
# pillar160_summary
# ---------------------------------------------------------------------------

def test_summary_returns_dict(summary):
    assert isinstance(summary, dict)


def test_summary_pillar_160(summary):
    assert summary["pillar"] == 160


def test_summary_status_open(summary):
    assert "OPEN" in summary["status"].upper()


def test_summary_has_analyses(summary):
    assert "analyses" in summary
    assert len(summary["analyses"]) >= 3


def test_summary_um_predictions(summary):
    preds = summary["um_predictions"]
    assert abs(preds["w0"] - (-0.9302)) < 1e-4
    assert preds["wa"] == 0.0


def test_summary_tensions_documented(summary):
    t = summary["tensions"]
    assert "w0_planck_bao" in t
    assert "wa_desi_cpl" in t


def test_summary_falsifier_roman(summary):
    assert "roman" in summary["falsifier"].lower() or \
           "Roman" in summary["falsifier"]


def test_summary_verdict_non_empty(summary):
    assert len(summary["verdict"]) > 0


# ---------------------------------------------------------------------------
# de_open_declaration
# ---------------------------------------------------------------------------

def test_declaration_is_string():
    d = de_open_declaration()
    assert isinstance(d, str)


def test_declaration_non_empty():
    d = de_open_declaration()
    assert len(d) > 0


def test_declaration_mentions_roman():
    d = de_open_declaration().lower()
    assert "roman" in d


def test_declaration_mentions_open():
    d = de_open_declaration().upper()
    assert "OPEN" in d


def test_declaration_mentions_birefringence():
    d = de_open_declaration().lower()
    assert "birefringence" in d or "β" in d


def test_declaration_mentions_desi():
    d = de_open_declaration().upper()
    assert "DESI" in d
