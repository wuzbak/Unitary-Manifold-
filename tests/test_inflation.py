"""
tests/test_inflation.py
=======================
Unit tests for src/core/inflation.py and src/core/transfer.py.

Covers:
  inflation.py
  - gw_potential: non-negative, zero at minimum (φ = ±φ₀), λ-scaling
  - gw_potential_derivs: finite, correct limits at φ=0 and φ=φ₀
  - slow_roll_params: correct ε/η at inflection point (η = 0); ValueError for V≤0
  - spectral_index: formula nₛ = 1−6ε+2η; scale-invariant limit
  - tensor_to_scalar_ratio: r = 16ε
  - gw_spectral_index: nₜ = −2ε
  - ns_from_phi0: returns finite tuple, λ-independence of nₛ
  - planck2018_check: accepts/rejects known values

  transfer.py
  - primordial_power_spectrum: scale-invariant limit, tilt direction
  - cmb_source_function: value at k=0, Silk damping at large k
  - angular_power_spectrum: shape, positivity, nₛ-dependence (bluer → more power
    at small scales)
  - dl_from_cl: monotone in ℓ for flat Cₗ, T_cmb scaling
  - chi2_planck: correct χ² for perfect match, raises on no overlap
"""

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.inflation import (
    gw_potential,
    gw_potential_derivs,
    slow_roll_params,
    spectral_index,
    tensor_to_scalar_ratio,
    gw_spectral_index,
    ns_from_phi0,
    planck2018_check,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
)
from src.core.transfer import (
    primordial_power_spectrum,
    cmb_source_function,
    angular_power_spectrum,
    dl_from_cl,
    chi2_planck,
    PLANCK_2018_DL_REF,
    PLANCK_2018_COSMO,
)


# ===========================================================================
# inflation.py tests
# ===========================================================================

class TestGWPotential:
    def test_zero_at_minimum(self):
        """V(±φ₀) = 0 for any φ₀ and λ."""
        phi0 = 1.5
        assert gw_potential(phi0,  phi0) == pytest.approx(0.0, abs=1e-14)
        assert gw_potential(-phi0, phi0) == pytest.approx(0.0, abs=1e-14)

    def test_non_negative(self):
        """V(φ) ≥ 0 everywhere (squared potential)."""
        phi  = np.linspace(-3.0, 3.0, 200)
        vals = gw_potential(phi, phi0=1.0)
        assert np.all(vals >= 0.0)

    def test_lambda_scaling(self):
        """V scales linearly with λ."""
        phi = 0.5
        V1  = gw_potential(phi, phi0=1.0, lam=1.0)
        V2  = gw_potential(phi, phi0=1.0, lam=3.0)
        assert V2 == pytest.approx(3.0 * V1, rel=1e-12)

    def test_array_input(self):
        """Accepts ndarray input and returns ndarray of same shape."""
        phi = np.array([0.0, 0.5, 1.0, 1.5])
        result = gw_potential(phi, phi0=1.0)
        assert result.shape == phi.shape


class TestGWPotentialDerivs:
    def test_at_minimum_V_zero(self):
        """V(φ₀) = 0 and V'(φ₀) = 0."""
        phi0 = 1.2
        V, dV, _ = gw_potential_derivs(phi0, phi0)
        assert V  == pytest.approx(0.0, abs=1e-14)
        assert dV == pytest.approx(0.0, abs=1e-14)

    def test_inflection_point_d2V_zero(self):
        """V''(φ₀/√3) = 0 exactly (inflection point of GW potential)."""
        phi0    = 1.0
        phi_inf = phi0 / np.sqrt(3.0)
        _, _, d2V = gw_potential_derivs(phi_inf, phi0)
        assert d2V == pytest.approx(0.0, abs=1e-12)

    def test_finite_at_phi_zero(self):
        """V, V', V'' all finite at φ = 0 (top of the hill)."""
        phi0 = 1.0
        V, dV, d2V = gw_potential_derivs(0.0, phi0)
        assert np.isfinite(V)
        assert np.isfinite(dV)
        assert np.isfinite(d2V)
        assert dV == pytest.approx(0.0, abs=1e-14)   # V'(0) = 0 by symmetry

    def test_consistency_with_gw_potential(self):
        """gw_potential_derivs V matches gw_potential at same φ."""
        phi0, phi = 1.3, 0.7
        V_ref = gw_potential(phi, phi0)
        V_der, _, _ = gw_potential_derivs(phi, phi0)
        assert V_der == pytest.approx(float(V_ref), rel=1e-12)


class TestSlowRollParams:
    def test_inflection_point_eta_zero(self):
        """At φ★ = φ₀/√3, η = 0 by construction."""
        phi0    = 1.0
        phi_inf = phi0 / np.sqrt(3.0)
        V, dV, d2V = gw_potential_derivs(phi_inf, phi0)
        _, eta = slow_roll_params(phi_inf, V, dV, d2V)
        assert eta == pytest.approx(0.0, abs=1e-10)

    def test_epsilon_non_negative(self):
        """ε ≥ 0 everywhere (definition: ε = (V'/V)²/2)."""
        phi0 = 1.0
        for phi in [0.1, 0.3, 0.5, 0.7, 0.9]:
            V, dV, d2V = gw_potential_derivs(phi, phi0)
            eps, _ = slow_roll_params(phi, V, dV, d2V)
            assert eps >= 0.0

    def test_raises_on_non_positive_V(self):
        """ValueError raised when V ≤ 0 (not physical during inflation)."""
        with pytest.raises(ValueError, match="strictly positive"):
            slow_roll_params(1.0, V=0.0, dV=0.5, d2V=0.1)

        with pytest.raises(ValueError, match="strictly positive"):
            slow_roll_params(1.0, V=-1.0, dV=0.5, d2V=0.1)

    def test_scale_invariant_limit(self):
        """ε = 0, η = 0 gives nₛ = 1 (exactly scale-invariant)."""
        eps, eta = 0.0, 0.0
        ns = spectral_index(eps, eta)
        assert ns == pytest.approx(1.0, abs=1e-14)


class TestCMBObservables:
    def test_spectral_index_formula(self):
        """nₛ = 1 − 6ε + 2η."""
        eps, eta = 0.01, 0.02
        assert spectral_index(eps, eta) == pytest.approx(
            1.0 - 6.0 * eps + 2.0 * eta, rel=1e-12
        )

    def test_tensor_ratio(self):
        """r = 16ε."""
        eps = 0.005
        assert tensor_to_scalar_ratio(eps) == pytest.approx(16.0 * eps, rel=1e-12)

    def test_tensor_tilt(self):
        """nₜ = −2ε."""
        eps = 0.005
        assert gw_spectral_index(eps) == pytest.approx(-2.0 * eps, rel=1e-12)

    def test_consistency_relation(self):
        """Single-field consistency: r = −8 nₜ."""
        eps = 0.01
        r  = tensor_to_scalar_ratio(eps)
        nt = gw_spectral_index(eps)
        assert r == pytest.approx(-8.0 * nt, rel=1e-12)


class TestNsFromPhi0:
    def test_returns_finite_tuple(self):
        """ns_from_phi0 returns 4 finite floats."""
        ns, r, eps, eta = ns_from_phi0(phi0=1.0)
        for val in (ns, r, eps, eta):
            assert np.isfinite(val)

    def test_ns_lambda_independent(self):
        """nₛ does not depend on λ (λ cancels in ε and η)."""
        ns1, *_ = ns_from_phi0(phi0=1.0, lam=1.0)
        ns2, *_ = ns_from_phi0(phi0=1.0, lam=100.0)
        assert ns1 == pytest.approx(ns2, rel=1e-10)

    def test_ns_phi0_dependence(self):
        """Larger φ₀ → smaller ε (shallower potential near inflection point)."""
        ns1, _, eps1, _ = ns_from_phi0(phi0=1.0)
        ns2, _, eps2, _ = ns_from_phi0(phi0=2.0)
        assert eps2 < eps1   # shallower slow roll for larger φ₀

    def test_custom_phi_star(self):
        """Explicit phi_star gives same result when set to default inflection."""
        phi0   = 1.2
        phi_if = phi0 / np.sqrt(3.0)
        ns_def, *_    = ns_from_phi0(phi0=phi0)
        ns_explicit, *_ = ns_from_phi0(phi0=phi0, phi_star=phi_if)
        assert ns_def == pytest.approx(ns_explicit, rel=1e-12)


class TestPlanck2018Check:
    def test_central_value_passes_1sigma(self):
        """Central Planck value passes 1-σ check."""
        assert planck2018_check(PLANCK_NS_CENTRAL, n_sigma=1.0) is True

    def test_value_at_1sigma_boundary(self):
        """Value exactly at 1-σ boundary passes."""
        assert planck2018_check(PLANCK_NS_CENTRAL + PLANCK_NS_SIGMA) is True
        assert planck2018_check(PLANCK_NS_CENTRAL - PLANCK_NS_SIGMA) is True

    def test_outside_1sigma_fails(self):
        """Value > 1 σ away fails 1-σ check."""
        assert planck2018_check(PLANCK_NS_CENTRAL + 1.1 * PLANCK_NS_SIGMA) is False

    def test_outside_1sigma_passes_2sigma(self):
        """Value between 1 σ and 2 σ passes the 2-σ check."""
        ns_1p5sigma = PLANCK_NS_CENTRAL + 1.5 * PLANCK_NS_SIGMA
        assert planck2018_check(ns_1p5sigma, n_sigma=1.0) is False
        assert planck2018_check(ns_1p5sigma, n_sigma=2.0) is True

    def test_far_value_fails_both(self):
        """A wildly wrong value fails at any sigma level."""
        assert planck2018_check(0.5, n_sigma=10.0) is False


# ===========================================================================
# transfer.py tests
# ===========================================================================

class TestPrimordialPowerSpectrum:
    def test_scale_invariant(self):
        """For nₛ = 1, Δ²_ℛ(k) = Aₛ for all k."""
        k  = np.geomspace(1e-4, 1.0, 50)
        ns = 1.0
        As = 2.1e-9
        P  = primordial_power_spectrum(k, ns, As=As)
        assert np.allclose(P, As, rtol=1e-12)

    def test_tilt_direction_red(self):
        """Red tilt (nₛ < 1): Δ²_ℛ decreases with k at k > k_pivot."""
        k_pivot = 0.05
        k1, k2  = 0.01, 0.1   # k1 < k_pivot < k2
        ns = 0.96
        P1 = primordial_power_spectrum(k1, ns, k_pivot=k_pivot)
        P2 = primordial_power_spectrum(k2, ns, k_pivot=k_pivot)
        assert P1 > P2

    def test_tilt_direction_blue(self):
        """Blue tilt (nₛ > 1): Δ²_ℛ increases with k."""
        k_pivot = 0.05
        k1, k2  = 0.01, 0.1
        ns = 1.04
        P1 = primordial_power_spectrum(k1, ns, k_pivot=k_pivot)
        P2 = primordial_power_spectrum(k2, ns, k_pivot=k_pivot)
        assert P1 < P2

    def test_at_pivot(self):
        """Δ²_ℛ(k★) = Aₛ exactly."""
        k_pivot = 0.05
        As = 2.101e-9
        P  = primordial_power_spectrum(k_pivot, ns=0.96, As=As, k_pivot=k_pivot)
        assert P == pytest.approx(As, rel=1e-12)


class TestCMBSourceFunction:
    def test_small_k_limit(self):
        """S(k→0) → 1/3 (Sachs-Wolfe plateau)."""
        S = cmb_source_function(1e-6)
        assert S == pytest.approx(1.0 / 3.0, rel=1e-4)

    def test_silk_damping_large_k(self):
        """S(k) is strongly suppressed at k >> k_silk."""
        k_large = 10.0 * PLANCK_2018_COSMO["k_silk"]
        S = cmb_source_function(k_large)
        assert abs(S) < 1e-10

    def test_acoustic_oscillations(self):
        """S(k) oscillates: value at k=π/(2 rs_star) is near zero (first zero of cosine)."""
        rs_star = PLANCK_2018_COSMO["rs_star"]
        k_silk  = PLANCK_2018_COSMO["k_silk"]
        # First zero of cos(k rs_star) is at k rs_star = π/2 → k = π/(2 rs_star)
        k_node  = np.pi / (2.0 * rs_star)
        if k_node < 0.5 * k_silk:               # only test if not Silk-suppressed
            S = cmb_source_function(k_node, rs_star=rs_star, k_silk=k_silk)
            assert abs(S) < 0.05

    def test_output_shape(self):
        """Returns array of the same shape as input k array."""
        k = np.linspace(0.001, 0.1, 30)
        S = cmb_source_function(k)
        assert S.shape == k.shape


class TestAngularPowerSpectrum:
    def test_returns_positive_values(self):
        """Cₗ > 0 for a physical spectrum."""
        ells = [10, 100, 220]
        Cl   = angular_power_spectrum(ells, ns=0.9649, n_k=300)
        assert np.all(Cl > 0.0)

    def test_returns_finite_values(self):
        """No NaN or Inf in Cₗ."""
        ells = [2, 10, 30, 100, 220]
        Cl   = angular_power_spectrum(ells, ns=0.9649, n_k=300)
        assert np.all(np.isfinite(Cl))

    def test_output_shape(self):
        """Output length equals len(ells)."""
        ells = [10, 100, 220, 540]
        Cl   = angular_power_spectrum(ells, ns=0.9649, n_k=300)
        assert len(Cl) == len(ells)

    def test_red_tilt_suppresses_high_ell(self):
        """Redder spectrum (smaller nₛ) → less power at high ℓ relative to low ℓ."""
        ells_lo = [10]
        ells_hi = [500]
        ns_red  = 0.90
        ns_blue = 1.05
        Cl_lo_red,  = angular_power_spectrum(ells_lo, ns=ns_red,  n_k=300)
        Cl_hi_red,  = angular_power_spectrum(ells_hi, ns=ns_red,  n_k=300)
        Cl_lo_blue, = angular_power_spectrum(ells_lo, ns=ns_blue, n_k=300)
        Cl_hi_blue, = angular_power_spectrum(ells_hi, ns=ns_blue, n_k=300)
        # ratio hi/lo should be smaller for red tilt than blue tilt
        ratio_red  = Cl_hi_red  / Cl_lo_red
        ratio_blue = Cl_hi_blue / Cl_lo_blue
        assert ratio_red < ratio_blue


class TestDlFromCl:
    def test_zero_ell_zero(self):
        """ℓ = 0 → Dₗ = 0 (prefactor ℓ(ℓ+1) = 0)."""
        Dl = dl_from_cl([0], np.array([1.0e-9]))
        assert Dl[0] == pytest.approx(0.0, abs=1e-30)

    def test_positive_for_positive_Cl(self):
        """Dₗ > 0 for Cₗ > 0 and ℓ > 0."""
        ells = [10, 100, 220]
        Cl   = np.array([1e-9, 2e-9, 3e-9])
        Dl   = dl_from_cl(ells, Cl)
        assert np.all(Dl > 0.0)

    def test_T_cmb_scaling(self):
        """Dₗ ∝ T_CMB²."""
        ells = [100]
        Cl   = np.array([1e-9])
        Dl1  = dl_from_cl(ells, Cl, T_cmb_K=2.7255)
        Dl2  = dl_from_cl(ells, Cl, T_cmb_K=2.0)
        ratio = Dl1[0] / Dl2[0]
        assert ratio == pytest.approx((2.7255 / 2.0) ** 2, rel=1e-10)

    def test_order_of_magnitude(self):
        """Dₗ at ℓ=220 with Planck Aₛ should be in a physically plausible range."""
        ells = [220]
        Cl   = angular_power_spectrum(ells, ns=0.9649,
                                       As=PLANCK_2018_COSMO["As"], n_k=400)
        Dl   = dl_from_cl(ells, Cl)
        # Analytic approximation; within a factor of ~10 of ~6000 μK²
        assert 100.0 < Dl[0] < 60_000.0


class TestChi2Planck:
    def test_perfect_match_zero_chi2(self):
        """If predicted Dₗ exactly matches the reference, χ² = 0."""
        ells = np.array(sorted(PLANCK_2018_DL_REF.keys()))
        Dl   = np.array([PLANCK_2018_DL_REF[int(ell)][0] for ell in ells])
        chi2, chi2_dof, n_dof = chi2_planck(ells, Dl)
        assert chi2     == pytest.approx(0.0, abs=1e-10)
        assert chi2_dof == pytest.approx(0.0, abs=1e-10)
        assert n_dof    == len(ells)

    def test_one_sigma_deviation_contributes_one(self):
        """A prediction shifted by exactly 1 σ contributes χ² += 1."""
        ell_test = 220
        Dl_ref, sigma = PLANCK_2018_DL_REF[ell_test]
        Dl_shifted    = np.array([Dl_ref + sigma])
        chi2, _, _    = chi2_planck([ell_test], Dl_shifted)
        assert chi2 == pytest.approx(1.0, rel=1e-10)

    def test_no_overlap_raises(self):
        """ValueError when no predicted multipoles match the reference table."""
        with pytest.raises(ValueError, match="No multipoles"):
            chi2_planck([999999, 888888], np.array([1.0, 2.0]))

    def test_partial_overlap(self):
        """Only matched multipoles contribute to χ²."""
        ells = np.array([220, 99999])   # only ℓ=220 is in reference
        Dl   = np.array([PLANCK_2018_DL_REF[220][0], 1234.0])
        _, _, n_dof = chi2_planck(ells, Dl)
        assert n_dof == 1

    def test_n_dof_counts_matched(self):
        """n_dof equals the number of multipoles present in the reference table."""
        ells = np.array([10, 30, 100, 220, 540])
        Dl   = np.array([PLANCK_2018_DL_REF[ell][0] for ell in ells])
        _, _, n_dof = chi2_planck(ells, Dl)
        assert n_dof == 5
