# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 636 — SU(3) internal orbifold-equivalence."""
from __future__ import annotations

from src.core.pillar636_su3_orbifold_equivalence import (
    HEAVY_GAUGE_BOSONS,
    M_KK_GEV,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SM_GAUGE_GROUP,
    SU3_STATUS_AFTER,
    SU3_STATUS_BEFORE,
    SU5_RANK,
    VERSION,
    Z2_ODD_BC_REUSE,
    orbifold_equivalence_theorem,
    pillar_report,
    residual_open,
    su5_decomposition,
    what_is_NOT_claimed,
    what_is_claimed,
    z2_boundary_condition,
)

REPORT = pillar_report()
BC = z2_boundary_condition()
DECOMP = su5_decomposition()
THEOREM = orbifold_equivalence_theorem()
RESIDUAL = residual_open()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 636

    def test_status(self):
        assert PILLAR_STATUS == "CONDITIONAL_SU5_PROJECTION_NOT_METRIC_DERIVED"

    def test_z2_bc_reuse(self):
        assert Z2_ODD_BC_REUSE is False

    def test_sm_gauge_group(self):
        assert "SU(3)" in SM_GAUGE_GROUP
        assert "SU(2)" in SM_GAUGE_GROUP

    def test_status_advance(self):
        assert SU3_STATUS_BEFORE == "SUBSTANTIALLY_CLOSED"
        assert SU3_STATUS_AFTER == "CONDITIONAL_SU5_PROJECTION_NOT_METRIC_DERIVED"


class TestZ2BoundaryCondition:
    def test_condition_format(self):
        assert "G_{μ5}" in BC["condition"]

    def test_reused_for_su5(self):
        assert BC["reused_for_su5_projection"] is False
        assert BC["internal_lift_required"]

    def test_z2_even_modes(self):
        assert len(BC["z2_parity_map"]["Z2_even_modes"]) == 3

    def test_z2_odd_modes(self):
        assert len(BC["z2_parity_map"]["Z2_odd_modes"]) == 2


class TestSU5Decomposition:
    def test_su5_generators(self):
        assert DECOMP["su5_generators"] == 24

    def test_sm_generators(self):
        assert DECOMP["sm_generators_even"] == 12

    def test_heavy_generators(self):
        assert DECOMP["heavy_generators_odd"] == 12

    def test_decoupled(self):
        assert DECOMP["decoupled_at_low_energy"] == "conditional on energy below the KK gap"

    def test_heavy_mass(self):
        assert DECOMP["heavy_mass_gev"] is None
        assert DECOMP["illustrative_kk_scale_gev"] == M_KK_GEV


class TestOrbifoldTheorem:
    def test_equivalence_established(self):
        assert THEOREM["equivalence_established"] is False
        assert len(THEOREM["inequivalent_lifts"]) == 3

    def test_lean4_nominated(self):
        assert THEOREM["lean4_proof_status"] == "NO_FUNCTIONAL_ANALYTIC_PROOF"


class TestResidualOpen:
    def test_residual_listed(self):
        assert len(RESIDUAL["open_item"]) > 5


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 3
        assert len(what_is_NOT_claimed()) >= 3
