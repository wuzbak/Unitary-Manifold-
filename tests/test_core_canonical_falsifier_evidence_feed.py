# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/canonical_falsifier_evidence_feed.py."""
from __future__ import annotations

from src.core.canonical_falsifier_evidence_feed import (
    collect_canonical_evidence_feed,
    falsifier_hard_gate,
    falsifier_status_table,
)


def test_collect_feed_structure():
    feed = collect_canonical_evidence_feed()
    assert feed["version"] == "v10.42"
    assert "generated_on" in feed
    required = {"litebird", "lab_cp_5_7", "cmbs4", "dune", "hyperk_juno", "desi_year3"}
    assert required.issubset(set(feed["experiments"].keys()))
    assert "readiness" in feed["experiments"]["litebird"]


def test_status_table_has_five_experiments():
    table = falsifier_status_table()
    assert len(table) >= 6
    assert any(row["experiment"] == "LiteBIRD" and row["primary_falsifier"] for row in table)
    assert any(row["experiment"] == "Lab_CP_5_7" and row["primary_falsifier"] for row in table)
    assert any(row["experiment"] == "DESI Year 3" and row["status"] in {"PASS", "TENSION", "FALSIFIED"} for row in table)


def test_hard_gate_shape():
    gate = falsifier_hard_gate()
    assert set(gate.keys()) == {"pass", "fail_count", "failures", "policy"}
    assert isinstance(gate["fail_count"], int)
    assert isinstance(gate["failures"], list)
