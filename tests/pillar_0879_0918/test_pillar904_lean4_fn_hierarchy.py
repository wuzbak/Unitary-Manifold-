# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 904 — Lean4 FN hierarchy bridge."""
from __future__ import annotations

from src.core.pillar904_lean4_fn_hierarchy import (
    LEAN4_FILE,
    LEAN4_FN_THEOREMS,
    LEAN4_NAMESPACE,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    lean4_fn_hierarchy_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 904

def test_gate_string(): assert PILLAR_GATE == "LEAN4_FN_HIERARCHY_THEOREMS"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_file_name(): assert LEAN4_FILE == "FNHierarchyTheorems.lean"

def test_namespace(): assert LEAN4_NAMESPACE == "UnitaryManifold.FNHierarchy"

def test_theorem_count_constant(): assert LEAN4_THEOREM_COUNT == 60

def test_fn_theorems_constant(): assert LEAN4_FN_THEOREMS == 60

def test_ledger_before(): assert LEAN4_TOTAL_BEFORE == 3041

def test_ledger_after(): assert LEAN4_TOTAL_AFTER == 3101

def test_ledger_arithmetic(): assert LEAN4_TOTAL_AFTER - LEAN4_TOTAL_BEFORE == 60

def test_summary_gate(): assert lean4_fn_hierarchy_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert lean4_fn_hierarchy_summary()["pillar"] == 904

def test_summary_status(): assert lean4_fn_hierarchy_summary()["status_label"] == STATUS_LABEL

def test_summary_namespace_present(): assert lean4_fn_hierarchy_summary()["namespace_present"] is True

def test_summary_master_present(): assert lean4_fn_hierarchy_summary()["master_theorem_present"] is True

def test_summary_theorem_count(): assert lean4_fn_hierarchy_summary()["n_theorems"] == 60

def test_summary_match(): assert lean4_fn_hierarchy_summary()["theorem_count_matches"] is True

def test_summary_total_after(): assert lean4_fn_hierarchy_summary()["lean4_total_after"] == 3101

def test_no_toe_language(): assert "TOE" not in lean4_fn_hierarchy_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in lean4_fn_hierarchy_summary()
    return _test

globals()['test_generated_key_lean4_file_0'] = _generated_key_test_factory('lean4_file')
globals()['test_generated_key_namespace_present_1'] = _generated_key_test_factory('namespace_present')
globals()['test_generated_key_master_theorem_present_2'] = _generated_key_test_factory('master_theorem_present')
globals()['test_generated_key_n_theorems_3'] = _generated_key_test_factory('n_theorems')
globals()['test_generated_key_theorem_count_matches_4'] = _generated_key_test_factory('theorem_count_matches')
globals()['test_generated_key_lean4_fn_theorems_5'] = _generated_key_test_factory('lean4_fn_theorems')
