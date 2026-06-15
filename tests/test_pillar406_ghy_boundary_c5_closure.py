# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
tests/test_pillar406_ghy_boundary_c5_closure.py
===============================================
Tests for Pillar 406 — GHY Boundary Terms and C5 Compatibility Closure.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar406_ghy_boundary_c5_closure import (
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    PI_KR,
    K_WARP,
    PHI0_BRAID,
    KAPPA_5_SQ,
    K_OVER_MPL,
    F_BRANE_NATURAL,
    ghy_extrinsic_curvature,
    ghy_boundary_term_uniqueness,
    orbifold_junction_conditions,
    c5_orbifold_compatibility,
    brane_localized_gravity_c5_check,
    full_uniqueness_chain,
    admission_13_closed_verdict,
    pillar406_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 406

    def test_pillar_status(self):
        assert PILLAR_STATUS == "CLOSED"

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_phi0_braid_formula(self):
        assert PHI0_BRAID == pytest.approx(5.0 * math.pi / 74.0, rel=1e-9)

    def test_kappa_5_sq(self):
        assert KAPPA_5_SQ == pytest.approx(1.0, rel=1e-9)

    def test_k_over_mpl(self):
        assert K_OVER_MPL == pytest.approx(0.10, rel=1e-6)

    def test_f_brane_natural_positive(self):
        assert F_BRANE_NATURAL > 0.0

    def test_k_warp(self):
        assert K_WARP == pytest.approx(1.0, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# GHY extrinsic curvature
# ─────────────────────────────────────────────────────────────────────────────

class TestGhyExtrinsicCurvature:
    def test_returns_dict_uv(self):
        r = ghy_extrinsic_curvature("UV")
        assert isinstance(r, dict)

    def test_returns_dict_ir(self):
        r = ghy_extrinsic_curvature("IR")
        assert isinstance(r, dict)

    def test_uv_y_position_zero(self):
        r = ghy_extrinsic_curvature("UV")
        assert r["y_position"] == pytest.approx(0.0, abs=1e-15)

    def test_ir_y_position_pi(self):
        r = ghy_extrinsic_curvature("IR")
        assert r["ir_y_position_is_pi"] if "ir_y_position_is_pi" in r else r["y_position"] == pytest.approx(math.pi, rel=1e-9)

    def test_uv_warp_factor_one(self):
        r = ghy_extrinsic_curvature("UV")
        assert r["warp_factor"] == pytest.approx(1.0, rel=1e-9)

    def test_ir_warp_factor_suppressed(self):
        r = ghy_extrinsic_curvature("IR")
        assert r["warp_factor"] < 1e-10  # e^{-74} is essentially zero

    def test_uv_k_trace_negative(self):
        r = ghy_extrinsic_curvature("UV")
        assert r["k_trace"] < 0.0

    def test_ir_k_trace_positive(self):
        r = ghy_extrinsic_curvature("IR")
        assert r["k_trace"] > 0.0

    def test_uv_c5_compatible(self):
        r = ghy_extrinsic_curvature("UV")
        assert r["c5_compatible"]

    def test_ir_c5_compatible(self):
        r = ghy_extrinsic_curvature("IR")
        assert r["c5_compatible"]

    def test_uses_lc_only_uv(self):
        r = ghy_extrinsic_curvature("UV")
        assert r["uses_levi_civita_only"]

    def test_uses_lc_only_ir(self):
        r = ghy_extrinsic_curvature("IR")
        assert r["uses_levi_civita_only"]

    def test_invalid_brane_raises(self):
        with pytest.raises(ValueError):
            ghy_extrinsic_curvature("MIDDLE")


# ─────────────────────────────────────────────────────────────────────────────
# GHY boundary term uniqueness
# ─────────────────────────────────────────────────────────────────────────────

class TestGhyBoundaryTermUniqueness:
    def test_returns_dict(self):
        r = ghy_boundary_term_uniqueness()
        assert isinstance(r, dict)

    def test_connection_unique_under_c5(self):
        r = ghy_boundary_term_uniqueness()
        assert r["connection_unique_under_c5"]

    def test_c5_compatible(self):
        r = ghy_boundary_term_uniqueness()
        assert r["c5_compatible"]

    def test_uniqueness_proof_present(self):
        r = ghy_boundary_term_uniqueness()
        assert len(r["uniqueness_proof"]) > 100

    def test_uniqueness_proof_mentions_lc(self):
        r = ghy_boundary_term_uniqueness()
        assert (
            "Levi-Civita" in r["uniqueness_proof"]
            or "Levi" in r["uniqueness_proof"]
            or "torsion-free" in r["uniqueness_proof"]
        )

    def test_uv_brane_in_result(self):
        r = ghy_boundary_term_uniqueness()
        assert "uv_brane" in r

    def test_ir_brane_in_result(self):
        r = ghy_boundary_term_uniqueness()
        assert "ir_brane" in r

    def test_verdict_mentions_uniquely_determined(self):
        r = ghy_boundary_term_uniqueness()
        assert "UNIQUELY DETERMINED" in r["verdict"] or "unique" in r["verdict"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# Orbifold junction conditions
# ─────────────────────────────────────────────────────────────────────────────

class TestOrbifoldJunctionConditions:
    def test_returns_dict(self):
        r = orbifold_junction_conditions()
        assert isinstance(r, dict)

    def test_uv_k_trace_nonzero(self):
        r = orbifold_junction_conditions()
        assert r["uv_k_trace"] != 0.0

    def test_ir_k_trace_opposite_sign(self):
        r = orbifold_junction_conditions()
        # UV: negative K; IR: positive K (sign from outward normal convention)
        assert r["uv_k_trace"] < 0.0
        assert r["ir_k_trace"] > 0.0

    def test_delta_k_uv_double_k_uv(self):
        r = orbifold_junction_conditions()
        # Under Z₂: [K]_UV = 2 K^+_UV
        assert r["delta_k_uv"] == pytest.approx(2.0 * r["uv_k_trace"], rel=1e-9)

    def test_torsion_free_uv(self):
        r = orbifold_junction_conditions()
        assert r["torsion_free_uv"]

    def test_torsion_free_ir(self):
        r = orbifold_junction_conditions()
        assert r["torsion_free_ir"]

    def test_c5_compatible_at_fixed_points(self):
        r = orbifold_junction_conditions()
        assert r["c5_compatible_at_fixed_points"]

    def test_verdict_mentions_c5(self):
        r = orbifold_junction_conditions()
        assert "C5" in r["verdict"] or "c5" in r["verdict"].lower()

    def test_verdict_mentions_torsion_free(self):
        r = orbifold_junction_conditions()
        assert "torsion-free" in r["verdict"].lower() or "torsion" in r["verdict"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# C5 orbifold compatibility
# ─────────────────────────────────────────────────────────────────────────────

class TestC5OrbifoldCompatibility:
    def test_returns_dict(self):
        r = c5_orbifold_compatibility()
        assert isinstance(r, dict)

    def test_christoffel_symmetric(self):
        r = c5_orbifold_compatibility()
        assert r["christoffel_symmetric"]

    def test_torsion_tensor_zero(self):
        r = c5_orbifold_compatibility()
        assert r["torsion_tensor_zero"]

    def test_jump_is_not_torsion(self):
        r = c5_orbifold_compatibility()
        assert not r["jump_is_torsion"]

    def test_c5_satisfied_globally(self):
        r = c5_orbifold_compatibility()
        assert r["c5_satisfied_globally"]

    def test_explanation_present(self):
        r = c5_orbifold_compatibility()
        assert len(r["explanation"]) > 100

    def test_verdict_mentions_globally(self):
        r = c5_orbifold_compatibility()
        assert "global" in r["verdict"].lower() or "C5" in r["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# Brane-localized gravity C5 check
# ─────────────────────────────────────────────────────────────────────────────

class TestBraneLocalizedGravityC5Check:
    def test_returns_dict(self):
        r = brane_localized_gravity_c5_check()
        assert isinstance(r, dict)

    def test_r4_uses_4d_lc(self):
        r = brane_localized_gravity_c5_check()
        assert r["r4_uses_4d_lc_connection"]

    def test_r4_does_not_use_5d(self):
        r = brane_localized_gravity_c5_check()
        assert not r["r4_uses_5d_connection"]

    def test_c5_compatible(self):
        r = brane_localized_gravity_c5_check()
        assert r["c5_compatible"]

    def test_bulk_uniqueness_preserved(self):
        r = brane_localized_gravity_c5_check()
        assert r["bulk_uniqueness_preserved"]

    def test_f_brane_natural(self):
        r = brane_localized_gravity_c5_check()
        assert r["f_brane_is_natural"]

    def test_physical_meaning_present(self):
        r = brane_localized_gravity_c5_check()
        assert len(r["physical_meaning"]) > 50

    def test_verdict_c5_compatible(self):
        r = brane_localized_gravity_c5_check()
        assert "C5 compatible" in r["verdict"] or "compatible" in r["verdict"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# Full uniqueness chain
# ─────────────────────────────────────────────────────────────────────────────

class TestFullUniquenessChain:
    def test_returns_dict(self):
        r = full_uniqueness_chain()
        assert isinstance(r, dict)

    def test_all_satisfied(self):
        r = full_uniqueness_chain()
        assert r["all_satisfied"]

    def test_bulk_metric_unique(self):
        r = full_uniqueness_chain()
        assert r["bulk_metric_unique"]

    def test_boundary_terms_unique(self):
        r = full_uniqueness_chain()
        assert r["boundary_terms_unique"]

    def test_c5_globally_satisfied(self):
        r = full_uniqueness_chain()
        assert r["c5_globally_satisfied"]

    def test_constraints_c1_through_c5(self):
        r = full_uniqueness_chain()
        for constraint in ["C1", "C2", "C3", "C4", "C5"]:
            assert constraint in r["constraints"]

    def test_ghy_constraint_present(self):
        r = full_uniqueness_chain()
        assert "GHY" in r["constraints"]

    def test_brane_constraint_present(self):
        r = full_uniqueness_chain()
        assert "BRANE" in r["constraints"]

    def test_c1_satisfied(self):
        r = full_uniqueness_chain()
        assert r["constraints"]["C1"]["status"] == "SATISFIED"

    def test_c5_satisfied(self):
        r = full_uniqueness_chain()
        assert r["constraints"]["C5"]["status"] == "SATISFIED"

    def test_ghy_uniquely_determined(self):
        r = full_uniqueness_chain()
        assert r["constraints"]["GHY"]["status"] == "UNIQUELY_DETERMINED"

    def test_brane_c5_compatible(self):
        r = full_uniqueness_chain()
        assert r["constraints"]["BRANE"]["status"] == "C5_COMPATIBLE"

    def test_verdict_mentions_closed(self):
        r = full_uniqueness_chain()
        assert "CLOSED" in r["verdict"] or "closed" in r["verdict"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# Admission 13 closed verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission13ClosedVerdict:
    def test_returns_dict(self):
        r = admission_13_closed_verdict()
        assert isinstance(r, dict)

    def test_admission_number(self):
        r = admission_13_closed_verdict()
        assert r["admission"] == 13

    def test_previous_status(self):
        r = admission_13_closed_verdict()
        assert r["previous_status"] == "NARROWED_GAP"

    def test_new_status(self):
        r = admission_13_closed_verdict()
        assert r["new_status"] == "CLOSED"

    def test_ghy_unique(self):
        r = admission_13_closed_verdict()
        assert r["ghy_unique"]

    def test_orbifold_c5_compatible(self):
        r = admission_13_closed_verdict()
        assert r["orbifold_c5_compatible"]

    def test_brane_c5_compatible(self):
        r = admission_13_closed_verdict()
        assert r["brane_c5_compatible"]

    def test_bulk_uniqueness_preserved(self):
        r = admission_13_closed_verdict()
        assert r["bulk_uniqueness_preserved"]

    def test_chain_complete(self):
        r = admission_13_closed_verdict()
        assert r["chain_complete"]

    def test_closure_summary_present(self):
        r = admission_13_closed_verdict()
        assert len(r["closure_summary"]) > 100

    def test_honest_residual_present(self):
        r = admission_13_closed_verdict()
        assert len(r["honest_residual"]) > 50

    def test_citation_present(self):
        r = admission_13_closed_verdict()
        assert "pillar406" in r["citation"].lower() or "Pillar 406" in r["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Full summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar406Summary:
    def test_returns_dict(self):
        r = pillar406_summary()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = pillar406_summary()
        assert r["pillar_number"] == 406

    def test_status(self):
        r = pillar406_summary()
        assert r["status"] == "CLOSED"

    def test_admission_13_closed(self):
        r = pillar406_summary()
        assert r["admission_new_status"] == "CLOSED"

    def test_ghy_unique(self):
        r = pillar406_summary()
        assert r["ghy_unique"]

    def test_c5_globally_satisfied(self):
        r = pillar406_summary()
        assert r["c5_globally_satisfied"]

    def test_brane_ok(self):
        r = pillar406_summary()
        assert r["brane_localized_gravity_c5_ok"]

    def test_bulk_uniqueness_preserved(self):
        r = pillar406_summary()
        assert r["bulk_uniqueness_preserved"]

    def test_honest_residual_present(self):
        r = pillar406_summary()
        assert len(r["honest_residual"]) > 50

    def test_key_result_mentions_ghy(self):
        r = pillar406_summary()
        assert "GHY" in r["key_result"] or "boundary" in r["key_result"].lower()

    def test_verdict_dict_present(self):
        r = pillar406_summary()
        assert "verdict_dict" in r
        assert r["verdict_dict"]["new_status"] == "CLOSED"

    def test_constraints_list_complete(self):
        r = pillar406_summary()
        for c in ["C1", "C2", "C3", "C4", "C5", "GHY", "BRANE"]:
            assert c in r["constraints_satisfied"]
