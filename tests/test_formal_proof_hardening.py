# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Post-MAS Track 1 formal proof hardening."""

from __future__ import annotations

from src.core.formal_proof_hardening import (
    ASSUMPTION_LEDGER,
    theorem_set,
    verify_theorem_set,
    track1_proof_hardening_artifact,
)


def test_assumption_ledger_present():
    assert len(ASSUMPTION_LEDGER) >= 3


def test_theorem_set_nonempty():
    theorems = theorem_set()
    assert len(theorems) >= 3


def test_all_theorems_verify():
    results = verify_theorem_set()
    assert all(item["verified"] for item in results)


def test_track1_artifact_pass():
    artifact = track1_proof_hardening_artifact()
    assert artifact["track"] == "T1"
    assert artifact["status"] == "PASS"
    assert artifact["all_verified"] is True

