# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/lab_litebird_substitute.py."""
from __future__ import annotations

import pytest

from src.core.lab_litebird_substitute import (
    SIGMA_TARGET,
    LabCPCampaignInput,
    evaluate_lab_cp_campaign,
    lab_protocol_checklist,
    lab_substitute_status_snapshot,
)


def _base_input(**kwargs) -> LabCPCampaignInput:
    data = dict(
        a_cp_lab=0.0,
        sigma_a=SIGMA_TARGET,
        topology_certified=True,
        independent_replications=2,
        systematics_controls_passed=True,
        topology_independent_asymmetry=False,
        sign_reversal_inverts_cp_odd=True,
        cp_even_baseline_stable=True,
        signal_explained_by_systematics=False,
    )
    data.update(kwargs)
    return LabCPCampaignInput(**data)


def test_negative_sigma_raises():
    with pytest.raises(ValueError, match="sigma_a must be positive"):
        evaluate_lab_cp_campaign(_base_input(sigma_a=-1e-5))


def test_not_topology_certified_is_inconclusive():
    out = evaluate_lab_cp_campaign(_base_input(topology_certified=False))
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["decision_grade"] is False


def test_not_decision_grade_sensitivity_is_inconclusive():
    out = evaluate_lab_cp_campaign(_base_input(sigma_a=2e-5))
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["decision_grade"] is False


def test_f_lab_cp_1_triggers_falsified():
    out = evaluate_lab_cp_campaign(_base_input(a_cp_lab=0.0, sigma_a=1e-5))
    assert out["verdict"] == "FALSIFIED"
    assert "F-LAB-CP-1" in out["triggered_conditions"]


def test_f_lab_cp_2_triggers_falsified():
    out = evaluate_lab_cp_campaign(_base_input(topology_independent_asymmetry=True))
    assert out["verdict"] == "FALSIFIED"
    assert "F-LAB-CP-2" in out["triggered_conditions"]


def test_f_lab_cp_3_triggers_falsified():
    out = evaluate_lab_cp_campaign(
        _base_input(sign_reversal_inverts_cp_odd=False, cp_even_baseline_stable=True)
    )
    assert out["verdict"] == "FALSIFIED"
    assert "F-LAB-CP-3" in out["triggered_conditions"]


def test_f_lab_cp_4_triggers_falsified():
    out = evaluate_lab_cp_campaign(_base_input(signal_explained_by_systematics=True))
    assert out["verdict"] == "FALSIFIED"
    assert "F-LAB-CP-4" in out["triggered_conditions"]


def test_supported_when_nonzero_and_controls_pass():
    out = evaluate_lab_cp_campaign(_base_input(a_cp_lab=4.0e-5, sigma_a=1.0e-5))
    assert out["verdict"] == "SUPPORTED"
    assert out["decision_grade"] is True
    assert out["falsified"] is False


def test_inconclusive_when_decision_grade_but_weak_signal():
    out = evaluate_lab_cp_campaign(_base_input(a_cp_lab=2.0e-5, sigma_a=1.0e-5))
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["decision_grade"] is True


def test_protocol_checklist_has_required_items():
    checklist = lab_protocol_checklist()
    assert len(checklist) >= 7
    assert any("sigma_a" in item for item in checklist)
    assert any("Topology-swap" in item for item in checklist)


def test_status_snapshot_shape():
    snap = lab_substitute_status_snapshot()
    assert snap["lane_id"] == "F14/P8"
    assert snap["status"] == "PENDING_CAMPAIGN"
    assert snap["sigma_target"] == SIGMA_TARGET
    assert isinstance(snap["checklist"], list)

