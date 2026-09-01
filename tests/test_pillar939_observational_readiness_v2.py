# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 939 — Observational Readiness Matrix v2."""
from __future__ import annotations
from src.core.pillar939_observational_readiness_v2 import (
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    OBSERVATIONAL_MATRIX, N_ENTRIES, N_PRIMARY_FALSIFIERS,
    N_PENDING, N_CONSISTENT, N_TENSION,
    observational_readiness_v2, obs_matrix_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 939
def test_gate(): assert PILLAR_GATE == "OBSERVATIONAL_READINESS_V2"
def test_status(): assert PILLAR_STATUS == "OBSERVATIONAL_MATRIX_COMPLETE"

def test_n_entries(): assert N_ENTRIES == 8
def test_n_primary_falsifiers(): assert N_PRIMARY_FALSIFIERS == 1
def test_n_tension_positive(): assert N_TENSION >= 1

def test_matrix_is_list(): assert isinstance(OBSERVATIONAL_MATRIX, list)
def test_matrix_length(): assert len(OBSERVATIONAL_MATRIX) == 8

def test_every_entry_has_id():
    for e in OBSERVATIONAL_MATRIX:
        assert "id" in e
        assert e["id"].startswith("ORM-")

def test_every_entry_has_required_fields():
    required = {"prediction", "experiment", "observable", "timeline",
                "current_status", "falsification_threshold"}
    for e in OBSERVATIONAL_MATRIX:
        for f in required:
            assert f in e, f"Missing field {f} in {e['id']}"

def test_litebird_is_primary_falsifier():
    litebird = [e for e in OBSERVATIONAL_MATRIX if "LiteBIRD" in e["experiment"]]
    assert len(litebird) >= 1
    assert litebird[0]["is_primary_falsifier"] is True

def test_desi_in_matrix():
    desi = [e for e in OBSERVATIONAL_MATRIX if "DESI" in e["experiment"]]
    assert len(desi) >= 1

def test_readiness_v2_dict():
    res = observational_readiness_v2()
    assert res["n_entries"] == 8
    assert res["version"] == "v2"

def test_readiness_matrix_field():
    res = observational_readiness_v2()
    assert len(res["matrix"]) == 8

def test_summary_pillar():
    s = obs_matrix_summary()
    assert s["pillar"] == 939

def test_summary_n_entries():
    s = obs_matrix_summary()
    assert s["n_entries"] == 8
