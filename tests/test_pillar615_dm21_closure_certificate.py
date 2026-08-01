# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 615 — Δm²₂₁ formal closure certificate."""
from __future__ import annotations

import pytest

from src.core.pillar615_dm21_closure_certificate import (
    CLOSURE_THRESHOLD,
    DM21_CLOSED,
    DM21_FINAL_EV2,
    FINAL_TENSION_SIGMA,
    JUNO_PHASE2_PREDICTION,
    P20_STATUS_AFTER,
    P20_STATUS_BEFORE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    TOE_DELTA,
    TOE_SCORE_AFTER,
    TOE_SCORE_BEFORE,
    VERSION,
    cascade_steps,
    closure_conditions,
    dm21_closure_certificate,
    juno_phase2_preregistration,
    pillar_report,
    toe_upgrade,
)

CERT = dm21_closure_certificate()
REPORT = pillar_report()
CONDITIONS = closure_conditions()
CASCADE = cascade_steps()
TOE_UP = toe_upgrade()

REPORT_KEYS = [
    "pillar", "title", "status", "version", "adjacent_track",
    "cascade_steps", "closure_conditions", "toe_upgrade",
    "juno_phase2_preregistration", "dm21_closure_certificate",
]
CERT_KEYS = [
    "pillar", "status", "dm21_final_ev2", "final_tension_sigma",
    "tension_trajectory", "dm21_closed", "all_conditions_met", "toe_upgrade",
]

NUMERIC_CHECKS = [
    DM21_CLOSED is True,
    FINAL_TENSION_SIGMA < 0.5,
    abs(TOE_SCORE_AFTER - 30.0) < 1e-9,
    abs(TOE_SCORE_BEFORE - 29.5) < 1e-9,
    abs(TOE_DELTA - 0.5) < 1e-9,
    len(CASCADE) == 6,
    CASCADE[0]["step"] == 0,
    CASCADE[5]["step"] == 5,
    CASCADE[5]["tension_sigma"] < 0.5,
    abs(CASCADE[5]["tension_sigma"] - FINAL_TENSION_SIGMA) < 1e-12,
    CONDITIONS["condition_1"]["met"] is True,
    CONDITIONS["condition_2"]["met"] is True,
    CONDITIONS["condition_3"]["met"] is True,
    CONDITIONS["condition_4"]["met"] is True,
    CONDITIONS["all_conditions_met"] is True,
    abs(TOE_UP["toe_delta"] - 0.5) < 1e-9,
    len(CERT["tension_trajectory"]) == 6,
    CERT["tension_trajectory"][0] == 4.63,
    CERT["tension_trajectory"][-1] == FINAL_TENSION_SIGMA,
]

STRING_CHECKS = [
    PILLAR_STATUS == "DM21_CLOSED_FIVE_STEP_CASCADE",
    "Closure Certificate" in PILLAR_TITLE,
    VERSION == "v20.6",
    P20_STATUS_BEFORE == "APPROACHING_CLOSURE",
    P20_STATUS_AFTER == "DM21_CLOSED_FIVE_STEP_CASCADE",
    DM21_CLOSED is True,
    REPORT["adjacent_track"] is False,
    len(CERT["what_is_claimed"]) >= 5,
    len(CERT["what_is_NOT_claimed"]) >= 4,
    TOE_UP["pillar_target"] == "P20",
    TOE_UP["parameter"] == "Δm²₂₁ (solar neutrino mass splitting)",
    juno_phase2_preregistration()["preregistered"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 615
    assert PILLAR_STATUS == "DM21_CLOSED_FIVE_STEP_CASCADE"


def test_dm21_formally_closed() -> None:
    """The central result: DM21 must be formally closed."""
    assert DM21_CLOSED is True
    assert FINAL_TENSION_SIGMA < CLOSURE_THRESHOLD


def test_toe_score_advances_to_30() -> None:
    assert abs(TOE_SCORE_AFTER - 30.0) < 1e-9
    assert abs(TOE_DELTA - 0.5) < 1e-9


def test_all_closure_conditions_met() -> None:
    assert CONDITIONS["all_conditions_met"] is True


def test_cascade_trajectory_monotone() -> None:
    """Tension must decrease monotonically along the cascade."""
    tensions = [step["tension_sigma"] for step in CASCADE]
    for i in range(1, len(tensions)):
        assert tensions[i] < tensions[i - 1], f"Non-monotone at step {i}"


def test_dm21_final_in_physical_range() -> None:
    PDG = 7.53e-5
    assert 0.95 * PDG < DM21_FINAL_EV2 < 1.05 * PDG


def test_toe_score_delta() -> None:
    assert abs(REPORT["toe_score_delta"] - 0.5) < 1e-9
    assert abs(REPORT["hardgate_score_delta"] - 0.5) < 1e-9


@pytest.mark.parametrize("key", REPORT_KEYS)
def test_report_keys(key: str) -> None:
    assert key in REPORT


@pytest.mark.parametrize("key", CERT_KEYS)
def test_cert_keys(key: str) -> None:
    assert key in CERT


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
