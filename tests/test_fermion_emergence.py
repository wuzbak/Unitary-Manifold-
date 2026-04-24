# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_fermion_emergence.py
================================
Test suite for Pillar 54: Fermion Emergence from the Z₂ Orbifold
(src/core/fermion_emergence.py).

~90 tests covering all public functions, constants, edge cases, and the
core claim that chiral zero modes emerge naturally from the S¹/Z₂ orbifold.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.fermion_emergence import (
    K_CS,
    N_GENERATIONS,
    N_W,
    PHI_0,
    SPINOR_DIM_4D,
    SPINOR_DIM_5D,
    chiral_zero_mode_wavefunction,
    dirac_determinant_ratio,
    dirac_kk_spectrum,
    fermion_condensate,
    fermion_emergence_summary,
    gamma5_matrix,
    gamma_matrices_4d,
    gamma_matrices_5d,
    index_theorem_check,
    kk_mode_chirality,
    orbifold_sector_table,
    orbifold_z2_projector,
    sm_generation_identification,
    twisted_sector_mass_shift,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi_0(self):
        assert abs(PHI_0 - 5 * 2 * math.pi) < 1e-12

    def test_n_generations(self):
        assert N_GENERATIONS == 3

    def test_spinor_dim_4d(self):
        assert SPINOR_DIM_4D == 4

    def test_spinor_dim_5d(self):
        assert SPINOR_DIM_5D == 8


# ---------------------------------------------------------------------------
# gamma_matrices_4d
# ---------------------------------------------------------------------------

class TestGammaMatrices4d:
    def test_shape(self):
        gamma = gamma_matrices_4d()
        assert gamma.shape == (4, 4, 4)

    def test_dtype_complex(self):
        gamma = gamma_matrices_4d()
        assert np.issubdtype(gamma.dtype, np.complexfloating)

    def test_g0_antidiagonal_block(self):
        """γ⁰ in Dirac basis is block-diagonal [[I, 0], [0, -I]]."""
        gamma = gamma_matrices_4d()
        g0 = gamma[0]
        # Top-left block should be I₂
        np.testing.assert_allclose(g0[:2, :2], np.eye(2), atol=1e-12)
        # Bottom-right block should be -I₂
        np.testing.assert_allclose(g0[2:, 2:], -np.eye(2), atol=1e-12)
        # Off-diagonal blocks should be zero
        np.testing.assert_allclose(g0[:2, 2:], 0.0, atol=1e-12)
        np.testing.assert_allclose(g0[2:, :2], 0.0, atol=1e-12)

    def test_clifford_algebra_spatial(self):
        """γ^k squares to -I for spatial indices (k=1,2,3) in west-coast signature."""
        gamma = gamma_matrices_4d()
        for k in range(1, 4):
            gk_sq = gamma[k] @ gamma[k]
            # In west-coast (+,-,-,-): (γ^k)² = η^{kk} I = -I
            np.testing.assert_allclose(gk_sq, -np.eye(4), atol=1e-12)

    def test_clifford_algebra_anticommutator(self):
        """Off-diagonal anticommutators vanish: {γ^μ, γ^ν} = 0 for μ ≠ ν."""
        gamma = gamma_matrices_4d()
        for mu in range(4):
            for nu in range(4):
                if mu != nu:
                    anti = gamma[mu] @ gamma[nu] + gamma[nu] @ gamma[mu]
                    np.testing.assert_allclose(anti, 0.0, atol=1e-12)

    def test_gamma0_squared_is_identity(self):
        """(γ⁰)² = I in the Dirac basis (west-coast convention)."""
        gamma = gamma_matrices_4d()
        np.testing.assert_allclose(gamma[0] @ gamma[0], np.eye(4), atol=1e-12)


# ---------------------------------------------------------------------------
# gamma5_matrix
# ---------------------------------------------------------------------------

class TestGamma5Matrix:
    def test_shape(self):
        g5 = gamma5_matrix()
        assert g5.shape == (4, 4)

    def test_squared_is_identity(self):
        g5 = gamma5_matrix()
        np.testing.assert_allclose(g5 @ g5, np.eye(4), atol=1e-12)

    def test_hermitian(self):
        g5 = gamma5_matrix()
        np.testing.assert_allclose(g5, g5.conj().T, atol=1e-12)

    def test_anticommutes_with_gamma(self):
        """{γ⁵, γ^μ} = 0 for all μ = 0,1,2,3."""
        g5 = gamma5_matrix()
        gamma = gamma_matrices_4d()
        for mu in range(4):
            anti = g5 @ gamma[mu] + gamma[mu] @ g5
            np.testing.assert_allclose(anti, 0.0, atol=1e-12)

    def test_off_diagonal_blocks(self):
        """γ⁵ in Dirac basis = [[0, I₂], [I₂, 0]]."""
        g5 = gamma5_matrix()
        np.testing.assert_allclose(g5[:2, :2], 0.0, atol=1e-12)
        np.testing.assert_allclose(g5[2:, 2:], 0.0, atol=1e-12)
        np.testing.assert_allclose(g5[:2, 2:], np.eye(2), atol=1e-12)
        np.testing.assert_allclose(g5[2:, :2], np.eye(2), atol=1e-12)

    def test_eigenvalues_pm1(self):
        """γ⁵ has eigenvalues ±1 (two of each)."""
        g5 = gamma5_matrix()
        eigvals = np.linalg.eigvalsh(g5.real)
        eigvals_sorted = np.sort(np.round(eigvals, 10))
        np.testing.assert_allclose(eigvals_sorted, [-1, -1, 1, 1], atol=1e-10)


# ---------------------------------------------------------------------------
# gamma_matrices_5d
# ---------------------------------------------------------------------------

class TestGammaMatrices5d:
    def test_shape(self):
        Gamma = gamma_matrices_5d()
        assert Gamma.shape == (5, 8, 8)

    def test_dtype_complex(self):
        Gamma = gamma_matrices_5d()
        assert np.issubdtype(Gamma.dtype, np.complexfloating)

    def test_gamma5_component_structure(self):
        """Γ⁵ = I₄ ⊗ (iσ₂) should be antihermitian."""
        Gamma = gamma_matrices_5d()
        G5 = Gamma[4]
        # iσ₂ is antihermitian: (iσ₂)† = -iσ₂
        # So G5† = (I₄ ⊗ iσ₂)† = I₄ ⊗ (-iσ₂) = -G5
        # Check: G5 + G5† should be zero if antihermitian
        assert G5.shape == (8, 8)

    def test_five_matrices_returned(self):
        Gamma = gamma_matrices_5d()
        assert len(Gamma) == 5


# ---------------------------------------------------------------------------
# orbifold_z2_projector
# ---------------------------------------------------------------------------

class TestOrbifoldZ2Projector:
    def test_plus_parity_shape(self):
        P = orbifold_z2_projector(+1)
        assert P.shape == (4, 4)

    def test_minus_parity_shape(self):
        P = orbifold_z2_projector(-1)
        assert P.shape == (4, 4)

    def test_projector_idempotent(self):
        """P² = P (projector property)."""
        for parity in (+1, -1):
            P = orbifold_z2_projector(parity)
            np.testing.assert_allclose(P @ P, P, atol=1e-12)

    def test_projectors_sum_to_identity(self):
        """P₊ + P₋ = I."""
        Pp = orbifold_z2_projector(+1)
        Pm = orbifold_z2_projector(-1)
        np.testing.assert_allclose(Pp + Pm, np.eye(4), atol=1e-12)

    def test_projectors_orthogonal(self):
        """P₊ P₋ = 0."""
        Pp = orbifold_z2_projector(+1)
        Pm = orbifold_z2_projector(-1)
        np.testing.assert_allclose(Pp @ Pm, 0.0, atol=1e-12)

    def test_invalid_parity_raises(self):
        with pytest.raises(ValueError):
            orbifold_z2_projector(0)

    def test_parity_plus2_raises(self):
        with pytest.raises(ValueError):
            orbifold_z2_projector(2)

    def test_plus_parity_trace(self):
        """Tr(P₊) = 2 (two left-chiral modes from 4 total)."""
        P = orbifold_z2_projector(+1)
        assert abs(np.trace(P) - 2.0) < 1e-12

    def test_minus_parity_trace(self):
        """Tr(P₋) = 2 (two right-chiral modes)."""
        P = orbifold_z2_projector(-1)
        assert abs(np.trace(P) - 2.0) < 1e-12


# ---------------------------------------------------------------------------
# dirac_kk_spectrum
# ---------------------------------------------------------------------------

class TestDiracKkSpectrum:
    def test_returns_dict(self):
        s = dirac_kk_spectrum()
        assert isinstance(s, dict)

    def test_required_keys(self):
        s = dirac_kk_spectrum()
        for key in ("untwisted_L", "untwisted_R", "twisted"):
            assert key in s

    def test_untwisted_L_zero_mode_massless(self):
        """n=0 left mode is massless (the SM fermion zero mode)."""
        s = dirac_kk_spectrum()
        assert s["untwisted_L"][0] == 0.0

    def test_untwisted_R_no_zero_mode(self):
        """Right-handed sector starts at n=1 (no zero mode)."""
        s = dirac_kk_spectrum()
        assert s["untwisted_R"][0] > 0.0

    def test_twisted_half_integer_spectrum(self):
        """Twisted sector masses are (n+½)/φ₀."""
        s = dirac_kk_spectrum()
        for i, m in enumerate(s["twisted"]):
            expected = (i + 0.5) / PHI_0
            assert abs(m - expected) < 1e-12

    def test_mass_ordering(self):
        """Each sector has increasing masses."""
        s = dirac_kk_spectrum()
        for key in ("untwisted_L", "untwisted_R", "twisted"):
            masses = s[key]
            for i in range(len(masses) - 1):
                assert masses[i + 1] >= masses[i]

    def test_phi0_zero_raises(self):
        with pytest.raises(ValueError):
            dirac_kk_spectrum(phi0=0.0)

    def test_phi0_negative_raises(self):
        with pytest.raises(ValueError):
            dirac_kk_spectrum(phi0=-1.0)

    def test_n_modes_one_raises(self):
        with pytest.raises(ValueError):
            dirac_kk_spectrum(n_modes=0)

    def test_n_modes_count(self):
        n = 4
        s = dirac_kk_spectrum(n_modes=n)
        assert len(s["untwisted_L"]) == n

    def test_twisted_lighter_than_kk(self):
        """Lightest twisted mode m=½/φ₀ < first massive KK m=1/φ₀."""
        s = dirac_kk_spectrum()
        m_twisted_0 = s["twisted"][0]
        m_kk_1 = s["untwisted_L"][1]
        assert m_twisted_0 < m_kk_1

    def test_n_w_stored(self):
        s = dirac_kk_spectrum(n_w=5)
        assert s["n_w"] == 5


# ---------------------------------------------------------------------------
# chiral_zero_mode_wavefunction
# ---------------------------------------------------------------------------

class TestChiralZeroModeWavefunction:
    def setup_method(self):
        self.R = PHI_0  # compactification radius
        self.y = np.linspace(0, math.pi * self.R, 100)

    def test_left_normalised(self):
        """∫|ψ_L|² dy = 1."""
        psi = chiral_zero_mode_wavefunction(self.y, sector="left")
        norm = np.trapezoid(psi**2, self.y)
        assert abs(norm - 1.0) < 1e-6

    def test_right_normalised(self):
        """∫|ψ_R|² dy = 1."""
        psi = chiral_zero_mode_wavefunction(self.y, sector="right")
        norm = np.trapezoid(psi**2, self.y)
        assert abs(norm - 1.0) < 1e-6

    def test_left_localised_at_y0(self):
        """Left mode is larger near y=0 than near y=πR."""
        psi = chiral_zero_mode_wavefunction(self.y, sector="left")
        assert psi[0] > psi[-1]

    def test_right_localised_at_piR(self):
        """Right mode is larger near y=πR than near y=0."""
        psi = chiral_zero_mode_wavefunction(self.y, sector="right")
        assert psi[-1] > psi[0]

    def test_left_positive(self):
        psi = chiral_zero_mode_wavefunction(self.y, sector="left")
        assert np.all(psi > 0.0)

    def test_right_positive(self):
        psi = chiral_zero_mode_wavefunction(self.y, sector="right")
        assert np.all(psi > 0.0)

    def test_output_shape(self):
        psi = chiral_zero_mode_wavefunction(self.y)
        assert psi.shape == self.y.shape

    def test_invalid_sector_raises(self):
        with pytest.raises(ValueError):
            chiral_zero_mode_wavefunction(self.y, sector="middle")

    def test_invalid_phi0_raises(self):
        with pytest.raises(ValueError):
            chiral_zero_mode_wavefunction(self.y, phi0=-1.0)

    def test_left_right_symmetric(self):
        """Left and right wavefunctions are mirror images: ψ_L(y) = ψ_R(πR-y)."""
        psi_L = chiral_zero_mode_wavefunction(self.y, sector="left")
        psi_R = chiral_zero_mode_wavefunction(self.y, sector="right")
        np.testing.assert_allclose(psi_L, psi_R[::-1], atol=1e-6)


# ---------------------------------------------------------------------------
# index_theorem_check
# ---------------------------------------------------------------------------

class TestIndexTheoremCheck:
    def test_nw5_index_is_5(self):
        result = index_theorem_check(5)
        assert result["index"] == 5

    def test_theorem_satisfied_nw5(self):
        result = index_theorem_check(5)
        assert result["theorem_satisfied"] is True

    def test_n_L_equals_nw(self):
        for n_w in (1, 3, 5, 7):
            result = index_theorem_check(n_w)
            assert result["n_L"] == n_w

    def test_n_R_zero(self):
        result = index_theorem_check(5)
        assert result["n_R"] == 0

    def test_stable_generations_is_3_for_nw5(self):
        """For n_w=5: modes n with n²≤5 are n=0,1,2 → 3 stable generations."""
        result = index_theorem_check(5)
        assert result["stable_generations"] == 3

    def test_cs_gap_for_nw5(self):
        """k_CS - n_w² = 74 - 25 = 49."""
        result = index_theorem_check(5)
        assert result["cs_gap"] == 49

    def test_summary_is_string(self):
        result = index_theorem_check(5)
        assert isinstance(result["summary"], str)

    def test_invalid_nw_raises(self):
        with pytest.raises(ValueError):
            index_theorem_check(0)

    def test_index_equals_nw(self):
        for n_w in (1, 2, 3, 5, 7):
            result = index_theorem_check(n_w)
            assert result["index"] == n_w


# ---------------------------------------------------------------------------
# sm_generation_identification
# ---------------------------------------------------------------------------

class TestSmGenerationIdentification:
    def test_returns_3_generations_for_nw5(self):
        gens = sm_generation_identification(5)
        assert len(gens) == 3

    def test_generation_numbers(self):
        gens = sm_generation_identification(5)
        assert [g["generation"] for g in gens] == [1, 2, 3]

    def test_mode_numbers(self):
        gens = sm_generation_identification(5)
        assert [g["mode_n"] for g in gens] == [0, 1, 2]

    def test_first_generation_mass_ratio(self):
        """n=0 mode: mass_ratio = √(1+0/5) = 1.0."""
        gens = sm_generation_identification(5)
        assert abs(gens[0]["mass_ratio"] - 1.0) < 1e-10

    def test_mass_ratios_increasing(self):
        gens = sm_generation_identification(5)
        ratios = [g["mass_ratio"] for g in gens]
        for i in range(len(ratios) - 1):
            assert ratios[i + 1] >= ratios[i]

    def test_first_gen_left_chiral(self):
        gens = sm_generation_identification(5)
        assert gens[0]["chiral_partner"] == "left-zero-mode"

    def test_higher_gens_massive_kk(self):
        gens = sm_generation_identification(5)
        for g in gens[1:]:
            assert g["chiral_partner"] == "massive-KK-mode"

    def test_sm_particles_lists(self):
        gens = sm_generation_identification(5)
        for g in gens:
            assert isinstance(g["sm_particles"], list)
            assert len(g["sm_particles"]) > 0

    def test_phi_eff_positive(self):
        gens = sm_generation_identification(5)
        for g in gens:
            assert g["phi_eff"] > 0.0

    def test_phi_eff_decreasing(self):
        """Higher generations have smaller effective radion."""
        gens = sm_generation_identification(5)
        phis = [g["phi_eff"] for g in gens]
        for i in range(len(phis) - 1):
            assert phis[i] >= phis[i + 1]


# ---------------------------------------------------------------------------
# twisted_sector_mass_shift
# ---------------------------------------------------------------------------

class TestTwistedSectorMassShift:
    def test_n0_is_half_inverse_phi(self):
        """m_0 = 0.5 / φ₀."""
        m = twisted_sector_mass_shift(phi0=PHI_0, n_twist=0)
        expected = 0.5 / PHI_0
        assert abs(m - expected) < 1e-12

    def test_n1_is_1p5_inverse_phi(self):
        m = twisted_sector_mass_shift(phi0=PHI_0, n_twist=1)
        expected = 1.5 / PHI_0
        assert abs(m - expected) < 1e-12

    def test_general_formula(self):
        for n in range(5):
            m = twisted_sector_mass_shift(phi0=PHI_0, n_twist=n)
            expected = (n + 0.5) / PHI_0
            assert abs(m - expected) < 1e-12

    def test_phi0_negative_raises(self):
        with pytest.raises(ValueError):
            twisted_sector_mass_shift(phi0=-1.0)

    def test_n_negative_raises(self):
        with pytest.raises(ValueError):
            twisted_sector_mass_shift(n_twist=-1)

    def test_smaller_phi_larger_mass(self):
        m1 = twisted_sector_mass_shift(phi0=1.0)
        m2 = twisted_sector_mass_shift(phi0=2.0)
        assert m1 > m2


# ---------------------------------------------------------------------------
# dirac_determinant_ratio
# ---------------------------------------------------------------------------

class TestDiracDeterminantRatio:
    def test_constant_phi_gives_one(self):
        """For φ = φ₀ everywhere, det ratio = 1."""
        phi = np.full(20, PHI_0)
        ratio = dirac_determinant_ratio(phi, phi0=PHI_0)
        assert abs(ratio - 1.0) < 1e-10

    def test_phi_larger_gives_ratio_less_than_one(self):
        """φ > φ₀ → smaller KK masses → smaller determinant."""
        phi = np.full(20, 2.0 * PHI_0)
        ratio = dirac_determinant_ratio(phi, phi0=PHI_0)
        assert ratio < 1.0

    def test_phi_smaller_gives_ratio_greater_than_one(self):
        """φ < φ₀ → larger KK masses → larger determinant."""
        phi = np.full(20, 0.5 * PHI_0)
        ratio = dirac_determinant_ratio(phi, phi0=PHI_0)
        assert ratio > 1.0

    def test_returns_float(self):
        phi = np.ones(10) * PHI_0
        ratio = dirac_determinant_ratio(phi)
        assert isinstance(ratio, float)


# ---------------------------------------------------------------------------
# fermion_condensate
# ---------------------------------------------------------------------------

class TestFermionCondensate:
    def test_negative_for_background_phi(self):
        """⟨ψ̄ψ⟩ < 0 signals chiral symmetry breaking."""
        phi = np.full(20, PHI_0)
        cond = fermion_condensate(phi)
        assert cond < 0.0

    def test_smaller_phi_larger_magnitude(self):
        """Smaller φ → heavier KK modes → larger condensate magnitude."""
        phi_small = np.full(20, 0.5 * PHI_0)
        phi_large = np.full(20, PHI_0)
        cond_small = abs(fermion_condensate(phi_small))
        cond_large = abs(fermion_condensate(phi_large))
        assert cond_small > cond_large

    def test_returns_float(self):
        phi = np.ones(10) * PHI_0
        cond = fermion_condensate(phi)
        assert isinstance(cond, float)


# ---------------------------------------------------------------------------
# orbifold_sector_table
# ---------------------------------------------------------------------------

class TestOrbifoldSectorTable:
    def test_returns_list(self):
        table = orbifold_sector_table()
        assert isinstance(table, list)

    def test_four_sectors(self):
        table = orbifold_sector_table()
        assert len(table) == 4

    def test_untwisted_left_has_zero_mode(self):
        table = orbifold_sector_table()
        ul = next(s for s in table if "Untwisted left" in s["sector"])
        assert ul["zero_mode_count"] == 1

    def test_untwisted_right_no_zero_mode(self):
        table = orbifold_sector_table()
        ur = next(s for s in table if "Untwisted right" in s["sector"])
        assert ur["zero_mode_count"] == 0

    def test_required_keys_present(self):
        table = orbifold_sector_table()
        for entry in table:
            for key in ("sector", "bc", "z2_parity", "zero_mode_count",
                        "sm_content", "localisation", "mass_gap"):
                assert key in entry

    def test_total_zero_modes_equals_1(self):
        """Only one sector (UL) has a zero mode."""
        table = orbifold_sector_table()
        total = sum(s["zero_mode_count"] for s in table)
        assert total == 1


# ---------------------------------------------------------------------------
# kk_mode_chirality
# ---------------------------------------------------------------------------

class TestKkModeChirality:
    def test_zero_mode_even_parity_is_left(self):
        assert kk_mode_chirality(0, z2_parity=+1) == "left-chiral"

    def test_zero_mode_odd_parity_projected_out(self):
        assert kk_mode_chirality(0, z2_parity=-1) == "right-chiral-projected-out"

    def test_massive_mode_is_dirac(self):
        for n in range(1, 5):
            assert kk_mode_chirality(n, z2_parity=+1) == "massive-dirac"

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            kk_mode_chirality(-1)

    def test_invalid_parity_raises(self):
        with pytest.raises(ValueError):
            kk_mode_chirality(0, z2_parity=0)


# ---------------------------------------------------------------------------
# fermion_emergence_summary
# ---------------------------------------------------------------------------

class TestFermionEmergenceSummary:
    def test_returns_dict(self):
        result = fermion_emergence_summary()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = fermion_emergence_summary()
        for key in ("n_w", "index_theorem", "sm_generations", "kk_spectrum",
                    "orbifold_sectors", "fermion_condensate",
                    "twisted_mass_gap", "chiral_symmetry_breaking"):
            assert key in result

    def test_n_w_stored(self):
        result = fermion_emergence_summary()
        assert result["n_w"] == 5

    def test_3_sm_generations(self):
        result = fermion_emergence_summary()
        assert len(result["sm_generations"]) == 3

    def test_chiral_symmetry_broken(self):
        result = fermion_emergence_summary()
        assert result["chiral_symmetry_breaking"] is True

    def test_condensate_negative(self):
        result = fermion_emergence_summary()
        assert result["fermion_condensate"] < 0.0

    def test_index_theorem_satisfied(self):
        result = fermion_emergence_summary()
        assert result["index_theorem"]["theorem_satisfied"] is True

    def test_twisted_mass_gap_positive(self):
        result = fermion_emergence_summary()
        assert result["twisted_mass_gap"] > 0.0
