# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 510 seven-layer AI governance stack."""

from src.core import pillar510_ai_governance_stack as p510


def test_constants():
    assert p510.PILLAR_NUMBER == 510
    assert p510.PILLAR_STATUS == "AI_GOVERNANCE_STACK_OPERATIONALIZED"
    assert p510.VERSION == "v15.7"
    assert len(p510.GOVERNANCE_LAYER_KEYS) == 7
    assert p510.APPROVAL_TIERS == ["routine", "sensitive", "critical", "forbidden"]


def test_governance_layer_registry_has_exact_seven_layer_overlay():
    registry = p510.governance_layer_registry()
    assert sorted(registry) == sorted(p510.GOVERNANCE_LAYER_KEYS)
    assert registry["CONSTITUTION"]["layer"] == "Constitution"
    assert registry["APPROVAL_GATES"]["layer"] == "Approval gates"
    assert registry["SAFETY_PROTOCOLS"]["layer"] == "Safety protocols"
    assert registry["AUDIT_TRAILS"]["layer"] == "Audit trails"
    assert registry["HUMAN_IN_THE_LOOP_VERIFICATION"]["layer"] == "Human-in-the-loop verification"
    assert registry["BRAND_SAFETY_CONTENT_MODERATION"]["layer"] == "Brand safety and content moderation"
    assert registry["RUNTIME_SANDBOXING"]["layer"] == "Runtime sandboxing"


def test_every_governance_layer_is_operationalized_with_artifact_and_approval_tier():
    registry = p510.governance_layer_registry()
    for entry in registry.values():
        assert entry["status"] == "OPERATIONALIZED"
        assert entry["artifacts"]
        assert entry["required_approval"] in p510.APPROVAL_TIERS
        assert entry["open_gaps"] == []


def test_critical_and_forbidden_approval_gates_are_not_autonomous():
    matrix = p510.approval_gate_matrix()
    assert matrix["critical"]["requires_human"] is True
    assert matrix["critical"]["requires_judgment_packet"] is True
    assert matrix["critical"]["requires_audit_trail"] is True
    assert matrix["forbidden"]["allowed_actor"] == "none autonomously"
    assert matrix["forbidden"]["requires_human"] is True


def test_action_classifier_routes_routine_sensitive_critical_and_forbidden_actions():
    assert p510.classify_action("run focused tests")["tier"] == "routine"
    assert p510.classify_action("publish public Substack claim")["tier"] == "sensitive"
    assert p510.classify_action("issue falsification declaration")["tier"] == "critical"
    assert p510.classify_action("expose credential in public log")["tier"] == "forbidden"


def test_public_claim_safety_filter_allows_bounded_claims():
    result = p510.public_claim_safety_filter(
        "Pillar 510 adds operational governance hardening with no physics score promotion."
    )
    assert result["verdict"] == "PASS_PUBLICATION_GATE"
    assert result["matched_patterns"] == []
    assert "docs/CLAIM_MASTER_BOARD.md" in result["required_references"]


def test_public_claim_safety_filter_blocks_overclaims():
    result = p510.public_claim_safety_filter(
        "This proves the universe and gives full non-perturbative 5D-KK closure."
    )
    assert result["verdict"] == "BLOCK_PUBLICATION"
    assert "proves the universe" in result["matched_patterns"]
    assert "full non-perturbative 5d-kk closure" in result["matched_patterns"]


def test_audit_trail_schema_has_required_machine_readable_fields():
    schema = p510.audit_trail_schema()
    assert schema["schema"] == "AI_STEWARD_ACTION_AUDIT_V1"
    assert schema["minimum_field_count"] >= 10
    for field in ("timestamp_utc", "actor", "risk_tier", "approval_status", "claim_boundary_verdict"):
        assert field in schema["required_fields"]
    assert "docs/mas_tracker.yml" in schema["machine_readable_surfaces"]


def test_governance_stack_certificate_verdict_and_no_physics_promotion():
    cert = p510.governance_stack_certificate()
    assert cert["layer_count"] == 7
    assert cert["all_layers_registered"] is True
    assert cert["all_layers_operational"] is True
    assert cert["all_layers_have_artifacts"] is True
    assert cert["critical_requires_human"] is True
    assert cert["forbidden_blocks_autonomy"] is True
    assert cert["public_gate_blocks_overclaim"] is True
    assert cert["audit_schema_complete"] is True
    assert cert["hardgate_score_delta"] == 0.0
    assert cert["physics_claim_delta"] == "NONE"
    assert cert["verdict"] == "AI_GOVERNANCE_STACK_OPERATIONALIZED__NO_PHYSICS_PROMOTION"


def test_pillar_report_contains_all_operational_boards():
    report = p510.pillar_report()
    assert report["pillar"] == 510
    assert report["status"] == p510.PILLAR_STATUS
    assert sorted(report["governance_layers"]) == sorted(p510.GOVERNANCE_LAYER_KEYS)
    assert sorted(report["approval_gates"]) == sorted(p510.APPROVAL_TIERS)
    assert report["certificate"]["verdict"] == "AI_GOVERNANCE_STACK_OPERATIONALIZED__NO_PHYSICS_PROMOTION"
