# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 703 — CMB fullchain audit."""
from __future__ import annotations

from src.core.pillar703_cmb_fullchain_audit import (
    PILLAR_NUMBER,
    cmb_fullchain_audit,
    cmb_sprint_aa_summary,
)

AUDIT = cmb_fullchain_audit()
SUMMARY = cmb_sprint_aa_summary()


def test_pillar_number():
    assert PILLAR_NUMBER == 703


def test_audit_contains_all_pillars():
    pillar_ids = {entry["pillar"] for entry in AUDIT["pillars"]}
    assert {78, 639, 679, 698, 699, 700, 701, 702}.issubset(pillar_ids)


def test_overall_status_valid():
    assert AUDIT["overall_cmb_amplitude_status"] in {"CLOSED", "ARCHITECTURE_LIMIT"}


def test_final_coverage_positive():
    assert AUDIT["final_coverage_fraction"] > 0.0


def test_phase2_coverage_positive():
    assert AUDIT["phase2_coverage_fraction"] > 0.0


def test_summary_status_matches_audit():
    assert SUMMARY["status"] == AUDIT["overall_cmb_amplitude_status"]


def test_summary_mentions_sprint():
    assert "Sprint AA" in SUMMARY["summary"]


def test_summary_pillar_count():
    assert SUMMARY["pillar_count"] == len(AUDIT["pillars"])


def test_honesty_label_present():
    assert AUDIT["honesty_label"] == "SIMPLIFIED_HIERARCHY_NOT_EXACT"
