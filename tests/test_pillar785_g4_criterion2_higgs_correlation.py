# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 785 — G4 Criterion 2 Higgs-CMB correlation."""
from __future__ import annotations

import pytest

from src.core.pillar733_higgs_ghu_nlo_phase2_full_tower import (
    GAP_FLOOR as UPSTREAM_HIGGS_GAP_FLOOR,
    M_H_PDG,
    compute_higgs_ghu_phase2,
)
from src.core.pillar780_cmb_peak_residual_decomposition_v2 import R_IRREDUCIBLE
from src.core.pillar785_g4_criterion2_higgs_correlation import (
    CMB_GAP,
    CRITERION2_PARTIAL_SCORE,
    CRITERION2_THRESHOLD,
    G4_GATE_LABEL,
    HIGGS_GAP,
    HIGGS_MASS_GEV,
    HIGGS_PREDICTED_MASS_GEV,
    K_CS,
    KK_CUTOFF_TEV,
    PILLAR,
    STATUS,
    TEST_EXPECTATIONS,
    VERSION,
    WINDING_NUMBER,
    g4_criterion2_higgs_cross_sector_correlation,
    pillar785_summary,
)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR == 785

    def test_version(self):
        assert VERSION == "v22.10"

    def test_status(self):
        assert STATUS == "G4_CRITERION2_HIGGS_CMB_CROSS_SECTOR_CORRELATION"

    def test_requested_constants(self):
        assert HIGGS_MASS_GEV == pytest.approx(125.25)
        assert KK_CUTOFF_TEV == pytest.approx(10.0)
        assert K_CS == 74
        assert WINDING_NUMBER == 5

    def test_test_expectations_scalar_checks(self):
        assert TEST_EXPECTATIONS["scalar_checks"]["PILLAR"] == 785
        assert TEST_EXPECTATIONS["scalar_checks"]["K_CS"] == 74

    def test_threshold_is_15_percent(self):
        assert CRITERION2_THRESHOLD == pytest.approx(0.15)


class TestUpstreamConsistency:
    def test_higgs_mass_matches_pillar733(self):
        assert HIGGS_MASS_GEV == pytest.approx(M_H_PDG)

    def test_higgs_predicted_mass_matches_pillar733(self):
        assert HIGGS_PREDICTED_MASS_GEV == pytest.approx(compute_higgs_ghu_phase2(), rel=1e-12)

    def test_higgs_gap_respects_floor(self):
        assert HIGGS_GAP >= UPSTREAM_HIGGS_GAP_FLOOR

    def test_higgs_gap_is_raw_phase2_gap_here(self):
        raw_gap = (HIGGS_MASS_GEV - HIGGS_PREDICTED_MASS_GEV) / HIGGS_MASS_GEV
        assert HIGGS_GAP == pytest.approx(raw_gap, rel=1e-12)

    def test_cmb_gap_matches_pillar780_irreducible_fraction(self):
        assert CMB_GAP == pytest.approx(R_IRREDUCIBLE, rel=1e-12)

    def test_cmb_gap_exceeds_higgs_gap(self):
        assert CMB_GAP > HIGGS_GAP


class TestCriterionFunction:
    def test_returns_dict(self):
        assert isinstance(g4_criterion2_higgs_cross_sector_correlation(), dict)

    def test_required_keys(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        for key in (
            "gap_higgs",
            "gap_cmb",
            "frac_diff",
            "criterion2_met",
            "gate_label",
        ):
            assert key in result

    def test_gap_values_match_module_constants(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert result["gap_higgs"] == pytest.approx(HIGGS_GAP, rel=1e-12)
        assert result["gap_cmb"] == pytest.approx(CMB_GAP, rel=1e-12)

    def test_frac_diff_matches_formula(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        expected = abs(HIGGS_GAP - CMB_GAP) / max(HIGGS_GAP, CMB_GAP)
        assert result["frac_diff"] == pytest.approx(expected, rel=1e-12)

    def test_partial_score_matches_min_over_max(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        expected = min(HIGGS_GAP, CMB_GAP) / max(HIGGS_GAP, CMB_GAP)
        assert result["criterion2_partial_score"] == pytest.approx(expected, rel=1e-12)

    def test_partial_score_plus_frac_diff_equals_one(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        total = result["criterion2_partial_score"] + result["frac_diff"]
        assert total == pytest.approx(1.0, rel=1e-12)

    def test_frac_diff_is_positive(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert result["frac_diff"] > 0.0

    def test_frac_diff_exceeds_threshold_honestly(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert result["frac_diff"] > result["criterion2_threshold"]

    def test_criterion2_not_met(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert result["criterion2_met"] is False

    def test_gate_label_remains_candidate(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert result["gate_label"].startswith("TYPE_B_CANDIDATE")
        assert result["gate_label"] == G4_GATE_LABEL

    def test_gate_label_includes_quantified_partial_score(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert f"{result['criterion2_partial_score']:.4f}" in result["gate_label"]

    def test_if_met_label_is_exposed(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert result["gate_label_if_met"] == "TYPE_B_STRUCTURAL_FLOOR"

    def test_cutoff_ratio_is_dimensionless_and_small(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert result["higgs_to_cutoff_ratio"] == pytest.approx(HIGGS_MASS_GEV / 10000.0, rel=1e-12)
        assert result["higgs_to_cutoff_ratio"] < 0.02

    def test_cross_sector_pair_names(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert result["cross_sector_pair"] == ("HIGGS_GAP", "CMB_SUPPRESSION_GAP")

    def test_honest_note_mentions_no_forced_upgrade(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert "No upgrade" in result["honest_note"]


class TestNumerics:
    def test_higgs_gap_value(self):
        assert HIGGS_GAP == pytest.approx(0.2753491347887091, rel=1e-12)

    def test_cmb_gap_value(self):
        assert CMB_GAP == pytest.approx(0.3364656438266557, rel=1e-12)

    def test_frac_diff_value(self):
        result = g4_criterion2_higgs_cross_sector_correlation()
        assert result["frac_diff"] == pytest.approx(0.18164264363818777, rel=1e-12)

    def test_partial_score_value(self):
        assert CRITERION2_PARTIAL_SCORE == pytest.approx(0.8183573563618122, rel=1e-12)


class TestSummary:
    def test_summary_returns_dict(self):
        assert isinstance(pillar785_summary(), dict)

    def test_summary_required_keys(self):
        result = pillar785_summary()
        for key in ("verdict", "gate_string", "criterion2_met", "frac_diff"):
            assert key in result

    def test_summary_gate_matches_function(self):
        result = pillar785_summary()
        corr = g4_criterion2_higgs_cross_sector_correlation()
        assert result["gate_string"] == corr["gate_label"]

    def test_summary_verdict_is_honest(self):
        result = pillar785_summary()
        assert "remains TYPE_B_CANDIDATE" in result["verdict"]

    def test_summary_reports_nonzero_partial_score(self):
        result = pillar785_summary()
        assert 0.0 < result["criterion2_partial_score"] < 1.0
