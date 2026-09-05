# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1066_qg_5d_eft_irreducibility_theorem import (
    LEAN4_THEOREM_DELTA,
    OBSTRUCTIONS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1066_summary,
    qg_5d_eft_irreducibility_theorem_report,
    theorem_statement,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1066
    assert PILLAR_GATE == "SPRINT_CF_TRACK_A_QG_IRREDUCIBILITY_NEGATIVE_THEOREM"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_A_QG_IRREDUCIBILITY_NEGATIVE_THEOREM_STATED"
    assert PILLAR_VALID is True


def test_obstruction_set_has_four_items() -> None:
    assert len(OBSTRUCTIONS) == 4


def test_theorem_is_negative_closure_type() -> None:
    thm = theorem_statement()
    assert thm["theorem_type"] == "NEGATIVE_IRREDUCIBILITY_THEOREM"
    assert thm["does_not_close_lane"] is True


def test_report_upgrades_justification() -> None:
    r = qg_5d_eft_irreducibility_theorem_report()
    assert r["runtime_label_changed"] is False
    assert r["lean4_theorem_delta"] == LEAN4_THEOREM_DELTA
    assert r["valid"] is True


def test_summary() -> None:
    s = pillar1066_summary()
    assert s["pillar"] == 1066
