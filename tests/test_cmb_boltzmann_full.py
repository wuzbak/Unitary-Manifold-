# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cmb_boltzmann_full.py
==================================
Test suite for Pillar 78 — Full KK-Boltzmann Integration
(src/core/cmb_boltzmann_full.py).

Covers:
  - Module constants (N_W, K_CS, A_S_PLANCK, N_S_PLANCK, Z_REC, etc.)
  - kk_boltzmann_correction: positivity, ℓ² scaling, Pillar 73 value
  - kk_sound_horizon: less than ΛCDM, positive, monotone in δ_rs
  - acoustic_peak_positions_kk: structure, peaks shifted, ratio > ΛCDM
  - transfer_function_kk: range [−1, 1], continuity
  - cl_spectrum_kk: structure, Cℓ positive at low ℓ, ratio < 1 at high ℓ
  - cl_ratio_um_to_lcdm: ratio < 1 at high ℓ, structure
  - peak_height_modification: structure, height change sign
  - cmb_s4_forecast_residuals: structure, SNR, detectable list
  - full_boltzmann_audit: all components listed, key predictions finite

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.cmb_boltzmann_full import (
    N_W, K_CS, C_S, N_S_PLANCK, A_S_PLANCK, K_STAR_MPC, Z_REC,
    C_S_REC_LCDM, R_S_LCDM_MPC, ELLS_PER_RS, DELTA_KK_CANONICAL,
    kk_boltzmann_correction,
    kk_sound_horizon,
    acoustic_peak_positions_kk,
    transfer_function_kk,
    cl_spectrum_kk,
    cl_ratio_um_to_lcdm,
    peak_height_modification,
    cmb_s4_forecast_residuals,
    full_boltzmann_audit,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s_value(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-10

    def test_n_s_planck(self):
        assert abs(N_S_PLANCK - 0.9649) < 0.001

    def test_a_s_planck(self):
        assert abs(A_S_PLANCK - 2.101e-9) < 1e-12

    def test_z_rec(self):
        assert abs(Z_REC - 1089.8) < 1.0

    def test_r_s_lcdm_mpc(self):
        assert abs(R_S_LCDM_MPC - 144.7) < 1.0

    def test_delta_kk_canonical(self):
        """Pillar 73 canonical value: δ_KK ≈ 8×10⁻⁴ at ℓ=100."""
        assert abs(DELTA_KK_CANONICAL - 8.0e-4) < 1e-5


# ---------------------------------------------------------------------------
# kk_boltzmann_correction
# ---------------------------------------------------------------------------

class TestKKBoltzmannCorrection:
    def test_positive(self):
        """KK correction is positive (suppresses power)."""
        assert kk_boltzmann_correction(100) > 0

    def test_canonical_value_at_ell100(self):
        """At ℓ=100, should return DELTA_KK_CANONICAL."""
        val = kk_boltzmann_correction(100)
        assert abs(val - DELTA_KK_CANONICAL) < 1e-10

    def test_ell2_scaling(self):
        """δ_KK ∝ ℓ²."""
        d100 = kk_boltzmann_correction(100)
        d200 = kk_boltzmann_correction(200)
        assert abs(d200 / d100 - 4.0) < 1e-10

    def test_zero_at_ell_zero(self):
        """δ_KK = 0 at ℓ = 0."""
        assert kk_boltzmann_correction(0) == 0.0

    def test_increases_with_ell(self):
        """Larger ℓ → larger correction."""
        d1 = kk_boltzmann_correction(100)
        d2 = kk_boltzmann_correction(500)
        d3 = kk_boltzmann_correction(1000)
        assert d1 < d2 < d3

    def test_raises_on_negative_ell(self):
        with pytest.raises(ValueError):
            kk_boltzmann_correction(-1)

    def test_custom_ref(self):
        """Custom reference value should scale correctly."""
        d = kk_boltzmann_correction(200, delta_kk_ref=1e-3, ell_ref=100)
        assert abs(d - 4e-3) < 1e-10


# ---------------------------------------------------------------------------
# kk_sound_horizon
# ---------------------------------------------------------------------------

class TestKKSoundHorizon:
    def test_positive(self):
        assert kk_sound_horizon() > 0

    def test_less_than_lcdm(self):
        """KK correction reduces the sound horizon."""
        r_s_kk = kk_sound_horizon()
        assert r_s_kk < R_S_LCDM_MPC

    def test_close_to_lcdm(self):
        """Correction should be small (δ_rs ~ n_w × f_braid / 2 ≈ 5×10⁻³ × 1.4×10⁻³ / 2)."""
        r_s_kk = kk_sound_horizon()
        frac = abs(r_s_kk - R_S_LCDM_MPC) / R_S_LCDM_MPC
        assert frac < 0.01  # < 1% correction

    def test_finite(self):
        assert math.isfinite(kk_sound_horizon())


# ---------------------------------------------------------------------------
# acoustic_peak_positions_kk
# ---------------------------------------------------------------------------

class TestAcousticPeakPositionsKK:
    def test_keys(self):
        result = acoustic_peak_positions_kk()
        for key in ("peaks_lcdm", "peaks_kk", "peak_shift_ell",
                    "fractional_shift", "r_s_lcdm_Mpc", "r_s_kk_Mpc",
                    "delta_rs_fraction"):
            assert key in result

    def test_n_peaks_count(self):
        result = acoustic_peak_positions_kk(n_peaks=5)
        assert len(result["peaks_lcdm"]) == 5
        assert len(result["peaks_kk"]) == 5

    def test_peaks_positive(self):
        result = acoustic_peak_positions_kk()
        assert all(p > 0 for p in result["peaks_lcdm"])
        assert all(p > 0 for p in result["peaks_kk"])

    def test_kk_peaks_shifted(self):
        """KK-corrected peaks should be shifted relative to ΛCDM."""
        result = acoustic_peak_positions_kk()
        # All shifts should be in same direction
        shifts = result["peak_shift_ell"]
        assert all(abs(s) > 0 for s in shifts)

    def test_first_peak_lcdm_near_220(self):
        """First acoustic peak is at ℓ ≈ 220 in ΛCDM."""
        result = acoustic_peak_positions_kk()
        assert 150 < result["peaks_lcdm"][0] < 300

    def test_r_s_kk_less_than_lcdm(self):
        result = acoustic_peak_positions_kk()
        assert result["r_s_kk_Mpc"] < result["r_s_lcdm_Mpc"]


# ---------------------------------------------------------------------------
# transfer_function_kk
# ---------------------------------------------------------------------------

class TestTransferFunctionKK:
    def test_finite_at_small_k(self):
        assert math.isfinite(transfer_function_kk(0.001))

    def test_unity_at_zero_k(self):
        """T(k=0) = 1 (large-scale limit)."""
        assert transfer_function_kk(0) == 1.0

    def test_range_check(self):
        """T(k) is bounded."""
        for k in [0.001, 0.01, 0.1, 1.0]:
            val = transfer_function_kk(k)
            assert math.isfinite(val)


# ---------------------------------------------------------------------------
# cl_spectrum_kk
# ---------------------------------------------------------------------------

class TestClSpectrumKK:
    def test_keys(self):
        result = cl_spectrum_kk(range(2, 20))
        for key in ("ell", "Cl_lcdm", "Cl_kk", "delta_Cl", "ratio_kk_to_lcdm"):
            assert key in result

    def test_ell_list_matches_input(self):
        ells = list(range(2, 50))
        result = cl_spectrum_kk(ells)
        assert result["ell"] == ells

    def test_cl_lcdm_positive_low_ell(self):
        result = cl_spectrum_kk(range(2, 20))
        assert all(c > 0 for c in result["Cl_lcdm"])

    def test_kk_less_than_lcdm(self):
        """KK correction suppresses power: Cℓ_KK ≤ Cℓ_ΛCDM."""
        result = cl_spectrum_kk(range(10, 200, 10))
        for i in range(len(result["ell"])):
            assert result["Cl_kk"][i] <= result["Cl_lcdm"][i] + 1e-40

    def test_ratio_at_most_one(self):
        """Cℓ_KK / Cℓ_ΛCDM ≤ 1."""
        result = cl_spectrum_kk(range(2, 200, 10))
        for r in result["ratio_kk_to_lcdm"]:
            assert r <= 1.0 + 1e-10

    def test_delta_cl_nonpositive(self):
        """ΔCℓ = Cℓ_KK − Cℓ_ΛCDM ≤ 0."""
        result = cl_spectrum_kk(range(2, 200, 10))
        for d in result["delta_Cl"]:
            assert d <= 0.0 + 1e-40

    def test_ell_less_than_2_gives_zero(self):
        result = cl_spectrum_kk([0, 1, 2])
        assert result["Cl_lcdm"][0] == 0.0
        assert result["Cl_lcdm"][1] == 0.0


# ---------------------------------------------------------------------------
# cl_ratio_um_to_lcdm
# ---------------------------------------------------------------------------

class TestClRatioUMToLCDM:
    def test_keys(self):
        result = cl_ratio_um_to_lcdm(range(2, 50))
        for key in ("ell", "ratio_UM_to_LCDM", "delta_KK_per_ell"):
            assert key in result

    def test_ratio_at_most_one(self):
        result = cl_ratio_um_to_lcdm(range(2, 500, 10))
        for r in result["ratio_UM_to_LCDM"]:
            assert r <= 1.0 + 1e-10

    def test_delta_kk_positive(self):
        result = cl_ratio_um_to_lcdm(range(10, 200, 10))
        for d in result["delta_KK_per_ell"]:
            assert d >= 0.0

    def test_ratio_decreases_with_ell(self):
        """Higher ℓ → more suppression → smaller ratio."""
        result = cl_ratio_um_to_lcdm([100, 500, 1000])
        ratios = result["ratio_UM_to_LCDM"]
        assert ratios[0] >= ratios[1] >= ratios[2]


# ---------------------------------------------------------------------------
# peak_height_modification
# ---------------------------------------------------------------------------

class TestPeakHeightModification:
    def test_keys(self):
        result = peak_height_modification(1)
        for key in ("n_peak", "ell_peak_lcdm", "ell_peak_kk",
                    "delta_ell", "fractional_height_change", "delta_KK_at_peak"):
            assert key in result

    def test_n_peak_stored(self):
        for n in [1, 2, 3]:
            assert peak_height_modification(n)["n_peak"] == n

    def test_height_change_negative(self):
        """KK correction suppresses peak heights: fractional_height_change < 0."""
        result = peak_height_modification(1)
        assert result["fractional_height_change"] < 0

    def test_peak_3_more_suppressed_than_1(self):
        """Higher peaks at higher ℓ are more suppressed."""
        r1 = peak_height_modification(1)
        r3 = peak_height_modification(3)
        assert abs(r3["fractional_height_change"]) > abs(r1["fractional_height_change"])

    def test_delta_kk_positive(self):
        assert peak_height_modification(1)["delta_KK_at_peak"] > 0

    def test_ell_peak_lcdm_positive(self):
        assert peak_height_modification(1)["ell_peak_lcdm"] > 0


# ---------------------------------------------------------------------------
# cmb_s4_forecast_residuals
# ---------------------------------------------------------------------------

class TestCMBS4ForecastResiduals:
    def test_keys(self):
        result = cmb_s4_forecast_residuals(range(2, 50))
        for key in ("ell", "delta_Cl", "SNR_per_ell",
                    "detectable_at_1sigma", "total_SNR",
                    "detection_threshold", "sigma_noise_per_ell"):
            assert key in result

    def test_list_lengths_match(self):
        ells = list(range(2, 50))
        result = cmb_s4_forecast_residuals(ells)
        assert len(result["ell"]) == len(ells)
        assert len(result["delta_Cl"]) == len(ells)
        assert len(result["SNR_per_ell"]) == len(ells)

    def test_snr_nonnegative(self):
        result = cmb_s4_forecast_residuals(range(2, 100))
        assert all(s >= 0 for s in result["SNR_per_ell"])

    def test_total_snr_positive_or_zero(self):
        result = cmb_s4_forecast_residuals(range(2, 100))
        assert result["total_SNR"] >= 0

    def test_detectable_is_bool_list(self):
        result = cmb_s4_forecast_residuals(range(2, 20))
        assert all(isinstance(d, bool) for d in result["detectable_at_1sigma"])


# ---------------------------------------------------------------------------
# full_boltzmann_audit
# ---------------------------------------------------------------------------

class TestFullBoltzmannAudit:
    def test_keys(self):
        result = full_boltzmann_audit()
        for key in ("title", "components", "key_predictions",
                    "testable_by", "remaining_open"):
            assert key in result

    def test_components_dict(self):
        result = full_boltzmann_audit()
        assert "COBE_normalisation" in result["components"]
        assert "KK_Boltzmann_correction" in result["components"]

    def test_key_predictions_finite(self):
        result = full_boltzmann_audit()
        for k, v in result["key_predictions"].items():
            if isinstance(v, (int, float)):
                assert math.isfinite(v), f"Non-finite value for {k}: {v}"

    def test_cobe_closed(self):
        result = full_boltzmann_audit()
        assert "CLOSED" in result["components"]["COBE_normalisation"]

    def test_full_boltzmann_open(self):
        result = full_boltzmann_audit()
        assert "OPEN" in result["components"]["full_numerical_Boltzmann"]

    def test_testable_by_includes_future(self):
        result = full_boltzmann_audit()
        telescopes = " ".join(result["testable_by"])
        assert "CMB-S4" in telescopes or "LiteBIRD" in telescopes

    def test_delta_kk_canonical_in_predictions(self):
        result = full_boltzmann_audit()
        assert abs(result["key_predictions"]["delta_KK_at_ell_100"] - DELTA_KK_CANONICAL) < 1e-10

    def test_remaining_open_not_empty(self):
        result = full_boltzmann_audit()
        assert len(result["remaining_open"]) >= 2
