# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_gap_residual_fix_audit.py
=======================================
Unit tests for src/core/gap_residual_fix_audit.py — Track 4.
"""

import math
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.gap_residual_fix_audit import (
    C_S, K_CS, N_W, N_C, PI_KR, M_KK_EW_MEV, M_PLANCK_MEV,
    ALPHA_GUT_UM, ALPHA_GUT_SU5,
    W_KK, W_PLANCK_BAO, W_DESI_DR2,
    LAMBDA_OBS_MPLANCK4, F_BRAID,
    DM31_UM_EV2, DM31_JUNO_EV2, DM31_JUNO_ERR_EV2,
    CLOSED, NARROWED, UNCHANGED,
    audit_gap1_cmb_peak_amplitude,
    audit_gap2_alpha_gut,
    audit_gap3_dark_energy_eos,
    audit_gap4_cosmological_constant,
    audit_gap5_juno_dm31,
    full_gap_audit,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_c_s(self):
        assert C_S == pytest.approx(12.0 / 37.0, rel=1e-10)

    def test_k_cs(self):
        assert K_CS == 74

    def test_w_kk_formula(self):
        expected = -1.0 + (2.0 / 3.0) * C_S**2
        assert W_KK == pytest.approx(expected, rel=1e-10)

    def test_w_kk_value(self):
        assert -0.94 < W_KK < -0.92

    def test_f_braid(self):
        assert F_BRAID == pytest.approx(C_S**2, rel=1e-10)

    def test_alpha_gut_um(self):
        assert ALPHA_GUT_UM == pytest.approx(N_C / K_CS, rel=1e-10)

    def test_alpha_gut_su5(self):
        assert ALPHA_GUT_SU5 == pytest.approx(1.0 / 24.0, rel=1e-10)


# ---------------------------------------------------------------------------
# GAP-1: CMB amplitude
# ---------------------------------------------------------------------------

class TestGap1:
    def setup_method(self):
        self.g = audit_gap1_cmb_peak_amplitude()

    def test_keys(self):
        for k in ["gap", "status", "residual_before", "residual_after",
                  "loop_correction_frac", "fix_description"]:
            assert k in self.g

    def test_status_narrowed(self):
        assert self.g["status"] == NARROWED

    def test_residual_before(self):
        assert self.g["residual_before"] == pytest.approx(0.26, rel=1e-6)

    def test_loop_correction_positive(self):
        assert self.g["loop_correction_frac"] > 0

    def test_residual_decreases(self):
        assert self.g["residual_after"] < self.g["residual_before"]

    def test_loop_correction_order_magnitude(self):
        # α_s × N_c / (4π) ≈ 0.028 × 3 / (4π) ≈ 0.0067
        assert 0.001 < self.g["loop_correction_frac"] < 0.02

    def test_z_phi_tree(self):
        assert self.g["Z_phi_tree"] == pytest.approx(5.30, rel=1e-6)

    def test_residual_after_not_closed(self):
        # Should not be < 1% (not CLOSED)
        assert self.g["residual_after"] > 0.01


# ---------------------------------------------------------------------------
# GAP-2: α_GUT
# ---------------------------------------------------------------------------

class TestGap2:
    def setup_method(self):
        self.g = audit_gap2_alpha_gut()

    def test_keys(self):
        for k in ["gap", "status", "alpha_gut_um", "alpha_gut_su5",
                  "delta_alpha_kk", "residual_after_kk", "fix_description"]:
            assert k in self.g

    def test_alpha_gut_um_value(self):
        assert self.g["alpha_gut_um"] == pytest.approx(3.0 / 74.0, rel=1e-9)

    def test_alpha_gut_su5_value(self):
        assert self.g["alpha_gut_su5"] == pytest.approx(1.0 / 24.0, rel=1e-9)

    def test_raw_residual_positive(self):
        assert self.g["residual_raw_frac"] > 0

    def test_delta_alpha_negative(self):
        # KK threshold correction decreases α (runs toward unification)
        assert self.g["delta_alpha_kk"] < 0

    def test_ln_mass_ratio_positive(self):
        assert self.g["ln_M_GUT_over_M_KK"] > 0

    def test_residual_after_kk_nonnegative(self):
        assert self.g["residual_after_kk"] >= 0

    def test_status_valid(self):
        assert self.g["status"] in (CLOSED, NARROWED, UNCHANGED)


# ---------------------------------------------------------------------------
# GAP-3: Dark energy EoS
# ---------------------------------------------------------------------------

class TestGap3:
    def setup_method(self):
        self.g = audit_gap3_dark_energy_eos()

    def test_keys(self):
        for k in ["gap", "status", "w_kk", "sigma_planck_bao_before",
                  "sigma_desi_dr2_before", "delta_cs", "w_corrected",
                  "sigma_planck_bao_after", "fix_description"]:
            assert k in self.g

    def test_w_kk_value(self):
        assert self.g["w_kk"] == pytest.approx(W_KK, rel=1e-9)

    def test_planck_tension_before(self):
        # 3.3σ tension with Planck+BAO
        assert self.g["sigma_planck_bao_before"] == pytest.approx(
            abs(W_KK - W_PLANCK_BAO) / 0.03, rel=1e-6
        )

    def test_desi_tension_small(self):
        # DESI DR2 is consistent (< 0.2σ)
        assert self.g["sigma_desi_dr2_before"] < 0.5

    def test_delta_cs_tiny(self):
        # φ⁴ correction very small
        assert abs(self.g["delta_cs"]) < 0.01

    def test_w_corrected_near_w_kk(self):
        # correction is negligible
        assert abs(self.g["w_corrected"] - W_KK) < 0.01

    def test_status_unchanged_vs_planck(self):
        assert self.g["status"] == UNCHANGED

    def test_tension_after_still_large(self):
        # φ⁴ fix is negligible → tension barely changes
        assert self.g["sigma_planck_bao_after"] > 3.0


# ---------------------------------------------------------------------------
# GAP-4: Cosmological constant
# ---------------------------------------------------------------------------

class TestGap4:
    def setup_method(self):
        self.g = audit_gap4_cosmological_constant()

    def test_keys(self):
        for k in ["gap", "status", "log10_lambda_obs", "N_exact_from_rho_obs_alone",
                  "fractional_part", "N_with_M_KK_prefactor",
                  "fractional_part_with_mkk", "fix_description"]:
            assert k in self.g

    def test_log10_lambda_obs(self):
        expected = math.log10(LAMBDA_OBS_MPLANCK4)
        assert self.g["log10_lambda_obs"] == pytest.approx(expected, rel=1e-6)
        assert self.g["log10_lambda_obs"] < -100

    def test_f_braid_value(self):
        assert self.g["f_braid"] == pytest.approx((12.0 / 37.0)**2, rel=1e-9)

    def test_n_exact_positive(self):
        # log(ρ_obs) / log(f_braid): both negative → positive ratio
        assert self.g["N_exact_from_rho_obs_alone"] > 0

    def test_n_with_mkk_positive(self):
        assert self.g["N_with_M_KK_prefactor"] > 0

    def test_fractional_parts_between_0_and_1(self):
        assert 0.0 <= self.g["fractional_part"] <= 0.5
        assert 0.0 <= self.g["fractional_part_with_mkk"] <= 0.5

    def test_status_valid(self):
        assert self.g["status"] in (CLOSED, NARROWED, UNCHANGED)


# ---------------------------------------------------------------------------
# GAP-5: JUNO Δm²₃₁
# ---------------------------------------------------------------------------

class TestGap5:
    def setup_method(self):
        self.g = audit_gap5_juno_dm31()

    def test_keys(self):
        for k in ["gap", "status", "dm31_um_ev2", "dm31_juno_ev2",
                  "tension_sigma_before", "delta_m2_ev2",
                  "dm31_corrected_ev2", "tension_sigma_after",
                  "fix_description"]:
            assert k in self.g

    def test_dm31_values(self):
        assert self.g["dm31_um_ev2"] == pytest.approx(DM31_UM_EV2, rel=1e-9)
        assert self.g["dm31_juno_ev2"] == pytest.approx(DM31_JUNO_EV2, rel=1e-9)

    def test_tension_before(self):
        expected = abs(DM31_UM_EV2 - DM31_JUNO_EV2) / DM31_JUNO_ERR_EV2
        assert self.g["tension_sigma_before"] == pytest.approx(expected, rel=1e-6)

    def test_delta_m2_negligibly_small(self):
        # Torsion correction ~10^-33 eV² vs gap ~9×10^-6 eV²
        assert abs(self.g["delta_m2_ev2"]) < 1e-20

    def test_tension_unchanged(self):
        # Delta_m² correction is negligible → tension virtually identical
        assert abs(self.g["tension_sigma_after"] - self.g["tension_sigma_before"]) < 0.01

    def test_status_unchanged(self):
        assert self.g["status"] == UNCHANGED

    def test_corrected_dm31_close_to_um(self):
        # Correction is tiny → corrected value ≈ UM prediction
        assert self.g["dm31_corrected_ev2"] == pytest.approx(DM31_UM_EV2, rel=1e-6)


# ---------------------------------------------------------------------------
# Full audit
# ---------------------------------------------------------------------------

class TestFullAudit:
    def setup_method(self):
        self.report = full_gap_audit()

    def test_all_gaps_present(self):
        for k in ["gap1_cmb_amplitude", "gap2_alpha_gut", "gap3_dark_energy_eos",
                  "gap4_cosmological_constant", "gap5_juno_dm31",
                  "summary", "overall_assessment"]:
            assert k in self.report

    def test_summary_structure(self):
        s = self.report["summary"]
        assert s["n_gaps_audited"] == 5
        assert s["n_closed"] + s["n_narrowed"] + s["n_unchanged"] == 5

    def test_summary_statuses_keys(self):
        s = self.report["summary"]["statuses"]
        assert "CMB amplitude" in s
        assert "alpha_GUT" in s
        assert "w_DE" in s
        assert "CC gap" in s
        assert "JUNO dm31" in s

    def test_all_statuses_valid(self):
        s = self.report["summary"]["statuses"]
        for v in s.values():
            assert v in (CLOSED, NARROWED, UNCHANGED)

    def test_overall_assessment_nonempty(self):
        assert isinstance(self.report["overall_assessment"], str)
        assert len(self.report["overall_assessment"]) > 50

    def test_gap3_status_unchanged(self):
        assert self.report["gap3_dark_energy_eos"]["status"] == UNCHANGED

    def test_gap5_status_unchanged(self):
        assert self.report["gap5_juno_dm31"]["status"] == UNCHANGED

    def test_gap1_status_narrowed(self):
        assert self.report["gap1_cmb_amplitude"]["status"] == NARROWED
