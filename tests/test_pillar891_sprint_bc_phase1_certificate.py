# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 891 — Sprint BC Phase 1 certificate."""
from __future__ import annotations

from src.core.pillar891_sprint_bc_phase1_certificate import (
    LEAN4_DELTA,
    LEAN4_PHASE1_END,
    LEAN4_START,
    PHASE1_VALID,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REGISTERED_GATES,
    STATUS_LABEL,
    phase1_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 891

def test_gate_string(): assert PILLAR_GATE == "SPRINT_BC_PHASE1_CERTIFICATE"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_lean4_start(): assert LEAN4_START == 2741

def test_lean4_end(): assert LEAN4_PHASE1_END == 2851

def test_lean4_delta(): assert LEAN4_DELTA == 110

def test_lean4_arithmetic(): assert LEAN4_START + LEAN4_DELTA == LEAN4_PHASE1_END

def test_registered_gate_count(): assert len(REGISTERED_GATES) == 4

def test_registered_pillars(): assert [row["pillar"] for row in REGISTERED_GATES] == [887, 888, 889, 890]

def test_phase1_valid(): assert PHASE1_VALID is True

def test_summary_gate(): assert phase1_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert phase1_summary()["pillar"] == 891

def test_summary_status(): assert phase1_summary()["status_label"] == STATUS_LABEL

def test_summary_valid(): assert phase1_summary()["phase_valid"] is True

def test_summary_lean4_start(): assert phase1_summary()["lean4_start"] == 2741

def test_summary_lean4_end(): assert phase1_summary()["lean4_end"] == 2851

def test_summary_lean4_delta(): assert phase1_summary()["lean4_delta"] == 110

def test_summary_counts_keys(): assert set(phase1_summary()["counts"]) == {"resolved", "partial", "tension"}

def test_summary_registered_same(): assert phase1_summary()["registered_gates"] == REGISTERED_GATES

def test_summary_one_resolved(): assert phase1_summary()["counts"]["resolved"] == 1

def test_summary_two_tension_or_less(): assert phase1_summary()["counts"]["tension"] <= 2

def test_summary_partial_nonzero(): assert phase1_summary()["counts"]["partial"] >= 1

def test_no_toe_language(): assert "TOE" not in phase1_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in phase1_summary()
    return _test

globals()['test_generated_key_phase_valid_0'] = _generated_key_test_factory('phase_valid')
globals()['test_generated_key_registered_gates_1'] = _generated_key_test_factory('registered_gates')
globals()['test_generated_key_counts_2'] = _generated_key_test_factory('counts')
globals()['test_generated_key_epistemic_status_3'] = _generated_key_test_factory('epistemic_status')
