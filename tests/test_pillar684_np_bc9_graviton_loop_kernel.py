# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 684: NP BC9 Graviton One-Loop WdW Path-Integral Kernel."""

from __future__ import annotations

import math
import pytest

from src.core.pillar684_np_bc9_graviton_loop_kernel import (
    N_W, K_CS, N_MODES, PI_KR, M_KK_NATURAL, G_N_STAR,
    D_MASSIVE_GRAVITON, D_MASSLESS_GRAVITON, BESSEL_J2_ROOTS,
    graviton_kk_mass,
    graviton_kk_spectrum,
    one_loop_kernel_coefficient,
    kernel_relative_to_planck,
    np_bc9_algebraic_kernel,
    np_bc9_certificate,
    what_is_claimed,
    what_is_NOT_claimed,
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
)


# ── Constants ─────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 684


def test_version():
    assert VERSION == "v21.1"


def test_n_w_k_cs():
    assert N_W == 5
    assert K_CS == 74


def test_n_modes():
    assert N_MODES == N_W * K_CS
    assert N_MODES == 370


def test_pi_kr():
    expected = math.pi * K_CS / N_W
    assert abs(PI_KR - expected) < 1e-10


def test_m_kk_natural():
    expected = math.exp(-PI_KR)
    assert abs(M_KK_NATURAL - expected) < 1e-15


def test_m_kk_natural_tiny():
    # M_KK << M_Pl
    assert M_KK_NATURAL < 1e-15


def test_g_n_star():
    expected = 3.0 * math.pi / (N_W * K_CS - 10)
    assert abs(G_N_STAR - expected) < 1e-12


def test_g_n_star_range():
    # G_N* ≈ 0.026 (dimensionless in Planck units)
    assert 0.01 < G_N_STAR < 0.05


def test_d_massive():
    assert D_MASSIVE_GRAVITON == 5


def test_d_massless():
    assert D_MASSLESS_GRAVITON == 2


def test_bessel_roots_first():
    # x_1 ≈ 3.832
    assert abs(BESSEL_J2_ROOTS[0] - 3.8317) < 0.001


def test_bessel_roots_increasing():
    for i in range(len(BESSEL_J2_ROOTS) - 1):
        assert BESSEL_J2_ROOTS[i] < BESSEL_J2_ROOTS[i + 1]


# ── graviton_kk_mass ──────────────────────────────────────────────────────────

def test_graviton_mass_zero_mode():
    assert graviton_kk_mass(0) == 0.0


def test_graviton_mass_n1():
    expected = BESSEL_J2_ROOTS[0] * M_KK_NATURAL
    assert abs(graviton_kk_mass(1) - expected) < 1e-15


def test_graviton_mass_n2():
    expected = BESSEL_J2_ROOTS[1] * M_KK_NATURAL
    assert abs(graviton_kk_mass(2) - expected) < 1e-15


def test_graviton_mass_increasing():
    for n in range(1, 5):
        assert graviton_kk_mass(n) < graviton_kk_mass(n + 1)


def test_graviton_mass_n6_asymptotic():
    # n=6 uses asymptotic formula
    m6 = graviton_kk_mass(6)
    assert m6 > graviton_kk_mass(5)


def test_graviton_mass_positive_for_n_ge_1():
    for n in range(1, 6):
        assert graviton_kk_mass(n) > 0


# ── graviton_kk_spectrum ──────────────────────────────────────────────────────

def test_spectrum_length():
    spec = graviton_kk_spectrum(5)
    assert len(spec) == 6  # n = 0..5


def test_spectrum_zero_mode():
    spec = graviton_kk_spectrum(3)
    assert spec[0]["n"] == 0
    assert spec[0]["mass_natural"] == 0.0
    assert spec[0]["degeneracy"] == D_MASSLESS_GRAVITON


def test_spectrum_massive_modes():
    spec = graviton_kk_spectrum(3)
    for entry in spec[1:]:
        assert entry["degeneracy"] == D_MASSIVE_GRAVITON
        assert entry["mass_natural"] > 0


def test_spectrum_keys():
    spec = graviton_kk_spectrum(2)
    for entry in spec:
        for k in ["n", "mass_natural", "degeneracy"]:
            assert k in entry


# ── one_loop_kernel_coefficient ───────────────────────────────────────────────

def test_kernel_coefficient_keys():
    c = one_loop_kernel_coefficient()
    for k in ["n_modes", "d_massive", "m_kk_natural", "m_kk_4", "gamma_grav"]:
        assert k in c


def test_kernel_gamma_positive():
    c = one_loop_kernel_coefficient()
    assert c["gamma_grav"] > 0


def test_kernel_gamma_formula():
    c = one_loop_kernel_coefficient()
    expected = N_MODES * D_MASSIVE_GRAVITON / (32.0 * math.pi**2) * M_KK_NATURAL**4
    assert abs(c["gamma_grav"] - expected) < 1e-100  # extremely small


def test_kernel_m_kk_4():
    c = one_loop_kernel_coefficient()
    assert abs(c["m_kk_4"] - M_KK_NATURAL**4) < 1e-100


# ── kernel_relative_to_planck ─────────────────────────────────────────────────

def test_kernel_suppressed():
    rel = kernel_relative_to_planck()
    assert rel["exponentially_suppressed"] is True


def test_kernel_gamma_over_mpl4_tiny():
    rel = kernel_relative_to_planck()
    assert rel["gamma_grav_over_mpl4"] < 1e-70


def test_warp_exp_4():
    rel = kernel_relative_to_planck()
    expected = math.exp(-4.0 * PI_KR)
    assert abs(rel["warp_exp_4"] - expected) < 1e-100


def test_log10_gamma_negative():
    rel = kernel_relative_to_planck()
    assert rel["log10_gamma"] < -50


# ── np_bc9_algebraic_kernel ───────────────────────────────────────────────────

def test_kernel_at_fixed_point_zero():
    # K_BC9(G_N*) = 0 by construction
    result = np_bc9_algebraic_kernel(G_N_STAR)
    assert result["k_bc9"] == pytest.approx(0.0, abs=1e-200)


def test_kernel_at_fixed_point_flow_factor():
    result = np_bc9_algebraic_kernel(G_N_STAR)
    assert abs(result["flow_factor"]) < 1e-20


def test_kernel_at_g_n_zero():
    # At G_N = 0: flow_factor = 1
    result = np_bc9_algebraic_kernel(0.0)
    assert abs(result["flow_factor"] - 1.0) < 1e-12


def test_kernel_formula_string():
    result = np_bc9_algebraic_kernel(0.01)
    assert "K_BC9" in result["formula"]


def test_kernel_at_physical_gn():
    result = np_bc9_algebraic_kernel(1.0)
    # flow_factor = (1 − 1/G_N*)²
    expected_flow = (1.0 - 1.0 / G_N_STAR) ** 2
    assert abs(result["flow_factor"] - expected_flow) < 1e-10


def test_kernel_keys():
    result = np_bc9_algebraic_kernel(0.02)
    for k in ["g_n_input", "g_n_star", "gamma_grav", "flow_factor", "k_bc9"]:
        assert k in result


# ── np_bc9_certificate ────────────────────────────────────────────────────────

def test_certificate_keys():
    cert = np_bc9_certificate()
    for k in ["pillar", "title", "version", "status", "n_modes", "g_n_star",
              "graviton_spectrum_n0_to_5", "one_loop_coefficient",
              "claimed", "not_claimed", "next_bc"]:
        assert k in cert


def test_certificate_pillar():
    cert = np_bc9_certificate()
    assert cert["pillar"] == 684


def test_certificate_n_modes():
    cert = np_bc9_certificate()
    assert cert["n_modes"] == 370


def test_certificate_toe_zero():
    cert = np_bc9_certificate()
    assert "0" in cert["toe_impact"]


def test_certificate_next_bc():
    cert = np_bc9_certificate()
    assert "BC10" in cert["next_bc"]


def test_certificate_kernel_at_fixed_pt_zero():
    cert = np_bc9_certificate()
    k_fp = cert["kernel_at_fixed_point"]["k_bc9"]
    assert k_fp == pytest.approx(0.0, abs=1e-200)


def test_certificate_spectrum_has_6_entries():
    cert = np_bc9_certificate()
    assert len(cert["graviton_spectrum_n0_to_5"]) == 6


# ── claimed / not_claimed ─────────────────────────────────────────────────────

def test_claimed_list():
    c = what_is_claimed()
    assert isinstance(c, list)
    assert len(c) >= 4


def test_not_claimed_list():
    nc = what_is_NOT_claimed()
    assert isinstance(nc, list)
    assert len(nc) >= 3


def test_status_token():
    assert PILLAR_STATUS == "NP_BC9_GRAVITON_LOOP_KERNEL_COMPUTED"


# ── Numerical consistency ─────────────────────────────────────────────────────

def test_g_n_star_numer():
    # G_N* = 3π / (n_w × K_CS − 10) = 3π / 360
    expected = 3.0 * math.pi / (370 - 10)
    assert abs(G_N_STAR - expected) < 1e-12


def test_n_modes_formula():
    assert N_MODES == 370


def test_kernel_vanishes_exactly_at_fixed_point():
    # K(G_N*) = G_N* × Γ × (1 − G_N*/G_N*)² = 0
    result = np_bc9_algebraic_kernel(G_N_STAR)
    assert result["at_fixed_point"] is True
    assert result["k_bc9"] == pytest.approx(0.0, abs=1e-200)
