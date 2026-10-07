# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 877 — Swampland Distance Conjecture bound on φ₀."""
from __future__ import annotations

import pytest

from src.core.pillar877_phi0_sdc_bounded import (
    DELTA_SDC,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_W,
    P834_OVERALL_STATUS,
    P834_SDC_VERDICT,
    PHI0_CONSISTENT_WITH_5D,
    PHI0_EXCURSION,
    PHI0_TARGET,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SDC_BOUNDED,
    TOWER_MASS_RATIO,
    phi0_excursion,
    phi0_sdc_summary,
    sdc_bound,
    tower_mass_ratio,
)


class TestPillar877Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 877
    def test_gate(self): assert PILLAR_GATE == "PHI0_SDC_BOUNDED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2551
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2571
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_n_w(self): assert N_W == 5
    def test_k_cs(self): assert K_CS == 74
    def test_phi0_target(self): assert PHI0_TARGET == pytest.approx(1.0)


class TestPillar877SDCBound:
    def test_bound_value(self): assert DELTA_SDC == pytest.approx(1.0 / 74.0)
    def test_bound_function(self): assert sdc_bound() == pytest.approx(DELTA_SDC, rel=1e-12)
    def test_bound_positive(self): assert DELTA_SDC > 0.0
    def test_bound_sub_planckian(self): assert DELTA_SDC < 1.0
    def test_bound_scales_inversely(self): assert sdc_bound(k_cs=148) == pytest.approx(DELTA_SDC / 2.0)
    def test_bound_rejects_zero(self):
        with pytest.raises(ValueError):
            sdc_bound(k_cs=0)
    def test_bound_below_two_percent(self): assert DELTA_SDC < 0.02


class TestPillar877Excursion:
    def test_excursion_value(self): assert PHI0_EXCURSION == pytest.approx(0.0)
    def test_excursion_function(self):
        assert phi0_excursion() == pytest.approx(PHI0_EXCURSION, rel=1e-12)
    def test_excursion_nonnegative(self): assert PHI0_EXCURSION >= 0.0
    def test_excursion_within_bound(self): assert PHI0_EXCURSION <= DELTA_SDC
    def test_excursion_custom(self): assert phi0_excursion(phi0=1.5, target=1.0) == pytest.approx(0.5)
    def test_sdc_bounded(self): assert SDC_BOUNDED is True
    def test_phi0_consistent_with_5d(self): assert PHI0_CONSISTENT_WITH_5D is True


class TestPillar877Tower:
    def test_tower_ratio(self): assert TOWER_MASS_RATIO == pytest.approx(1.0)
    def test_tower_function(self): assert tower_mass_ratio() == pytest.approx(TOWER_MASS_RATIO)
    def test_tower_decays(self): assert tower_mass_ratio(excursion=1.0) < 1.0
    def test_tower_rejects_negative(self):
        with pytest.raises(ValueError):
            tower_mass_ratio(excursion=-1.0)
    def test_tower_in_unit_interval(self): assert 0.0 < TOWER_MASS_RATIO <= 1.0
    def test_tower_lambda_scaling(self):
        assert tower_mass_ratio(excursion=1.0, lam=2.0) < tower_mass_ratio(excursion=1.0, lam=1.0)


class TestPillar877CrossPillar:
    def test_p834_sdc_verdict(self): assert P834_SDC_VERDICT == "PASS"
    def test_p834_overall_status(self): assert P834_OVERALL_STATUS == "PASS"
    def test_verdicts_consistent(self): assert P834_SDC_VERDICT == P834_OVERALL_STATUS


class TestPillar877Summary:
    def test_summary_gate(self): assert phi0_sdc_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert phi0_sdc_summary()["pillar"] == 877
    def test_summary_lean4(self): assert phi0_sdc_summary()["lean4_total_after"] == 2571
    def test_summary_bounded(self): assert phi0_sdc_summary()["sdc_bounded"] is True
    def test_summary_delta(self): assert phi0_sdc_summary()["delta_sdc"] == pytest.approx(DELTA_SDC)
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_partial_closure(self):
        assert "PARTIAL_CLOSURE" in phi0_sdc_summary()["epistemic_status"].upper()
