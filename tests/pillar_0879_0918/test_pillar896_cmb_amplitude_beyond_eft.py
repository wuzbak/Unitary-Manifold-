# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 896 — beyond-EFT CMB amplitude survey."""
from __future__ import annotations

from src.core.pillar896_cmb_amplitude_beyond_eft import (
    CANDIDATES,
    CMB_BEYOND_EFT_GATE,
    IN_SCOPE_CANDIDATES,
    IRREDUCIBLE_CANDIDATES,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    beyond_eft_survey_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 896

def test_gate_string(): assert PILLAR_GATE == "CMB_AMPLITUDE_BEYOND_EFT_SURVEY"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_candidate_count(): assert len(CANDIDATES) == 4

def test_candidate_labels(): assert {row["label"] for row in CANDIDATES} == {"A", "B", "C", "D"}

def test_in_scope_count(): assert len(IN_SCOPE_CANDIDATES) == 2

def test_irreducible_count(): assert len(IRREDUCIBLE_CANDIDATES) == 2

def test_gate_arch_limit(): assert CMB_BEYOND_EFT_GATE == "ARCHITECTURE_LIMIT_CONFIRMED"

def test_summary_gate(): assert beyond_eft_survey_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert beyond_eft_survey_summary()["pillar"] == 896

def test_summary_status(): assert beyond_eft_survey_summary()["status_label"] == STATUS_LABEL

def test_summary_result_gate(): assert beyond_eft_survey_summary()["result_gate"] == CMB_BEYOND_EFT_GATE

def test_summary_candidate_count(): assert len(beyond_eft_survey_summary()["candidates"]) == 4

def test_summary_in_scope_matches(): assert beyond_eft_survey_summary()["in_scope_candidates"] == IN_SCOPE_CANDIDATES

def test_summary_irreducible_matches(): assert beyond_eft_survey_summary()["irreducible_candidates"] == IRREDUCIBLE_CANDIDATES

def test_summary_max_candidate_small(): assert beyond_eft_survey_summary()["max_candidate_contribution"] < 1.0

def test_summary_required_range(): assert beyond_eft_survey_summary()["required_suppression_fraction_range"] == [3.0, 6.0]

def test_no_toe_language(): assert "TOE" not in beyond_eft_survey_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in beyond_eft_survey_summary()
    return _test

globals()['test_generated_key_kk_contribution_fraction_0'] = _generated_key_test_factory('kk_contribution_fraction')
globals()['test_generated_key_result_gate_1'] = _generated_key_test_factory('result_gate')
globals()['test_generated_key_required_suppression_fraction_range_2'] = _generated_key_test_factory('required_suppression_fraction_range')
globals()['test_generated_key_max_candidate_contribution_3'] = _generated_key_test_factory('max_candidate_contribution')
globals()['test_generated_key_epistemic_status_4'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_status_label_5'] = _generated_key_test_factory('status_label')
globals()['test_generated_key_candidates_6'] = _generated_key_test_factory('candidates')
