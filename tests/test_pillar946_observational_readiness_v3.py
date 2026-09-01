# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 946 — Observational Readiness v3."""
from __future__ import annotations
from src.core.pillar946_observational_readiness_v3 import (
    OBSERVATIONAL_MATRIX_V3,
    OPEN_SET_BG,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    observational_readiness_v3_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 946
def test_gate(): assert PILLAR_GATE == "OBSERVATIONAL_READINESS_V3"

def test_open_set_length():
    assert len(OPEN_SET_BG) == 8

def test_open_set_ids():
    ids = [item["id"] for item in OPEN_SET_BG]
    assert "B3_G4_FLUX" in ids
    assert "CKM_TEXTURE_13D" in ids
    assert "CMB_AMP_ARCHITECTURE_LIMIT" in ids
    assert "LITEBIRD_BIREFRINGENCE" in ids

def test_open_set_labels():
    for item in OPEN_SET_BG:
        assert "label" in item
        assert len(item["label"]) > 0

def test_matrix_length():
    assert len(OBSERVATIONAL_MATRIX_V3) == 8

def test_matrix_keys():
    for row in OBSERVATIONAL_MATRIX_V3:
        for key in ["prediction", "value", "experiment", "timeline",
                    "falsification_condition", "current_status"]:
            assert key in row

def test_litebird_in_matrix():
    expts = [r["experiment"] for r in OBSERVATIONAL_MATRIX_V3]
    assert any("LiteBIRD" in e for e in expts)

def test_desi_in_matrix():
    expts = [r["experiment"] for r in OBSERVATIONAL_MATRIX_V3]
    assert any("DESI" in e for e in expts)

def test_status():
    assert PILLAR_STATUS == "OBSERVATIONAL_READINESS_V3_COMPLETE"

def test_pillar_valid():
    assert PILLAR_VALID is True

def test_summary_keys():
    s = observational_readiness_v3_summary()
    for key in ["pillar", "gate", "status", "valid", "open_set",
                "n_open", "observational_matrix", "n_predictions",
                "primary_falsifier"]:
        assert key in s

def test_summary_pillar():
    assert observational_readiness_v3_summary()["pillar"] == 946

def test_n_open():
    assert observational_readiness_v3_summary()["n_open"] == 8

def test_n_predictions():
    assert observational_readiness_v3_summary()["n_predictions"] == 8

def test_primary_falsifier_litebird():
    s = observational_readiness_v3_summary()
    assert "LiteBIRD" in s["primary_falsifier"]

def test_desi_tension_below_5sigma():
    for row in OBSERVATIONAL_MATRIX_V3:
        if "DESI" in row["experiment"]:
            assert "TENSION" in row["current_status"] or "2." in row["current_status"]

def test_b3_g4_updated():
    b3 = next(x for x in OPEN_SET_BG if x["id"] == "B3_G4_FLUX")
    assert "PARTIAL_CONSISTENT" in b3["label"]
