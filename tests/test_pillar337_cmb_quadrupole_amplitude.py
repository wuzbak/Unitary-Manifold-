# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 337 — CMB Quadrupole Full Amplitude Mechanism."""
import math
import pytest

from src.core.pillar337_cmb_quadrupole_amplitude import (
    N_W, K_CS, PI_KR,
    L_QUADRUPOLE,
    C2_PLANCK_OBSERVED_NORMED, C2_LCDM_EXPECTED_CENTRAL,
    SUPPRESSION_OBSERVED_LOW, SUPPRESSION_OBSERVED_HIGH,
    F_BRAID, G_MU_STRING,
    CV_SIGMA_FRACTION, GAP_LOW, GAP_HIGH,
    separation_guard,
    mechanism_1_braided_winding,
    mechanism_2_kk_topological_defects,
    mechanism_3_finite_topology,
    mechanism_4_trans_planckian,
    cosmic_variance_assessment,
    combined_suppression_budget,
    quadrupole_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_l_quadrupole(self):
        assert L_QUADRUPOLE == 2

    def test_f_braid_formula(self):
        assert abs(F_BRAID - N_W / K_CS) < 1e-12

    def test_f_braid_approx(self):
        assert abs(F_BRAID - 5/74) < 1e-9

    def test_observed_suppression_range(self):
        assert 0 < SUPPRESSION_OBSERVED_LOW < SUPPRESSION_OBSERVED_HIGH < 1.0

    def test_suppression_significant(self):
        # Observed suppression is 40-60% range
        assert SUPPRESSION_OBSERVED_LOW > 0.3
        assert SUPPRESSION_OBSERVED_HIGH > 0.4

    def test_g_mu_string_tiny(self):
        # String tension (T_KK/M_Pl)² ~ 10⁻³⁰
        assert G_MU_STRING < 1e-28

    def test_cv_sigma_fraction(self):
        # √(2/5) ≈ 0.632 for ℓ=2
        expected = math.sqrt(2 / (2 * L_QUADRUPOLE + 1))
        assert abs(CV_SIGMA_FRACTION - expected) < 1e-9

    def test_gap_positive(self):
        # Gap is positive: understood suppression < required
        assert GAP_LOW > 0 or GAP_HIGH > 0


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent_track(self):
        assert "ADJACENT" in separation_guard()

    def test_partial_mechanism(self):
        assert "PARTIAL_MECHANISM" in separation_guard()


class TestMechanism1:
    def test_returns_dict(self):
        m1 = mechanism_1_braided_winding()
        assert isinstance(m1, dict)

    def test_suppression_fraction_correct(self):
        m1 = mechanism_1_braided_winding()
        assert abs(m1["suppression_fraction"] - F_BRAID) < 1e-9

    def test_direction_correct(self):
        m1 = mechanism_1_braided_winding()
        assert m1["direction"] == "CORRECT"

    def test_partial_mechanism(self):
        m1 = mechanism_1_braided_winding()
        assert "PARTIAL" in m1["magnitude"].upper() or "PARTIAL" in m1["epistemic_status"].upper()

    def test_suppression_percent_roughly_7(self):
        m1 = mechanism_1_braided_winding()
        assert 5.0 < m1["suppression_percent"] < 10.0


class TestMechanism2:
    def test_returns_dict(self):
        m2 = mechanism_2_kk_topological_defects()
        assert isinstance(m2, dict)

    def test_g_mu_negligible(self):
        m2 = mechanism_2_kk_topological_defects()
        assert m2["g_mu_string"] < 1e-28

    def test_suppression_negligible(self):
        m2 = mechanism_2_kk_topological_defects()
        assert m2["suppression_estimate"] < 1e-14

    def test_verdict_negligible(self):
        m2 = mechanism_2_kk_topological_defects()
        assert m2["verdict"] in ("NEGLIGIBLE", "MECHANISM_FAILS")


class TestMechanism3:
    def test_returns_dict(self):
        m3 = mechanism_3_finite_topology()
        assert isinstance(m3, dict)

    def test_pi_kr_um_correct(self):
        m3 = mechanism_3_finite_topology()
        assert abs(m3["pi_kr_um"] - 37.0) < 1e-9

    def test_verdict_external_assumption(self):
        m3 = mechanism_3_finite_topology()
        assert "EXTERNAL" in m3["verdict"] or "ASSUMPTION" in m3["verdict"]

    def test_pi_kr_needed_computed(self):
        m3 = mechanism_3_finite_topology()
        assert isinstance(m3["pi_kr_needed_for_hubble_topology"], float)
        assert m3["pi_kr_needed_for_hubble_topology"] > 0


class TestMechanism4:
    def test_returns_dict(self):
        m4 = mechanism_4_trans_planckian()
        assert isinstance(m4, dict)

    def test_verdict_inconclusive(self):
        m4 = mechanism_4_trans_planckian()
        assert "INCONCLUSIVE" in m4["verdict"].upper()

    def test_h_inf_above_m_kk(self):
        m4 = mechanism_4_trans_planckian()
        assert m4["h_inf_gev"] > m4["m_kk_gev"]


class TestCosmicVariance:
    def test_returns_dict(self):
        cv = cosmic_variance_assessment()
        assert isinstance(cv, dict)

    def test_cv_fraction_correct(self):
        cv = cosmic_variance_assessment()
        assert abs(cv["cosmic_variance_fraction"] - math.sqrt(2/5)) < 1e-9

    def test_n_sigma_positive(self):
        cv = cosmic_variance_assessment()
        assert cv["n_sigma_below_lcdm"] > 0

    def test_verdict_present(self):
        cv = cosmic_variance_assessment()
        assert cv["verdict"] in ("WITHIN_COSMIC_VARIANCE", "ANOMALOUS")

    def test_observed_c2_less_than_expected(self):
        cv = cosmic_variance_assessment()
        assert cv["c2_observed"] < cv["c2_lcdm_central"]


class TestCombinedBudget:
    def test_returns_dict(self):
        budget = combined_suppression_budget()
        assert isinstance(budget, dict)

    def test_gap_present(self):
        budget = combined_suppression_budget()
        assert "gap_low" in budget
        assert "gap_high" in budget

    def test_understood_suppression(self):
        budget = combined_suppression_budget()
        assert abs(budget["total_derived_suppression"] - F_BRAID) < 1e-9

    def test_verdict_partial_mechanism(self):
        budget = combined_suppression_budget()
        assert "PARTIAL" in budget["epistemic_verdict"]

    def test_gap_larger_than_understood(self):
        budget = combined_suppression_budget()
        # Gap should be larger than the understood suppression
        assert budget["gap_high"] > budget["total_derived_suppression"]

    def test_honest_summary_present(self):
        budget = combined_suppression_budget()
        assert isinstance(budget["honest_summary"], str)
        assert len(budget["honest_summary"]) > 50


class TestFullReport:
    def test_returns_dict(self):
        report = quadrupole_full_report()
        assert isinstance(report, dict)

    def test_pillar_number(self):
        assert quadrupole_full_report()["pillar"] == 337

    def test_has_all_mechanisms(self):
        report = quadrupole_full_report()
        assert "mechanism_1_braided_winding" in report
        assert "mechanism_2_kk_defects" in report
        assert "mechanism_3_finite_topology" in report
        assert "mechanism_4_trans_planckian" in report

    def test_partial_mechanism_status(self):
        report = quadrupole_full_report()
        assert "PARTIAL" in report["epistemic_status"]

    def test_conclusion_present(self):
        report = quadrupole_full_report()
        assert isinstance(report["conclusion"], str)
        assert len(report["conclusion"]) > 100

    def test_separation_guard_present(self):
        report = quadrupole_full_report()
        assert "ADJACENT" in report["separation_guard"]
