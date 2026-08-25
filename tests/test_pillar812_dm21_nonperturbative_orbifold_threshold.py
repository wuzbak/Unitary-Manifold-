# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import math

import pytest

from src.core.pillar812_dm21_nonperturbative_orbifold_threshold import (
    DM21_AFTER_EXACT_THRESHOLD,
    EXACT_THRESHOLD_CORRECTION,
    G4_RECLASSIFICATION_GATE,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    NONPERTURBATIVE_OVERLAP_COEFFICIENT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    SUB_0P8SIGMA_ACHIEVED,
    TENSION_AFTER_EXACT_THRESHOLD,
    OrbifoldThresholdResult,
    exact_fixed_point_overlap,
    g4_reclassification_summary,
    nonperturbative_orbifold_threshold,
)
from src.core.pillar773_dm21_nlo_lattice_correction import (
    DELTA_C,
    DM21_AFTER_NLO,
    DM21_PDG_EV2,
    DM21_SIGMA_EV2,
    SIN2_THETA12,
)


class TestConstants:
    def test_pillar_number_and_gate(self):
        assert PILLAR_NUMBER == 812
        assert PILLAR_GATE == "DM21_NONPERTURBATIVE_ORBIFOLD_THRESHOLD_SUB_0P8SIGMA"

    def test_lean4_accounting(self):
        assert LEAN4_THEOREM_COUNT == 15
        assert LEAN4_TOTAL_AFTER == 1336

    def test_reclassification_gate(self):
        assert G4_RECLASSIFICATION_GATE == "G4_INTERNAL_TYPE_B_CANDIDATE_RETIRED"


class TestExactOverlap:
    def test_exact_overlap_formula(self):
        expected = SIN2_THETA12 / math.pi
        assert abs(exact_fixed_point_overlap() - expected) < 1e-15

    def test_overlap_coefficient_matches_constant(self):
        assert abs(NONPERTURBATIVE_OVERLAP_COEFFICIENT - SIN2_THETA12 / math.pi) < 1e-15

    def test_invalid_overlap_input_raises(self):
        with pytest.raises(ValueError):
            exact_fixed_point_overlap(-0.1)


class TestThresholdAudit:
    def test_threshold_result_type(self):
        result = nonperturbative_orbifold_threshold()
        assert isinstance(result, OrbifoldThresholdResult)

    def test_threshold_correction_formula(self):
        assert abs(EXACT_THRESHOLD_CORRECTION - DELTA_C * NONPERTURBATIVE_OVERLAP_COEFFICIENT) < 1e-15

    def test_threshold_improves_dm21(self):
        assert DM21_AFTER_EXACT_THRESHOLD > DM21_AFTER_NLO

    def test_sigma_target_achieved(self):
        assert SUB_0P8SIGMA_ACHIEVED is True
        assert TENSION_AFTER_EXACT_THRESHOLD < 0.8

    def test_explicit_sigma_value(self):
        expected = abs(DM21_PDG_EV2 - DM21_AFTER_EXACT_THRESHOLD) / DM21_SIGMA_EV2
        assert abs(TENSION_AFTER_EXACT_THRESHOLD - expected) < 1e-15

    def test_gate_matches_result(self):
        result = nonperturbative_orbifold_threshold()
        assert result.gate == PILLAR_GATE
        assert result.no_new_parameters is True


class TestReclassificationSummary:
    def test_summary_status(self):
        summary = g4_reclassification_summary()
        assert summary["pillar"] == 812
        assert summary["status"] == PILLAR_GATE

    def test_summary_retires_g4_candidate(self):
        summary = g4_reclassification_summary()
        assert summary["prior_g4_status"] == "TYPE_B_CANDIDATE"
        assert summary["sub_0p8sigma_achieved"] is True
        assert summary["reclassification_gate"] == "G4_INTERNAL_TYPE_B_CANDIDATE_RETIRED"
