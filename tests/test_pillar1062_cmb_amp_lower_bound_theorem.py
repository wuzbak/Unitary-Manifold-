# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from fractions import Fraction

import pytest

from src.core.pillar1062_cmb_amp_lower_bound_theorem import (
    LEAN4_THEOREM_DELTA,
    LEAN4_THEOREM_NAME,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    cmb_amp_lower_bound_theorem_report,
    pillar1062_summary,
    reciprocal_deficit_bound,
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
    assert thm["warp_class_invariant_sign"] == "assumed_positive_not_derived"
    assert thm["closure_type"] == "CONDITIONAL_RECIPROCAL_UPPER_BOUND"
    assert thm["assumptions"] == ["0 < S_min", "S_min ≤ S"]
    assert thm["physical_bound_established"] is False
    assert thm["irreducibility_established"] is False
    assert thm["does_not_close_lane"] is True
    assert len(thm["falsifier_conditions"]) >= 1


def test_report_upgrades_justification() -> None:
    r = cmb_amp_lower_bound_theorem_report()
    assert r["runtime_label_changed"] is False
    assert r["lane_target"] == "CMB_AMPLITUDE_DERIVATION_OPEN"
    assert r["historical_lane_target"] == "CMB_AMP_CONFIRMED_IRREDUCIBLE"
    assert r["justification_upgrade"]["before"] == "TYPE_B_CRITERION_MET"
    assert r["justification_upgrade"]["after"] == "CONDITIONAL_ARITHMETIC_ONLY_PHYSICAL_BOUND_UNESTABLISHED"
    assert r["lean4_theorem_delta"] == LEAN4_THEOREM_DELTA == 0
    assert r["lean4_compilation_verified"] is False
    assert r["physical_theorem_proved"] is False
    assert r["scientific_progress"] is False
    assert r["valid"] is True


def test_summary() -> None:
    s = pillar1062_summary()
    assert s["pillar"] == 1062
    assert s["lean4_delta"] == LEAN4_THEOREM_DELTA


@pytest.mark.parametrize("minimum", [Fraction(1, 100), Fraction(25, 5476), Fraction(1), Fraction(2)])
@pytest.mark.parametrize("multiple", [1, 2, 10, 100])
def test_reciprocal_bound_has_correct_direction_independent_of_report(minimum, multiple) -> None:
    suppression = minimum * multiple
    expected_deficit = 1 / suppression
    expected_upper = 1 / minimum
    assert expected_deficit <= expected_upper
    actual = reciprocal_deficit_bound(float(minimum), float(suppression))
    assert actual["deficit"] == pytest.approx(float(expected_deficit))
    assert actual["deficit_upper_bound"] == pytest.approx(float(expected_upper))
    assert actual["deficit"] <= actual["deficit_upper_bound"]


@pytest.mark.parametrize("minimum", [0.001, 25 / 5476, 0.5, 1.0])
def test_positive_lower_bound_does_not_exclude_closure(minimum) -> None:
    actual = reciprocal_deficit_bound(minimum, 1.0)
    assert actual["deficit"] == 1.0
    assert actual["deficit"] <= actual["deficit_upper_bound"]


@pytest.mark.parametrize("minimum,suppression", [
    (0, 1), (-1, 1), (2, 1), (float("nan"), 1), (1, float("nan")),
    (float("inf"), float("inf")), (1, float("inf")),
    (True, 1), (1, True), ("0.1", 1), (None, 1), (5e-324, 1),
])
def test_invalid_reciprocal_hypotheses_fail_closed(minimum, suppression) -> None:
    with pytest.raises(ValueError):
        reciprocal_deficit_bound(minimum, suppression)


@pytest.mark.parametrize("n_w,k_cs", [(0, 74), (5, 0), (-5, 74), (True, 74), (5.0, 74), (5, 10**1000)])
def test_historical_formula_rejects_invalid_or_unrepresentable_inputs(n_w, k_cs) -> None:
    with pytest.raises(ValueError):
        s_min_lower_bound(n_w, k_cs)
