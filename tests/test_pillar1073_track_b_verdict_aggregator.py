# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1073_track_b_verdict_aggregator import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    TRACK_B_ATTEMPT_PILLARS,
    TRACK_B_AUDIT_PILLARS,
    pillar1073_summary,
    track_b_verdict_report,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1073
    assert PILLAR_GATE == "SPRINT_CF_TRACK_B_VERDICT_AGGREGATOR"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_B_VERDICT_AGGREGATOR_COMPLETE"
    assert PILLAR_VALID is True


def test_verdict_is_honest_no_false_closure() -> None:
    r = track_b_verdict_report()
    # None of the three attempt pillars actually close their lane in v36.2.
    assert r["all_lanes_closed"] is False
    assert r["verdict"] == "EXTENSION_TIGHTENED_BUT_NO_CLOSURE_EARNED"
    assert r["closure_earned"] is False
    assert r["runtime_labels_changed"] is False


def test_parameter_free_and_hardgate_ok() -> None:
    r = track_b_verdict_report()
    assert r["parameter_free_extension"] is True
    assert r["hardgate_non_breakage_verified"] is True


def test_track_b_pillar_lists() -> None:
    assert TRACK_B_ATTEMPT_PILLARS == [1068, 1069, 1070]
    assert TRACK_B_AUDIT_PILLARS == [1071, 1072]


def test_summary() -> None:
    s = pillar1073_summary()
    assert s["pillar"] == 1073
    assert s["closure_earned"] is False
