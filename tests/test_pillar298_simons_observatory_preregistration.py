# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 298 — Simons Observatory CMB Preregistration Package."""
import math
import pytest
from src.core.pillar298_simons_observatory_preregistration import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    UM_R_HARDGATED,
    UM_NS_HARDGATED,
    SO_SIGMA_R_DR1,
    SO_SIGMA_R_5YR,
    SO_SIGMA_NS_5YR,
    SO_DR1_YEAR_EST,
    SO_5YR_YEAR_EST,
    SO_FSKY,
    P1_FALSIFIER_NS_LOW,
    P1_FALSIFIER_NS_HIGH,
    P2_FALSIFIER_R_THRESHOLD,
    SO_ROUTING_CONSISTENT_R,
    SO_ROUTING_FALSIFIED_R,
    DOCS_TO_UPDATE,
    separation_guard,
    so_r_detection_snr,
    so_ns_pull,
    so_dr1_r_routing,
    so_5yr_r_routing,
    so_ns_routing,
    so_preregistration_checklist,
    so_preregistration_report,
)


# ── Constants ──────────────────────────────────────────────────────────────


def test_pillar_number():
    assert PILLAR_NUMBER == 298


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_um_r():
    assert abs(UM_R_HARDGATED - 0.0315) < 1e-6


def test_um_ns():
    assert abs(UM_NS_HARDGATED - 0.9635) < 1e-6


def test_so_sigma_r_dr1_positive():
    assert SO_SIGMA_R_DR1 > 0.0


def test_so_sigma_r_5yr_positive():
    assert SO_SIGMA_R_5YR > 0.0


def test_so_sigma_r_5yr_tighter_than_dr1():
    assert SO_SIGMA_R_5YR < SO_SIGMA_R_DR1


def test_so_sigma_ns_5yr_positive():
    assert SO_SIGMA_NS_5YR > 0.0


def test_so_dr1_year():
    assert SO_DR1_YEAR_EST >= 2026


def test_so_fsky():
    assert 0.0 < SO_FSKY <= 1.0


def test_p1_falsifier_bounds():
    assert P1_FALSIFIER_NS_LOW < P1_FALSIFIER_NS_HIGH


def test_um_ns_inside_falsifier_bounds():
    # UM n_s should be inside P1 falsifier window
    assert P1_FALSIFIER_NS_LOW < UM_NS_HARDGATED < P1_FALSIFIER_NS_HIGH


def test_p2_falsifier_threshold():
    assert abs(P2_FALSIFIER_R_THRESHOLD - 0.010) < 1e-6


def test_routing_threshold_ordering():
    assert SO_ROUTING_FALSIFIED_R < SO_ROUTING_CONSISTENT_R


def test_docs_to_update_nonempty():
    assert len(DOCS_TO_UPDATE) >= 4


# ── separation_guard ────────────────────────────────────────────────────────


def test_separation_guard_pillar():
    g = separation_guard()
    assert g["pillar"] == 298


def test_separation_guard_not_hardgate():
    g = separation_guard()
    assert g["is_hardgate"] is False


def test_separation_guard_preregistration():
    g = separation_guard()
    assert g["preregistration"] is True


def test_separation_guard_experiment():
    g = separation_guard()
    assert "Simons" in g["target_experiment"]


# ── so_r_detection_snr ─────────────────────────────────────────────────────


def test_so_r_snr_keys():
    s = so_r_detection_snr()
    for key in ("r_assumed", "sigma_r", "snr",
                "detectable_at_3sigma", "detectable_at_5sigma"):
        assert key in s


def test_so_r_snr_5yr_above_5sigma():
    # At 5-yr sensitivity σ_r=0.003, UM r=0.0315 → SNR~10.5
    s = so_r_detection_snr(sigma_r=SO_SIGMA_R_5YR)
    assert s["snr"] > 5.0
    assert s["detectable_at_5sigma"] is True


def test_so_r_snr_dr1():
    # At DR1 σ_r=0.006, SNR~5.25 → detectable at 3σ
    s = so_r_detection_snr(sigma_r=SO_SIGMA_R_DR1)
    assert s["snr"] > 3.0
    assert s["detectable_at_3sigma"] is True


def test_so_r_snr_formula():
    s = so_r_detection_snr(r_true=0.030, sigma_r=0.005)
    expected = 0.030 / 0.005
    assert abs(s["snr"] - expected) < 1e-6


def test_so_r_snr_bad_sigma():
    with pytest.raises(ValueError):
        so_r_detection_snr(sigma_r=0.0)


# ── so_ns_pull ─────────────────────────────────────────────────────────────


def test_so_ns_pull_keys():
    p = so_ns_pull()
    for key in ("um_ns", "planck_ns", "sigma_ns",
                "pull_from_planck_sigma", "pull_from_falsifier_low_sigma",
                "p1_distinguishable"):
        assert key in p


def test_so_ns_pull_consistent_from_planck():
    p = so_ns_pull(sigma_ns=SO_SIGMA_NS_5YR)
    # pull from Planck n_s=0.9649 should be small
    assert p["pull_from_planck_sigma"] < 2.0
    assert p["ns_verdict_expected"] == "CONSISTENT"


def test_so_ns_p1_distinguishable():
    p = so_ns_pull(sigma_ns=SO_SIGMA_NS_5YR)
    # SO can distinguish UM n_s from falsifier lower bound (0.955)
    assert p["p1_distinguishable"] is True


def test_so_ns_pull_bad_sigma():
    with pytest.raises(ValueError):
        so_ns_pull(sigma_ns=-0.001)


# ── so_dr1_r_routing ─────────────────────────────────────────────────────


def test_dr1_routing_consistent():
    # r = 0.025 (central value) → CONSISTENT
    v = so_dr1_r_routing(r_measured=0.025, sigma_r=0.005)
    assert v["verdict"] == "CONSISTENT"
    assert v["p2_falsifier_triggered"] is False


def test_dr1_routing_tension():
    # r = 0.015 → between 0.010 and 0.020 → TENSION_MAINTAINED
    v = so_dr1_r_routing(r_measured=0.015, sigma_r=0.005)
    assert v["verdict"] == "TENSION_MAINTAINED"
    assert v["p2_falsifier_triggered"] is False


def test_dr1_routing_falsified():
    # r = 0.005 at sigma=0.001 → r/sigma = 5.0 ≥ 3 and r < 0.010 → FALSIFIED
    v = so_dr1_r_routing(r_measured=0.005, sigma_r=0.001)
    assert v["verdict"] == "FALSIFIED"
    assert v["p2_falsifier_triggered"] is True


def test_dr1_routing_not_falsified_without_3sigma():
    # r = 0.005 at sigma=0.010 → pull_from_zero = 0.5 < 3 → TENSION_MAINTAINED
    v = so_dr1_r_routing(r_measured=0.005, sigma_r=0.010)
    assert v["verdict"] == "TENSION_MAINTAINED"
    assert v["p2_falsifier_triggered"] is False


def test_dr1_routing_keys():
    v = so_dr1_r_routing(r_measured=0.020, sigma_r=0.003)
    for key in ("experiment", "r_measured", "sigma_r", "um_r",
                "pull_from_um", "verdict", "action", "p2_falsifier_triggered"):
        assert key in v


def test_dr1_routing_bad_sigma():
    with pytest.raises(ValueError):
        so_dr1_r_routing(r_measured=0.020, sigma_r=0.0)


# ── so_5yr_r_routing ──────────────────────────────────────────────────────


def test_5yr_routing_consistent_um_prediction():
    # If UM prediction is correct, SO 5-yr should route CONSISTENT
    v = so_5yr_r_routing(r_measured=UM_R_HARDGATED, sigma_r=SO_SIGMA_R_5YR)
    assert v["verdict"] == "CONSISTENT"


# ── so_ns_routing ─────────────────────────────────────────────────────────


def test_ns_routing_consistent():
    v = so_ns_routing(ns_measured=0.963, sigma_ns=0.002)
    assert v["verdict"] == "CONSISTENT"
    assert v["p1_falsifier_triggered"] is False


def test_ns_routing_falsified():
    # n_s outside falsifier window → FALSIFIED
    v = so_ns_routing(ns_measured=0.940, sigma_ns=0.001)
    assert v["verdict"] == "FALSIFIED"
    assert v["p1_falsifier_triggered"] is True


def test_ns_routing_tension():
    # n_s = 0.959 (inside bounds but 2σ from UM) — borderline tension
    v = so_ns_routing(ns_measured=0.9595, sigma_ns=0.002)
    # pull = |0.9595 - 0.9635| / 0.002 = 2.0 → TENSION
    assert v["pull_from_um"] >= 2.0


def test_ns_routing_keys():
    v = so_ns_routing(ns_measured=0.9635, sigma_ns=0.003)
    for key in ("experiment", "ns_measured", "sigma_ns", "um_ns",
                "pull_from_um", "verdict", "action", "p1_falsifier_triggered"):
        assert key in v


def test_ns_routing_bad_sigma():
    with pytest.raises(ValueError):
        so_ns_routing(ns_measured=0.9635, sigma_ns=0.0)


# ── so_preregistration_checklist ──────────────────────────────────────────


def test_checklist_is_list():
    c = so_preregistration_checklist()
    assert isinstance(c, list)


def test_checklist_has_steps():
    c = so_preregistration_checklist()
    assert len(c) >= 5


def test_checklist_sequential():
    c = so_preregistration_checklist()
    steps = [item["step"] for item in c]
    assert steps == sorted(steps)


def test_checklist_has_actions():
    c = so_preregistration_checklist()
    for item in c:
        assert "action" in item


# ── so_preregistration_report ─────────────────────────────────────────────


def test_report_keys():
    r = so_preregistration_report()
    for key in ("pillar", "title", "adjacency_guard", "um_predictions",
                "so_projections", "r_snr_dr1", "r_snr_5yr", "ns_pull_5yr",
                "routing_thresholds", "checklist", "significance", "status"):
        assert key in r


def test_report_pillar():
    r = so_preregistration_report()
    assert r["pillar"] == 298


def test_report_status():
    r = so_preregistration_report()
    assert r["status"] == "PREREGISTRATION_LOCKED"


def test_report_routing_thresholds_version():
    r = so_preregistration_report()
    assert r["routing_thresholds"]["preregistration_version"] == "v11.10"


def test_report_um_predictions():
    r = so_preregistration_report()
    assert abs(r["um_predictions"]["r"] - UM_R_HARDGATED) < 1e-6
    assert abs(r["um_predictions"]["ns"] - UM_NS_HARDGATED) < 1e-6


def test_report_significance_mentions_detection():
    r = so_preregistration_report()
    assert "DETECT" in r["significance"] or "detect" in r["significance"]
