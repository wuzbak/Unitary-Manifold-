# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Sprint AM Wave 5: CMB acoustic peak audit."""
import pytest
from src.core.cmb_acoustic_peak_audit import (
    diagnose_peak_offset,
    kk_threshold_correction,
    test_cs_braid_shift,
    architecture_limit_proof,
    cmb_peak_gap5_certificate,
    CMB_PEAK_STATUS,
)


def test_status_token():
    assert CMB_PEAK_STATUS == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_diagnose_peak_offset_returns_dict():
    r = diagnose_peak_offset()
    assert isinstance(r, dict)


def test_diagnose_mean_offset_pct_exists():
    r = diagnose_peak_offset()
    assert "mean_offset_pct" in r


def test_diagnose_mean_offset_nonneg():
    r = diagnose_peak_offset()
    assert r["mean_offset_pct"] >= 0


def test_kk_threshold_correction_returns_dict():
    r = kk_threshold_correction()
    assert isinstance(r, dict)


def test_cs_braid_shift_returns_dict():
    r = test_cs_braid_shift()
    assert isinstance(r, dict)


def test_architecture_limit_status():
    r = architecture_limit_proof()
    assert r["CMB_PEAK_STATUS"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_certificate_status():
    cert = cmb_peak_gap5_certificate()
    assert cert["CMB_PEAK_STATUS"] == "ARCHITECTURE_LIMIT_CERTIFIED"
