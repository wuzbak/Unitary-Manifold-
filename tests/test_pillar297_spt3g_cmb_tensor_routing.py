# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 297 — SPT-3G CMB Tensor-to-Scalar Ratio Routing."""
import math
import pytest
from src.core.pillar297_spt3g_cmb_tensor_routing import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    UM_R_HARDGATED,
    UM_NS_HARDGATED,
    SPT3G_NS_PLANCK,
    SPT3G_NS_PLANCK_SIGMA,
    SPT3G_NS_ALONE,
    SPT3G_NS_ALONE_SIGMA,
    SPT3G_R_UPPER_95,
    BICEP_KECK_R_UPPER_95,
    ACT_DR6_R_UPPER_95,
    P2_FALSIFIER_THRESHOLD,
    JOINT_CONSISTENT_THRESHOLD,
    JOINT_FALSIFIED_THRESHOLD,
    separation_guard,
    spt3g_ns_verdict,
    spt3g_r_verdict,
    ground_based_cmb_network_summary,
    joint_actdr6_spt3g_preregistration,
    spt3g_routing_report,
)


# ── Constants ──────────────────────────────────────────────────────────────


def test_pillar_number():
    assert PILLAR_NUMBER == 297


def test_pillar_title():
    assert "SPT" in PILLAR_TITLE


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_um_r_hardgated():
    assert abs(UM_R_HARDGATED - 0.0315) < 1e-6


def test_um_ns_hardgated():
    assert abs(UM_NS_HARDGATED - 0.9635) < 1e-6


def test_spt3g_ns_planck():
    assert abs(SPT3G_NS_PLANCK - 0.9657) < 1e-4


def test_spt3g_ns_planck_sigma():
    assert SPT3G_NS_PLANCK_SIGMA > 0.0


def test_spt3g_ns_alone():
    assert abs(SPT3G_NS_ALONE - 0.9707) < 1e-4


def test_spt3g_r_upper():
    # SPT-3G r bound must be at BICEP/Keck level (0.036)
    assert abs(SPT3G_R_UPPER_95 - 0.036) < 1e-6


def test_act_dr6_r_tighter_than_spt3g():
    # ACT DR6 is more constraining than SPT-3G alone
    assert ACT_DR6_R_UPPER_95 < SPT3G_R_UPPER_95


def test_p2_falsifier_threshold():
    assert abs(P2_FALSIFIER_THRESHOLD - 0.010) < 1e-6


def test_joint_consistent_threshold():
    assert abs(JOINT_CONSISTENT_THRESHOLD - 0.020) < 1e-6


def test_joint_falsified_threshold():
    assert abs(JOINT_FALSIFIED_THRESHOLD - 0.010) < 1e-6


def test_threshold_ordering():
    # Falsified < Consistent
    assert JOINT_FALSIFIED_THRESHOLD < JOINT_CONSISTENT_THRESHOLD


# ── separation_guard ────────────────────────────────────────────────────────


def test_separation_guard_pillar():
    g = separation_guard()
    assert g["pillar"] == 297


def test_separation_guard_not_hardgate():
    g = separation_guard()
    assert g["is_hardgate"] is False


def test_separation_guard_no_hardgate_modification():
    g = separation_guard()
    assert g["modifies_hardgate_module"] is False


def test_separation_guard_extends_pillar():
    g = separation_guard()
    assert g["extends_pillar"] == 292


def test_separation_guard_dataset():
    g = separation_guard()
    assert "SPT" in g["dataset"]


# ── spt3g_ns_verdict ────────────────────────────────────────────────────────


def test_ns_verdict_keys():
    v = spt3g_ns_verdict()
    for key in ("um_ns", "spt3g_ns_planck", "pull_spt3g_planck_sigma", "verdict"):
        assert key in v, f"Missing key: {key}"


def test_ns_verdict_consistent():
    v = spt3g_ns_verdict()
    assert v["verdict"] == "CONSISTENT"


def test_ns_pull_below_1sigma():
    v = spt3g_ns_verdict()
    # n_s tension should be well below 1σ
    assert v["pull_spt3g_planck_sigma"] < 1.0


def test_ns_pull_planck_approx():
    # |0.9635 − 0.9657| / 0.0040 = 0.55σ
    v = spt3g_ns_verdict()
    expected_pull = abs(UM_NS_HARDGATED - SPT3G_NS_PLANCK) / SPT3G_NS_PLANCK_SIGMA
    assert abs(v["pull_spt3g_planck_sigma"] - expected_pull) < 1e-4


def test_ns_alone_pull_included():
    v = spt3g_ns_verdict()
    assert "pull_spt3g_alone_sigma" in v
    assert v["pull_spt3g_alone_sigma"] >= 0.0


# ── spt3g_r_verdict ─────────────────────────────────────────────────────────


def test_r_verdict_keys():
    v = spt3g_r_verdict()
    for key in ("um_r", "spt3g_r_upper_95", "spt3g_consistent",
                "act_dr6_r_upper_95", "act_dr6_consistent",
                "p2_falsifier_triggered", "verdict_spt3g", "verdict_act_dr6"):
        assert key in v, f"Missing key: {key}"


def test_r_verdict_spt3g_consistent():
    v = spt3g_r_verdict()
    assert v["verdict_spt3g"] == "CONSISTENT"


def test_r_verdict_act_dr6_tension():
    v = spt3g_r_verdict()
    assert v["verdict_act_dr6"] == "HIGH_TENSION"


def test_r_p2_not_triggered():
    v = spt3g_r_verdict()
    assert v["p2_falsifier_triggered"] is False


def test_r_spt3g_consistent_boolean():
    v = spt3g_r_verdict()
    assert v["spt3g_consistent"] is True


def test_r_act_not_consistent():
    v = spt3g_r_verdict()
    assert v["act_dr6_consistent"] is False


def test_r_combined_network_label():
    v = spt3g_r_verdict()
    assert "HIGH_TENSION" in v["combined_network_verdict"]


# ── ground_based_cmb_network_summary ────────────────────────────────────────


def test_network_summary_is_list():
    n = ground_based_cmb_network_summary()
    assert isinstance(n, list)


def test_network_summary_length():
    n = ground_based_cmb_network_summary()
    assert len(n) >= 5  # At least Planck, BK, ACT, SPT-3G, SO, CMB-S4


def test_network_planck_entry():
    n = ground_based_cmb_network_summary()
    planck = [inst for inst in n if "Planck" in inst["instrument"]]
    assert len(planck) == 1
    assert planck[0]["ns_verdict"] == "CONSISTENT"


def test_network_spt3g_consistent():
    n = ground_based_cmb_network_summary()
    spt = [inst for inst in n if "SPT" in inst["instrument"]]
    assert len(spt) == 1
    assert spt[0]["r_verdict"] == "CONSISTENT"


def test_network_act_high_tension():
    n = ground_based_cmb_network_summary()
    act = [inst for inst in n if "ACT" in inst["instrument"]]
    assert len(act) == 1
    assert act[0]["r_verdict"] == "HIGH_TENSION"


def test_network_cmbs4_pending():
    n = ground_based_cmb_network_summary()
    cmbs4 = [inst for inst in n if "CMB-S4" in inst["instrument"]]
    assert len(cmbs4) == 1
    assert cmbs4[0]["r_verdict"] == "PENDING"


def test_network_so_pending():
    n = ground_based_cmb_network_summary()
    so = [inst for inst in n if "Simons" in inst["instrument"]]
    assert len(so) == 1
    assert so[0]["r_verdict"] == "PENDING"


def test_network_all_have_instrument_key():
    n = ground_based_cmb_network_summary()
    for inst in n:
        assert "instrument" in inst


# ── joint_actdr6_spt3g_preregistration ─────────────────────────────────────


def test_preregistration_keys():
    p = joint_actdr6_spt3g_preregistration()
    for key in ("preregistration_label", "preregistration_version",
                "preregistration_date", "routing_rules"):
        assert key in p, f"Missing key: {key}"


def test_preregistration_version():
    p = joint_actdr6_spt3g_preregistration()
    assert p["preregistration_version"] == "v11.10"


def test_preregistration_routing_rules_complete():
    p = joint_actdr6_spt3g_preregistration()
    rules = p["routing_rules"]
    for verdict in ("CONSISTENT", "TENSION_MAINTAINED", "FALSIFIED"):
        assert verdict in rules, f"Missing routing rule: {verdict}"


def test_preregistration_falsified_rule_has_action():
    p = joint_actdr6_spt3g_preregistration()
    falsified = p["routing_rules"]["FALSIFIED"]
    assert "action" in falsified
    assert "CLAIM_MASTER_BOARD" in falsified["action"]


# ── spt3g_routing_report ─────────────────────────────────────────────────────


def test_report_keys():
    r = spt3g_routing_report()
    for key in ("pillar", "title", "adjacency_guard", "ns_routing",
                "r_routing", "ground_based_network", "joint_preregistration",
                "summary", "status"):
        assert key in r, f"Missing key: {key}"


def test_report_pillar():
    r = spt3g_routing_report()
    assert r["pillar"] == 297


def test_report_summary_p2_not_triggered():
    r = spt3g_routing_report()
    assert r["summary"]["p2_falsifier_triggered"] is False


def test_report_summary_decisive_experiment():
    r = spt3g_routing_report()
    assert "CMB-S4" in r["summary"]["decisive_experiment"]


def test_report_summary_consistent_count():
    r = spt3g_routing_report()
    # At least Planck BK and SPT-3G give r CONSISTENT (= 2 instruments)
    # Note: Planck doesn't test r, BK/BICEP does, SPT-3G does → 2 r CONSISTENT
    assert r["summary"]["r_consistent"] >= 2


def test_report_summary_tension_count():
    r = spt3g_routing_report()
    # ACT DR6 alone gives HIGH_TENSION
    assert r["summary"]["r_tension"] >= 1


def test_report_status():
    r = spt3g_routing_report()
    assert "COMPLETE" in r["status"]


def test_report_label():
    r = spt3g_routing_report()
    assert r["label"] == "ADJACENT_TRACK"
