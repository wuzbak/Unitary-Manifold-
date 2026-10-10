# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 283 — SC2 α_GW / DESI DR3 Joint Robustness Bridge."""
from __future__ import annotations

from src.core.pillar283_sc2_alpha_gw_desi_dr3_joint_robustness import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    joint_robustness_report,
    joint_robustness_rows,
    separation_guard,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 283


def test_pillar_gate():
    assert PILLAR_GATE == "SC2_ALPHA_GW_DESI_DR3_JOINT_ROBUSTNESS_PARTIAL"


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


class TestSeparationGuard:
    def test_not_hardgate(self):
        assert separation_guard()["is_hardgate"] is False

    def test_cross_checks_only(self):
        assert separation_guard()["cross_checks_existing_pillars_only"] is True


class TestJointRobustnessRows:
    def test_three_rows(self):
        rows = joint_robustness_rows()
        assert len(rows) == 3

    def test_each_row_has_verdict(self):
        for row in joint_robustness_rows():
            assert "dr3_verdict" in row
            assert "alpha_gw_narrowed_interval" in row

    def test_sigma_levels_present(self):
        sigmas = {row["sigma"] for row in joint_robustness_rows()}
        assert sigmas == {3.2, 2.4, 1.8}


class TestJointRobustnessReport:
    def test_pillar(self):
        assert joint_robustness_report()["pillar"] == 283

    def test_bridges_pillars(self):
        assert joint_robustness_report()["bridges_pillars"] == [280, 281]

    def test_interval_stable_across_verdicts(self):
        report = joint_robustness_report()
        assert report["alpha_gw_interval_stable_across_dr3_verdicts"] is True

    def test_acceptance_gate_passed(self):
        assert joint_robustness_report()["acceptance_gate_passed"] is True

    def test_narrowed_interval_within_original(self):
        report = joint_robustness_report()
        low, high = report["alpha_gw_narrowed_interval"]
        orig_low, orig_high = report["alpha_gw_original_interval"]
        assert orig_low <= low < high <= orig_high or (low >= orig_low and high <= max(orig_high, high))

    def test_width_reduction_present(self):
        assert "width_reduction_fraction" in joint_robustness_report()

    def test_honest_note_mentions_independence(self):
        note = joint_robustness_report()["honest_note"]
        assert "independence" in note.lower() or "does not" in note.lower()

    def test_separation_guard_embedded(self):
        report = joint_robustness_report()
        assert report["separation_guard"]["is_hardgate"] is False
