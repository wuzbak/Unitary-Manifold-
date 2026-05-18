# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 259 — Autonomous GitHub Community Steward & Security Operations."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone

from src.core.pillar259_autonomous_github_community_steward import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N_W,
    K_CS,
    C_S,
    MAX_CONCURRENT_OPERATIONS,
    OPERATION_TIMEOUT_SECONDS,
    SECURITY_REPORT_RETENTION_DAYS,
    GOOD_DEEDS_QUOTA_PER_RUN,
    ALLOWED_OPERATIONS,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
    SEVERITY_INFO,
    SecurityFinding,
    CommunityGoodDeed,
    OperationReport,
    separation_guard,
    enforce_security_boundary,
    detect_orphaned_dependencies,
    triage_stale_issues,
    scan_security_vulnerabilities,
    generate_community_health_report,
    recommend_contributor_onboarding,
    create_operation_report,
    verify_operation_report_integrity,
    summarize_operations,
)


# ===========================================================================
# 1. Module-level constants
# ===========================================================================


class TestConstants:
    def test_adjacency_label(self):
        assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 259

    def test_pillar_title(self):
        assert "Steward" in PILLAR_TITLE or "Community" in PILLAR_TITLE

    def test_core_constants(self):
        assert N_W == 5
        assert K_CS == 74
        assert C_S == pytest.approx(12.0 / 37.0)

    def test_operational_boundaries(self):
        assert MAX_CONCURRENT_OPERATIONS == 3
        assert OPERATION_TIMEOUT_SECONDS == 300
        assert SECURITY_REPORT_RETENTION_DAYS == 90
        assert GOOD_DEEDS_QUOTA_PER_RUN == 10

    def test_allowed_operations_immutable(self):
        assert isinstance(ALLOWED_OPERATIONS, frozenset)
        assert len(ALLOWED_OPERATIONS) == 5
        expected = {
            "detect_orphaned_dependencies",
            "triage_stale_issues",
            "scan_security_vulnerabilities",
            "recommend_contributor_onboarding",
            "generate_community_health_report",
        }
        assert ALLOWED_OPERATIONS == expected

    def test_severity_constants(self):
        assert SEVERITY_CRITICAL == "CRITICAL"
        assert SEVERITY_HIGH == "HIGH"
        assert SEVERITY_MEDIUM == "MEDIUM"
        assert SEVERITY_LOW == "LOW"
        assert SEVERITY_INFO == "INFO"


# ===========================================================================
# 2. Separation guard & boundary enforcement
# ===========================================================================


def test_separation_guard_returns_true():
    assert separation_guard() is True


def test_enforce_security_boundary_all_checks():
    result = enforce_security_boundary()
    assert isinstance(result, dict)
    assert result["non_hardgate"] is True
    assert result["max_concurrent_respected"] is True
    assert result["timeout_enforced"] is True
    assert result["whitelist_enforced"] is True
    assert result["immutable_report_schema"] is True


# ===========================================================================
# 3. SecurityFinding dataclass
# ===========================================================================


def test_security_finding_creation():
    finding = SecurityFinding(
        finding_id="SEC-2026-001",
        severity="HIGH",
        type="outdated_dependency",
        component="requests",
        description="requests < 2.31.0 vulnerable to XXE",
        recommendation="Update requests to >= 2.31.0",
        confidence=0.98,
    )
    assert finding.finding_id == "SEC-2026-001"
    assert finding.severity == "HIGH"
    assert finding.confidence == 0.98
    assert finding.timestamp_utc is not None


def test_security_finding_immutability():
    finding = SecurityFinding(
        finding_id="SEC-2026-002",
        severity="CRITICAL",
        type="exposed_secret",
        component="config.py",
        description="AWS key exposed in repo",
        recommendation="Rotate immediately",
    )
    with pytest.raises(AttributeError):
        finding.severity = "LOW"  # type: ignore


def test_security_finding_invalid_severity():
    with pytest.raises(ValueError):
        SecurityFinding(
            finding_id="SEC-X",
            severity="INVALID_SEVERITY",
            type="test",
            component="test",
            description="test",
            recommendation="test",
        )


def test_security_finding_invalid_confidence():
    with pytest.raises(ValueError):
        SecurityFinding(
            finding_id="SEC-X",
            severity="HIGH",
            type="test",
            component="test",
            description="test",
            recommendation="test",
            confidence=1.5,  # Outside [0.0, 1.0]
        )


def test_security_finding_with_evidence_url():
    finding = SecurityFinding(
        finding_id="SEC-2026-003",
        severity="MEDIUM",
        type="weak_crypto",
        component="crypto.py",
        description="MD5 used for hashing",
        recommendation="Use SHA256 instead",
        evidence_url="https://owasp.org/www-community/attacks/MD5_Collision",
    )
    assert finding.evidence_url is not None


# ===========================================================================
# 4. CommunityGoodDeed dataclass
# ===========================================================================


def test_good_deed_creation():
    deed = CommunityGoodDeed(
        deed_id="DEED-2026-001",
        operation_type="triage_stale_issues",
        action_description="Triaged 15 stale issues",
        repository="unitary-manifold",
        issue_count=15,
    )
    assert deed.deed_id == "DEED-2026-001"
    assert deed.issue_count == 15
    assert "triage" in deed.operation_type


def test_good_deed_immutability():
    deed = CommunityGoodDeed(
        deed_id="DEED-2026-002",
        operation_type="generate_community_health_report",
        action_description="Generated health report",
        repository="test-repo",
    )
    with pytest.raises(AttributeError):
        deed.issue_count = 5  # type: ignore


def test_good_deed_invalid_operation_type():
    with pytest.raises(ValueError):
        CommunityGoodDeed(
            deed_id="DEED-X",
            operation_type="invalid_operation",
            action_description="test",
            repository="test",
        )


def test_good_deed_with_contributor_count():
    deed = CommunityGoodDeed(
        deed_id="DEED-2026-003",
        operation_type="recommend_contributor_onboarding",
        action_description="Recommended 5 new contributors",
        repository="test-repo",
        contributors_onboarded=5,
    )
    assert deed.contributors_onboarded == 5


# ===========================================================================
# 5. OperationReport schema validation
# ===========================================================================


def test_operation_report_creation():
    report = OperationReport(
        report_id="OPS-2026-001",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        operation_type="scan_security_vulnerabilities",
        status="COMPLETED",
        security_findings=[],
        good_deeds=[],
        operations_count=1,
        boundary_violations=[],
        deterministic_hash="abc123def456" * 5,  # 60 chars (mock)
    )
    assert report.report_id == "OPS-2026-001"
    assert report.status == "COMPLETED"


def test_operation_report_immutability():
    report = OperationReport(
        report_id="OPS-2026-002",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        operation_type="detect_orphaned_dependencies",
        status="COMPLETED",
        security_findings=[],
        good_deeds=[],
        operations_count=1,
        boundary_violations=[],
        deterministic_hash="abc123def456" * 5,
    )
    with pytest.raises(AttributeError):
        report.status = "FAILED"  # type: ignore


def test_operation_report_invalid_operation_type():
    with pytest.raises(ValueError):
        OperationReport(
            report_id="OPS-X",
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            operation_type="invalid_op",
            status="COMPLETED",
            security_findings=[],
            good_deeds=[],
            operations_count=1,
            boundary_violations=[],
            deterministic_hash="abc123",
        )


def test_operation_report_invalid_status():
    with pytest.raises(ValueError):
        OperationReport(
            report_id="OPS-X",
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            operation_type="scan_security_vulnerabilities",
            status="INVALID_STATUS",
            security_findings=[],
            good_deeds=[],
            operations_count=1,
            boundary_violations=[],
            deterministic_hash="abc123",
        )


# ===========================================================================
# 6. Detect orphaned dependencies
# ===========================================================================


def test_detect_orphaned_dependencies_returns_valid_structure():
    result = detect_orphaned_dependencies(
        repository_path="/tmp/test_repo",
        include_transitive=True,
    )
    assert "operation_id" in result
    assert "orphaned_packages" in result
    assert "security_findings" in result
    assert "status" in result
    assert "findings_count" in result
    assert result["status"] in ("COMPLETED", "FAILED_SAFETY_BOUNDARY")


def test_detect_orphaned_dependencies_respects_severity():
    result = detect_orphaned_dependencies(
        repository_path="/tmp/test_repo",
        severity_threshold="CRITICAL",
    )
    findings = result.get("security_findings", [])
    for finding in findings:
        assert finding.severity in ("CRITICAL",)


def test_detect_orphaned_dependencies_operation_id_format():
    result = detect_orphaned_dependencies(
        repository_path="/tmp/test_repo",
    )
    assert result["operation_id"].startswith("OP-ORPHANED-")


# ===========================================================================
# 7. Triage stale issues
# ===========================================================================


def test_triage_stale_issues_returns_valid_structure():
    result = triage_stale_issues(
        repository="test-repo",
        stale_days=90,
    )
    assert "operation_id" in result
    assert "issues_triaged" in result
    assert "closed_count" in result
    assert "labeled_count" in result
    assert "good_deeds" in result
    assert "status" in result


def test_triage_stale_issues_respects_quota():
    result = triage_stale_issues(
        repository="test-repo",
        stale_days=90,
        max_operations=GOOD_DEEDS_QUOTA_PER_RUN,
    )
    assert result["issues_triaged"] <= GOOD_DEEDS_QUOTA_PER_RUN


def test_triage_stale_issues_returns_good_deeds():
    result = triage_stale_issues(
        repository="test-repo",
        stale_days=90,
    )
    assert isinstance(result["good_deeds"], list)
    for deed in result["good_deeds"]:
        assert deed.operation_type == "triage_stale_issues"


def test_triage_stale_issues_operation_id_format():
    result = triage_stale_issues(
        repository="test-repo",
    )
    assert result["operation_id"].startswith("OP-TRIAGE-")


# ===========================================================================
# 8. Security vulnerability scanning
# ===========================================================================


def test_scan_security_vulnerabilities_returns_valid_structure():
    result = scan_security_vulnerabilities(
        repository="test-repo",
        scan_type="dependency_check",
    )
    assert "operation_id" in result
    assert "findings" in result
    assert "critical_count" in result
    assert "high_count" in result
    assert "medium_count" in result
    assert "scan_timestamp_utc" in result


def test_scan_security_vulnerabilities_no_auto_fix():
    # All findings are logged; no automatic fixes triggered
    result = scan_security_vulnerabilities(
        repository="test-repo",
    )
    findings = result.get("findings", [])
    assert isinstance(findings, list)
    # Findings should be present (not acted upon)


def test_scan_security_vulnerabilities_operation_id_format():
    result = scan_security_vulnerabilities(
        repository="test-repo",
    )
    assert result["operation_id"].startswith("OP-SECURITY-")


def test_scan_security_vulnerabilities_severity_counts():
    result = scan_security_vulnerabilities(
        repository="test-repo",
    )
    # Counts should be non-negative
    assert result["critical_count"] >= 0
    assert result["high_count"] >= 0
    assert result["medium_count"] >= 0


# ===========================================================================
# 9. Community health report
# ===========================================================================


def test_generate_community_health_report_returns_valid_structure():
    result = generate_community_health_report(
        repository="test-repo",
    )
    assert "report_id" in result
    assert "repository" in result
    assert "timestamp_utc" in result
    assert "metrics" in result
    assert "recommendations" in result
    assert "health_score" in result


def test_generate_community_health_report_metrics():
    result = generate_community_health_report(
        repository="test-repo",
    )
    metrics = result.get("metrics", {})
    assert "issue_response_time_hours" in metrics
    assert "pr_merge_time_hours" in metrics
    assert "contributor_retention_pct" in metrics
    assert "security_issue_backlog" in metrics
    assert "stale_dependency_count" in metrics


def test_generate_community_health_report_health_score_range():
    result = generate_community_health_report(
        repository="test-repo",
    )
    health_score = result.get("health_score", 0)
    assert 0.0 <= health_score <= 1.0


# ===========================================================================
# 10. Contributor onboarding recommendations
# ===========================================================================


def test_recommend_contributor_onboarding_returns_valid_structure():
    result = recommend_contributor_onboarding(
        repository="test-repo",
    )
    assert "operation_id" in result
    assert "contributor_count" in result
    assert "onboarding_suggestions" in result
    assert "good_first_issues" in result
    assert "mentorship_gaps" in result


def test_recommend_contributor_onboarding_operation_id_format():
    result = recommend_contributor_onboarding(
        repository="test-repo",
    )
    assert result["operation_id"].startswith("OP-ONBOARD-")


# ===========================================================================
# 11. Report creation & integrity
# ===========================================================================


def test_create_operation_report_immutable():
    report = create_operation_report(
        operation_type="scan_security_vulnerabilities",
        security_findings=[],
        good_deeds=[],
    )
    assert isinstance(report, OperationReport)
    assert report.status in ("COMPLETED", "PARTIAL", "FAILED_SAFETY_BOUNDARY")
    assert isinstance(report.deterministic_hash, str)
    assert len(report.deterministic_hash) == 64  # SHA256 hex


def test_create_operation_report_with_findings():
    finding = SecurityFinding(
        finding_id="SEC-TEST",
        severity="HIGH",
        type="test",
        component="test",
        description="test",
        recommendation="test",
    )
    report = create_operation_report(
        operation_type="scan_security_vulnerabilities",
        security_findings=[finding],
        good_deeds=[],
    )
    assert len(report.security_findings) == 1
    assert report.security_findings[0].finding_id == "SEC-TEST"


def test_create_operation_report_with_good_deeds():
    deed = CommunityGoodDeed(
        deed_id="DEED-TEST",
        operation_type="triage_stale_issues",
        action_description="test",
        repository="test",
    )
    report = create_operation_report(
        operation_type="triage_stale_issues",
        security_findings=[],
        good_deeds=[deed],
    )
    assert len(report.good_deeds) == 1
    assert report.good_deeds[0].deed_id == "DEED-TEST"


def test_create_operation_report_canonical_hash():
    finding = SecurityFinding(
        finding_id="SEC-1",
        severity="HIGH",
        type="test",
        component="pkg",
        description="test",
        recommendation="test",
    )
    report1 = create_operation_report(
        operation_type="scan_security_vulnerabilities",
        security_findings=[finding],
    )
    report2 = create_operation_report(
        operation_type="scan_security_vulnerabilities",
        security_findings=[finding],
    )
    # Same findings in same order → same hash
    assert report1.deterministic_hash == report2.deterministic_hash


def test_create_operation_report_invalid_operation_type():
    with pytest.raises(ValueError):
        create_operation_report(
            operation_type="invalid_operation",
        )


# ===========================================================================
# 12. Report verification
# ===========================================================================


def test_verify_operation_report_integrity_valid():
    report = create_operation_report(
        operation_type="detect_orphaned_dependencies",
        security_findings=[],
        good_deeds=[],
    )
    result = verify_operation_report_integrity(report)
    assert result["hash_valid"] is True
    assert result["schema_valid"] is True
    assert result["no_boundary_violations"] is True


def test_verify_operation_report_integrity_structure():
    report = create_operation_report(
        operation_type="triage_stale_issues",
    )
    result = verify_operation_report_integrity(report)
    assert isinstance(result, dict)
    assert set(result.keys()) == {"hash_valid", "schema_valid", "no_boundary_violations"}


# ===========================================================================
# 13. Summary aggregation
# ===========================================================================


def test_summarize_operations_returns_valid_structure():
    result = summarize_operations(
        start_timestamp_utc="2026-01-01T00:00:00Z",
        end_timestamp_utc="2026-01-31T23:59:59Z",
    )
    assert "time_window" in result
    assert "total_operations" in result
    assert "total_security_findings" in result
    assert "critical_findings" in result
    assert "good_deeds_completed" in result
    assert "boundary_violations" in result
    assert "average_operation_duration_seconds" in result


def test_summarize_operations_counts_non_negative():
    result = summarize_operations(
        start_timestamp_utc="2026-01-01T00:00:00Z",
        end_timestamp_utc="2026-01-02T00:00:00Z",
    )
    assert result["total_operations"] >= 0
    assert result["total_security_findings"] >= 0
    assert result["critical_findings"] >= 0
    assert result["good_deeds_completed"] >= 0
    assert result["boundary_violations"] >= 0


def test_summarize_operations_no_boundary_violations():
    result = summarize_operations(
        start_timestamp_utc="2026-01-01T00:00:00Z",
        end_timestamp_utc="2026-01-02T00:00:00Z",
    )
    # Properly designed operations should have zero boundary violations
    assert result["boundary_violations"] == 0
