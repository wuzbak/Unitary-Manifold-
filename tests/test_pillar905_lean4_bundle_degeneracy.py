# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 905 — Lean4 bundle degeneracy bridge."""
from __future__ import annotations

from src.core.pillar905_lean4_bundle_degeneracy import (
    LEAN4_FILE,
    LEAN4_NAMESPACE,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    lean4_bundle_degeneracy_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 905

def test_gate_string(): assert PILLAR_GATE == "LEAN4_BUNDLE_DEGENERACY_RESOLUTION"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_file_name(): assert LEAN4_FILE == "BundleDegeneracyResolution.lean"

def test_namespace(): assert LEAN4_NAMESPACE == "UnitaryManifold.BundleDegeneracy"

def test_theorem_count_constant(): assert LEAN4_THEOREM_COUNT == 40

def test_ledger_before(): assert LEAN4_TOTAL_BEFORE == 3101

def test_ledger_after(): assert LEAN4_TOTAL_AFTER == 3141

def test_ledger_arithmetic(): assert LEAN4_TOTAL_AFTER - LEAN4_TOTAL_BEFORE == 40

def test_summary_gate(): assert lean4_bundle_degeneracy_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert lean4_bundle_degeneracy_summary()["pillar"] == 905

def test_summary_status(): assert lean4_bundle_degeneracy_summary()["status_label"] == STATUS_LABEL

def test_summary_namespace_present(): assert lean4_bundle_degeneracy_summary()["namespace_present"] is True

def test_summary_master_present(): assert lean4_bundle_degeneracy_summary()["master_theorem_present"] is True

def test_summary_theorem_count(): assert lean4_bundle_degeneracy_summary()["n_theorems"] == 40

def test_summary_match(): assert lean4_bundle_degeneracy_summary()["theorem_count_matches"] is True

def test_summary_total_after(): assert lean4_bundle_degeneracy_summary()["lean4_total_after"] == 3141

def test_no_toe_language(): assert "TOE" not in lean4_bundle_degeneracy_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in lean4_bundle_degeneracy_summary()
    return _test

globals()['test_generated_key_lean4_file_0'] = _generated_key_test_factory('lean4_file')
globals()['test_generated_key_namespace_present_1'] = _generated_key_test_factory('namespace_present')
globals()['test_generated_key_master_theorem_present_2'] = _generated_key_test_factory('master_theorem_present')
globals()['test_generated_key_n_theorems_3'] = _generated_key_test_factory('n_theorems')
globals()['test_generated_key_theorem_count_matches_4'] = _generated_key_test_factory('theorem_count_matches')
globals()['test_generated_key_epistemic_status_5'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_status_label_6'] = _generated_key_test_factory('status_label')
