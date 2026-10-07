# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 874 — NLO KK-tower survey of the CMB peak amplitude."""
from __future__ import annotations

import math

import pytest

from src.core.pillar874_cmb_amplitude_kk_survey import (
    BOUND_FRACTION,
    BOUND_HOLDS,
    CONVERGED_TO_CLOSED_FORM,
    KK_EXPLAINS_SUPPRESSION,
    KK_TOWER_CLOSED_FORM,
    KK_TOWER_FRACTION,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_MODES_SURVEYED,
    PEAK_ELL_VALUES,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    REQUIRED_CORRECTION_HI,
    REQUIRED_CORRECTION_LO,
    SHORTFALL_ORDERS_OF_MAGNITUDE,
    cmb_amplitude_kk_survey_summary,
    convergence_table,
    mode_contribution,
    tower_closed_form,
    tower_sum,
)


class TestPillar874Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 874
    def test_gate(self): assert PILLAR_GATE == "CMB_PEAK_AMPLITUDE_ARCHITECTURE_LIMIT_CONFIRMED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2496
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2516
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_modes_surveyed(self): assert N_MODES_SURVEYED == 100
    def test_bound_fraction(self): assert BOUND_FRACTION == pytest.approx(0.0135)
    def test_bound_is_one_point_three_five_percent(self):
        assert BOUND_FRACTION * 100.0 == pytest.approx(1.35)
    def test_peak_ells(self): assert PEAK_ELL_VALUES == (220, 540, 820)


class TestPillar874ModeSum:
    def test_first_mode(self): assert mode_contribution(1) == pytest.approx((5.0 / 74.0) ** 2)
    def test_mode_falls_as_fourth_power(self):
        assert mode_contribution(2) == pytest.approx(mode_contribution(1) / 16.0)
    def test_mode_rejects_zero(self):
        with pytest.raises(ValueError):
            mode_contribution(0)
    def test_mode_positive(self): assert mode_contribution(50) > 0.0
    def test_tower_sum_value(self): assert KK_TOWER_FRACTION == pytest.approx(0.0049412112, rel=1e-7)
    def test_tower_sum_function(self):
        assert tower_sum() == pytest.approx(KK_TOWER_FRACTION, rel=1e-12)
    def test_tower_sum_rejects_zero(self):
        with pytest.raises(ValueError):
            tower_sum(0)
    def test_tower_sum_monotone(self): assert tower_sum(50) < tower_sum(100)
    def test_closed_form_value(self):
        assert KK_TOWER_CLOSED_FORM == pytest.approx(0.0049412127, rel=1e-7)
    def test_closed_form_is_zeta_four(self):
        assert tower_closed_form() == pytest.approx((5.0 / 74.0) ** 2 * math.pi**4 / 90.0, rel=1e-12)
    def test_converged(self): assert CONVERGED_TO_CLOSED_FORM is True
    def test_sum_below_closed_form(self): assert KK_TOWER_FRACTION < KK_TOWER_CLOSED_FORM


class TestPillar874Convergence:
    def test_table_rows(self): assert len(convergence_table()) == 6
    def test_table_has_partial_sums(self): assert all("partial_sum" in r for r in convergence_table())
    def test_table_monotone(self):
        rows = convergence_table()
        assert all(rows[i]["partial_sum"] <= rows[i + 1]["partial_sum"] for i in range(len(rows) - 1))
    def test_table_approaches_unity(self):
        assert convergence_table()[-1]["fraction_of_closed_form"] > 0.999
    def test_table_custom_levels(self): assert len(convergence_table(levels=(1, 3))) == 2


class TestPillar874Bound:
    def test_bound_holds(self): assert BOUND_HOLDS is True
    def test_tower_below_bound(self): assert KK_TOWER_FRACTION < BOUND_FRACTION
    def test_required_correction_ordered(self): assert REQUIRED_CORRECTION_LO < REQUIRED_CORRECTION_HI
    def test_required_correction_far_above_tower(self):
        assert REQUIRED_CORRECTION_LO > KK_TOWER_FRACTION * 100.0
    def test_kk_does_not_explain_suppression(self): assert KK_EXPLAINS_SUPPRESSION is False
    def test_shortfall_orders(self):
        assert SHORTFALL_ORDERS_OF_MAGNITUDE == pytest.approx(2.8113166, rel=1e-6)
    def test_shortfall_above_two_decades(self): assert SHORTFALL_ORDERS_OF_MAGNITUDE > 2.0


class TestPillar874Summary:
    def test_summary_gate(self): assert cmb_amplitude_kk_survey_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert cmb_amplitude_kk_survey_summary()["pillar"] == 874
    def test_summary_lean4(self): assert cmb_amplitude_kk_survey_summary()["lean4_total_after"] == 2516
    def test_summary_kk_explains_false(self):
        assert cmb_amplitude_kk_survey_summary()["kk_explains_suppression"] is False
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_architecture_limit(self):
        assert "ARCHITECTURE" in cmb_amplitude_kk_survey_summary()["epistemic_status"].upper()
