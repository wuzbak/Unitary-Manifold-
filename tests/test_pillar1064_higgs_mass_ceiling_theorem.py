# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1064_higgs_mass_ceiling_theorem import (
    LEAN4_THEOREM_DELTA,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    higgs_mass_ceiling_theorem_report,
    lambda_max,
    pillar1064_summary,
    theorem_statement,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1064
    assert PILLAR_GATE == "SPRINT_CF_TRACK_A_HIGGS_MASS_CEILING_THEOREM"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_A_HIGGS_MASS_CEILING_THEOREM_STATED"
    assert PILLAR_VALID is True


def test_lambda_max_positive_and_below_sm() -> None:
    lm = lambda_max()
    assert lm > 0.0
    assert lm < 0.129


def test_theorem_gap_positive() -> None:
    thm = theorem_statement()
    assert thm["gap_is_positive"] is True
    assert thm["gap_orders_of_magnitude"] == 2
    assert thm["closure_type"] == "UPPER_BOUND_CEILING_THEOREM"
    assert thm["does_not_close_lane"] is True


def test_report_upgrades_justification() -> None:
    r = higgs_mass_ceiling_theorem_report()
    assert r["runtime_label_changed"] is False
    assert r["lean4_theorem_delta"] == LEAN4_THEOREM_DELTA
    assert r["valid"] is True


def test_summary() -> None:
    s = pillar1064_summary()
    assert s["pillar"] == 1064
    assert s["lean4_delta"] == LEAN4_THEOREM_DELTA
