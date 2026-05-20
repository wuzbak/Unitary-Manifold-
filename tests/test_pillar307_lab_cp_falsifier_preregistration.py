# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 307 — Lab-Scale CP Falsifier Preregistration and Decision Routing."""
import math
import pytest
from src.core.pillar307_lab_cp_falsifier_preregistration import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N1_BRAID,
    N2_BRAID,
    K_CS,
    J_GEO_LAYER1,
    TOPOLOGY_TRANSFER_EFFICIENCY,
    A_CP_LAB_TARGET,
    A_CP_LAB_TARGET_WITH_DILUTION,
    A_CP_LAB_SIGMA_REQUIRED,
    CONSISTENT_THRESHOLD,
    FALSIFICATION_THRESHOLD,
    BELOW_SENSITIVITY_LOWER,
    PREREGISTRATION_STATUS,
    PREREGISTRATION_VERSION,
    separation_guard,
    compute_a_cp_lab_prediction,
    topology_transfer_estimate,
    route_lab_cp_result,
    decision_grade_checklist,
    preregistration_packet,
    pillar307_report,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 307

def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

def test_pillar_title_contains_cp():
    assert "CP" in PILLAR_TITLE or "Falsifier" in PILLAR_TITLE

def test_preregistration_status():
    assert "PREREGISTERED" in PREREGISTRATION_STATUS

def test_preregistration_version():
    assert "v11.12" in PREREGISTRATION_VERSION


# ── Constants ──────────────────────────────────────────────────────────────────

def test_braid_pair():
    assert N1_BRAID == 5
    assert N2_BRAID == 7

def test_k_cs():
    assert K_CS == 74
    assert K_CS == N1_BRAID ** 2 + N2_BRAID ** 2

def test_j_geo_layer1_order():
    assert 0.01 < J_GEO_LAYER1 < 0.05

def test_a_cp_lab_target_raw_order():
    # Raw (before orientation dilution): ~1.6e-3
    assert 5e-4 < A_CP_LAB_TARGET < 5e-3

def test_a_cp_lab_target_with_dilution_order():
    # After ×1/100 dilution: ~O(10⁻⁵)
    assert 1e-6 < A_CP_LAB_TARGET_WITH_DILUTION < 1e-4

def test_sigma_required():
    assert A_CP_LAB_SIGMA_REQUIRED == pytest.approx(1e-5, rel=0.01)

def test_consistent_threshold():
    assert CONSISTENT_THRESHOLD == pytest.approx(1e-5, rel=0.01)

def test_falsification_threshold():
    assert FALSIFICATION_THRESHOLD == pytest.approx(1e-6, rel=0.01)

def test_thresholds_ordered():
    assert FALSIFICATION_THRESHOLD <= BELOW_SENSITIVITY_LOWER <= CONSISTENT_THRESHOLD


# ── separation_guard ──────────────────────────────────────────────────────────

def test_separation_guard_returns_dict():
    sg = separation_guard()
    assert isinstance(sg, dict)

def test_separation_guard_no_hardgate():
    sg = separation_guard()
    assert sg["hardgate_impact"] == "NONE"
    assert sg["toe_score_impact"] == "NONE"


# ── compute_a_cp_lab_prediction ───────────────────────────────────────────────

def test_compute_a_cp_returns_dict():
    res = compute_a_cp_lab_prediction()
    assert isinstance(res, dict)

def test_compute_a_cp_canonical():
    res = compute_a_cp_lab_prediction()
    assert res["n1"] == 5
    assert res["n2"] == 7
    assert res["k_cs"] == 74

def test_compute_a_cp_j_geo_positive():
    res = compute_a_cp_lab_prediction()
    assert res["j_geo"] > 0

def test_compute_a_cp_target_positive():
    res = compute_a_cp_lab_prediction()
    assert res["a_cp_lab_target"] > 0

def test_compute_a_cp_target_order_1e5():
    res = compute_a_cp_lab_prediction()
    # Should be O(10⁻⁵) to O(10⁻⁴)
    assert 1e-6 < res["a_cp_lab_target"] < 1e-3

def test_compute_a_cp_theta_braid_range():
    res = compute_a_cp_lab_prediction()
    assert 30 < res["theta_braid_deg"] < 50

def test_compute_a_cp_dilution_reduces():
    res_100 = compute_a_cp_lab_prediction(orientation_suppression=100.0)
    res_10 = compute_a_cp_lab_prediction(orientation_suppression=10.0)
    assert res_100["a_cp_lab_target"] < res_10["a_cp_lab_target"]

def test_compute_a_cp_invalid_raises():
    with pytest.raises(ValueError):
        compute_a_cp_lab_prediction(n1=0, n2=7, k_cs=74)


# ── topology_transfer_estimate ────────────────────────────────────────────────

def test_topology_transfer_returns_dict():
    res = topology_transfer_estimate()
    assert isinstance(res, dict)

def test_topology_transfer_default_eta():
    res = topology_transfer_estimate()
    expected = N1_BRAID / K_CS
    assert abs(res["eta_t"] - expected) < 1e-5

def test_topology_transfer_exp_suppression():
    res0 = topology_transfer_estimate(l_over_xi_t=0.0)
    res1 = topology_transfer_estimate(l_over_xi_t=1.0)
    assert res1["eta_t"] < res0["eta_t"]

def test_topology_transfer_xi_ratio_scales():
    res1 = topology_transfer_estimate(xi_lab_over_xi_kk=1.0)
    res2 = topology_transfer_estimate(xi_lab_over_xi_kk=2.0)
    assert abs(res2["eta_t"] / res1["eta_t"] - 2.0) < 0.01


# ── route_lab_cp_result ───────────────────────────────────────────────────────

def test_route_no_topology_cert():
    res = route_lab_cp_result(1e-5, 1e-6, topology_certified=False)
    assert res["verdict"] == "INCONCLUSIVE"

def test_route_insufficient_sigma():
    # σ > 1e-5 → BELOW_MEASUREMENT_THRESHOLD
    res = route_lab_cp_result(5e-5, 5e-5, topology_certified=True)
    assert res["verdict"] == "BELOW_MEASUREMENT_THRESHOLD"

def test_route_consistent():
    # |A_CP| >= 1e-5 at 3σ, topology certified
    res = route_lab_cp_result(3e-5, 5e-6, topology_certified=True)
    assert res["verdict"] == "CONSISTENT"

def test_route_p8_tension():
    # |A_CP| < 1e-6 at 3σ, topology certified
    res = route_lab_cp_result(1e-7, 2e-8, topology_certified=True)
    assert res["verdict"] == "P8_TENSION"

def test_route_below_sensitivity():
    # |A_CP| between 1e-6 and 1e-5, at 3σ, topology certified
    res = route_lab_cp_result(5e-6, 1e-6, topology_certified=True)
    assert res["verdict"] == "BELOW_SENSITIVITY"

def test_route_no_verdict_yet():
    # significance < 3σ
    res = route_lab_cp_result(1e-5, 8e-6, topology_certified=True)
    assert res["verdict"] == "NO_VERDICT_YET"

def test_route_consistent_has_action():
    res = route_lab_cp_result(3e-5, 5e-6, topology_certified=True)
    assert "action" in res
    assert len(res["action"]) > 0

def test_route_significance_computed():
    res = route_lab_cp_result(3e-5, 5e-6, topology_certified=True)
    expected_sig = 3e-5 / 5e-6
    assert abs(res["significance_sigma"] - expected_sig) < 0.1


# ── decision_grade_checklist ──────────────────────────────────────────────────

def test_checklist_returns_dict():
    cl = decision_grade_checklist()
    assert isinstance(cl, dict)

def test_checklist_five_items():
    cl = decision_grade_checklist()
    assert len(cl["checklist"]) == 5

def test_checklist_items_have_ids():
    cl = decision_grade_checklist()
    for item in cl["checklist"]:
        assert "item" in item
        assert item["item"].startswith("F-LAB-CP-")

def test_checklist_preregistration_status():
    cl = decision_grade_checklist()
    assert "PREREGISTERED" in cl["preregistration_status"]

def test_checklist_f_lab_cp_1_topology():
    cl = decision_grade_checklist()
    f1 = next(i for i in cl["checklist"] if i["item"] == "F-LAB-CP-1")
    assert "topology" in f1["description"].lower() or "Topology" in f1["description"]

def test_checklist_f_lab_cp_5_replication():
    cl = decision_grade_checklist()
    f5 = next(i for i in cl["checklist"] if i["item"] == "F-LAB-CP-5")
    assert "replication" in f5["description"].lower()


# ── preregistration_packet ────────────────────────────────────────────────────

def test_preregistration_packet_returns_dict():
    pkt = preregistration_packet()
    assert isinstance(pkt, dict)

def test_preregistration_packet_prediction_p8():
    pkt = preregistration_packet()
    assert pkt["prediction"] == "P8"

def test_preregistration_packet_has_routing_table():
    pkt = preregistration_packet()
    rt = pkt["routing_table"]
    assert "CONSISTENT" in rt
    assert "P8_TENSION" in rt
    assert "BELOW_SENSITIVITY" in rt
    assert "INCONCLUSIVE" in rt

def test_preregistration_packet_timeline_now():
    pkt = preregistration_packet()
    assert "NOW" in pkt["timeline"].upper() or "now" in pkt["timeline"]

def test_preregistration_packet_platforms_two():
    pkt = preregistration_packet()
    assert len(pkt["platforms"]) >= 2

def test_preregistration_packet_falsification_note():
    pkt = preregistration_packet()
    assert "LiteBIRD" in pkt["falsification_note"]
    assert "P2" in pkt["falsification_note"] or "framework" in pkt["falsification_note"]

def test_preregistration_packet_checklist_present():
    pkt = preregistration_packet()
    assert "decision_grade_checklist" in pkt


# ── pillar307_report ──────────────────────────────────────────────────────────

def test_pillar307_report_returns_dict():
    rpt = pillar307_report()
    assert isinstance(rpt, dict)

def test_pillar307_report_pillar_number():
    rpt = pillar307_report()
    assert rpt["pillar"] == 307

def test_pillar307_report_status_preregistered():
    rpt = pillar307_report()
    assert "PREREGISTERED" in rpt["status"]

def test_pillar307_report_what_it_does_nonempty():
    rpt = pillar307_report()
    assert len(rpt["what_this_pillar_does"]) >= 4

def test_pillar307_report_next_action():
    rpt = pillar307_report()
    assert "next_action" in rpt
    assert "F-LAB-CP" in rpt["next_action"] or "route_lab" in rpt["next_action"]

def test_pillar307_report_separation_guard():
    rpt = pillar307_report()
    assert "separation_guard" in rpt
    assert rpt["separation_guard"]["hardgate_impact"] == "NONE"
