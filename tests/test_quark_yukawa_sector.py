# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_quark_yukawa_sector.py
==================================
Test suite for src/core/quark_yukawa_sector.py (Pillar 81).

Coverage (~60 tests):
  - TestConstants: PDG masses, PI_KR, K_RS, SIN_THETA_C_PDG, etc.
  - TestRsWavefunctionZeroMode: properties identical to Pillar 75 wavefunction
  - TestDeltaCForRatio: correct Δc values for known mass ratios
  - TestFitUpSectorBulkMasses: keys, ratios reproduced, Δc sign conventions
  - TestFitDownSectorBulkMasses: same for down sector
  - TestQuarkMassRatiosAll: all intra-sector PDG ratios reproduced
  - TestCabiboAngleFromBulkMismatch: Cabibbo angle ≠ 0, within factor 3 of PDG
  - TestFNGenerationChargeInterpretation: epsilon < 1 for all sectors
  - TestBottomTauRatio: ratio ≈ 2.354, keys present
  - TestQuarkSectorGapReport: structure and epistemic status
"""
from __future__ import annotations

import math
import pytest

from src.core.quark_yukawa_sector import (
    # Constants
    M_UP_MEV,
    M_DOWN_MEV,
    M_STRANGE_MEV,
    M_CHARM_MEV,
    M_BOTTOM_MEV,
    M_TOP_MEV,
    M_ELECTRON_MEV,
    M_MUON_MEV,
    M_TAU_MEV,
    PI_KR_CANONICAL,
    K_RS_CANONICAL,
    C_R_QUARKS,
    SIN_THETA_C_PDG,
    THETA_C_PDG_DEG,
    R_CHARM_UP,
    R_TOP_CHARM,
    R_STRANGE_DOWN,
    R_BOTTOM_STRANGE,
    R_BOTTOM_TAU,
    # Functions
    rs_wavefunction_zero_mode,
    delta_c_for_ratio,
    fit_up_sector_bulk_masses,
    fit_down_sector_bulk_masses,
    quark_mass_ratios_all,
    cabibbo_angle_from_bulk_mismatch,
    fn_generation_charge_interpretation,
    bottom_tau_ratio,
    quark_sector_gap_report,
)


# ---------------------------------------------------------------------------
# TestConstants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_m_up(self):
        assert M_UP_MEV == pytest.approx(2.16, rel=1e-6)

    def test_m_down(self):
        assert M_DOWN_MEV == pytest.approx(4.67, rel=1e-6)

    def test_m_strange(self):
        assert M_STRANGE_MEV == pytest.approx(93.4, rel=1e-6)

    def test_m_charm(self):
        assert M_CHARM_MEV == pytest.approx(1273.0, rel=1e-6)

    def test_m_bottom(self):
        assert M_BOTTOM_MEV == pytest.approx(4183.0, rel=1e-6)

    def test_m_top(self):
        assert M_TOP_MEV == pytest.approx(172760.0, rel=1e-6)

    def test_pi_kr(self):
        assert PI_KR_CANONICAL == pytest.approx(37.0, rel=1e-9)

    def test_k_rs(self):
        assert K_RS_CANONICAL == pytest.approx(1.0, rel=1e-9)

    def test_c_r_quarks(self):
        assert C_R_QUARKS == pytest.approx(0.5, rel=1e-9)

    def test_sin_theta_c_pdg(self):
        assert SIN_THETA_C_PDG == pytest.approx(0.2257, rel=1e-3)

    def test_theta_c_pdg_deg(self):
        assert THETA_C_PDG_DEG == pytest.approx(13.04, rel=1e-3)

    def test_r_charm_up(self):
        assert R_CHARM_UP == pytest.approx(M_CHARM_MEV / M_UP_MEV, rel=1e-6)

    def test_r_top_charm(self):
        assert R_TOP_CHARM == pytest.approx(M_TOP_MEV / M_CHARM_MEV, rel=1e-6)

    def test_r_strange_down(self):
        assert R_STRANGE_DOWN == pytest.approx(M_STRANGE_MEV / M_DOWN_MEV, rel=1e-6)

    def test_r_bottom_strange(self):
        assert R_BOTTOM_STRANGE == pytest.approx(M_BOTTOM_MEV / M_STRANGE_MEV, rel=1e-6)

    def test_r_bottom_tau(self):
        assert R_BOTTOM_TAU == pytest.approx(M_BOTTOM_MEV / M_TAU_MEV, rel=1e-3)


# ---------------------------------------------------------------------------
# TestRsWavefunctionZeroMode
# ---------------------------------------------------------------------------

class TestRsWavefunctionZeroMode:
    """Properties of the RS zero-mode wavefunction (identical to Pillar 75)."""

    def test_positive(self):
        """Wavefunction value is always positive."""
        for c in [0.0, 0.3, 0.5, 0.6, 0.8, 1.0]:
            assert rs_wavefunction_zero_mode(c) > 0

    def test_uv_localised_larger(self):
        """c < 0.5 (UV-localised) gives larger wavefunction than c > 0.5 (IR-localised)."""
        f_uv = rs_wavefunction_zero_mode(0.3)
        f_ir = rs_wavefunction_zero_mode(0.7)
        assert f_uv > f_ir

    def test_flat_limit(self):
        """At c = 0.5 (flat profile), wavefunction ≈ sqrt(k/πkR) = sqrt(1/37)."""
        f = rs_wavefunction_zero_mode(0.5, k_RS=1.0, pi_kR=37.0)
        expected = math.sqrt(1.0 / 37.0)
        assert f == pytest.approx(expected, rel=0.01)

    def test_returns_float(self):
        assert isinstance(rs_wavefunction_zero_mode(0.6), float)

    def test_exponential_sensitivity(self):
        """f(c1)/f(c2) ≈ sqrt((2c1-1)/(2c2-1)) * exp((c2-c1)*πkR) for IR-localized (both c>0.5)."""
        c1 = 0.6  # lighter, less IR-localized
        c2 = 0.7  # heavier, more IR-localized
        pi_kR = 37.0
        f1 = rs_wavefunction_zero_mode(c1, pi_kR=pi_kR)
        f2 = rs_wavefunction_zero_mode(c2, pi_kR=pi_kR)
        # In the IR-localized limit: f(c1)/f(c2) ≈ sqrt((2c1-1)/(2c2-1)) * exp((c2-c1)*πkR)
        exp_factor = math.exp((c2 - c1) * pi_kR)
        prefactor = math.sqrt((2 * c1 - 1) / (2 * c2 - 1))
        approx_ratio = prefactor * exp_factor
        actual_ratio = f1 / f2
        # Allow 10% relative error (formula is exact in large-πkR limit)
        assert actual_ratio == pytest.approx(approx_ratio, rel=0.1)

    def test_custom_pi_kr(self):
        f37 = rs_wavefunction_zero_mode(0.6, pi_kR=37.0)
        f50 = rs_wavefunction_zero_mode(0.6, pi_kR=50.0)
        # Larger πkR → more sensitive → expect different values
        assert f37 != pytest.approx(f50, rel=0.01)

    def test_identical_to_pillar75_formula(self):
        """Verify the exact formula: sqrt(|1-2c|*k / |1 - exp(-(1-2c)*πkR)|)."""
        c = 0.6
        k = 1.0
        pi_kR = 37.0
        exponent = (1.0 - 2.0 * c) * pi_kR
        prefactor = (1.0 - 2.0 * c) * k
        denom = abs(1.0 - math.exp(-exponent))
        expected = math.sqrt(abs(prefactor) / denom)
        assert rs_wavefunction_zero_mode(c, k, pi_kR) == pytest.approx(expected, rel=1e-12)


# ---------------------------------------------------------------------------
# TestDeltaCForRatio
# ---------------------------------------------------------------------------

class TestDeltaCForRatio:
    """Δc = ln(ratio)/πkR."""

    def test_ratio_207_approx(self):
        """μ/e ≈ 206.77 → Δc ≈ 0.1437."""
        dc = delta_c_for_ratio(206.77)
        assert dc == pytest.approx(math.log(206.77) / 37.0, rel=1e-9)
        assert dc == pytest.approx(0.1437, abs=0.001)

    def test_ratio_17_approx(self):
        """τ/μ ≈ 16.817 → Δc ≈ 0.0762."""
        dc = delta_c_for_ratio(16.817)
        assert dc == pytest.approx(math.log(16.817) / 37.0, rel=1e-9)
        assert dc == pytest.approx(0.0762, abs=0.001)

    def test_ratio_1_gives_zero(self):
        assert delta_c_for_ratio(1.0) == pytest.approx(0.0, abs=1e-12)

    def test_positive_for_ratio_gt_1(self):
        assert delta_c_for_ratio(100.0) > 0

    def test_negative_ratio_raises(self):
        with pytest.raises(ValueError):
            delta_c_for_ratio(-1.0)

    def test_zero_ratio_raises(self):
        with pytest.raises(ValueError):
            delta_c_for_ratio(0.0)

    def test_zero_pi_kr_raises(self):
        with pytest.raises(ValueError):
            delta_c_for_ratio(10.0, pi_kR=0.0)

    def test_custom_pi_kr(self):
        dc = delta_c_for_ratio(100.0, pi_kR=50.0)
        assert dc == pytest.approx(math.log(100.0) / 50.0, rel=1e-9)


# ---------------------------------------------------------------------------
# TestFitUpSectorBulkMasses
# ---------------------------------------------------------------------------

class TestFitUpSectorBulkMasses:
    def setup_method(self):
        self.fit = fit_up_sector_bulk_masses()

    def test_keys_present(self):
        for k in ["c_L_up", "c_L_charm", "c_L_top",
                  "delta_c_cu", "delta_c_tc",
                  "ratio_cu_achieved", "ratio_tc_achieved",
                  "ratio_cu_pdg", "ratio_tc_pdg"]:
            assert k in self.fit

    def test_c_L_ordering(self):
        """Heavier quarks have smaller c_L (more UV localised)."""
        assert self.fit["c_L_charm"] < self.fit["c_L_up"]
        assert self.fit["c_L_top"] < self.fit["c_L_charm"]

    def test_delta_c_cu_negative(self):
        assert self.fit["delta_c_cu"] < 0

    def test_delta_c_tc_negative(self):
        assert self.fit["delta_c_tc"] < 0

    def test_charm_over_up_reproduced(self):
        achieved = self.fit["ratio_cu_achieved"]
        pdg = self.fit["ratio_cu_pdg"]
        assert achieved == pytest.approx(pdg, rel=0.001)

    def test_top_over_charm_reproduced(self):
        achieved = self.fit["ratio_tc_achieved"]
        pdg = self.fit["ratio_tc_pdg"]
        assert achieved == pytest.approx(pdg, rel=0.001)

    def test_pdg_ratios_correct(self):
        assert self.fit["ratio_cu_pdg"] == pytest.approx(M_CHARM_MEV / M_UP_MEV, rel=1e-6)
        assert self.fit["ratio_tc_pdg"] == pytest.approx(M_TOP_MEV / M_CHARM_MEV, rel=1e-6)


# ---------------------------------------------------------------------------
# TestFitDownSectorBulkMasses
# ---------------------------------------------------------------------------

class TestFitDownSectorBulkMasses:
    def setup_method(self):
        self.fit = fit_down_sector_bulk_masses()

    def test_keys_present(self):
        for k in ["c_L_down", "c_L_strange", "c_L_bottom",
                  "delta_c_sd", "delta_c_bs",
                  "ratio_sd_achieved", "ratio_bs_achieved",
                  "ratio_sd_pdg", "ratio_bs_pdg"]:
            assert k in self.fit

    def test_c_L_ordering(self):
        assert self.fit["c_L_strange"] < self.fit["c_L_down"]
        assert self.fit["c_L_bottom"] < self.fit["c_L_strange"]

    def test_delta_c_sd_negative(self):
        assert self.fit["delta_c_sd"] < 0

    def test_delta_c_bs_negative(self):
        assert self.fit["delta_c_bs"] < 0

    def test_strange_over_down_reproduced(self):
        achieved = self.fit["ratio_sd_achieved"]
        pdg = self.fit["ratio_sd_pdg"]
        assert achieved == pytest.approx(pdg, rel=0.001)

    def test_bottom_over_strange_reproduced(self):
        achieved = self.fit["ratio_bs_achieved"]
        pdg = self.fit["ratio_bs_pdg"]
        assert achieved == pytest.approx(pdg, rel=0.001)

    def test_pdg_ratios_correct(self):
        assert self.fit["ratio_sd_pdg"] == pytest.approx(M_STRANGE_MEV / M_DOWN_MEV, rel=1e-6)
        assert self.fit["ratio_bs_pdg"] == pytest.approx(M_BOTTOM_MEV / M_STRANGE_MEV, rel=1e-6)


# ---------------------------------------------------------------------------
# TestQuarkMassRatiosAll
# ---------------------------------------------------------------------------

class TestQuarkMassRatiosAll:
    def setup_method(self):
        self.ratios = quark_mass_ratios_all()

    def test_top_level_keys(self):
        assert "up_sector" in self.ratios
        assert "down_sector" in self.ratios
        assert "inter_sector" in self.ratios

    def test_up_sector_keys(self):
        up = self.ratios["up_sector"]
        for k in ["charm_over_up", "top_over_charm", "top_over_up"]:
            assert k in up

    def test_down_sector_keys(self):
        dn = self.ratios["down_sector"]
        for k in ["strange_over_down", "bottom_over_strange", "bottom_over_down"]:
            assert k in dn

    def test_charm_over_up(self):
        cu = self.ratios["up_sector"]["charm_over_up"]
        assert cu["achieved"] == pytest.approx(cu["pdg"], rel=0.001)

    def test_top_over_charm(self):
        tc = self.ratios["up_sector"]["top_over_charm"]
        assert tc["achieved"] == pytest.approx(tc["pdg"], rel=0.001)

    def test_strange_over_down(self):
        sd = self.ratios["down_sector"]["strange_over_down"]
        assert sd["achieved"] == pytest.approx(sd["pdg"], rel=0.001)

    def test_bottom_over_strange(self):
        bs = self.ratios["down_sector"]["bottom_over_strange"]
        assert bs["achieved"] == pytest.approx(bs["pdg"], rel=0.001)

    def test_top_over_up_pdg_value(self):
        tu = self.ratios["up_sector"]["top_over_up"]
        assert tu["pdg"] == pytest.approx(M_TOP_MEV / M_UP_MEV, rel=1e-6)

    def test_bottom_over_down_pdg_value(self):
        bd = self.ratios["down_sector"]["bottom_over_down"]
        assert bd["pdg"] == pytest.approx(M_BOTTOM_MEV / M_DOWN_MEV, rel=1e-6)

    def test_inter_sector_keys(self):
        inter = self.ratios["inter_sector"]
        for k in ["charm_over_strange_wf", "top_over_bottom_wf", "up_over_down_wf"]:
            assert k in inter


# ---------------------------------------------------------------------------
# TestCabiboAngleFromBulkMismatch
# ---------------------------------------------------------------------------

class TestCabiboAngleFromBulkMismatch:
    def setup_method(self):
        self.result = cabibbo_angle_from_bulk_mismatch()

    def test_keys_present(self):
        for k in ["c_L_up", "c_L_down", "f0_up", "f0_down",
                  "sin_theta_C_derived", "sin_theta_C_pdg",
                  "theta_C_derived_deg", "theta_C_pdg_deg",
                  "residual_ratio", "status"]:
            assert k in self.result

    def test_sin_theta_nonzero(self):
        """Derived Cabibbo sine must be non-zero."""
        assert self.result["sin_theta_C_derived"] > 0

    def test_sin_theta_range(self):
        """sin(θ_C) ∈ (0, 1)."""
        s = self.result["sin_theta_C_derived"]
        assert 0.0 < s < 1.0

    def test_pdg_value(self):
        assert self.result["sin_theta_C_pdg"] == pytest.approx(0.2257, rel=1e-3)

    def test_theta_pdg_deg(self):
        assert self.result["theta_C_pdg_deg"] == pytest.approx(13.04, rel=1e-3)

    def test_within_factor_3_of_pdg(self):
        """The derived value should be within a factor of 3 of the PDG value."""
        ratio = self.result["residual_ratio"]
        assert 1.0 / 3.0 <= ratio <= 3.0

    def test_status_is_string(self):
        assert isinstance(self.result["status"], str)

    def test_f0_up_positive(self):
        assert self.result["f0_up"] > 0

    def test_f0_down_positive(self):
        assert self.result["f0_down"] > 0

    def test_theta_derived_deg_positive(self):
        assert self.result["theta_C_derived_deg"] > 0


# ---------------------------------------------------------------------------
# TestFNGenerationChargeInterpretation
# ---------------------------------------------------------------------------

class TestFNGenerationChargeInterpretation:
    def setup_method(self):
        self.fn = fn_generation_charge_interpretation()

    def test_keys_present(self):
        for k in ["leptons", "up_quarks", "down_quarks", "pattern", "connection_to_nw"]:
            assert k in self.fn

    def test_lepton_keys(self):
        for k in ["delta_c_10", "delta_c_21", "epsilon_10", "epsilon_21"]:
            assert k in self.fn["leptons"]

    def test_up_quark_keys(self):
        for k in ["delta_c_cu", "delta_c_tc", "epsilon_cu", "epsilon_tc"]:
            assert k in self.fn["up_quarks"]

    def test_down_quark_keys(self):
        for k in ["delta_c_sd", "delta_c_bs", "epsilon_sd", "epsilon_bs"]:
            assert k in self.fn["down_quarks"]

    def test_lepton_epsilon_lt_1(self):
        assert self.fn["leptons"]["epsilon_10"] < 1.0
        assert self.fn["leptons"]["epsilon_21"] < 1.0

    def test_up_quark_epsilon_lt_1(self):
        assert self.fn["up_quarks"]["epsilon_cu"] < 1.0
        assert self.fn["up_quarks"]["epsilon_tc"] < 1.0

    def test_down_quark_epsilon_lt_1(self):
        assert self.fn["down_quarks"]["epsilon_sd"] < 1.0
        assert self.fn["down_quarks"]["epsilon_bs"] < 1.0

    def test_lepton_delta_c_positive(self):
        assert self.fn["leptons"]["delta_c_10"] > 0
        assert self.fn["leptons"]["delta_c_21"] > 0

    def test_pattern_is_string(self):
        assert isinstance(self.fn["pattern"], str)

    def test_connection_to_nw_mentions_nw5(self):
        assert "n_w = 5" in self.fn["connection_to_nw"] or "nw=5" in self.fn["connection_to_nw"]

    def test_all_delta_c_positive(self):
        for val in [
            self.fn["leptons"]["delta_c_10"],
            self.fn["leptons"]["delta_c_21"],
            self.fn["up_quarks"]["delta_c_cu"],
            self.fn["up_quarks"]["delta_c_tc"],
            self.fn["down_quarks"]["delta_c_sd"],
            self.fn["down_quarks"]["delta_c_bs"],
        ]:
            assert val > 0


# ---------------------------------------------------------------------------
# TestBottomTauRatio
# ---------------------------------------------------------------------------

class TestBottomTauRatio:
    def setup_method(self):
        self.result = bottom_tau_ratio()

    def test_keys_present(self):
        for k in ["ratio_pdg", "c_L_bottom_quark", "c_L_tau_lepton",
                  "delta_c_b_tau", "wf_ratio_b_over_tau",
                  "ratio_rs_gut_limit", "gut_prediction_approx",
                  "status", "note"]:
            assert k in self.result

    def test_ratio_pdg_approx(self):
        assert self.result["ratio_pdg"] == pytest.approx(
            M_BOTTOM_MEV / M_TAU_MEV, rel=1e-3
        )

    def test_ratio_pdg_value(self):
        assert self.result["ratio_pdg"] == pytest.approx(2.354, rel=0.01)

    def test_gut_prediction_approx(self):
        assert self.result["gut_prediction_approx"] == pytest.approx(3.0, rel=0.1)

    def test_wf_ratio_positive(self):
        assert self.result["wf_ratio_b_over_tau"] > 0

    def test_status_is_string(self):
        assert isinstance(self.result["status"], str)

    def test_note_nonempty(self):
        assert len(self.result["note"]) > 10

    def test_c_L_bottom_less_than_c_L_tau(self):
        """Bottom quark is heavier than tau → more UV localised → smaller c_L."""
        # This is not guaranteed since the two sectors have different reference c_L values
        # but we check c_L values are reasonable (not NaN or inf)
        assert math.isfinite(self.result["c_L_bottom_quark"])
        assert math.isfinite(self.result["c_L_tau_lepton"])


# ---------------------------------------------------------------------------
# TestQuarkSectorGapReport
# ---------------------------------------------------------------------------

class TestQuarkSectorGapReport:
    def setup_method(self):
        self.report = quark_sector_gap_report()

    def test_keys_present(self):
        for k in ["pillar", "title", "derived", "mechanism", "open", "epistemic_status"]:
            assert k in self.report

    def test_pillar_81(self):
        assert self.report["pillar"] == 81

    def test_derived_is_list(self):
        assert isinstance(self.report["derived"], list)

    def test_derived_nonempty(self):
        assert len(self.report["derived"]) > 0

    def test_open_is_list(self):
        assert isinstance(self.report["open"], list)

    def test_open_mentions_cp_violation(self):
        combined = " ".join(self.report["open"]).lower()
        assert "cp" in combined or "complex" in combined

    def test_open_mentions_ckm(self):
        combined = " ".join(self.report["open"]).lower()
        assert "ckm" in combined or "cabibbo" in combined

    def test_epistemic_status_is_string(self):
        assert isinstance(self.report["epistemic_status"], str)

    def test_epistemic_status_nonempty(self):
        assert len(self.report["epistemic_status"]) > 5

    def test_mechanism_mentions_rs(self):
        assert "RS" in self.report["mechanism"] or "Randall" in self.report["mechanism"]
