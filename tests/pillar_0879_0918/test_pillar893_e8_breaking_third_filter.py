# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 893 — E8 third filter."""
from __future__ import annotations

from src.sixd.pillar893_e8_breaking_third_filter import (
    E8_DEGENERACY_FINAL,
    E8_GATE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    TORSION_CLASS_FILTER,
    WGC_FILTER,
    e8_third_filter_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 893

def test_gate_string(): assert PILLAR_GATE == "E8_BREAKING_THIRD_FILTER"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_torsion_filter_true(): assert TORSION_CLASS_FILTER is True

def test_wgc_filter_true(): assert WGC_FILTER is True

def test_final_degeneracy_two(): assert E8_DEGENERACY_FINAL == 2

def test_e8_gate_irreducible(): assert E8_GATE == "IRREDUCIBLE_ARCHITECTURE_LIMIT"

def test_summary_gate(): assert e8_third_filter_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert e8_third_filter_summary()["pillar"] == 893

def test_summary_status(): assert e8_third_filter_summary()["status_label"] == STATUS_LABEL

def test_summary_before_after(): assert e8_third_filter_summary()["degeneracy_before_filter"] == e8_third_filter_summary()["e8_degeneracy_final"]

def test_summary_chain_count(): assert len(e8_third_filter_summary()["surviving_chains"]) == 2

def test_summary_chains_have_sm(): assert all(row["contains_sm"] for row in e8_third_filter_summary()["surviving_chains"])

def test_summary_chains_have_chirality(): assert all(row["chiral_matter"] for row in e8_third_filter_summary()["surviving_chains"])

def test_summary_indices_survive(): assert {row["embedding_index"] for row in e8_third_filter_summary()["surviving_chains"]} == {1, 2}

def test_summary_torsion_true(): assert e8_third_filter_summary()["torsion_class_filter"] is True

def test_summary_wgc_true(): assert e8_third_filter_summary()["wgc_filter"] is True

def test_no_toe_language(): assert "TOE" not in e8_third_filter_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in e8_third_filter_summary()
    return _test

globals()['test_generated_key_result_gate_0'] = _generated_key_test_factory('result_gate')
globals()['test_generated_key_surviving_chains_1'] = _generated_key_test_factory('surviving_chains')
globals()['test_generated_key_degeneracy_before_filter_2'] = _generated_key_test_factory('degeneracy_before_filter')
globals()['test_generated_key_e8_degeneracy_final_3'] = _generated_key_test_factory('e8_degeneracy_final')
globals()['test_generated_key_epistemic_status_4'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_status_label_5'] = _generated_key_test_factory('status_label')
globals()['test_generated_key_torsion_class_filter_6'] = _generated_key_test_factory('torsion_class_filter')
