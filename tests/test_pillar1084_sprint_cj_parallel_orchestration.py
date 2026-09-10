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
    assert isinstance(bool(PILLAR_VALID), bool)
    assert bool(PILLAR_VALID) == sprint_cj_parallel_orchestration()["valid"]


def test_parallel_packet_contract() -> None:
    report = sprint_cj_parallel_orchestration()
    assert report["outcome"] == "SPRINT_CJ_PARALLEL_ORCHESTRATION_READY"
    assert report["valid"] is True
    assert report["lane_1"]["attempt_policy"]["exactly_one_new_object_evidence_class_required"] is True
    assert report["lane_2"]["sovereign_local_primary"] is True
    assert report["lane_2"]["external_token_path_compatibility_only"] is True
    assert report["integrated_board"]["mode"] == "parallel_fail_closed"
    assert len(report["integrated_board"]["truth_surface_sync_paths"]) == 9
    assert report["benchmark_corpora_check"]["stage_coverage_pass"] is True
    assert report["truth_surface_sync"]["all_pass"] is True


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


def test_invalid_if_frontier_stage_order_breaks(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _bad_frontier(limit=3):
        packet = original(limit=limit)
        packet["multi_stage_plan"]["stages"] = list(reversed(packet["multi_stage_plan"]["stages"]))
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _bad_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_frontier_stage_sequence_ok"] is False
    assert report["integrated_board"]["dependencies"]["lane_2_frontier_packet_ok"] is False
    assert report["promotion_policy_state"] == "INVALID"
    assert report["valid"] is False


def test_invalid_if_corpora_stage_missing(monkeypatch) -> None:
    benchmark_mod = p1084._load("ox_navigator.engine.merlin_benchmark")
    original = benchmark_mod.get_benchmark_corpus
    monkeypatch.setattr(
        benchmark_mod,
        "get_benchmark_corpus",
        lambda stage="all": {"ok": True, "corpora": {}} if stage == "all" else original(stage),
    )
    report = sprint_cj_parallel_orchestration()
    assert report["benchmark_corpora_check"]["stage_coverage_pass"] is False
    assert report["integrated_board"]["dependencies"]["lane_2_requires_nonempty_stage_corpora"] is False
    assert report["valid"] is False


def test_invalid_if_truth_surface_sync_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1084, "_truth_surface_sync_status", lambda: {"all_pass": False, "files": []})
    report = sprint_cj_parallel_orchestration()
    assert report["truth_surface_sync"]["all_pass"] is False
    assert report["integrated_board"]["dependencies"]["truth_surfaces_synchronized_to_v36_6"] is False
    assert report["valid"] is False


def test_invalid_if_frontier_packet_reports_failure(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _failed_frontier(limit=3):
        packet = original(limit=limit)
        packet["sync_checks"] = {"ok": False}
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _failed_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_frontier_packet_ok"] is False
    assert report["promotion_policy_state"] == "INVALID"
    assert report["valid"] is False


def test_invalid_if_frontier_blocker_consistency_breaks(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _inconsistent_frontier(limit=3):
        packet = original(limit=limit)
        packet["promotion_blockers_all_clear"] = not bool(packet.get("promotion_blockers_all_clear"))
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _inconsistent_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_blocker_consistency_ok"] is False
    assert report["valid"] is False


def test_invalid_if_blockers_all_clear_type_is_non_boolean(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _invalid_type_frontier(limit=3):
        packet = original(limit=limit)
        packet["promotion_blockers"] = []
        packet["promotion_blockers_all_clear"] = "false"
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _invalid_type_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_blockers_all_clear_type_ok"] is False
    assert report["integrated_board"]["dependencies"]["lane_2_frontier_packet_ok"] is False
    assert report["promotion_policy_state"] == "INVALID"
    assert report["valid"] is False


def test_invalid_if_blocker_pass_field_is_non_boolean(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _invalid_blocker_pass_type(limit=3):
        packet = original(limit=limit)
        packet["promotion_blockers"] = [{"name": "quality_floor", "pass": "false"}]
        packet["promotion_blockers_all_clear"] = False
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _invalid_blocker_pass_type)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_blocker_pass_fields_are_boolean"] is False
    assert report["integrated_board"]["dependencies"]["lane_2_blocker_consistency_ok"] is False
    assert report["integrated_board"]["dependencies"]["lane_2_frontier_packet_ok"] is False
    assert report["promotion_policy_state"] == "INVALID"
    assert report["valid"] is False


def test_empty_blockers_all_clear_is_consistent(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _empty_clear_frontier(limit=3):
        packet = original(limit=limit)
        packet["promotion_blockers"] = []
        packet["promotion_blockers_all_clear"] = True
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _empty_clear_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_requires_promotion_blockers_declared"] is True
    assert report["integrated_board"]["dependencies"]["lane_2_blocker_consistency_ok"] is True
    assert report["valid"] is True
    assert report["outcome"] == "SPRINT_CJ_PARALLEL_ORCHESTRATION_READY"


def test_empty_blockers_without_declared_all_clear_is_consistent(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _empty_implicit_clear_frontier(limit=3):
        packet = original(limit=limit)
        packet["promotion_blockers"] = []
        packet.pop("promotion_blockers_all_clear", None)
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _empty_implicit_clear_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_blocker_consistency_ok"] is True
    assert report["lane_2"]["promotion_blockers_all_clear"] is True
    assert report["valid"] is True


def test_nonempty_passing_blockers_imply_all_clear(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _nonempty_passing_blockers(limit=3):
        packet = original(limit=limit)
        packet["promotion_blockers"] = [{"name": "info_only", "pass": True}]
        packet.pop("promotion_blockers_all_clear", None)
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _nonempty_passing_blockers)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_blocker_consistency_ok"] is True
    assert report["lane_2"]["promotion_blockers_all_clear"] is True
    assert report["promotion_policy_state"] == "PASS"
    assert report["integrated_board"]["dependencies"]["promotion_language_gate_pass"] is True
    assert report["integrated_board"]["dependencies"]["promotion_language_freeze_enforced"] is False


def test_nonempty_passing_blockers_declared_true_is_consistent(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _declared_true_frontier(limit=3):
        packet = original(limit=limit)
        packet["promotion_blockers"] = [{"name": "info_only", "pass": True}]
        packet["promotion_blockers_all_clear"] = True
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _declared_true_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["lane_2"]["promotion_blockers_all_clear_declared"] is True
    assert report["lane_2"]["promotion_blockers_all_clear"] is True
    assert report["integrated_board"]["dependencies"]["lane_2_declared_all_clear_matches_effective_semantics"] is True
    assert report["integrated_board"]["dependencies"]["lane_2_blocker_consistency_ok"] is True
    assert report["promotion_policy_state"] == "PASS"
    assert report["valid"] is True


def test_nonempty_failing_blockers_enforce_freeze(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _failing_blockers_frontier(limit=3):
        packet = original(limit=limit)
        packet["promotion_blockers"] = [{"name": "quality_floor", "pass": False}]
        packet["promotion_blockers_all_clear"] = False
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _failing_blockers_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["lane_2"]["promotion_blockers_all_clear"] is False
    assert report["integrated_board"]["dependencies"]["lane_2_blocker_consistency_ok"] is True
    assert report["promotion_policy_state"] == "FREEZE"
    assert report["integrated_board"]["dependencies"]["promotion_language_gate_pass"] is False
    assert report["integrated_board"]["dependencies"]["promotion_language_freeze_enforced"] is True
    assert report["valid"] is True


def test_summary() -> None:
    summary = pillar1084_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True


def test_summary_reflects_invalid_packet(monkeypatch) -> None:
    monkeypatch.setattr(
        p1084,
        "sprint_cj_parallel_orchestration",
        lambda: {"status": PILLAR_STATUS, "outcome": "SPRINT_CJ_PARALLEL_ORCHESTRATION_BLOCKED", "valid": False},
    )
    summary = pillar1084_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["outcome"] == "SPRINT_CJ_PARALLEL_ORCHESTRATION_BLOCKED"
    assert summary["valid"] is False


def test_invalid_if_proof_contract_name_changes(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    monkeypatch.setattr(
        program_mod,
        "get_deterministic_proof_closure_contract",
        lambda: {"name": "wrong_contract"},
    )
    report = sprint_cj_parallel_orchestration()
    assert report["proof_first_contract"]["name"] == "wrong_contract"
    assert report["valid"] is False


def test_invalid_if_proof_contract_is_nondict(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    monkeypatch.setattr(
        program_mod,
        "get_deterministic_proof_closure_contract",
        lambda: None,
    )
    report = sprint_cj_parallel_orchestration()
    assert report["proof_first_contract"] == {}
    assert report["valid"] is False


def test_invalid_if_benchmark_plan_is_nondict(monkeypatch) -> None:
    benchmark_mod = p1084._load("ox_navigator.engine.merlin_benchmark")
    monkeypatch.setattr(benchmark_mod, "get_multi_stage_benchmark_plan", lambda: [])
    report = sprint_cj_parallel_orchestration()
    assert report["lane_2"]["stage_sequence"] == []
    assert report["valid"] is False


def test_invalid_if_benchmark_plan_has_mixed_stage_rows(monkeypatch) -> None:
    benchmark_mod = p1084._load("ox_navigator.engine.merlin_benchmark")
    original = benchmark_mod.get_multi_stage_benchmark_plan

    def _mixed_rows():
        plan = original()
        plan["stages"] = [plan["stages"][0], "bad-row", plan["stages"][1]]
        return plan

    monkeypatch.setattr(benchmark_mod, "get_multi_stage_benchmark_plan", _mixed_rows)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_stage_list_shape_ok"] is False
    assert report["valid"] is False


def test_invalid_if_frontier_control_tower_payload_missing(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _broken_frontier(limit=3):
        packet = original(limit=limit)
        packet["control_tower"] = {}
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _broken_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_frontier_packet_ok"] is False
    assert report["valid"] is False


def test_invalid_if_frontier_control_tower_nested_payloads_empty(monkeypatch) -> None:
    program_mod = p1084._load("ox_navigator.engine.merlin_program")
    original = program_mod.get_frontier_readiness_packet

    def _broken_frontier(limit=3):
        packet = original(limit=limit)
        packet["control_tower"]["replacement_readiness"] = {}
        packet["control_tower"]["longitudinal_acceptance"] = {}
        return packet

    monkeypatch.setattr(program_mod, "get_frontier_readiness_packet", _broken_frontier)
    report = sprint_cj_parallel_orchestration()
    assert report["integrated_board"]["dependencies"]["lane_2_frontier_packet_ok"] is False
    assert report["promotion_policy_state"] == "INVALID"
    assert report["valid"] is False
