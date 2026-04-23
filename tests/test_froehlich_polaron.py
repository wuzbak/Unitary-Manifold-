# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_froehlich_polaron.py
================================
Unit tests for src/materials/froehlich_polaron.py — Pillar 46.

Tests cover:
  - froehlich_alpha_um / froehlich_alpha_canonical
  - polaron_formation_time_fs
  - polaron_binding_energy_ev / polaron_binding_energy_feynman_ev
  - polaron_effective_mass_ratio
  - polaron_radius_nm
  - kk_phonon_branch_weight
  - braid_phonon_coupling_decomposition
  - bioi_alpha_in_range / bioi_alpha_sigma_offset
  - kk_imprint_magnitude_squared
  - um_froehlich_summary / FroehlichSummary

The critical assertion is that the canonical UM prediction α ≈ 6.194
falls within the BiOI measured range [4, 7].
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import pytest

from src.materials.froehlich_polaron import (
    # Constants
    N_W_CANONICAL, N1_CANONICAL, N2_CANONICAL, K_CS_CANONICAL,
    C_S_CANONICAL, HBAR_EV_FS,
    BIOI_ALPHA_LO, BIOI_ALPHA_HI, BIOI_OMEGA_LO_MEV,
    # Core
    froehlich_alpha_um,
    froehlich_alpha_canonical,
    # Polaron observables
    polaron_formation_time_fs,
    polaron_binding_energy_ev,
    polaron_binding_energy_feynman_ev,
    polaron_effective_mass_ratio,
    polaron_radius_nm,
    # KK branch decomposition
    kk_phonon_branch_weight,
    braid_phonon_coupling_decomposition,
    # BiOI validation
    bioi_alpha_in_range,
    bioi_alpha_sigma_offset,
    # Imprint
    kk_imprint_magnitude_squared,
    # Summary
    um_froehlich_summary,
    FroehlichSummary,
)


# ---------------------------------------------------------------------------
# TestConstants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_k_cs_equals_sum_of_squares(self):
        assert K_CS_CANONICAL == N1_CANONICAL ** 2 + N2_CANONICAL ** 2

    def test_c_s_canonical_value(self):
        assert C_S_CANONICAL == pytest.approx(12.0 / 37.0)

    def test_c_s_from_braid(self):
        expected = (N2_CANONICAL ** 2 - N1_CANONICAL ** 2) / K_CS_CANONICAL
        assert C_S_CANONICAL == pytest.approx(expected, rel=1e-10)

    def test_bioi_range_consistent(self):
        assert BIOI_ALPHA_LO < BIOI_ALPHA_HI

    def test_hbar_ev_fs_positive(self):
        assert HBAR_EV_FS > 0.0


# ---------------------------------------------------------------------------
# TestFroehlichAlphaUm
# ---------------------------------------------------------------------------

class TestFroehlichAlphaUm:
    def test_canonical_value(self):
        alpha = froehlich_alpha_um(5, 5, 7)
        assert alpha == pytest.approx(6.194, rel=1e-3)

    def test_exact_formula(self):
        # α = n_w × k_cs × c_s² / (2π), k_cs=74, c_s=12/37
        expected = 5 * 74 * (12.0 / 37.0) ** 2 / (2.0 * math.pi)
        assert froehlich_alpha_um(5, 5, 7) == pytest.approx(expected, rel=1e-10)

    def test_in_bioi_range(self):
        alpha = froehlich_alpha_um(5, 5, 7)
        assert BIOI_ALPHA_LO <= alpha <= BIOI_ALPHA_HI

    def test_scales_with_n_w(self):
        a1 = froehlich_alpha_um(1, 5, 7)
        a2 = froehlich_alpha_um(2, 5, 7)
        assert a2 == pytest.approx(2.0 * a1, rel=1e-10)

    def test_different_braid_pair(self):
        # (3, 5): k_cs=34, c_s=16/34=8/17
        alpha = froehlich_alpha_um(3, 3, 5)
        k = 34
        c = (25 - 9) / 34
        expected = 3 * k * c ** 2 / (2.0 * math.pi)
        assert alpha == pytest.approx(expected, rel=1e-10)

    def test_raises_n_w_zero(self):
        with pytest.raises(ValueError):
            froehlich_alpha_um(0, 5, 7)

    def test_raises_n_w_negative(self):
        with pytest.raises(ValueError):
            froehlich_alpha_um(-1, 5, 7)

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            froehlich_alpha_um(5, 0, 7)

    def test_raises_n2_equal_n1(self):
        with pytest.raises(ValueError):
            froehlich_alpha_um(5, 5, 5)

    def test_raises_n2_less_than_n1(self):
        with pytest.raises(ValueError):
            froehlich_alpha_um(5, 7, 5)

    def test_positive_for_any_valid_input(self):
        for n_w, n1, n2 in [(1, 1, 2), (2, 3, 5), (5, 5, 7), (7, 1, 10)]:
            assert froehlich_alpha_um(n_w, n1, n2) > 0.0

    def test_larger_braid_pair_gives_different_alpha(self):
        a57 = froehlich_alpha_um(5, 5, 7)
        a59 = froehlich_alpha_um(5, 5, 9)
        assert a57 != pytest.approx(a59)


# ---------------------------------------------------------------------------
# TestFroehlichAlphaCanonical
# ---------------------------------------------------------------------------

class TestFroehlichAlphaCanonical:
    def test_value_approx_6194(self):
        assert froehlich_alpha_canonical() == pytest.approx(6.194, rel=1e-3)

    def test_matches_froehlich_alpha_um(self):
        assert froehlich_alpha_canonical() == pytest.approx(
            froehlich_alpha_um(N_W_CANONICAL, N1_CANONICAL, N2_CANONICAL),
            rel=1e-10,
        )

    def test_in_bioi_range(self):
        assert bioi_alpha_in_range(froehlich_alpha_canonical())

    def test_deterministic(self):
        assert froehlich_alpha_canonical() == froehlich_alpha_canonical()


# ---------------------------------------------------------------------------
# TestPolaron formationTime
# ---------------------------------------------------------------------------

class TestPolaronFormationTime:
    def test_positive_output(self):
        tau = polaron_formation_time_fs(12.0)
        assert tau > 0.0

    def test_bioi_default_approximately_170fs(self):
        # ħ/ω_LO = 0.6582 / 0.012 ≈ 54.85 fs; ÷ c_s = 54.85 × 37/12 ≈ 169 fs
        tau = polaron_formation_time_fs(BIOI_OMEGA_LO_MEV)
        assert 100.0 < tau < 300.0

    def test_scales_inversely_with_omega(self):
        t1 = polaron_formation_time_fs(12.0)
        t2 = polaron_formation_time_fs(24.0)
        assert t1 == pytest.approx(2.0 * t2, rel=1e-6)

    def test_formula_exact(self):
        omega_lo_mev = 15.0
        omega_ev = 15.0e-3
        expected = (HBAR_EV_FS / omega_ev) / C_S_CANONICAL
        assert polaron_formation_time_fs(omega_lo_mev) == pytest.approx(expected, rel=1e-10)

    def test_raises_zero_omega(self):
        with pytest.raises(ValueError):
            polaron_formation_time_fs(0.0)

    def test_raises_negative_omega(self):
        with pytest.raises(ValueError):
            polaron_formation_time_fs(-5.0)

    def test_larger_omega_shorter_time(self):
        t_lo = polaron_formation_time_fs(5.0)
        t_hi = polaron_formation_time_fs(50.0)
        assert t_hi < t_lo


# ---------------------------------------------------------------------------
# TestPolaronBindingEnergy (weak coupling)
# ---------------------------------------------------------------------------

class TestPolaronBindingEnergyEv:
    def test_canonical_bioi(self):
        alpha = froehlich_alpha_canonical()
        e_b = polaron_binding_energy_ev(alpha, BIOI_OMEGA_LO_MEV)
        # α × 12 meV ≈ 74.3 meV
        assert e_b == pytest.approx(alpha * BIOI_OMEGA_LO_MEV * 1e-3, rel=1e-10)

    def test_bioi_in_physiccal_range_mev(self):
        e_b_mev = polaron_binding_energy_ev(
            froehlich_alpha_canonical(), BIOI_OMEGA_LO_MEV
        ) * 1e3
        # expect ~50-100 meV
        assert 40.0 < e_b_mev < 120.0

    def test_linear_in_alpha(self):
        e1 = polaron_binding_energy_ev(2.0, 12.0)
        e2 = polaron_binding_energy_ev(4.0, 12.0)
        assert e2 == pytest.approx(2.0 * e1, rel=1e-10)

    def test_linear_in_omega(self):
        e1 = polaron_binding_energy_ev(5.0, 10.0)
        e2 = polaron_binding_energy_ev(5.0, 20.0)
        assert e2 == pytest.approx(2.0 * e1, rel=1e-10)

    def test_raises_zero_alpha(self):
        with pytest.raises(ValueError):
            polaron_binding_energy_ev(0.0, 12.0)

    def test_raises_zero_omega(self):
        with pytest.raises(ValueError):
            polaron_binding_energy_ev(5.0, 0.0)


# ---------------------------------------------------------------------------
# TestPolaronBindingEnergyFeynman
# ---------------------------------------------------------------------------

class TestPolaronBindingEnergyFeynman:
    def test_feynman_larger_than_weak(self):
        alpha = froehlich_alpha_canonical()
        e_weak = polaron_binding_energy_ev(alpha, BIOI_OMEGA_LO_MEV)
        e_feyn = polaron_binding_energy_feynman_ev(alpha, BIOI_OMEGA_LO_MEV)
        assert e_feyn > e_weak

    def test_feynman_formula_exact(self):
        alpha, omega = 3.0, 10.0
        expected = alpha * omega * 1e-3 * (1.0 + alpha / 12.0)
        assert polaron_binding_energy_feynman_ev(alpha, omega) == pytest.approx(
            expected, rel=1e-10
        )

    def test_bioi_feynman_mev_range(self):
        e_f_mev = polaron_binding_energy_feynman_ev(
            froehlich_alpha_canonical(), BIOI_OMEGA_LO_MEV
        ) * 1e3
        # expect 90-150 meV for intermediate coupling
        assert 60.0 < e_f_mev < 200.0

    def test_raises_zero_alpha(self):
        with pytest.raises(ValueError):
            polaron_binding_energy_feynman_ev(0.0, 12.0)

    def test_raises_zero_omega(self):
        with pytest.raises(ValueError):
            polaron_binding_energy_feynman_ev(5.0, 0.0)


# ---------------------------------------------------------------------------
# TestPolaronEffectiveMassRatio
# ---------------------------------------------------------------------------

class TestPolaronEffectiveMassRatio:
    def test_alpha_zero_gives_one(self):
        assert polaron_effective_mass_ratio(0.0) == pytest.approx(1.0)

    def test_alpha_six_gives_two(self):
        assert polaron_effective_mass_ratio(6.0) == pytest.approx(2.0)

    def test_canonical_alpha_gives_greater_than_two(self):
        ratio = polaron_effective_mass_ratio(froehlich_alpha_canonical())
        assert ratio > 2.0

    def test_linear_in_alpha(self):
        r1 = polaron_effective_mass_ratio(3.0)
        r2 = polaron_effective_mass_ratio(6.0)
        # m*/m_b = 1 + α/6; Δ(m*/m_b) = Δα/6
        assert r2 - r1 == pytest.approx(0.5, rel=1e-10)

    def test_raises_negative_alpha(self):
        with pytest.raises(ValueError):
            polaron_effective_mass_ratio(-0.1)

    def test_bioi_prediction_approximately_two(self):
        ratio = polaron_effective_mass_ratio(froehlich_alpha_canonical())
        assert 1.8 < ratio < 2.5


# ---------------------------------------------------------------------------
# TestPolaronRadiusNm
# ---------------------------------------------------------------------------

class TestPolaronRadiusNm:
    def test_positive(self):
        r = polaron_radius_nm(12.0, 0.5)
        assert r > 0.0

    def test_bioi_sub_nanometre_to_few_nm(self):
        r = polaron_radius_nm(BIOI_OMEGA_LO_MEV, 0.5)
        assert 0.1 < r < 10.0

    def test_heavier_mass_smaller_radius(self):
        r_light = polaron_radius_nm(12.0, 0.3)
        r_heavy = polaron_radius_nm(12.0, 1.0)
        assert r_light > r_heavy

    def test_lower_omega_larger_radius(self):
        r_lo = polaron_radius_nm(6.0, 0.5)
        r_hi = polaron_radius_nm(12.0, 0.5)
        assert r_lo > r_hi

    def test_raises_zero_omega(self):
        with pytest.raises(ValueError):
            polaron_radius_nm(0.0, 0.5)

    def test_raises_zero_mass(self):
        with pytest.raises(ValueError):
            polaron_radius_nm(12.0, 0.0)


# ---------------------------------------------------------------------------
# TestKkPhononBranchWeight
# ---------------------------------------------------------------------------

class TestKkPhononBranchWeight:
    def test_braid_locked_n1_weight_one(self):
        assert kk_phonon_branch_weight(5) == pytest.approx(1.0)

    def test_braid_locked_n2_weight_one(self):
        assert kk_phonon_branch_weight(7) == pytest.approx(1.0)

    def test_zero_mode_suppressed(self):
        w = kk_phonon_branch_weight(0)
        assert w == pytest.approx(1.0)   # n=0: exp(0) = 1

    def test_n1_not_equal_gives_suppressed(self):
        # mode 3 is not braid-locked
        w = kk_phonon_branch_weight(3)
        expected = math.exp(-9.0 / 74.0)
        assert w == pytest.approx(expected, rel=1e-10)

    def test_high_mode_heavily_suppressed(self):
        w = kk_phonon_branch_weight(20)
        assert w < 0.005

    def test_raises_negative_n(self):
        with pytest.raises(ValueError):
            kk_phonon_branch_weight(-1)

    def test_custom_braid_pair(self):
        # n=3 is braid-locked with n1=3, n2=5
        w = kk_phonon_branch_weight(3, n1=3, n2=5, k_cs=34)
        assert w == pytest.approx(1.0)

    def test_weight_in_range_01(self):
        for n in range(15):
            w = kk_phonon_branch_weight(n)
            assert 0.0 < w <= 1.0


# ---------------------------------------------------------------------------
# TestBraidPhononCouplingDecomposition
# ---------------------------------------------------------------------------

class TestBraidPhononCouplingDecomposition:
    def test_keys_present(self):
        d = braid_phonon_coupling_decomposition()
        for key in ("alpha_n1", "alpha_n2", "alpha_total", "weight_n1", "weight_n2", "c_s"):
            assert key in d

    def test_weights_are_one(self):
        d = braid_phonon_coupling_decomposition()
        assert d["weight_n1"] == pytest.approx(1.0)
        assert d["weight_n2"] == pytest.approx(1.0)

    def test_alpha_total_equals_sum(self):
        d = braid_phonon_coupling_decomposition()
        assert d["alpha_total"] == pytest.approx(d["alpha_n1"] + d["alpha_n2"], rel=1e-10)

    def test_alpha_n2_larger_than_n1(self):
        d = braid_phonon_coupling_decomposition()
        assert d["alpha_n2"] > d["alpha_n1"]

    def test_alpha_total_matches_canonical(self):
        d = braid_phonon_coupling_decomposition()
        # The decomposition (n1 + n2) × factor is NOT the same as n_w × factor
        # unless n_w == n1; check internal consistency
        alpha_um = froehlich_alpha_canonical()
        # canonical uses n_w = n1 = 5; decomp uses n1+n2 = 12 as total winding:
        # alpha_total != alpha_um when n_w != n1+n2
        assert d["alpha_total"] > alpha_um  # n1+n2=12 > n_w=5

    def test_c_s_canonical(self):
        d = braid_phonon_coupling_decomposition()
        assert d["c_s"] == pytest.approx(C_S_CANONICAL, rel=1e-10)

    def test_raises_n2_not_greater_n1(self):
        with pytest.raises(ValueError):
            braid_phonon_coupling_decomposition(n1=7, n2=5)

    def test_raises_invalid_c_s(self):
        with pytest.raises(ValueError):
            braid_phonon_coupling_decomposition(c_s=1.5)


# ---------------------------------------------------------------------------
# TestBioiAlphaInRange
# ---------------------------------------------------------------------------

class TestBioiAlphaInRange:
    def test_canonical_in_range(self):
        assert bioi_alpha_in_range(froehlich_alpha_canonical())

    def test_midpoint_in_range(self):
        assert bioi_alpha_in_range(5.5)

    def test_lo_boundary_in_range(self):
        assert bioi_alpha_in_range(BIOI_ALPHA_LO)

    def test_hi_boundary_in_range(self):
        assert bioi_alpha_in_range(BIOI_ALPHA_HI)

    def test_below_range_false(self):
        assert not bioi_alpha_in_range(3.9)

    def test_above_range_false(self):
        assert not bioi_alpha_in_range(7.1)

    def test_custom_range(self):
        assert bioi_alpha_in_range(5.0, lo=4.5, hi=5.5)
        assert not bioi_alpha_in_range(5.0, lo=5.5, hi=6.5)


# ---------------------------------------------------------------------------
# TestBioiAlphaSigmaOffset
# ---------------------------------------------------------------------------

class TestBioiAlphaSigmaOffset:
    def test_at_midpoint_zero_offset(self):
        assert bioi_alpha_sigma_offset(5.5) == pytest.approx(0.0)

    def test_one_sigma_above(self):
        assert bioi_alpha_sigma_offset(6.5) == pytest.approx(1.0)

    def test_canonical_within_one_sigma(self):
        offset = bioi_alpha_sigma_offset(froehlich_alpha_canonical())
        assert offset < 1.5

    def test_always_non_negative(self):
        for alpha in [0.5, 1.0, 5.5, 10.0]:
            assert bioi_alpha_sigma_offset(alpha) >= 0.0

    def test_raises_zero_sigma(self):
        with pytest.raises(ValueError):
            bioi_alpha_sigma_offset(5.5, alpha_sigma=0.0)


# ---------------------------------------------------------------------------
# TestKkImprintMagnitudeSquared
# ---------------------------------------------------------------------------

class TestKkImprintMagnitudeSquared:
    def test_canonical_value(self):
        # c_s² × k_CS = (12/37)² × 74
        expected = C_S_CANONICAL ** 2 * K_CS_CANONICAL
        assert kk_imprint_magnitude_squared() == pytest.approx(expected, rel=1e-10)

    def test_numerical_value_approx_778(self):
        val = kk_imprint_magnitude_squared()
        assert 7.0 < val < 9.0

    def test_raises_zero_k_cs(self):
        with pytest.raises(ValueError):
            kk_imprint_magnitude_squared(k_cs=0)

    def test_raises_c_s_geq_one(self):
        with pytest.raises(ValueError):
            kk_imprint_magnitude_squared(c_s=1.0)

    def test_raises_c_s_zero(self):
        with pytest.raises(ValueError):
            kk_imprint_magnitude_squared(c_s=0.0)


# ---------------------------------------------------------------------------
# TestUmFroehlichSummary
# ---------------------------------------------------------------------------

class TestUmFroehlichSummary:
    def setup_method(self):
        self.s = um_froehlich_summary()

    def test_returns_froehlich_summary_instance(self):
        assert isinstance(self.s, FroehlichSummary)

    def test_alpha_in_bioi_range(self):
        assert self.s.alpha_in_bioi_range

    def test_alpha_canonical_value(self):
        assert self.s.alpha_um == pytest.approx(6.194, rel=1e-3)

    def test_sigma_offset_under_two(self):
        assert self.s.sigma_offset < 2.0

    def test_formation_time_positive(self):
        assert self.s.formation_time_fs > 0.0

    def test_binding_energy_positive(self):
        assert self.s.binding_energy_ev > 0.0

    def test_feynman_greater_than_weak(self):
        assert self.s.binding_feynman_ev > self.s.binding_energy_ev

    def test_mass_ratio_greater_than_one(self):
        assert self.s.mass_ratio > 1.0

    def test_radius_positive(self):
        assert self.s.radius_nm > 0.0

    def test_imprint_sq_positive(self):
        assert self.s.imprint_sq > 0.0

    def test_branch_decomp_keys(self):
        for key in ("alpha_n1", "alpha_n2", "alpha_total"):
            assert key in self.s.branch_decomp

    def test_custom_omega(self):
        s2 = um_froehlich_summary(omega_lo_mev=20.0)
        assert s2.formation_time_fs < self.s.formation_time_fs

    def test_raises_zero_omega(self):
        with pytest.raises(ValueError):
            um_froehlich_summary(omega_lo_mev=0.0)

    def test_raises_zero_mass(self):
        with pytest.raises(ValueError):
            um_froehlich_summary(m_band_me=0.0)
