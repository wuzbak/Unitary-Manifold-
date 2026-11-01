# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 909 — Sprint BC master bridge."""
from __future__ import annotations

from src.core.pillar909_sprint_bc_master_bridge import (
    LEAN4_PHASE4_END,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    sprint_bc_master_bridge_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 909

def test_gate_string(): assert PILLAR_GATE == "SPRINT_BC_MASTER_BRIDGE"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_lean4_end(): assert LEAN4_PHASE4_END == 3176

def test_summary_gate(): assert sprint_bc_master_bridge_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert sprint_bc_master_bridge_summary()["pillar"] == 909

def test_summary_status(): assert sprint_bc_master_bridge_summary()["status_label"] == STATUS_LABEL

def test_summary_bridge_valid(): assert sprint_bc_master_bridge_summary()["bridge_valid"] is True

def test_summary_namespace_present(): assert sprint_bc_master_bridge_summary()["namespace_present"] is True

def test_summary_master_present(): assert sprint_bc_master_bridge_summary()["master_theorem_present"] is True

def test_summary_all_files_present(): assert sprint_bc_master_bridge_summary()["all_files_present"] is True

def test_summary_bridge_theorems(): assert sprint_bc_master_bridge_summary()["bridge_theorems"] == 35

def test_summary_total_delta(): assert sprint_bc_master_bridge_summary()["total_delta"] == 435

def test_no_toe_language(): assert "TOE" not in sprint_bc_master_bridge_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in sprint_bc_master_bridge_summary()
    return _test

globals()['test_generated_key_bridge_valid_0'] = _generated_key_test_factory('bridge_valid')
globals()['test_generated_key_lean4_file_1'] = _generated_key_test_factory('lean4_file')
globals()['test_generated_key_namespace_present_2'] = _generated_key_test_factory('namespace_present')
globals()['test_generated_key_master_theorem_present_3'] = _generated_key_test_factory('master_theorem_present')
globals()['test_generated_key_all_files_present_4'] = _generated_key_test_factory('all_files_present')
globals()['test_generated_key_bridge_theorems_5'] = _generated_key_test_factory('bridge_theorems')
globals()['test_generated_key_lean4_phase4_end_6'] = _generated_key_test_factory('lean4_phase4_end')
globals()['test_generated_key_total_delta_7'] = _generated_key_test_factory('total_delta')
globals()['test_generated_key_epistemic_status_8'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_status_label_9'] = _generated_key_test_factory('status_label')
globals()['test_generated_key_gate_10'] = _generated_key_test_factory('gate')
