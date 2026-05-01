# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_aps_spin_structure.py
================================
Test suite for src/core/aps_spin_structure.py — Pillar 70-B.

Covers:
  - Module constants
  - dirac_z2_bc_table: structure, Z₂ parities, BC strings
  - orbifold_field_parity: known values, KeyError on unknown
  - hurwitz_zeta_zero: exact formula ½ − α
  - eta_function_zero: exact formula 1 − 2α
  - reduced_eta_bar_from_holonomy: α=0 → ½, α=½ → 0, intermediate
  - kk_spectrum_z2_even: integer/half-integer modes, length, ordering
  - aps_eta_from_kk_spectrum: matches eta_bar_from_cs_inflow for candidates
  - triangular_number: T(1)=1, T(5)=15, T(7)=28
  - braid_crossing_parity: sign = (−1)^T, patterns
  - cs_three_form_orbifold: n_w(n_w+1)/4 mod 1 for candidates
  - eta_bar_from_cs_inflow: 0.5 for n_w=5, 0.0 for n_w=7
  - zero_mode_z2_even: True for n_w=5, False for n_w=7
  - eta_bar_consistent: three methods agree
  - path_integral_phase: i for n_w=5, 1 for n_w=7
  - aps_integrality_residual: 0 for n_w=5 (bulk=½)
  - sm_chirality_requires_eta_half: structure, selection
  - nw_uniqueness_full_aps: selected_nw=5, keys, status
  - aps_full_derivation_chain: proof steps, status labels, advancement text

"""

import cmath
import math
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.aps_spin_structure import (
    N_W_CANONICAL,
    N_W2_CANONICAL,
    K_CS_CANONICAL,
    N_GEN_SM,
    ETA_BAR_NONTRIVIAL,
    ETA_BAR_TRIVIAL,
    Z2_EVEN,
    Z2_ODD,
    dirac_z2_bc_table,
    orbifold_field_parity,
    hurwitz_zeta_zero,
    eta_function_zero,
    reduced_eta_bar_from_holonomy,
    kk_spectrum_z2_even,
    aps_eta_from_kk_spectrum,
    triangular_number,
    braid_crossing_parity,
    cs_three_form_orbifold,
    eta_bar_from_cs_inflow,
    zero_mode_z2_even,
    eta_bar_consistent,
    path_integral_phase,
    aps_integrality_residual,
    sm_chirality_requires_eta_half,
    nw_uniqueness_full_aps,
    aps_full_derivation_chain,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_n_w2_canonical(self):
        assert N_W2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_k_cs_sum_of_squares(self):
        assert K_CS_CANONICAL == N_W_CANONICAL**2 + N_W2_CANONICAL**2

    def test_n_gen_sm(self):
        assert N_GEN_SM == 3

    def test_eta_nontrivial(self):
        assert ETA_BAR_NONTRIVIAL == pytest.approx(0.5, rel=1e-10)

    def test_eta_trivial(self):
        assert ETA_BAR_TRIVIAL == pytest.approx(0.0, abs=1e-14)

    def test_z2_even(self):
        assert Z2_EVEN == 1

    def test_z2_odd(self):
        assert Z2_ODD == -1


# ---------------------------------------------------------------------------
# dirac_z2_bc_table
# ---------------------------------------------------------------------------

class TestDiracZ2BcTable:
    def setup_method(self):
        self.table = dirac_z2_bc_table()

    def test_returns_dict(self):
        assert isinstance(self.table, dict)

    def test_has_metric_key(self):
        assert "metric_g_munu" in self.table

    def test_has_kk_photon_key(self):
        assert "kk_photon_A_mu" in self.table

    def test_has_radion_key(self):
        assert "radion_sigma" in self.table

    def test_has_gauge_a5_key(self):
        assert "gauge_A5" in self.table

    def test_has_spinor_r_key(self):
        assert "spinor_psi_R" in self.table

    def test_has_spinor_l_key(self):
        assert "spinor_psi_L" in self.table

    def test_six_fields(self):
        assert len(self.table) == 6

    def test_metric_z2_even(self):
        assert self.table["metric_g_munu"]["parity"] == Z2_EVEN

    def test_kk_photon_z2_odd(self):
        assert self.table["kk_photon_A_mu"]["parity"] == Z2_ODD

    def test_radion_z2_even(self):
        assert self.table["radion_sigma"]["parity"] == Z2_EVEN

    def test_gauge_a5_z2_odd(self):
        assert self.table["gauge_A5"]["parity"] == Z2_ODD

    def test_spinor_r_z2_even(self):
        assert self.table["spinor_psi_R"]["parity"] == Z2_EVEN

    def test_spinor_l_z2_odd(self):
        assert self.table["spinor_psi_L"]["parity"] == Z2_ODD

    def test_metric_survives(self):
        assert self.table["metric_g_munu"]["survives"] is True

    def test_kk_photon_does_not_survive(self):
        assert self.table["kk_photon_A_mu"]["survives"] is False

    def test_radion_survives(self):
        assert self.table["radion_sigma"]["survives"] is True

    def test_gauge_a5_does_not_survive(self):
        assert self.table["gauge_A5"]["survives"] is False

    def test_spinor_r_survives(self):
        assert self.table["spinor_psi_R"]["survives"] is True

    def test_spinor_l_does_not_survive(self):
        assert self.table["spinor_psi_L"]["survives"] is False

    def test_kk_photon_has_dirichlet_bc(self):
        assert "Dirichlet" in self.table["kk_photon_A_mu"]["bc"]

    def test_gauge_a5_has_dirichlet_bc(self):
        assert "Dirichlet" in self.table["gauge_A5"]["bc"]

    def test_spinor_l_has_dirichlet_bc(self):
        assert "Dirichlet" in self.table["spinor_psi_L"]["bc"]

    def test_entries_are_dicts(self):
        for key, val in self.table.items():
            assert isinstance(val, dict), f"{key} should be a dict"

    def test_parity_in_plus_minus_1(self):
        for key, val in self.table.items():
            assert val["parity"] in (1, -1), f"{key} has invalid parity"


# ---------------------------------------------------------------------------
# orbifold_field_parity
# ---------------------------------------------------------------------------

class TestOrbifoldFieldParity:
    def test_metric_even(self):
        assert orbifold_field_parity("metric") == Z2_EVEN

    def test_kk_photon_odd(self):
        assert orbifold_field_parity("kk_photon") == Z2_ODD

    def test_radion_even(self):
        assert orbifold_field_parity("radion") == Z2_EVEN

    def test_gauge_a5_odd(self):
        assert orbifold_field_parity("gauge_a5") == Z2_ODD

    def test_spinor_r_even(self):
        assert orbifold_field_parity("spinor_R") == Z2_EVEN

    def test_spinor_l_odd(self):
        assert orbifold_field_parity("spinor_L") == Z2_ODD

    def test_unknown_raises_key_error(self):
        with pytest.raises(KeyError):
            orbifold_field_parity("gravitino")

    def test_output_type(self):
        assert isinstance(orbifold_field_parity("metric"), int)


# ---------------------------------------------------------------------------
# hurwitz_zeta_zero
# ---------------------------------------------------------------------------

class TestHurwitzZetaZero:
    def test_alpha_half(self):
        assert hurwitz_zeta_zero(0.5) == pytest.approx(0.0, abs=1e-14)

    def test_alpha_quarter(self):
        assert hurwitz_zeta_zero(0.25) == pytest.approx(0.25, rel=1e-10)

    def test_alpha_one(self):
        # ζ_H(0, 1) = ½ − 1 = −½
        assert hurwitz_zeta_zero(1.0) == pytest.approx(-0.5, rel=1e-10)

    def test_alpha_three_quarters(self):
        assert hurwitz_zeta_zero(0.75) == pytest.approx(-0.25, rel=1e-10)

    def test_formula_exact(self):
        for alpha in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            expected = 0.5 - alpha
            assert hurwitz_zeta_zero(alpha) == pytest.approx(expected, rel=1e-10)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            hurwitz_zeta_zero(0.0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            hurwitz_zeta_zero(-0.1)

    def test_above_one_raises(self):
        with pytest.raises(ValueError):
            hurwitz_zeta_zero(1.1)

    def test_output_type(self):
        assert isinstance(hurwitz_zeta_zero(0.5), float)


# ---------------------------------------------------------------------------
# eta_function_zero
# ---------------------------------------------------------------------------

class TestEtaFunctionZero:
    def test_alpha_quarter(self):
        assert eta_function_zero(0.25) == pytest.approx(0.5, rel=1e-10)

    def test_alpha_three_quarters(self):
        assert eta_function_zero(0.75) == pytest.approx(-0.5, rel=1e-10)

    def test_alpha_half(self):
        assert eta_function_zero(0.5) == pytest.approx(0.0, abs=1e-14)

    def test_formula_1_minus_2alpha(self):
        for alpha in [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]:
            expected = 1.0 - 2.0 * alpha
            assert eta_function_zero(alpha) == pytest.approx(expected, rel=1e-10)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            eta_function_zero(0.0)

    def test_one_raises(self):
        with pytest.raises(ValueError):
            eta_function_zero(1.0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            eta_function_zero(-0.1)

    def test_output_type(self):
        assert isinstance(eta_function_zero(0.5), float)

    def test_matches_hurwitz_difference(self):
        # η(0,α) = ζ_H(0,α) − ζ_H(0, 1−α)
        for alpha in [0.1, 0.2, 0.3, 0.4]:
            hurwitz_diff = hurwitz_zeta_zero(alpha) - hurwitz_zeta_zero(1.0 - alpha)
            assert eta_function_zero(alpha) == pytest.approx(hurwitz_diff, rel=1e-10)


# ---------------------------------------------------------------------------
# reduced_eta_bar_from_holonomy
# ---------------------------------------------------------------------------

class TestReducedEtaBarFromHolonomy:
    def test_alpha_zero_gives_half(self):
        assert reduced_eta_bar_from_holonomy(0.0) == pytest.approx(0.5, rel=1e-10)

    def test_alpha_half_gives_zero(self):
        assert reduced_eta_bar_from_holonomy(0.5) == pytest.approx(0.0, abs=1e-14)

    def test_alpha_quarter(self):
        # (1 − 2×0.25) / 2 = 0.5 / 2 = 0.25
        assert reduced_eta_bar_from_holonomy(0.25) == pytest.approx(0.25, rel=1e-10)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            reduced_eta_bar_from_holonomy(-0.1)

    def test_above_half_raises(self):
        with pytest.raises(ValueError):
            reduced_eta_bar_from_holonomy(0.6)

    def test_output_in_unit_interval(self):
        for alpha in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
            val = reduced_eta_bar_from_holonomy(alpha)
            assert 0.0 <= val <= 0.5


# ---------------------------------------------------------------------------
# kk_spectrum_z2_even
# ---------------------------------------------------------------------------

class TestKkSpectrumZ2Even:
    def test_n_w_5_starts_at_zero(self):
        spec = kk_spectrum_z2_even(5, n_modes=5)
        assert spec[0] == pytest.approx(0.0, abs=1e-14)

    def test_n_w_5_integer_modes(self):
        spec = kk_spectrum_z2_even(5, n_modes=4)
        assert spec == [0.0, 1.0, 2.0, 3.0, 4.0]

    def test_n_w_7_starts_at_half(self):
        spec = kk_spectrum_z2_even(7, n_modes=5)
        assert spec[0] == pytest.approx(0.5, rel=1e-10)

    def test_n_w_7_half_integer_modes(self):
        spec = kk_spectrum_z2_even(7, n_modes=3)
        assert spec == pytest.approx([0.5, 1.5, 2.5, 3.5], rel=1e-10)

    def test_n_w_1_integer_modes(self):
        # 1 ≡ 1 (mod 4) → α = 0
        spec = kk_spectrum_z2_even(1, n_modes=2)
        assert spec == pytest.approx([0.0, 1.0, 2.0], rel=1e-10)

    def test_n_w_3_half_integer_modes(self):
        # 3 ≡ 3 (mod 4) → α = ½
        spec = kk_spectrum_z2_even(3, n_modes=2)
        assert spec == pytest.approx([0.5, 1.5, 2.5], rel=1e-10)

    def test_n_w_9_integer_modes(self):
        # 9 ≡ 1 (mod 4) → α = 0
        spec = kk_spectrum_z2_even(9, n_modes=2)
        assert spec == pytest.approx([0.0, 1.0, 2.0], rel=1e-10)

    def test_n_w_11_half_integer_modes(self):
        # 11 ≡ 3 (mod 4) → α = ½
        spec = kk_spectrum_z2_even(11, n_modes=2)
        assert spec == pytest.approx([0.5, 1.5, 2.5], rel=1e-10)

    def test_length_n_modes_plus_1(self):
        for n_modes in [1, 5, 10]:
            spec = kk_spectrum_z2_even(5, n_modes=n_modes)
            assert len(spec) == n_modes + 1

    def test_ascending_order(self):
        spec = kk_spectrum_z2_even(5, n_modes=10)
        assert spec == sorted(spec)

    def test_even_n_w_raises(self):
        with pytest.raises(ValueError):
            kk_spectrum_z2_even(4)

    def test_zero_n_w_raises(self):
        with pytest.raises(ValueError):
            kk_spectrum_z2_even(0)

    def test_n_modes_zero_raises(self):
        with pytest.raises(ValueError):
            kk_spectrum_z2_even(5, n_modes=0)

    def test_output_type(self):
        assert isinstance(kk_spectrum_z2_even(5, n_modes=3), list)

    def test_elements_are_float(self):
        spec = kk_spectrum_z2_even(5, n_modes=3)
        for s in spec:
            assert isinstance(s, float)


# ---------------------------------------------------------------------------
# aps_eta_from_kk_spectrum
# ---------------------------------------------------------------------------

class TestApsEtaFromKkSpectrum:
    def test_n_w_5_is_half(self):
        assert aps_eta_from_kk_spectrum(5) == pytest.approx(0.5, rel=1e-10)

    def test_n_w_7_is_zero(self):
        assert aps_eta_from_kk_spectrum(7) == pytest.approx(0.0, abs=1e-14)

    def test_n_w_1_is_half(self):
        assert aps_eta_from_kk_spectrum(1) == pytest.approx(0.5, rel=1e-10)

    def test_n_w_3_is_zero(self):
        assert aps_eta_from_kk_spectrum(3) == pytest.approx(0.0, abs=1e-14)

    def test_n_w_9_is_half(self):
        assert aps_eta_from_kk_spectrum(9) == pytest.approx(0.5, rel=1e-10)

    def test_n_w_11_is_zero(self):
        assert aps_eta_from_kk_spectrum(11) == pytest.approx(0.0, abs=1e-14)

    def test_agrees_with_cs_inflow(self):
        for n_w in [1, 3, 5, 7, 9, 11, 13, 15]:
            assert aps_eta_from_kk_spectrum(n_w) == pytest.approx(
                eta_bar_from_cs_inflow(n_w), abs=1e-10
            )

    def test_even_raises(self):
        with pytest.raises(ValueError):
            aps_eta_from_kk_spectrum(6)

    def test_output_type(self):
        assert isinstance(aps_eta_from_kk_spectrum(5), float)


# ---------------------------------------------------------------------------
# triangular_number
# ---------------------------------------------------------------------------

class TestTriangularNumber:
    def test_t_1(self):
        assert triangular_number(1) == 1

    def test_t_2(self):
        assert triangular_number(2) == 3

    def test_t_3(self):
        assert triangular_number(3) == 6

    def test_t_5(self):
        assert triangular_number(5) == 15

    def test_t_7(self):
        assert triangular_number(7) == 28

    def test_t_9(self):
        assert triangular_number(9) == 45

    def test_t_11(self):
        assert triangular_number(11) == 66

    def test_t_general_formula(self):
        for n in range(1, 20):
            assert triangular_number(n) == n * (n + 1) // 2

    def test_t_5_is_odd(self):
        assert triangular_number(5) % 2 == 1

    def test_t_7_is_even(self):
        assert triangular_number(7) % 2 == 0

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            triangular_number(0)

    def test_output_type(self):
        assert isinstance(triangular_number(5), int)


# ---------------------------------------------------------------------------
# braid_crossing_parity
# ---------------------------------------------------------------------------

class TestBraidCrossingParity:
    def test_n_w_5_is_minus_one(self):
        # T(5) = 15 (odd) → parity = -1
        assert braid_crossing_parity(5) == -1

    def test_n_w_7_is_plus_one(self):
        # T(7) = 28 (even) → parity = +1
        assert braid_crossing_parity(7) == 1

    def test_n_w_1_is_minus_one(self):
        # T(1) = 1 (odd) → -1
        assert braid_crossing_parity(1) == -1

    def test_n_w_3_is_plus_one(self):
        # T(3) = 6 (even) → +1
        assert braid_crossing_parity(3) == 1

    def test_n_w_9_is_minus_one(self):
        # T(9) = 45 (odd) → -1
        assert braid_crossing_parity(9) == -1

    def test_n_w_11_is_plus_one(self):
        # T(11) = 66 (even) → +1
        assert braid_crossing_parity(11) == 1

    def test_parity_equals_minus_one_to_power_t(self):
        for n_w in [1, 3, 5, 7, 9, 11, 13, 15]:
            t = triangular_number(n_w)
            expected = (-1) ** t
            assert braid_crossing_parity(n_w) == expected

    def test_even_raises(self):
        with pytest.raises(ValueError):
            braid_crossing_parity(4)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            braid_crossing_parity(0)

    def test_output_type(self):
        assert isinstance(braid_crossing_parity(5), int)


# ---------------------------------------------------------------------------
# cs_three_form_orbifold
# ---------------------------------------------------------------------------

class TestCsThreeFormOrbifold:
    def test_n_w_5_is_half(self):
        assert cs_three_form_orbifold(5) == pytest.approx(0.5, rel=1e-10)

    def test_n_w_7_is_zero(self):
        assert cs_three_form_orbifold(7) == pytest.approx(0.0, abs=1e-14)

    def test_n_w_1_is_half(self):
        # T(1)=1, 1/2=0.5 mod 1 = 0.5
        assert cs_three_form_orbifold(1) == pytest.approx(0.5, rel=1e-10)

    def test_n_w_3_is_zero(self):
        # T(3)=6, 6/2=3.0 mod 1 = 0.0
        assert cs_three_form_orbifold(3) == pytest.approx(0.0, abs=1e-14)

    def test_n_w_9_is_half(self):
        # T(9)=45, 45/2=22.5 mod 1 = 0.5
        assert cs_three_form_orbifold(9) == pytest.approx(0.5, rel=1e-10)

    def test_n_w_11_is_zero(self):
        # T(11)=66, 66/2=33.0 mod 1 = 0.0
        assert cs_three_form_orbifold(11) == pytest.approx(0.0, abs=1e-14)

    def test_formula_T_div_2_mod_1(self):
        for n_w in [1, 3, 5, 7, 9, 11, 13, 15]:
            t = triangular_number(n_w)
            expected = (t / 2.0) % 1.0
            assert cs_three_form_orbifold(n_w) == pytest.approx(expected, abs=1e-10)

    def test_in_admissible_set(self):
        for n_w in [1, 3, 5, 7, 9, 11, 13, 15]:
            val = cs_three_form_orbifold(n_w)
            assert val in (pytest.approx(0.0, abs=1e-10), pytest.approx(0.5, rel=1e-10))

    def test_even_raises(self):
        with pytest.raises(ValueError):
            cs_three_form_orbifold(4)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            cs_three_form_orbifold(0)

    def test_output_type(self):
        assert isinstance(cs_three_form_orbifold(5), float)


# ---------------------------------------------------------------------------
# eta_bar_from_cs_inflow
# ---------------------------------------------------------------------------

class TestEtaBarFromCsInflow:
    def test_n_w_5_half(self):
        assert eta_bar_from_cs_inflow(5) == pytest.approx(0.5, rel=1e-10)

    def test_n_w_7_zero(self):
        assert eta_bar_from_cs_inflow(7) == pytest.approx(0.0, abs=1e-14)

    def test_equals_cs_three_form(self):
        for n_w in [1, 3, 5, 7, 9, 11]:
            assert eta_bar_from_cs_inflow(n_w) == pytest.approx(
                cs_three_form_orbifold(n_w), abs=1e-10
            )

    def test_output_type(self):
        assert isinstance(eta_bar_from_cs_inflow(5), float)


# ---------------------------------------------------------------------------
# zero_mode_z2_even
# ---------------------------------------------------------------------------

class TestZeroModeZ2Even:
    def test_n_w_5_true(self):
        assert zero_mode_z2_even(5) is True

    def test_n_w_7_false(self):
        assert zero_mode_z2_even(7) is False

    def test_n_w_1_true(self):
        assert zero_mode_z2_even(1) is True

    def test_n_w_3_false(self):
        assert zero_mode_z2_even(3) is False

    def test_n_w_9_true(self):
        assert zero_mode_z2_even(9) is True

    def test_n_w_11_false(self):
        assert zero_mode_z2_even(11) is False

    def test_consistent_with_parity(self):
        for n_w in [1, 3, 5, 7, 9, 11, 13, 15]:
            zm_even = zero_mode_z2_even(n_w)
            parity = braid_crossing_parity(n_w)
            # Z₂-even zero mode iff parity == -1
            assert zm_even == (parity == -1)

    def test_output_type(self):
        assert isinstance(zero_mode_z2_even(5), bool)

    def test_even_raises(self):
        with pytest.raises(ValueError):
            zero_mode_z2_even(4)


# ---------------------------------------------------------------------------
# eta_bar_consistent
# ---------------------------------------------------------------------------

class TestEtaBarConsistent:
    def test_n_w_5_consistent(self):
        assert eta_bar_consistent(5) is True

    def test_n_w_7_consistent(self):
        assert eta_bar_consistent(7) is True

    def test_n_w_1_consistent(self):
        assert eta_bar_consistent(1) is True

    def test_n_w_3_consistent(self):
        assert eta_bar_consistent(3) is True

    def test_all_odd_up_to_15_consistent(self):
        for n_w in range(1, 16, 2):
            assert eta_bar_consistent(n_w), f"n_w={n_w} not consistent"

    def test_output_type(self):
        assert isinstance(eta_bar_consistent(5), bool)


# ---------------------------------------------------------------------------
# path_integral_phase
# ---------------------------------------------------------------------------

class TestPathIntegralPhase:
    def test_n_w_5_is_i(self):
        phase = path_integral_phase(5)
        # exp(iπ × ½) = i
        assert abs(phase - 1j) == pytest.approx(0.0, abs=1e-10)

    def test_n_w_7_is_one(self):
        phase = path_integral_phase(7)
        # exp(iπ × 0) = 1
        assert abs(phase - 1.0) == pytest.approx(0.0, abs=1e-10)

    def test_n_w_5_magnitude_one(self):
        assert abs(path_integral_phase(5)) == pytest.approx(1.0, rel=1e-10)

    def test_n_w_7_magnitude_one(self):
        assert abs(path_integral_phase(7)) == pytest.approx(1.0, rel=1e-10)

    def test_n_w_1_is_i(self):
        # η̄(1) = 0.5 → phase = i
        assert abs(path_integral_phase(1) - 1j) == pytest.approx(0.0, abs=1e-10)

    def test_n_w_3_is_one(self):
        # η̄(3) = 0.0 → phase = 1
        assert abs(path_integral_phase(3) - 1.0) == pytest.approx(0.0, abs=1e-10)

    def test_phase_formula(self):
        for n_w in [1, 3, 5, 7, 9, 11]:
            eta = eta_bar_from_cs_inflow(n_w)
            expected = cmath.exp(1j * math.pi * eta)
            assert abs(path_integral_phase(n_w) - expected) == pytest.approx(0.0, abs=1e-10)

    def test_output_type(self):
        assert isinstance(path_integral_phase(5), complex)

    def test_even_raises(self):
        with pytest.raises(ValueError):
            path_integral_phase(4)


# ---------------------------------------------------------------------------
# aps_integrality_residual
# ---------------------------------------------------------------------------

class TestApsIntegralityResidual:
    def test_n_w_5_bulk_half_gives_zero(self):
        # η̄(5) = ½, bulk = ½: residual = |½ − ½| mod 1 = 0
        assert aps_integrality_residual(5, 0.5) == pytest.approx(0.0, abs=1e-10)

    def test_n_w_7_bulk_half_gives_half(self):
        # η̄(7) = 0, bulk = ½: residual = |½ − 0| mod 1 = ½
        assert aps_integrality_residual(7, 0.5) == pytest.approx(0.5, rel=1e-10)

    def test_n_w_5_bulk_zero_gives_half(self):
        # η̄(5) = ½, bulk = 0: residual = ½
        assert aps_integrality_residual(5, 0.0) == pytest.approx(0.5, rel=1e-10)

    def test_n_w_7_bulk_zero_gives_zero(self):
        # η̄(7) = 0, bulk = 0: residual = 0
        assert aps_integrality_residual(7, 0.0) == pytest.approx(0.0, abs=1e-10)

    def test_residual_nonnegative(self):
        for n_w in [1, 3, 5, 7, 9, 11]:
            assert aps_integrality_residual(n_w) >= 0.0

    def test_residual_at_most_half(self):
        for n_w in [1, 3, 5, 7, 9, 11]:
            assert aps_integrality_residual(n_w) <= 0.5 + 1e-10

    def test_output_type(self):
        assert isinstance(aps_integrality_residual(5), float)

    def test_even_raises(self):
        with pytest.raises(ValueError):
            aps_integrality_residual(4)


# ---------------------------------------------------------------------------
# sm_chirality_requires_eta_half
# ---------------------------------------------------------------------------

class TestSmChiralityRequiresEtaHalf:
    def test_n_w_5_satisfies(self):
        result = sm_chirality_requires_eta_half(5)
        assert result["satisfies_sm_chirality"] is True

    def test_n_w_7_does_not_satisfy(self):
        result = sm_chirality_requires_eta_half(7)
        assert result["satisfies_sm_chirality"] is False

    def test_n_w_5_eta_bar(self):
        assert sm_chirality_requires_eta_half(5)["eta_bar"] == pytest.approx(0.5, rel=1e-10)

    def test_n_w_7_eta_bar(self):
        assert sm_chirality_requires_eta_half(7)["eta_bar"] == pytest.approx(0.0, abs=1e-14)

    def test_returns_dict(self):
        assert isinstance(sm_chirality_requires_eta_half(5), dict)

    def test_has_n_w_key(self):
        assert "n_w" in sm_chirality_requires_eta_half(5)

    def test_has_status_key(self):
        assert "status" in sm_chirality_requires_eta_half(5)

    def test_status_mentions_physically_motivated(self):
        status = sm_chirality_requires_eta_half(5)["status"]
        assert "PHYSICALLY-MOTIVATED" in status

    def test_status_mentions_open(self):
        status = sm_chirality_requires_eta_half(5)["status"]
        assert "OPEN" in status

    def test_sm_requires_lh(self):
        assert sm_chirality_requires_eta_half(5)["sm_requires_lh_zero_mode"] is True

    def test_zero_mode_z2_even_n_w_5(self):
        assert sm_chirality_requires_eta_half(5)["zero_mode_z2_even"] is True

    def test_zero_mode_z2_even_n_w_7(self):
        assert sm_chirality_requires_eta_half(7)["zero_mode_z2_even"] is False

    def test_spin_structure_n_w_5_mentions_nontrivial(self):
        sc = sm_chirality_requires_eta_half(5)["spin_structure_class"]
        assert "non-trivial" in sc.lower()

    def test_even_raises(self):
        with pytest.raises(ValueError):
            sm_chirality_requires_eta_half(4)


# ---------------------------------------------------------------------------
# nw_uniqueness_full_aps
# ---------------------------------------------------------------------------

class TestNwUniquenessFullAps:
    def setup_method(self):
        self.result = nw_uniqueness_full_aps()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_selected_nw_is_5(self):
        assert self.result["selected_nw"] == 5

    def test_candidates_contains_5_and_7(self):
        assert 5 in self.result["candidates"]
        assert 7 in self.result["candidates"]

    def test_eta_values_key(self):
        assert "eta_values" in self.result

    def test_eta_5_is_half(self):
        assert self.result["eta_values"][5] == pytest.approx(0.5, rel=1e-10)

    def test_eta_7_is_zero(self):
        assert self.result["eta_values"][7] == pytest.approx(0.0, abs=1e-14)

    def test_honest_status(self):
        assert "DERIVED" in self.result["honest_status"]

    def test_selection_basis_mentions_aps(self):
        assert "APS" in self.result["selection_basis"]

    def test_integrality_residuals_key(self):
        assert "integrality_residuals" in self.result

    def test_n_w_5_residual_zero(self):
        assert self.result["integrality_residuals"][5] == pytest.approx(0.0, abs=1e-10)

    def test_n_w_7_residual_nonzero(self):
        assert self.result["integrality_residuals"][7] > 0.1

    def test_sm_chirality_key(self):
        assert "sm_chirality" in self.result

    def test_k_cs_key(self):
        assert "k_cs" in self.result

    def test_k_cs_value(self):
        assert self.result["k_cs"] == K_CS_CANONICAL

    def test_custom_candidates(self):
        # Only {5,7} are the Pillar-67 candidates; both have η̄ defined
        r = nw_uniqueness_full_aps([5, 7])
        assert r["selected_nw"] == 5

    def test_output_type(self):
        assert isinstance(self.result, dict)


# ---------------------------------------------------------------------------
# aps_full_derivation_chain
# ---------------------------------------------------------------------------

class TestApsFullDerivationChain:
    def setup_method(self):
        self.chain = aps_full_derivation_chain()

    def test_returns_dict(self):
        assert isinstance(self.chain, dict)

    def test_pillar_key(self):
        assert "pillar" in self.chain
        assert self.chain["pillar"] == "70-B"

    def test_name_key(self):
        assert "name" in self.chain

    def test_sharpens_key(self):
        assert "sharpens" in self.chain
        assert "70" in self.chain["sharpens"]

    def test_proof_steps_key(self):
        assert "proof_steps" in self.chain

    def test_step_1_proved(self):
        assert self.chain["proof_steps"]["step_1"]["status"] == "PROVED"

    def test_step_2_derived(self):
        assert self.chain["proof_steps"]["step_2"]["status"] == "DERIVED"

    def test_step_2_previous_schematic(self):
        assert "SCHEMATIC" in self.chain["proof_steps"]["step_2"]["previous_status"]

    def test_step_3_physically_motivated(self):
        assert self.chain["proof_steps"]["step_3"]["status"] == "PHYSICALLY-MOTIVATED"

    def test_step_3_previous_conjectured(self):
        assert "CONJECTURED" in self.chain["proof_steps"]["step_3"]["previous_status"]

    def test_hurwitz_result_in_step_2(self):
        hr = self.chain["proof_steps"]["step_2"]["hurwitz_result"]
        assert hr["eta_5"] == pytest.approx(0.5, rel=1e-10)
        assert hr["eta_7"] == pytest.approx(0.0, abs=1e-14)

    def test_cs_inflow_t5(self):
        cs = self.chain["proof_steps"]["step_2"]["cs_inflow_result"]
        assert cs["T_5"] == 15

    def test_cs_inflow_t7(self):
        cs = self.chain["proof_steps"]["step_2"]["cs_inflow_result"]
        assert cs["T_7"] == 28

    def test_cs_inflow_cs3_5(self):
        cs = self.chain["proof_steps"]["step_2"]["cs_inflow_result"]
        assert cs["CS3_5"] == pytest.approx(0.5, rel=1e-10)

    def test_cs_inflow_cs3_7(self):
        cs = self.chain["proof_steps"]["step_2"]["cs_inflow_result"]
        assert cs["CS3_7"] == pytest.approx(0.0, abs=1e-14)

    def test_consistency_n_w_5(self):
        ck = self.chain["proof_steps"]["step_2"]["consistency_check"]
        assert ck["n_w_5_consistent"] is True

    def test_consistency_n_w_7(self):
        ck = self.chain["proof_steps"]["step_2"]["consistency_check"]
        assert ck["n_w_7_consistent"] is True

    def test_honest_status_summary_key(self):
        assert "honest_status_summary" in self.chain

    def test_honest_status_proved(self):
        assert "PROVED" in self.chain["honest_status_summary"]

    def test_honest_status_derived(self):
        assert "DERIVED" in self.chain["honest_status_summary"]

    def test_honest_status_physically_motivated(self):
        assert "PHYSICALLY-MOTIVATED" in self.chain["honest_status_summary"]

    def test_honest_status_open(self):
        assert "OPEN" in self.chain["honest_status_summary"]

    def test_advancement_text_key(self):
        assert "advancement_over_pillar_70" in self.chain

    def test_advancement_mentions_step_2(self):
        assert "Step 2" in self.chain["advancement_over_pillar_70"]

    def test_advancement_mentions_step_3(self):
        assert "Step 3" in self.chain["advancement_over_pillar_70"]

    def test_boundary_conditions_key(self):
        assert "boundary_conditions" in self.chain

    def test_selection_key(self):
        assert "selection" in self.chain

    def test_selection_selected_nw(self):
        assert self.chain["selection"]["selected_nw"] == 5
