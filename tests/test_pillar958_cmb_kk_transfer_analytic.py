# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 958 — CMB KK Transfer Function (Analytic)."""

import math
import pytest
from src.core.pillar958_cmb_kk_transfer_analytic import (
    PILLAR_STATUS, PILLAR_VALID, K_CS, N_W, N_2, C_S, NS_BRAIDED, R_BRAIDED,
    DELTA_KK_SOUND, DELTA_SILK, LCDM_PEAK_POSITIONS, Z_PHI_QUOTED,
    kk_sound_horizon_correction, silk_damping_kk_correction,
    braided_primordial_spectrum, full_kk_cl_residual,
    cmb_falsification_predictions, pillar958_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "CMB_KK_TRANSFER_ANALYTIC_COMPLETE"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_cs_value():
    assert abs(C_S - 12.0/37.0) < 1e-10


def test_ns_braided():
    assert abs(NS_BRAIDED - 0.9635) < 1e-6


def test_r_braided():
    assert abs(R_BRAIDED - 0.0315) < 1e-6


def test_delta_kk_sound():
    assert DELTA_KK_SOUND == 8.0e-4


def test_delta_silk():
    assert DELTA_SILK == 3.55e-3


def test_z_phi_quoted():
    assert abs(Z_PHI_QUOTED - 5.30) < 1e-6


def test_sound_horizon_correction():
    result = kk_sound_horizon_correction()
    assert result["shift_negligible_at_current_precision"] is True
    assert len(result["kk_peak_positions"]) == len(LCDM_PEAK_POSITIONS)
    # Peak positions shift slightly (negatively)
    for kk, lcdm in zip(result["kk_peak_positions"], LCDM_PEAK_POSITIONS):
        assert kk <= lcdm


def test_silk_damping_corrections_negative():
    result = silk_damping_kk_correction()
    for ell, dcl in result["delta_cl_over_cl_at_ell"].items():
        # All corrections are negative (suppression)
        assert dcl <= 0


def test_silk_damping_magnitude():
    result = silk_damping_kk_correction()
    # At ℓ=1500 (Silk scale), correction = -2×δ_D
    assert abs(result["peak_correction_at_l1500"] + 2 * DELTA_SILK) < 1e-10


def test_silk_within_cmbs4_target():
    result = silk_damping_kk_correction()
    assert result["within_cmb_s4_target"] is True


def test_ns_planck_consistent():
    prim = braided_primordial_spectrum()
    assert prim["planck_consistency"] is True


def test_ns_difference_within_sigma():
    prim = braided_primordial_spectrum()
    # Planck 1σ = ±0.0042
    assert abs(prim["ns_difference"]) < 0.0042


def test_r_braided_value():
    prim = braided_primordial_spectrum()
    assert abs(prim["r_braided"] - 0.0315) < 1e-6


def test_full_cl_residual_structure():
    result = full_kk_cl_residual()
    assert "kk_cl_residuals" in result
    assert result["camb_class_required"] is False
    assert "IRREDUCIBLE" in result["amplitude_gap_status"]


def test_cl_residuals_at_standard_ells():
    result = full_kk_cl_residual([220, 540, 1000])
    ells = list(result["kk_cl_residuals"].keys())
    assert 220 in ells
    assert 540 in ells
    assert 1000 in ells


def test_max_residual_bounded():
    result = full_kk_cl_residual()
    # Max residual should be < 5% (shape effects only)
    assert result["max_residual_percent"] < 5.0


def test_falsification_predictions():
    fp = cmb_falsification_predictions()
    assert "ns" in fp["predictions"]
    assert "r" in fp["predictions"]
    assert "beta_prediction_0p331" not in fp["predictions"]  # key is birefringence_beta_deg
    assert "birefringence_beta_deg" in fp["predictions"]
    assert fp["predictions"]["r"]["value"] < 0.036


def test_litebird_timeline():
    fp = cmb_falsification_predictions()
    assert "LiteBIRD" in fp["timeline"]


def test_summary():
    s = pillar958_summary()
    assert s["pillar"] == 958
    assert s["valid"] is True
    assert s["key_results"]["camb_not_required_for_leading_corrections"] is True
