# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 614 — Δm²₂₁ KamLAND/KAM solar cross-check."""
from __future__ import annotations

import pytest

from src.core.pillar614_dm21_kamland_solar_crosscheck import (
    CLOSURE_READY,
    CROSSCHECK_PASS,
    DM21_KAMLAND_EV2,
    DM21_KAMLAND_SIGMA_EV2,
    DM21_UM_PREDICTION_EV2,
    NEW_ARCHITECTURE_LIMIT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    TENSION_VS_KAMLAND,
    TENSION_VS_PDG,
    VERSION,
    architecture_limit_audit,
    closure_readiness,
    crosscheck_tensions,
    kamland_measurement,
    pillar_report,
)

PRIMARY = crosscheck_tensions()
REPORT = pillar_report()
AUDIT = architecture_limit_audit()
READY = closure_readiness()

PRIMARY_KEYS = ["um_prediction_ev2", "vs_pdg", "vs_kamland", "both_pass"]
REPORT_KEYS = [
    "pillar", "title", "status", "version", "adjacent_track",
    "kamland_measurement", "crosscheck_tensions", "architecture_limit_audit",
    "closure_readiness",
]

NUMERIC_CHECKS = [
    abs(DM21_KAMLAND_EV2 - 7.59e-5) < 1e-12,
    abs(DM21_KAMLAND_SIGMA_EV2 - 0.21e-5) < 1e-12,
    TENSION_VS_PDG < 0.5,
    TENSION_VS_KAMLAND < 1.0,
    abs(TENSION_VS_KAMLAND - abs(DM21_KAMLAND_EV2 - DM21_UM_PREDICTION_EV2) / DM21_KAMLAND_SIGMA_EV2) < 1e-12,
    PRIMARY["vs_pdg"]["tension_sigma"] < 0.5,
    PRIMARY["vs_kamland"]["tension_sigma"] < 1.0,
    PRIMARY["vs_pdg"]["pass"] is True,
    PRIMARY["vs_kamland"]["pass"] is True,
    len(READY["conditions_met"]) == 4,
]

STRING_CHECKS = [
    PILLAR_STATUS == "DM21_KAMLAND_KAM_SOLAR_CROSSCHECK_PASS",
    "KamLAND" in PILLAR_TITLE,
    VERSION == "v20.6",
    CROSSCHECK_PASS is True,
    NEW_ARCHITECTURE_LIMIT is False,
    CLOSURE_READY is True,
    AUDIT["new_free_parameter"] is False,
    AUDIT["new_field_content"] is False,
    AUDIT["five_step_cascade_complete"] is True,
    READY["formal_certificate_in"] == "Pillar 615",
    kamland_measurement()["channel"] == "reactor_antineutrino",
    REPORT["adjacent_track"] is False,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 614
    assert PILLAR_STATUS == "DM21_KAMLAND_KAM_SOLAR_CROSSCHECK_PASS"


def test_both_tensions_below_one_sigma() -> None:
    assert TENSION_VS_PDG < 1.0
    assert TENSION_VS_KAMLAND < 1.0


def test_crosscheck_pass() -> None:
    assert CROSSCHECK_PASS is True


def test_no_architecture_limit() -> None:
    assert NEW_ARCHITECTURE_LIMIT is False


def test_closure_ready() -> None:
    assert CLOSURE_READY is True
    assert all(READY["conditions_met"])


def test_no_toe_delta() -> None:
    assert REPORT["toe_score_delta"] == 0.0


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
