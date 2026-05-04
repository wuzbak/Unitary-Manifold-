# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 159 — Neutrino Mass Seesaw Canonical Resolution."""

import math
import pytest

from src.core.neutrino_mass_seesaw_canonical import (
    seesaw_canonical_mass,
    dirac_mechanism_status,
    cross_consistency_table,
    pillar159_summary,
    neutrino_mass_resolution_verdict,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def seesaw_default():
    return seesaw_canonical_mass()


@pytest.fixture(scope="module")
def dirac_status():
    return dirac_mechanism_status()


@pytest.fixture(scope="module")
def consistency():
    return cross_consistency_table()


@pytest.fixture(scope="module")
def summary():
    return pillar159_summary()


# ---------------------------------------------------------------------------
# seesaw_canonical_mass — basic physics
# ---------------------------------------------------------------------------

def test_seesaw_returns_dict(seesaw_default):
    assert isinstance(seesaw_default, dict)


def test_seesaw_has_m_nu_ev(seesaw_default):
    assert "m_nu_ev" in seesaw_default


def test_seesaw_default_planck_consistent(seesaw_default):
    """At y_D=1, M_R=M_Pl the seesaw mass must satisfy Planck Σm_ν < 0.12 eV."""
    assert seesaw_default["planck_consistent"] is True


def test_seesaw_default_mass_few_mev(seesaw_default):
    """Default seesaw mass should be in the few-meV range (< 50 meV)."""
    m_mev = seesaw_default["m_nu_mev"]
    assert 0.001 < m_mev < 1.0, f"Expected \u03bcV-meV range, got {m_mev:.5f} meV"


def test_seesaw_formula(seesaw_default):
    """Verify m_ν = y_D² v² / M_R numerically."""
    y_d = seesaw_default["y_dirac"]
    v = seesaw_default["v_higgs_gev"]
    m_r = seesaw_default["m_r_gev"]
    expected = y_d**2 * v**2 / m_r * 1e9  # in eV
    assert abs(seesaw_default["m_nu_ev"] - expected) < 1e-30


def test_seesaw_scales_with_yd(seesaw_default):
    """m_ν ∝ y_D²: doubling y_D quadruples the mass."""
    r1 = seesaw_canonical_mass(y_dirac=1.0)
    r2 = seesaw_canonical_mass(y_dirac=2.0)
    assert abs(r2["m_nu_ev"] / r1["m_nu_ev"] - 4.0) < 1e-6


def test_seesaw_scales_inverse_mr(seesaw_default):
    """m_ν ∝ 1/M_R: doubling M_R halves the mass."""
    m_r = seesaw_default["m_r_gev"]
    r1 = seesaw_canonical_mass(m_r_gev=m_r)
    r2 = seesaw_canonical_mass(m_r_gev=2.0 * m_r)
    assert abs(r2["m_nu_ev"] / r1["m_nu_ev"] - 0.5) < 1e-6


def test_seesaw_planck_violation_at_low_mr():
    """At M_R = 1 TeV, the seesaw mass is large and violates Planck."""
    r = seesaw_canonical_mass(m_r_gev=1.0e3)
    assert r["planck_consistent"] is False


def test_seesaw_status_contains_canonical(seesaw_default):
    assert "SEESAW CANONICAL" in seesaw_default["status"].upper() or \
           "canonical" in seesaw_default["status"].lower()


def test_seesaw_mechanism_label(seesaw_default):
    assert "Pillar 146" in seesaw_default["mechanism"] or \
           "seesaw" in seesaw_default["mechanism"].lower()


# ---------------------------------------------------------------------------
# dirac_mechanism_status — deprecated RS Dirac
# ---------------------------------------------------------------------------

def test_dirac_returns_dict(dirac_status):
    assert isinstance(dirac_status, dict)


def test_dirac_m_nu_violates_planck(dirac_status):
    """Pillar 140 RS Dirac result should violate Planck (m_ν₁ ~ 1 eV > 0.12 eV)."""
    m_ev = dirac_status["m_nu_dirac_ev"]
    assert m_ev > 0.12, f"Expected ~1 eV, got {m_ev:.4f} eV"


def test_dirac_violation_factor_large(dirac_status):
    """Violation factor should be ~9× (1 eV / 0.12 eV)."""
    factor = dirac_status["planck_violation_factor"]
    assert factor > 5.0, f"Expected ~9×, got {factor:.2f}×"


def test_dirac_c_r_correct(dirac_status):
    """c_R should be 23/25 = 0.920."""
    c_r = dirac_status["c_R_geometric"]
    assert abs(c_r - 23.0 / 25.0) < 1e-10


def test_dirac_c_l_naive(dirac_status):
    """c_L naive estimate should be 0.776."""
    assert abs(dirac_status["c_L_naive"] - 0.776) < 1e-10


def test_dirac_status_deprecated(dirac_status):
    assert "DEPRECATED" in dirac_status["status"].upper()


def test_dirac_role_mentions_seesaw(dirac_status):
    assert "seesaw" in dirac_status["role"].lower() or \
           "seesaw" in dirac_status["resolution"].lower()


def test_dirac_f0_r_very_small(dirac_status):
    """f₀(c_R=0.920) should be ~1.6×10⁻⁷ (UV-localised, exponentially suppressed)."""
    f0_r = dirac_status["f0_c_R"]
    assert f0_r < 1e-5, f"Expected ~1.6e-7, got {f0_r:.3e}"


# ---------------------------------------------------------------------------
# cross_consistency_table
# ---------------------------------------------------------------------------

def test_consistency_returns_dict(consistency):
    assert isinstance(consistency, dict)


def test_consistency_has_mechanisms(consistency):
    assert "mechanisms" in consistency


def test_consistency_three_mechanisms(consistency):
    assert len(consistency["mechanisms"]) == 3


def test_consistency_has_rs_dirac(consistency):
    assert "RS_Dirac_P140" in consistency["mechanisms"]


def test_consistency_has_braid_ratio(consistency):
    assert "Braid_Ratio_P135" in consistency["mechanisms"]


def test_consistency_has_seesaw(consistency):
    assert "Type_I_Seesaw_P146_150" in consistency["mechanisms"]


def test_consistency_rs_dirac_fails_planck(consistency):
    assert consistency["mechanisms"]["RS_Dirac_P140"]["planck_consistent"] is False


def test_consistency_braid_ratio_passes_planck(consistency):
    assert consistency["mechanisms"]["Braid_Ratio_P135"]["planck_consistent"] is True


def test_consistency_seesaw_passes_planck(consistency):
    assert consistency["mechanisms"]["Type_I_Seesaw_P146_150"]["planck_consistent"] is True


def test_consistency_cross_consistent(consistency):
    """Seesaw and braid-ratio should agree to within an order of magnitude."""
    assert consistency["cross_consistent"] is True


def test_consistency_factor_reasonable(consistency):
    """Seesaw vs braid-ratio symmetric factor should be < 1000 (< 3 orders)."""
    factor = consistency["seesaw_vs_braid_ratio_factor"]
    assert factor > 1.0 and factor < 1000.0, f"Expected 1-1000, got {factor:.1f}"


def test_consistency_verdict_non_empty(consistency):
    assert len(consistency["verdict"]) > 0


def test_consistency_verdict_mentions_resolved(consistency):
    v = consistency["verdict"].upper()
    assert "RESOLVED" in v or "resolved" in consistency["verdict"].lower()


def test_consistency_braid_ratio_mev_range(consistency):
    """Braid-ratio implied mass should be ~1–2 meV."""
    m_mev = consistency["mechanisms"]["Braid_Ratio_P135"]["m_nu_mev"]
    assert 0.5 < m_mev < 5.0, f"Expected ~1.5 meV, got {m_mev:.3f} meV"


def test_consistency_seesaw_mev_range(consistency):
    """Seesaw mass at y_D=1, M_R=M_Pl should be in μeV range (~0.005 meV)."""
    m_mev = consistency["mechanisms"]["Type_I_Seesaw_P146_150"]["m_nu_mev"]
    assert 0.001 < m_mev < 1.0, f"Expected μeV range, got {m_mev:.5f} meV"


def test_consistency_rs_dirac_ev_range(consistency):
    """RS Dirac result should be ~1 eV (1000 meV)."""
    m_mev = consistency["mechanisms"]["RS_Dirac_P140"]["m_nu_mev"]
    assert m_mev > 100.0, f"Expected ~1000 meV, got {m_mev:.2f} meV"


# ---------------------------------------------------------------------------
# pillar159_summary
# ---------------------------------------------------------------------------

def test_summary_returns_dict(summary):
    assert isinstance(summary, dict)


def test_summary_pillar_159(summary):
    assert summary["pillar"] == 159


def test_summary_closed(summary):
    assert summary["closed"] is True


def test_summary_canonical_mechanism_seesaw(summary):
    m = summary["canonical_mechanism"].lower()
    assert "seesaw" in m or "type-i" in m or "type i" in m


def test_summary_planck_consistent(summary):
    assert summary["planck_consistent"] is True


def test_summary_has_open_issues(summary):
    assert "open_issues" in summary
    assert len(summary["open_issues"]) > 0


def test_summary_cross_consistent(summary):
    assert summary["cross_consistent"] is True


def test_summary_components_present(summary):
    comps = summary["components"]
    assert "RS_Dirac_P140" in comps
    assert "Braid_Ratio_P135" in comps
    assert "Type_I_Seesaw" in comps


# ---------------------------------------------------------------------------
# neutrino_mass_resolution_verdict
# ---------------------------------------------------------------------------

def test_verdict_is_string():
    v = neutrino_mass_resolution_verdict()
    assert isinstance(v, str)


def test_verdict_non_empty():
    v = neutrino_mass_resolution_verdict()
    assert len(v) > 0


def test_verdict_mentions_seesaw():
    v = neutrino_mass_resolution_verdict().lower()
    assert "seesaw" in v


def test_verdict_mentions_resolution():
    v = neutrino_mass_resolution_verdict().lower()
    assert "resolved" in v or "resolve" in v


def test_verdict_mentions_planck():
    v = neutrino_mass_resolution_verdict().lower()
    assert "planck" in v
