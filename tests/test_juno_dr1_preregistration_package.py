# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for JUNO DR1 Preregistration Package."""
import pytest
from src.core.juno_dr1_preregistration_package import (
    ADJACENCY_TRACK_LABEL,
    UM_DM31_NLO_EV2,
    UM_DM31_BASELINE_EV2,
    DM31_PDG_EV2,
    JUNO_PRECISION_TARGET,
    TENSION_THRESHOLD_PCT,
    FALSIFIED_THRESHOLD_PCT,
    DOCS_TO_UPDATE,
    separation_guard,
    um_dm31_prediction,
    juno_dr1_routing,
    juno_dr1_readiness_checklist,
    juno_dr1_preregistration_report,
)


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard_keys():
    g = separation_guard()
    assert g["is_hardgate"] is False
    assert g["preregistration"] is True
    assert g["target_experiment"] == "JUNO"
    assert g["expected_dr1_year"] == 2027


def test_nlo_prediction_close_to_pdg():
    # NLO-tightened should be within 1% of PDG
    assert abs(UM_DM31_NLO_EV2 - DM31_PDG_EV2) / DM31_PDG_EV2 < 0.01


def test_baseline_below_pdg():
    assert UM_DM31_BASELINE_EV2 < DM31_PDG_EV2


def test_nlo_above_baseline():
    assert UM_DM31_NLO_EV2 > UM_DM31_BASELINE_EV2


def test_prediction_chain_keys():
    p = um_dm31_prediction()
    for key in ("baseline_ev2", "nlo_tightened_ev2", "pdg_2024_ev2",
                "baseline_residual_pct", "nlo_residual_pct",
                "preregistered_prediction_ev2"):
        assert key in p


def test_prediction_nlo_residual_below_tension():
    p = um_dm31_prediction()
    assert p["nlo_residual_pct"] < TENSION_THRESHOLD_PCT


def test_prediction_baseline_residual_large():
    p = um_dm31_prediction()
    assert p["baseline_residual_pct"] > 1.0  # 2.16% at baseline


def test_routing_consistent():
    r = juno_dr1_routing(UM_DM31_NLO_EV2, JUNO_PRECISION_TARGET * UM_DM31_NLO_EV2)
    assert r["verdict"] == "JUNO_CONSISTENT"


def test_routing_consistent_residual_zero():
    r = juno_dr1_routing(UM_DM31_NLO_EV2, 1.23e-5)
    assert r["residual_pct"] == 0.0


def test_routing_tension():
    # 1.5% away from UM prediction → TENSION
    measured = UM_DM31_NLO_EV2 * 1.015
    r = juno_dr1_routing(measured, 1.23e-5)
    assert r["verdict"] == "JUNO_TENSION"


def test_routing_falsified():
    # 5% away → FALSIFIED
    measured = UM_DM31_NLO_EV2 * 1.05
    r = juno_dr1_routing(measured, 1.23e-5)
    assert r["verdict"] == "JUNO_FALSIFIED"


def test_routing_keys():
    r = juno_dr1_routing(DM31_PDG_EV2, 1.23e-5)
    for key in ("measured_dm31_ev2", "um_prediction_ev2", "residual_pct",
                "sigma_pull", "verdict", "action_required", "docs_to_update"):
        assert key in r


def test_routing_raises_non_positive_measured():
    with pytest.raises(ValueError):
        juno_dr1_routing(0.0, 1.23e-5)


def test_routing_raises_non_positive_sigma():
    with pytest.raises(ValueError):
        juno_dr1_routing(DM31_PDG_EV2, 0.0)


def test_routing_sigma_pull_positive():
    r = juno_dr1_routing(DM31_PDG_EV2, 1.23e-5)
    assert r["sigma_pull"] >= 0.0


def test_docs_to_update_is_list():
    assert isinstance(DOCS_TO_UPDATE, list)
    assert len(DOCS_TO_UPDATE) > 0


def test_readiness_checklist_is_list():
    c = juno_dr1_readiness_checklist()
    assert isinstance(c, list)
    assert len(c) >= 5


def test_readiness_checklist_items_have_keys():
    c = juno_dr1_readiness_checklist()
    for item in c:
        for key in ("item", "status", "value"):
            assert key in item


def test_preregistration_report_status():
    r = juno_dr1_preregistration_report()
    assert r["status"] == "PREREGISTRATION_LOCKED"


def test_preregistration_report_has_sections():
    r = juno_dr1_preregistration_report()
    for key in ("prediction_chain", "routing_example_consistent", "readiness_checklist"):
        assert key in r
