# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_transfer.py
======================
Comprehensive test suite for src/core/transfer.py — the CMB transfer-function
module.  Covers every public function:

    primordial_power_spectrum
    cmb_source_function
    ee_source_function
    te_source_function
    angular_power_spectrum          (TT Cℓ)
    dl_from_cl                      (Dℓ conversion)
    chi2_planck                     (χ² comparison)
    birefringence_angle_freq        (frequency-dependent β)
    tb_eb_spectrum                  (TB/EB 2D spectra — the LiteBIRD falsifier)
    birefringence_transfer_function (T_ℓ mode-dependent suppression)
    propagate_primordial_amplitude  (T_ℓ inversion)

"""
from __future__ import annotations

import math

import numpy as np
import pytest

from src.core.transfer import (
    PLANCK_2018_COSMO,
    PLANCK_2018_DL_REF,
    angular_power_spectrum,
    birefringence_angle_freq,
    birefringence_transfer_function,
    chi2_planck,
    cmb_source_function,
    dl_from_cl,
    ee_source_function,
    primordial_power_spectrum,
    propagate_primordial_amplitude,
    tb_eb_spectrum,
    te_source_function,
)


# ---------------------------------------------------------------------------
# Shared test fixtures / constants
# ---------------------------------------------------------------------------

_NS   = 0.9635          # Unitary Manifold prediction
_AS   = PLANCK_2018_COSMO["As"]
# β₀ ≈ birefringence_angle(cs_axion_photon_coupling(k_CS=74, ...), ...) [radians]
# This value is used as a representative β for testing; the exact formula is in
# src/core/inflation.birefringence_angle / cs_axion_photon_coupling (k_CS=74).
_BETA = 0.006109

# Small ℓ set for fast integration (n_k=200 is enough for shape / monotonicity)
_ELLS_SMALL = [10, 50, 100, 200, 500]
_NU_3       = [93.0, 145.0, 220.0]    # LiteBIRD-representative bands


# ===========================================================================
# 1.  primordial_power_spectrum
# ===========================================================================

class TestPrimordialPowerSpectrum:
    """Scale-free primordial power spectrum Δ²_ℛ(k) = Aₛ (k/k★)^(nₛ−1)."""

    def test_at_pivot_equals_as(self):
        """Δ²_ℛ(k★) = Aₛ exactly."""
        k_pivot = PLANCK_2018_COSMO["k_pivot"]
        result  = primordial_power_spectrum(k_pivot, _NS)
        assert result == pytest.approx(_AS)

    def test_positive_everywhere(self):
        k = np.geomspace(1e-5, 1.0, 100)
        assert np.all(primordial_power_spectrum(k, _NS) > 0)

    def test_red_tilt_decreases_with_k(self):
        """nₛ < 1 → P decreases as k increases (red tilt)."""
        k = np.geomspace(1e-3, 1.0, 10)
        P = primordial_power_spectrum(k, _NS)
        assert np.all(np.diff(P) < 0)

    def test_flat_spectrum_is_constant(self):
        """nₛ = 1 → scale-invariant → constant ratio at any two k."""
        k1, k2 = 0.01, 0.10
        P1 = primordial_power_spectrum(k1, 1.0)
        P2 = primordial_power_spectrum(k2, 1.0)
        assert P1 == pytest.approx(P2, rel=1e-12)

    def test_custom_as_scales_result(self):
        k   = PLANCK_2018_COSMO["k_pivot"]
        As2 = 2.0 * _AS
        assert primordial_power_spectrum(k, _NS, As=As2) == pytest.approx(2.0 * _AS)

    def test_scalar_input_returns_scalar(self):
        result = primordial_power_spectrum(0.05, _NS)
        assert isinstance(result, float)

    def test_array_input_returns_array(self):
        k = np.array([0.01, 0.05, 0.1])
        result = primordial_power_spectrum(k, _NS)
        assert result.shape == (3,)

    def test_power_law_ratio(self):
        """P(2k) / P(k) = 2^(nₛ−1) for any k."""
        k = 0.05
        ratio = primordial_power_spectrum(2 * k, _NS) / primordial_power_spectrum(k, _NS)
        assert ratio == pytest.approx(2.0 ** (_NS - 1.0), rel=1e-12)


# ===========================================================================
# 2.  cmb_source_function  (temperature / TT source)
# ===========================================================================

class TestCMBSourceFunction:
    """S(k) = (1/3) cos(k r_s★) exp(−(k/k_silk)^α) — SW plateau model."""

    def test_returns_array_for_array_input(self):
        k = np.geomspace(1e-5, 0.8, 50)
        S = cmb_source_function(k)
        assert S.shape == (50,)

    def test_finite_everywhere(self):
        k = np.geomspace(1e-5, 0.8, 200)
        assert np.all(np.isfinite(cmb_source_function(k)))

    def test_amplitude_at_k_zero_limit(self):
        """As k → 0, cos → 1 and damping → 1, so S → 1/3."""
        k_tiny = 1e-6
        S = cmb_source_function(k_tiny)
        assert S == pytest.approx(1.0 / 3.0, rel=1e-3)

    def test_silk_damping_suppresses_large_k(self):
        """S(k) → 0 exponentially for k >> k_silk."""
        k_silk = PLANCK_2018_COSMO["k_silk"]
        S_large = cmb_source_function(5.0 * k_silk)
        S_small = cmb_source_function(0.1 * k_silk)
        assert abs(S_large) < abs(S_small)

    def test_acoustic_oscillation_sign_change(self):
        """cos(k r_s★) changes sign → S changes sign over k range."""
        k = np.linspace(1e-4, 0.3, 1000)
        S = cmb_source_function(k)
        assert np.any(S > 0) and np.any(S < 0)

    def test_default_rs_star_matches_planck(self):
        """Default rs_star = 144.7 Mpc → first zero at k = π/(2 r_s★) ≈ 0.0108 Mpc⁻¹."""
        rs_star = PLANCK_2018_COSMO["rs_star"]
        k_zero  = math.pi / (2.0 * rs_star)
        S = cmb_source_function(k_zero)
        assert abs(S) < 1e-3   # near zero (residual from damping factor negligible here)

    def test_scalar_input(self):
        assert isinstance(cmb_source_function(0.05), float)


# ===========================================================================
# 3.  ee_source_function  (E-mode / polarization source)
# ===========================================================================

class TestEESourceFunction:
    """S_E(k) = (√3/2) sin(k r_s★) exp(−(k/k_silk)^α) — E-mode source."""

    def test_returns_array(self):
        k = np.geomspace(1e-5, 0.8, 50)
        assert ee_source_function(k).shape == (50,)

    def test_finite_everywhere(self):
        k = np.geomspace(1e-5, 0.8, 200)
        assert np.all(np.isfinite(ee_source_function(k)))

    def test_zero_at_k_zero(self):
        """S_E → 0 as k → 0 (sin(k r_s★) → 0)."""
        S = ee_source_function(1e-8)
        assert abs(S) < 1e-5

    def test_phase_quadrature_with_tt_source(self):
        """At k where cos(k r_s★)=0, S_T=0 and S_E is at its peak, and vice versa."""
        rs_star = PLANCK_2018_COSMO["rs_star"]
        # k where cos = 0: k r_s★ = π/2 → k = π/(2 r_s★)
        k_cos_zero = math.pi / (2.0 * rs_star)
        S_T = cmb_source_function(k_cos_zero)
        S_E = ee_source_function(k_cos_zero)
        assert abs(S_T) < 1e-3 * abs(S_E)   # S_T ≈ 0, S_E ≠ 0

    def test_amplitude_at_first_sin_peak(self):
        """At k r_s★ = π/2, S_E = (√3/2) × damping ≤ √3/2."""
        rs_star = PLANCK_2018_COSMO["rs_star"]
        k_peak  = math.pi / (2.0 * rs_star)
        S_E     = ee_source_function(k_peak)
        assert abs(S_E) <= math.sqrt(3.0) / 2.0 + 1e-10

    def test_silk_suppressed_at_large_k(self):
        k_silk = PLANCK_2018_COSMO["k_silk"]
        S_lo   = ee_source_function(0.05 * k_silk)
        S_hi   = ee_source_function(5.0 * k_silk)
        assert abs(S_hi) < abs(S_lo) or abs(S_hi) < 1e-3


# ===========================================================================
# 4.  te_source_function  (TE cross-correlation source)
# ===========================================================================

class TestTESourceFunction:
    """S_TE(k) = S_T(k) · S_E(k) — product source."""

    def test_equals_product_of_tt_and_ee(self):
        k = np.geomspace(1e-4, 0.3, 80)
        S_TE = te_source_function(k)
        S_T  = cmb_source_function(k)
        S_E  = ee_source_function(k)
        assert np.allclose(S_TE, S_T * S_E, rtol=1e-12)

    def test_finite_everywhere(self):
        k = np.geomspace(1e-5, 0.8, 200)
        assert np.all(np.isfinite(te_source_function(k)))

    def test_negative_trough_exists(self):
        """TE source can be negative → negative TE correlation at some scales."""
        k   = np.linspace(1e-4, 0.3, 500)
        S   = te_source_function(k)
        assert np.any(S < 0)

    def test_zero_at_k_zero(self):
        """S_TE → 0 as k → 0 because S_E → 0."""
        assert abs(te_source_function(1e-8)) < 1e-5

    def test_silk_suppressed(self):
        k_silk = PLANCK_2018_COSMO["k_silk"]
        assert abs(te_source_function(5.0 * k_silk)) < 1e-3


# ===========================================================================
# 5.  angular_power_spectrum  (TT Cℓ)
# ===========================================================================

class TestAngularPowerSpectrum:
    """Cℓ via line-of-sight k-integration: shape, positivity, ℓ-dependence."""

    @classmethod
    def _cl(cls, ells=None, ns=_NS, n_k=300):
        if ells is None:
            ells = _ELLS_SMALL
        return angular_power_spectrum(ells, ns, n_k=n_k)

    def test_output_shape(self):
        Cl = self._cl()
        assert Cl.shape == (len(_ELLS_SMALL),)

    def test_all_positive(self):
        """TT Cℓ must be non-negative (S² integrand is non-negative)."""
        Cl = self._cl()
        assert np.all(Cl >= 0.0)

    def test_finite(self):
        assert np.all(np.isfinite(self._cl()))

    def test_redder_ns_gives_more_large_scale_power(self):
        """ns_red < ns_blue → C_ℓ_small is larger for redder spectrum."""
        Cl_red  = angular_power_spectrum([10], 0.96, n_k=200)
        Cl_blue = angular_power_spectrum([10], 0.98, n_k=200)
        assert Cl_red[0] > Cl_blue[0]

    def test_higher_as_scales_cl_linearly(self):
        """Cℓ ∝ Aₛ."""
        As0 = PLANCK_2018_COSMO["As"]
        Cl1 = angular_power_spectrum([100], _NS, As=As0, n_k=200)
        Cl2 = angular_power_spectrum([100], _NS, As=2.0 * As0, n_k=200)
        assert Cl2[0] == pytest.approx(2.0 * Cl1[0], rel=1e-10)

    def test_cl_decreases_in_damping_tail(self):
        """Silk damping: C_1000 < C_200 (damping tail suppressed)."""
        Cl = angular_power_spectrum([200, 1000], _NS, n_k=500)
        assert Cl[1] < Cl[0]

    def test_single_ell_returns_length_one_array(self):
        Cl = angular_power_spectrum([220], _NS, n_k=300)
        assert Cl.shape == (1,)


# ===========================================================================
# 6.  dl_from_cl  (Dℓ = ℓ(ℓ+1)/(2π) Cℓ T_CMB² [μK²])
# ===========================================================================

class TestDlFromCl:
    """Dℓ conversion: correct formula and μK² units."""

    def test_formula(self):
        """Dℓ = ℓ(ℓ+1)/(2π) Cℓ T²_μK."""
        ells = np.array([100])
        Cl   = np.array([1.0e-10])
        T_K  = PLANCK_2018_COSMO["T_cmb_K"]
        T_uK = T_K * 1e6
        expected = 100 * 101 / (2.0 * math.pi) * 1.0e-10 * T_uK ** 2
        Dl   = dl_from_cl(ells, Cl, T_K)
        assert Dl[0] == pytest.approx(expected, rel=1e-12)

    def test_output_shape_matches_input(self):
        ells = np.array([2, 10, 100, 500])
        Cl   = np.ones(4) * 1e-10
        Dl   = dl_from_cl(ells, Cl)
        assert Dl.shape == (4,)

    def test_dl_non_negative_for_positive_cl(self):
        ells = np.arange(2, 11)
        Cl   = np.full(9, 1e-10)
        Dl   = dl_from_cl(ells, Cl)
        assert np.all(Dl >= 0)

    def test_dl_at_ell_2_correct_prefactor(self):
        """ℓ=2: prefactor = 2×3/(2π) = 3/π."""
        Cl   = np.array([1.0])
        T_uK = PLANCK_2018_COSMO["T_cmb_K"] * 1e6
        Dl   = dl_from_cl(np.array([2]), Cl)
        expected = 3.0 / math.pi * T_uK ** 2
        assert Dl[0] == pytest.approx(expected, rel=1e-12)

    def test_dl_increases_with_ell_for_constant_cl(self):
        """ℓ(ℓ+1) is increasing → Dℓ increases for constant Cℓ."""
        ells = np.array([10, 100, 1000])
        Cl   = np.full(3, 1e-10)
        Dl   = dl_from_cl(ells, Cl)
        assert Dl[0] < Dl[1] < Dl[2]

    def test_round_trip_cl_dl(self):
        """Inverting Dℓ → Cℓ recovers the original spectrum."""
        ells = np.array([50, 200, 500])
        Cl   = np.array([2.0e-10, 1.0e-10, 5.0e-11])
        T_K  = PLANCK_2018_COSMO["T_cmb_K"]
        T_uK = T_K * 1e6
        Dl   = dl_from_cl(ells, Cl, T_K)
        Cl_back = Dl / (ells * (ells + 1) / (2 * math.pi) * T_uK ** 2)
        assert np.allclose(Cl_back, Cl, rtol=1e-12)


# ===========================================================================
# 7.  chi2_planck  (χ² comparison vs Planck 2018)
# ===========================================================================

class TestChi2Planck:
    """χ² statistics vs built-in Planck 2018 Dℓ reference table."""

    @classmethod
    def _ref_ells(cls):
        return np.array(sorted(PLANCK_2018_DL_REF.keys()))

    @classmethod
    def _ref_dl(cls, ells):
        return np.array([PLANCK_2018_DL_REF[el][0] for el in ells])

    def test_perfect_match_gives_zero_chi2(self):
        """Supplying the reference Dℓ values yields χ² = 0."""
        ells = self._ref_ells()
        Dl   = self._ref_dl(ells)
        chi2, _, _ = chi2_planck(ells, Dl)
        assert chi2 == pytest.approx(0.0, abs=1e-12)

    def test_returns_three_values(self):
        ells = self._ref_ells()
        Dl   = self._ref_dl(ells)
        result = chi2_planck(ells, Dl)
        assert len(result) == 3

    def test_n_dof_equals_matched_multipoles(self):
        ells = self._ref_ells()
        Dl   = self._ref_dl(ells)
        _, _, n_dof = chi2_planck(ells, Dl)
        assert n_dof == len(ells)

    def test_chi2_positive_for_shifted_dl(self):
        ells = self._ref_ells()
        Dl   = self._ref_dl(ells) * 1.5   # deliberate 50% shift
        chi2, _, _ = chi2_planck(ells, Dl)
        assert chi2 > 0.0

    def test_chi2_dof_equals_chi2_over_n(self):
        ells = self._ref_ells()
        Dl   = self._ref_dl(ells) * 1.2
        chi2, chi2_dof, n = chi2_planck(ells, Dl)
        assert chi2_dof == pytest.approx(chi2 / n, rel=1e-12)

    def test_unmatched_ells_raises_value_error(self):
        """All ells outside reference table → ValueError."""
        with pytest.raises(ValueError):
            chi2_planck(np.array([999999]), np.array([100.0]))

    def test_partial_match_uses_only_matched(self):
        """Mixed matched/unmatched: χ² uses only the matched multipoles."""
        ells_ref    = self._ref_ells()
        Dl_ref      = self._ref_dl(ells_ref)
        # Append a non-reference multipole
        ells_mixed  = np.append(ells_ref, [9999])
        Dl_mixed    = np.append(Dl_ref, [0.0])
        _, _, n_mixed = chi2_planck(ells_mixed, Dl_mixed)
        assert n_mixed == len(ells_ref)   # extra ell not counted

    def test_larger_shift_gives_larger_chi2(self):
        ells = self._ref_ells()
        Dl0  = self._ref_dl(ells)
        c1, _, _ = chi2_planck(ells, Dl0 * 1.1)
        c2, _, _ = chi2_planck(ells, Dl0 * 1.5)
        assert c2 > c1


# ===========================================================================
# 8.  birefringence_angle_freq  (frequency-dependent β(ν))
# ===========================================================================

class TestBirefringenceAngleFreq:
    """β(ν): achromatic UL-axion and dispersive Faraday scaling."""

    def test_achromatic_is_independent_of_frequency(self):
        """Achromatic model: β(ν) = β₀ for all ν."""
        for nu in [30.0, 93.0, 145.0, 220.0, 280.0]:
            assert birefringence_angle_freq(nu, _BETA) == pytest.approx(_BETA)

    def test_achromatic_at_reference_equals_beta0(self):
        nu_ref = 145.0
        assert birefringence_angle_freq(nu_ref, _BETA, nu_ref_GHz=nu_ref) == pytest.approx(_BETA)

    def test_dispersive_at_reference_equals_beta0(self):
        nu_ref = 145.0
        result = birefringence_angle_freq(nu_ref, _BETA, nu_ref_GHz=nu_ref,
                                          frequency_achromatic=False)
        assert result == pytest.approx(_BETA)

    def test_dispersive_below_reference_larger(self):
        """Faraday: β(ν_low) > β(ν_high) because β ∝ ν⁻²."""
        b93  = birefringence_angle_freq(93.0,  _BETA, frequency_achromatic=False)
        b145 = birefringence_angle_freq(145.0, _BETA, frequency_achromatic=False)
        assert b93 > b145

    def test_dispersive_faraday_scaling(self):
        """β(ν₁)/β(ν₂) = (ν₂/ν₁)²."""
        nu1, nu2 = 93.0, 145.0
        b1 = birefringence_angle_freq(nu1, _BETA, frequency_achromatic=False)
        b2 = birefringence_angle_freq(nu2, _BETA, frequency_achromatic=False)
        assert b1 / b2 == pytest.approx((nu2 / nu1) ** 2, rel=1e-12)

    def test_achromatic_ratio_is_one(self):
        """Achromatic: C_TB(93) / C_TB(145) is tested via ratio of β values = 1."""
        b93  = birefringence_angle_freq(93.0,  _BETA, frequency_achromatic=True)
        b145 = birefringence_angle_freq(145.0, _BETA, frequency_achromatic=True)
        assert b93 / b145 == pytest.approx(1.0, rel=1e-12)

    def test_faraday_ratio_distinguishable_from_one(self):
        b93  = birefringence_angle_freq(93.0,  _BETA, frequency_achromatic=False)
        b145 = birefringence_angle_freq(145.0, _BETA, frequency_achromatic=False)
        assert not math.isclose(b93 / b145, 1.0, rel_tol=0.01)

    def test_returns_float(self):
        assert isinstance(birefringence_angle_freq(145.0, _BETA), float)


# ===========================================================================
# 9.  tb_eb_spectrum  (TB and EB angular power spectra — the LiteBIRD falsifier)
# ===========================================================================

class TestTBEBSpectrum:
    """C_TB[ℓ, ν] and C_EB[ℓ, ν]: the frequency-dependent birefringence spectra.

    These are the LiteBIRD-testable falsifiers for the Unitary Manifold.
    The key prediction is achromaticity: C_TB(ν₁)/C_TB(ν₂) = 1 for all ℓ
    under the UL-axion birefringence model.
    """

    @classmethod
    def _run(cls, beta=_BETA, achromatic=True, n_k=200, ells=None,
             nu_array=None, transfer_ell=None):
        if ells is None:
            ells = _ELLS_SMALL
        if nu_array is None:
            nu_array = _NU_3
        return tb_eb_spectrum(
            ells=ells, nu_array=nu_array,
            beta_0=beta, ns=_NS, n_k=n_k,
            frequency_achromatic=achromatic,
            transfer_ell=transfer_ell,
        )

    # --- output structure ---

    def test_output_is_dict(self):
        out = self._run()
        assert isinstance(out, dict)

    def test_output_has_required_keys(self):
        out  = self._run()
        keys = {"ells", "nu_array", "C_TE", "C_EE", "C_TB", "C_EB",
                "beta_0", "frequency_achromatic", "transfer_ell"}
        assert keys.issubset(out.keys())

    def test_c_tb_shape(self):
        out = self._run()
        assert out["C_TB"].shape == (len(_ELLS_SMALL), len(_NU_3))

    def test_c_eb_shape(self):
        out = self._run()
        assert out["C_EB"].shape == (len(_ELLS_SMALL), len(_NU_3))

    def test_c_te_shape(self):
        out = self._run()
        assert out["C_TE"].shape == (len(_ELLS_SMALL),)

    def test_c_ee_shape(self):
        out = self._run()
        assert out["C_EE"].shape == (len(_ELLS_SMALL),)

    def test_beta_0_echoed_in_output(self):
        out = self._run(beta=0.1)
        assert out["beta_0"] == pytest.approx(0.1)

    def test_frequency_achromatic_flag_echoed(self):
        out_ach  = self._run(achromatic=True)
        out_disp = self._run(achromatic=False)
        assert out_ach["frequency_achromatic"] is True
        assert out_disp["frequency_achromatic"] is False

    # --- finite / valid values ---

    def test_all_finite(self):
        out = self._run()
        for key in ("C_TE", "C_EE", "C_TB", "C_EB"):
            assert np.all(np.isfinite(out[key])), f"{key} has non-finite values"

    def test_c_ee_non_negative(self):
        """C_EE ≥ 0 (S_E² integrand is non-negative)."""
        out = self._run()
        assert np.all(out["C_EE"] >= 0.0)

    # --- ΛCDM limit (β = 0) ---

    def test_lcdm_tb_exactly_zero(self):
        """β = 0 → C_TB = 0 (standard ΛCDM has no parity violation)."""
        out = self._run(beta=0.0)
        assert np.allclose(out["C_TB"], 0.0, atol=0.0)

    def test_lcdm_eb_exactly_zero(self):
        """β = 0 → C_EB = 0."""
        out = self._run(beta=0.0)
        assert np.allclose(out["C_EB"], 0.0, atol=0.0)

    def test_lcdm_c_te_nonzero(self):
        """C_TE is computed independently of β — it survives at β = 0."""
        out = self._run(beta=0.0)
        assert np.any(out["C_TE"] != 0.0)

    # --- Non-ΛCDM signal ---

    def test_model_tb_nonzero(self):
        """β ≠ 0 → C_TB ≠ 0."""
        out = self._run()
        assert np.any(out["C_TB"] != 0.0)

    def test_model_eb_nonzero(self):
        """β ≠ 0 → C_EB ≠ 0."""
        out = self._run()
        assert np.any(out["C_EB"] != 0.0)

    # --- Proportionality relations ---

    def test_c_tb_proportional_to_c_te(self):
        """C_TB[:, j] = 2 β(νⱼ) C_TE for each ν-column."""
        out  = self._run()
        C_TE = out["C_TE"]
        for j, nu in enumerate(_NU_3):
            beta_nu  = birefringence_angle_freq(nu, _BETA, frequency_achromatic=True)
            expected = 2.0 * beta_nu * C_TE
            assert np.allclose(out["C_TB"][:, j], expected, rtol=1e-12)

    def test_c_eb_proportional_to_c_ee(self):
        """C_EB[:, j] = 2 β(νⱼ) C_EE for each ν-column."""
        out  = self._run()
        C_EE = out["C_EE"]
        for j, nu in enumerate(_NU_3):
            beta_nu  = birefringence_angle_freq(nu, _BETA, frequency_achromatic=True)
            expected = 2.0 * beta_nu * C_EE
            assert np.allclose(out["C_EB"][:, j], expected, rtol=1e-12)

    # --- Frequency achromaticity (THE LiteBIRD falsification handle) ---

    def test_achromatic_ctb_ratio_equals_one(self):
        """Achromatic UL-axion: C_TB(93 GHz) / C_TB(145 GHz) = 1 at all ℓ.

        This is the unique observable signature of the Unitary Manifold
        birefringence prediction.  Deviations > 3σ from unity at LiteBIRD
        sensitivity (σ ≈ few %) would falsify the model.
        """
        out     = self._run(achromatic=True)
        idx_93  = _NU_3.index(93.0)
        idx_145 = _NU_3.index(145.0)
        C_93    = out["C_TB"][:, idx_93]
        C_145   = out["C_TB"][:, idx_145]
        assert np.allclose(C_93 / C_145, 1.0, rtol=1e-12)

    def test_achromatic_ceb_ratio_equals_one(self):
        """Achromatic: C_EB(93 GHz) / C_EB(145 GHz) = 1."""
        out     = self._run(achromatic=True)
        idx_93  = _NU_3.index(93.0)
        idx_145 = _NU_3.index(145.0)
        ratio   = out["C_EB"][:, idx_93] / out["C_EB"][:, idx_145]
        assert np.allclose(ratio, 1.0, rtol=1e-12)

    def test_achromatic_all_nu_ratios_one(self):
        """Achromatic: ALL ν-column ratios = 1 (not just one pair)."""
        out   = self._run(achromatic=True)
        col_0 = out["C_TB"][:, 0]
        for j in range(1, len(_NU_3)):
            ratio = out["C_TB"][:, j] / col_0
            assert np.allclose(ratio, 1.0, rtol=1e-12), (
                f"Achromaticity broken at ν={_NU_3[j]} GHz"
            )

    def test_faraday_ratio_is_inverse_square(self):
        """Dispersive model: C_TB(93) / C_TB(145) = (145/93)²."""
        out     = self._run(achromatic=False)
        idx_93  = _NU_3.index(93.0)
        idx_145 = _NU_3.index(145.0)
        ratio   = out["C_TB"][:, idx_93] / out["C_TB"][:, idx_145]
        assert np.allclose(ratio, (145.0 / 93.0) ** 2, rtol=1e-10)

    def test_faraday_ratio_is_not_one(self):
        """Faraday model: ratio ≠ 1 — distinguishable from UL-axion."""
        out     = self._run(achromatic=False)
        idx_93  = _NU_3.index(93.0)
        idx_145 = _NU_3.index(145.0)
        ratio   = out["C_TB"][:, idx_93] / out["C_TB"][:, idx_145]
        assert not np.allclose(ratio, 1.0, rtol=0.01)

    def test_achromatic_and_dispersive_differ_at_large_separation(self):
        """For widely separated frequencies the two models are distinguishable."""
        out_ach  = self._run(achromatic=True,  nu_array=[30.0, 220.0])
        out_disp = self._run(achromatic=False, nu_array=[30.0, 220.0])
        ratio_ach  = out_ach["C_TB"][:, 0]  / out_ach["C_TB"][:, 1]
        ratio_disp = out_disp["C_TB"][:, 0] / out_disp["C_TB"][:, 1]
        # Achromatic ratio = 1; dispersive = (220/30)² ≈ 53.8
        assert np.allclose(ratio_ach, 1.0, rtol=1e-12)
        assert np.all(ratio_disp > 10.0)

    # --- Linearity in β ---

    def test_tb_linear_in_beta(self):
        """C_TB(2β) = 2 C_TB(β) — linear in β (small-angle approximation)."""
        out1 = self._run(beta=_BETA)
        out2 = self._run(beta=2.0 * _BETA)
        assert np.allclose(out2["C_TB"], 2.0 * out1["C_TB"], rtol=1e-12)

    def test_eb_linear_in_beta(self):
        out1 = self._run(beta=_BETA)
        out2 = self._run(beta=2.0 * _BETA)
        assert np.allclose(out2["C_EB"], 2.0 * out1["C_EB"], rtol=1e-12)

    def test_negative_beta_flips_sign(self):
        out_pos = self._run(beta=_BETA)
        out_neg = self._run(beta=-_BETA)
        assert np.allclose(out_neg["C_TB"], -out_pos["C_TB"], rtol=1e-12)

    # --- transfer_ell parameter ---

    def test_transfer_ell_none_gives_ones(self):
        """Default transfer_ell=None → output transfer_ell is all-ones array."""
        out = self._run()
        assert np.all(out["transfer_ell"] == 1.0)

    def test_transfer_ell_ones_equals_none(self):
        """Passing np.ones(n_ell) is identical to None."""
        T_ones = np.ones(len(_ELLS_SMALL))
        out_none = self._run(transfer_ell=None)
        out_ones = self._run(transfer_ell=T_ones)
        assert np.allclose(out_none["C_TB"], out_ones["C_TB"], rtol=1e-12)

    def test_transfer_ell_half_halves_ctb(self):
        """T_ℓ = 0.5 → C_TB is halved."""
        T_half   = np.full(len(_ELLS_SMALL), 0.5)
        out_full = self._run(transfer_ell=None)
        out_half = self._run(transfer_ell=T_half)
        assert np.allclose(out_half["C_TB"], 0.5 * out_full["C_TB"], rtol=1e-12)

    def test_transfer_ell_zero_gives_zero_ctb(self):
        """T_ℓ = 0 → C_TB = 0 (full suppression)."""
        T_zero = np.zeros(len(_ELLS_SMALL))
        out    = self._run(transfer_ell=T_zero)
        assert np.allclose(out["C_TB"], 0.0, atol=0.0)

    def test_transfer_ell_wrong_length_raises(self):
        """transfer_ell with wrong length raises ValueError."""
        with pytest.raises(ValueError):
            self._run(transfer_ell=np.ones(len(_ELLS_SMALL) + 2))

    def test_transfer_ell_echoed_in_output(self):
        T = np.array([0.9, 0.8, 0.7, 0.6, 0.5])
        out = self._run(transfer_ell=T)
        assert np.allclose(out["transfer_ell"], T)


# ===========================================================================
# 10. birefringence_transfer_function  (T_ℓ mode-dependent suppression)
# ===========================================================================

class TestBirefringenceTransferFunction:
    """T_ℓ ∈ [0,1] — coherent and gaussian suppression models."""

    _ELLS = np.array([10, 50, 100, 200, 500, 1000])

    def test_coherent_model_returns_ones(self):
        T = birefringence_transfer_function(self._ELLS, model="coherent")
        assert np.allclose(T, 1.0)

    def test_coherent_model_shape(self):
        T = birefringence_transfer_function(self._ELLS, model="coherent")
        assert T.shape == (len(self._ELLS),)

    def test_gaussian_infinite_coherence_gives_ones(self):
        """ξ → ∞ → no suppression → T_ℓ = 1."""
        T = birefringence_transfer_function(self._ELLS, model="gaussian",
                                             coherence_scale_mpc=np.inf)
        assert np.allclose(T, 1.0)

    def test_gaussian_decreases_with_ell(self):
        """Gaussian model: T_ℓ is a monotonically decreasing function of ℓ."""
        T = birefringence_transfer_function(self._ELLS, model="gaussian",
                                             coherence_scale_mpc=100.0)
        assert np.all(np.diff(T) <= 0)

    def test_gaussian_clipped_to_zero_one(self):
        """T_ℓ values are clipped to [0, 1]."""
        T = birefringence_transfer_function(self._ELLS, model="gaussian",
                                             coherence_scale_mpc=0.1)
        assert np.all((T >= 0.0) & (T <= 1.0))

    def test_gaussian_small_coherence_strong_suppression(self):
        """Very small coherence scale → T_ℓ → 0 at large ℓ."""
        T = birefringence_transfer_function(np.array([1000]), model="gaussian",
                                             coherence_scale_mpc=0.01)
        assert T[0] < 0.01

    def test_gaussian_large_coherence_near_one(self):
        """Very large (but finite) coherence scale → T_ℓ ≈ 1 for all ℓ.

        sigma_coh = chi_star / coherence_scale_mpc; at 1e8 Mpc the suppression
        is < 1% even at ℓ = 1000.
        """
        T = birefringence_transfer_function(self._ELLS, model="gaussian",
                                             coherence_scale_mpc=1e8)
        assert np.all(T > 0.99)

    def test_unknown_model_raises_value_error(self):
        with pytest.raises(ValueError):
            birefringence_transfer_function(self._ELLS, model="faraday")

    def test_coherent_model_is_ul_axion_limit(self):
        """coherent = UL-axion limit, confirmed by T_ℓ = 1 for all ℓ."""
        T = birefringence_transfer_function(self._ELLS, model="coherent")
        assert np.all(T == 1.0)


# ===========================================================================
# 11. propagate_primordial_amplitude  (T_ℓ inversion)
# ===========================================================================

class TestPropagatePrimordialAmplitude:
    """Invert the T_ℓ chain: required primordial β from observed β."""

    def _make_c_ee(self):
        """Quick C_EE for 5 multipoles."""
        return np.array([1e-14, 2e-14, 3e-14, 2e-14, 1e-14])

    def test_coherent_model_no_enhancement(self):
        """T_ℓ = 1 → β_primordial = β_obs (no extra amplitude needed)."""
        T    = np.ones(5)
        C_EE = self._make_c_ee()
        res  = propagate_primordial_amplitude(0.006, T, C_EE)
        assert res["required_beta_primordial"] == pytest.approx(0.006, rel=1e-9)

    def test_suppressed_model_enhances_primordial(self):
        """T_ℓ = 0.5 → β_primordial = 2 × β_obs."""
        T    = np.full(5, 0.5)
        C_EE = self._make_c_ee()
        res  = propagate_primordial_amplitude(0.006, T, C_EE)
        assert res["required_beta_primordial"] == pytest.approx(0.012, rel=1e-9)

    def test_returns_required_keys(self):
        res = propagate_primordial_amplitude(0.006, np.ones(5), self._make_c_ee())
        for key in ("beta_obs_rad", "T_eff", "required_beta_primordial",
                    "suppression_factor", "is_coherent_limit",
                    "no_extra_amplitude_needed", "amplitude_enhancement"):
            assert key in res, f"Missing key: {key}"

    def test_t_eff_is_weighted_mean(self):
        """T_eff = Σ(T_ℓ C_EE) / Σ(C_EE)."""
        T    = np.array([0.8, 0.6, 0.4, 0.6, 0.8])
        C_EE = self._make_c_ee()
        res  = propagate_primordial_amplitude(0.006, T, C_EE)
        expected_T_eff = np.sum(T * C_EE) / np.sum(C_EE)
        assert res["T_eff"] == pytest.approx(expected_T_eff, rel=1e-10)

    def test_coherent_limit_flag_true_for_ones(self):
        """is_coherent_limit = True when T_eff ≈ 1."""
        res = propagate_primordial_amplitude(0.006, np.ones(5), self._make_c_ee())
        assert res["is_coherent_limit"] is True
        assert res["no_extra_amplitude_needed"] is True

    def test_coherent_limit_flag_false_for_half(self):
        """is_coherent_limit = False when T_eff = 0.5."""
        res = propagate_primordial_amplitude(0.006, np.full(5, 0.5), self._make_c_ee())
        assert res["is_coherent_limit"] is False

    def test_amplitude_enhancement_is_one_over_t_eff(self):
        T    = np.full(5, 0.4)
        C_EE = self._make_c_ee()
        res  = propagate_primordial_amplitude(0.006, T, C_EE)
        assert res["amplitude_enhancement"] == pytest.approx(1.0 / 0.4, rel=1e-9)

    def test_zero_c_ee_gives_t_eff_one(self):
        """Zero-weight C_EE → T_eff = 1 (no suppression by convention)."""
        T    = np.full(5, 0.5)
        C_EE = np.zeros(5)
        res  = propagate_primordial_amplitude(0.006, T, C_EE)
        assert res["T_eff"] == pytest.approx(1.0)

    def test_beta_obs_echoed(self):
        res = propagate_primordial_amplitude(0.006, np.ones(5), self._make_c_ee())
        assert res["beta_obs_rad"] == pytest.approx(0.006)

    def test_suppression_factor_equals_t_eff(self):
        T    = np.full(5, 0.7)
        C_EE = self._make_c_ee()
        res  = propagate_primordial_amplitude(0.006, T, C_EE)
        assert res["suppression_factor"] == pytest.approx(res["T_eff"])


# ===========================================================================
# 12. End-to-end LiteBIRD falsification pipeline
# ===========================================================================

class TestLiteBIRDFalsificationPipeline:
    """Integration test: full pipeline from β₀ → C_TB[ℓ, ν] → falsification.

    This is the purpose-built test that confirms the TB/EB spectra are
    LiteBIRD-testable.  The decisive observable is:

        C_TB(ν₁) / C_TB(ν₂) = 1   (achromatic UL-axion model)

    measured across the three LiteBIRD CMB bands: 93, 145, 220 GHz.
    """

    _NU_LB  = [93.0, 145.0, 220.0]   # LiteBIRD representative bands
    _ELLS   = [10, 50, 100, 200, 500, 1000]
    _N_K    = 400

    @classmethod
    def _run(cls, achromatic=True):
        return tb_eb_spectrum(
            ells=cls._ELLS,
            nu_array=cls._NU_LB,
            beta_0=_BETA,
            ns=_NS,
            n_k=cls._N_K,
            frequency_achromatic=achromatic,
        )

    def test_tb_signal_amplitude_above_noise_floor(self):
        """C_TB amplitude is non-trivially large (| C_TB / C_TE | = 2 β)."""
        out   = self._run()
        ratio = np.abs(out["C_TB"][:, 0]) / np.abs(out["C_TE"])
        # 2β ≈ 0.012, so ratio should be in the correct order of magnitude
        assert np.all(ratio == pytest.approx(2.0 * _BETA, rel=1e-10))

    def test_achromaticity_all_band_pairs(self):
        """All LiteBIRD band-pair ratios of C_TB equal 1 in the achromatic model."""
        out = self._run(achromatic=True)
        for i in range(len(self._NU_LB)):
            for j in range(i + 1, len(self._NU_LB)):
                ratio = out["C_TB"][:, i] / out["C_TB"][:, j]
                assert np.allclose(ratio, 1.0, rtol=1e-12), (
                    f"Achromaticity broken for ν={self._NU_LB[i]}/{self._NU_LB[j]} GHz"
                )

    def test_faraday_distinguishable_from_achromatic(self):
        """Faraday model differs from achromatic by (ν₂/ν₁)²  — LiteBIRD can tell apart."""
        out_ach  = self._run(achromatic=True)
        out_far  = self._run(achromatic=False)
        # 93 vs 220 GHz: expected Faraday ratio = (220/93)² ≈ 5.60
        i93  = self._NU_LB.index(93.0)
        i220 = self._NU_LB.index(220.0)
        ratio_far = out_far["C_TB"][:, i93] / out_far["C_TB"][:, i220]
        expected  = (220.0 / 93.0) ** 2
        assert np.allclose(ratio_far, expected, rtol=1e-10)
        # Achromatic ratio is 1, dispersive ratio is ~5.6 — clearly distinguishable
        assert np.all(np.abs(ratio_far - 1.0) > 4.0)

    def test_eb_signal_structure(self):
        """C_EB ≥ 0 at all ℓ and ν (C_EE ≥ 0, β > 0 → 2β C_EE ≥ 0)."""
        out = self._run()
        assert np.all(out["C_EB"] >= 0.0)

    def test_transfer_ell_coherent_consistent_with_propagate(self):
        """Coherent T_ℓ = 1 → propagate_primordial_amplitude returns T_eff = 1."""
        out  = self._run()
        T    = birefringence_transfer_function(np.array(self._ELLS), model="coherent")
        C_EE = out["C_EE"]
        res  = propagate_primordial_amplitude(_BETA, T, C_EE)
        assert res["is_coherent_limit"]
        assert res["T_eff"] == pytest.approx(1.0, rel=1e-10)

    def test_litebird_sensitivity_level_detectable(self):
        """Predicted β ≈ 0.006 rad gives C_EB/C_EE = 2β ≈ 1.2% — above LiteBIRD noise.

        LiteBIRD targets σ_β ≈ 0.02° ≈ 3.5e-4 rad, so the 3σ detection limit
        is ~1e-3 rad.  Our β ≈ 6e-3 rad is ~17σ above noise — easily detectable.
        """
        out  = self._run()
        # C_EB[:, 0] / C_EE = 2 * beta_nu = 2 * _BETA for achromatic model
        ratio = out["C_EB"][:, 0] / out["C_EE"]
        assert np.allclose(ratio, 2.0 * _BETA, rtol=1e-10)
        # Confirm the ratio is >> LiteBIRD 3σ detection threshold (2 × 3σ_β ≈ 2e-3)
        assert np.all(ratio > 2.0 * 3.0 * 3.5e-4)
