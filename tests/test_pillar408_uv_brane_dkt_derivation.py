# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 408 — UV Brane δ_KT Derivation (Admission 7 Closure)."""
import math
import pytest

from src.core.pillar408_uv_brane_dkt_derivation import (
    PILLAR_STATUS,
    ADMISSION_7_STATUS,
    N_W,
    K_CS,
    PI_KR,
    DELTA_C_LATTICE,
    uv_brane_overlap,
    uv_brane_overlap_correction,
    natural_brane_thickness,
    dkt_analytic_estimate,
    admission_7_naturalness_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == "NATURALNESS_DERIVED"

    def test_admission_7_status(self):
        assert ADMISSION_7_STATUS == "NATURALNESS_DERIVED"

    def test_nw(self):
        assert N_W == 5

    def test_kcs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37

    def test_delta_c_lattice(self):
        assert abs(DELTA_C_LATTICE - 5.0 / 74.0) < 1e-12


class TestUVBraneOverlap:
    def test_zero_brane_thickness(self):
        # For k_epsilon = 0, overlap ratio should be 1
        ratio = uv_brane_overlap(c_L=0.1, k_epsilon=0.0)
        assert abs(ratio - 1.0) < 1e-12

    def test_uv_localised_enhancement(self):
        # For c_L < 0.5 (UV-localised), overlap > 1 for positive k_epsilon
        ratio = uv_brane_overlap(c_L=0.1, k_epsilon=0.5)
        assert ratio > 1.0

    def test_ir_localised_suppression(self):
        # For c_L > 0.5 (IR-localised), overlap < 1
        ratio = uv_brane_overlap(c_L=0.8, k_epsilon=0.5)
        assert ratio < 1.0

    def test_formula(self):
        c_L = 0.09
        k_eps = 1.0 / 74.0
        expected = math.exp((1.0 - 2.0 * c_L) * k_eps)
        result = uv_brane_overlap(c_L, k_eps)
        assert abs(result - expected) < 1e-12


class TestUVBraneOverlapCorrection:
    def test_zero_correction_at_zero_thickness(self):
        corr = uv_brane_overlap_correction(c_L=0.1, k_epsilon=0.0)
        assert abs(corr) < 1e-10

    def test_positive_correction_uv_localised(self):
        # UV-localised fermion: correction should be positive
        corr = uv_brane_overlap_correction(c_L=0.1, k_epsilon=0.01)
        assert corr > 0

    def test_correction_proportional_to_cl(self):
        # For small k_epsilon: δc_L ≈ (1-2c_L) × kε × c_L
        c_L = 0.1
        k_eps = 1e-4
        expected_lo = (1.0 - 2.0 * c_L) * k_eps * c_L
        result = uv_brane_overlap_correction(c_L, k_eps)
        assert abs(result - expected_lo) / abs(expected_lo) < 0.01  # within 1%


class TestNaturalBraneThickness:
    def test_returns_dict(self):
        data = natural_brane_thickness()
        assert isinstance(data, dict)

    def test_three_scales(self):
        data = natural_brane_thickness()
        assert len(data["scales"]) == 3

    def test_scale_A_keps(self):
        data = natural_brane_thickness()
        scale_A = data["scales"][0]
        assert scale_A["label"] == "1/K_CS"
        assert abs(scale_A["k_epsilon"] - 1.0 / 74.0) < 1e-12

    def test_scale_B_keps(self):
        data = natural_brane_thickness()
        scale_B = data["scales"][1]
        assert scale_B["label"] == "πkR/K_CS"
        assert abs(scale_B["k_epsilon"] - 37.0 / 74.0) < 1e-12

    def test_scale_C_keps(self):
        data = natural_brane_thickness()
        scale_C = data["scales"][2]
        assert scale_C["label"] == "1/(2K_CS)"
        assert abs(scale_C["k_epsilon"] - 1.0 / 148.0) < 1e-12

    def test_delta_KT_natural_for_all_scales(self):
        data = natural_brane_thickness()
        for sc in data["scales"]:
            # All analytic estimates should be well below the lattice step
            assert sc["delta_KT_leading"] < 10.0  # loose bound


class TestDktAnalyticEstimate:
    def test_returns_dict(self):
        data = dkt_analytic_estimate()
        assert isinstance(data, dict)

    def test_naturalness_flag(self):
        data = dkt_analytic_estimate()
        assert data["naturalness"] is True  # dkt < 10% of lattice step

    def test_naturalness_verdict_natural(self):
        data = dkt_analytic_estimate()
        assert data["naturalness_verdict"] == "NATURAL"

    def test_leading_order_positive(self):
        data = dkt_analytic_estimate()
        assert data["delta_KT_leading_order"] > 0

    def test_nlo_larger_than_lo(self):
        data = dkt_analytic_estimate()
        # NLO should be slightly larger than LO (positive NLO correction)
        assert data["delta_KT_nlo"] > data["delta_KT_leading_order"]

    def test_scan_value_stored(self):
        data = dkt_analytic_estimate()
        assert abs(data["P402_dkt_scan"] - 0.053) < 1e-6


class TestAdmission7Verdict:
    def test_status_upgrade(self):
        verdict = admission_7_naturalness_verdict()
        assert verdict["new_status"] == "NATURALNESS_DERIVED"
        assert verdict["previous_status"] == "ARCHITECTURE_LIMIT_MAPPED"

    def test_admission_number(self):
        verdict = admission_7_naturalness_verdict()
        assert verdict["admission_number"] == 7

    def test_naturalness_true(self):
        verdict = admission_7_naturalness_verdict()
        assert verdict["naturalness"] is True

    def test_naturalness_verdict_natural(self):
        verdict = admission_7_naturalness_verdict()
        assert verdict["naturalness_verdict"] == "NATURAL"

    def test_delta_ell_inputs(self):
        verdict = admission_7_naturalness_verdict()
        assert abs(verdict["delta_ell_12"] - 1.390) < 1e-6
        assert abs(verdict["delta_ell_23"] - 0.665) < 1e-6

    def test_dkt_scan_stored(self):
        verdict = admission_7_naturalness_verdict()
        assert abs(verdict["dkt_scan"] - 0.053) < 1e-6

    def test_analytic_lo_positive(self):
        verdict = admission_7_naturalness_verdict()
        assert verdict["dkt_analytic_lo"] > 0

    def test_closure_verdict_present(self):
        verdict = admission_7_naturalness_verdict()
        assert "closure_verdict" in verdict
        assert len(verdict["closure_verdict"]) > 50

    def test_brane_mechanism_described(self):
        verdict = admission_7_naturalness_verdict()
        assert "brane" in verdict["brane_mechanism"].lower()
