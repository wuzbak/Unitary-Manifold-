# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 866 — tightened α_s route D."""
from __future__ import annotations

import pytest

from src.core.pillar866_alphas_7d_route_d_tightened import (
    ALPHA_S_COMBINED,
    ALPHA_S_COMBINED_UNCERTAINTY,
    ALPHA_S_PDG,
    ALPHA_S_ROUTE_D,
    KAHLER_WIDTH,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    PDG_INSIDE_TIGHTENED,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    ROUTE_AGREEMENT_FRACTION,
    TENSION_SIGMA,
    TIGHTENED_INTERVAL,
    TIGHTENED_WIDTH,
    TIGHTENING_ACHIEVED,
    ALPHA_S_KAHLER,
    ROUTE_D_INTERVAL,
    alphas_route_d_tightened_summary,
    combine_routes,
    interval_intersection,
)


class TestPillar866Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 866
    def test_gate(self): assert PILLAR_GATE == "ALPHA_S_7D_ROUTE_D_TIGHTENED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 15
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2326
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2341
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_pdg_reference(self): assert ALPHA_S_PDG == pytest.approx(0.1179)


class TestPillar866RouteD:
    def test_route_d_value(self): assert ALPHA_S_ROUTE_D == pytest.approx(0.11635245, rel=1e-6)
    def test_route_d_interval_ordered(self):
        assert ROUTE_D_INTERVAL[0] < ROUTE_D_INTERVAL[1]
    def test_route_d_positive(self): assert ALPHA_S_ROUTE_D > 0.0
    def test_route_d_near_pdg(self): assert abs(ALPHA_S_ROUTE_D - ALPHA_S_PDG) < 0.005


class TestPillar866Combination:
    def test_combined_value(self): assert ALPHA_S_COMBINED == pytest.approx(0.11629909, rel=1e-6)
    def test_combined_between_routes(self):
        assert min(ALPHA_S_ROUTE_D, ALPHA_S_KAHLER) <= ALPHA_S_COMBINED <= max(ALPHA_S_ROUTE_D, ALPHA_S_KAHLER)
    def test_interval_intersection_basic(self):
        assert interval_intersection((0.0, 2.0), (1.0, 3.0)) == (1.0, 2.0)
    def test_interval_intersection_disjoint_raises(self):
        with pytest.raises(ValueError):
            interval_intersection((0.0, 1.0), (2.0, 3.0))
    def test_combined_uncertainty(self):
        assert ALPHA_S_COMBINED_UNCERTAINTY == pytest.approx(5.336708e-05, rel=1e-5)
    def test_combined_uncertainty_positive(self): assert ALPHA_S_COMBINED_UNCERTAINTY > 0.0
    def test_combine_routes_symmetric(self):
        assert combine_routes(0.10, 0.12) == pytest.approx(0.11)
    def test_combine_routes_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            combine_routes(0.0, 0.12)
    def test_combine_routes_default_matches_constant(self):
        assert combine_routes() == pytest.approx(ALPHA_S_COMBINED, rel=1e-12)


class TestPillar866Interval:
    def test_interval_ordered(self): assert TIGHTENED_INTERVAL[0] < TIGHTENED_INTERVAL[1]
    def test_interval_low(self): assert TIGHTENED_INTERVAL[0] == pytest.approx(0.09845742, rel=1e-6)
    def test_interval_high(self): assert TIGHTENED_INTERVAL[1] == pytest.approx(0.13857606, rel=1e-6)
    def test_tightened_width(self): assert TIGHTENED_WIDTH == pytest.approx(0.04011864, rel=1e-6)
    def test_kahler_width(self): assert KAHLER_WIDTH == pytest.approx(0.10773035, rel=1e-6)
    def test_tightening_achieved(self): assert TIGHTENING_ACHIEVED is True
    def test_tightened_narrower_than_kahler(self): assert TIGHTENED_WIDTH < KAHLER_WIDTH
    def test_pdg_inside_tightened(self): assert PDG_INSIDE_TIGHTENED is True
    def test_interval_still_wide(self): assert TIGHTENED_WIDTH > 0.01


class TestPillar866Tension:
    def test_route_agreement_fraction(self):
        assert ROUTE_AGREEMENT_FRACTION == pytest.approx(0.00091776, rel=1e-4)
    def test_routes_agree_below_one_percent(self): assert ROUTE_AGREEMENT_FRACTION < 0.01
    def test_tension_sigma(self): assert TENSION_SIGMA == pytest.approx(1.60091, rel=1e-4)
    def test_tension_below_two_sigma(self): assert TENSION_SIGMA < 2.0


class TestPillar866Summary:
    def test_summary_gate(self): assert alphas_route_d_tightened_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert alphas_route_d_tightened_summary()["pillar"] == 866
    def test_summary_lean4(self): assert alphas_route_d_tightened_summary()["lean4_total_after"] == 2341
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_not_closure(self):
        assert "CLOSED" not in alphas_route_d_tightened_summary()["epistemic_status"].upper()
