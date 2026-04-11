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
  - jacobian_5d_4d: KK Jacobian formula, monotone in n_winding/phi0, errors
  - effective_phi0_kk: n_winding=5 recovers Planck nₛ, scaling laws
  - casimir_potential: positivity, φ⁻⁴ scaling, array input
  - casimir_effective_potential_derivs: reduces to GW at A_c=0, sign of dV
  - casimir_A_c_from_phi_min: round-trip minimum, error on phi_min≤phi0
  - ns_with_casimir: Planck-compatible nₛ at KK-Jacobian minimum

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
    jacobian_5d_4d,
    effective_phi0_kk,
    casimir_potential,
    casimir_effective_potential_derivs,
    casimir_A_c_from_phi_min,
    ns_with_casimir,
    ns_gw_at_casimir_minimum,
    jacobian_rs_orbifold,
    effective_phi0_rs,
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


# ===========================================================================
# 5D → 4D KK Jacobian tests
# ===========================================================================

class TestJacobian5d4d:
    def test_formula_n1(self):
        """J = 1 · 2π · √1 = 2π for n_winding=1, phi0_bare=1."""
        assert jacobian_5d_4d(1.0, n_winding=1) == pytest.approx(
            2.0 * np.pi, rel=1e-12
        )

    def test_formula_n5_phi1(self):
        """J = 5 · 2π for n_winding=5, phi0_bare=1 (the factor-of-32 fix)."""
        assert jacobian_5d_4d(1.0, n_winding=5) == pytest.approx(
            5.0 * 2.0 * np.pi, rel=1e-12
        )

    def test_scales_with_sqrt_phi0(self):
        """J ∝ √φ₀_bare: doubling φ₀ multiplies J by √2."""
        J1 = jacobian_5d_4d(1.0, n_winding=2)
        J4 = jacobian_5d_4d(4.0, n_winding=2)
        assert J4 == pytest.approx(2.0 * J1, rel=1e-12)

    def test_scales_linearly_with_n_winding(self):
        """J ∝ n_winding."""
        J1 = jacobian_5d_4d(1.0, n_winding=1)
        J3 = jacobian_5d_4d(1.0, n_winding=3)
        assert J3 == pytest.approx(3.0 * J1, rel=1e-12)

    def test_raises_on_non_positive_phi0(self):
        """ValueError when phi0_bare ≤ 0."""
        with pytest.raises(ValueError, match="positive"):
            jacobian_5d_4d(0.0)
        with pytest.raises(ValueError, match="positive"):
            jacobian_5d_4d(-1.0)

    def test_raises_on_zero_winding(self):
        """ValueError when n_winding < 1."""
        with pytest.raises(ValueError):
            jacobian_5d_4d(1.0, n_winding=0)


class TestEffectivePhi0KK:
    def test_n5_recovers_planck_ns(self):
        """With n_winding=5, effective φ₀ gives nₛ inside Planck 2018 1-σ."""
        phi0_eff = effective_phi0_kk(phi0_bare=1.0, n_winding=5)
        ns, *_ = ns_from_phi0(phi0=phi0_eff)
        assert planck2018_check(ns, n_sigma=1.0), (
            f"nₛ={ns:.5f} not in Planck 1-σ window after KK Jacobian correction"
        )

    def test_n5_phi_eff_approx_31(self):
        """φ₀_eff ≈ 31.42 for n_winding=5, phi0_bare=1."""
        phi0_eff = effective_phi0_kk(phi0_bare=1.0, n_winding=5)
        assert phi0_eff == pytest.approx(5.0 * 2.0 * np.pi, rel=1e-12)

    def test_bare_phi0_fails_planck(self):
        """Bare FTUM fixed point (n_winding=0 path) gives nₛ ≈ −35."""
        ns_bare, *_ = ns_from_phi0(phi0=1.0)
        assert ns_bare < -10.0, "Bare φ₀=1 should give catastrophically wrong nₛ"

    def test_larger_n_increases_phi_eff(self):
        """Higher winding number → larger effective vev → nₛ closer to 1."""
        phi4 = effective_phi0_kk(1.0, n_winding=4)
        phi5 = effective_phi0_kk(1.0, n_winding=5)
        assert phi5 > phi4

    def test_phi_eff_scales_with_phi0_bare(self):
        """φ₀_eff = J · φ₀_bare, so it grows faster than linearly in φ₀_bare."""
        p1 = effective_phi0_kk(phi0_bare=1.0, n_winding=2)
        p4 = effective_phi0_kk(phi0_bare=4.0, n_winding=2)
        # J(phi0=1) = 2*2π*√1 = 2*2π,  phi_eff(1) = J(1)*1 = p1
        # J(phi0=4) = 2*2π*√4 = 2*J(1), phi_eff(4) = J(4)*4 = 2*J(1)*4 = 8*p1
        assert p4 == pytest.approx(8.0 * p1, rel=1e-12)


# ===========================================================================
# Casimir potential tests
# ===========================================================================

class TestCasimirPotential:
    def test_positive_for_positive_A_c(self):
        """V_C = A_c/φ⁴ > 0 for A_c > 0."""
        assert casimir_potential(2.0, A_c=1.0) > 0.0

    def test_phi4_scaling(self):
        """V_C(2φ) = V_C(φ) / 16  (scales as φ⁻⁴)."""
        Vc1 = casimir_potential(1.0, A_c=5.0)
        Vc2 = casimir_potential(2.0, A_c=5.0)
        assert Vc2 == pytest.approx(Vc1 / 16.0, rel=1e-12)

    def test_A_c_scaling(self):
        """V_C ∝ A_c."""
        Vc1 = casimir_potential(3.0, A_c=1.0)
        Vc2 = casimir_potential(3.0, A_c=7.0)
        assert Vc2 == pytest.approx(7.0 * Vc1, rel=1e-12)

    def test_array_input(self):
        """Accepts ndarray and returns same shape."""
        phi = np.array([1.0, 2.0, 4.0])
        Vc  = casimir_potential(phi, A_c=1.0)
        assert Vc.shape == phi.shape


class TestCasimirEffectivePotentialDerivs:
    def test_reduces_to_gw_at_zero_A_c(self):
        """At A_c=0, V_eff = GW potential."""
        phi, phi0, lam = 0.8, 1.0, 1.0
        V_cas, dV_cas, d2V_cas = casimir_effective_potential_derivs(
            phi, phi0, lam, A_c=0.0
        )
        V_gw, dV_gw, d2V_gw = gw_potential_derivs(phi, phi0, lam)
        assert V_cas   == pytest.approx(V_gw,   rel=1e-12)
        assert dV_cas  == pytest.approx(dV_gw,  rel=1e-12)
        assert d2V_cas == pytest.approx(d2V_gw, rel=1e-12)

    def test_casimir_increases_V(self):
        """Adding A_c > 0 increases V_eff compared to bare GW."""
        phi, phi0, lam, A_c = 2.0, 1.0, 1.0, 1e4
        V_cas, _, _ = casimir_effective_potential_derivs(phi, phi0, lam, A_c)
        V_gw, _, _  = gw_potential_derivs(phi, phi0, lam)
        assert V_cas > V_gw

    def test_casimir_makes_dV_more_negative_at_small_phi(self):
        """Casimir repulsion (−4A_c/φ⁵) makes dV_eff more negative (slower roll)."""
        phi, phi0, lam = 0.5, 1.0, 1.0
        _, dV_gw, _  = gw_potential_derivs(phi, phi0, lam)
        _, dV_cas, _ = casimir_effective_potential_derivs(phi, phi0, lam, A_c=1.0)
        assert dV_cas < dV_gw

    def test_d2V_casimir_positive_correction(self):
        """20 A_c/φ⁶ > 0 term adds to d²V_eff."""
        phi, phi0, lam, A_c = 1.5, 1.0, 1.0, 1e3
        _, _, d2V_cas = casimir_effective_potential_derivs(phi, phi0, lam, A_c)
        _, _, d2V_gw  = gw_potential_derivs(phi, phi0, lam)
        assert d2V_cas > d2V_gw


class TestCasimirAcFromPhiMin:
    def test_round_trip_minimum(self):
        """dV_eff/dφ = 0 at φ_min when using the computed A_c."""
        phi_min, phi0, lam = 10.0, 1.0, 1.0
        A_c = casimir_A_c_from_phi_min(phi_min, phi0, lam)
        _, dV, _ = casimir_effective_potential_derivs(phi_min, phi0, lam, A_c)
        assert dV == pytest.approx(0.0, abs=1e-6)

    def test_positive_A_c(self):
        """A_c > 0 for any phi_min > phi0."""
        assert casimir_A_c_from_phi_min(5.0, 1.0) > 0.0

    def test_raises_when_phi_min_le_phi0(self):
        """ValueError when phi_min ≤ phi0."""
        with pytest.raises(ValueError, match="must exceed"):
            casimir_A_c_from_phi_min(1.0, 1.0)
        with pytest.raises(ValueError, match="must exceed"):
            casimir_A_c_from_phi_min(0.5, 1.0)

    def test_scales_as_phi_min_8_for_large_phi_min(self):
        """For φ_min ≫ φ₀, A_c ≈ λ φ_min⁸."""
        phi_min = 100.0
        phi0 = 1.0
        lam = 1.0
        A_c = casimir_A_c_from_phi_min(phi_min, phi0, lam)
        assert A_c == pytest.approx(lam * phi_min**8, rel=1e-3)


class TestNsWithCasimir:
    def test_casimir_at_kk_minimum_is_near_scale_invariant(self):
        """Casimir-corrected potential at φ_min/√3 gives slow-roll and nₛ ∈ (0.9, 1.0).

        The Casimir repulsion (+A_c/φ⁴) always adds a positive contribution to
        η = V_eff''/V_eff, pushing nₛ above the bare-GW prediction at the same
        field value.  The result nₛ ≈ 0.982 is in the near-scale-invariant
        regime (0.9 < nₛ < 1.0) and satisfies slow-roll (ε < 1).
        The Planck-1σ-compatible nₛ ≈ 0.9635 is obtained via the KK Jacobian
        rescaling tested in TestEffectivePhi0KK.test_n5_recovers_planck_ns.
        """
        phi0_bare = 1.0
        phi_min   = effective_phi0_kk(phi0_bare, n_winding=5)
        A_c       = casimir_A_c_from_phi_min(phi_min, phi0_bare)
        phi_star  = phi_min / np.sqrt(3.0)
        ns, r, eps, eta = ns_with_casimir(phi0_bare, A_c, phi_star=phi_star)
        # Slow-roll must hold
        assert eps < 1.0, f"ε={eps:.4f} ≥ 1: not slow-rolling"
        # Near-scale-invariant (vastly better than bare nₛ ≈ -35)
        assert 0.90 < ns < 1.05, f"nₛ={ns:.5f} outside near-scale-invariant window"

    def test_jacobian_minimum_gives_planck_ns(self):
        """Decoupled approach: Casimir locks φ_min; bare GW at φ_min/√3 passes Planck 1-σ.

        The two roles are separated:
          1. Casimir/KK Jacobian identifies φ_min ≈ 31.42 (compactification radius).
          2. Slow-roll is evaluated on the *bare* GW potential with φ₀_eff = φ_min,
             eliminating the A_c ~ 10¹² interference in d²V/V at horizon exit.
        """
        phi0_bare = 1.0
        phi_min   = effective_phi0_kk(phi0_bare, n_winding=5)
        A_c       = casimir_A_c_from_phi_min(phi_min, phi0_bare)
        ns, *_    = ns_gw_at_casimir_minimum(phi0_bare, A_c, n_winding=5)
        assert planck2018_check(ns, n_sigma=1.0), (
            f"Decoupled nₛ={ns:.5f} not within Planck 2018 1-σ"
        )

    def test_returns_four_finite_values(self):
        """ns_with_casimir returns 4 finite floats."""
        A_c = casimir_A_c_from_phi_min(10.0, 1.0)
        result = ns_with_casimir(phi0=1.0, A_c=A_c, phi_star=5.0)
        assert len(result) == 4
        for val in result:
            assert np.isfinite(val)

    def test_larger_phi_min_increases_ns(self):
        """Larger stabilisation radius → smaller ε → nₛ closer to 1."""
        for phi_min1, phi_min2 in [(5.0, 15.0), (15.0, 30.0)]:
            A1 = casimir_A_c_from_phi_min(phi_min1, 1.0)
            A2 = casimir_A_c_from_phi_min(phi_min2, 1.0)
            ns1, *_ = ns_with_casimir(1.0, A1, phi_star=phi_min1/np.sqrt(3))
            ns2, *_ = ns_with_casimir(1.0, A2, phi_star=phi_min2/np.sqrt(3))
            assert ns2 > ns1

    def test_casimir_dramatically_improves_over_bare_ftum(self):
        """Casimir nₛ ≈ 0.98 is many σ closer to Planck than bare nₛ ≈ −35."""
        ns_bare, *_ = ns_with_casimir(phi0=1.0, A_c=0.0, phi_star=1.0/np.sqrt(3))
        phi_min = effective_phi0_kk(1.0, n_winding=5)
        A_c = casimir_A_c_from_phi_min(phi_min, 1.0)
        ns_corr, *_ = ns_with_casimir(1.0, A_c, phi_star=phi_min/np.sqrt(3))
        # Corrected value is far closer to Planck central value
        assert abs(ns_corr - PLANCK_NS_CENTRAL) < abs(ns_bare - PLANCK_NS_CENTRAL)


# ===========================================================================
# S¹/Z₂ orbifold (Randall–Sundrum) Jacobian tests
# ===========================================================================

class TestJacobianRSOrbifold:
    def test_formula(self):
        """J_RS = √[(1−e^{−2πkrc})/(2k)] for arbitrary k and r_c."""
        k, r_c = 2.0, 3.0
        expected = np.sqrt((1.0 - np.exp(-2.0*np.pi*k*r_c)) / (2.0*k))
        assert jacobian_rs_orbifold(k, r_c) == pytest.approx(expected, rel=1e-12)

    def test_saturates_at_large_krc(self):
        """For kr_c ≥ 5 the exponential vanishes: J_RS → 1/√(2k)."""
        k = 1.0
        J_limit = 1.0 / np.sqrt(2.0 * k)
        for r_c in [5.0, 10.0, 12.0, 15.0]:
            assert jacobian_rs_orbifold(k, r_c) == pytest.approx(J_limit, rel=1e-10)

    def test_saturation_independent_of_krc_above_10(self):
        """J_RS is identical (to machine precision) for kr_c = 11 … 15."""
        k = 1.0
        values = [jacobian_rs_orbifold(k, float(kr_c)) for kr_c in range(11, 16)]
        assert all(v == pytest.approx(values[0], rel=1e-12) for v in values)

    def test_smaller_krc_gives_smaller_J(self):
        """J_RS increases with r_c (more volume → larger Jacobian)."""
        k = 1.0
        assert jacobian_rs_orbifold(k, 1.0) < jacobian_rs_orbifold(k, 3.0)

    def test_larger_k_gives_smaller_J(self):
        """Stronger AdS warping reduces J_RS (1/√(2k) decreases with k)."""
        r_c = 12.0
        assert jacobian_rs_orbifold(2.0, r_c) < jacobian_rs_orbifold(1.0, r_c)

    def test_raises_on_non_positive_k(self):
        """ValueError when k ≤ 0."""
        with pytest.raises(ValueError, match="curvature"):
            jacobian_rs_orbifold(0.0, 1.0)
        with pytest.raises(ValueError, match="curvature"):
            jacobian_rs_orbifold(-1.0, 1.0)

    def test_raises_on_non_positive_rc(self):
        """ValueError when r_c ≤ 0."""
        with pytest.raises(ValueError, match="radius"):
            jacobian_rs_orbifold(1.0, 0.0)


class TestEffectivePhi0RS:
    def test_n7_k1_recovers_planck_ns(self):
        """RS orbifold with n_winding=7, k=1, kr_c=12 gives nₛ inside Planck 1-σ."""
        phi0_eff = effective_phi0_rs(phi0_bare=1.0, k=1.0, r_c=12.0, n_winding=7)
        ns, *_ = ns_from_phi0(phi0=phi0_eff)
        assert planck2018_check(ns, n_sigma=1.0), (
            f"RS nₛ={ns:.5f} not in Planck 1-σ window"
        )

    def test_phi_eff_approx_31(self):
        """φ₀_eff ≈ 7·2π/√2 ≈ 31.10 for k=1, r_c=12, n_winding=7."""
        phi0_eff = effective_phi0_rs(phi0_bare=1.0, k=1.0, r_c=12.0, n_winding=7)
        expected = 7.0 * 2.0 * np.pi / np.sqrt(2.0)
        assert phi0_eff == pytest.approx(expected, rel=1e-6)

    def test_bare_phi0_fails_planck(self):
        """Bare FTUM φ₀ = 1 still gives nₛ ≈ −35 before RS correction."""
        ns_bare, *_ = ns_from_phi0(phi0=1.0)
        assert ns_bare < -10.0


class TestNsStabilityRS:
    """The geometric attractor: nₛ is an orbifold fixed point, not a tuned value."""

    def test_ns_stability_across_krc(self):
        """nₛ stays in (0.96, 0.97) for the full hierarchy-solving range kr_c ∈ [11..15].

        Because J_RS saturates to 1/√(2k) for kr_c ≥ 5, the spectral index
        is identically robust across all manifold thicknesses that solve the
        hierarchy problem — confirming nₛ ≈ 0.9628 is a geometric attractor.
        """
        k = 1.0
        for kr_c in range(11, 16):
            phi0_eff = effective_phi0_rs(phi0_bare=1.0, k=k, r_c=float(kr_c),
                                         n_winding=7)
            ns, *_ = ns_from_phi0(phi0=phi0_eff)
            assert 0.96 < ns < 0.97, (
                f"Stability broken at kr_c={kr_c}: nₛ={ns:.5f}"
            )

    def test_tensor_to_scalar_stable_across_krc(self):
        """r = 16ε is also stable across kr_c ∈ [11..15] (same φ₀_eff)."""
        k = 1.0
        r_values = []
        for kr_c in range(11, 16):
            phi0_eff = effective_phi0_rs(phi0_bare=1.0, k=k, r_c=float(kr_c),
                                         n_winding=7)
            _, r, *_ = ns_from_phi0(phi0=phi0_eff)
            r_values.append(r)
        # All r values are identical (Jacobian saturates)
        assert all(rv == pytest.approx(r_values[0], rel=1e-10) for rv in r_values)

    def test_ns_stable_means_planck_across_krc(self):
        """Every point in kr_c ∈ [11..15] individually passes Planck 1-σ."""
        k = 1.0
        for kr_c in range(11, 16):
            phi0_eff = effective_phi0_rs(phi0_bare=1.0, k=k, r_c=float(kr_c),
                                         n_winding=7)
            ns, *_ = ns_from_phi0(phi0=phi0_eff)
            assert planck2018_check(ns, n_sigma=1.0), (
                f"Planck check failed at kr_c={kr_c}: nₛ={ns:.5f}"
            )
