# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1084_sprint_cj_parallel_orchestration as p1084

from src.core.pillar1084_sprint_cj_parallel_orchestration import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1084_summary,
    sprint_cj_parallel_orchestration,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1084
    assert PILLAR_GATE == "SPRINT_CJ_PARALLEL_ORCHESTRATION"
    assert PILLAR_STATUS == "SPRINT_CJ_PARALLEL_ORCHESTRATION_COMPLETE"
    assert isinstance(PILLAR_VALID, bool)


def test_parallel_packet_contract() -> None:
    report = sprint_cj_parallel_orchestration()
    assert report["outcome"] == "SPRINT_CJ_PARALLEL_ORCHESTRATION_READY"
    assert report["valid"] is True
    assert report["lane_1"]["attempt_policy"]["exactly_one_new_object_evidence_class_required"] is True
    assert report["lane_2"]["sovereign_local_primary"] is True
    assert report["lane_2"]["external_token_path_compatibility_only"] is True
    assert report["integrated_board"]["mode"] == "parallel_fail_closed"
    assert len(report["integrated_board"]["truth_surface_sync_paths"]) == 9


def test_stage_sequence_is_a_to_e() -> None:
    report = sprint_cj_parallel_orchestration()
    assert report["lane_2"]["stage_sequence"] == [
        "stage_a_parity_capture",
        "stage_b_sovereign_takeover",
        "stage_c_capability_expansion",
        "stage_d_replacement_gates",
        "stage_e_external_decommission",
    ]


def test_invalid_if_foundation_dependency_fails(monkeypatch) -> None:
    packet = p1084.foundation_first_photon_action_audit()
    packet["valid"] = False
    monkeypatch.setattr(p1084, "foundation_first_photon_action_audit", lambda: packet)
    report = sprint_cj_parallel_orchestration()
    assert report["valid"] is False
    assert report["lane_1"]["status"] == "BLOCKED"


def test_invalid_if_stage_order_breaks(monkeypatch) -> None:
    benchmark_mod = p1084._load("ox_navigator.engine.merlin_benchmark")
    plan = benchmark_mod.get_multi_stage_benchmark_plan()
    plan["stages"] = list(reversed(plan["stages"]))

    monkeypatch.setattr(benchmark_mod, "get_multi_stage_benchmark_plan", lambda: plan)
    report = sprint_cj_parallel_orchestration()
    assert report["valid"] is False
    assert report["integrated_board"]["dependencies"]["lane_2_requires_stage_sequence_a_to_e"] is False


def test_summary() -> None:
    summary = pillar1084_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
