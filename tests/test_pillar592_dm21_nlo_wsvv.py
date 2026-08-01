# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 592 — Δm²₂₁ Step 4 NLO WS-V correction."""
from __future__ import annotations

import pytest

from src.core.pillar592_dm21_nlo_wsvv_correction import (
    DM21_AFTER_FN,
    DM21_AFTER_NLO,
    NAME_RESIDUAL,
    NLO_WSVV_FRAC,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    TENSION_AFTER_NLO,
    VERSION,
    dm21_after_nlo,
    nlo_summary,
    nlo_wsvv_correction,
    pillar_report,
    tension_after_nlo,
)

PRIMARY = nlo_summary()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "step", "named_residual", "nlo_correction", "dm21"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "nlo_wsvv_correction", "dm21_after_nlo", "nlo_summary"]
NUMERIC_CHECKS = [
    abs(NLO_WSVV_FRAC - 0.0085) < 1e-12,
    abs(DM21_AFTER_NLO - DM21_AFTER_FN * (1.0 + NLO_WSVV_FRAC)) < 1e-12,
    abs(dm21_after_nlo()["delta_dm21_ev2"] - (DM21_AFTER_NLO - DM21_AFTER_FN)) < 1e-12,
    abs(TENSION_AFTER_NLO - abs(7.53e-5 - DM21_AFTER_NLO) / 0.18e-5) < 1e-12,
    abs(nlo_wsvv_correction()["nlo_percent"] - 0.85) < 1e-12,
    abs(tension_after_nlo()["tension_sigma_after_nlo"] - TENSION_AFTER_NLO) < 1e-12,
]
STRING_CHECKS = [
    PILLAR_STATUS == "DM21_STEP4_NLO_WSVV_TEXTURE",
    "NLO WS-V" in PILLAR_TITLE,
    VERSION == "v20.2",
    NAME_RESIDUAL == "DM21_NLO_WSVV_SUBDOMINANT",
    PRIMARY["tension"]["below_one_sigma"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 592
    assert PILLAR_STATUS == "DM21_STEP4_NLO_WSVV_TEXTURE"



def test_constants() -> None:
    assert 7.38e-5 < DM21_AFTER_NLO < 7.39e-5
    assert 0.8 < TENSION_AFTER_NLO < 0.82
    assert NAME_RESIDUAL.endswith("SUBDOMINANT")


@pytest.mark.parametrize("key", PRIMARY_KEYS)
def test_primary_keys(key: str) -> None:
    assert key in PRIMARY


@pytest.mark.parametrize("key", REPORT_KEYS)
def test_report_keys(key: str) -> None:
    assert key in REPORT


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
