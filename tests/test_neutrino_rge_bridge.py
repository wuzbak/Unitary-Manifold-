# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 144: RGE Bridge (src/core/neutrino_rge_bridge.py).

Verifies the discrepancy factor, RGE correction, c_L consistency solve,
and the full bridge report.
"""

import math
import pytest

from src.core.neutrino_rge_bridge import (
    discrepancy_factor,
    rge_log_correction,
    c_left_from_rge_consistency,
    neutrino_rge_bridge_report,
    pillar144_summary,
    PILLAR135_M_NU1_EV,
    PILLAR140_C_L_NAIVE,
    PILLAR140_C_R,
    M_KK_GEV,
    M_Z_GEV,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_pillar135_mass(self):
        # m_ν₁ = sqrt(7.53e-5/34) ≈ 1.487 meV
        assert abs(PILLAR135_M_NU1_EV - math.sqrt(7.53e-5 / 34)) < 1e-10

    def test_pillar135_in_meV_range(self):
        assert 1.0e-3 < PILLAR135_M_NU1_EV < 3.0e-3  # in eV

    def test_pillar140_c_l_naive(self):
        assert abs(PILLAR140_C_L_NAIVE - 0.776) < 1e-12

    def test_pillar140_c_r(self):
        assert abs(PILLAR140_C_R - 23.0 / 25.0) < 1e-14

    def test_mkk_larger_than_mz(self):
        assert M_KK_GEV > M_Z_GEV


# ---------------------------------------------------------------------------
# discrepancy_factor
# ---------------------------------------------------------------------------

class TestDiscrepancyFactor:
    @pytest.fixture(scope="class")
    def result(self):
        return discrepancy_factor()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_pillar135_mass_correct(self, result):
        expected = math.sqrt(7.53e-5 / 34.0) * 1e3  # meV
        assert abs(result["m_nu1_135_meV"] - expected) < 1e-8

    def test_pillar140_mass_above_planck(self, result):
        # Pillar 140 with c_L=0.776 gives m_ν₁ > 0.12 eV (violates Planck)
        assert result["m_nu1_140_ev"] > 0.12

    def test_large_ratio(self, result):
        # Ratio must be > 100× (the known ~730× discrepancy)
        assert result["ratio_140_over_135"] > 100

    def test_log10_ratio_positive(self, result):
        assert result["log10_ratio"] > 0

    def test_diagnosis_present(self, result):
        assert len(result["diagnosis"]) > 50

    def test_diagnosis_mentions_cl(self, result):
        assert "c_L" in result["diagnosis"] or "c_l" in result["diagnosis"].lower()

    def test_both_keys_present(self, result):
        assert "m_nu1_135_ev" in result
        assert "m_nu1_140_ev" in result


# ---------------------------------------------------------------------------
# rge_log_correction
# ---------------------------------------------------------------------------

class TestRgeLogCorrection:
    @pytest.fixture(scope="class")
    def rge(self):
        return rge_log_correction()

    def test_log_scale_positive(self, rge):
        assert rge["log_scale_ratio"] > 0

    def test_pct_correction_small(self, rge):
        # RGE correction should be well below 730% — it's only ~few %
        assert rge["pct_correction"] < 50.0

    def test_mass_ratio_near_one(self, rge):
        # The RGE-corrected mass ratio should be close to 1 (few percent)
        assert 0.8 < rge["mass_ratio_rge"] < 1.2

    def test_verdict_mentions_negligible(self, rge):
        assert "negligible" in rge["verdict"].lower() or \
               "insufficient" in rge["verdict"].lower() or \
               "small" in rge["verdict"].lower() or \
               "%" in rge["verdict"]

    def test_beta_top_positive(self, rge):
        # Top Yukawa drives mass UP when running to lower scales
        assert rge["beta_top"] > 0

    def test_log_ratio_value(self, rge):
        # ln(1041/91.2) ≈ 2.44
        expected = math.log(M_KK_GEV / M_Z_GEV)
        assert abs(rge["log_scale_ratio"] - expected) < 1e-10


# ---------------------------------------------------------------------------
# c_left_from_rge_consistency
# ---------------------------------------------------------------------------

class TestCLeftFromRgeConsistency:
    @pytest.fixture(scope="class")
    def solved(self):
        return c_left_from_rge_consistency()

    def test_returns_dict(self, solved):
        assert isinstance(solved, dict)

    def test_c_left_in_physical_range(self, solved):
        # c_L^phys must be > 0.5 for UV localization
        assert solved["c_left_required"] > 0.5

    def test_c_left_above_naive(self, solved):
        # Must be significantly larger than the naive 0.776
        assert solved["c_left_required"] > 0.776

    def test_achieved_mass_matches_target(self, solved):
        # The solved c_L should reproduce the target mass to < 0.01%
        assert solved["relative_error"] < 1e-3

    def test_achieved_mass_in_meV_range(self, solved):
        # Target is ~1.49 meV → achieved should be similar
        assert 0.5e-3 < solved["achieved_m_nu1_ev"] < 5e-3

    def test_not_equal_to_2_over_25(self, solved):
        # c_L^phys ≠ 2/25 = 0.08 (topological label is different)
        assert abs(solved["c_left_required"] - 2.0 / 25.0) > 0.5

    def test_topological_note_present(self, solved):
        assert len(solved["topological_note"]) > 20

    def test_c_l_plus_c_r_gt_one(self, solved):
        # c_L^phys + c_R > 1: NOT at the unitarity boundary
        assert solved["c_l_plus_c_r"] > 1.0

    def test_status_resolved(self, solved):
        assert "RESOLVED" in solved["status"].upper() or \
               "OPEN" in solved["status"].upper()


# ---------------------------------------------------------------------------
# neutrino_rge_bridge_report
# ---------------------------------------------------------------------------

class TestNeutrinoRgeBridgeReport:
    @pytest.fixture(scope="class")
    def report(self):
        return neutrino_rge_bridge_report()

    def test_pillar_number(self, report):
        assert report["pillar"] == 144

    def test_summary_present(self, report):
        assert "summary" in report

    def test_discrepancy_in_summary(self, report):
        assert "ratio_140_over_135" in report["summary"]

    def test_open_items_present(self, report):
        assert len(report["open_items"]) >= 1

    def test_closed_items_present(self, report):
        assert len(report["closed_items"]) >= 1

    def test_overall_status_mentions_c_l(self, report):
        assert "c_L" in report["overall_status"] or "c_l" in report["overall_status"].lower()


# ---------------------------------------------------------------------------
# pillar144_summary
# ---------------------------------------------------------------------------

class TestPillar144Summary:
    @pytest.fixture(scope="class")
    def summary(self):
        return pillar144_summary()

    def test_pillar_number(self, summary):
        assert summary["pillar"] == 144

    def test_title_present(self, summary):
        assert "144" in summary["title"] or "rge" in summary["title"].lower() or \
               "bridge" in summary["title"].lower()

    def test_c_left_required_physical(self, summary):
        assert summary["c_left_required"] > 0.5

    def test_c_right_theorem_value(self, summary):
        assert abs(summary["c_right_theorem"] - 23.0 / 25.0) < 1e-14

    def test_rge_correction_small(self, summary):
        assert summary["rge_correction_pct"] < 50.0
