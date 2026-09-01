# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 952 — Observational Readiness v4."""
from __future__ import annotations
from src.core.pillar952_observational_readiness_v4 import (
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS, PILLAR_VALID,
    OBSERVATIONAL_MATRIX_VERSION, PREDICTIONS, OPEN_LANES, ARCHITECTURE_LIMITS,
    observational_readiness_v4_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 952
def test_gate(): assert PILLAR_GATE == "OBSERVATIONAL_READINESS_V4"
def test_valid(): assert PILLAR_VALID is True
def test_status(): assert PILLAR_STATUS == "OBSERVATIONAL_READINESS_V4_COMPLETE"
def test_version(): assert OBSERVATIONAL_MATRIX_VERSION == "v4"

def test_predictions_count(): assert len(PREDICTIONS) == 8

def test_predictions_have_required_fields():
    for p in PREDICTIONS:
        assert "id" in p
        assert "observable" in p
        assert "prediction" in p
        assert "status" in p

def test_prediction_ns_consistent():
    ns_pred = next(p for p in PREDICTIONS if p["id"] == "P1_NS")
    assert ns_pred["status"] == "CONSISTENT"

def test_prediction_r_consistent():
    r_pred = next(p for p in PREDICTIONS if p["id"] == "P2_R")
    assert r_pred["status"] == "CONSISTENT"

def test_prediction_dark_energy_monitoring():
    de_pred = next(p for p in PREDICTIONS if p["id"] == "P5_DARK_ENERGY")
    assert de_pred["status"] == "MONITORING"

def test_open_lanes_count(): assert len(OPEN_LANES) == 6

def test_open_lanes_b3_present():
    ids = [l["item"] for l in OPEN_LANES]
    assert "B3_G4_FLUX" in ids

def test_open_lanes_ckm_present():
    ids = [l["item"] for l in OPEN_LANES]
    assert "CKM_TEXTURE_13D" in ids

def test_open_lanes_fermion_present():
    ids = [l["item"] for l in OPEN_LANES]
    assert "FERMION_MASS_RATIO" in ids

def test_b3_upgraded_to_bounded():
    b3 = next(l for l in OPEN_LANES if l["item"] == "B3_G4_FLUX")
    assert "BOUNDED" in b3["status"]

def test_ckm_upgraded_to_true_arch_limit():
    ckm = next(l for l in OPEN_LANES if l["item"] == "CKM_TEXTURE_13D")
    assert "TRUE_ARCHITECTURE_LIMIT" in ckm["status"]

def test_fermion_upgraded_to_window_constrained():
    fm = next(l for l in OPEN_LANES if l["item"] == "FERMION_MASS_RATIO")
    assert "CONSTRAINED" in fm["status"]

def test_architecture_limits_count(): assert len(ARCHITECTURE_LIMITS) >= 4

def test_litebird_mentioned():
    all_text = str(PREDICTIONS) + str(OPEN_LANES)
    assert "LiteBIRD" in all_text or "LITEBIRD" in all_text

def test_summary_keys():
    s = observational_readiness_v4_summary()
    for key in ["pillar", "gate", "status", "valid", "version",
                "n_predictions", "n_open_lanes", "predictions", "open_lanes",
                "primary_falsifier"]:
        assert key in s

def test_summary_valid(): assert observational_readiness_v4_summary()["valid"] is True
def test_summary_pillar(): assert observational_readiness_v4_summary()["pillar"] == 952
def test_summary_primary_falsifier():
    s = observational_readiness_v4_summary()
    assert "LiteBIRD" in s["primary_falsifier"] or "litebird" in s["primary_falsifier"].lower()
