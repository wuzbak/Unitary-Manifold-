# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/lab_litebird_substitute.py."""
from __future__ import annotations

import pytest

from src.core.lab_litebird_substitute import (
    LAB_TRACKS,
    SIGMA_TARGET,
    LabCPCampaignInput,
    dual_track_campaign_readiness,
    evaluate_dual_track_campaign,
    evaluate_lab_cp_campaign,
    lab_track_packet_template,
    lab_protocol_checklist,
    lab_substitute_status_snapshot,
)


def _create_lab_campaign_input_with_defaults(**kwargs) -> LabCPCampaignInput:
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
        evaluate_lab_cp_campaign(_create_lab_campaign_input_with_defaults(sigma_a=-1e-5))


def test_not_topology_certified_is_inconclusive():
    out = evaluate_lab_cp_campaign(_create_lab_campaign_input_with_defaults(topology_certified=False))
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["decision_grade"] is False


def test_not_decision_grade_sensitivity_is_inconclusive():
    out = evaluate_lab_cp_campaign(_create_lab_campaign_input_with_defaults(sigma_a=2e-5))
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["decision_grade"] is False


def test_f_lab_cp_1_triggers_falsified():
    out = evaluate_lab_cp_campaign(_create_lab_campaign_input_with_defaults(a_cp_lab=0.0, sigma_a=1e-5))
    assert out["verdict"] == "FALSIFIED"
    assert "F-LAB-CP-1" in out["triggered_conditions"]


def test_f_lab_cp_2_triggers_falsified():
    out = evaluate_lab_cp_campaign(_create_lab_campaign_input_with_defaults(topology_independent_asymmetry=True))
    assert out["verdict"] == "FALSIFIED"
    assert "F-LAB-CP-2" in out["triggered_conditions"]


def test_f_lab_cp_3_triggers_falsified():
    out = evaluate_lab_cp_campaign(
        _create_lab_campaign_input_with_defaults(
            sign_reversal_inverts_cp_odd=False, cp_even_baseline_stable=True
        )
    )
    assert out["verdict"] == "FALSIFIED"
    assert "F-LAB-CP-3" in out["triggered_conditions"]


def test_f_lab_cp_4_triggers_falsified():
    out = evaluate_lab_cp_campaign(_create_lab_campaign_input_with_defaults(signal_explained_by_systematics=True))
    assert out["verdict"] == "FALSIFIED"
    assert "F-LAB-CP-4" in out["triggered_conditions"]


def test_supported_when_nonzero_and_controls_pass():
    out = evaluate_lab_cp_campaign(_create_lab_campaign_input_with_defaults(a_cp_lab=4.0e-5, sigma_a=1.0e-5))
    assert out["verdict"] == "SUPPORTED"
    assert out["decision_grade"] is True
    assert out["falsified"] is False


def test_inconclusive_when_decision_grade_but_weak_signal():
    out = evaluate_lab_cp_campaign(_create_lab_campaign_input_with_defaults(a_cp_lab=2.0e-5, sigma_a=1.0e-5))
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["decision_grade"] is True


def test_protocol_checklist_has_required_items():
    checklist = lab_protocol_checklist()
    assert len(checklist) >= 7
    assert any("topology certification" in item.lower() for item in checklist)
    assert any("conjugate protocols" in item.lower() for item in checklist)
    assert any("sigma_a" in item for item in checklist)
    assert any("topology-swap" in item.lower() for item in checklist)
    assert any("sign-reversal" in item.lower() for item in checklist)
    assert any("systematics decomposition" in item.lower() for item in checklist)
    assert any("independent replications" in item.lower() for item in checklist)


def test_track_packet_template_shape():
    packet = lab_track_packet_template("A")
    assert packet["track_id"] == "A"
    assert packet["platform"] == LAB_TRACKS["A"]["platform"]
    assert packet["decision_grade_sigma_target"] == SIGMA_TARGET
    assert "required_packet_fields" in packet
    assert "required_checklist" in packet


def test_track_packet_template_rejects_unknown_track():
    with pytest.raises(ValueError, match="Unknown track_id"):
        lab_track_packet_template("C")


def test_dual_track_campaign_readiness_has_both_tracks():
    report = dual_track_campaign_readiness()
    assert report["execution_mode"] == "PARALLEL_DUAL_TRACK"
    assert [track["track_id"] for track in report["tracks"]] == ["A", "B"]
    assert "consensus_rule" in report


def test_dual_track_campaign_supported_when_both_tracks_support():
    campaign = {
        "A": _create_lab_campaign_input_with_defaults(a_cp_lab=4.0e-5, sigma_a=1.0e-5),
        "B": _create_lab_campaign_input_with_defaults(a_cp_lab=5.0e-5, sigma_a=1.0e-5),
    }
    out = evaluate_dual_track_campaign(campaign)
    assert out["verdict"] == "SUPPORTED"
    assert out["falsified_tracks"] == []
    assert out["supported_tracks"] == ["A", "B"]


def test_dual_track_campaign_falsified_when_any_track_falsifies():
    campaign = {
        "A": _create_lab_campaign_input_with_defaults(a_cp_lab=0.0, sigma_a=1.0e-5),
        "B": _create_lab_campaign_input_with_defaults(a_cp_lab=5.0e-5, sigma_a=1.0e-5),
    }
    out = evaluate_dual_track_campaign(campaign)
    assert out["verdict"] == "FALSIFIED"
    assert out["falsified_tracks"] == ["A"]
    assert "F-LAB-CP-1" in out["triggered_conditions"]


def test_dual_track_campaign_inconclusive_when_tracks_mixed():
    campaign = {
        "A": _create_lab_campaign_input_with_defaults(a_cp_lab=5.0e-5, sigma_a=1.0e-5),
        "B": _create_lab_campaign_input_with_defaults(a_cp_lab=2.0e-5, sigma_a=1.0e-5),
    }
    out = evaluate_dual_track_campaign(campaign)
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["supported_tracks"] == ["A"]


def test_dual_track_campaign_requires_exact_track_set():
    with pytest.raises(ValueError, match="campaigns must provide exactly tracks"):
        evaluate_dual_track_campaign({"A": _create_lab_campaign_input_with_defaults()})


def test_status_snapshot_shape():
    snap = lab_substitute_status_snapshot()
    assert snap["lane_id"] == "F14/P8"
    assert snap["status"] == "PENDING_CAMPAIGN"
    assert snap["sigma_target"] == SIGMA_TARGET
    assert snap["execution_mode"] == "PARALLEL_DUAL_TRACK"
    assert [track["track_id"] for track in snap["tracks"]] == ["A", "B"]
    assert isinstance(snap["checklist"], list)
