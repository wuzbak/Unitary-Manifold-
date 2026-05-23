# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar363_lambda5_derivation.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar363_lambda5_derivation import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    K_WARP, LAMBDA5_FROM_WARP, K_CS, PI_KR,
    separation_guard, rs1_warp_factor, bulk_cc_from_warp,
    gw_mechanism_constraint, derivation_attempt_ftum_entropy,
    derivation_attempt_gw_stabilization, derivation_attempt_orbifold_bc,
    lambda5_derivation_audit, pillar363_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 363
    def test_status(self): assert PILLAR_STATUS == "MINIMAL_AXIOM"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_lambda5_negative(self): assert LAMBDA5_FROM_WARP < 0
    def test_k_warp_positive(self): assert K_WARP > 0
    def test_k_cs(self): assert K_CS == 74
    def test_pi_kr(self): assert abs(PI_KR - 37.0) < 1.0


class TestRS1WarpFactor:
    def test_at_zero(self): assert abs(rs1_warp_factor(0.0) - 1.0) < 1e-10
    def test_decreasing(self): assert rs1_warp_factor(1.0) < rs1_warp_factor(0.0)
    def test_positive(self): assert rs1_warp_factor(5.0) > 0
    def test_symmetric(self):
        assert abs(rs1_warp_factor(-1.0) - rs1_warp_factor(1.0)) < 1e-10


class TestBulkCC:
    def test_negative(self): assert bulk_cc_from_warp() < 0
    def test_formula(self):
        k = K_WARP
        assert abs(bulk_cc_from_warp(k) - (-6 * k**2)) < 1e-10
    def test_zero_k_gives_zero(self): assert bulk_cc_from_warp(0.0) == 0.0


class TestGWConstraint:
    def test_returns_dict(self): assert isinstance(gw_mechanism_constraint(), dict)
    def test_gw_works_if_negative(self):
        result = gw_mechanism_constraint()
        assert result["gw_works_if_lambda5_negative"] is True
    def test_conditional(self):
        result = gw_mechanism_constraint()
        assert result["derivation_status"] == "CONDITIONAL"


class TestDerivationAttempts:
    def test_attempt1_circular(self):
        result = derivation_attempt_ftum_entropy()
        assert result["status"] == "CIRCULAR"
    def test_attempt2_conditional(self):
        result = derivation_attempt_gw_stabilization()
        assert result["status"] == "CONDITIONAL_DERIVATION"
    def test_attempt3_conditional(self):
        result = derivation_attempt_orbifold_bc()
        assert result["status"] == "CONDITIONAL_DERIVATION"
    def test_all_attempts_numbered(self):
        for fn, n in [(derivation_attempt_ftum_entropy, 1),
                      (derivation_attempt_gw_stabilization, 2),
                      (derivation_attempt_orbifold_bc, 3)]:
            assert fn()["attempt"] == n


class TestAudit:
    def test_returns_dict(self): assert isinstance(lambda5_derivation_audit(), dict)
    def test_pillar_363(self): assert lambda5_derivation_audit()["pillar"] == 363
    def test_minimal_axiom_label(self):
        result = lambda5_derivation_audit()
        assert result["formal_certification"]["label"] == "MINIMAL_AXIOM"
    def test_three_attempts(self):
        result = lambda5_derivation_audit()
        assert len(result["derivation_attempts"]) == 3
    def test_falsifiable_present(self):
        result = lambda5_derivation_audit()
        assert "falsifiable" in result["formal_certification"]


class TestSummary:
    def test_pillar_363(self): assert pillar363_summary()["pillar"] == 363
    def test_status(self): assert pillar363_summary()["status"] == "MINIMAL_AXIOM"


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
