# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 916 — 13D DBP Rung 8 Master Certificate."""
from __future__ import annotations
from src.core.pillar916_rung8_master_certificate import (
    PILLAR_NUMBER, PILLAR_GATE, RUNG_8_STATUS, BRIDGE_VALID,
    REMAINING_OPEN, ARCHITECTURE_LIMITS_CERTIFIED,
    rung8_master_certificate, sprint_bd_master_bridge_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 916
def test_gate(): assert PILLAR_GATE == "RUNG_8_DBP_MASTER_CERTIFICATE"
def test_bridge_valid(): assert BRIDGE_VALID is True
def test_rung8_status_valid():
    assert RUNG_8_STATUS in {"RUNG_8_PARTIAL_CLOSURE", "RUNG_8_ARCHITECTURE_CERTIFIED"}
def test_remaining_open_is_list(): assert isinstance(REMAINING_OPEN, list)
def test_arch_limits_is_list(): assert isinstance(ARCHITECTURE_LIMITS_CERTIFIED, list)

def test_certificate_keys():
    r = rung8_master_certificate()
    for k in ["pillar", "gate", "rung_7_status", "rung_8_status", "bridge_valid",
              "pillar_results", "closed_or_narrowed", "open_items", "n_closed", "n_open",
              "remaining_open", "architecture_limits_certified", "pillar_summaries"]:
        assert k in r

def test_rung7_complete(): assert rung8_master_certificate()["rung_7_status"] == "SCAFFOLD_COMPLETE"
def test_pillar_results_count(): assert len(rung8_master_certificate()["pillar_results"]) == 5
def test_n_closed_nonneg(): assert rung8_master_certificate()["n_closed"] >= 0
def test_n_open_nonneg(): assert rung8_master_certificate()["n_open"] >= 0
def test_closed_plus_open_equals_five():
    r = rung8_master_certificate()
    assert r["n_closed"] + r["n_open"] == 5

def test_pillar_summaries_keys():
    sums = rung8_master_certificate()["pillar_summaries"]
    for key in ["P911", "P912", "P913", "P914", "P915"]:
        assert key in sums

def test_epistemic_note_present(): assert "honest" in rung8_master_certificate()["epistemic_note"].lower()

def test_summary_keys():
    s = sprint_bd_master_bridge_summary()
    for k in ["pillar", "gate", "rung_8_status", "n_closed", "n_open", "bridge_valid"]:
        assert k in s

def test_summary_bridge_valid(): assert sprint_bd_master_bridge_summary()["bridge_valid"] is True
def test_summary_pillar(): assert sprint_bd_master_bridge_summary()["pillar"] == 916
