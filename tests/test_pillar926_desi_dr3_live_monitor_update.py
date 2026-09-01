# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 926 — DESI DR3 live monitor update."""
from __future__ import annotations
from src.core.pillar926_desi_dr3_live_monitor_update import (
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    DESI_CURRENT_SIGMA_LOW, DESI_CURRENT_SIGMA_HIGH, DESI_DR3_AVAILABLE,
    THRESHOLD_FALSIFIED, THRESHOLD_HIGH_TENSION, THRESHOLD_TENSION,
    desi_live_monitor, desi_live_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 926
def test_gate(): assert PILLAR_GATE == "DESI_DR3_LIVE_MONITOR_UPDATE"
def test_status(): assert PILLAR_STATUS == "DESI_DR3_MONITORING"
def test_dr3_not_available(): assert DESI_DR3_AVAILABLE is False
def test_sigma_low_positive(): assert DESI_CURRENT_SIGMA_LOW > 0
def test_sigma_high_ge_low(): assert DESI_CURRENT_SIGMA_HIGH >= DESI_CURRENT_SIGMA_LOW
def test_sigma_below_high_tension(): assert DESI_CURRENT_SIGMA_HIGH < THRESHOLD_HIGH_TENSION
def test_sigma_above_tension(): assert DESI_CURRENT_SIGMA_LOW >= THRESHOLD_TENSION
def test_threshold_ordering():
    assert THRESHOLD_TENSION < THRESHOLD_HIGH_TENSION < THRESHOLD_FALSIFIED

def test_monitor_dict():
    r = desi_live_monitor()
    assert isinstance(r, dict)

def test_monitor_pillar():
    r = desi_live_monitor()
    assert r["pillar"] == 926

def test_monitor_gate():
    r = desi_live_monitor()
    assert r["gate"] == "DESI_DR3_LIVE_MONITOR_UPDATE"

def test_monitor_status():
    r = desi_live_monitor()
    assert r["status"] == PILLAR_STATUS

def test_monitor_um_wa_prediction():
    r = desi_live_monitor()
    assert r["um_wa_prediction"] == 0.0

def test_monitor_sigma_range():
    r = desi_live_monitor()
    lo, hi = r["current_sigma_range"]
    assert lo <= hi

def test_monitor_route_bao_only():
    r = desi_live_monitor()
    assert r["route_bao_only"] == "TENSION"

def test_monitor_route_cov_corrected():
    r = desi_live_monitor()
    assert r["route_cov_corrected"] == "TENSION"

def test_monitor_interpretation():
    r = desi_live_monitor()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 20

def test_summary_dict():
    s = desi_live_summary()
    assert isinstance(s, dict)

def test_summary_pillar():
    s = desi_live_summary()
    assert s["pillar"] == 926

def test_summary_status():
    s = desi_live_summary()
    assert s["status"] == PILLAR_STATUS
