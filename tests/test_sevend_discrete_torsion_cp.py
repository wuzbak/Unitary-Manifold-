# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for 7D Rung 2: src/sevend/discrete_torsion_cp.py"""

from __future__ import annotations

import math
import pytest

from src.sevend.discrete_torsion_cp import (
    RUNG_ID, DIMENSION,
    N_FP, TORSION_ORDER,
    PHI_HOLONOMY_RAD,
    DELTA_CP_GEO_RAD,
    DELTA_CP_PDG_RAD,
    RESIDUAL_RAW, RESIDUAL_PHYSICAL,
    RESIDUAL_TOLERANCE,
    KILL_SWITCH_PASS, STATUS, EPISTEMIC_STATUS,
    torsion_group,
    fixed_point_holonomies,
    aharonov_bohm_phase,
    unitarity_triangle_cp_angle,
    raw_holonomy_cp_angle,
    kill_switch_check,
    discrete_torsion_summary,
    rung2_gate_evidence,
    scaffold_spec,
    evaluate_candidate,
)


class TestConstants:
    def test_rung_id(self):
        assert RUNG_ID == "R2"

    def test_dimension(self):
        assert DIMENSION == "7D"

    def test_n_fp(self):
        assert N_FP == 3

    def test_torsion_order(self):
        assert TORSION_ORDER == 3

    def test_phi_holonomy_rad(self):
        assert PHI_HOLONOMY_RAD == pytest.approx(2.0 * math.pi / 3.0)

    def test_delta_cp_geo_is_pi_minus_phi(self):
        assert DELTA_CP_GEO_RAD == pytest.approx(math.pi - PHI_HOLONOMY_RAD)

    def test_delta_cp_geo_value(self):
        # π/3 ≈ 1.0472
        assert DELTA_CP_GEO_RAD == pytest.approx(math.pi / 3.0, rel=1e-6)

    def test_delta_cp_pdg_near_1p2(self):
        assert 1.0 < DELTA_CP_PDG_RAD < 1.5

    def test_residual_physical_lt_tolerance(self):
        # 12.7% < 40%
        assert RESIDUAL_PHYSICAL < RESIDUAL_TOLERANCE

    def test_residual_raw_gt_tolerance(self):
        # 74% > 40%
        assert RESIDUAL_RAW > RESIDUAL_TOLERANCE

    def test_kill_switch_pass(self):
        assert KILL_SWITCH_PASS is True

    def test_status_solid(self):
        assert STATUS == "RUNG_SOLID"

    def test_epistemic_status_nonempty(self):
        assert len(EPISTEMIC_STATUS) > 10


class TestTorsionGroup:
    def test_returns_dict(self):
        assert isinstance(torsion_group(), dict)

    def test_z3_group(self):
        r = torsion_group()
        assert r["group"] == "Z_3"

    def test_order_3(self):
        r = torsion_group()
        assert r["order"] == 3

    def test_generator_phase(self):
        r = torsion_group()
        assert r["generator_phase_rad"] == pytest.approx(2.0 * math.pi / 3.0)

    def test_three_classes(self):
        r = torsion_group()
        assert len(r["classes"]) == 3

    def test_first_class_trivial(self):
        r = torsion_group()
        assert r["classes"][0]["phase_rad"] == pytest.approx(0.0)

    def test_cohomology_string(self):
        r = torsion_group()
        assert "Z_3" in r["cohomology"]

    def test_n2_group(self):
        r = torsion_group(n=2)
        assert r["order"] == 2
        assert len(r["classes"]) == 2

    def test_raises_for_n_lt_2(self):
        with pytest.raises(ValueError):
            torsion_group(n=1)


class TestFixedPointHolonomies:
    def test_returns_list(self):
        fps = fixed_point_holonomies()
        assert isinstance(fps, list)

    def test_three_points(self):
        fps = fixed_point_holonomies()
        assert len(fps) == 3

    def test_z0_trivial_holonomy(self):
        fps = fixed_point_holonomies()
        assert fps[0]["holonomy_phase_rad"] == pytest.approx(0.0)

    def test_z1_phase(self):
        fps = fixed_point_holonomies()
        assert fps[1]["holonomy_phase_rad"] == pytest.approx(2.0 * math.pi / 3.0)

    def test_z2_phase(self):
        fps = fixed_point_holonomies()
        assert fps[2]["holonomy_phase_rad"] == pytest.approx(4.0 * math.pi / 3.0)

    def test_indices_sequential(self):
        fps = fixed_point_holonomies()
        for i, fp in enumerate(fps):
            assert fp["index"] == i

    def test_raises_for_n_lt_2(self):
        with pytest.raises(ValueError):
            fixed_point_holonomies(n=1)


class TestAharonovBohmPhase:
    def test_returns_dict(self):
        assert isinstance(aharonov_bohm_phase(), dict)

    def test_trivial_class_zero(self):
        r = aharonov_bohm_phase(torsion_class=0)
        assert r["phi_ab_rad"] == pytest.approx(0.0)

    def test_class_1_is_2pi_over_3(self):
        r = aharonov_bohm_phase(torsion_class=1)
        assert r["phi_ab_rad"] == pytest.approx(2.0 * math.pi / 3.0)

    def test_class_2_is_4pi_over_3(self):
        r = aharonov_bohm_phase(torsion_class=2)
        assert r["phi_ab_rad"] == pytest.approx(4.0 * math.pi / 3.0)

    def test_raises_for_invalid_class(self):
        with pytest.raises(ValueError):
            aharonov_bohm_phase(torsion_class=3, n=3)


class TestUnitarityTriangleCpAngle:
    def test_returns_dict(self):
        assert isinstance(unitarity_triangle_cp_angle(), dict)

    def test_gamma_geo_is_pi_third(self):
        r = unitarity_triangle_cp_angle()
        assert r["gamma_geo_rad"] == pytest.approx(math.pi / 3.0, rel=1e-6)

    def test_gamma_geo_deg_is_60(self):
        r = unitarity_triangle_cp_angle()
        assert r["gamma_geo_deg"] == pytest.approx(60.0, rel=1e-4)

    def test_pct_err_lt_40(self):
        r = unitarity_triangle_cp_angle()
        assert r["pct_err"] < 40.0

    def test_pct_err_lt_20(self):
        # Should be ~12.7%
        r = unitarity_triangle_cp_angle()
        assert r["pct_err"] < 20.0

    def test_pdg_in_result(self):
        r = unitarity_triangle_cp_angle()
        assert r["delta_cp_pdg_rad"] == pytest.approx(DELTA_CP_PDG_RAD)


class TestRawHolonomyCpAngle:
    def test_returns_dict(self):
        assert isinstance(raw_holonomy_cp_angle(), dict)

    def test_raw_phi(self):
        r = raw_holonomy_cp_angle()
        assert r["phi_raw_rad"] == pytest.approx(2.0 * math.pi / 3.0)

    def test_raw_pct_err_gt_40(self):
        r = raw_holonomy_cp_angle()
        assert r["pct_err"] > 40.0

    def test_raw_kill_switch_fails(self):
        r = raw_holonomy_cp_angle()
        assert r["kill_switch_pass"] is False


class TestKillSwitchCheck:
    def test_returns_dict(self):
        assert isinstance(kill_switch_check(), dict)

    def test_overall_pass(self):
        r = kill_switch_check()
        assert r["kill_switch_pass"] is True

    def test_four_checks(self):
        r = kill_switch_check()
        assert len(r["checks"]) == 4

    def test_all_individual_checks_pass(self):
        r = kill_switch_check()
        for ks in r["checks"]:
            assert ks["result"] is True

    def test_residual_lt_tolerance(self):
        r = kill_switch_check()
        assert r["residual_physical"] < r["residual_tolerance"]

    def test_ks3_residual(self):
        r = kill_switch_check()
        ks3 = next(x for x in r["checks"] if x["name"] == "cp_phase_numeric_residual_check")
        assert ks3["residual_pct"] < 40.0


class TestDiscreteTorsionSummary:
    def test_returns_dict(self):
        assert isinstance(discrete_torsion_summary(), dict)

    def test_rung_id(self):
        r = discrete_torsion_summary()
        assert r["rung_id"] == "R2"

    def test_transition_label(self):
        r = discrete_torsion_summary()
        assert "6D" in r["transition"] and "7D" in r["transition"]

    def test_status_solid(self):
        r = discrete_torsion_summary()
        assert r["status"] == "RUNG_SOLID"

    def test_canonical_result_present(self):
        r = discrete_torsion_summary()
        cr = r["canonical_result"]
        assert cr["delta_cp_geo_rad"] == pytest.approx(math.pi / 3.0, rel=1e-6)

    def test_next_rung_mentioned(self):
        r = discrete_torsion_summary()
        assert "8D" in r["next_rung"]


class TestRung2GateEvidence:
    def test_returns_dict(self):
        assert isinstance(rung2_gate_evidence(), dict)

    def test_kill_switch_pass(self):
        r = rung2_gate_evidence()
        assert r["kill_switch_pass"] is True

    def test_gate_passed(self):
        r = rung2_gate_evidence()
        assert r["gate_passed"] is True

    def test_axiomzero_compliant(self):
        r = rung2_gate_evidence()
        assert r["axiomzero_compliant"] is True

    def test_residual_lt_tolerance(self):
        r = rung2_gate_evidence()
        assert r["residual_pct"] < r["kill_switch_tolerance_pct"]

    def test_anchor_burned(self):
        r = rung2_gate_evidence()
        assert r["anchor_burned"] == "delta_CP"

    def test_prediction_contains_pi_third(self):
        r = rung2_gate_evidence()
        assert "π/3" in r["prediction"] or "60" in r["prediction"]


class TestScaffoldSpecLegacy:
    def test_returns_dict(self):
        assert isinstance(scaffold_spec(), dict)

    def test_rung_id(self):
        r = scaffold_spec()
        assert r["rung_id"] == "R2"

    def test_now_implemented(self):
        r = scaffold_spec()
        assert r["now_implemented"] is True


class TestEvaluateCandidateLegacy:
    def test_returns_dict(self):
        evidence = {
            "traceability_pass": True,
            "reproducibility_pass": True,
            "tests_pass": True,
            "epistemic_integrity_pass": True,
            "axiomzero_pass": True,
            "residual": 0.127,
        }
        r = evaluate_candidate(evidence)
        assert isinstance(r, dict)

    def test_gate_pass_for_good_evidence(self):
        evidence = {
            "traceability_pass": True,
            "reproducibility_pass": True,
            "tests_pass": True,
            "epistemic_integrity_pass": True,
            "axiomzero_pass": True,
            "residual": 0.127,
        }
        r = evaluate_candidate(evidence)
        assert r["gate_pass"] is True

    def test_gate_fail_for_bad_residual(self):
        evidence = {
            "traceability_pass": True,
            "reproducibility_pass": True,
            "tests_pass": True,
            "epistemic_integrity_pass": True,
            "axiomzero_pass": True,
            "residual": 0.75,
        }
        r = evaluate_candidate(evidence)
        assert r["gate_pass"] is False

    def test_has_internal_evidence(self):
        r = evaluate_candidate({})
        assert "internal_evidence" in r
