# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 602 — F-theory rung 9 spectral cover."""
from __future__ import annotations

import pytest

from src.core.pillar602_ftheory_rung9_spectral_cover import (
    BLOCKING_RESIDUAL_SPECTRAL_COVER,
    N_SHEETS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SPECTRAL_COVER_DISCRIMINANT,
    SPECTRAL_COVER_STATUS,
    VERSION,
    pillar_report,
    resolution_certificate,
    spectral_cover_analysis,
)

PRIMARY = spectral_cover_analysis()
REPORT = pillar_report()

PRIMARY_KEYS = ["n_sheets", "discriminant", "status", "reference_cy4", "matter_curves_avoided"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "spectral_cover_analysis", "resolution_certificate", "toe_score_delta"]
NUMERIC_CHECKS = [
    N_SHEETS == 5,
    BLOCKING_RESIDUAL_SPECTRAL_COVER is False,
    PRIMARY["reference_cy4"] is True,
    PRIMARY["matter_curves_avoided"] is True,
    resolution_certificate()["resolved"] is True,
    REPORT["adjacent_track"] is True,
]
STRING_CHECKS = [
    PILLAR_STATUS == "FTHEORY_RUNG9_SPECTRAL_COVER_RESOLVED_ADJACENT",
    SPECTRAL_COVER_DISCRIMINANT == "Weierstrass_f4_g6",
    SPECTRAL_COVER_STATUS == "RESOLVED_AT_REFERENCE_CY4",
    VERSION == "v20.4",
    "Spectral Cover" in PILLAR_TITLE,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 602
    assert PILLAR_STATUS == "FTHEORY_RUNG9_SPECTRAL_COVER_RESOLVED_ADJACENT"



def test_constants() -> None:
    assert resolution_certificate()["blocking_residual_spectral_cover"] is False
    assert REPORT["hardgate_score_delta"] == 0.0


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
