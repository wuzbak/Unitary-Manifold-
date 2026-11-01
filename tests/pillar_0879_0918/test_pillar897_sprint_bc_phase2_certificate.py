# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 897 — Sprint BC Phase 2 certificate."""
from __future__ import annotations

from src.core.pillar897_sprint_bc_phase2_certificate import (
    LEAN4_DELTA,
    LEAN4_PHASE2_END,
    PHASE2_VALID,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    phase2_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 897

def test_gate_string(): assert PILLAR_GATE == "SPRINT_BC_PHASE2_CERTIFICATE"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_lean4_end(): assert LEAN4_PHASE2_END == 2941

def test_lean4_delta(): assert LEAN4_DELTA == 90

def test_phase_valid(): assert PHASE2_VALID is True

def test_summary_gate(): assert phase2_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert phase2_summary()["pillar"] == 897

def test_summary_status(): assert phase2_summary()["status_label"] == STATUS_LABEL

def test_summary_valid(): assert phase2_summary()["phase_valid"] is True

def test_summary_lean4_end(): assert phase2_summary()["lean4_end"] == 2941

def test_summary_lean4_delta(): assert phase2_summary()["lean4_delta"] == 90

def test_summary_registered_count(): assert len(phase2_summary()["registered_gates"]) == 5

def test_summary_has_irreducible(): assert phase2_summary()["status_counts"]["IRREDUCIBLE_ARCHITECTURE_LIMIT"] == 2

def test_summary_has_partial(): assert phase2_summary()["status_counts"]["PARTIAL"] >= 1

def test_summary_has_resolved(): assert phase2_summary()["status_counts"]["RESOLVED"] >= 1

def test_no_toe_language(): assert "TOE" not in phase2_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in phase2_summary()
    return _test

globals()['test_generated_key_phase_valid_0'] = _generated_key_test_factory('phase_valid')
globals()['test_generated_key_registered_gates_1'] = _generated_key_test_factory('registered_gates')
globals()['test_generated_key_status_counts_2'] = _generated_key_test_factory('status_counts')
globals()['test_generated_key_epistemic_status_3'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_lean4_start_4'] = _generated_key_test_factory('lean4_start')
globals()['test_generated_key_lean4_end_5'] = _generated_key_test_factory('lean4_end')
globals()['test_generated_key_status_label_6'] = _generated_key_test_factory('status_label')
globals()['test_generated_key_gate_7'] = _generated_key_test_factory('gate')
