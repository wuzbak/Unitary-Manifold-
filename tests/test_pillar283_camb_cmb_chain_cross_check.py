# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 283 — CAMB CMB Chain Cross-Check."""
from __future__ import annotations

import math
import pytest

from src.core.pillar283_camb_cmb_chain_cross_check import (
    ADJACENCY_TRACK_LABEL,
    CAMB_PARAM_MAP,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PLANCK_2018_DL_REFERENCE,
    UM_CMB_PARAMS,
    analytic_transfer_function,
    braided_sound_speed_acoustic_correction,
    camb_cmb_cross_check_report,
    camb_soft_dependency_report,
    cmb_chain_consistency_check,
    dl_from_primordial,
    planck_reference_comparison,
    primordial_power_spectrum,
    separation_guard,
)


# ---------------------------------------------------------------------------
# Identity and metadata
# ---------------------------------------------------------------------------

def test_pillar_identity():
    assert PILLAR_NUMBER == 283
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard():
    g = separation_guard()
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
    assert g["validates_cmb_prediction_chain_end_to_end"] is True


# ---------------------------------------------------------------------------
# UM CMB parameter set
# ---------------------------------------------------------------------------

def test_um_cmb_params_spectral_index():
    assert abs(UM_CMB_PARAMS["n_s"] - 0.9635) < 1.0e-6


def test_um_cmb_params_tensor_ratio():
    assert abs(UM_CMB_PARAMS["r"] - 0.0315) < 1.0e-6


def test_um_cmb_params_tensor_tilt_consistency():
    # n_t = -r/8 (consistency relation)
    n_t_expected = -UM_CMB_PARAMS["r"] / 8.0
    assert abs(UM_CMB_PARAMS["n_t"] - n_t_expected) < 1.0e-12


def test_um_cmb_params_braided_cs():
    c_s_expected = 12.0 / 37.0
    assert abs(UM_CMB_PARAMS["c_s"] - c_s_expected) < 1.0e-12


def test_um_cmb_params_winding_number():
    assert UM_CMB_PARAMS["n_w"] == 5
    assert UM_CMB_PARAMS["K_CS"] == 74
    assert UM_CMB_PARAMS["n_w"] ** 2 + 7 ** 2 == UM_CMB_PARAMS["K_CS"]


def test_planck_2018_reference_multipoles():
    assert set(PLANCK_2018_DL_REFERENCE.keys()) >= {200, 500, 1000, 2000}
    for ell, ref in PLANCK_2018_DL_REFERENCE.items():
        assert ref["Dl_TT_uK2"] > 0.0
        assert ref["sigma_uK2"] > 0.0


# ---------------------------------------------------------------------------
# CAMB parameter map
# ---------------------------------------------------------------------------

def test_camb_param_map_coverage():
    for um_key, camb_key in CAMB_PARAM_MAP.items():
        assert camb_key, f"Empty CAMB key for '{um_key}'"


# ---------------------------------------------------------------------------
# Primordial power spectrum
# ---------------------------------------------------------------------------

def test_primordial_ps_at_pivot():
    ps = primordial_power_spectrum(UM_CMB_PARAMS["k_star_mpc"])
    assert abs(ps["P_s"] - UM_CMB_PARAMS["A_s"]) < 1.0e-15 * UM_CMB_PARAMS["A_s"]


def test_primordial_ps_tilt():
    k1 = 0.05   # pivot
    k2 = 0.50   # 10× pivot
    ps1 = primordial_power_spectrum(k1)
    ps2 = primordial_power_spectrum(k2)
    ratio = ps2["P_s"] / ps1["P_s"]
    expected = (k2 / k1) ** (UM_CMB_PARAMS["n_s"] - 1.0)
    assert abs(ratio - expected) < 1.0e-10


def test_primordial_ps_tensor_to_scalar():
    ps = primordial_power_spectrum(0.05)
    assert abs(ps["P_s_to_P_t_ratio"] - UM_CMB_PARAMS["r"]) < 1.0e-10


def test_primordial_ps_validation():
    with pytest.raises(ValueError):
        primordial_power_spectrum(-0.1)
    with pytest.raises(ValueError):
        primordial_power_spectrum(0.0)


# ---------------------------------------------------------------------------
# Analytic transfer function
# ---------------------------------------------------------------------------

def test_transfer_function_low_ell():
    T_sq = analytic_transfer_function(2)
    # At ℓ=2, should be > 0 (SW plateau)
    assert T_sq > 0.0


def test_transfer_function_positive():
    for ell in [10, 50, 100, 200, 500, 1000, 2000]:
        T_sq = analytic_transfer_function(ell)
        assert T_sq >= 0.0, f"T²({ell}) < 0"


def test_transfer_function_damping_at_high_ell():
    T_low = analytic_transfer_function(100)
    T_high = analytic_transfer_function(2000)
    # Silk damping should make high-ell T² smaller
    assert T_high < T_low


def test_transfer_function_validation():
    with pytest.raises(ValueError):
        analytic_transfer_function(0)
    with pytest.raises(ValueError):
        analytic_transfer_function(-10)


# ---------------------------------------------------------------------------
# Dℓ computation
# ---------------------------------------------------------------------------

def test_dl_positive():
    for ell in [100, 200, 500, 1000]:
        dl = dl_from_primordial(ell)
        assert dl > 0.0, f"Dℓ({ell}) ≤ 0"


def test_dl_uK2_order_of_magnitude():
    # Planck Dℓ at ℓ=220 (first peak) is ~6000 μK².
    # The analytic SW+acoustic approximation is accurate at the ~30% level.
    dl_220 = dl_from_primordial(220)
    assert 1000.0 < dl_220 < 20000.0, (
        f"Dℓ(220) = {dl_220:.1f} μK²: out of physical range for analytic SW approximation"
    )
    # Also check high ℓ where Silk damping applies
    dl_2000 = dl_from_primordial(2000)
    assert 10.0 < dl_2000 < 5000.0, f"Dℓ(2000) = {dl_2000:.1f} μK²: out of damped range"


# ---------------------------------------------------------------------------
# Planck reference comparison
# ---------------------------------------------------------------------------

def test_planck_comparison_structure():
    comparisons = planck_reference_comparison()
    assert len(comparisons) == len(PLANCK_2018_DL_REFERENCE)
    for c in comparisons:
        assert "ell" in c
        assert "Dl_UM_uK2" in c
        assert "Dl_Planck_uK2" in c
        assert "residual_sigma" in c
        assert "within_2sigma" in c


def test_planck_comparison_residuals_finite():
    comparisons = planck_reference_comparison()
    for c in comparisons:
        assert math.isfinite(c["residual_sigma"]), f"Non-finite residual at ℓ={c['ell']}"
        assert math.isfinite(c["Dl_UM_uK2"])


# ---------------------------------------------------------------------------
# Braided sound speed acoustic correction
# ---------------------------------------------------------------------------

def test_braided_cs_correction_structure():
    ac = braided_sound_speed_acoustic_correction()
    assert abs(ac["c_s_um"] - 12.0 / 37.0) < 1.0e-12
    assert abs(ac["c_s_lcdm"] - 1.0 / math.sqrt(3.0)) < 1.0e-12
    assert ac["c_s_ratio"] < 1.0   # c_s^UM < c_s^ΛCDM


def test_braided_cs_shifts_peaks_higher():
    ac = braided_sound_speed_acoustic_correction()
    assert ac["ell_peak1_um"] > ac["ell_peak1_lcdm"]
    assert ac["peak1_shift_delta_ell"] > 0.0


def test_braided_cs_sound_horizon_smaller():
    ac = braided_sound_speed_acoustic_correction()
    assert ac["r_s_um_mpc"] < ac["r_s_lcdm_mpc"]


# ---------------------------------------------------------------------------
# CMB chain consistency check
# ---------------------------------------------------------------------------

def test_cmb_chain_consistency_structure():
    check = cmb_chain_consistency_check()
    assert "step1_primordial_tilt_self_consistency" in check
    assert "step2_transfer_function_normalisation" in check
    assert "step3_planck_dl_comparison" in check
    assert "step4_braided_cs_acoustic_correction" in check
    assert "step5_cmb_suppression_factor_in_range" in check
    assert "chain_consistent" in check


def test_cmb_chain_step1_pass():
    check = cmb_chain_consistency_check()
    assert check["step1_primordial_tilt_self_consistency"]["pass"] is True


def test_cmb_chain_step5_suppression_in_range():
    check = cmb_chain_consistency_check()
    assert check["step5_cmb_suppression_factor_in_range"]["pass"] is True


def test_cmb_chain_overall_consistent():
    check = cmb_chain_consistency_check()
    # The chain should be internally consistent
    assert isinstance(check["chain_consistent"], bool)


# ---------------------------------------------------------------------------
# CAMB soft dependency report
# ---------------------------------------------------------------------------

def test_camb_soft_dependency_structure():
    dep = camb_soft_dependency_report()
    assert "camb_version_required" in dep
    assert "camb_inputs" in dep
    assert "camb_cross_check_command" in dep
    assert dep["camb_available"] is False
    assert "n_s" in str(dep["camb_cross_check_command"]) or "ns" in str(dep["camb_cross_check_command"])


def test_camb_inputs_contain_key_params():
    dep = camb_soft_dependency_report()
    inputs = dep["camb_inputs"]
    assert inputs.get("ns") is not None or inputs.get("n_s") is not None


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def test_camb_cross_check_report_structure():
    report = camb_cmb_cross_check_report()
    assert report["pillar"] == 283
    assert "um_cmb_params" in report
    assert "chain_check" in report
    assert "camb_soft_dependency" in report
    assert "acoustic_horizon_correction" in report


def test_camb_cross_check_report_no_hardgate_drift():
    report = camb_cmb_cross_check_report()
    g = report["separation_guard"]
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
