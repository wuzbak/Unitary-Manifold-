# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 925 — F-theory Rung 10 master certificate."""
from __future__ import annotations
from src.core.pillar925_ftheory_rung10_certificate import (
    PILLAR_NUMBER, PILLAR_GATE, RUNG10_STATUS, RUNG10_VALID,
    N_BLOCKERS_RESOLVED, N_BLOCKERS_OPEN, rung10_certificate, rung10_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 925
def test_gate(): assert PILLAR_GATE == "FTHEORY_RUNG10_CERTIFICATE"
def test_rung10_valid(): assert RUNG10_VALID is True
def test_n_blockers_total(): assert N_BLOCKERS_RESOLVED + N_BLOCKERS_OPEN == 3
def test_n_blockers_resolved_range(): assert 0 <= N_BLOCKERS_RESOLVED <= 3
def test_rung10_status_valid():
    assert RUNG10_STATUS in {"RUNG10_PROVED", "RUNG10_PARTIAL"}

def test_rung10_proved_iff_all_resolved():
    if N_BLOCKERS_OPEN == 0:
        assert RUNG10_STATUS == "RUNG10_PROVED"
    else:
        assert RUNG10_STATUS == "RUNG10_PARTIAL"

def test_certificate_dict():
    r = rung10_certificate()
    assert isinstance(r, dict)

def test_certificate_pillar():
    r = rung10_certificate()
    assert r["pillar"] == 925

def test_certificate_gate():
    r = rung10_certificate()
    assert r["gate"] == "FTHEORY_RUNG10_CERTIFICATE"

def test_certificate_status():
    r = rung10_certificate()
    assert r["rung10_status"] == RUNG10_STATUS

def test_certificate_n_blockers():
    r = rung10_certificate()
    assert r["n_blockers_total"] == 3

def test_certificate_n_resolved():
    r = rung10_certificate()
    assert r["n_blockers_resolved"] == N_BLOCKERS_RESOLVED

def test_certificate_pillar_summaries():
    r = rung10_certificate()
    assert "P922" in r["pillar_summaries"]
    assert "P923" in r["pillar_summaries"]
    assert "P924" in r["pillar_summaries"]

def test_certificate_interpretation():
    r = rung10_certificate()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 20

def test_certificate_epistemic_note():
    r = rung10_certificate()
    assert isinstance(r["epistemic_note"], str) and len(r["epistemic_note"]) > 20

def test_summary_dict():
    s = rung10_summary()
    assert isinstance(s, dict)

def test_summary_pillar():
    s = rung10_summary()
    assert s["pillar"] == 925

def test_summary_status():
    s = rung10_summary()
    assert s["rung10_status"] == RUNG10_STATUS
