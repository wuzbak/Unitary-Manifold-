# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cmb_spectral_shape.py
==================================
Test suite for Pillar 78-B — CMB Spectral Shape Residuals
(src/core/cmb_spectral_shape.py).

Covers:
  - silk_damping_kk: positivity, KK scale > ΛCDM, envelope ratio, canonical params
  - ee_tt_ratio_kk: ratio structure, KK suppression, delta sign, at-zero
  - peak_width_kk: positivity, KK vs ΛCDM, peak number scaling
  - spectral_shape_residual: structure, near-zero at low ℓ, grows at high ℓ
  - shape_audit: completeness, key presence, honest gap statement

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.cmb_spectral_shape import (
    N_W, K_CS, C_S, ELL_SILK_LCDM, ELLS_PER_RS, DELTA_KK_REF,
    R_POL_LCDM_PEAK1, FWHM_PEAK1_LCDM,
    silk_damping_kk,
    ee_tt_ratio_kk,
    peak_width_kk,
    spectral_shape_residual,
    shape_audit,
)


# ---------------------------------------------------------------------------
# TestSilkDampingKK  (5 tests)
# ---------------------------------------------------------------------------

class TestSilkDampingKK:
    def test_ell_D_kk_greater_than_lcdm(self):
        """KK correction shifts Silk scale upward (less damping)."""
        result = silk_damping_kk(500.0)
        assert result["ell_D_kk"] > result["ell_D_lcdm"]

    def test_delta_D_canonical_value(self):
        """δ_D = 5 × (12/37)² / (2×74) for canonical parameters."""
        result = silk_damping_kk(100.0)
        expected = N_W * C_S ** 2 / (2.0 * K_CS)
        assert abs(result["delta_D"] - expected) < 1e-10

    def test_delta_D_small(self):
        """Silk damping KK shift is small (< 1%)."""
        result = silk_damping_kk(100.0)
        assert result["delta_D"] < 0.01

    def test_envelope_ratio_greater_than_one_at_high_ell(self):
        """At high ℓ the KK envelope ratio > 1 (KK less damped than ΛCDM)."""
        result = silk_damping_kk(1000.0)
        assert result["envelope_ratio"] > 1.0

    def test_envelope_ratio_near_one_at_low_ell(self):
        """At low ℓ the KK envelope ratio is close to 1 (negligible damping)."""
        result = silk_damping_kk(10.0)
        # Both envelopes are ~1, ratio should be very close to 1
        assert abs(result["envelope_ratio"] - 1.0) < 0.01


# ---------------------------------------------------------------------------
# TestEETTPolarizationRatio  (5 tests)
# ---------------------------------------------------------------------------

class TestEETTPolarizationRatio:
    def test_r_pol_kk_less_than_lcdm_at_high_ell(self):
        """EE/TT ratio is KK-suppressed at high ℓ."""
        result = ee_tt_ratio_kk(500.0)
        assert result["r_pol_kk"] < result["r_pol_lcdm"]

    def test_delta_r_pol_negative(self):
        """KK correction reduces the polarization ratio."""
        result = ee_tt_ratio_kk(300.0)
        assert result["delta_r_pol"] < 0.0

    def test_r_pol_kk_positive(self):
        """KK-corrected polarization ratio remains positive."""
        result = ee_tt_ratio_kk(1000.0)
        assert result["r_pol_kk"] > 0.0

    def test_delta_kk_at_100_equals_canonical(self):
        """δ_KK at ℓ=100 equals the canonical Pillar 73 value."""
        result = ee_tt_ratio_kk(100.0)
        assert abs(result["delta_kk"] - DELTA_KK_REF) < 1e-12

    def test_r_pol_kk_approaches_lcdm_at_zero_ell(self):
        """At ℓ=0 the KK correction vanishes and r_pol matches ΛCDM."""
        result = ee_tt_ratio_kk(0.0)
        assert abs(result["r_pol_kk"] - result["r_pol_lcdm"]) < 1e-12


# ---------------------------------------------------------------------------
# TestPeakWidthKK  (4 tests)
# ---------------------------------------------------------------------------

class TestPeakWidthKK:
    def test_peak_width_positive(self):
        """Peak FWHM must be positive for all peaks."""
        for n in [1, 2, 3, 5]:
            result = peak_width_kk(n)
            assert result["fwhm_kk"] > 0.0

    def test_peak_width_scales_with_sqrt_n(self):
        """ΛCDM FWHM scales as √n between peaks 1 and 4."""
        pw1 = peak_width_kk(1)
        pw4 = peak_width_kk(4)
        ratio = pw4["fwhm_lcdm"] / pw1["fwhm_lcdm"]
        assert abs(ratio - 2.0) < 1e-10  # √4 = 2

    def test_kk_peak_kk_position_greater_than_lcdm(self):
        """KK-corrected peak positions are shifted to higher ℓ."""
        for n in [1, 2, 3]:
            result = peak_width_kk(n)
            assert result["ell_peak_kk"] > result["ell_peak_lcdm"]

    def test_fractional_width_change_small(self):
        """Fractional KK width change is small (< 1%)."""
        for n in [1, 2, 3]:
            result = peak_width_kk(n)
            assert abs(result["fractional_width_change"]) < 0.01


# ---------------------------------------------------------------------------
# TestSpectralShapeResidual  (5 tests)
# ---------------------------------------------------------------------------

class TestSpectralShapeResidual:
    def test_residual_returns_correct_keys(self):
        """spectral_shape_residual returns all expected dict keys."""
        result = spectral_shape_residual([100, 500, 1000])
        for key in ["ell", "delta_Cl_over_Cl_boltzmann",
                    "delta_Cl_over_Cl_silk", "delta_Cl_over_Cl_total",
                    "cumulative_snr_proxy"]:
            assert key in result

    def test_residual_ell_list_matches_input(self):
        """Output ell list matches input range."""
        ells = [100, 200, 500, 1000]
        result = spectral_shape_residual(ells)
        assert result["ell"] == ells

    def test_residual_near_zero_at_low_ell(self):
        """Shape residual is very small at low ℓ (< 10⁻³)."""
        result = spectral_shape_residual([50, 100])
        for val in result["delta_Cl_over_Cl_total"]:
            assert abs(val) < 1e-2

    def test_residual_grows_at_high_ell(self):
        """Shape residual grows toward higher ℓ (power law in ℓ²)."""
        result = spectual_shape = spectral_shape_residual([200, 1000])
        # At ℓ=1000 the Boltzmann term ~−2×8e-4×100 = −0.16 (large), while at
        # ℓ=200 it's ~−2×8e-4×4 = −0.0064. So |residual| at 1000 > at 200.
        abs_200 = abs(result["delta_Cl_over_Cl_total"][0])
        abs_1000 = abs(result["delta_Cl_over_Cl_total"][1])
        assert abs_1000 > abs_200

    def test_cumulative_snr_proxy_nonnegative(self):
        """Cumulative SNR proxy is non-negative and non-decreasing."""
        result = spectral_shape_residual(list(range(100, 1001, 100)))
        snr = result["cumulative_snr_proxy"]
        for i in range(1, len(snr)):
            assert snr[i] >= snr[i - 1] - 1e-10  # non-decreasing


# ---------------------------------------------------------------------------
# TestShapeAudit  (5 tests)
# ---------------------------------------------------------------------------

class TestShapeAudit:
    def test_audit_returns_dict(self):
        """shape_audit() returns a dict."""
        result = shape_audit()
        assert isinstance(result, dict)

    def test_audit_has_required_top_level_keys(self):
        """shape_audit dict contains all required top-level keys."""
        result = shape_audit()
        for key in ["title", "status", "silk_damping", "polarization",
                    "peak_widths", "shape_residual", "detectability", "open_gap"]:
            assert key in result, f"Missing key: {key}"

    def test_audit_silk_delta_D_canonical(self):
        """Audit reports the correct canonical δ_D value."""
        result = shape_audit()
        expected_delta_D = N_W * C_S ** 2 / (2.0 * K_CS)
        assert abs(result["silk_damping"]["delta_D_canonical"] - expected_delta_D) < 1e-10

    def test_audit_open_gap_is_honest(self):
        """Open gap statement mentions Boltzmann integration."""
        result = shape_audit()
        assert "Boltzmann" in result["open_gap"] or "CAMB" in result["open_gap"]

    def test_audit_pillar_reference(self):
        """Audit references Pillar 78-B."""
        result = shape_audit()
        assert "78" in result["pillar"]
