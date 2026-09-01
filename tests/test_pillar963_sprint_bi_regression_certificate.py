# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 963 — Sprint BI Regression Certificate."""

import pytest
from src.core.pillar963_sprint_bi_regression_certificate import (
    PILLAR_STATUS, PILLAR_VALID, SPRINT_NAME, VERSION, NEXT_PILLAR_SLOT,
    SPRINT_PILLARS, sprint_bi_outcome_table, sprint_bi_regression_report,
    STATUS_955, VALID_955, STATUS_956, VALID_956, STATUS_957, VALID_957,
    STATUS_958, VALID_958, STATUS_959, VALID_959, STATUS_960, VALID_960,
    STATUS_961, VALID_961, STATUS_962, VALID_962,
    LEAN4_START, LEAN4_END, LEAN4_DELTA,
)


def test_pillar_status():
    assert PILLAR_STATUS == "SPRINT_BI_REGRESSION_CERTIFICATE_COMPLETE"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_sprint_name():
    assert SPRINT_NAME == "BI"


def test_version():
    assert VERSION == "v32.1"


def test_next_pillar_slot():
    assert NEXT_PILLAR_SLOT == 964


def test_sprint_pillars():
    assert 955 in SPRINT_PILLARS
    assert 963 in SPRINT_PILLARS
    assert len(SPRINT_PILLARS) == 9  # 955..963 inclusive


def test_all_component_pillars_valid():
    assert VALID_955 is True
    assert VALID_956 is True
    assert VALID_957 is True
    assert VALID_958 is True
    assert VALID_959 is True
    assert VALID_960 is True
    assert VALID_961 is True
    assert VALID_962 is True


def test_all_statuses_non_empty():
    for status in [STATUS_955, STATUS_956, STATUS_957, STATUS_958,
                   STATUS_959, STATUS_960, STATUS_961, STATUS_962]:
        assert len(status) > 0


def test_lean4_delta():
    assert LEAN4_DELTA == 100
    assert LEAN4_END == LEAN4_START + LEAN4_DELTA
    assert LEAN4_END == 3812


def test_outcome_table_length():
    outcomes = sprint_bi_outcome_table()
    assert len(outcomes) == 8  # 7 physics + Lean4


def test_outcome_table_all_valid():
    for outcome in sprint_bi_outcome_table():
        assert outcome["valid"] is True


def test_outcome_955_kawamura():
    outcomes = sprint_bi_outcome_table()
    p955 = [o for o in outcomes if o["pillar"] == 955][0]
    assert p955["verdict"] == "CLOSED"


def test_outcome_956_n2():
    outcomes = sprint_bi_outcome_table()
    p956 = [o for o in outcomes if o["pillar"] == 956][0]
    assert p956["verdict"] == "CLOSED"


def test_regression_report_all_valid():
    report = sprint_bi_regression_report()
    assert report["all_valid"] is True


def test_regression_closures():
    report = sprint_bi_regression_report()
    closures = report["closures_this_sprint"]
    assert any("955" in c for c in closures)
    assert any("956" in c for c in closures)


def test_regression_remaining_open_documented():
    report = sprint_bi_regression_report()
    remaining = report["remaining_open"]
    # Confirmed irreducibles must still be documented
    assert any("IRREDUCIBLE" in r for r in remaining)


def test_regression_next_slot():
    report = sprint_bi_regression_report()
    assert report["next_pillar_slot"] == 964
