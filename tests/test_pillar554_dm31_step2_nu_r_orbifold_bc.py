# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 554 — DM31 Step 2: ν_R Orbifold BC Derivation."""
from __future__ import annotations

import math
import pytest
from src.core.pillar554_dm31_step2_nu_r_orbifold_bc import (
    C_R_CANONICAL,
    DELTA_C,
    DM31_STEP1,
    JUNO_DM31,
    JUNO_SIGMA,
    K_CS,
    K_PI_R,
    N_W,
    ORBIFOLD_BC_CORRECTION,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    STEP2_RESULT,
    VERSION,
    bessel_zero_approx,
    dm31_orbifold_shift,
    dm31_step2_projection,
    nu_r_kk_mass_lightest,
    orbifold_bc_factor,
    pillar_report,
    step2_certificate,
    tension_after_step2,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 554


def test_pillar_status():
    assert PILLAR_STATUS == "DM31_STEP2_NU_R_ORBIFOLD_BC_DERIVED"


def test_version():
    assert VERSION == "v19.2"


# ─── Constants ───────────────────────────────────────────────────────────────

def test_delta_c():
    assert DELTA_C == pytest.approx(5.0 / 74.0)


def test_k_pi_r():
    assert K_PI_R == pytest.approx(37.0)


def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_juno_dm31():
    assert JUNO_DM31 == pytest.approx(2.411e-3)


def test_dm31_step1_below_juno():
    assert DM31_STEP1 < JUNO_DM31


def test_c_r_canonical():
    assert C_R_CANONICAL == pytest.approx(0.0)


# ─── Bessel zero approximation ───────────────────────────────────────────────

def test_bessel_zero_alpha0():
    """J_0 first zero is 2.4048."""
    assert bessel_zero_approx(0.0) == pytest.approx(2.4048)


def test_bessel_zero_alpha_half():
    """J_{1/2} first zero is π (exact)."""
    assert bessel_zero_approx(0.5) == pytest.approx(math.pi, rel=1e-6)


def test_bessel_zero_alpha1():
    """J_1 first zero is 3.8317."""
    assert bessel_zero_approx(1.0) == pytest.approx(3.8317, rel=1e-3)


def test_bessel_zero_alpha2():
    """J_2 first zero is 5.1356."""
    assert bessel_zero_approx(2.0) == pytest.approx(5.1356, rel=1e-3)


def test_bessel_zero_positive():
    """All Bessel zeros are positive."""
    for alpha in [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]:
        assert bessel_zero_approx(alpha) > 0.0


def test_bessel_zero_increasing():
    """First zeros increase with order α."""
    prev = bessel_zero_approx(0.0)
    for alpha in [0.5, 1.0, 1.5, 2.0]:
        curr = bessel_zero_approx(alpha)
        assert curr > prev
        prev = curr


# ─── ν_R KK mass ─────────────────────────────────────────────────────────────

def test_nu_r_kk_mass_canonical():
    """For c_R = 0, m_{R,1} = M_KK × π."""
    mass = nu_r_kk_mass_lightest(c_r=0.0, m_kk=1.0)
    assert mass == pytest.approx(math.pi, rel=1e-6)


def test_nu_r_kk_mass_default_mKK():
    """Default m_kk = 1.0 gives M_KK = 1 result."""
    mass = nu_r_kk_mass_lightest(c_r=0.0)
    assert mass == pytest.approx(math.pi, rel=1e-6)


def test_nu_r_kk_mass_positive():
    """ν_R KK mass is always positive."""
    for c_r in [-0.5, 0.0, 0.25, 0.5, 1.0]:
        assert nu_r_kk_mass_lightest(c_r) > 0.0


def test_nu_r_kk_mass_increases_with_cr():
    """ν_R KK mass increases with |c_R + 1/2| (higher Bessel order)."""
    m0 = nu_r_kk_mass_lightest(c_r=0.0)     # α = 0.5 → x = π
    m1 = nu_r_kk_mass_lightest(c_r=0.5)     # α = 1.0 → x ≈ 3.83
    assert m1 > m0


def test_nu_r_kk_mass_scaling():
    """m_{R,1} scales linearly with M_KK."""
    m1 = nu_r_kk_mass_lightest(c_r=0.0, m_kk=1.0)
    m2 = nu_r_kk_mass_lightest(c_r=0.0, m_kk=2.0)
    assert m2 == pytest.approx(2.0 * m1)


# ─── Orbifold BC factor ───────────────────────────────────────────────────────

def test_orbifold_bc_factor_canonical():
    """f_orb(c_R=0) = π/2.4048 > 1."""
    f = orbifold_bc_factor(c_r=0.0, c_l=0.0)
    assert f == pytest.approx(math.pi / 2.4048, rel=1e-6)
    assert f > 1.0


def test_orbifold_bc_factor_positive():
    """f_orb is always positive."""
    for c_r in [0.0, 0.5 * DELTA_C, DELTA_C, 2 * DELTA_C]:
        assert orbifold_bc_factor(c_r, 0.0) > 0.0


def test_orbifold_bc_factor_increases_with_cr():
    """f_orb increases as c_R increases (higher Bessel order)."""
    f0 = orbifold_bc_factor(c_r=0.0, c_l=0.0)
    f1 = orbifold_bc_factor(c_r=0.5, c_l=0.0)
    assert f1 > f0


# ─── Δm²₃₁ orbifold shift ────────────────────────────────────────────────────

def test_dm31_orbifold_shift_keys():
    """Shift dict has required keys."""
    orb = dm31_orbifold_shift()
    required = [
        "frac_shift", "frac_shift_pct", "dm31_base_ev2",
        "dm31_corrected_ev2", "shift_ev2", "dirichlet_bc_satisfied",
    ]
    for key in required:
        assert key in orb, f"Missing key: {key}"


def test_dm31_orbifold_shift_positive():
    """Orbifold BC gives upward shift (toward JUNO)."""
    orb = dm31_orbifold_shift()
    assert orb["frac_shift"] > 0.0


def test_dm31_orbifold_shift_small():
    """Orbifold BC fractional shift is between 0.05% and 5%."""
    orb = dm31_orbifold_shift()
    assert 0.05 < orb["frac_shift_pct"] < 5.0


def test_dm31_corrected_above_base():
    """Corrected Δm²₃₁ > base (Step 1) value."""
    orb = dm31_orbifold_shift()
    assert orb["dm31_corrected_ev2"] > orb["dm31_base_ev2"]


def test_dm31_orbifold_dirichlet_bc():
    """Dirichlet BC is satisfied flag."""
    orb = dm31_orbifold_shift()
    assert orb["dirichlet_bc_satisfied"] is True


# ─── Step 2 projection ───────────────────────────────────────────────────────

def test_step2_projection_keys():
    """Projection dict has required keys."""
    proj = dm31_step2_projection()
    required = ["dm31_step1_ev2", "dm31_step2_ev2", "juno_ev2", "orbifold_frac_shift_pct"]
    for k in required:
        assert k in proj


def test_step2_above_step1():
    """Step 2 Δm²₃₁ > Step 1 (correction moves toward JUNO)."""
    proj = dm31_step2_projection()
    assert proj["dm31_step2_ev2"] > proj["dm31_step1_ev2"]


def test_step2_below_juno():
    """Step 2 estimate is still below JUNO (we haven't overshot)."""
    proj = dm31_step2_projection()
    assert proj["dm31_step2_ev2"] < proj["juno_ev2"]


# ─── Tension after Step 2 ────────────────────────────────────────────────────

def test_tension_after_step2_keys():
    """Tension dict has required keys."""
    t = tension_after_step2()
    required = [
        "tension_sigma_after_step1", "tension_sigma_after_step2", "improvement_step1_to_step2"
    ]
    for k in required:
        assert k in t


def test_tension_improved():
    """Step 2 reduces tension (improvement > 0)."""
    t = tension_after_step2()
    assert t["improvement_step1_to_step2"] > 0.0


def test_tension_step2_positive():
    """Remaining tension is positive (not overshot)."""
    t = tension_after_step2()
    assert t["tension_sigma_after_step2"] > 0.0


def test_tension_step2_below_step1():
    """Tension after Step 2 < tension after Step 1."""
    t = tension_after_step2()
    assert t["tension_sigma_after_step2"] < t["tension_sigma_after_step1"]


def test_tension_step2_within_3sigma():
    """Tension after Steps 1+2 is less than 3σ."""
    t = tension_after_step2()
    assert t["tension_sigma_after_step2"] < 3.0


def test_step2_result_module_level():
    """Module-level STEP2_RESULT is consistent with function results."""
    t = tension_after_step2()
    assert STEP2_RESULT["tension_after_sigma"] == pytest.approx(
        t["tension_sigma_after_step2"], rel=1e-6
    )


# ─── Step 2 certificate ──────────────────────────────────────────────────────

def test_certificate_pillar():
    cert = step2_certificate()
    assert cert["pillar"] == 554


def test_certificate_step():
    cert = step2_certificate()
    assert cert["step"] == 2


def test_certificate_status():
    cert = step2_certificate()
    assert cert["status"] == "DM31_STEP2_NU_R_ORBIFOLD_BC_DERIVED"


def test_certificate_toe_delta():
    cert = step2_certificate()
    assert cert["toe_score_delta"] == 0.0


def test_certificate_dirichlet_claimed():
    cert = step2_certificate()
    derived = cert["what_is_DERIVED"]
    assert any("Dirichlet" in s for s in derived)


def test_certificate_not_claimed_closed():
    cert = step2_certificate()
    not_claimed = cert["what_is_NOT_claimed"]
    assert any("Step 3" in s or "not claimed" in s.lower() or "closed" in s.lower()
               for s in not_claimed)


# ─── ORBIFOLD_BC_CORRECTION module constant ───────────────────────────────────

def test_orbifold_bc_correction_module_const():
    """Module-level constant is populated."""
    assert "frac_shift_pct" in ORBIFOLD_BC_CORRECTION
    assert ORBIFOLD_BC_CORRECTION["frac_shift_pct"] > 0.0


# ─── Pillar report ───────────────────────────────────────────────────────────

def test_pillar_report_keys():
    r = pillar_report()
    assert r["pillar"] == 554
    assert r["status"] == "DM31_STEP2_NU_R_ORBIFOLD_BC_DERIVED"
    assert r["closure_step"] == 2
    assert 3 in r["remaining_steps"]
    assert r["toe_score_delta"] == 0.0
    assert r["hardgate_score_delta"] == 0.0
    assert r["parent_pillar"] == 548


def test_pillar_report_no_adjacent_track():
    r = pillar_report()
    assert r["adjacent_track"] is False
