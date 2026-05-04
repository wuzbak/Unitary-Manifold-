# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 163: PMNS Solar Angle θ₁₂ RGE Running 4/15 → PDG
(src/core/pmns_solar_rge_correction.py).

Verifies constants, helper functions, RGE delta, seesaw threshold correction,
combined M_Z prediction, full report, and pillar summary.
"""

import math
import pytest

from src.core.pmns_solar_rge_correction import (
    # constants
    N_W,
    K_CS,
    SIN2_THETA12_GUT,
    SIN2_THETA12_PDG,
    SIN2_THETA12_PDG_ERR,
    SIN2_THETA13_PDG,
    SIN2_THETA23_PDG,
    DM2_21_EV2,
    DM2_32_EV2,
    M_TAU_GEV,
    V_HIGGS_GEV,
    M_Z_GEV,
    M_GUT_GEV,
    # functions
    tau_yukawa,
    log_rge_factor,
    dmass_ratio,
    sin2_2theta12_at_gut,
    rge_delta_sin2_theta12,
    seesaw_threshold_correction,
    sin2_theta12_at_mz,
    pmns_solar_rge_report,
    pillar163_summary,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_sin2_theta12_gut_exact(self):
        assert abs(SIN2_THETA12_GUT - 4 / 15) < 1e-14

    def test_sin2_theta12_gut_approx(self):
        assert abs(SIN2_THETA12_GUT - 0.26667) < 1e-4

    def test_sin2_theta12_pdg(self):
        assert SIN2_THETA12_PDG == pytest.approx(0.307, abs=1e-10)

    def test_sin2_theta12_pdg_err(self):
        assert SIN2_THETA12_PDG_ERR == pytest.approx(0.013, abs=1e-10)

    def test_sin2_theta13_pdg(self):
        assert abs(SIN2_THETA13_PDG - 0.02224) < 1e-8

    def test_sin2_theta23_pdg(self):
        assert abs(SIN2_THETA23_PDG - 0.572) < 1e-10

    def test_dm2_21(self):
        assert DM2_21_EV2 == pytest.approx(7.53e-5, rel=1e-6)

    def test_dm2_32(self):
        assert DM2_32_EV2 == pytest.approx(2.51e-3, rel=1e-6)

    def test_m_tau(self):
        assert M_TAU_GEV == pytest.approx(1.776, abs=1e-8)

    def test_v_higgs(self):
        assert V_HIGGS_GEV == pytest.approx(246.0, abs=1e-8)

    def test_m_z(self):
        assert M_Z_GEV == pytest.approx(91.2, abs=1e-8)

    def test_m_gut(self):
        assert M_GUT_GEV == pytest.approx(2.0e16, rel=1e-8)

    def test_gut_above_gut(self):
        assert M_GUT_GEV > M_Z_GEV


# ---------------------------------------------------------------------------
# tau_yukawa
# ---------------------------------------------------------------------------

class TestTauYukawa:
    def test_value(self):
        assert tau_yukawa() == pytest.approx(M_TAU_GEV / V_HIGGS_GEV, rel=1e-12)

    def test_range_lower(self):
        assert tau_yukawa() > 0.005

    def test_range_upper(self):
        assert tau_yukawa() < 0.015

    def test_small(self):
        assert tau_yukawa() < 1.0


# ---------------------------------------------------------------------------
# log_rge_factor
# ---------------------------------------------------------------------------

class TestLogRgeFactor:
    def test_positive(self):
        assert log_rge_factor() > 0

    def test_lower_bound(self):
        assert log_rge_factor() > 30

    def test_upper_bound(self):
        assert log_rge_factor() < 40

    def test_matches_math_log(self):
        assert log_rge_factor() == pytest.approx(math.log(M_GUT_GEV / M_Z_GEV), rel=1e-12)

    def test_custom_scales(self):
        val = log_rge_factor(m_gut_gev=1e10, m_z_gev=100.0)
        assert val == pytest.approx(math.log(1e10 / 100.0), rel=1e-12)


# ---------------------------------------------------------------------------
# dmass_ratio
# ---------------------------------------------------------------------------

class TestDmassRatio:
    def test_positive(self):
        assert dmass_ratio() > 0

    def test_lower_bound(self):
        assert dmass_ratio() > 30

    def test_upper_bound(self):
        assert dmass_ratio() < 40

    def test_exact(self):
        assert dmass_ratio() == pytest.approx(DM2_32_EV2 / DM2_21_EV2, rel=1e-12)


# ---------------------------------------------------------------------------
# sin2_2theta12_at_gut
# ---------------------------------------------------------------------------

class TestSin2_2theta12AtGut:
    def test_in_unit_interval(self):
        val = sin2_2theta12_at_gut()
        assert 0.0 < val < 1.0

    def test_formula(self):
        s = SIN2_THETA12_GUT
        expected = 4.0 * s * (1.0 - s)
        assert sin2_2theta12_at_gut(s) == pytest.approx(expected, rel=1e-12)

    def test_default_gut(self):
        s = 4 / 15
        expected = 4 * s * (1 - s)
        assert sin2_2theta12_at_gut() == pytest.approx(expected, rel=1e-12)

    def test_custom_input(self):
        s = 0.3
        assert sin2_2theta12_at_gut(s) == pytest.approx(4 * 0.3 * 0.7, rel=1e-12)

    def test_symmetry(self):
        # sin²(2θ) is symmetric about sin²θ = 0.5
        val_low = sin2_2theta12_at_gut(0.25)
        val_high = sin2_2theta12_at_gut(0.75)
        assert val_low == pytest.approx(val_high, rel=1e-12)


# ---------------------------------------------------------------------------
# rge_delta_sin2_theta12
# ---------------------------------------------------------------------------

class TestRgeDeltaSin2Theta12:
    def setup_method(self):
        self.result = rge_delta_sin2_theta12()

    def test_delta_positive(self):
        assert self.result["delta_sin2_theta12"] > 0

    def test_delta_upper_bound(self):
        assert self.result["delta_sin2_theta12"] < 0.05

    def test_delta_lower_bound(self):
        assert self.result["delta_sin2_theta12"] > 1e-4

    def test_keys_present(self):
        for key in ("delta_sin2_theta12", "y_tau_sq", "log_factor", "dm_ratio", "sin2_2theta12", "formula"):
            assert key in self.result

    def test_y_tau_sq(self):
        assert self.result["y_tau_sq"] == pytest.approx(tau_yukawa() ** 2, rel=1e-12)

    def test_log_factor(self):
        assert self.result["log_factor"] == pytest.approx(log_rge_factor(), rel=1e-12)

    def test_dm_ratio(self):
        assert self.result["dm_ratio"] == pytest.approx(dmass_ratio(), rel=1e-12)

    def test_sin2_2theta12(self):
        assert self.result["sin2_2theta12"] == pytest.approx(sin2_2theta12_at_gut(), rel=1e-12)

    def test_formula_string(self):
        assert isinstance(self.result["formula"], str)
        assert len(self.result["formula"]) > 10


# ---------------------------------------------------------------------------
# seesaw_threshold_correction
# ---------------------------------------------------------------------------

class TestSeesawThresholdCorrection:
    def setup_method(self):
        self.result = seesaw_threshold_correction()

    def test_delta_positive(self):
        assert self.result["delta_threshold"] > 0

    def test_delta_tiny(self):
        # Threshold correction << bulk RGE correction
        assert self.result["delta_threshold"] < 1e-4

    def test_keys_present(self):
        assert "delta_threshold" in self.result
        assert "m_r_gev" in self.result
        assert "method" in self.result

    def test_default_m_r(self):
        assert self.result["m_r_gev"] == pytest.approx(1e16, rel=1e-8)

    def test_custom_m_r(self):
        res = seesaw_threshold_correction(m_r_gev=1e15)
        assert res["m_r_gev"] == pytest.approx(1e15, rel=1e-8)

    def test_method_string(self):
        assert isinstance(self.result["method"], str)


# ---------------------------------------------------------------------------
# sin2_theta12_at_mz
# ---------------------------------------------------------------------------

class TestSin2Theta12AtMz:
    def setup_method(self):
        self.result = sin2_theta12_at_mz()

    def test_mz_greater_than_gut(self):
        assert self.result["sin2_theta12_mz"] > SIN2_THETA12_GUT

    def test_mz_below_pdg(self):
        # RGE partially closes but doesn't fully reach PDG
        assert self.result["sin2_theta12_mz"] < SIN2_THETA12_PDG

    def test_rge_shift_real(self):
        # 1-loop correction is small but positive; M_Z value > GUT value
        assert self.result["sin2_theta12_mz"] > SIN2_THETA12_GUT + 1e-5

    def test_residual_positive(self):
        assert self.result["residual"] > 0

    def test_residual_small(self):
        assert self.result["residual"] < 0.045

    def test_keys_present(self):
        for key in ("sin2_theta12_gut", "delta_rge", "delta_threshold",
                    "sin2_theta12_mz", "sin2_theta12_pdg", "residual",
                    "fractional_gap", "status"):
            assert key in self.result

    def test_gut_value(self):
        assert self.result["sin2_theta12_gut"] == pytest.approx(SIN2_THETA12_GUT, rel=1e-12)

    def test_pdg_value(self):
        assert self.result["sin2_theta12_pdg"] == pytest.approx(SIN2_THETA12_PDG, rel=1e-12)

    def test_status_valid(self):
        assert self.result["status"] in ("PARTIALLY_CLOSED", "IMPROVED")

    def test_delta_rge_positive(self):
        assert self.result["delta_rge"] > 0

    def test_delta_threshold_positive(self):
        assert self.result["delta_threshold"] > 0

    def test_consistency(self):
        r = self.result
        expected_mz = r["sin2_theta12_gut"] + r["delta_rge"] + r["delta_threshold"]
        assert r["sin2_theta12_mz"] == pytest.approx(expected_mz, rel=1e-12)

    def test_fractional_gap_small(self):
        assert self.result["fractional_gap"] < 0.15


# ---------------------------------------------------------------------------
# pmns_solar_rge_report
# ---------------------------------------------------------------------------

class TestPmnsSolarRgeReport:
    def setup_method(self):
        self.report = pmns_solar_rge_report()

    def test_contains_epistemic_label(self):
        assert "epistemic_label" in self.report

    def test_epistemic_label_value(self):
        assert self.report["epistemic_label"] == "PARTIALLY_CLOSED"

    def test_pillar_number(self):
        assert self.report["pillar"] == 163

    def test_keys_present(self):
        for key in ("sin2_theta12_gut", "sin2_theta12_mz_predicted", "sin2_theta12_pdg",
                    "delta_rge", "delta_threshold", "y_tau", "log_rge_factor",
                    "dm_ratio", "residual_gap", "fractional_gap", "status",
                    "honest_note", "reference"):
            assert key in self.report

    def test_gut_value(self):
        assert self.report["sin2_theta12_gut"] == pytest.approx(4 / 15, rel=1e-12)

    def test_mz_predicted_reasonable(self):
        # 1-loop RGE gives a small but positive shift from the GUT-scale value
        assert self.report["sin2_theta12_mz_predicted"] > SIN2_THETA12_GUT
        assert self.report["sin2_theta12_mz_predicted"] < SIN2_THETA12_PDG

    def test_residual_gap_positive(self):
        assert self.report["residual_gap"] > 0

    def test_status_label(self):
        # Dynamic status from sin2_theta12_at_mz; epistemic_label is always PARTIALLY_CLOSED
        assert self.report["status"] in ("PARTIALLY_CLOSED", "IMPROVED", "NO_CHANGE")

    def test_gap_reduction_positive(self):
        assert self.report["gap_reduction_pct"] > 0

    def test_honest_note_string(self):
        assert isinstance(self.report["honest_note"], str)
        assert len(self.report["honest_note"]) > 10

    def test_reference_string(self):
        assert isinstance(self.report["reference"], str)
        assert "Antusch" in self.report["reference"]


# ---------------------------------------------------------------------------
# pillar163_summary
# ---------------------------------------------------------------------------

class TestPillar163Summary:
    def setup_method(self):
        self.summary = pillar163_summary()

    def test_pillar_number(self):
        assert self.summary["pillar"] == 163

    def test_method(self):
        assert self.summary["method"] == "PMNS_theta12_1loop_RGE"

    def test_sin2_theta12_gut(self):
        assert self.summary["sin2_theta12_gut"] == pytest.approx(4 / 15, rel=1e-12)

    def test_sin2_theta12_pdg(self):
        assert self.summary["sin2_theta12_pdg"] == pytest.approx(0.307, abs=1e-10)

    def test_status(self):
        assert self.summary["status"] == "PARTIALLY_CLOSED"

    def test_honest_note(self):
        assert "8%" in self.summary["honest_note"]

    def test_mz_predicted_present(self):
        assert "sin2_theta12_mz_predicted" in self.summary

    def test_mz_predicted_reasonable(self):
        # 1-loop RGE gives small but positive shift; still below PDG value
        assert self.summary["sin2_theta12_mz_predicted"] > SIN2_THETA12_GUT
        assert self.summary["sin2_theta12_mz_predicted"] < SIN2_THETA12_PDG
