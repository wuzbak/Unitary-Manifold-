# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1063_alpha_s_geometric_floor_theorem import (
    LEAN4_THEOREM_DELTA,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    ROUTES,
    alpha_s_floor_theorem_report,
    epsilon_min,
    pillar1063_summary,
    theorem_statement,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1063
    assert PILLAR_GATE == "SPRINT_CF_TRACK_A_ALPHA_S_FLOOR_THEOREM"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_A_ALPHA_S_FLOOR_THEOREM_STATED"
    assert PILLAR_VALID is True


def test_epsilon_min_topological_scaling() -> None:
    assert epsilon_min() == 5.0 / 74.0


def test_two_routes_covered() -> None:
    thm = theorem_statement()
    assert set(thm["routes_covered"]) == set(ROUTES)
    assert len(thm["routes_covered"]) == 2


def test_report_upgrades_justification() -> None:
    r = alpha_s_floor_theorem_report()
    assert r["runtime_label_changed"] is False
    assert r["lean4_theorem_delta"] == LEAN4_THEOREM_DELTA
    assert r["valid"] is True


def test_summary() -> None:
    s = pillar1063_summary()
    assert s["pillar"] == 1063
    assert s["lean4_delta"] == LEAN4_THEOREM_DELTA
