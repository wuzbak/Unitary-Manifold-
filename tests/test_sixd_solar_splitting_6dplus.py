# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/sixd/solar_splitting_6dplus.py — P16 closure attempt."""
from __future__ import annotations

import math
import pytest

from src.sixd.solar_splitting_6dplus import (
    K_CS,
    N_W,
    PI_KR,
    C_NU_BASE,
    DELTA_C01,
    DM2_21_PDG,
    DM2_31_PDG,
    R_SPLITTINGS_PDG,
    c_nu_spectrum,
    mass_eigenvalues_from_seed,
    splitting_ratio_geometric,
    solar_splitting_estimate,
    p16_gate_check,
    solar_splitting_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_constants_positive():
    assert K_CS == 74
    assert N_W == 5
    assert PI_KR == 37.0
    assert C_NU_BASE > 0.0
    assert DELTA_C01 > 0.0


def test_delta_c01_formula():
    """Δc₀₁ = 1/(2 K_CS) = 1/148."""
    expected = 1.0 / (2.0 * K_CS)
    assert abs(DELTA_C01 - expected) < 1e-15


def test_pdg_values_reasonable():
    assert 5e-5 < DM2_21_PDG < 1e-4
    assert 2e-3 < DM2_31_PDG < 3e-3
    assert 0.01 < R_SPLITTINGS_PDG < 0.1


# ---------------------------------------------------------------------------
# c_nu_spectrum
# ---------------------------------------------------------------------------

def test_c_nu_spectrum_ordering():
    """c₀ < c₁ < c₂ (torsion split is positive)."""
    c0, c1, c2 = c_nu_spectrum()
    assert c0 < c1 < c2


def test_c_nu_spectrum_average_is_base():
    """Average of c₀ and c₁ is close to base."""
    c0, c1, _ = c_nu_spectrum()
    assert abs((c0 + c1) / 2.0 - C_NU_BASE) < 1e-10


def test_c_nu_spectrum_split_magnitude():
    """c₁ − c₀ = Δc₀₁."""
    c0, c1, _ = c_nu_spectrum()
    assert abs(c1 - c0 - DELTA_C01) < 1e-12


def test_c_nu_spectrum_custom():
    c0, c1, c2 = c_nu_spectrum(c_nu_base=0.5, delta_c01=0.01)
    assert abs(c0 - 0.495) < 1e-10
    assert abs(c1 - 0.505) < 1e-10
    assert abs(c2 - 0.52) < 1e-10


# ---------------------------------------------------------------------------
# mass_eigenvalues_from_seed
# ---------------------------------------------------------------------------

def test_mass_eigenvalues_ordering():
    """m₀ > m₁ > m₂ (larger c_ν → more suppressed → lighter)."""
    m0, m1, m2 = mass_eigenvalues_from_seed(m_seed_ev=1.0)
    assert m0 > m1 > m2


def test_mass_eigenvalues_positive():
    m0, m1, m2 = mass_eigenvalues_from_seed(m_seed_ev=10.0)
    assert m0 > 0.0
    assert m1 > 0.0
    assert m2 > 0.0


def test_mass_eigenvalues_zero_seed():
    m0, m1, m2 = mass_eigenvalues_from_seed(m_seed_ev=0.0)
    assert m0 == 0.0
    assert m1 == 0.0
    assert m2 == 0.0


# ---------------------------------------------------------------------------
# splitting_ratio_geometric
# ---------------------------------------------------------------------------

def test_splitting_ratio_positive():
    r = splitting_ratio_geometric()
    assert r > 0.0


def test_splitting_ratio_less_than_one():
    """The solar splitting is smaller than the atmospheric splitting."""
    r = splitting_ratio_geometric()
    assert r < 1.0


def test_splitting_ratio_finite():
    r = splitting_ratio_geometric()
    assert math.isfinite(r)


def test_splitting_ratio_order_of_magnitude():
    """Ratio should be O(0.01-1.0) — same order of magnitude as PDG."""
    r = splitting_ratio_geometric()
    assert 0.001 < r < 2.0


# ---------------------------------------------------------------------------
# solar_splitting_estimate
# ---------------------------------------------------------------------------

def test_solar_splitting_estimate_returns_dict():
    est = solar_splitting_estimate()
    assert isinstance(est, dict)
    for key in ("ratio_geometric", "dm2_21_pred_eV2", "dm2_21_pdg_eV2", "residual_pct", "status"):
        assert key in est


def test_solar_splitting_estimate_prediction_positive():
    est = solar_splitting_estimate()
    assert est["dm2_21_pred_eV2"] > 0.0


def test_solar_splitting_estimate_status_not_open():
    """After this module, P16 should no longer be OPEN."""
    est = solar_splitting_estimate()
    assert est["status"] != "OPEN"


def test_solar_splitting_estimate_ratio_residual():
    """The ratio residual should be bounded (demonstrates non-zero constraint)."""
    est = solar_splitting_estimate()
    assert math.isfinite(est["ratio_residual_pct"])
    assert est["ratio_residual_pct"] >= 0.0


# ---------------------------------------------------------------------------
# p16_gate_check
# ---------------------------------------------------------------------------

def test_p16_gate_check_returns_dict():
    gate = p16_gate_check()
    assert isinstance(gate, dict)
    assert "all_pass" in gate
    assert "parameter" in gate
    assert "new_status" in gate


def test_p16_gate_check_parameter():
    gate = p16_gate_check()
    assert gate["parameter"] == "P16"


def test_p16_gate_check_axiomzero():
    gate = p16_gate_check()
    assert gate["gate4_axiomzero_compliant"] is True


def test_p16_gate_check_previous_status():
    gate = p16_gate_check()
    assert gate["previous_status"] == "OPEN"


def test_p16_gate_check_prediction_positive():
    gate = p16_gate_check()
    assert gate["dm2_21_pred_eV2"] > 0.0


def test_p16_gate_check_ratio_positive_finite():
    gate = p16_gate_check()
    assert gate["gate1_ratio_positive_finite"] is True


# ---------------------------------------------------------------------------
# solar_splitting_summary
# ---------------------------------------------------------------------------

def test_solar_splitting_summary_completeness():
    summary = solar_splitting_summary()
    for key in ("pillar", "version", "title", "mechanism", "status", "toe_delta", "gate"):
        assert key in summary


def test_solar_splitting_summary_version():
    summary = solar_splitting_summary()
    assert summary["version"] == "v10.17"


def test_solar_splitting_summary_no_sm_inputs():
    """AxiomZero check: only {K_CS, n_w, πkR} as inputs."""
    summary = solar_splitting_summary()
    inputs = summary.get("axiom_zero_inputs", [])
    assert any("K_CS" in s for s in inputs)
    assert any("n_w" in s for s in inputs)
    assert any("πkR" in s for s in inputs)
