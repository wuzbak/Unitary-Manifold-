# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 903 — Sprint BC Phase 3 certificate."""
from __future__ import annotations

from src.core.pillar903_sprint_bc_phase3_certificate import (
    LEAN4_DELTA,
    LEAN4_PHASE3_END,
    PHASE3_VALID,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    phase3_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 903

def test_gate_string(): assert PILLAR_GATE == "SPRINT_BC_PHASE3_CERTIFICATE"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_lean4_end(): assert LEAN4_PHASE3_END == 3041

def test_lean4_delta(): assert LEAN4_DELTA == 100

def test_phase_valid(): assert PHASE3_VALID is True

def test_summary_gate(): assert phase3_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert phase3_summary()["pillar"] == 903

def test_summary_status(): assert phase3_summary()["status_label"] == STATUS_LABEL

def test_summary_valid(): assert phase3_summary()["phase_valid"] is True

def test_summary_lean4_end(): assert phase3_summary()["lean4_end"] == 3041

def test_summary_lean4_delta(): assert phase3_summary()["lean4_delta"] == 100

def test_summary_registered_count(): assert len(phase3_summary()["registered_statuses"]) == 5

def test_summary_has_tension(): assert "TENSION_PERSISTS" in set(phase3_summary()["registered_statuses"].values())

def test_summary_has_resolved(): assert "RESOLVED" in set(phase3_summary()["registered_statuses"].values())

def test_no_toe_language(): assert "TOE" not in phase3_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in phase3_summary()
    return _test

globals()['test_generated_key_phase_valid_0'] = _generated_key_test_factory('phase_valid')
globals()['test_generated_key_registered_statuses_1'] = _generated_key_test_factory('registered_statuses')
globals()['test_generated_key_epistemic_status_2'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_lean4_start_3'] = _generated_key_test_factory('lean4_start')
globals()['test_generated_key_lean4_end_4'] = _generated_key_test_factory('lean4_end')
globals()['test_generated_key_status_label_5'] = _generated_key_test_factory('status_label')
globals()['test_generated_key_gate_6'] = _generated_key_test_factory('gate')
globals()['test_generated_key_pillar_7'] = _generated_key_test_factory('pillar')
globals()['test_generated_key_lean4_delta_8'] = _generated_key_test_factory('lean4_delta')
