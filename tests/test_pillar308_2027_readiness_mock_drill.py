# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 308 — 2027 Data Readiness Mock-Drill Audit v2."""
import pytest
from src.core.pillar308_2027_readiness_mock_drill import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    READINESS_STATUS,
    DESI_WA_CONSISTENT_THRESHOLD,
    DESI_WA_TENSION_HIGH,
    DESI_WA_FALSIFICATION_SIGMA,
    DESI_DR2_WA_CENTRAL,
    DESI_DR2_TENSION_SIGMA,
    JUNO_DM31_UM_PREDICTION_EV2,
    JUNO_DM31_PDG_EV2,
    JUNO_PRECISION_TARGET,
    JUNO_TENSION_SIGMA,
    SO_R_UM_PREDICTION,
    SO_R_CONSISTENT_MIN,
    SO_R_FALSIFICATION_MAX,
    route_desi_dr3,
    route_juno_dr1,
    route_so_dr1,
    run_full_drill,
    idempotence_check,
    same_day_update_chain,
    readiness_audit_v2027,
    pillar308_report,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 308

def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

def test_pillar_title_mentions_2027():
    assert "2027" in PILLAR_TITLE

def test_readiness_status():
    assert "DRILL_VERIFIED_READY" in READINESS_STATUS


# ── Constants ──────────────────────────────────────────────────────────────────

def test_desi_wa_consistent_threshold():
    assert DESI_WA_CONSISTENT_THRESHOLD == pytest.approx(0.15, rel=0.01)

def test_desi_dr2_tension():
    assert abs(DESI_DR2_TENSION_SIGMA - 2.75) < 0.1

def test_juno_pdg_ev2():
    assert abs(JUNO_DM31_PDG_EV2 - 2.453e-3) < 1e-6

def test_juno_um_prediction_near_pdg():
    residual = abs(JUNO_DM31_UM_PREDICTION_EV2 - JUNO_DM31_PDG_EV2) / JUNO_DM31_PDG_EV2
    assert residual < 0.001  # < 0.1% from PDG

def test_so_r_um_prediction():
    assert abs(SO_R_UM_PREDICTION - 0.0315) < 0.001

def test_threshold_ordering_so():
    assert SO_R_FALSIFICATION_MAX < SO_R_CONSISTENT_MIN


# ── separation_guard ──────────────────────────────────────────────────────────

def test_separation_guard_returns_dict():
    sg = separation_guard()
    assert isinstance(sg, dict)

def test_separation_guard_no_hardgate():
    sg = separation_guard()
    assert sg["hardgate_impact"] == "NONE"


# ── route_desi_dr3 ────────────────────────────────────────────────────────────

def test_desi_dr3_consistent():
    res = route_desi_dr3(wa_measured=-0.05, wa_sigma=0.10)
    assert res["verdict"] == "CONSISTENT"

def test_desi_dr3_high_tension():
    res = route_desi_dr3(wa_measured=-0.25, wa_sigma=0.12)
    assert res["verdict"] == "HIGH_TENSION"

def test_desi_dr3_falsified():
    res = route_desi_dr3(wa_measured=-0.55, wa_sigma=0.10, joint_sigma=3.5)
    assert res["verdict"] == "FALSIFIED"

def test_desi_dr3_experiment_name():
    res = route_desi_dr3(-0.05, 0.10)
    assert res["experiment"] == "DESI_DR3"

def test_desi_dr3_action_present():
    res = route_desi_dr3(-0.05, 0.10)
    assert "action" in res and len(res["action"]) > 0

def test_desi_dr3_consistent_has_observation_tracker_action():
    res = route_desi_dr3(-0.05, 0.10)
    assert "CONSISTENT" in res["verdict"]
    assert "OBSERVATION_TRACKER" in res["action"] or "CONSISTENT" in res["action"]

def test_desi_dr3_falsified_has_retraction_action():
    res = route_desi_dr3(-0.55, 0.10, joint_sigma=3.5)
    assert "retraction" in res["action"].lower() or "FALSIFIED" in res["action"]

def test_desi_dr3_joint_sigma_included_when_provided():
    res = route_desi_dr3(-0.25, 0.12, joint_sigma=2.8)
    assert "joint_significance_sigma" in res
    assert res["joint_significance_sigma"] == pytest.approx(2.8, rel=0.01)

def test_desi_dr3_um_prediction_zero():
    res = route_desi_dr3(-0.05, 0.10)
    assert res["um_prediction"] == pytest.approx(0.0)

def test_desi_dr3_significance_positive():
    res = route_desi_dr3(-0.25, 0.12)
    assert res["significance_sigma"] > 0


# ── route_juno_dr1 ────────────────────────────────────────────────────────────

def test_juno_consistent():
    dm31_consistent = JUNO_DM31_UM_PREDICTION_EV2 * 0.9999
    sigma_precise = JUNO_DM31_UM_PREDICTION_EV2 * 0.003
    res = route_juno_dr1(dm31_consistent, sigma_precise)
    assert res["verdict"] == "CONSISTENT"

def test_juno_below_precision():
    sigma_poor = JUNO_DM31_PDG_EV2 * 0.015  # > 0.5% precision
    res = route_juno_dr1(JUNO_DM31_PDG_EV2, sigma_poor)
    assert res["verdict"] == "BELOW_PRECISION_TARGET"

def test_juno_tension():
    dm31_tension = JUNO_DM31_PDG_EV2 * 1.018  # 1.8% away
    sigma_tight = JUNO_DM31_PDG_EV2 * 0.004
    res = route_juno_dr1(dm31_tension, sigma_tight)
    assert res["verdict"] in ("TENSION", "FALSIFIED")

def test_juno_falsified():
    dm31_far = JUNO_DM31_PDG_EV2 * 1.035  # 3.5% away
    sigma_tight = JUNO_DM31_PDG_EV2 * 0.003
    res = route_juno_dr1(dm31_far, sigma_tight)
    assert res["verdict"] == "FALSIFIED"

def test_juno_experiment_name():
    res = route_juno_dr1(JUNO_DM31_PDG_EV2, JUNO_DM31_PDG_EV2 * 0.003)
    assert res["experiment"] == "JUNO_DR1"

def test_juno_residual_fraction_nonneg():
    res = route_juno_dr1(JUNO_DM31_PDG_EV2, JUNO_DM31_PDG_EV2 * 0.003)
    assert res["residual_fraction"] >= 0

def test_juno_action_present():
    res = route_juno_dr1(JUNO_DM31_PDG_EV2, JUNO_DM31_PDG_EV2 * 0.003)
    assert "action" in res


# ── route_so_dr1 ──────────────────────────────────────────────────────────────

def test_so_consistent_measurement():
    res = route_so_dr1(r_measured=0.032, r_sigma=0.006)
    assert res["verdict"] == "CONSISTENT"

def test_so_tension_maintained():
    res = route_so_dr1(r_measured=0.015, r_sigma=0.005)
    assert res["verdict"] == "TENSION_MAINTAINED"

def test_so_falsified():
    res = route_so_dr1(r_measured=0.008, r_sigma=0.002)
    assert res["verdict"] == "FALSIFIED"

def test_so_upper_limit_consistent():
    res = route_so_dr1(r_measured=0.025, r_sigma=0.0, is_upper_limit=True)
    assert res["verdict"] == "UPPER_LIMIT_CONSISTENT"

def test_so_upper_limit_tension():
    res = route_so_dr1(r_measured=0.015, r_sigma=0.0, is_upper_limit=True)
    assert res["verdict"] == "UPPER_LIMIT_TENSION"

def test_so_experiment_name():
    res = route_so_dr1(0.032, 0.006)
    assert "SIMONS_OBSERVATORY" in res["experiment"]

def test_so_um_prediction():
    res = route_so_dr1(0.032, 0.006)
    assert abs(res["um_prediction"] - 0.0315) < 0.001

def test_so_action_present():
    res = route_so_dr1(0.032, 0.006)
    assert "action" in res

def test_so_falsified_has_retraction():
    res = route_so_dr1(r_measured=0.008, r_sigma=0.002)
    assert "retraction" in res["action"].lower() or "FALSIFIED" in res["action"]


# ── run_full_drill ────────────────────────────────────────────────────────────

def test_run_full_drill_returns_dict():
    drill = run_full_drill()
    assert isinstance(drill, dict)

def test_run_full_drill_has_all_experiments():
    drill = run_full_drill()
    assert "desi_dr3_scenarios" in drill
    assert "juno_dr1_scenarios" in drill
    assert "so_dr1_scenarios" in drill
    assert "combined_scenarios" in drill

def test_run_full_drill_desi_scenario_count():
    drill = run_full_drill()
    assert len(drill["desi_dr3_scenarios"]) == 3

def test_run_full_drill_juno_scenario_count():
    drill = run_full_drill()
    assert len(drill["juno_dr1_scenarios"]) == 4

def test_run_full_drill_so_scenario_count():
    drill = run_full_drill()
    assert len(drill["so_dr1_scenarios"]) == 3

def test_run_full_drill_combined_scenario_count():
    drill = run_full_drill()
    assert len(drill["combined_scenarios"]) == 3

def test_run_full_drill_total_count():
    drill = run_full_drill()
    assert drill["summary"]["total_scenarios"] >= 13

def test_run_full_drill_framework_standing():
    drill = run_full_drill()
    assert drill["summary"]["framework_status_current"] == "STANDING"

def test_run_full_drill_desi_consistent_scenario():
    drill = run_full_drill()
    consistent = next(
        s for s in drill["desi_dr3_scenarios"]
        if s["scenario_label"] == "DESI_CONSISTENT"
    )
    assert consistent["verdict"] == "CONSISTENT"

def test_run_full_drill_best_case_not_falsified():
    drill = run_full_drill()
    best = next(s for s in drill["combined_scenarios"] if s["scenario_label"] == "BEST_CASE")
    assert not best["any_falsified"]
    assert best["framework_status"] == "STANDING"

def test_run_full_drill_worst_case_falsified():
    drill = run_full_drill()
    worst = next(s for s in drill["combined_scenarios"] if s["scenario_label"] == "WORST_CASE")
    assert worst["any_falsified"]
    assert worst["framework_status"] == "RETRACTION_REQUIRED"


# ── idempotence_check ─────────────────────────────────────────────────────────

def test_idempotence_check_passes():
    result = idempotence_check()
    assert result["all_idempotent"] is True
    assert result["verdict"] == "PASS"

def test_idempotence_desi():
    result = idempotence_check()
    assert result["desi_idempotent"] is True

def test_idempotence_juno():
    result = idempotence_check()
    assert result["juno_idempotent"] is True

def test_idempotence_so():
    result = idempotence_check()
    assert result["so_idempotent"] is True


# ── same_day_update_chain ─────────────────────────────────────────────────────

def test_update_chain_returns_dict():
    chain = same_day_update_chain()
    assert isinstance(chain, dict)

def test_update_chain_has_three_experiments():
    chain = same_day_update_chain()
    assert "DESI_DR3" in chain
    assert "JUNO_DR1" in chain
    assert "SIMONS_OBSERVATORY_DR1" in chain

def test_update_chain_desi_has_observation_tracker():
    chain = same_day_update_chain()
    surfaces = chain["DESI_DR3"]["surfaces_to_update"]
    assert any("OBSERVATION_TRACKER" in s for s in surfaces)

def test_update_chain_juno_has_claim_board():
    chain = same_day_update_chain()
    surfaces = chain["JUNO_DR1"]["surfaces_to_update"]
    assert any("CLAIM_MASTER_BOARD" in s for s in surfaces)

def test_update_chain_so_has_status():
    chain = same_day_update_chain()
    surfaces = chain["SIMONS_OBSERVATORY_DR1"]["surfaces_to_update"]
    assert any("STATUS.md" in s for s in surfaces)

def test_update_chain_executables_present():
    chain = same_day_update_chain()
    for exp in chain.values():
        assert "executable" in exp
        assert exp["executable"].endswith(".py")


# ── readiness_audit_v2027 ─────────────────────────────────────────────────────

def test_readiness_audit_returns_dict():
    audit = readiness_audit_v2027()
    assert isinstance(audit, dict)

def test_readiness_audit_status():
    audit = readiness_audit_v2027()
    assert "DRILL_VERIFIED_READY" in audit["readiness_status"]

def test_readiness_audit_provenance_receipt():
    audit = readiness_audit_v2027()
    prov = audit["provenance_receipt"]
    assert prov["all_13_scenarios_passed"] is True
    assert prov["all_routing_idempotent"] is True
    assert prov["update_chains_documented"] is True

def test_readiness_audit_framework_standing():
    audit = readiness_audit_v2027()
    assert audit["provenance_receipt"]["framework_currently_standing"] == "STANDING"

def test_readiness_audit_three_experiments():
    audit = readiness_audit_v2027()
    assert len(audit["experiments_covered"]) == 3

def test_readiness_audit_version():
    audit = readiness_audit_v2027()
    assert "v11.12" in audit["audit_version"]


# ── pillar308_report ──────────────────────────────────────────────────────────

def test_pillar308_report_returns_dict():
    rpt = pillar308_report()
    assert isinstance(rpt, dict)

def test_pillar308_report_pillar_number():
    rpt = pillar308_report()
    assert rpt["pillar"] == 308

def test_pillar308_report_readiness_status():
    rpt = pillar308_report()
    assert "DRILL_VERIFIED_READY" in rpt["readiness_status"]

def test_pillar308_report_scenario_count():
    rpt = pillar308_report()
    assert rpt["scenario_count"] >= 13

def test_pillar308_report_framework_standing():
    rpt = pillar308_report()
    assert rpt["framework_status"] == "STANDING"

def test_pillar308_report_what_it_does_nonempty():
    rpt = pillar308_report()
    assert len(rpt["what_this_pillar_does"]) >= 4

def test_pillar308_report_separation_guard():
    rpt = pillar308_report()
    assert "separation_guard" in rpt
    assert rpt["separation_guard"]["hardgate_impact"] == "NONE"
