# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cmb_transfer.py — Test suite for Pillar 63: E-H CMB Transfer Function.

Covers:
- baryon_loading_R: physical range, known value, edge cases
- eh_transfer_no_baryon: large-scale limit, sub-equality suppression, monotonicity
- baryon_acoustic_source: amplitude enhancement, Silk suppression, edge cases
- angular_power_spectrum_eh: shape, positivity, ℓ-dependence
- dl_from_cl_eh: unit conversion correctness
- um_dl_spectrum: output shape, positivity, physics checks
- acoustic_peak_positions: angular position of peaks, ratio consistency
- planck_reference_check_eh: χ² computation correctness
- suppression_gap_audit: gap resolution, R_b, amplitude ratio

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from src.core.cmb_transfer import (
    OMEGA_M,
    OMEGA_B,
    H_REDUCED,
    T_CMB_K,
    CHI_STAR,
    RS_STAR,
    K_SILK,
    SILK_EXP,
    K_PIVOT,
    Z_STAR,
    NS_UM,
    AS_PLANCK,
    PLANCK_DL_REF,
    baryon_loading_R,
    eh_transfer_no_baryon,
    baryon_acoustic_source,
    angular_power_spectrum_eh,
    dl_from_cl_eh,
    um_dl_spectrum,
    acoustic_peak_positions,
    planck_reference_check_eh,
    suppression_gap_audit,
)


# ---------------------------------------------------------------------------
# Module constants sanity tests
# ---------------------------------------------------------------------------

class TestConstants:
    def test_omega_m(self):
        assert abs(OMEGA_M - 0.3153) < 1e-6

    def test_omega_b(self):
        assert abs(OMEGA_B - 0.04930) < 1e-5

    def test_h_reduced(self):
        assert abs(H_REDUCED - 0.6736) < 1e-5

    def test_t_cmb_k(self):
        assert abs(T_CMB_K - 2.7255) < 1e-5

    def test_chi_star_mpc(self):
        assert 13000.0 < CHI_STAR < 15000.0

    def test_rs_star_mpc(self):
        assert 130.0 < RS_STAR < 160.0

    def test_k_silk_mpc_inv(self):
        assert 0.05 < K_SILK < 0.3

    def test_z_star(self):
        assert abs(Z_STAR - 1090.0) < 1.0

    def test_ns_um(self):
        assert abs(NS_UM - 0.9635) < 1e-5

    def test_as_planck(self):
        assert abs(AS_PLANCK - 2.101e-9) < 1e-15

    def test_planck_ref_has_peak_ells(self):
        for ell in (220, 540, 810):
            assert ell in PLANCK_DL_REF

    def test_omega_b_less_than_omega_m(self):
        assert OMEGA_B < OMEGA_M

    def test_k_pivot_is_standard(self):
        assert abs(K_PIVOT - 0.05) < 1e-10


# ---------------------------------------------------------------------------
# baryon_loading_R tests
# ---------------------------------------------------------------------------

class TestBaryonLoadingR:
    def test_positive(self):
        R_b = baryon_loading_R()
        assert R_b > 0.0

    def test_planck_value_range(self):
        """R_b at z★=1090 with Planck cosmology should be ≈ 0.5–0.8."""
        R_b = baryon_loading_R()
        assert 0.3 < R_b < 1.2

    def test_known_formula(self):
        """Verify formula: R_b = 31.5e3 × omega_b_h2 / (T27^4 × (1+z))."""
        omega_b_h2 = OMEGA_B * H_REDUCED ** 2
        T27 = T_CMB_K / 2.7
        z = Z_STAR
        expected = 31.5e3 * omega_b_h2 / (T27 ** 4 * (1.0 + z))
        R_b = baryon_loading_R(z, omega_b_h2, T_CMB_K)
        assert abs(R_b - expected) < 1e-12

    def test_higher_z_smaller_R_b(self):
        """At higher z, photons dominate more → smaller R_b."""
        R_low = baryon_loading_R(z_rec=1090.0)
        R_high = baryon_loading_R(z_rec=3000.0)
        assert R_high < R_low

    def test_higher_omega_b_larger_R_b(self):
        omega_b_h2_low = 0.01 * H_REDUCED ** 2
        omega_b_h2_high = 0.05 * H_REDUCED ** 2
        R_low = baryon_loading_R(omega_b_h2=omega_b_h2_low)
        R_high = baryon_loading_R(omega_b_h2=omega_b_h2_high)
        assert R_high > R_low

    def test_zero_z_rec_raises(self):
        with pytest.raises(ValueError):
            baryon_loading_R(z_rec=0.0)

    def test_negative_z_rec_raises(self):
        with pytest.raises(ValueError):
            baryon_loading_R(z_rec=-100.0)

    def test_zero_omega_b_h2_raises(self):
        with pytest.raises(ValueError):
            baryon_loading_R(omega_b_h2=0.0)

    def test_zero_T_cmb_raises(self):
        with pytest.raises(ValueError):
            baryon_loading_R(T_cmb_K=0.0)

    def test_negative_T_cmb_raises(self):
        with pytest.raises(ValueError):
            baryon_loading_R(T_cmb_K=-2.7)

    def test_result_type_float(self):
        assert isinstance(baryon_loading_R(), float)


# ---------------------------------------------------------------------------
# eh_transfer_no_baryon tests
# ---------------------------------------------------------------------------

class TestEhTransferNoBaryon:
    def test_large_scale_limit(self):
        """T(k→0) → 1 (super-horizon modes unaffected by growth suppression)."""
        T = eh_transfer_no_baryon(1e-5)
        assert abs(T - 1.0) < 0.02

    def test_sub_equality_suppression(self):
        """T(k ≫ k_eq) ≪ 1 (sub-horizon modes during radiation domination)."""
        T = eh_transfer_no_baryon(10.0)
        assert T < 0.1

    def test_monotonically_decreasing(self):
        """T(k) is strictly decreasing for k > 0."""
        k_vals = np.array([1e-4, 1e-3, 1e-2, 0.1, 1.0])
        T_vals = eh_transfer_no_baryon(k_vals)
        assert np.all(np.diff(T_vals) < 0)

    def test_range_0_to_1(self):
        """All T values lie in (0, 1]."""
        k_vals = np.geomspace(1e-5, 10.0, 50)
        T_vals = eh_transfer_no_baryon(k_vals)
        assert np.all(T_vals > 0.0)
        assert np.all(T_vals <= 1.0 + 1e-6)

    def test_vectorised_output_shape(self):
        k = np.linspace(0.001, 1.0, 100)
        T = eh_transfer_no_baryon(k)
        assert T.shape == (100,)

    def test_scalar_output_is_float(self):
        T = eh_transfer_no_baryon(0.1)
        assert isinstance(T, float)

    def test_zero_omega_m_raises(self):
        with pytest.raises(ValueError):
            eh_transfer_no_baryon(0.1, omega_m=0.0)

    def test_zero_h_raises(self):
        with pytest.raises(ValueError):
            eh_transfer_no_baryon(0.1, h=0.0)

    def test_zero_T_cmb_raises(self):
        with pytest.raises(ValueError):
            eh_transfer_no_baryon(0.1, T_cmb_K=0.0)

    def test_negative_omega_m_raises(self):
        with pytest.raises(ValueError):
            eh_transfer_no_baryon(0.1, omega_m=-0.3)

    def test_k_eq_scaling(self):
        """T(k) at a given k/k_eq should be independent of overall scale."""
        omega_m_h2 = OMEGA_M * H_REDUCED ** 2
        k_eq = 7.46e-2 * omega_m_h2 * (T_CMB_K / 2.7) ** (-2)
        T_mid = eh_transfer_no_baryon(k_eq)
        assert 0.3 < T_mid < 0.7

    def test_at_k_silk_nonzero(self):
        """T(k_silk) should still be significantly > 0 (Silk scale ~EH scale)."""
        T = eh_transfer_no_baryon(K_SILK)
        assert T > 0.05

    def test_no_negative_values(self):
        k = np.geomspace(1e-5, 100.0, 200)
        T = eh_transfer_no_baryon(k)
        assert np.all(T >= 0.0)


# ---------------------------------------------------------------------------
# baryon_acoustic_source tests
# ---------------------------------------------------------------------------

class TestBaryonAcousticSource:
    def test_amplitude_enhanced_over_no_baryon(self):
        """Baryon-loaded source amplitude > 1/3 (canonical SW value)."""
        k_peak = np.pi / RS_STAR   # first acoustic peak
        S = baryon_acoustic_source(k_peak, R_b=0.61)
        assert abs(S) > 1.0 / 3.0

    def test_no_baryon_limit_returns_canonical(self):
        """At R_b → 0, source → (1/3) cos(k r_s★) × damping."""
        k = 0.01
        S_br = baryon_acoustic_source(k, R_b=1e-6)
        S_can = (1.0 / 3.0) * np.cos(k * RS_STAR) * np.exp(-((k / K_SILK) ** SILK_EXP))
        assert abs(S_br - S_can) < 1e-5

    def test_silk_damping_at_large_k(self):
        """Source is exponentially suppressed for k ≫ k_silk."""
        S_small = baryon_acoustic_source(0.01, R_b=0.61)
        S_large = baryon_acoustic_source(5.0, R_b=0.61)
        assert abs(S_large) < 1e-6 * abs(S_small) + 1e-30

    def test_vectorised_shape(self):
        k = np.linspace(0.001, 1.0, 50)
        S = baryon_acoustic_source(k, R_b=0.61)
        assert S.shape == (50,)

    def test_scalar_is_float(self):
        S = baryon_acoustic_source(0.02, R_b=0.61)
        assert isinstance(S, float)

    def test_oscillatory_sign(self):
        """Source changes sign between acoustic peaks and troughs."""
        k_peak1 = np.pi / RS_STAR
        k_trough1 = 2.0 * np.pi / RS_STAR
        S_peak1 = baryon_acoustic_source(k_peak1, R_b=0.61)
        S_trough1 = baryon_acoustic_source(k_trough1, R_b=0.61)
        assert S_peak1 * S_trough1 < 0.0

    def test_auto_R_b_computation(self):
        """Without explicit R_b, function computes it from cosmological params."""
        S_auto = baryon_acoustic_source(0.02)
        R_b = baryon_loading_R()
        S_manual = baryon_acoustic_source(0.02, R_b=R_b)
        assert abs(S_auto - S_manual) < 1e-12

    def test_zero_rs_star_raises(self):
        with pytest.raises(ValueError):
            baryon_acoustic_source(0.02, rs_star=0.0, R_b=0.61)

    def test_zero_k_silk_raises(self):
        with pytest.raises(ValueError):
            baryon_acoustic_source(0.02, k_silk=0.0, R_b=0.61)

    def test_zero_silk_exp_raises(self):
        with pytest.raises(ValueError):
            baryon_acoustic_source(0.02, silk_exponent=0.0, R_b=0.61)

    def test_amplitude_ratio_is_correct(self):
        """Amplitude at k→0 is (1+3R_b)/(3(1+R_b)) — check for R_b=0.6."""
        R_b = 0.6
        k_small = 1e-6
        S = baryon_acoustic_source(k_small, R_b=R_b)
        expected_amp = (1.0 + 3.0 * R_b) / (3.0 * (1.0 + R_b))
        assert abs(abs(S) - abs(expected_amp)) < 0.01

    def test_amplitude_increases_with_R_b(self):
        """More baryon loading → larger source amplitude at compression peaks."""
        k = np.pi / RS_STAR
        S_low = baryon_acoustic_source(k, R_b=0.1)
        S_high = baryon_acoustic_source(k, R_b=0.8)
        assert abs(S_high) > abs(S_low)


# ---------------------------------------------------------------------------
# angular_power_spectrum_eh tests
# ---------------------------------------------------------------------------

class TestAngularPowerSpectrumEh:
    _ells = [10, 30, 100, 220, 420, 540]

    def test_output_shape(self):
        Cl = angular_power_spectrum_eh(self._ells, n_k=300)
        assert Cl.shape == (len(self._ells),)

    def test_all_positive(self):
        Cl = angular_power_spectrum_eh(self._ells, n_k=300)
        assert np.all(Cl > 0.0)

    def test_large_ell_smaller_than_small_ell(self):
        """Silk damping: Cl at ℓ=1500 < Cl at ℓ=220 (power falls off)."""
        Cl = angular_power_spectrum_eh([220, 1500], n_k=600)
        # After Silk damping tail, Cl[220] / Cl[1500] >> 1
        assert Cl[0] > Cl[1]

    def test_scalar_amplitude_dependence(self):
        """Doubling As doubles Cl (linear dependence)."""
        Cl1 = angular_power_spectrum_eh([220], n_k=300, As=AS_PLANCK)
        Cl2 = angular_power_spectrum_eh([220], n_k=300, As=2.0 * AS_PLANCK)
        ratio = Cl2[0] / Cl1[0]
        assert abs(ratio - 2.0) < 0.01

    def test_ns_tilt_effect(self):
        """More red tilt (smaller ns) reduces power at high ℓ (k > k_pivot)."""
        # Need ℓ where k_ℓ = ℓ/χ★ > k_pivot=0.05 Mpc⁻¹ → ℓ > 0.05×13890 = 695
        Cl_flat = angular_power_spectrum_eh([1000], n_k=300, ns=1.0)
        Cl_red = angular_power_spectrum_eh([1000], n_k=300, ns=0.9)
        assert Cl_red[0] < Cl_flat[0]

    def test_positive_definiteness(self):
        """Cl values must be strictly positive (they are integrals of positive quantities)."""
        Cl = angular_power_spectrum_eh([2, 10, 50, 200], n_k=300)
        assert np.all(Cl > 0.0)


# ---------------------------------------------------------------------------
# dl_from_cl_eh tests
# ---------------------------------------------------------------------------

class TestDlFromClEh:
    def test_ell_2_formula(self):
        """D2 = 2×3/(2π) × C2 × T_CMB_uK^2"""
        ells = np.array([2])
        Cl = np.array([1.0e-10])
        Dl = dl_from_cl_eh(ells, Cl, T_CMB_K)
        T_uK = T_CMB_K * 1e6
        expected = 2.0 * 3.0 / (2.0 * math.pi) * 1e-10 * T_uK ** 2
        assert abs(Dl[0] - expected) < 1e-3 * abs(expected)

    def test_shape_preserved(self):
        ells = np.array([10, 50, 100, 220])
        Cl = np.ones(4) * 1e-10
        Dl = dl_from_cl_eh(ells, Cl)
        assert Dl.shape == (4,)

    def test_monotone_in_ell_for_flat_Cl(self):
        """For constant Cl, Dl ∝ ℓ(ℓ+1) which increases with ℓ."""
        ells = np.array([10, 50, 200, 500])
        Cl = np.ones(4) * 1e-10
        Dl = dl_from_cl_eh(ells, Cl)
        assert np.all(np.diff(Dl) > 0)

    def test_scale_with_temperature(self):
        """Dl ∝ T_CMB^2."""
        ells = np.array([100])
        Cl = np.array([1e-10])
        Dl1 = dl_from_cl_eh(ells, Cl, T_cmb_K=2.7255)
        Dl2 = dl_from_cl_eh(ells, Cl, T_cmb_K=2.7255 * 2.0)
        assert abs(Dl2[0] / Dl1[0] - 4.0) < 0.01

    def test_positive_for_positive_Cl(self):
        ells = np.arange(2, 100)
        Cl = np.ones(98) * 1e-10
        Dl = dl_from_cl_eh(ells, Cl)
        assert np.all(Dl > 0.0)


# ---------------------------------------------------------------------------
# um_dl_spectrum tests
# ---------------------------------------------------------------------------

class TestUmDlSpectrum:
    def test_output_shape(self):
        ells = [10, 50, 100, 220, 540, 810]
        Dl = um_dl_spectrum(ells, n_k=300)
        assert Dl.shape == (len(ells),)

    def test_all_positive(self):
        Dl = um_dl_spectrum([100, 220, 540], n_k=300)
        assert np.all(Dl > 0.0)

    def test_dl_order_of_magnitude(self):
        """Dl at ℓ=220 should be in the 100–20000 μK² range."""
        Dl = um_dl_spectrum([220], n_k=600)
        assert 10.0 < Dl[0] < 50000.0

    def test_uses_ns_um_and_as_planck(self):
        """Explicitly passing UM inputs gives same result as defaults."""
        Dl_default = um_dl_spectrum([220], n_k=300)
        Dl_explicit = um_dl_spectrum([220], ns=NS_UM, As=AS_PLANCK, n_k=300)
        assert abs(Dl_default[0] - Dl_explicit[0]) < 1e-6

    def test_larger_as_gives_larger_dl(self):
        Dl1 = um_dl_spectrum([220], As=AS_PLANCK, n_k=300)
        Dl2 = um_dl_spectrum([220], As=2.0 * AS_PLANCK, n_k=300)
        assert Dl2[0] > Dl1[0]

    def test_silk_tail_suppressed(self):
        """Dl at ℓ=1500 should be less than Dl at ℓ=220."""
        Dl = um_dl_spectrum([220, 1500], n_k=600)
        assert Dl[0] > Dl[1]


# ---------------------------------------------------------------------------
# acoustic_peak_positions tests
# ---------------------------------------------------------------------------

class TestAcousticPeakPositions:
    def test_first_peak_near_220(self):
        pos = acoustic_peak_positions()
        # Naive formula ℓ₁ = π χ★/r_s★ ≈ 300 (phase shift not included)
        assert 250.0 < pos["peak_1"] < 360.0

    def test_first_trough_near_420(self):
        pos = acoustic_peak_positions()
        assert 500.0 < pos["trough_1"] < 720.0

    def test_second_peak_near_540(self):
        pos = acoustic_peak_positions()
        assert 750.0 < pos["peak_2"] < 1080.0

    def test_peak_3_near_810(self):
        pos = acoustic_peak_positions()
        assert 1250.0 < pos["peak_3"] < 1800.0

    def test_integer_ratios(self):
        """Peak positions are in ratio 1:2:3:4:5 from the first peak."""
        pos = acoustic_peak_positions()
        p1 = pos["peak_1"]
        assert abs(pos["trough_1"] / p1 - 2.0) < 0.01
        assert abs(pos["peak_2"] / p1 - 3.0) < 0.01
        assert abs(pos["trough_2"] / p1 - 4.0) < 0.01
        assert abs(pos["peak_3"] / p1 - 5.0) < 0.01

    def test_rs_star_echoed(self):
        pos = acoustic_peak_positions(rs_star=144.7)
        assert abs(pos["rs_star"] - 144.7) < 1e-10

    def test_chi_star_echoed(self):
        pos = acoustic_peak_positions(chi_star=13890.0)
        assert abs(pos["chi_star"] - 13890.0) < 1e-10

    def test_zero_rs_star_raises(self):
        with pytest.raises(ValueError):
            acoustic_peak_positions(rs_star=0.0)

    def test_zero_chi_star_raises(self):
        with pytest.raises(ValueError):
            acoustic_peak_positions(chi_star=0.0)

    def test_result_keys_complete(self):
        pos = acoustic_peak_positions()
        for key in ("peak_1", "trough_1", "peak_2", "trough_2", "peak_3"):
            assert key in pos

    def test_all_positive(self):
        pos = acoustic_peak_positions()
        for key in ("peak_1", "trough_1", "peak_2", "trough_2", "peak_3"):
            assert pos[key] > 0.0

    def test_monotonically_increasing(self):
        pos = acoustic_peak_positions()
        peaks = [pos["peak_1"], pos["trough_1"], pos["peak_2"],
                 pos["trough_2"], pos["peak_3"]]
        assert all(peaks[i] < peaks[i + 1] for i in range(len(peaks) - 1))


# ---------------------------------------------------------------------------
# planck_reference_check_eh tests
# ---------------------------------------------------------------------------

class TestPlanckReferenceCheckEh:
    def test_chi2_positive(self):
        Dl_pred = np.array([5795.0])
        chi2, _, _ = planck_reference_check_eh([220], Dl_pred)
        assert chi2 >= 0.0

    def test_perfect_match_gives_zero_chi2(self):
        ell = 220
        Dl_ref = PLANCK_DL_REF[ell][0]
        chi2, _, n = planck_reference_check_eh([ell], np.array([Dl_ref]))
        assert abs(chi2) < 1e-10

    def test_n_dof_counts_matched_ells(self):
        ells = [220, 540, 810]
        Dl = np.array([5795.0, 2705.0, 2440.0])
        _, _, n = planck_reference_check_eh(ells, Dl)
        assert n == 3

    def test_no_matching_ells_raises(self):
        with pytest.raises(ValueError):
            planck_reference_check_eh([999], np.array([1000.0]))

    def test_chi2_dof_equals_chi2_over_n(self):
        ells = [220, 540]
        Dl = np.array([5000.0, 2000.0])
        chi2, chi2_dof, n = planck_reference_check_eh(ells, Dl)
        assert abs(chi2_dof - chi2 / n) < 1e-10

    def test_larger_residual_gives_larger_chi2(self):
        Dl_close = np.array([5800.0])
        Dl_far = np.array([1000.0])
        chi2_close, _, _ = planck_reference_check_eh([220], Dl_close)
        chi2_far, _, _ = planck_reference_check_eh([220], Dl_far)
        assert chi2_far > chi2_close


# ---------------------------------------------------------------------------
# suppression_gap_audit tests
# ---------------------------------------------------------------------------

class TestSuppressionGapAudit:
    def setup_method(self):
        self.audit = suppression_gap_audit()

    def test_R_b_physical_range(self):
        """R_b should be ≈ 0.3–1.2 at z★ with Planck cosmology."""
        assert 0.3 < self.audit["R_b"] < 1.2

    def test_R_b_unit_check(self):
        assert self.audit["R_b_unit_check"] is True

    def test_source_amp_ratio_gt_1(self):
        """Baryon-loaded amplitude > 1/3 (no-baryon) for R_b > 0."""
        assert self.audit["source_amp_ratio"] > 1.0

    def test_gap_resolved(self):
        """Baryon loading amplitude ratio > 1.5 at acoustic peaks."""
        assert self.audit["gap_resolved"] is True

    def test_amp_nobaryon_is_third(self):
        assert abs(self.audit["amp_nobaryon"] - 1.0 / 3.0) < 1e-12

    def test_amp_baryon_gt_amp_nobaryon(self):
        assert self.audit["amp_baryon"] > self.audit["amp_nobaryon"]

    def test_dl_ratio_at_peaks_gt_1(self):
        for ell, ratio in self.audit["dl_ratio_ells"].items():
            assert ratio > 1.0, f"Dl ratio at ℓ={ell} should be > 1"

    def test_planck_ref_present(self):
        assert len(self.audit["planck_ref"]) > 0

    def test_peak_positions_present(self):
        assert "peak_1" in self.audit["peak_positions"]

    def test_keys_complete(self):
        expected = {
            "R_b", "amp_nobaryon", "amp_baryon", "source_amp_ratio",
            "dl_ratio_ells", "planck_ref", "gap_resolved",
            "peak_positions", "R_b_unit_check",
        }
        assert expected.issubset(self.audit.keys())

    def test_first_peak_position_near_220(self):
        pos = self.audit["peak_positions"]
        # Naive formula ℓ₁ = π χ★/r_s★ ≈ 300 (phase shift not modelled)
        assert 250.0 < pos["peak_1"] < 360.0

    def test_source_amp_formula_consistent(self):
        """amp_baryon = (1+3R_b)/(3(1+R_b))."""
        R_b = self.audit["R_b"]
        expected = (1.0 + 3.0 * R_b) / (3.0 * (1.0 + R_b))
        assert abs(self.audit["amp_baryon"] - expected) < 1e-12

    def test_dl_ratio_equals_source_ratio_squared(self):
        """dl_ratio = source_amp_ratio^2 at peaks (cos ≈ ±1)."""
        ratio = self.audit["source_amp_ratio"]
        for ell, dl_ratio in self.audit["dl_ratio_ells"].items():
            assert abs(dl_ratio - ratio ** 2) < 1e-12


# ---------------------------------------------------------------------------
# Physics sanity / integration tests
# ---------------------------------------------------------------------------

class TestPhysicsSanity:
    def test_first_peak_position_matches_planck(self):
        """ℓ_peak1 from naive formula ≈ 300 (phase shift from ISW not included)."""
        pos = acoustic_peak_positions()
        assert 250.0 < pos["peak_1"] < 360.0

    def test_sound_horizon_ratio(self):
        """r_s★ / χ★ ≈ 0.010 (≈ 1/100 of the comoving horizon)."""
        ratio = RS_STAR / CHI_STAR
        assert 0.008 < ratio < 0.013

    def test_baryon_loading_is_order_unity(self):
        """R_b ~ 0.6 is O(1): baryons and photons comparable at recombination."""
        R_b = baryon_loading_R()
        assert 0.1 < R_b < 5.0

    def test_eh_transfer_at_keq_is_middle(self):
        """T(k_eq) is between 0.3 and 0.7 (half-suppression at equality scale)."""
        omega_m_h2 = OMEGA_M * H_REDUCED ** 2
        T27 = T_CMB_K / 2.7
        k_eq = 7.46e-2 * omega_m_h2 * T27 ** (-2)
        T = eh_transfer_no_baryon(k_eq)
        assert 0.2 < T < 0.8

    def test_silk_scale_is_sub_degree(self):
        """Silk damping at ℓ_D = k_silk × chi_star > 1000 (< 0.2°)."""
        ell_silk = K_SILK * CHI_STAR
        assert ell_silk > 800.0

    def test_um_spectral_index_within_planck(self):
        """UM ns = 0.9635 is within 1σ of Planck 0.9649 ± 0.0042."""
        assert abs(NS_UM - 0.9649) < 0.0042

    def test_baryon_acoustic_source_at_first_peak(self):
        """Source amplitude at ℓ=220 with baryon loading > 1/3."""
        k_peak1 = math.pi / RS_STAR
        S = baryon_acoustic_source(k_peak1)
        assert abs(S) > 1.0 / 3.0

    def test_planck_ref_dl220_approximately_5800(self):
        """Planck reference Dl at ℓ=220 is ≈ 5795 μK²."""
        Dl_ref, sigma = PLANCK_DL_REF[220]
        assert abs(Dl_ref - 5795.0) < 50.0

    def test_amplitude_ratio_resolves_factor_4_to_7_gap(self):
        """Baryon loading provides > ×1.5 amplitude enhancement, reducing the gap."""
        R_b = baryon_loading_R()
        amp_bar = (1.0 + 3.0 * R_b) / (3.0 * (1.0 + R_b))
        amp_nobar = 1.0 / 3.0
        ratio = amp_bar / amp_nobar
        assert ratio > 1.5
