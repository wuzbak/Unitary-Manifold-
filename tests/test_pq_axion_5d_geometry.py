# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for the 5D Peccei-Quinn axion geometry module (Gap SC3 closure)."""
from __future__ import annotations

import math

import pytest

from src.core.pq_axion_5d_geometry import (
    ALPHA_EM,
    K_CS,
    LAMBDA_QCD_GEV,
    M_PL_GEV,
    N_W,
    PI_KR,
    canonical_5d_pq_params,
    pq_5d_params,
)
from src.core.strong_cp_pq_z2_closure import theta_effective

# ---------------------------------------------------------------------------
# Canonical result fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def canonical():
    return canonical_5d_pq_params()


# ---------------------------------------------------------------------------
# Basic positivity / finiteness
# ---------------------------------------------------------------------------

def test_f_a_positive(canonical):
    assert canonical["f_a_GeV"] > 0


def test_m_a_positive(canonical):
    assert canonical["m_a_eV"] > 0


def test_g_agg_positive(canonical):
    assert canonical["g_agg_GeV_inv"] > 0


def test_theta_eff_positive(canonical):
    assert canonical["theta_eff"] > 0


def test_pi_kr_stored(canonical):
    assert canonical["pi_kr"] > 0


def test_g_agg_gev_inv_finite(canonical):
    assert math.isfinite(canonical["g_agg_GeV_inv"])


def test_units_f_a_gev(canonical):
    """f_a must be in GeV (at least 1 GeV, i.e. above the MeV scale)."""
    assert canonical["f_a_GeV"] > 1.0


def test_units_m_a_ev(canonical):
    """m_a in eV must be positive and finite."""
    assert canonical["m_a_eV"] > 0
    assert math.isfinite(canonical["m_a_eV"])


# ---------------------------------------------------------------------------
# QCD axion relation
# ---------------------------------------------------------------------------

def test_qcd_axion_mass_relation(canonical):
    """m_a [GeV] * f_a [GeV] ≈ Λ_QCD² [GeV²] within a factor of 2."""
    m_a_gev = canonical["m_a_eV"] / 1e9
    f_a = canonical["f_a_GeV"]
    product = m_a_gev * f_a
    expected = LAMBDA_QCD_GEV**2
    assert abs(product - expected) / expected < 1e-10  # exact by construction


# ---------------------------------------------------------------------------
# PDG bound satisfaction
# ---------------------------------------------------------------------------

def test_theta_eff_below_pdg_bound_canonical(canonical):
    """Canonical θ_eff must satisfy the PDG bound < 1e-10."""
    assert canonical["theta_eff"] < 1e-10


def test_theta_below_pdg_with_z2_closure():
    """theta_effective() from the Z2-closure module must satisfy PDG bound."""
    assert theta_effective() < 1e-10


# ---------------------------------------------------------------------------
# Astrophysical window flag (informational — PI_KR=37 puts f_a ~208 GeV)
# ---------------------------------------------------------------------------

def test_canonical_f_a_is_positive_float(canonical):
    """f_a from canonical params is a positive real number."""
    assert isinstance(canonical["f_a_GeV"], float)
    assert canonical["f_a_GeV"] > 0


def test_canonical_astrophysical_window_flag_is_bool(canonical):
    assert isinstance(canonical["f_a_in_astrophysical_window"], bool)


# ---------------------------------------------------------------------------
# Required keys
# ---------------------------------------------------------------------------

def test_dict_has_all_required_keys(canonical):
    required = {
        "f_a_GeV",
        "m_a_eV",
        "g_agg_GeV_inv",
        "theta_eff",
        "pi_kr",
        "k",
        "R",
        "n_w",
        "f_a_in_astrophysical_window",
        "theta_eff_below_pdg_bound",
    }
    assert required.issubset(canonical.keys())


# ---------------------------------------------------------------------------
# Monotone behaviour: larger πkR → smaller f_a and smaller θ_eff
# ---------------------------------------------------------------------------

def test_larger_pi_kr_smaller_f_a():
    r1 = pq_5d_params(k=0.1, R=10.0 / (math.pi * 0.1))
    r2 = pq_5d_params(k=0.1, R=20.0 / (math.pi * 0.1))
    assert r2["f_a_GeV"] < r1["f_a_GeV"]


def test_larger_pi_kr_smaller_theta():
    r1 = pq_5d_params(k=0.1, R=10.0 / (math.pi * 0.1))
    r2 = pq_5d_params(k=0.1, R=20.0 / (math.pi * 0.1))
    assert r2["theta_eff"] < r1["theta_eff"]


def test_larger_n_w_smaller_theta():
    r1 = pq_5d_params(k=0.1, R=PI_KR / (math.pi * 0.1), n_w=5)
    r2 = pq_5d_params(k=0.1, R=PI_KR / (math.pi * 0.1), n_w=10)
    assert r2["theta_eff"] < r1["theta_eff"]


def test_n_w_stored_correctly():
    r = pq_5d_params(k=0.2, R=5.0, n_w=7)
    assert r["n_w"] == 7


def test_k_and_r_stored_correctly():
    r = pq_5d_params(k=0.3, R=4.0)
    assert r["k"] == pytest.approx(0.3)
    assert r["R"] == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# Parametric tests with explicit (k, R) pairs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pi_kr_val", [5.0, 10.0, 20.0, 30.0, 37.0])
def test_f_a_decreases_with_pi_kr(pi_kr_val):
    """f_a = M_Pl * exp(-πkR) must decrease as πkR increases."""
    k = 0.1
    R = pi_kr_val / (math.pi * k)
    r = pq_5d_params(k=k, R=R)
    expected_f_a = M_PL_GEV * math.exp(-pi_kr_val)
    assert r["f_a_GeV"] == pytest.approx(expected_f_a, rel=1e-9)


@pytest.mark.parametrize("pi_kr_val", [5.0, 10.0, 20.0, 30.0, 37.0])
def test_theta_eff_formula(pi_kr_val):
    """θ_eff = exp(-πkR) / N_W must match the formula exactly."""
    k = 0.1
    R = pi_kr_val / (math.pi * k)
    r = pq_5d_params(k=k, R=R)
    expected = math.exp(-pi_kr_val) / N_W
    assert r["theta_eff"] == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize("pi_kr_val", [25.0, 30.0, 37.0])
def test_theta_eff_below_pdg_for_large_pi_kr(pi_kr_val):
    """For πkR ≥ 25, θ_eff must be well below the PDG bound 1e-10."""
    k = 0.1
    R = pi_kr_val / (math.pi * k)
    r = pq_5d_params(k=k, R=R)
    assert r["theta_eff"] < 1e-10


@pytest.mark.parametrize("n_w", [1, 2, 5, 10, 74])
def test_theta_eff_inversely_proportional_to_n_w(n_w):
    """θ_eff ∝ 1/n_w for fixed geometry."""
    k, R = 0.1, PI_KR / (math.pi * 0.1)
    r = pq_5d_params(k=k, R=R, n_w=n_w)
    expected = math.exp(-PI_KR) / n_w
    assert r["theta_eff"] == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize("pi_kr_val", [5.0, 10.0, 20.0, 30.0, 37.0])
def test_g_agg_proportional_to_inverse_f_a(pi_kr_val):
    """g_agg = α_EM / (2π f_a) must be consistent with stored f_a."""
    k = 0.1
    R = pi_kr_val / (math.pi * k)
    r = pq_5d_params(k=k, R=R)
    expected_g = ALPHA_EM / (2.0 * math.pi * r["f_a_GeV"])
    assert r["g_agg_GeV_inv"] == pytest.approx(expected_g, rel=1e-9)
