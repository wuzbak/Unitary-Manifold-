# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 892 — bundle third filter."""
from __future__ import annotations

from src.sixd.pillar892_ngen_bundle_third_filter import (
    ANOMALY_INFLOW_FILTER_APPLIED,
    COBORDISM_FILTER_APPLIED,
    DEGENERACY_AFTER_FILTER,
    NGEN_BUNDLE_GATE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    bundle_third_filter_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 892

def test_gate_string(): assert PILLAR_GATE == "NGEN_6D_BUNDLE_THIRD_FILTER"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_filters_applied_one(): assert COBORDISM_FILTER_APPLIED is True

def test_filters_applied_two(): assert ANOMALY_INFLOW_FILTER_APPLIED is True

def test_degeneracy_expected(): assert DEGENERACY_AFTER_FILTER == 2

def test_result_gate_limit(): assert NGEN_BUNDLE_GATE.endswith("IRREDUCIBLE_ARCHITECTURE_LIMIT")

def test_summary_gate(): assert bundle_third_filter_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert bundle_third_filter_summary()["pillar"] == 892

def test_summary_status(): assert bundle_third_filter_summary()["status_label"] == STATUS_LABEL

def test_summary_before_after(): assert bundle_third_filter_summary()["degeneracy_before_filter"] >= bundle_third_filter_summary()["degeneracy_after_filter"]

def test_summary_after_equals_two(): assert bundle_third_filter_summary()["degeneracy_after_filter"] == 2

def test_summary_filters_true(): assert bundle_third_filter_summary()["cobordism_filter_applied"] is True

def test_summary_inflow_true(): assert bundle_third_filter_summary()["anomaly_inflow_filter_applied"] is True

def test_summary_survivor_count(): assert len(bundle_third_filter_summary()["surviving_bundles"]) == 2

def test_summary_first_bundle_has_c1(): assert bundle_third_filter_summary()["surviving_bundles"][0]["c1"] == 3

def test_summary_all_have_target_c1(): assert all(row["c1"] == 3 for row in bundle_third_filter_summary()["surviving_bundles"])

def test_summary_charges_survive(): assert {row["u1_charge"] for row in bundle_third_filter_summary()["surviving_bundles"]} == {1, 3}

def test_no_toe_language(): assert "TOE" not in bundle_third_filter_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in bundle_third_filter_summary()
    return _test

globals()['test_generated_key_result_gate_0'] = _generated_key_test_factory('result_gate')
globals()['test_generated_key_surviving_bundles_1'] = _generated_key_test_factory('surviving_bundles')
globals()['test_generated_key_degeneracy_before_filter_2'] = _generated_key_test_factory('degeneracy_before_filter')
globals()['test_generated_key_degeneracy_after_filter_3'] = _generated_key_test_factory('degeneracy_after_filter')
globals()['test_generated_key_epistemic_status_4'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_status_label_5'] = _generated_key_test_factory('status_label')
