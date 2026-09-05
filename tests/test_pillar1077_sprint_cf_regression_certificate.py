# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1077_sprint_cf_regression_certificate import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SPRINT_TRACK_PILLARS,
    pillar1077_summary,
    sprint_cf_regression_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1077
    assert PILLAR_GATE == "SPRINT_CF_REGRESSION_CERTIFICATE"
    assert PILLAR_STATUS == "SPRINT_CF_REGRESSION_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_sprint_track_pillar_coverage() -> None:
    assert SPRINT_TRACK_PILLARS["track_a_floor_theorems"] == [
        1062, 1063, 1064, 1065, 1066, 1067
    ]
    assert SPRINT_TRACK_PILLARS["track_b_extension_attempt"] == [
        1068, 1069, 1070, 1071, 1072, 1073
    ]
    assert SPRINT_TRACK_PILLARS["track_c_falsifier_sharpening"] == [1074, 1075, 1076]


def test_sprint_success_conditions() -> None:
    r = sprint_cf_regression_certificate()
    assert r["track_a_valid"] is True
    assert r["track_b_valid"] is True
    assert r["track_c_valid"] is True
    assert r["hardgate_untouched"] is True
    assert r["parameter_free_extension"] is True
    assert r["meaningful_progress"] is True
    assert r["sprint_success"] is True
    # Track B verdict must be the honest binary outcome, not a false closure.
    assert r["track_b_verdict"] == "EXTENSION_TIGHTENED_BUT_NO_CLOSURE_EARNED"


def test_next_pillar_slot_is_1078() -> None:
    r = sprint_cf_regression_certificate()
    assert r["next_pillar_slot"] == 1078


def test_summary() -> None:
    s = pillar1077_summary()
    assert s["pillar"] == 1077
    assert s["sprint_success"] is True
