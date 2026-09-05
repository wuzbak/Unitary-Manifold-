# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1062_cmb_amp_lower_bound_theorem import (
    LEAN4_THEOREM_DELTA,
    LEAN4_THEOREM_NAME,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    cmb_amp_lower_bound_theorem_report,
    pillar1062_summary,
    s_min_lower_bound,
    theorem_statement,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1062
    assert PILLAR_GATE == "SPRINT_CF_TRACK_A_CMB_LOWER_BOUND_THEOREM"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_A_CMB_LOWER_BOUND_THEOREM_STATED"
    assert PILLAR_VALID is True


def test_lower_bound_positive() -> None:
    assert s_min_lower_bound() > 0.0


def test_theorem_packet_shape() -> None:
    thm = theorem_statement()
    assert thm["name"] == LEAN4_THEOREM_NAME
    assert thm["topological_inputs"] == {"n_w": 5, "k_cs": 74}
    assert thm["warp_class_invariant_sign"] == "positive"
    assert thm["closure_type"] == "LOWER_BOUND_FLOOR_THEOREM"
    assert thm["does_not_close_lane"] is True
    assert len(thm["falsifier_conditions"]) >= 1


def test_report_upgrades_justification() -> None:
    r = cmb_amp_lower_bound_theorem_report()
    assert r["runtime_label_changed"] is False
    assert r["justification_upgrade"]["before"] == "TYPE_B_CRITERION_MET"
    assert r["justification_upgrade"]["after"] == "LEAN4_LOWER_BOUND_THEOREM_STATED"
    assert r["lean4_theorem_delta"] == LEAN4_THEOREM_DELTA
    assert r["valid"] is True


def test_summary() -> None:
    s = pillar1062_summary()
    assert s["pillar"] == 1062
    assert s["lean4_delta"] == LEAN4_THEOREM_DELTA
