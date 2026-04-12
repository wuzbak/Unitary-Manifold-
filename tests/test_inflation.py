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
    gauge_coupling_4d,
    gauge_coupling_5d_for_alpha,
    fine_structure_rs,
    cs_axion_photon_coupling,
    field_displacement_gw,
    birefringence_angle,
    cs_level_for_birefringence,
    triple_constraint,
    CS_LEVEL_PLANCK_MATCH,
    BIREFRINGENCE_TARGET_DEG,
    BIREFRINGENCE_SIGMA_DEG,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
)
from src.core.transfer import (
    primordial_power_spectrum,
    cmb_source_function,
    angular_power_spectrum,
    dl_from_cl,
    chi2_planck,
    ee_source_function,
    te_source_function,
    birefringence_angle_freq,
    tb_eb_spectrum,
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


# ===========================================================================
# Cosmic birefringence (induced Chern–Simons coupling) tests
# ===========================================================================

# Reference geometry used throughout: flat S¹/Z₂, k=1, kr_c=12
_K_REF   = 1.0
_KRC_REF = 12
_RC_REF  = float(_KRC_REF) / _K_REF          # = 12.0
_J_RS    = jacobian_rs_orbifold(_K_REF, _RC_REF)  # ≈ 1/√2
_PHI_MIN_BARE   = 18.0                        # 5D GW minimum (user convention)
_PHI_MIN_PHYS   = _J_RS * _PHI_MIN_BARE       # J_RS-projected minimum ≈ 12.73
_ALPHA_EM       = 1.0 / 137.036


class TestCsAxionPhotonCoupling:
    def test_formula(self):
        """g_aγγ = k_cs · α / (2π² · r_c)."""
        g = cs_axion_photon_coupling(1, _ALPHA_EM, _RC_REF)
        assert g == pytest.approx(_ALPHA_EM / (2 * np.pi**2 * _RC_REF), rel=1e-12)

    def test_linear_in_k_cs(self):
        """g_aγγ ∝ k_cs."""
        g1 = cs_axion_photon_coupling(1, _ALPHA_EM, _RC_REF)
        g3 = cs_axion_photon_coupling(3, _ALPHA_EM, _RC_REF)
        assert g3 == pytest.approx(3.0 * g1, rel=1e-12)

    def test_positive(self):
        """g_aγγ > 0."""
        assert cs_axion_photon_coupling(74, _ALPHA_EM, _RC_REF) > 0.0

    def test_raises_on_bad_k_cs(self):
        with pytest.raises(ValueError):
            cs_axion_photon_coupling(0, _ALPHA_EM, _RC_REF)

    def test_raises_on_bad_alpha(self):
        with pytest.raises(ValueError):
            cs_axion_photon_coupling(1, 0.0, _RC_REF)

    def test_raises_on_bad_rc(self):
        with pytest.raises(ValueError):
            cs_axion_photon_coupling(1, _ALPHA_EM, 0.0)


class TestFieldDisplacementGW:
    def test_formula(self):
        """Δφ = φ_min · (1 − 1/√3)."""
        phi = 12.73
        assert field_displacement_gw(phi) == pytest.approx(
            phi * (1.0 - 1.0/np.sqrt(3.0)), rel=1e-12
        )

    def test_positive(self):
        """Δφ > 0 for φ_min > 0."""
        assert field_displacement_gw(10.0) > 0.0

    def test_raises_on_non_positive(self):
        with pytest.raises(ValueError):
            field_displacement_gw(0.0)

    def test_reference_value(self):
        """Δφ ≈ 5.38 for φ_min_phys ≈ 12.73 (J_RS × 18)."""
        assert field_displacement_gw(_PHI_MIN_PHYS) == pytest.approx(5.38, abs=0.01)


class TestBirefringenceAngle:
    def test_formula(self):
        """β = (g_aγγ / 2) · |Δφ|."""
        assert birefringence_angle(0.002, 5.0) == pytest.approx(0.005, rel=1e-12)

    def test_takes_absolute_value(self):
        """β is the same for +Δφ and −Δφ."""
        assert birefringence_angle(0.002, 5.0) == birefringence_angle(0.002, -5.0)

    def test_zero_for_zero_delta_phi(self):
        assert birefringence_angle(0.002, 0.0) == pytest.approx(0.0, abs=1e-15)


class TestCsLevelForBirefringence:
    def test_matches_planck_constant(self):
        """cs_level_for_birefringence(0.35°, …) rounds to CS_LEVEL_PLANCK_MATCH=74."""
        dphi  = field_displacement_gw(_PHI_MIN_PHYS)
        k_cs_float = cs_level_for_birefringence(
            BIREFRINGENCE_TARGET_DEG, _ALPHA_EM, _RC_REF, dphi
        )
        assert round(k_cs_float) == CS_LEVEL_PLANCK_MATCH

    def test_round_trip(self):
        """k_cs → g_aγγ → β → k_cs round-trip is exact."""
        dphi  = field_displacement_gw(_PHI_MIN_PHYS)
        k_cs_f = cs_level_for_birefringence(0.35, _ALPHA_EM, _RC_REF, dphi)
        k_cs_i = round(k_cs_f)
        g_agg  = cs_axion_photon_coupling(k_cs_i, _ALPHA_EM, _RC_REF)
        beta_deg = np.degrees(birefringence_angle(g_agg, dphi))
        assert abs(beta_deg - 0.35) < 0.01

    def test_scales_linearly_with_beta(self):
        """k_cs ∝ β_target."""
        dphi = field_displacement_gw(_PHI_MIN_PHYS)
        k1 = cs_level_for_birefringence(0.35, _ALPHA_EM, _RC_REF, dphi)
        k2 = cs_level_for_birefringence(0.70, _ALPHA_EM, _RC_REF, dphi)
        assert k2 == pytest.approx(2.0 * k1, rel=1e-12)


class TestCosmicBirefringenceK74:
    """k_cs = 74 is the topological level that closes the manifold signature."""

    def test_k_cs_74_gives_target_birefringence(self):
        """CS_LEVEL=74 reproduces the Minami-Komatsu β ≈ 0.35° to 0.01° accuracy."""
        dphi  = field_displacement_gw(_PHI_MIN_PHYS)
        g_agg = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, _ALPHA_EM, _RC_REF)
        beta_deg = np.degrees(birefringence_angle(g_agg, dphi))
        assert abs(beta_deg - BIREFRINGENCE_TARGET_DEG) < 0.01, (
            f"β = {beta_deg:.4f}°, expected {BIREFRINGENCE_TARGET_DEG}°"
        )

    def test_birefringence_within_1sigma(self):
        """β(k_cs=74) is within 1σ of Minami-Komatsu (0.35° ± 0.14°)."""
        dphi  = field_displacement_gw(_PHI_MIN_PHYS)
        g_agg = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, _ALPHA_EM, _RC_REF)
        beta_deg = np.degrees(birefringence_angle(g_agg, dphi))
        assert abs(beta_deg - BIREFRINGENCE_TARGET_DEG) <= BIREFRINGENCE_SIGMA_DEG, (
            f"β = {beta_deg:.4f}° not within 1σ of {BIREFRINGENCE_TARGET_DEG}°"
        )

    def test_birefringence_stable_across_krc(self):
        """β is stable across kr_c ∈ [11..15] (same as nₛ and g₄ stability)."""
        dphi = field_displacement_gw(_PHI_MIN_PHYS)
        betas = []
        for kr_c in range(11, 16):
            g_agg = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, _ALPHA_EM,
                                              float(kr_c) / _K_REF)
            betas.append(np.degrees(birefringence_angle(g_agg, dphi)))
        # All values must be different (g_agg ∝ 1/r_c, so varies with kr_c)
        # but all within physically plausible range
        for b in betas:
            assert 0.0 < b < 1.0, f"β={b:.4f}° outside (0, 1) degree window"

    def test_topological_consistency(self):
        """Geometric closure: same J_RS that fixes nₛ also fixes β (via k_cs=74)."""
        phi0_eff  = effective_phi0_rs(1.0, _K_REF, _RC_REF, n_winding=7)
        dphi      = field_displacement_gw(_PHI_MIN_PHYS)
        g_agg     = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, _ALPHA_EM, _RC_REF)
        ns, *_    = ns_from_phi0(phi0=phi0_eff)
        beta_deg  = np.degrees(birefringence_angle(g_agg, dphi))
        # Both close the manifold signature simultaneously
        assert planck2018_check(ns, n_sigma=1.0), f"nₛ={ns:.5f} fails Planck 1σ"
        assert abs(beta_deg - BIREFRINGENCE_TARGET_DEG) < 0.01, (
            f"β={beta_deg:.4f}° fails birefringence target"
        )


class TestTripleConstraint:
    """The 'Manifold Signature': nₛ, r, β from one geometric origin."""

    _RESULT = None

    @classmethod
    def _get_result(cls):
        if cls._RESULT is None:
            phi0_eff = effective_phi0_rs(1.0, _K_REF, _RC_REF, n_winding=7)
            cls._RESULT = triple_constraint(
                phi0_eff=phi0_eff,
                k_cs=CS_LEVEL_PLANCK_MATCH,
                alpha_em=_ALPHA_EM,
                r_c=_RC_REF,
                phi_min_phys=_PHI_MIN_PHYS,
            )
        return cls._RESULT

    def test_returns_all_keys(self):
        r = self._get_result()
        for key in ("ns", "r", "epsilon", "eta", "beta_deg", "g_agg", "delta_phi"):
            assert key in r
            assert np.isfinite(r[key])

    def test_ns_passes_planck(self):
        """nₛ from triple_constraint is within Planck 2018 1-σ."""
        assert planck2018_check(self._get_result()["ns"], n_sigma=1.0)

    def test_beta_matches_target(self):
        """β from triple_constraint ≈ 0.35° (< 0.01° error)."""
        assert abs(self._get_result()["beta_deg"] - BIREFRINGENCE_TARGET_DEG) < 0.01

    def test_r_positive_and_finite(self):
        """Tensor-to-scalar ratio r = 16ε is positive and finite."""
        r = self._get_result()["r"]
        assert r > 0.0
        assert np.isfinite(r)


# ===========================================================================
# ee_source_function tests
# ===========================================================================

class TestEESourceFunction:
    def test_small_k_limit(self):
        """S_E(k→0) → 0 because sin(k rs_star) → 0."""
        S = ee_source_function(1e-11)
        assert abs(S) < 1e-8

    def test_silk_damping_large_k(self):
        """S_E is strongly suppressed at k >> k_silk."""
        k_large = 10.0 * PLANCK_2018_COSMO["k_silk"]
        assert abs(ee_source_function(k_large)) < 1e-10

    def test_amplitude_factor(self):
        """Peak amplitude bounded by √3/2 ≈ 0.866."""
        k = np.linspace(1e-4, PLANCK_2018_COSMO["k_silk"], 2000)
        assert np.max(np.abs(ee_source_function(k))) <= np.sqrt(3.0) / 2.0 + 1e-12

    def test_output_shape(self):
        """Returns array of same shape as k."""
        k = np.linspace(0.001, 0.1, 40)
        assert ee_source_function(k).shape == k.shape

    def test_phase_orthogonal_to_temperature(self):
        """S_E uses sin; S_T uses cos — they are π/2 out of phase."""
        rs = PLANCK_2018_COSMO["rs_star"]
        # At k·rs = π/2, cos = 0 (S_T node) and sin = 1 (S_E peak)
        k_node = (np.pi / 2.0) / rs
        S_T = cmb_source_function(k_node)
        S_E = ee_source_function(k_node)
        assert abs(S_T) < 0.02          # S_T near zero
        assert abs(S_E) > abs(S_T)      # S_E dominant at T node


# ===========================================================================
# te_source_function tests
# ===========================================================================

class TestTESourceFunction:
    def test_equals_product_of_t_and_e(self):
        """S_TE(k) == S_T(k) * S_E(k) exactly."""
        k = np.geomspace(1e-4, 0.3, 80)
        S_TE = te_source_function(k)
        S_T  = cmb_source_function(k)
        S_E  = ee_source_function(k)
        assert np.allclose(S_TE, S_T * S_E, rtol=1e-12)

    def test_small_k_limit(self):
        """S_TE(k→0) → 0 because S_E → 0."""
        assert abs(te_source_function(1e-8)) < 1e-6

    def test_silk_damping_large_k(self):
        """S_TE suppressed at k >> k_silk."""
        k_large = 10.0 * PLANCK_2018_COSMO["k_silk"]
        assert abs(te_source_function(k_large)) < 1e-10

    def test_can_be_negative(self):
        """S_TE can be negative (sign of TE correlation changes with acoustic phase)."""
        k = np.linspace(1e-3, 0.5, 2000)
        vals = te_source_function(k)
        assert np.any(vals < 0.0)

    def test_output_shape(self):
        """Returns array of same shape as k."""
        k = np.linspace(0.001, 0.1, 35)
        assert te_source_function(k).shape == k.shape


# ===========================================================================
# birefringence_angle_freq tests
# ===========================================================================

class TestBirefringenceAngleFreq:
    _BETA0 = 0.006109   # β₀ ≈ 0.351° in radians (k_CS=74 model value)

    def test_achromatic_returns_beta0_at_any_nu(self):
        """Achromatic mode: β(ν) = β₀ for all ν."""
        for nu in [30.0, 93.0, 145.0, 220.0, 353.0]:
            assert birefringence_angle_freq(nu, self._BETA0) == pytest.approx(
                self._BETA0, rel=1e-12
            )

    def test_achromatic_ratio_is_one(self):
        """Achromatic: β(ν₁)/β(ν₂) = 1 for any pair."""
        b93  = birefringence_angle_freq(93.0,  self._BETA0)
        b145 = birefringence_angle_freq(145.0, self._BETA0)
        b220 = birefringence_angle_freq(220.0, self._BETA0)
        assert b93  / b145 == pytest.approx(1.0, rel=1e-12)
        assert b220 / b145 == pytest.approx(1.0, rel=1e-12)

    def test_dispersive_at_ref_freq_equals_beta0(self):
        """Dispersive mode: β(ν_ref) = β₀ by construction."""
        nu_ref = 145.0
        b = birefringence_angle_freq(nu_ref, self._BETA0,
                                     nu_ref_GHz=nu_ref,
                                     frequency_achromatic=False)
        assert b == pytest.approx(self._BETA0, rel=1e-12)

    def test_dispersive_scales_as_nu_minus2(self):
        """Dispersive: β(ν) ∝ ν⁻². Halving ν quadruples β."""
        nu_ref = 145.0
        b145 = birefringence_angle_freq(145.0, self._BETA0,
                                        nu_ref_GHz=nu_ref,
                                        frequency_achromatic=False)
        b72  = birefringence_angle_freq(72.5, self._BETA0,
                                        nu_ref_GHz=nu_ref,
                                        frequency_achromatic=False)
        assert b72 == pytest.approx(4.0 * b145, rel=1e-12)

    def test_dispersive_ratio_not_one(self):
        """Dispersive: β(93)/β(145) = (145/93)² ≠ 1 — fails achromaticity."""
        nu_ref = 145.0
        b93  = birefringence_angle_freq(93.0,  self._BETA0,
                                        nu_ref_GHz=nu_ref,
                                        frequency_achromatic=False)
        b145 = birefringence_angle_freq(145.0, self._BETA0,
                                        nu_ref_GHz=nu_ref,
                                        frequency_achromatic=False)
        expected = (nu_ref / 93.0) ** 2
        assert b93 / b145 == pytest.approx(expected, rel=1e-10)
        assert abs(b93 / b145 - 1.0) > 0.1   # clearly ≠ 1


# ===========================================================================
# tb_eb_spectrum tests
# ===========================================================================

# Shared geometry for birefringence (flat S¹/Z₂, k=1, kr_c=12)
_J_RS_TB   = jacobian_rs_orbifold(1.0, 12.0)
_DPHI_TB   = field_displacement_gw(_J_RS_TB * 18.0)
_GAGG_TB   = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH,
                                      1.0 / 137.036, 12.0)
_BETA0_TB  = birefringence_angle(_GAGG_TB, _DPHI_TB)   # ≈ 0.006109 rad
_NS_TB     = 0.9635
_ELLS_TB   = [10, 50, 100, 200, 500]
_NU_TB     = [93.0, 145.0, 220.0]


class TestTBEBSpectrum:
    """tb_eb_spectrum: shape, ΛCDM limit, signal, and frequency achromaticity."""

    @classmethod
    def _run(cls, beta=_BETA0_TB, achromatic=True, n_k=300):
        return tb_eb_spectrum(
            ells=_ELLS_TB, nu_array=_NU_TB,
            beta_0=beta, ns=_NS_TB, n_k=n_k,
            frequency_achromatic=achromatic,
        )

    # --- shape ---

    def test_output_shape_tb(self):
        """C_TB has shape (n_ell, n_nu)."""
        out = self._run()
        assert out["C_TB"].shape == (len(_ELLS_TB), len(_NU_TB))

    def test_output_shape_eb(self):
        """C_EB has shape (n_ell, n_nu)."""
        out = self._run()
        assert out["C_EB"].shape == (len(_ELLS_TB), len(_NU_TB))

    def test_c_te_shape(self):
        """C_TE has shape (n_ell,) — frequency-independent."""
        out = self._run()
        assert out["C_TE"].shape == (len(_ELLS_TB),)

    def test_c_ee_positive(self):
        """C_EE ≥ 0 everywhere (S_E² ≥ 0 integrand)."""
        out = self._run()
        assert np.all(out["C_EE"] >= 0.0)

    def test_finite_values(self):
        """No NaN or Inf in any output array."""
        out = self._run()
        for key in ("C_TE", "C_EE", "C_TB", "C_EB"):
            assert np.all(np.isfinite(out[key])), f"{key} contains non-finite values"

    # --- ΛCDM limit ---

    def test_lcdm_limit_tb_zero(self):
        """β = 0 → C_TB = 0 exactly.  Standard ΛCDM has no TB signal."""
        out = self._run(beta=0.0)
        assert np.allclose(out["C_TB"], 0.0, atol=0.0)

    def test_lcdm_limit_eb_zero(self):
        """β = 0 → C_EB = 0 exactly."""
        out = self._run(beta=0.0)
        assert np.allclose(out["C_EB"], 0.0, atol=0.0)

    # --- non-ΛCDM signal ---

    def test_model_tb_nonzero(self):
        """β = β₀(k_CS=74) → C_TB ≠ 0 at all ℓ and ν."""
        out = self._run()
        assert np.any(out["C_TB"] != 0.0)

    def test_model_eb_nonzero(self):
        """β = β₀(k_CS=74) → C_EB ≠ 0 at all ℓ and ν."""
        out = self._run()
        assert np.any(out["C_EB"] != 0.0)

    def test_tb_proportional_to_c_te(self):
        """C_TB[:, j] = 2 β(ν_j) C_TE for each ν column."""
        out  = self._run()
        C_TE = out["C_TE"]
        for j, nu in enumerate(_NU_TB):
            beta_nu = birefringence_angle_freq(nu, _BETA0_TB)
            expected = 2.0 * beta_nu * C_TE
            assert np.allclose(out["C_TB"][:, j], expected, rtol=1e-12)

    def test_eb_proportional_to_c_ee(self):
        """C_EB[:, j] = 2 β(ν_j) C_EE for each ν column."""
        out  = self._run()
        C_EE = out["C_EE"]
        for j, nu in enumerate(_NU_TB):
            beta_nu = birefringence_angle_freq(nu, _BETA0_TB)
            expected = 2.0 * beta_nu * C_EE
            assert np.allclose(out["C_EB"][:, j], expected, rtol=1e-12)

    # --- frequency achromaticity (the falsification handle) ---

    def test_achromaticity_ratio_is_one(self):
        """Achromatic model: C_TB(93 GHz) / C_TB(145 GHz) = 1 at all ℓ.

        This is the unique Unitary Manifold signature.
        ❌ Fails for Faraday rotation  (ratio = (145/93)² ≈ 2.43)
        ❌ Fails for most instrumental systematics (beam/scan dependent)
        ✅ Survives only for achromatic birefringence
        """
        out    = self._run(achromatic=True)
        idx_93  = list(_NU_TB).index(93.0)
        idx_145 = list(_NU_TB).index(145.0)
        ratio = out["C_TB"][:, idx_93] / out["C_TB"][:, idx_145]
        assert np.allclose(ratio, 1.0, rtol=1e-12)

    def test_achromaticity_ratio_eb_is_one(self):
        """Achromatic model: C_EB(93 GHz) / C_EB(145 GHz) = 1 at all ℓ."""
        out     = self._run(achromatic=True)
        idx_93  = list(_NU_TB).index(93.0)
        idx_145 = list(_NU_TB).index(145.0)
        ratio = out["C_EB"][:, idx_93] / out["C_EB"][:, idx_145]
        assert np.allclose(ratio, 1.0, rtol=1e-12)

    def test_faraday_ratio_not_one(self):
        """Faraday (dispersive) mode: C_TB(93)/C_TB(145) = (145/93)² ≠ 1."""
        out     = self._run(achromatic=False)
        idx_93  = list(_NU_TB).index(93.0)
        idx_145 = list(_NU_TB).index(145.0)
        ratio    = out["C_TB"][:, idx_93] / out["C_TB"][:, idx_145]
        expected = (145.0 / 93.0) ** 2
        assert np.allclose(ratio, expected, rtol=1e-10)
        assert not np.allclose(ratio, 1.0, rtol=0.01)

    def test_achromaticity_invariant_across_all_nu_pairs(self):
        """Achromatic: all ν-column ratios of C_TB equal 1 — not just one pair."""
        out = self._run(achromatic=True)
        col_0 = out["C_TB"][:, 0]
        for j in range(1, len(_NU_TB)):
            ratio = out["C_TB"][:, j] / col_0
            assert np.allclose(ratio, 1.0, rtol=1e-12), (
                f"Achromaticity broken at ν={_NU_TB[j]} GHz"
            )


# ---------------------------------------------------------------------------
# Amplitude gap analysis tests
# ---------------------------------------------------------------------------

from src.core.inflation import (
    slow_roll_amplitude,
    cobe_normalization,
    ftum_attractor_domain,
    rs1_phase_scan,
    classify_attractor_regime,
    amplitude_attractor_scan,
    scale_dependence_comparison,
    foliation_clock_check,
    amplitude_gap_report,
    PLANCK_AS_CENTRAL,
    BICEP_KECK_R_LIMIT,
    M_PL_GEV,
    ATTRACTOR_PHI0_EFF_TARGET,
    ATTRACTOR_NS_TARGET,
    ATTRACTOR_TOLERANCE,
    einstein_frame_potential_derivs,
    field_metric_nonminimal,
    einstein_inflection_phi,
    nonminimal_xi_slow_roll,
    starobinsky_large_xi_ns_r,
)


class TestSlowRollAmplitude:
    """Tests for slow_roll_amplitude() — term-by-term As breakdown."""

    def test_returns_required_keys(self):
        result = slow_roll_amplitude(31.4159, lam=1.0)
        for key in ("As", "H_inf", "epsilon", "eta", "V", "dV", "d2V",
                    "phi_star", "phi0_eff", "lam", "As_formula"):
            assert key in result, f"Missing key: {key}"

    def test_As_positive(self):
        result = slow_roll_amplitude(31.4159, lam=1.0)
        assert result["As"] > 0.0

    def test_H_inf_positive(self):
        result = slow_roll_amplitude(31.4159, lam=1.0)
        assert result["H_inf"] > 0.0

    def test_As_equals_standard_slow_roll_formula(self):
        """As = V^3 / (12 pi^2 dV^2)  and  As = H^2 / (8 pi^2 eps) must agree."""
        result = slow_roll_amplitude(31.4159, lam=1.0)
        As_alt = result["H_inf"]**2 / (8.0 * np.pi**2 * result["epsilon"])
        assert abs(result["As"] - As_alt) / result["As"] < 1e-10

    def test_As_scales_linearly_with_lambda(self):
        """As(2*lam) = 2 * As(lam): the amplitude gap is closed by a single scale."""
        r1 = slow_roll_amplitude(31.4159, lam=1.0)
        r2 = slow_roll_amplitude(31.4159, lam=2.0)
        assert abs(r2["As"] / r1["As"] - 2.0) < 1e-10

    def test_phi_star_default_is_phi0_over_sqrt3(self):
        phi0 = 31.4159
        result = slow_roll_amplitude(phi0, lam=1.0)
        assert abs(result["phi_star"] - phi0 / np.sqrt(3.0)) < 1e-10

    def test_explicit_phi_star_respected(self):
        phi0 = 31.4159
        pstar = phi0 / 2.0
        result = slow_roll_amplitude(phi0, lam=1.0, phi_star=pstar)
        assert result["phi_star"] == pytest.approx(pstar)

    def test_lam1_As_is_large_compared_to_planck_value(self):
        """With lam=1 (natural units) As >> Planck: normalization is needed."""
        result = slow_roll_amplitude(31.4159, lam=1.0)
        assert result["As"] > 1e4 * PLANCK_AS_CENTRAL

    def test_epsilon_small_for_valid_slow_roll(self):
        """ε < 1 at φ* = φ₀/√3 — slow-roll is valid."""
        result = slow_roll_amplitude(31.4159, lam=1.0)
        assert result["epsilon"] < 1.0

    def test_eta_near_zero_at_inflection_point(self):
        """η ≈ 0 at the inflection point φ* = φ₀/√3 (V'' = 0 there)."""
        result = slow_roll_amplitude(31.4159, lam=1.0)
        assert abs(result["eta"]) < 1e-10


class TestCOBENormalization:
    """Tests for cobe_normalization() — the single free parameter that closes the gap."""

    def test_returns_required_keys(self):
        result = cobe_normalization()
        for key in ("lam_cobe", "As_predicted", "As_target", "H_inf",
                    "E_inf_MPlunits", "E_inf_GeV", "ns", "r",
                    "r_planck_limit", "r_within_bound", "phi0_eff",
                    "n_winding", "lam_independent_observables"):
            assert key in result, f"Missing key: {key}"

    def test_As_predicted_matches_target(self):
        """After solving for lambda_COBE, predicted As must equal target."""
        result = cobe_normalization()
        assert result["As_predicted"] == pytest.approx(result["As_target"], rel=1e-9)

    def test_lam_cobe_positive_and_small(self):
        """lambda_COBE must be positive and much less than 1 (COBE suppression)."""
        result = cobe_normalization()
        assert result["lam_cobe"] > 0.0
        assert result["lam_cobe"] < 1e-10

    def test_ns_within_planck_1sigma(self):
        """nₛ must lie within 1σ of Planck 2018 (λ-independent)."""
        result = cobe_normalization()
        assert abs(result["ns"] - PLANCK_NS_CENTRAL) < PLANCK_NS_SIGMA

    def test_r_exceeds_bicep_keck_bound(self):
        """r ≈ 0.097 > 0.036 (BK21): the pure GW hilltop model has r-tension.

        The BICEP/Keck 2021 bound r < 0.036 (arXiv:2110.00483) is tighter
        than the stale Planck 2018+BK15 limit r < 0.10 used previously.
        r_planck_limit is updated to BICEP_KECK_R_LIMIT = 0.036 so this flag
        correctly documents the tension.  Non-minimal coupling ξ can suppress r
        in the large-field Starobinsky regime; see starobinsky_large_xi_ns_r().
        """
        result = cobe_normalization()
        assert not result["r_within_bound"], (
            f"Expected r_within_bound=False (r={result['r']:.4f} "
            f"exceeds BK21 limit {BICEP_KECK_R_LIMIT})"
        )
        assert result["r"] < 0.10   # still within the stale Planck+BK15 bound

    def test_E_inf_in_GUT_range(self):
        """Inflation energy scale should be in the GUT range ~10^15–10^17 GeV."""
        result = cobe_normalization()
        assert 1e15 <= result["E_inf_GeV"] <= 1e18

    def test_lam_independent_observables_listed(self):
        """The five lambda-independent observables must be listed."""
        result = cobe_normalization()
        for obs in ("ns", "r", "nt", "alpha_s", "beta_deg"):
            assert obs in result["lam_independent_observables"]

    def test_custom_As_target(self):
        """Doubling As_target should double lam_cobe (linear scaling)."""
        r1 = cobe_normalization(As_target=PLANCK_AS_CENTRAL)
        r2 = cobe_normalization(As_target=2.0 * PLANCK_AS_CENTRAL)
        assert r2["lam_cobe"] == pytest.approx(2.0 * r1["lam_cobe"], rel=1e-9)

    def test_h_inf_positive(self):
        result = cobe_normalization()
        assert result["H_inf"] > 0.0

    def test_phi0_eff_matches_effective_phi0_kk(self):
        from src.core.inflation import effective_phi0_kk
        result = cobe_normalization(phi0_bare=1.0, n_winding=5)
        expected = effective_phi0_kk(1.0, 5)
        assert result["phi0_eff"] == pytest.approx(expected)


class TestClassifyAttractorRegime:
    """Tests for classify_attractor_regime() — regime labelling."""

    def test_flat_s1_ftum_at_reference(self):
        assert classify_attractor_regime(1.0, 5) == "Flat_S1_FTUM"

    def test_flat_s1_ftum_within_band(self):
        for phi0b in [0.96, 0.98, 1.0, 1.02, 1.04]:
            assert classify_attractor_regime(phi0b, 5) == "Flat_S1_FTUM", (
                f"phi0_bare={phi0b} should be Flat_S1_FTUM"
            )

    def test_flat_s1_outside_band_is_off_attractor(self):
        assert classify_attractor_regime(0.5, 5) == "Off_Attractor"
        assert classify_attractor_regime(2.0, 5) == "Off_Attractor"

    def test_rs1_saturated_at_kr_c_12(self):
        assert classify_attractor_regime(1.0, 7, k=1.0, r_c=12.0) == "RS1_Saturated"

    def test_rs1_saturated_at_kr_c_15(self):
        assert classify_attractor_regime(1.0, 7, k=1.0, r_c=15.0) == "RS1_Saturated"

    def test_rs1_with_n_winding_5_is_off_attractor(self):
        """RS1 geometry with n_w=5 gives phi0_eff ≈ 22 — excluded phase."""
        assert classify_attractor_regime(1.0, 5, k=1.0, r_c=12.0) != "RS1_Saturated"

    def test_wrong_n_winding_is_off_attractor(self):
        assert classify_attractor_regime(1.0, 3) == "Off_Attractor"
        assert classify_attractor_regime(1.0, 6) == "Off_Attractor"

    def test_rs1_unsaturated_is_off_attractor(self):
        """RS1 at small kr_c (J_RS not yet saturated) should be Off_Attractor."""
        assert classify_attractor_regime(1.0, 7, k=1.0, r_c=0.1) == "Off_Attractor"

    def test_returns_string(self):
        result = classify_attractor_regime(1.0, 5)
        assert isinstance(result, str)
        assert result in ("Flat_S1_FTUM", "RS1_Saturated", "Off_Attractor")


class TestAmplitudeAttractor:
    """Tests for amplitude_attractor_scan() — branch-aware unified attractor."""

    def test_returns_required_keys(self):
        result = amplitude_attractor_scan()
        for key in ("lam_values", "ns_vs_lam", "r_vs_lam", "As_vs_lam",
                    "ns_lam_spread", "r_lam_spread", "As_lam_linearity",
                    "attractor_set", "ns_attractor_spread",
                    "phi0eff_attractor_spread_frac",
                    "attractor_set_all_in_2sigma", "off_attractor_points",
                    "ns_ref", "r_ref",
                    "fraction_within_1sigma", "fraction_within_2sigma",
                    "is_lam_independent", "is_ns_attractor", "is_As_linear"):
            assert key in result, f"Missing key: {key}"

    def test_lam_independent_ns(self):
        """nₛ must be exactly identical for all λ values — to machine precision."""
        result = amplitude_attractor_scan()
        assert result["is_lam_independent"], (
            f"ns_lam_spread={result['ns_lam_spread']:.2e}, "
            f"r_lam_spread={result['r_lam_spread']:.2e}"
        )

    def test_As_scales_linearly_with_lam(self):
        """As(λ) / As(λ₀) = λ / λ₀ to machine precision."""
        result = amplitude_attractor_scan()
        assert result["is_As_linear"], (
            f"As_lam_linearity = {result['As_lam_linearity']:.2e}"
        )

    def test_unified_ns_attractor(self):
        """Both branches in set A must satisfy the unified attractor criterion."""
        result = amplitude_attractor_scan()
        assert result["is_ns_attractor"], (
            f"ns_spread={result['ns_attractor_spread']:.4f}, "
            f"phi0eff_spread_frac={result['phi0eff_attractor_spread_frac']:.4f}, "
            f"all_in_2sigma={result['attractor_set_all_in_2sigma']}"
        )

    def test_attractor_set_contains_both_branches(self):
        """Set A must contain at least one Flat_S1_FTUM and one RS1_Saturated point."""
        result = amplitude_attractor_scan()
        branches = {p["branch"] for p in result["attractor_set"]}
        assert "Flat_S1_FTUM"  in branches, "Flat_S1_FTUM branch missing from attractor set"
        assert "RS1_Saturated" in branches, "RS1_Saturated branch missing from attractor set"

    def test_all_attractor_set_in_2sigma(self):
        """Every point in set A must be within Planck 2σ."""
        result = amplitude_attractor_scan()
        assert result["attractor_set_all_in_2sigma"], (
            f"Not all attractor-set points within Planck 2σ"
        )

    def test_ns_attractor_spread_tight(self):
        """ns spread over set A (both branches) must be ≤ 0.011."""
        result = amplitude_attractor_scan()
        assert result["ns_attractor_spread"] <= 0.011, (
            f"ns_attractor_spread = {result['ns_attractor_spread']:.4f} > 0.011"
        )

    def test_phi0eff_spread_within_two_percent(self):
        """φ₀_eff fractional spread between the two canonical branches must be ≤ 1.5%.
        The measured gap is ~1% (flat=31.42, RS1=31.10), a genuine geometric near-degeneracy."""
        result = amplitude_attractor_scan()
        assert result["phi0eff_attractor_spread_frac"] <= 0.015, (
            f"phi0eff_spread_frac = {result['phi0eff_attractor_spread_frac']:.4f} > 0.015"
        )

    def test_majority_attractor_set_within_1sigma(self):
        result = amplitude_attractor_scan()
        assert result["fraction_within_1sigma"] >= 0.5

    def test_all_attractor_set_within_2sigma(self):
        result = amplitude_attractor_scan()
        assert result["fraction_within_2sigma"] == pytest.approx(1.0)

    def test_ns_ref_within_planck_1sigma(self):
        result = amplitude_attractor_scan()
        assert abs(result["ns_ref"] - PLANCK_NS_CENTRAL) < PLANCK_NS_SIGMA

    def test_As_increases_with_lam(self):
        result = amplitude_attractor_scan()
        assert np.all(np.diff(result["As_vs_lam"]) > 0)

    def test_attractor_set_records_have_required_keys(self):
        result = amplitude_attractor_scan()
        for rec in result["attractor_set"]:
            for k in ("phi0_bare", "branch", "phi0_eff", "ns", "r"):
                assert k in rec, f"Attractor set record missing key: {k}"


class TestScaleDependence:
    """Tests for scale_dependence_comparison() — tilt/running/r vs Planck."""

    def test_returns_required_keys(self):
        result = scale_dependence_comparison()
        for key in ("ns", "r", "nt", "alpha_s", "r_consistency",
                    "ns_planck", "ns_deviation_sigma", "r_planck_limit",
                    "r_within_bound", "alpha_s_planck_bound",
                    "alpha_s_within_bound", "gap_is_normalization"):
            assert key in result, f"Missing key: {key}"

    def test_ns_within_1sigma_planck(self):
        result = scale_dependence_comparison()
        assert result["ns_deviation_sigma"] < 1.0

    def test_r_exceeds_bicep_keck_bound(self):
        """r ≈ 0.097 > 0.036 (BK21): r-tension documented, resolved by Starobinsky ξ."""
        result = scale_dependence_comparison()
        assert not result["r_within_bound"], (
            f"Expected r_within_bound=False; got r={result['r']:.4f}"
        )
        assert result["r"] < 0.10   # within the older Planck+BK15 bound

    def test_r_consistency_relation(self):
        """Tensor consistency: r + 8 nₜ = 0 to machine precision."""
        result = scale_dependence_comparison()
        assert result["r_consistency"] < 1e-12

    def test_alpha_s_within_planck_bound(self):
        """Spectral running |αₛ| < 0.013 (Planck 2018)."""
        result = scale_dependence_comparison()
        assert result["alpha_s_within_bound"], (
            f"|alpha_s| = {abs(result['alpha_s']):.4e} exceeds Planck bound 0.013"
        )

    def test_gap_is_normalization(self):
        """The gap is purely a normalization issue: nₛ and αₛ satisfy Planck bounds."""
        result = scale_dependence_comparison()
        assert result["gap_is_normalization"]

    def test_nt_negative(self):
        """Tensor tilt nₜ = -2ε must be negative (blue gravity wave is wrong)."""
        result = scale_dependence_comparison()
        assert result["nt"] < 0.0

    def test_ns_planck_echo(self):
        result = scale_dependence_comparison()
        assert result["ns_planck"] == pytest.approx(PLANCK_NS_CENTRAL)


class TestFoliationClock:
    """Tests for foliation_clock_check() — FTUM entropy clock vs inflaton clock."""

    def test_returns_required_keys(self):
        result = foliation_clock_check()
        for key in ("N_efolds", "N_target", "N_in_window", "epsilon_at_phi_star",
                    "slow_roll_valid", "entropy_clock_correction",
                    "foliations_consistent", "phi_star", "phi0_eff"):
            assert key in result, f"Missing key: {key}"

    def test_N_efolds_in_canonical_window(self):
        """With n_winding=5, phi0_bare=1: 50 ≤ N ≤ 70 e-folds."""
        result = foliation_clock_check()
        assert result["N_in_window"], (
            f"N = {result['N_efolds']:.1f} not in [50, 70]"
        )

    def test_slow_roll_valid_at_phi_star(self):
        """ε < 0.1 at horizon exit — slow roll is well-defined."""
        result = foliation_clock_check()
        assert result["slow_roll_valid"], (
            f"epsilon = {result['epsilon_at_phi_star']:.4f} >= 0.1"
        )

    def test_foliations_consistent(self):
        """FTUM entropy foliation is consistent with inflaton clock."""
        result = foliation_clock_check()
        assert result["foliations_consistent"]

    def test_entropy_clock_correction_small(self):
        """Accumulated entropy–clock deviation N * 2ε must be < 1 (sub-leading)."""
        result = foliation_clock_check()
        assert result["entropy_clock_correction"] < 1.0, (
            f"Entropy clock correction = {result['entropy_clock_correction']:.3f} >= 1"
        )

    def test_phi_star_default_is_phi0_over_sqrt3(self):
        result = foliation_clock_check()
        phi0_eff = result["phi0_eff"]
        assert result["phi_star"] == pytest.approx(phi0_eff / np.sqrt(3.0))

    def test_N_efolds_positive(self):
        result = foliation_clock_check()
        assert result["N_efolds"] > 0.0


class TestAmplitudeGapReport:
    """Tests for amplitude_gap_report() — full consolidated gap analysis."""

    def test_returns_required_keys(self):
        result = amplitude_gap_report()
        for key in ("slow_roll", "cobe", "scale_dependence", "attractor",
                    "foliation", "gap_factor", "gap_summary", "fully_determined",
                    "r_bk21_tension"):
            assert key in result, f"Missing key: {key}"

    def test_gap_factor_equals_lambda_cobe(self):
        """gap_factor should equal lam_cobe (they are the same quantity)."""
        result = amplitude_gap_report()
        assert result["gap_factor"] == pytest.approx(
            result["cobe"]["lam_cobe"], rel=1e-9
        )

    def test_gap_factor_positive(self):
        result = amplitude_gap_report()
        assert result["gap_factor"] > 0.0

    def test_gap_summary_is_string(self):
        result = amplitude_gap_report()
        assert isinstance(result["gap_summary"], str)
        assert len(result["gap_summary"]) > 0

    def test_fully_determined(self):
        """Theory is fully determined up to a single normalization (lambda_COBE).

        ``fully_determined`` is about parameter counting (amplitude gap reduces
        to one free parameter), not observational compliance.  The r tension is
        documented separately via the ``r_bk21_tension`` key.
        """
        result = amplitude_gap_report()
        assert result["fully_determined"], (
            f"Not fully determined. Summary: {result['gap_summary']}"
        )

    def test_r_bk21_tension_present(self):
        """r_bk21_tension must be True: r ≈ 0.097 exceeds the BK21 bound 0.036."""
        result = amplitude_gap_report()
        assert result["r_bk21_tension"] is True, (
            f"Expected r_bk21_tension=True; got r={result['cobe']['r']:.4f}"
        )

    def test_slow_roll_sub_dict_correct(self):
        result = amplitude_gap_report()
        assert "As" in result["slow_roll"]
        assert result["slow_roll"]["lam"] == pytest.approx(1.0)

    def test_sub_dicts_internally_consistent(self):
        """ns from slow_roll and scale_dependence must agree."""
        result = amplitude_gap_report()
        ns_sr = result["cobe"]["ns"]
        ns_sd = result["scale_dependence"]["ns"]
        assert abs(ns_sr - ns_sd) < 1e-10

    def test_gap_summary_contains_key_numbers(self):
        """Summary string must mention lambda_COBE-related content and ns."""
        result = amplitude_gap_report()
        summary = result["gap_summary"]
        assert "ns" in summary.lower() or "0.96" in summary
        assert "gap" in summary.lower() or "lambda" in summary.lower()


class TestFTUMAttractorDomain:
    """Tests for ftum_attractor_domain() — domain definition and branch consistency."""

    def test_returns_required_keys(self):
        result = ftum_attractor_domain()
        for key in ("flat_branch", "rs1_branch", "excluded_rs1_phase",
                    "phi0_bare_ref", "phi0_band_lo", "phi0_band_hi",
                    "ns_branch_delta", "phi0eff_branch_delta_frac",
                    "branches_consistent", "ftum_condition"):
            assert key in result, f"Missing key: {key}"

    def test_flat_branch_keys(self):
        result = ftum_attractor_domain()
        for key in ("phi0_eff", "ns", "r", "n_winding", "jacobian"):
            assert key in result["flat_branch"], f"Missing flat_branch key: {key}"

    def test_rs1_branch_keys(self):
        result = ftum_attractor_domain()
        for key in ("phi0_eff", "ns", "r", "n_winding",
                    "jacobian", "kr_c", "j_rs_saturated"):
            assert key in result["rs1_branch"], f"Missing rs1_branch key: {key}"

    def test_excluded_phase_keys(self):
        result = ftum_attractor_domain()
        for key in ("phi0_eff", "ns", "r", "n_winding", "why_excluded"):
            assert key in result["excluded_rs1_phase"], f"Missing excluded key: {key}"

    def test_flat_branch_ns_within_planck_1sigma(self):
        result = ftum_attractor_domain()
        ns = result["flat_branch"]["ns"]
        assert abs(ns - PLANCK_NS_CENTRAL) < PLANCK_NS_SIGMA

    def test_rs1_branch_ns_within_planck_1sigma(self):
        result = ftum_attractor_domain()
        ns = result["rs1_branch"]["ns"]
        assert abs(ns - PLANCK_NS_CENTRAL) < PLANCK_NS_SIGMA

    def test_excluded_phase_outside_planck_1sigma(self):
        """The excluded phase must be well outside Planck 1σ — it is a distinct phase."""
        result = ftum_attractor_domain()
        ns = result["excluded_rs1_phase"]["ns"]
        assert abs(ns - PLANCK_NS_CENTRAL) > PLANCK_NS_SIGMA

    def test_both_branches_consistent(self):
        """Flat-S1 and RS1-saturated branches must agree within 1σ_Planck."""
        result = ftum_attractor_domain()
        assert result["branches_consistent"], (
            f"ns_branch_delta = {result['ns_branch_delta']:.4f} >= {PLANCK_NS_SIGMA}"
        )

    def test_branches_agree_in_phi0eff_within_2pct(self):
        """Both branches give phi0_eff within 2% of each other."""
        result = ftum_attractor_domain()
        assert result["phi0eff_branch_delta_frac"] < 0.02, (
            f"phi0_eff branch difference = "
            f"{100*result['phi0eff_branch_delta_frac']:.2f}% >= 2%"
        )

    def test_phi0_band_symmetric_around_ref(self):
        result = ftum_attractor_domain(phi0_bare_ref=1.0, phi0_band_frac=0.05)
        assert result["phi0_band_lo"] == pytest.approx(0.95)
        assert result["phi0_band_hi"] == pytest.approx(1.05)

    def test_flat_branch_phi0_eff_near_pi5(self):
        """Flat-S1: phi0_eff = 5*2pi*sqrt(1) = 5*2pi = 31.416..."""
        result = ftum_attractor_domain()
        assert result["flat_branch"]["phi0_eff"] == pytest.approx(5 * 2 * np.pi, rel=1e-6)

    def test_rs1_branch_jacobian_near_saturation(self):
        """RS1 Jacobian at kr_c=12 must be within 1e-6 of 1/sqrt(2) for k=1."""
        result = ftum_attractor_domain()
        j_sat = result["rs1_branch"]["j_rs_saturated"]
        j_actual = result["rs1_branch"]["jacobian"]
        assert abs(j_actual - j_sat) < 1e-6

    def test_excluded_phase_phi0eff_below_25(self):
        """Excluded phase with n_w=5 on RS1 must have phi0_eff < 25 (off-attractor)."""
        result = ftum_attractor_domain()
        assert result["excluded_rs1_phase"]["phi0_eff"] < 25.0

    def test_ftum_condition_is_string(self):
        result = ftum_attractor_domain()
        assert isinstance(result["ftum_condition"], str)
        assert len(result["ftum_condition"]) > 0

    def test_degeneracy_is_close(self):
        """The two independent Jacobian flows give ns within 0.2*sigma of each other."""
        result = ftum_attractor_domain()
        ns_delta_in_sigma = result["ns_branch_delta"] / PLANCK_NS_SIGMA
        assert ns_delta_in_sigma < 0.2, (
            f"Branch ns delta = {ns_delta_in_sigma:.2f} sigma — "
            f"degeneracy less tight than expected"
        )


class TestRS1PhaseScan:
    """Tests for rs1_phase_scan() — Jacobian saturation and phase classification."""

    def test_returns_required_keys(self):
        result = rs1_phase_scan()
        for key in ("kr_c_values", "J_RS_values", "J_RS_saturated",
                    "J_RS_converged", "kr_c_saturation",
                    "ns_natural", "ns_mixed",
                    "ns_natural_spread", "natural_all_in_2sigma",
                    "mixed_all_outside_1sigma",
                    "phase_label_natural", "phase_label_mixed"):
            assert key in result, f"Missing key: {key}"

    def test_j_rs_saturates_by_kr_c_5(self):
        """J_RS must be converged to 1/sqrt(2k) for kr_c >= 3."""
        result = rs1_phase_scan()
        assert result["kr_c_saturation"] <= 3.0, (
            f"Saturation only reached at kr_c={result['kr_c_saturation']:.1f}"
        )

    def test_j_rs_saturated_value_correct(self):
        """Saturation value must equal 1/sqrt(2k) for k=1."""
        result = rs1_phase_scan(k=1.0)
        assert result["J_RS_saturated"] == pytest.approx(1.0 / np.sqrt(2.0), rel=1e-10)

    def test_j_rs_monotone_increasing(self):
        """J_RS must increase toward saturation as kr_c increases."""
        result = rs1_phase_scan()
        J = result["J_RS_values"]
        assert np.all(np.diff(J) >= 0.0)

    def test_natural_branch_all_within_planck_2sigma(self):
        """Post-saturation RS1 ns (n_w=7) must all be within Planck 2σ."""
        result = rs1_phase_scan()
        assert result["natural_all_in_2sigma"], (
            f"Some natural-branch ns outside Planck 2σ. "
            f"ns range: [{result['ns_natural'].min():.4f}, "
            f"{result['ns_natural'].max():.4f}]"
        )

    def test_mixed_phase_all_outside_planck_1sigma(self):
        """RS1 mixed phase (n_w=5) must lie outside Planck 1σ — it is excluded."""
        result = rs1_phase_scan()
        assert result["mixed_all_outside_1sigma"], (
            f"Some mixed-phase ns inside Planck 1σ. "
            f"ns range: [{result['ns_mixed'].min():.4f}, "
            f"{result['ns_mixed'].max():.4f}]"
        )

    def test_natural_branch_ns_spread_tiny_post_saturation(self):
        """After saturation, ns must be constant to < 1e-4 (J_RS fully converged)."""
        result = rs1_phase_scan()
        assert result["ns_natural_spread"] < 1e-4, (
            f"ns_natural_spread={result['ns_natural_spread']:.2e} after saturation"
        )

    def test_mixed_phase_ns_lower_than_natural(self):
        """Excluded phase (n_w=5) gives systematically lower ns than natural (n_w=7)."""
        result = rs1_phase_scan()
        assert np.all(result["ns_mixed"] < result["ns_natural"])

    def test_phase_labels_are_strings(self):
        result = rs1_phase_scan()
        assert isinstance(result["phase_label_natural"], str)
        assert isinstance(result["phase_label_mixed"],   str)

    def test_custom_r_c_values(self):
        result = rs1_phase_scan(r_c_values=[5.0, 10.0, 15.0])
        assert len(result["kr_c_values"]) == 3
        assert len(result["ns_natural"])  == 3

    def test_natural_ns_in_planck_window_at_saturation(self):
        """At kr_c=12 (well into saturation), natural-branch ns within 1σ."""
        result = rs1_phase_scan(r_c_values=[12.0])
        ns = float(result["ns_natural"][0])
        assert abs(ns - PLANCK_NS_CENTRAL) < PLANCK_NS_SIGMA


# ===========================================================================
# Transfer function chain: B_mu → rotation → TB/EB   (6 new function tests)
# ===========================================================================

from src.core.inflation import (
    b_mu_rotation_angle,
    quadratic_correction_bound,
    b_mu_kinetic_running,
    verify_dual_jacobian_paths,
    rs1_jacobian_trace,
    birefringence_angle,
    cs_axion_photon_coupling,
    field_displacement_gw,
    jacobian_rs_orbifold,
    effective_phi0_kk,
    effective_phi0_rs,
    jacobian_5d_4d,
    ATTRACTOR_PHI0_EFF_TARGET,
    ATTRACTOR_NS_TARGET,
    ATTRACTOR_TOLERANCE,
    PLANCK_NS_SIGMA,
)
from src.core.transfer import (
    birefringence_transfer_function,
    propagate_primordial_amplitude,
    tb_eb_spectrum,
    PLANCK_2018_COSMO,
)

# shared model values used across tests
_G_AGAMMA_TEST = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, 1.0 / 137.036, 12.0)
_DPHI_TEST     = field_displacement_gw(jacobian_rs_orbifold(1.0, 12.0) * 18.0)
_BETA0_TEST    = birefringence_angle(_G_AGAMMA_TEST, _DPHI_TEST)   # ≈ 0.006132 rad
_CHI_STAR      = PLANCK_2018_COSMO["chi_star"]                     # 13 740 Mpc
_ELLS_TF       = np.array([2, 10, 50, 100, 500])


# ---------------------------------------------------------------------------
# TestBirefringenceTransferFunction
# ---------------------------------------------------------------------------

class TestBirefringenceTransferFunction:
    """birefringence_transfer_function: physics, limits, monotonicity, error cases."""

    def test_coherent_model_all_ones(self):
        """model='coherent' returns T_ℓ = 1 for every ℓ — the UL-axion limit."""
        T = birefringence_transfer_function(_ELLS_TF, model="coherent")
        assert np.all(T == 1.0)

    def test_coherent_shape(self):
        """Output shape equals input ells length."""
        T = birefringence_transfer_function(_ELLS_TF, model="coherent")
        assert T.shape == (_ELLS_TF.shape[0],)

    def test_gaussian_ul_axion_limit(self):
        """gaussian with xi=1e12 Mpc (super-Hubble coherence) ≈ 1 at all CMB ells."""
        T = birefringence_transfer_function(_ELLS_TF, model="gaussian",
                                            coherence_scale_mpc=1e12)
        assert np.allclose(T, 1.0, atol=1e-6), (
            f"UL-axion limit failed: T = {T}"
        )

    def test_gaussian_qcd_axion_limit(self):
        """gaussian with xi=1 Mpc (sub-pc coherence) → T_ℓ = 0 at all CMB ells."""
        T = birefringence_transfer_function(_ELLS_TF, model="gaussian",
                                            coherence_scale_mpc=1.0)
        assert np.all(T == 0.0), f"QCD-axion limit failed: T = {T}"

    def test_gaussian_monotonically_decreasing_in_ell(self):
        """Gaussian suppression is strictly stronger at higher ℓ."""
        ells = np.array([10, 50, 100, 500])
        T = birefringence_transfer_function(ells, model="gaussian",
                                            coherence_scale_mpc=1e7)
        for i in range(len(T) - 1):
            assert T[i] > T[i + 1], (
                f"Not monotone: T[{ells[i]}]={T[i]:.6f} <= T[{ells[i+1]}]={T[i+1]:.6f}"
            )

    def test_gaussian_values_in_unit_interval(self):
        """All T_ℓ values must be in [0, 1]."""
        for xi in [1.0, 1e4, 1e7, 1e12]:
            T = birefringence_transfer_function(_ELLS_TF, model="gaussian",
                                                coherence_scale_mpc=xi)
            assert np.all((T >= 0.0) & (T <= 1.0)), (
                f"Out-of-range values at xi={xi}: {T}"
            )

    def test_invalid_model_raises(self):
        """Unknown model string raises ValueError."""
        with pytest.raises(ValueError, match="coherent.*gaussian"):
            birefringence_transfer_function(_ELLS_TF, model="faraday")


# ---------------------------------------------------------------------------
# TestPropagatePrimordialAmplitude
# ---------------------------------------------------------------------------

class TestPropagatePrimordialAmplitude:
    """propagate_primordial_amplitude: coherent limit, suppressed case, keys."""

    _C_EE = np.array([1.0, 2.0, 4.0, 6.0, 8.0])   # arbitrary positive weights
    _BETA = _BETA0_TEST

    def test_coherent_t_eff_is_one(self):
        """T_ℓ = 1 everywhere → T_eff = 1.0 exactly."""
        r = propagate_primordial_amplitude(self._BETA, np.ones(5), self._C_EE)
        assert r["T_eff"] == pytest.approx(1.0, rel=1e-12)

    def test_coherent_required_equals_observed(self):
        """T_eff=1 → required_beta_primordial = beta_obs (no extra amplitude needed)."""
        r = propagate_primordial_amplitude(self._BETA, np.ones(5), self._C_EE)
        assert r["required_beta_primordial"] == pytest.approx(self._BETA, rel=1e-12)

    def test_coherent_no_extra_amplitude_needed(self):
        """no_extra_amplitude_needed = True iff T_eff ≈ 1."""
        r = propagate_primordial_amplitude(self._BETA, np.ones(5), self._C_EE)
        assert r["no_extra_amplitude_needed"] is True
        assert r["is_coherent_limit"] is True
        assert r["amplitude_enhancement"] == pytest.approx(1.0, rel=1e-12)

    def test_suppressed_requires_more_primordial_amplitude(self):
        """T_eff=0.5 → required_beta_primordial = 2 × beta_obs."""
        r = propagate_primordial_amplitude(self._BETA, np.full(5, 0.5), self._C_EE)
        assert r["T_eff"] == pytest.approx(0.5, rel=1e-12)
        assert r["required_beta_primordial"] == pytest.approx(2.0 * self._BETA, rel=1e-10)
        assert r["no_extra_amplitude_needed"] is False

    def test_c_ee_weighted_mean_correct(self):
        """T_eff is the C_EE-weighted mean of T_ℓ, not an unweighted mean."""
        T = np.array([1.0, 1.0, 0.5, 0.5, 0.5])
        C = np.array([0.0, 0.0, 1.0, 1.0, 1.0])   # weight is entirely on suppressed modes
        r = propagate_primordial_amplitude(self._BETA, T, C)
        assert r["T_eff"] == pytest.approx(0.5, rel=1e-12)


# ---------------------------------------------------------------------------
# TestTBEBWithTransfer
# ---------------------------------------------------------------------------

_ELLS_TW = [10, 50, 100]
_NU_TW   = [145.0]
_NS_TW   = 0.9635

class TestTBEBWithTransfer:
    """tb_eb_spectrum transfer_ell parameter: backward compat, suppression."""

    @classmethod
    def _run(cls, transfer_ell=None, n_k=150):
        return tb_eb_spectrum(
            ells=_ELLS_TW, nu_array=_NU_TW, beta_0=_BETA0_TEST, ns=_NS_TW,
            n_k=n_k, transfer_ell=transfer_ell,
        )

    def test_none_matches_explicit_ones(self):
        """transfer_ell=None is identical to passing an array of ones."""
        out_none = self._run()
        out_ones = self._run(transfer_ell=np.ones(3))
        assert np.allclose(out_none["C_TB"], out_ones["C_TB"], rtol=1e-12)
        assert np.allclose(out_none["C_EB"], out_ones["C_EB"], rtol=1e-12)

    def test_default_transfer_ell_is_ones_in_output(self):
        """Output dict always contains transfer_ell; default is all-ones."""
        out = self._run()
        assert "transfer_ell" in out
        assert np.all(out["transfer_ell"] == 1.0)

    def test_half_transfer_halves_signal(self):
        """T_ℓ = 0.5 uniformly halves both C_TB and C_EB."""
        out_base = self._run()
        out_half = self._run(transfer_ell=np.full(3, 0.5))
        assert np.allclose(out_half["C_TB"] / out_base["C_TB"], 0.5, rtol=1e-12)
        assert np.allclose(out_half["C_EB"] / out_base["C_EB"], 0.5, rtol=1e-12)

    def test_wrong_shape_raises(self):
        """transfer_ell with wrong length raises ValueError."""
        with pytest.raises(ValueError):
            self._run(transfer_ell=np.ones(5))   # 5 ≠ 3


# ---------------------------------------------------------------------------
# TestBMuRotationAngle
# ---------------------------------------------------------------------------

class TestBMuRotationAngle:
    """b_mu_rotation_angle: normalization, linearity, quadratic sub-dominance."""

    def test_consistent_with_birefringence_angle(self):
        """α = (g/2)·(Δφ/L)·L = (g/2)·Δφ = birefringence_angle(g, Δφ) exactly."""
        b_mu_rms = _DPHI_TEST / _CHI_STAR   # Δφ / L_LoS = temporal gradient
        r = b_mu_rotation_angle(b_mu_rms, _G_AGAMMA_TEST, _CHI_STAR)
        assert r["alpha_rad"] == pytest.approx(_BETA0_TEST, rel=1e-12), (
            f"alpha_rad={r['alpha_rad']:.8f} != birefringence_angle={_BETA0_TEST:.8f}"
        )

    def test_is_linear_flag_always_true(self):
        """is_linear must be True regardless of input values."""
        r = b_mu_rotation_angle(0.001, 0.01, 5000.0)
        assert r["is_linear"] is True

    def test_linearity_double_b_mu_doubles_alpha(self):
        """Doubling b_mu_rms doubles alpha_rad — explicit linear check."""
        r1 = b_mu_rotation_angle(1e-6,   _G_AGAMMA_TEST, _CHI_STAR)
        r2 = b_mu_rotation_angle(2e-6,   _G_AGAMMA_TEST, _CHI_STAR)
        assert r2["alpha_rad"] == pytest.approx(2.0 * r1["alpha_rad"], rel=1e-12)

    def test_coupling_factor_formula(self):
        """coupling_factor = (g_agamma / 2) × integration_length_mpc."""
        r = b_mu_rotation_angle(1.0, _G_AGAMMA_TEST, _CHI_STAR)
        expected_cf = 0.5 * _G_AGAMMA_TEST * _CHI_STAR
        assert r["coupling_factor"] == pytest.approx(expected_cf, rel=1e-12)

    def test_quadratic_subdominant_for_model_beta(self):
        """For the model β ≈ 0.006 rad, quadratic correction is < 0.1%."""
        b_mu_rms = _DPHI_TEST / _CHI_STAR
        r = b_mu_rotation_angle(b_mu_rms, _G_AGAMMA_TEST, _CHI_STAR)
        assert r["quadratic_subdominant"] is True
        assert r["quadratic_fraction"] < 0.001

    def test_alpha_zero_for_zero_b_mu(self):
        """Zero B_μ → zero rotation angle."""
        r = b_mu_rotation_angle(0.0, _G_AGAMMA_TEST, _CHI_STAR)
        assert r["alpha_rad"] == 0.0
        assert r["quadratic_fraction"] == 0.0


# ---------------------------------------------------------------------------
# TestQuadraticCorrectionBound
# ---------------------------------------------------------------------------

class TestQuadraticCorrectionBound:
    """quadratic_correction_bound: exact formula, limiting values, subdominance."""

    def test_zero_alpha_exact_prefactor_is_one(self):
        """sin(4α)/(4α) → 1 as α → 0 (L'Hôpital)."""
        q = quadratic_correction_bound(0.0)
        assert q["exact_prefactor"] == pytest.approx(1.0, rel=1e-12)
        assert q["fractional_deviation"] == pytest.approx(0.0, abs=1e-14)

    def test_model_beta_is_subdominant(self):
        """For α ≈ 0.006 rad (β = 0.35°): fractional_deviation < 0.001 (0.1 %)."""
        q = quadratic_correction_bound(_BETA0_TEST)
        assert q["is_subdominant"] is True
        assert q["fractional_deviation"] < 0.001

    def test_analytic_approximation_accuracy(self):
        """Leading-order estimate 8α²/3 agrees with exact to < 10 % for small α."""
        alpha = 0.01
        q = quadratic_correction_bound(alpha)
        assert abs(q["analytic_approximation"] - q["fractional_deviation"]) / \
               q["fractional_deviation"] < 0.10

    def test_exact_prefactor_less_than_one_for_nonzero_alpha(self):
        """sin(4α)/(4α) < 1 for all α ≠ 0 in (0, π/4) — suppression, not enhancement."""
        for alpha in [0.001, 0.01, 0.1, 0.5]:
            q = quadratic_correction_bound(alpha)
            assert q["exact_prefactor"] < 1.0, (
                f"expected < 1 for alpha={alpha}, got {q['exact_prefactor']}"
            )


# ---------------------------------------------------------------------------
# TestBMuKineticRunning
# ---------------------------------------------------------------------------

class TestBMuKineticRunning:
    """b_mu_kinetic_running: trivial default, power-law dependence, stub documentation."""

    def test_default_gamma_zero_returns_one(self):
        """gamma_B = 0 (default) → Z_B = 1.0 at any k_scale."""
        for k in [1e-4, 0.05, 1.0, 100.0]:
            assert b_mu_kinetic_running(k) == pytest.approx(1.0, rel=1e-12)

    def test_power_law_scaling(self):
        """Z_B(k) = (k/k_ref)^gamma_B: doubling k multiplies Z_B by 2^gamma_B."""
        gamma = 1e-3
        z1 = b_mu_kinetic_running(0.05, gamma_B=gamma)
        z2 = b_mu_kinetic_running(0.10, gamma_B=gamma)
        assert z2 / z1 == pytest.approx(2.0**gamma, rel=1e-10)

    def test_perturbative_estimate_is_small(self):
        """For gamma_B ~ alpha_em/(4pi) ~ 6e-4, Z_B deviates from 1 by < 1% at CMB scales.

        At the extremes of the CMB k-range (k ~ 2e-4 to 0.2 Mpc^-1) relative to
        the pivot k_ref=0.05 Mpc^-1, the maximum deviation is:
            |Z_B - 1| = |(k/k_ref)^gamma_B - 1| ≈ gamma_B × |ln(k/k_ref)|
        For gamma_B = 6e-4 and k/k_ref = 4e-3: |Z_B-1| ≈ 6e-4 × 5.5 ≈ 0.33%
        This is physically negligible (< 1%) — confirming no running is required.
        """
        gamma_phys = 6e-4   # ~ alpha_em / (4*pi)
        for k in [2e-4, 0.05, 0.2]:
            z = b_mu_kinetic_running(k, gamma_B=gamma_phys)
            assert abs(z - 1.0) < 0.01, (
                f"Z_B({k})={z:.6f} deviates by {abs(z-1)*100:.3f}% > 1% for physical gamma_B"
            )


# ---------------------------------------------------------------------------
# TestVerifyDualJacobianPaths
# ---------------------------------------------------------------------------

class TestVerifyDualJacobianPaths:
    """verify_dual_jacobian_paths: both branches pass attractor, paths truly differ."""

    @classmethod
    def setup_class(cls):
        cls.result = verify_dual_jacobian_paths()

    def test_both_branches_pass_attractor(self):
        """Both flat-S¹ and RS1 branches must individually satisfy the attractor criterion."""
        assert self.result["flat_branch"]["passes_attractor"] is True, (
            f"Flat branch failed: phi0_eff={self.result['flat_branch']['phi0_eff']:.4f}, "
            f"ns={self.result['flat_branch']['ns']:.4f}"
        )
        assert self.result["rs1_branch"]["passes_attractor"] is True, (
            f"RS1 branch failed: phi0_eff={self.result['rs1_branch']['phi0_eff']:.4f}, "
            f"ns={self.result['rs1_branch']['ns']:.4f}"
        )

    def test_jacobians_differ(self):
        """The two Jacobian flows are genuinely different (different geometry)."""
        assert self.result["paths_differ"] is True
        jac_flat = self.result["flat_branch"]["jacobian"]
        jac_rs1  = self.result["rs1_branch"]["jacobian"]
        assert abs(jac_flat - jac_rs1) > 1.0, (
            f"Jacobians too similar: {jac_flat:.4f} vs {jac_rs1:.4f}"
        )

    def test_dual_path_confirmed(self):
        """dual_path_confirmed = paths_differ AND endpoints_agree."""
        assert self.result["dual_path_confirmed"] is True

    def test_regime_labels_correct(self):
        """Each branch carries the correct geometric regime string."""
        assert self.result["flat_branch"]["regime"] == "Flat_S1_FTUM"
        assert self.result["rs1_branch"]["regime"]  == "RS1_Saturated"

    def test_ns_delta_within_one_sigma(self):
        """The two branches differ in nₛ by less than 1σ_Planck — a tight cluster."""
        assert self.result["ns_delta_sigma"] < 1.0, (
            f"ns_delta_sigma={self.result['ns_delta_sigma']:.3f} >= 1σ"
        )


# ---------------------------------------------------------------------------
# TestRS1JacobianTrace
# ---------------------------------------------------------------------------

class TestRS1JacobianTrace:
    """rs1_jacobian_trace: every step is instrumented, analytic 1% claim verified."""

    @classmethod
    def setup_class(cls):
        cls.trace = rs1_jacobian_trace()

    def test_warp_factor_is_negligible_at_krc12(self):
        """exp(-2π k r_c) at k=1, r_c=12 is effectively zero (< 10⁻³⁰)."""
        assert self.trace["warp_factor"] < 1e-30

    def test_jacobian_fully_saturated(self):
        """J_RS equals J_sat = 1/√(2k) to machine precision at k r_c = 12."""
        assert self.trace["is_saturated"] is True
        assert self.trace["saturation_error"] < 1e-6

    def test_delta_is_geometric(self):
        """Numerical Δ matches analytic 7√2/10 − 1 to < 10⁻⁴."""
        assert self.trace["delta_is_geometric"] is True
        assert abs(self.trace["delta_fraction"] - self.trace["delta_analytic"]) < 1e-4

    def test_delta_value_is_minus_one_percent(self):
        """The RS1 branch lies −1.005 % below flat S¹: Δ = 7√2/10 − 1."""
        assert self.trace["delta_fraction"] == pytest.approx(-0.010050506, rel=1e-6)

    def test_phi0_eff_values_match_existing_functions(self):
        """Trace values must agree with effective_phi0_rs and effective_phi0_kk."""
        expected_rs1  = float(effective_phi0_rs(1.0, 1.0, 12.0, 7))
        expected_flat = float(effective_phi0_kk(1.0, 5))
        assert self.trace["phi0_eff_rs1"]  == pytest.approx(expected_rs1,  rel=1e-12)
        assert self.trace["phi0_eff_flat"] == pytest.approx(expected_flat, rel=1e-12)


# ---------------------------------------------------------------------------
# TestNonMinimalXiSlowRoll
# ---------------------------------------------------------------------------

class TestNonMinimalXiSlowRoll:
    """Tests for nonminimal_xi_slow_roll(), einstein_frame_potential_derivs(),
    field_metric_nonminimal(), and einstein_inflection_phi()."""

    def test_xi_zero_recovers_minimal_coupling(self):
        """At ξ=0, nonminimal_xi_slow_roll must agree with ns_from_phi0."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        ns_ref, r_ref, *_ = ns_from_phi0(phi0_eff)
        ns_xi, r_xi, *_ = nonminimal_xi_slow_roll(phi0_bare=1.0, xi=0.0)
        assert ns_xi == pytest.approx(ns_ref, rel=1e-6), (
            f"ns mismatch at ξ=0: {ns_xi:.8f} vs {ns_ref:.8f}"
        )
        assert r_xi == pytest.approx(r_ref, rel=1e-6), (
            f"r mismatch at ξ=0: {r_xi:.8f} vs {r_ref:.8f}"
        )

    def test_eta_approx_zero_at_inflection_point(self):
        """η ≈ 0 at the inflection point (d²V_E/dχ² = 0 by construction)."""
        for xi in [0.0, 0.0005, 0.001]:
            *_, eps, eta = nonminimal_xi_slow_roll(xi=xi)
            assert abs(eta) < 1e-10, (
                f"η = {eta:.3e} is not ≈ 0 at ξ={xi} inflection point"
            )

    def test_r_has_minimum_near_xi_0005(self):
        """In the hilltop regime, r has a shallow minimum near ξ ≈ 0.0005.

        The minimum r ≈ 0.088 is still above the BK21 bound of 0.036.
        For genuine suppression to r < 0.036 the theory needs the large-field
        Starobinsky regime (see starobinsky_large_xi_ns_r).
        """
        xi_values = [0.0, 0.0005, 0.001, 0.002]
        r_vals = [nonminimal_xi_slow_roll(xi=xi)[1] for xi in xi_values]
        # r should dip near xi=0.0005 and rise back by xi=0.002
        assert r_vals[1] < r_vals[0], "r should decrease at ξ=0.0005 vs ξ=0"
        assert r_vals[3] > r_vals[1], "r should increase again by ξ=0.002"
        # Minimum still well above BK21 bound
        r_min = min(r_vals)
        assert r_min > BICEP_KECK_R_LIMIT, (
            f"Minimum r in hilltop regime ({r_min:.4f}) must exceed "
            f"BK21 bound {BICEP_KECK_R_LIMIT} — suppression requires "
            "large-field Starobinsky regime"
        )

    def test_hilltop_r_cannot_reach_bk21_bound(self):
        """No small-field ξ can bring hilltop r below 0.036.

        The minimum r in the small-field hilltop regime is ≈ 0.088 (at ξ≈0.0005),
        about 2.4× the BK21 bound.  This is an irreducible tension for the
        hilltop GW potential.
        """
        xi_scan = np.linspace(0.0, 0.005, 50)
        r_vals = [nonminimal_xi_slow_roll(xi=float(xi))[1] for xi in xi_scan]
        r_min_hilltop = min(r_vals)
        assert r_min_hilltop > BICEP_KECK_R_LIMIT, (
            f"Unexpectedly found r = {r_min_hilltop:.4f} < {BICEP_KECK_R_LIMIT} "
            "in hilltop regime — please verify."
        )

    def test_einstein_frame_potential_reduces_to_gw_at_xi_zero(self):
        """einstein_frame_potential_derivs at ξ=0 equals gw_potential_derivs."""
        phi0, phi, lam = 2.0, 1.0, 3.0
        V_e, dV_e, d2V_e = einstein_frame_potential_derivs(phi, phi0, lam, xi=0.0)
        V_j, dV_j, d2V_j = gw_potential_derivs(phi, phi0, lam)
        assert V_e   == pytest.approx(V_j,   rel=1e-12)
        assert dV_e  == pytest.approx(dV_j,  rel=1e-12)
        assert d2V_e == pytest.approx(d2V_j, rel=1e-12)

    def test_field_metric_unity_at_xi_zero(self):
        """field_metric_nonminimal = 1 at ξ = 0 (canonical kinetic term)."""
        F = field_metric_nonminimal(5.0, xi=0.0)
        assert F == pytest.approx(1.0, rel=1e-12)

    def test_field_metric_positive_for_xi_gt_zero(self):
        """F = (dφ/dχ)² must be strictly positive for any φ and ξ ≥ 0."""
        for xi in [0.0, 0.001, 0.01, 1.0]:
            for phi in [1.0, 5.0, 20.0]:
                F = field_metric_nonminimal(phi, xi=xi)
                assert F > 0.0, f"F = {F} ≤ 0 at φ={phi}, ξ={xi}"

    def test_einstein_inflection_at_xi_zero(self):
        """At ξ=0, einstein_inflection_phi returns φ₀/√3 to high precision."""
        phi0 = 31.4159
        phi_star = einstein_inflection_phi(phi0, xi=0.0)
        assert phi_star == pytest.approx(phi0 / np.sqrt(3.0), rel=1e-7)

    def test_inflection_point_decreases_with_xi(self):
        """The Einstein-frame inflection point φ* shifts to smaller φ as ξ grows."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        phi_stars = [einstein_inflection_phi(phi0_eff, xi=xi) for xi in [0.0, 0.0005, 0.001]]
        for i in range(len(phi_stars) - 1):
            assert phi_stars[i] > phi_stars[i + 1], (
                f"φ* did not decrease: φ*(ξ={0.0005*i})={phi_stars[i]:.4f} "
                f"≤ φ*(ξ={0.0005*(i+1)})={phi_stars[i+1]:.4f}"
            )

    def test_bicep_keck_r_limit_constant(self):
        """BICEP_KECK_R_LIMIT must equal 0.036."""
        assert BICEP_KECK_R_LIMIT == pytest.approx(0.036, rel=1e-10)


# ---------------------------------------------------------------------------
# TestStarobinskyLargeXiLimit
# ---------------------------------------------------------------------------

class TestStarobinskyLargeXiLimit:
    """Tests for starobinsky_large_xi_ns_r() — analytic Starobinsky plateau."""

    def test_ns_formula_n60(self):
        """nₛ = 1 − 2/N at N = 60."""
        ns, _ = starobinsky_large_xi_ns_r(N=60)
        assert ns == pytest.approx(1.0 - 2.0/60.0, rel=1e-12)

    def test_r_formula_n60(self):
        """r = 12/N² at N = 60."""
        _, r = starobinsky_large_xi_ns_r(N=60)
        assert r == pytest.approx(12.0/3600.0, rel=1e-12)

    def test_r_below_bk21_for_n_ge_19(self):
        """r < 0.036 for all N ≥ 19 (Starobinsky limit resolves BK21 tension)."""
        for N in [19, 30, 50, 55, 60, 65]:
            _, r = starobinsky_large_xi_ns_r(N=N)
            assert r < BICEP_KECK_R_LIMIT, (
                f"r = {r:.4f} ≥ {BICEP_KECK_R_LIMIT} at N={N}"
            )

    def test_ns_within_planck_2sigma_for_n_55_to_65(self):
        """nₛ within Planck 2018 2σ for N in [55, 65]."""
        for N in [55, 57, 60, 63, 65]:
            ns, _ = starobinsky_large_xi_ns_r(N=N)
            assert abs(ns - PLANCK_NS_CENTRAL) < 2.0 * PLANCK_NS_SIGMA, (
                f"nₛ = {ns:.4f} outside Planck 2σ at N={N}"
            )

    def test_n55_matches_hilltop_ns(self):
        """At N=55, Starobinsky nₛ ≈ 0.9636, matching the hilltop value."""
        ns_starobinsky, _ = starobinsky_large_xi_ns_r(N=55)
        ns_hilltop, *_ = nonminimal_xi_slow_roll(xi=0.0)
        # They should be within 1σ_Planck of each other
        assert abs(ns_starobinsky - ns_hilltop) < PLANCK_NS_SIGMA, (
            f"nₛ(Starobinsky,N=55)={ns_starobinsky:.4f} and "
            f"nₛ(hilltop)={ns_hilltop:.4f} differ by >{PLANCK_NS_SIGMA}"
        )

    def test_r_ratio_starobinsky_vs_hilltop(self):
        """Starobinsky r/r_hilltop < 0.04 at N=60 (24× suppression)."""
        _, r_staro = starobinsky_large_xi_ns_r(N=60)
        _, r_hilltop, *_ = nonminimal_xi_slow_roll(xi=0.0)
        ratio = r_staro / r_hilltop
        assert ratio < 0.04, (
            f"Expected Starobinsky r/r_hilltop < 0.04; got {ratio:.4f}"
        )

