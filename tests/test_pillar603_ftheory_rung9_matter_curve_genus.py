# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 603 — F-theory rung 9 matter-curve genus."""
from __future__ import annotations

import pytest

from src.core.pillar603_ftheory_rung9_matter_curve_genus import (
    BLOCKING_RESIDUAL_MATTER_CURVE_GENUS,
    CY4_EULER_CHAR_CONTRIBUTION,
    GENUS,
    N_W_DISCRIMINANT_LOCUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    VERSION,
    genus_resolution_certificate,
    matter_curve_genus,
    pillar_report,
)

PRIMARY = matter_curve_genus()
REPORT = pillar_report()

PRIMARY_KEYS = ["genus", "n_w_discriminant_locus", "cy4_euler_char_contribution", "trivial_bundle", "unique_matter_representation"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "matter_curve_genus", "genus_resolution_certificate", "toe_score_delta"]
NUMERIC_CHECKS = [
    GENUS == 0,
    N_W_DISCRIMINANT_LOCUS == 5,
    CY4_EULER_CHAR_CONTRIBUTION == 74,
    BLOCKING_RESIDUAL_MATTER_CURVE_GENUS is False,
    PRIMARY["trivial_bundle"] is True,
    REPORT["adjacent_track"] is True,
]
STRING_CHECKS = [
    PILLAR_STATUS == "FTHEORY_RUNG9_MATTER_CURVE_GENUS_COMPUTED_ADJACENT",
    VERSION == "v20.4",
    "Matter-Curve Genus" in PILLAR_TITLE,
    genus_resolution_certificate()["resolved"] is True,
    PRIMARY["unique_matter_representation"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 603
    assert PILLAR_STATUS == "FTHEORY_RUNG9_MATTER_CURVE_GENUS_COMPUTED_ADJACENT"



def test_constants() -> None:
    assert genus_resolution_certificate()["blocking_residual_matter_curve_genus"] is False
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
