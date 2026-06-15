# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for Pillar 396 — ACT r-Tension Formal Architecture Limit Certificate.

Verifies the WZW loop-correction analysis, preregistered routing, closure
conditions, and the machine-readable pillar status interface.
"""

import math
import pytest

from src.core.pillar396_act_r_tension_architecture_limit import (
    N_W, N_SHADOW, K_CS, RHO_WZW,
    R_BARE, R_BRAIDED, R_ACT_UPPER, PERTURBATIVITY_N_LOOPS,
    SODR1_ROUTING, ACTDR6_STATUS,
    TensionRouting, ClosureCondition,
    wzw_loop_correction_factor,
    cumulative_wzw_correction,
    required_fractional_correction,
    n_loops_to_reach_target,
    architecture_limit_proof,
    act_r_tension_routing,
    closure_conditions_report,
    act_r_architecture_limit_certificate,
    pillar_396_status,
)


# ──────────────────────────────────────────────────────────────────────────────
# Physical constants
# ──────────────────────────────────────────────────────────────────────────────

class TestPhysicalConstants:

    def test_nw_is_5(self):
        assert N_W == 5

    def test_nshadow_is_7(self):
        assert N_SHADOW == 7

    def test_kcs_is_74(self):
        assert K_CS == 74

    def test_rho_wzw_formula(self):
        expected = 2 * 5 * 7 / 74
        assert abs(RHO_WZW - expected) < 1e-12

    def test_rho_wzw_value(self):
        assert abs(RHO_WZW - 70/74) < 1e-12

    def test_rho_wzw_below_one(self):
        assert 0 < RHO_WZW < 1

    def test_r_braided_value(self):
        assert abs(R_BRAIDED - 0.0315) < 1e-6

    def test_r_act_upper_value(self):
        assert abs(R_ACT_UPPER - 0.016) < 1e-6

    def test_r_braided_above_act_upper(self):
        assert R_BRAIDED > R_ACT_UPPER, "UM prediction must exceed ACT DR6 bound for tension to exist"

    def test_perturbativity_limit_positive(self):
        assert PERTURBATIVITY_N_LOOPS > 0


# ──────────────────────────────────────────────────────────────────────────────
# WZW loop correction
# ──────────────────────────────────────────────────────────────────────────────

class TestWZWLoopCorrection:

    def test_correction_factor_zero_loops(self):
        assert wzw_loop_correction_factor(0) == 0.0

    def test_correction_factor_one_loop_positive(self):
        f1 = wzw_loop_correction_factor(1)
        assert f1 > 0

    def test_correction_factor_decreases_with_n(self):
        f1 = wzw_loop_correction_factor(1)
        f2 = wzw_loop_correction_factor(2)
        f3 = wzw_loop_correction_factor(3)
        assert f2 < f1, "Higher loop orders should have smaller individual contributions"
        assert f3 < f2

    def test_correction_factor_exponential_decay(self):
        loop_factor = (RHO_WZW / (4 * math.pi)) ** 2
        for n in range(1, 5):
            expected = loop_factor ** n
            computed = wzw_loop_correction_factor(n)
            assert abs(computed - expected) < 1e-15

    def test_correction_factor_at_n1_explicit(self):
        expected = (RHO_WZW / (4 * math.pi)) ** 2
        assert abs(wzw_loop_correction_factor(1) - expected) < 1e-15

    def test_cumulative_correction_positive(self):
        assert cumulative_wzw_correction(10) > 0

    def test_cumulative_correction_monotone(self):
        # Use small N values where the series has not yet converged to machine precision.
        c1 = cumulative_wzw_correction(1)
        c3 = cumulative_wzw_correction(3)
        c5 = cumulative_wzw_correction(5)
        assert c3 > c1
        assert c5 > c3

    def test_cumulative_correction_converges(self):
        # The geometric series sum converges since (ρ/4π)^2 < 1.
        c_large = cumulative_wzw_correction(1000)
        c_larger = cumulative_wzw_correction(2000)
        # Should be very close to the same value (within 1e-20).
        assert abs(c_large - c_larger) < 1e-15

    def test_cumulative_correction_at_perturbativity_limit_small(self):
        # The total correction at the perturbativity limit should be tiny
        # — confirming that perturbativity never accumulates to 49%.
        c = cumulative_wzw_correction(PERTURBATIVITY_N_LOOPS)
        assert c < 0.49, (
            "If cumulative WZW correction reaches 49% before perturbativity "
            "breaks, the architecture limit proof is invalidated."
        )

    def test_required_fractional_correction_value(self):
        frac = required_fractional_correction(R_BRAIDED, R_ACT_UPPER)
        # (0.0315 - 0.016) / 0.0315 ≈ 0.492
        assert abs(frac - (R_BRAIDED - R_ACT_UPPER) / R_BRAIDED) < 1e-12
        assert 0.45 < frac < 0.55

    def test_required_fractional_correction_positive(self):
        assert required_fractional_correction(R_BRAIDED, R_ACT_UPPER) > 0

    def test_n_loops_to_target_perturbativity_broken(self):
        n, broken = n_loops_to_reach_target(R_BRAIDED, R_ACT_UPPER, RHO_WZW, PERTURBATIVITY_N_LOOPS)
        # The architecture-limit proof requires that the target is reached only
        # after perturbativity breaks.
        assert broken is True, (
            "The architecture limit proof requires that reaching r<0.016 via "
            "WZW loops requires breaking perturbativity."
        )

    def test_n_loops_to_target_returns_tuple(self):
        result = n_loops_to_reach_target()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_n_loops_none_if_never_reached(self):
        # With very small rho (e.g. 0.01), the target may never be reached.
        n, broken = n_loops_to_reach_target(rho=0.001)
        # Either n is None or broken is True.
        assert broken is True or n is None


# ──────────────────────────────────────────────────────────────────────────────
# Architecture limit proof certificate
# ──────────────────────────────────────────────────────────────────────────────

class TestArchitectureLimitProof:

    def test_proof_returns_dict(self):
        proof = architecture_limit_proof()
        assert isinstance(proof, dict)

    def test_proof_certificate_label(self):
        proof = architecture_limit_proof()
        assert "PILLAR_396" in proof["certificate"]

    def test_proof_architecture_limit_certified(self):
        proof = architecture_limit_proof()
        assert proof["architecture_limit_certified"] is True, (
            "Architecture limit must be certified: WZW loops cannot reach r<0.016 "
            "before perturbativity breaks."
        )

    def test_proof_routing_is_architecture_limit(self):
        proof = architecture_limit_proof()
        assert proof["routing"] == "ARCHITECTURE_LIMIT_CERTIFIED"

    def test_proof_rho_matches_constant(self):
        proof = architecture_limit_proof()
        assert abs(proof["rho_wzw"] - RHO_WZW) < 1e-12

    def test_proof_r_predicted_matches(self):
        proof = architecture_limit_proof()
        assert abs(proof["r_predicted"] - R_BRAIDED) < 1e-10

    def test_proof_r_act_upper_matches(self):
        proof = architecture_limit_proof()
        assert abs(proof["r_act_upper_95cl"] - R_ACT_UPPER) < 1e-10

    def test_proof_required_correction_about_49pct(self):
        proof = architecture_limit_proof()
        frac = proof["required_fractional_correction"]
        assert 0.40 < frac < 0.60, f"Required fractional correction should be ~49%, got {frac}"

    def test_proof_perturbativity_broken(self):
        proof = architecture_limit_proof()
        assert proof["perturbativity_broken_at_target"] is True

    def test_proof_cumulative_at_limit_small(self):
        proof = architecture_limit_proof()
        # The cumulative WZW correction at the perturbativity limit must be < 49%.
        c = proof["cumulative_correction_at_perturbativity_limit"]
        assert c < 0.49, (
            f"Cumulative correction at perturbativity limit = {c:.4f} is "
            f">= 49% — architecture limit proof would be invalid."
        )

    def test_proof_statement_present(self):
        proof = architecture_limit_proof()
        assert "proof_statement" in proof
        assert len(proof["proof_statement"]) > 100

    def test_proof_statement_mentions_perturbativity(self):
        proof = architecture_limit_proof()
        assert "perturbat" in proof["proof_statement"].lower()

    def test_proof_rho_formula_correct(self):
        proof = architecture_limit_proof()
        assert "70/74" in proof["rho_formula"] or "70" in proof["rho_formula"]

    def test_proof_version(self):
        proof = architecture_limit_proof()
        assert "12.9" in proof["version"]


# ──────────────────────────────────────────────────────────────────────────────
# Preregistered routing
# ──────────────────────────────────────────────────────────────────────────────

class TestPreregisteredRouting:

    def test_sodr1_routing_constant_fields(self):
        assert SODR1_ROUTING.experiment == "Simons Observatory DR1"
        assert SODR1_ROUTING.expected_year == 2027
        assert abs(SODR1_ROUTING.predicted_r - R_BRAIDED) < 1e-10

    def test_sodr1_routing_if_consistent(self):
        assert SODR1_ROUTING.routing_if_consistent == TensionRouting.CONSISTENT

    def test_sodr1_routing_if_falsified(self):
        assert SODR1_ROUTING.routing_if_falsified == TensionRouting.ARCHITECTURE_FALSIFIED

    def test_act_r_tension_routing_no_measurement(self):
        result = act_r_tension_routing()
        assert result["status"] == "HIGH_TENSION"
        assert result["routing"] == TensionRouting.HIGH_TENSION.value
        assert result["falsified"] == "False"

    def test_act_r_tension_routing_consistent_measurement(self):
        # If SO DR1 measures r = 0.032 (consistent with UM)
        result = act_r_tension_routing(measured_r=0.032, measured_sigma=1.0)
        assert result["falsified"] == "False"
        assert result["routing"] != TensionRouting.ARCHITECTURE_FALSIFIED.value

    def test_act_r_tension_routing_falsified_measurement(self):
        # If SO DR1 confirms r = 0.010 at 3.5σ → FALSIFIED
        result = act_r_tension_routing(measured_r=0.010, measured_sigma=3.5)
        assert result["routing"] == TensionRouting.ARCHITECTURE_FALSIFIED.value
        assert result["falsified"] == "True"

    def test_act_r_tension_routing_high_tension_case(self):
        # r below prediction but not at falsification threshold
        result = act_r_tension_routing(measured_r=0.020, measured_sigma=2.0)
        assert result["falsified"] == "False"

    def test_closure_conditions_count(self):
        conditions = closure_conditions_report()
        assert len(conditions) == 3

    def test_closure_conditions_have_condition_field(self):
        for c in closure_conditions_report():
            assert "condition" in c
            assert "description" in c
            assert "status" in c

    def test_so_dr1_closure_condition_present(self):
        conditions = closure_conditions_report()
        cond_names = [c["condition"] for c in conditions]
        assert ClosureCondition.SO_DR1_CONSISTENT.value in cond_names

    def test_act_revision_closure_condition_present(self):
        conditions = closure_conditions_report()
        cond_names = [c["condition"] for c in conditions]
        assert ClosureCondition.ACT_REVISION_UPWARD.value in cond_names

    def test_new_cs_mechanism_closure_condition_present(self):
        conditions = closure_conditions_report()
        cond_names = [c["condition"] for c in conditions]
        assert ClosureCondition.NEW_CS_MECHANISM.value in cond_names


# ──────────────────────────────────────────────────────────────────────────────
# Full certificate
# ──────────────────────────────────────────────────────────────────────────────

class TestFullCertificate:

    def test_certificate_structure(self):
        cert = act_r_architecture_limit_certificate()
        required_keys = [
            "pillar", "title", "version", "reference_pillar_303",
            "certificate_status", "proof", "current_routing",
            "so_dr1_preregistered_routing", "closure_conditions",
            "falsification_statement",
        ]
        for key in required_keys:
            assert key in cert, f"Missing '{key}' in certificate"

    def test_certificate_pillar_number(self):
        cert = act_r_architecture_limit_certificate()
        assert cert["pillar"] == 396

    def test_certificate_status_certified(self):
        cert = act_r_architecture_limit_certificate()
        assert cert["certificate_status"] == "ARCHITECTURE_LIMIT_CERTIFIED"

    def test_certificate_mentions_pillar_303(self):
        cert = act_r_architecture_limit_certificate()
        assert "303" in cert["reference_pillar_303"]

    def test_certificate_so_routing_year(self):
        cert = act_r_architecture_limit_certificate()
        assert cert["so_dr1_preregistered_routing"]["year"] == 2027

    def test_certificate_falsification_if_3sigma(self):
        cert = act_r_architecture_limit_certificate()
        routing = cert["so_dr1_preregistered_routing"]
        assert routing["if_r_lt_threshold_at_3sigma"] == TensionRouting.ARCHITECTURE_FALSIFIED.value

    def test_certificate_falsification_statement_nonempty(self):
        cert = act_r_architecture_limit_certificate()
        assert len(cert["falsification_statement"]) > 100

    def test_certificate_version(self):
        cert = act_r_architecture_limit_certificate()
        assert "12.9" in cert["version"]


# ──────────────────────────────────────────────────────────────────────────────
# Pillar status interface
# ──────────────────────────────────────────────────────────────────────────────

class TestPillarStatus:

    def test_status_returns_dict(self):
        assert isinstance(pillar_396_status(), dict)

    def test_status_pillar_field(self):
        assert pillar_396_status()["pillar"] == "396"

    def test_status_r_predicted(self):
        status = pillar_396_status()
        assert float(status["r_predicted"]) == pytest.approx(R_BRAIDED, abs=1e-6)

    def test_status_r_act_upper(self):
        status = pillar_396_status()
        assert float(status["r_act_upper"]) == pytest.approx(R_ACT_UPPER, abs=1e-6)

    def test_status_rho_wzw_close(self):
        status = pillar_396_status()
        assert abs(float(status["rho_wzw"]) - RHO_WZW) < 1e-5

    def test_status_falsification_condition_present(self):
        status = pillar_396_status()
        assert "3σ" in status["falsification_condition"] or "3sigma" in status["falsification_condition"].lower() or "FALSIFIED" in status["falsification_condition"]
