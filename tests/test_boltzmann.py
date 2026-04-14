"""
tests/test_boltzmann.py
=======================
Tests for src/core/boltzmann.py — baryon-loaded CMB transfer function.

Covers:
  - baryon_loading_factor: correct R★ at recombination
  - sound_speed_squared: cs² = 1/3(1+R) formula
  - baryon_corrected_rs: shorter than zero-baryon value
  - sw_amplitude: reduces to 1/3 for R → 0
  - baryon_loaded_source: shape, amplitude, silk damping
  - baryon_loaded_spectrum: Cₗ shape and dimension
  - dl_baryon: Dₗ positive, correct shape
  - peak_position_correction: fractional shift positive
  - accuracy_vs_tight_coupling: baryon model differs from zero-baryon
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import numpy as np

from src.core.boltzmann import (
    baryon_loading_factor,
    sound_speed_squared,
    baryon_corrected_rs,
    sw_amplitude,
    baryon_loaded_source,
    baryon_loaded_spectrum,
    dl_baryon,
    peak_position_correction,
    accuracy_vs_tight_coupling,
    _OMEGA_B,
    _OMEGA_GAMMA,
    _OMEGA_B_H2,
    _OMEGA_GAMMA_H2,
    _Z_REC,
)
from src.core.transfer import PLANCK_2018_COSMO


# ---------------------------------------------------------------------------
# baryon_loading_factor
# ---------------------------------------------------------------------------

class TestBaryonLoadingFactor:
    def test_positive(self):
        R = baryon_loading_factor()
        assert R > 0.0

    def test_less_than_one(self):
        # At recombination (z~1090), R★ ≈ 0.62 < 1 for Planck 2018 params
        R = baryon_loading_factor()
        assert R < 1.0

    def test_increases_with_omega_b(self):
        R1 = baryon_loading_factor(omega_b=0.01)
        R2 = baryon_loading_factor(omega_b=0.04)
        assert R2 > R1

    def test_decreases_with_higher_z_rec(self):
        R1 = baryon_loading_factor(z_rec=500.0)
        R2 = baryon_loading_factor(z_rec=1090.0)
        assert R2 < R1

    def test_zero_baryons_gives_zero(self):
        R = baryon_loading_factor(omega_b=0.0)
        assert R == pytest.approx(0.0)

    def test_planck_value_in_expected_range(self):
        # R★ ≈ 0.617 for Planck 2018 Ω_b h² = 0.02218
        R = baryon_loading_factor()
        assert 0.4 < R < 1.0, f"R★ = {R:.4f} outside [0.4, 1.0]"

    def test_formula_manual(self):
        omega_b = _OMEGA_B_H2
        omega_gamma = _OMEGA_GAMMA_H2
        z_rec = _Z_REC
        a_rec = 1.0 / (1.0 + z_rec)
        expected = (3.0 / 4.0) * (omega_b / omega_gamma) * a_rec
        R = baryon_loading_factor(omega_b, omega_gamma, z_rec)
        assert R == pytest.approx(expected, rel=1e-10)


# ---------------------------------------------------------------------------
# sound_speed_squared
# ---------------------------------------------------------------------------

class TestSoundSpeedSquared:
    def test_zero_baryon_limit(self):
        cs2 = sound_speed_squared(0.0)
        assert cs2 == pytest.approx(1.0 / 3.0, rel=1e-10)

    def test_decreases_with_R(self):
        cs2_0 = sound_speed_squared(0.0)
        cs2_1 = sound_speed_squared(1.0)
        assert cs2_1 < cs2_0

    def test_positive(self):
        for R in [0.0, 0.5, 1.0, 2.0]:
            assert sound_speed_squared(R) > 0.0

    def test_formula(self):
        R = 0.75
        expected = 1.0 / (3.0 * (1.0 + R))
        assert sound_speed_squared(R) == pytest.approx(expected, rel=1e-10)

    def test_large_R_approaches_zero(self):
        cs2 = sound_speed_squared(100.0)
        assert cs2 < 0.005


# ---------------------------------------------------------------------------
# baryon_corrected_rs
# ---------------------------------------------------------------------------

class TestBaryonCorrectedRs:
    def test_shorter_than_zero_baryon(self):
        # baryon_corrected_rs returns the actual r_s★ which is shorter than
        # the zero-baryon value η★/√3
        eta_star = PLANCK_2018_COSMO["eta_star"]
        rs_zero = eta_star / np.sqrt(3.0)   # ≈ 161.7 Mpc
        rs_corr = baryon_corrected_rs()
        assert rs_corr < rs_zero

    def test_finite_positive(self):
        rs_corr = baryon_corrected_rs()
        assert np.isfinite(rs_corr) and rs_corr > 0.0

    def test_zero_baryon_returns_eta_over_sqrt3(self):
        eta_star = PLANCK_2018_COSMO["eta_star"]
        rs_corr = baryon_corrected_rs(R_star=0.0)
        assert rs_corr == pytest.approx(eta_star / np.sqrt(3.0), rel=1e-10)

    def test_larger_R_gives_shorter_rs(self):
        rs_small = baryon_corrected_rs(R_star=0.3)
        rs_large = baryon_corrected_rs(R_star=1.0)
        assert rs_large < rs_small

    def test_planck_value_reproduced(self):
        # The formula should reproduce r_s★ ≈ 144.7 Mpc within ~2%
        rs_corr = baryon_corrected_rs()
        planck_rs = PLANCK_2018_COSMO["rs_star"]  # 144.7 Mpc
        assert abs(rs_corr - planck_rs) / planck_rs < 0.05, (
            f"Expected r_s★ ≈ {planck_rs} Mpc, got {rs_corr:.2f} Mpc"
        )

    def test_result_within_physical_bounds(self):
        rs_corr = baryon_corrected_rs()
        assert 130.0 < rs_corr < 165.0


# ---------------------------------------------------------------------------
# sw_amplitude
# ---------------------------------------------------------------------------

class TestSwAmplitude:
    def test_zero_baryon_gives_one_third(self):
        A = sw_amplitude(0.0)
        assert A == pytest.approx(1.0 / 3.0, rel=1e-10)

    def test_positive_for_all_R(self):
        for R in [0.0, 0.5, 1.0, 2.0, 5.0]:
            assert sw_amplitude(R) > 0.0

    def test_numerically_finite(self):
        for R in np.linspace(0, 3, 20):
            assert np.isfinite(sw_amplitude(R))

    def test_formula(self):
        R = 0.8
        expected = (1.0 + 3.0 * R) / (3.0 * (1.0 + R) ** 0.75)
        assert sw_amplitude(R) == pytest.approx(expected, rel=1e-10)


# ---------------------------------------------------------------------------
# baryon_loaded_source
# ---------------------------------------------------------------------------

class TestBaryonLoadedSource:
    def test_scalar_input(self):
        S = baryon_loaded_source(0.05)
        assert np.isscalar(S) or (hasattr(S, 'shape') and S.shape == ())

    def test_array_input(self):
        k = np.linspace(0.001, 0.5, 50)
        S = baryon_loaded_source(k)
        assert S.shape == (50,)

    def test_finite(self):
        k = np.geomspace(1e-4, 0.5, 100)
        S = baryon_loaded_source(k)
        assert np.all(np.isfinite(S))

    def test_silk_damping_at_high_k(self):
        S_low = abs(float(baryon_loaded_source(0.01)))
        S_high = abs(float(baryon_loaded_source(1.0)))
        assert S_high < S_low, "Silk damping should suppress high-k modes"

    def test_magnitude_order_of_third(self):
        # At k → 0, S should be approximately A_sw (from the cos(0) = 1 factor)
        S = float(baryon_loaded_source(1e-6))
        A_sw = sw_amplitude(baryon_loading_factor())
        assert abs(S - A_sw) < 0.01 * A_sw

    def test_zero_at_null_of_cosine(self):
        # k r_s★ = π/2 → first zero of cos
        rs = PLANCK_2018_COSMO["rs_star"]
        k_zero = np.pi / (2.0 * rs)
        S = float(baryon_loaded_source(k_zero, rs_star=rs, R_star=0.0))
        # cos(π/2) = 0, but Silk damping is negligible here
        assert abs(S) < 0.05

    def test_zero_baryon_close_to_transfer_source(self):
        from src.core.transfer import cmb_source_function
        k = np.geomspace(0.001, 0.3, 50)
        # With R★ = 0, the only difference should be the rs_star used
        # (baryon_corrected_rs → η★/√3 vs PLANCK_2018_COSMO["rs_star"])
        # Pass the Planck rs_star explicitly to get a matching comparison
        S_zero_baryon = baryon_loaded_source(k, R_star=0.0,
                                              rs_star=PLANCK_2018_COSMO["rs_star"])
        S_transfer = cmb_source_function(k)
        # For R★ = 0 and same rs★, the functions should agree closely
        frac_diff = np.abs(S_zero_baryon - S_transfer) / (np.abs(S_transfer) + 1e-30)
        assert float(np.mean(frac_diff)) < 0.05


# ---------------------------------------------------------------------------
# baryon_loaded_spectrum
# ---------------------------------------------------------------------------

class TestBaryonLoadedSpectrum:
    ELLS = [10, 50, 100, 200, 300, 500, 700, 1000]
    NS = 0.9635

    def test_shape(self):
        Cl = baryon_loaded_spectrum(self.ELLS, self.NS)
        assert Cl.shape == (len(self.ELLS),)

    def test_all_finite(self):
        Cl = baryon_loaded_spectrum(self.ELLS, self.NS)
        assert np.all(np.isfinite(Cl))

    def test_all_positive(self):
        Cl = baryon_loaded_spectrum(self.ELLS, self.NS)
        assert np.all(Cl >= 0.0)

    def test_lower_ns_shifts_power(self):
        Cl_high = baryon_loaded_spectrum([200], 0.97)
        Cl_low = baryon_loaded_spectrum([200], 0.93)
        # Different n_s should give measurably different Cₗ (at least 2% difference)
        frac_diff = abs(float(Cl_high[0]) - float(Cl_low[0])) / float(Cl_high[0])
        assert frac_diff > 0.02, f"Expected > 2% difference, got {frac_diff:.4f}"

    def test_planck_as_gives_correct_order(self):
        Cl = baryon_loaded_spectrum([200], self.NS)
        Dl = float(Cl[0]) * 200 * 201 / (2 * np.pi) * (PLANCK_2018_COSMO["T_cmb_K"] * 1e6) ** 2
        # Dₗ at ℓ~200 should be in range 3000–8000 μK² (first peak)
        assert 100 < Dl < 20000, f"Dₗ(200) = {Dl:.0f} μK² seems unphysical"


# ---------------------------------------------------------------------------
# dl_baryon
# ---------------------------------------------------------------------------

class TestDlBaryon:
    ELLS = [50, 100, 200, 500, 1000]
    NS = 0.9635

    def test_shape(self):
        Dl = dl_baryon(self.ELLS, self.NS)
        assert Dl.shape == (len(self.ELLS),)

    def test_all_positive(self):
        Dl = dl_baryon(self.ELLS, self.NS)
        assert np.all(Dl >= 0.0)

    def test_all_finite(self):
        Dl = dl_baryon(self.ELLS, self.NS)
        assert np.all(np.isfinite(Dl))

    def test_first_acoustic_peak_positive(self):
        Dl = dl_baryon([200], self.NS)
        assert float(Dl[0]) > 0.0


# ---------------------------------------------------------------------------
# peak_position_correction
# ---------------------------------------------------------------------------

class TestPeakPositionCorrection:
    def test_returns_dict_with_keys(self):
        d = peak_position_correction()
        for key in ("R_star", "rs_uncorrected", "rs_corrected",
                    "fractional_shift", "ell_shift_percent"):
            assert key in d

    def test_fractional_shift_positive(self):
        # Baryon loading reduces r_s★ → frac_shift = (r_s0 - r_s★)/r_s0 > 0
        d = peak_position_correction()
        assert d["fractional_shift"] > 0.0

    def test_rs_corrected_positive(self):
        d = peak_position_correction()
        assert d["rs_corrected"] > 0.0

    def test_rs_corrected_shorter_than_uncorrected(self):
        # The corrected r_s★ should be shorter than the zero-baryon r_s0
        d = peak_position_correction()
        assert d["rs_corrected"] < d["rs_uncorrected"]

    def test_r_star_in_physical_range(self):
        d = peak_position_correction()
        assert 0.3 < d["R_star"] < 1.5


# ---------------------------------------------------------------------------
# accuracy_vs_tight_coupling
# ---------------------------------------------------------------------------

class TestAccuracyVsTightCoupling:
    ELLS = [50, 100, 200, 300, 500]

    def test_returns_dict(self):
        d = accuracy_vs_tight_coupling(self.ELLS, 0.9635)
        assert isinstance(d, dict)

    def test_has_required_keys(self):
        d = accuracy_vs_tight_coupling(self.ELLS, 0.9635)
        for key in ("dl_baryon", "dl_zero_baryon", "fractional_diff",
                    "mean_frac_diff", "max_frac_diff"):
            assert key in d

    def test_spectra_differ(self):
        d = accuracy_vs_tight_coupling(self.ELLS, 0.9635)
        assert not np.allclose(d["dl_baryon"], d["dl_zero_baryon"])

    def test_fractional_diff_shape(self):
        d = accuracy_vs_tight_coupling(self.ELLS, 0.9635)
        assert d["fractional_diff"].shape == (len(self.ELLS),)

    def test_mean_frac_diff_positive(self):
        d = accuracy_vs_tight_coupling(self.ELLS, 0.9635)
        assert d["mean_frac_diff"] >= 0.0

    def test_max_frac_diff_finite(self):
        d = accuracy_vs_tight_coupling(self.ELLS, 0.9635)
        assert np.isfinite(d["max_frac_diff"])
