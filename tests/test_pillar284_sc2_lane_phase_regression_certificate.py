# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 284 — SC2 Lane Phase Regression Certificate."""
from __future__ import annotations

from src.core.pillar284_sc2_lane_phase_regression_certificate import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLARS_IN_LANE,
    REMAINING_OPEN,
    SPRINT_NAME,
    sc2_lane_phase_summary,
    separation_guard,
    validate_lane,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 284


def test_pillar_gate():
    assert PILLAR_GATE == "SC2_LANE_PHASE_REGRESSION_CERTIFICATE"


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_sprint_name():
    assert "SC2" in SPRINT_NAME


def test_pillars_in_lane():
    assert PILLARS_IN_LANE == [280, 281, 283]


def test_remaining_open_nonempty():
    assert len(REMAINING_OPEN) >= 1


class TestSeparationGuard:
    def test_not_hardgate(self):
        assert separation_guard()["is_hardgate"] is False

    def test_cert_only(self):
        assert separation_guard()["is_regression_certificate_only"] is True


class TestValidateLane:
    def test_passes(self):
        result = validate_lane()
        assert result["passed"] is True
        assert result["errors"] == []

    def test_pillar(self):
        assert validate_lane()["pillar"] == 284

    def test_pillars_in_lane(self):
        assert validate_lane()["pillars_in_lane"] == [280, 281, 283]


class TestSc2LanePhaseSummary:
    def test_pillar(self):
        assert sc2_lane_phase_summary()["pillar"] == 284

    def test_n_pillars(self):
        assert sc2_lane_phase_summary()["n_pillars"] == 3

    def test_lane_complete(self):
        assert sc2_lane_phase_summary()["lane_complete"] is True

    def test_hands_off_to_285(self):
        assert sc2_lane_phase_summary()["hands_off_to_pillar"] == 285

    def test_remaining_open_count(self):
        summary = sc2_lane_phase_summary()
        assert summary["n_remaining_open"] == len(REMAINING_OPEN)

    def test_no_errors(self):
        assert sc2_lane_phase_summary()["errors"] == []
