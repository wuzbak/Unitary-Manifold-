# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 611 — Hyper-K proton decay Run 3."""
from __future__ import annotations

import pytest

from src.core.pillar611_hyperk_proton_decay_run3 import (
    HLLHC_RUN3_KK_GRAVITON_LOWER_BOUND,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    TAU_BOUND_CURRENT,
    TAU_UM_PREDICTION,
    VERSION,
    consistency_check,
    hllhc_run3_update,
    pillar_report,
    proton_decay_bound,
)

PRIMARY = proton_decay_bound()
REPORT = pillar_report()

PRIMARY_KEYS = ["tau_bound_current", "tau_um_prediction", "prediction_to_bound_ratio", "safe_margin"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "proton_decay_bound", "hllhc_run3_update", "consistency_check"]
NUMERIC_CHECKS = [
    TAU_BOUND_CURRENT == 1.6e34,
    TAU_UM_PREDICTION == 1.0e37,
    HLLHC_RUN3_KK_GRAVITON_LOWER_BOUND == 2.5e3,
    abs(PRIMARY["prediction_to_bound_ratio"] - 625.0) < 1e-12,
    abs(hllhc_run3_update()["improvement_gev"] - 200.0) < 1e-12,
    consistency_check()["hl_lhc_context_strengthened"] is True,
]
STRING_CHECKS = [
    PILLAR_STATUS == "HYPERK_PROTON_DECAY_RUN3_BOUND_UPDATED",
    VERSION == "v20.5",
    "Hyper-K" in PILLAR_TITLE,
    PRIMARY["safe_margin"] is True,
    REPORT["hardgate_score_delta"] == 0.0,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 611
    assert PILLAR_STATUS == "HYPERK_PROTON_DECAY_RUN3_BOUND_UPDATED"



def test_constants() -> None:
    assert consistency_check()["verdict"] == "CONSISTENT_WITH_NO_SIGNAL"
    assert REPORT["adjacent_track"] is False


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
