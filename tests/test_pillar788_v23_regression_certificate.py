# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 788 — v23 Sprint Regression Certificate."""

from __future__ import annotations

import pytest

from src.core.pillar788_v23_regression_certificate import (
    PILLAR,
    VERSION,
    STATUS,
    SPRINT_NAME,
    SPRINT_DATE,
    TESTS_PASSED_FLOOR,
    LEAN4_THEOREMS_FLOOR,
    NEXT_PILLAR_SLOT,
    V23_PILLARS,
    V23_EPISTEMIC_GATES,
    V23_APPLICATION,
    regression_certificate_summary,
    TEST_EXPECTATIONS,
)


def test_pillar_number():
    assert PILLAR == 788

def test_version():
    assert VERSION == "v23.0"

def test_status():
    assert STATUS == "V23_REGRESSION_CERTIFICATE_ISSUED"

def test_sprint_name_contains_v23():
    assert "v23" in SPRINT_NAME.lower()

def test_sprint_date():
    assert SPRINT_DATE == "2026-08-20"

def test_tests_passed_floor():
    assert TESTS_PASSED_FLOOR >= 57_000

def test_lean4_floor():
    assert LEAN4_THEOREMS_FLOOR >= 1000

def test_next_pillar_slot():
    assert NEXT_PILLAR_SLOT == 789

def test_v23_pillars_count():
    assert len(V23_PILLARS) == 3

def test_v23_pillars_numbers():
    nums = [p["pillar"] for p in V23_PILLARS]
    assert 786 in nums
    assert 787 in nums
    assert 788 in nums

def test_v23_pillars_have_gates():
    for p in V23_PILLARS:
        assert "gate" in p
        assert len(p["gate"]) > 5

def test_v23_epistemic_gates_p786():
    assert "P786_STABILITY_BASIN" in V23_EPISTEMIC_GATES
    assert V23_EPISTEMIC_GATES["P786_STABILITY_BASIN"] == "WINDING_BASIN_CLOSED"

def test_v23_epistemic_gates_p787():
    assert "P787_FALSIFICATION_MAP" in V23_EPISTEMIC_GATES
    assert V23_EPISTEMIC_GATES["P787_FALSIFICATION_MAP"] == "FALSIFICATION_MAP_REGISTERED"

def test_v23_epistemic_gates_p788():
    assert "P788_REGRESSION" in V23_EPISTEMIC_GATES

def test_v23_application_name():
    assert "Interrogator" in V23_APPLICATION["name"]

def test_v23_application_html_path():
    assert "18-interrogator" in V23_APPLICATION["html"]

def test_v23_application_has_tests():
    assert "tests" in V23_APPLICATION
    assert "test_interrogator" in V23_APPLICATION["tests"]

def test_regression_summary_keys():
    s = regression_certificate_summary()
    for key in ["pillar", "version", "status", "sprint_name",
                "tests_passed_floor", "lean4_theorems_floor",
                "next_pillar_slot", "v23_pillars", "v23_epistemic_gates",
                "v23_application", "invariant"]:
        assert key in s

def test_regression_summary_invariant():
    s = regression_certificate_summary()
    assert "0 test failures" in s["invariant"]

def test_expectations_pillar():
    assert TEST_EXPECTATIONS["pillar"] == 788

def test_expectations_status():
    assert TEST_EXPECTATIONS["status"] == "V23_REGRESSION_CERTIFICATE_ISSUED"

def test_expectations_test_floor():
    assert TEST_EXPECTATIONS["tests_passed_floor"] == 57124

def test_expectations_lean4_floor():
    assert TEST_EXPECTATIONS["lean4_floor"] == 1006

def test_expectations_next_slot():
    assert TEST_EXPECTATIONS["next_slot"] == 789

def test_expectations_pillar_count():
    assert TEST_EXPECTATIONS["v23_pillar_count"] == 3

def test_expectations_gates_present():
    assert TEST_EXPECTATIONS["all_gates_present"] is True
