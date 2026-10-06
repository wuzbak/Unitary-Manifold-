# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 867 — cross-dimensional α_s audit."""
from __future__ import annotations

import pytest

from src.core.pillar867_alphas_cross_dimensional_audit import (
    ARCHITECTURE_LIMITS_CERTIFIED,
    AUDIT_COMPLETE,
    BEST_CENTRAL,
    BEST_TENSION_SIGMA,
    DIMENSIONS_AUDITED,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_ARCHITECTURE_LIMIT_ROUTES,
    N_PARTIAL_ROUTES,
    N_ROUTES,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    ROUTES,
    alphas_cross_dimensional_audit_summary,
    route_by_label,
)


class TestPillar867Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 867
    def test_gate(self): assert PILLAR_GATE == "ALPHA_S_ALL_DIMENSIONAL_AUDIT_COMPLETE"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 15
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2341
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2356
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER


class TestPillar867Routes:
    def test_route_count(self): assert N_ROUTES == 6
    def test_routes_length_matches(self): assert len(ROUTES) == N_ROUTES
    def test_route_labels_unique(self):
        assert len({r["route"] for r in ROUTES}) == N_ROUTES
    def test_every_route_has_verdict(self): assert all("verdict" in r for r in ROUTES)
    def test_every_route_has_pillar(self): assert all(isinstance(r["pillar"], int) for r in ROUTES)
    def test_route_a_architecture_limit(self):
        assert route_by_label("A")["verdict"] == "ARCHITECTURE_LIMIT"
    def test_route_d_partial(self): assert route_by_label("D")["verdict"] == "PARTIAL"
    def test_route_e_narrowed(self): assert route_by_label("E")["verdict"] == "PARTIAL_NARROWED"
    def test_route_de_tightened(self): assert route_by_label("D+E")["verdict"] == "TIGHTENED"
    def test_route_e_from_pillar865(self): assert route_by_label("E")["pillar"] == 865
    def test_route_de_from_pillar866(self): assert route_by_label("D+E")["pillar"] == 866
    def test_unknown_route_raises(self):
        with pytest.raises(KeyError):
            route_by_label("Z")


class TestPillar867Tallies:
    def test_architecture_limit_routes(self): assert N_ARCHITECTURE_LIMIT_ROUTES == 3
    def test_partial_routes(self): assert N_PARTIAL_ROUTES == 2
    def test_dimensions_audited(self): assert DIMENSIONS_AUDITED == [5, 7]
    def test_five_d_routes_all_limited(self):
        five_d = [r for r in ROUTES if r["dimension"] == 5]
        assert all(r["verdict"] == "ARCHITECTURE_LIMIT" for r in five_d)
    def test_seven_d_routes_present(self):
        assert any(r["dimension"] == 7 for r in ROUTES)
    def test_tally_consistency(self):
        assert N_ARCHITECTURE_LIMIT_ROUTES + N_PARTIAL_ROUTES < N_ROUTES


class TestPillar867Synthesis:
    def test_best_central(self): assert BEST_CENTRAL == pytest.approx(0.11629909, rel=1e-6)
    def test_best_tension(self): assert BEST_TENSION_SIGMA == pytest.approx(1.60091, rel=1e-4)
    def test_best_tension_below_two_sigma(self): assert BEST_TENSION_SIGMA < 2.0
    def test_audit_complete(self): assert AUDIT_COMPLETE is True
    def test_two_architecture_limits_certified(self):
        assert len(ARCHITECTURE_LIMITS_CERTIFIED) == 2
    def test_certifications_labelled(self):
        assert all("ARCHITECTURE_LIMIT" in c for c in ARCHITECTURE_LIMITS_CERTIFIED)
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2


class TestPillar867Summary:
    def test_summary_gate(self): assert alphas_cross_dimensional_audit_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert alphas_cross_dimensional_audit_summary()["pillar"] == 867
    def test_summary_lean4(self):
        assert alphas_cross_dimensional_audit_summary()["lean4_total_after"] == 2356
    def test_summary_routes(self): assert alphas_cross_dimensional_audit_summary()["n_routes"] == 6
    def test_summary_no_closure_claim(self):
        assert "CLOSED" not in alphas_cross_dimensional_audit_summary()["epistemic_status"].upper()
