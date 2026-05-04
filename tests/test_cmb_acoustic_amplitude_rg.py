# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cmb_acoustic_amplitude_rg.py
========================================
Pillar 149 — Tests for cmb_acoustic_amplitude_rg.py.

Tests cover:
  - planck_cl_template(): ΛCDM acoustic peak template
  - um_transfer_function_correction(): tilt ratio (negligible)
  - um_cl_at_peak(): UM acoustic peak prediction
  - acoustic_peak_amplitude_ratio(): full per-peak ratio
  - cmb_amplitude_closure_status(): honest closure assessment
  - pillar149_summary(): structured audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.cmb_acoustic_amplitude_rg import (
    A_S_PLANCK,
    N_S_LCDM,
    N_S_UM,
    K_PIVOT,
    ACOUSTIC_PEAK_ELLS,
    R_S_MPC,
    D_A_CMB_MPC,
    CL_PEAK1_LCDM_UK2,
    CL_PEAK2_LCDM_UK2,
    CL_PEAK3_LCDM_UK2,
    UM_SUPPRESSION_PEAK1,
    UM_SUPPRESSION_PEAK2,
    UM_SUPPRESSION_PEAK3,
    planck_cl_template,
    um_transfer_function_correction,
    um_cl_at_peak,
    acoustic_peak_amplitude_ratio,
    cmb_amplitude_closure_status,
    pillar149_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_a_s_planck_order(self):
        assert 1e-10 < A_S_PLANCK < 1e-8

    def test_n_s_lcdm_is_0_9649(self):
        assert abs(N_S_LCDM - 0.9649) < 1e-6

    def test_n_s_um_is_0_9635(self):
        assert abs(N_S_UM - 0.9635) < 1e-6

    def test_n_s_um_less_than_n_s_lcdm(self):
        assert N_S_UM < N_S_LCDM

    def test_k_pivot_is_0_05(self):
        assert abs(K_PIVOT - 0.05) < 1e-8

    def test_acoustic_peaks_are_3(self):
        assert len(ACOUSTIC_PEAK_ELLS) == 3

    def test_peak_ells_increasing(self):
        assert ACOUSTIC_PEAK_ELLS[0] < ACOUSTIC_PEAK_ELLS[1] < ACOUSTIC_PEAK_ELLS[2]

    def test_first_peak_near_220(self):
        assert 200 < ACOUSTIC_PEAK_ELLS[0] < 250

    def test_r_s_mpc_order(self):
        assert 100 < R_S_MPC < 200

    def test_d_a_cmb_mpc_order(self):
        assert 1e4 < D_A_CMB_MPC < 1.5e4

    def test_cl_peak1_positive(self):
        assert CL_PEAK1_LCDM_UK2 > 0

    def test_suppression_factors_above_3(self):
        assert UM_SUPPRESSION_PEAK1 > 3.0
        assert UM_SUPPRESSION_PEAK2 > 3.0
        assert UM_SUPPRESSION_PEAK3 > 3.0


# ---------------------------------------------------------------------------
# planck_cl_template
# ---------------------------------------------------------------------------

class TestPlanckClTemplate:
    def test_first_peak_amplitude(self):
        """C_ℓ at ℓ~220 should be ~5000-6500 μK²."""
        cl = planck_cl_template(220)
        assert 3000 < cl < 8000

    def test_second_peak_amplitude(self):
        cl = planck_cl_template(540)
        assert cl > 0

    def test_third_peak_amplitude(self):
        cl = planck_cl_template(820)
        assert cl > 0

    def test_positive_for_all_ells(self):
        for ell in [10, 50, 100, 220, 540, 820, 1500]:
            assert planck_cl_template(ell) > 0

    def test_invalid_ell_raises(self):
        with pytest.raises(ValueError):
            planck_cl_template(0)
        with pytest.raises(ValueError):
            planck_cl_template(-10)

    def test_large_ell_damped(self):
        """Silk damping should reduce amplitude at large ℓ."""
        cl_220 = planck_cl_template(220)
        cl_3000 = planck_cl_template(3000)
        assert cl_3000 < cl_220


# ---------------------------------------------------------------------------
# um_transfer_function_correction
# ---------------------------------------------------------------------------

class TestUmTransferFunctionCorrection:
    def test_at_pivot_returns_1(self):
        """At k = k_pivot: ratio = (k/k_pivot)^Δn_s = 1."""
        ratio = um_transfer_function_correction(K_PIVOT)
        assert abs(ratio - 1.0) < 1e-10

    def test_ratio_close_to_1_at_cmb_scales(self):
        """Δn_s = -0.0014 gives negligible correction at acoustic peak scales."""
        k_peak1 = ACOUSTIC_PEAK_ELLS[0] / D_A_CMB_MPC
        ratio = um_transfer_function_correction(k_peak1)
        assert abs(ratio - 1.0) < 0.02  # < 2% correction

    def test_um_slightly_less_than_lcdm_at_large_k(self):
        """For n_s_um < n_s_lcdm and k > k_pivot: ratio < 1."""
        k_large = 1.0  # Mpc⁻¹, >> k_pivot = 0.05
        ratio = um_transfer_function_correction(k_large)
        assert ratio < 1.0

    def test_ratio_positive(self):
        k = 0.1  # Mpc⁻¹
        assert um_transfer_function_correction(k) > 0

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            um_transfer_function_correction(0.0)
        with pytest.raises(ValueError):
            um_transfer_function_correction(-0.1)

    def test_custom_n_s(self):
        ratio = um_transfer_function_correction(K_PIVOT, n_s_um=0.96, n_s_lcdm=0.97)
        assert abs(ratio - 1.0) < 1e-10

    def test_correction_is_pct_scale(self):
        """Correction at ℓ~220 should be less than 1%."""
        k = 220.0 / D_A_CMB_MPC
        ratio = um_transfer_function_correction(k)
        pct = abs(ratio - 1.0) * 100.0
        assert pct < 1.0


# ---------------------------------------------------------------------------
# um_cl_at_peak
# ---------------------------------------------------------------------------

class TestUmClAtPeak:
    def test_no_suppression_is_tilt_corrected_lcdm(self):
        """With suppression=1, UM Cl ≈ ΛCDM × tilt_ratio."""
        ell = 220
        cl_um = um_cl_at_peak(ell, suppression_factor=1.0)
        cl_lcdm = planck_cl_template(ell)
        k = ell / D_A_CMB_MPC
        t = um_transfer_function_correction(k)
        expected = cl_lcdm * t
        assert abs(cl_um - expected) / expected < 1e-8

    def test_suppression_reduces_amplitude(self):
        cl_nosupp = um_cl_at_peak(220, suppression_factor=1.0)
        cl_supp = um_cl_at_peak(220, suppression_factor=4.0)
        assert cl_supp < cl_nosupp

    def test_suppression_by_4_gives_quarter_amplitude(self):
        cl_1 = um_cl_at_peak(220, suppression_factor=1.0)
        cl_4 = um_cl_at_peak(220, suppression_factor=4.0)
        assert abs(cl_4 / cl_1 - 0.25) < 0.01

    def test_positive(self):
        assert um_cl_at_peak(220) > 0

    def test_invalid_ell_raises(self):
        with pytest.raises(ValueError):
            um_cl_at_peak(0)

    def test_invalid_suppression_raises(self):
        with pytest.raises(ValueError):
            um_cl_at_peak(220, suppression_factor=0.0)
        with pytest.raises(ValueError):
            um_cl_at_peak(220, suppression_factor=-1.0)


# ---------------------------------------------------------------------------
# acoustic_peak_amplitude_ratio
# ---------------------------------------------------------------------------

class TestAcousticPeakAmplitudeRatio:
    @pytest.fixture
    def ratio_result(self):
        return acoustic_peak_amplitude_ratio()

    def test_peaks_list_length_is_3(self, ratio_result):
        assert len(ratio_result["peaks"]) == 3

    def test_each_peak_has_required_keys(self, ratio_result):
        for p in ratio_result["peaks"]:
            assert "ell" in p
            assert "cl_lcdm_uk2" in p
            assert "tilt_ratio" in p
            assert "suppression_factor" in p
            assert "cl_um_predicted_uk2" in p
            assert "ratio_um_to_lcdm" in p

    def test_tilt_ratio_close_to_1(self, ratio_result):
        for p in ratio_result["peaks"]:
            assert abs(p["tilt_ratio"] - 1.0) < 0.05

    def test_ratio_um_to_lcdm_below_1(self, ratio_result):
        """UM amplitude is suppressed relative to ΛCDM."""
        for p in ratio_result["peaks"]:
            assert p["ratio_um_to_lcdm"] < 1.0

    def test_suppression_factors_above_3(self, ratio_result):
        for p in ratio_result["peaks"]:
            assert p["suppression_factor"] > 3.0

    def test_delta_ns_negative(self, ratio_result):
        assert ratio_result["delta_ns"] < 0

    def test_tilt_correction_summary_is_string(self, ratio_result):
        assert isinstance(ratio_result["tilt_correction_summary"], str)
        assert "NEGLIGIBLE" in ratio_result["tilt_correction_summary"]

    def test_suppression_summary_mentions_fallibility(self, ratio_result):
        assert "FALLIBILITY" in ratio_result["suppression_summary"]

    def test_peak_ells_match_acoustic_peaks(self, ratio_result):
        ells = [p["ell"] for p in ratio_result["peaks"]]
        assert list(ells) == list(ACOUSTIC_PEAK_ELLS)


# ---------------------------------------------------------------------------
# cmb_amplitude_closure_status
# ---------------------------------------------------------------------------

class TestCmbAmplitudeClosureStatus:
    @pytest.fixture
    def closure(self):
        return cmb_amplitude_closure_status()

    def test_pillar_is_149(self, closure):
        assert closure["pillar"] == 149

    def test_status_is_string(self, closure):
        assert isinstance(closure["status"], str)

    def test_status_mentions_open(self, closure):
        assert "OPEN" in closure["status"]

    def test_suppression_values_stored(self, closure):
        assert abs(closure["suppression_peak1"] - UM_SUPPRESSION_PEAK1) < 1e-8
        assert abs(closure["suppression_peak2"] - UM_SUPPRESSION_PEAK2) < 1e-8
        assert abs(closure["suppression_peak3"] - UM_SUPPRESSION_PEAK3) < 1e-8

    def test_suppression_range_correct(self, closure):
        lo, hi = closure["suppression_range"]
        assert lo < hi
        assert lo > 3.0

    def test_tilt_correction_negligible(self, closure):
        assert closure["tilt_correction_negligible"] is True

    def test_what_fixes_mentions_ns(self, closure):
        assert "n_s" in closure["what_braided_winding_fixes"] or "0.9635" in closure["what_braided_winding_fixes"]

    def test_fallibility_update_is_string(self, closure):
        assert isinstance(closure["fallibility_md_admission_2_update"], str)
        assert len(closure["fallibility_md_admission_2_update"]) > 100

    def test_fallibility_mentions_pillar_149(self, closure):
        assert "149" in closure["fallibility_md_admission_2_update"]

    def test_what_remains_open_mentions_r_s(self, closure):
        assert "r_s" in closure["what_remains_open"] or "R_b" in closure["what_remains_open"]


# ---------------------------------------------------------------------------
# pillar149_summary
# ---------------------------------------------------------------------------

class TestPillar149Summary:
    @pytest.fixture
    def p149(self):
        return pillar149_summary()

    def test_pillar_is_149(self, p149):
        assert p149["pillar"] == 149

    def test_status_open(self, p149):
        assert "OPEN" in p149["status"]

    def test_n_s_um_correct(self, p149):
        assert abs(p149["n_s_um"] - N_S_UM) < 1e-6

    def test_amplitude_not_fixed(self, p149):
        assert p149["amplitude_fixed"] is False

    def test_tilt_fixed(self, p149):
        assert p149["tilt_fixed"] is True

    def test_admission_2_update_is_string(self, p149):
        assert isinstance(p149["admission_2_update"], str)
        assert len(p149["admission_2_update"]) > 50

    def test_pillar_references_list(self, p149):
        assert isinstance(p149["pillar_references"], list)
        assert len(p149["pillar_references"]) >= 2

    def test_suppression_peak1_above_3(self, p149):
        assert p149["suppression_peak1"] > 3.0
