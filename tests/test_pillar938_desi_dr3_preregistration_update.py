# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 938 — DESI DR3 Pre-Registration Update."""
from __future__ import annotations
from src.core.pillar938_desi_dr3_preregistration_update import (
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    DESI_SIGMA_LOW, DESI_SIGMA_HIGH,
    SPHEREX_SIGMA_WA_PROJECTED, DESI_DR3_SIGMA_WA_PROJECTED,
    FALSIFICATION_THRESHOLDS, DESI_DR3_AVAILABLE,
    desi_update, desi_update_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 938
def test_gate(): assert PILLAR_GATE == "DESI_DR3_PREREGISTRATION_UPDATE"
def test_status(): assert PILLAR_STATUS == "DESI_DR3_PREREGISTRATION_UPDATED"

def test_sigma_low(): assert DESI_SIGMA_LOW == 2.30
def test_sigma_high(): assert DESI_SIGMA_HIGH == 2.75
def test_sigma_ordering(): assert DESI_SIGMA_LOW < DESI_SIGMA_HIGH

def test_spherex_sigma_projected(): assert 0 < SPHEREX_SIGMA_WA_PROJECTED < DESI_DR3_SIGMA_WA_PROJECTED

def test_dr3_not_available(): assert DESI_DR3_AVAILABLE is False

def test_thresholds_locked():
    assert FALSIFICATION_THRESHOLDS["FALSIFIED"] == 5.0
    assert FALSIFICATION_THRESHOLDS["HIGH_TENSION"] == 3.0
    assert FALSIFICATION_THRESHOLDS["TENSION"] == 2.0

def test_update_dict_keys():
    res = desi_update()
    assert "sprint_be_sigma_range" in res
    assert "desi_dr3_available" in res
    assert "falsification_thresholds" in res

def test_current_verdict_tension():
    res = desi_update()
    assert res["current_verdict"] == "TENSION"

def test_thresholds_not_changed():
    res = desi_update()
    assert res["falsification_thresholds"]["FALSIFIED"] == 5.0

def test_summary_pillar():
    s = desi_update_summary()
    assert s["pillar"] == 938

def test_summary_thresholds_locked():
    s = desi_update_summary()
    assert s["thresholds_locked"] is True
