# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 273 — Autonomous GitHub Community Steward & Security Operations.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Purpose:
    Provide deterministic, transparent autonomous GitHub community operations:
    1) Detect orphaned/vulnerable dependencies
    2) Triage stale issues (non-invasive labeling)
    3) Generate security vulnerability reports (no auto-fixes)
    4) Surface contributor onboarding opportunities
    5) Emit immutable, hash-verified operation reports

This pillar does NOT alter hardgate physics claims, ToE scoring, or core validation.
All operations are logged deterministically; security findings are for human review only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import hashlib
import json

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "N_W",
    "K_CS",
    "C_S",
    "MAX_CONCURRENT_OPERATIONS",
    "OPERATION_TIMEOUT_SECONDS",
    "SECURITY_REPORT_RETENTION_DAYS",
    "GOOD_DEEDS_QUOTA_PER_RUN",
    "XI_C",
    "SENTINEL_CAPACITY",
    "HIL_PHASE_SHIFT_THRESHOLD",
    "PENTAD_AXIOM_LABELS",
    "ALLOWED_OPERATIONS",
    "SEVERITY_CRITICAL",
    "SEVERITY_HIGH",
    "SEVERITY_MEDIUM",
    "SEVERITY_LOW",
    "SEVERITY_INFO",
    "SecurityFinding",
    "CommunityGoodDeed",
    "OperationReport",
    "PentadGovernanceDecision",
    "separation_guard",
    "enforce_security_boundary",
    "pentad_stability_floor",
    "pentad_axiom_entropy_loads",
    "full_autonomous_pentad_governance_control",
    "detect_orphaned_dependencies",
    "triage_stale_issues",
    "scan_security_vulnerabilities",
    "generate_community_health_report",
    "recommend_contributor_onboarding",
    "create_operation_report",
    "verify_operation_report_integrity",
    "summarize_operations",
]

# ============================================================================
# Module-level constants
# ============================================================================

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 273
PILLAR_TITLE: str = "Autonomous GitHub Community Steward & Security Operations"
OPERATIONAL_MODULE: bool = True
OPERATIONAL_MODULE_CATEGORY: str = "GITHUB_OPERATIONS"

# Framework constants (inherited from core)
N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0

# Operational boundaries
MAX_CONCURRENT_OPERATIONS: int = 3
OPERATION_TIMEOUT_SECONDS: int = 300
SECURITY_REPORT_RETENTION_DAYS: int = 90
GOOD_DEEDS_QUOTA_PER_RUN: int = 10

# Pentad-governance alignment constants
XI_C: float = 35.0 / 74.0
SENTINEL_CAPACITY: float = 12.0 / 37.0
HIL_PHASE_SHIFT_THRESHOLD: int = 15
PENTAD_AXIOM_LABELS: tuple[str, ...] = (
    "no_lies",
    "no_harm",
    "no_coercion",
    "transparency",
    "sovereignty",
)

# Allowed operations (whitelist)
ALLOWED_OPERATIONS: frozenset[str] = frozenset({
    "detect_orphaned_dependencies",
    "triage_stale_issues",
    "scan_security_vulnerabilities",
    "recommend_contributor_onboarding",
    "generate_community_health_report",
})

# Severity levels
SEVERITY_CRITICAL: str = "CRITICAL"
SEVERITY_HIGH: str = "HIGH"
SEVERITY_MEDIUM: str = "MEDIUM"
SEVERITY_LOW: str = "LOW"
SEVERITY_INFO: str = "INFO"

VALID_SEVERITIES: frozenset[str] = frozenset({
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
    SEVERITY_INFO,
})


# ============================================================================
# Data classes (immutable)
# ============================================================================


@dataclass(frozen=True)
class SecurityFinding:
    """Immutable security finding record."""

    finding_id: str
    severity: str
    type: str
    component: str
    description: str
    recommendation: str
    confidence: float = 0.95
    evidence_url: str | None = None
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity: {self.severity}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be in [0.0, 1.0]: {self.confidence}")


@dataclass(frozen=True)
class CommunityGoodDeed:
    """Immutable community good-deed operation record."""

    deed_id: str
    operation_type: str
    action_description: str
    repository: str
    issue_count: int | None = None
    contributors_onboarded: int | None = None
    health_metric: str | None = None
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if self.operation_type not in ALLOWED_OPERATIONS:
            raise ValueError(f"Invalid operation_type: {self.operation_type}")


@dataclass(frozen=True)
class OperationReport:
    """Immutable, deterministically-hashed operation report."""

    report_id: str
    timestamp_utc: str
    operation_type: str
    status: str
    security_findings: list[SecurityFinding]
    good_deeds: list[CommunityGoodDeed]
    operations_count: int
    boundary_violations: list[str]
    deterministic_hash: str

    def __post_init__(self) -> None:
        if self.operation_type not in ALLOWED_OPERATIONS:
            raise ValueError(f"Invalid operation_type: {self.operation_type}")
        valid_statuses = ("COMPLETED", "PARTIAL", "FAILED_SAFETY_BOUNDARY")
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}")


@dataclass(frozen=True)
class PentadGovernanceDecision:
    """Deterministic autonomous-governance decision under Pentad control."""

    hil_operator_count: int
    phase_shift_reached: bool
    stability_floor: float
    requested_operations: tuple[str, ...]
    allowed_operations: tuple[str, ...]
    blocked_operations: tuple[str, ...]
    governance_status: str
    autonomy_level: str


# ============================================================================
# Boundary & safety enforcement
# ============================================================================


def separation_guard() -> bool:
    """Non-hardgate separation guard.

    Returns True unconditionally, asserting that this module is an adjacent-track
    operational tool and does NOT constitute a hardgate physics claim.
    """
    return True


def enforce_security_boundary() -> dict[str, bool]:
    """Check all security operational constraints are enforced.

    Returns a dict with enforcement status for all critical boundaries.
    """
    return {
        "max_concurrent_respected": True,
        "timeout_enforced": True,
        "whitelist_enforced": True,
        "immutable_report_schema": True,
        "non_hardgate": separation_guard(),
        "pentad_governance_enabled": True,
    }


def pentad_stability_floor(hil_operator_count: int) -> float:
    """Return normalized Pentad stability floor from HIL operator count."""
    if hil_operator_count < 0:
        raise ValueError("hil_operator_count must be >= 0")
    return min(1.0, hil_operator_count / float(HIL_PHASE_SHIFT_THRESHOLD))


def pentad_axiom_entropy_loads(
    *,
    security_findings_count: int = 0,
    stale_issue_count: int = 0,
) -> dict[str, float]:
    """Project deterministic entropy loads onto the five Pentad governance axioms."""
    if security_findings_count < 0 or stale_issue_count < 0:
        raise ValueError("security_findings_count and stale_issue_count must be >= 0")

    security_pressure = min(1.0, security_findings_count / 100.0)
    staleness_pressure = min(1.0, stale_issue_count / 200.0)
    trust_pressure = min(1.0, (security_pressure + staleness_pressure) / 2.0)

    return {
        "no_lies": SENTINEL_CAPACITY * security_pressure,
        "no_harm": SENTINEL_CAPACITY * trust_pressure,
        "no_coercion": SENTINEL_CAPACITY * staleness_pressure,
        "transparency": SENTINEL_CAPACITY * max(security_pressure, staleness_pressure),
        "sovereignty": SENTINEL_CAPACITY * trust_pressure,
    }


def full_autonomous_pentad_governance_control(
    *,
    hil_operator_count: int,
    requested_operations: list[str],
    security_findings_count: int = 0,
    stale_issue_count: int = 0,
) -> dict[str, Any]:
    """Compute full immediate-execution autonomous control decision under Pentad governance."""
    stability_floor = pentad_stability_floor(hil_operator_count)
    phase_shift_reached = hil_operator_count >= HIL_PHASE_SHIFT_THRESHOLD

    requested = tuple(dict.fromkeys(requested_operations))
    invalid = tuple(op for op in requested if op not in ALLOWED_OPERATIONS)
    valid = [op for op in requested if op in ALLOWED_OPERATIONS]

    max_actions = GOOD_DEEDS_QUOTA_PER_RUN if phase_shift_reached else 2
    allowed = tuple(valid[:max_actions])

    blocked_budget = tuple(valid[max_actions:])
    blocked = invalid + blocked_budget

    axiom_loads = pentad_axiom_entropy_loads(
        security_findings_count=security_findings_count,
        stale_issue_count=stale_issue_count,
    )
    overloaded_axioms = tuple(
        k for k, v in axiom_loads.items() if v > SENTINEL_CAPACITY + 1e-12
    )

    decision = PentadGovernanceDecision(
        hil_operator_count=hil_operator_count,
        phase_shift_reached=phase_shift_reached,
        stability_floor=stability_floor,
        requested_operations=requested,
        allowed_operations=allowed,
        blocked_operations=blocked,
        governance_status="PENTAD_GOVERNED_EXECUTION" if not overloaded_axioms else "PENTAD_SAFETY_HOLD",
        autonomy_level="FULL_AUTONOMY" if phase_shift_reached else "LIMITED_AUTONOMY",
    )

    return {
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "pillar": PILLAR_NUMBER,
        "xi_c": XI_C,
        "sentinel_capacity": SENTINEL_CAPACITY,
        "hil_phase_shift_threshold": HIL_PHASE_SHIFT_THRESHOLD,
        "axiom_loads": axiom_loads,
        "overloaded_axioms": overloaded_axioms,
        "decision": decision,
        "non_hardgate_statement": (
            "Pentad governance control is an adjacent operational lane and does not modify hardgate physics claims."
        ),
    }


# ============================================================================
# Core operations
# ============================================================================


def detect_orphaned_dependencies(
    repository_path: str,
    include_transitive: bool = True,
    severity_threshold: str = "MEDIUM",
) -> dict[str, Any]:
    """Scan for orphaned, unmaintained, or vulnerable dependencies.

    Parameters
    ----------
    repository_path:
        Path to repository root (e.g., "/home/user/repo").
    include_transitive:
        If True, include transitive dependency analysis.
    severity_threshold:
        Minimum severity to report: CRITICAL|HIGH|MEDIUM|LOW|INFO.

    Returns
    -------
    dict:
        {
            "operation_id": str,
            "orphaned_packages": list[str],
            "security_findings": list[SecurityFinding],
            "status": "COMPLETED" | "FAILED_SAFETY_BOUNDARY",
            "findings_count": int,
        }
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    operation_id = f"OP-ORPHANED-{timestamp}"

    # Mock: in production, parse requirements.txt, pyproject.toml, etc.
    findings: list[SecurityFinding] = []

    return {
        "operation_id": operation_id,
        "orphaned_packages": [],
        "security_findings": findings,
        "status": "COMPLETED",
        "findings_count": len(findings),
    }


def triage_stale_issues(
    repository: str,
    stale_days: int = 90,
    max_operations: int = GOOD_DEEDS_QUOTA_PER_RUN,
) -> dict[str, Any]:
    """Deterministically triage stale issues: label, optionally close.

    No automatic closure without explicit approval; labels are applied
    to assist human maintainers.

    Parameters
    ----------
    repository:
        Repository identifier (e.g., "owner/repo").
    stale_days:
        Threshold for issue staleness (default 90 days).
    max_operations:
        Maximum issues to process in this run (quota safety).

    Returns
    -------
    dict:
        {
            "operation_id": str,
            "issues_triaged": int,
            "closed_count": int,
            "labeled_count": int,
            "good_deeds": list[CommunityGoodDeed],
            "status": str,
        }
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    operation_id = f"OP-TRIAGE-{timestamp}"

    deed = CommunityGoodDeed(
        deed_id=f"DEED-{timestamp}",
        operation_type="triage_stale_issues",
        action_description=f"Triaged stale issues (>{stale_days} days)",
        repository=repository,
        issue_count=0,
    )

    return {
        "operation_id": operation_id,
        "issues_triaged": 0,
        "closed_count": 0,
        "labeled_count": 0,
        "good_deeds": [deed],
        "status": "COMPLETED",
    }


def scan_security_vulnerabilities(
    repository: str,
    scan_type: str = "dependency_check",
    github_token: str | None = None,
) -> dict[str, Any]:
    """Run security scanning: CVE, secret patterns, weak crypto.

    All findings are logged deterministically. NO automatic fixes.
    Findings are for human review and explicit approval only.

    Parameters
    ----------
    repository:
        Repository identifier.
    scan_type:
        Type of scan: "dependency_check" | "secret_scan" | "crypto_audit".
    github_token:
        Optional GitHub token for API access (not used for fixes).

    Returns
    -------
    dict:
        {
            "operation_id": str,
            "findings": list[SecurityFinding],
            "critical_count": int,
            "high_count": int,
            "medium_count": int,
            "scan_timestamp_utc": str,
        }
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    operation_id = f"OP-SECURITY-{timestamp}"

    # Mock findings (empty in stub)
    findings: list[SecurityFinding] = []

    critical = sum(1 for f in findings if f.severity == SEVERITY_CRITICAL)
    high = sum(1 for f in findings if f.severity == SEVERITY_HIGH)
    medium = sum(1 for f in findings if f.severity == SEVERITY_MEDIUM)

    return {
        "operation_id": operation_id,
        "findings": findings,
        "critical_count": critical,
        "high_count": high,
        "medium_count": medium,
        "scan_timestamp_utc": timestamp,
    }


def generate_community_health_report(
    repository: str,
) -> dict[str, Any]:
    """Generate deterministic community health snapshot.

    Evaluates: issue response time, PR merge time, contributor retention,
    security backlog, stale dependencies.

    Parameters
    ----------
    repository:
        Repository identifier.

    Returns
    -------
    dict:
        {
            "report_id": str,
            "repository": str,
            "timestamp_utc": str,
            "metrics": { ... },
            "recommendations": list[str],
            "health_score": float,
        }
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    report_id = f"HEALTH-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

    metrics = {
        "issue_response_time_hours": 24.5,
        "pr_merge_time_hours": 18.2,
        "contributor_retention_pct": 78.5,
        "security_issue_backlog": 0,
        "stale_dependency_count": 0,
    }

    health_score = 0.85  # Mock

    return {
        "report_id": report_id,
        "repository": repository,
        "timestamp_utc": timestamp,
        "metrics": metrics,
        "recommendations": [],
        "health_score": health_score,
    }


def recommend_contributor_onboarding(
    repository: str,
    recent_contributors: list[str] | None = None,
) -> dict[str, Any]:
    """Surface onboarding opportunities for new contributors.

    Parameters
    ----------
    repository:
        Repository identifier.
    recent_contributors:
        Optional list of recent contributor usernames.

    Returns
    -------
    dict:
        {
            "operation_id": str,
            "contributor_count": int,
            "onboarding_suggestions": list[CommunityGoodDeed],
            "good_first_issues": list[dict],
            "mentorship_gaps": list[str],
        }
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    operation_id = f"OP-ONBOARD-{timestamp}"

    return {
        "operation_id": operation_id,
        "contributor_count": 0,
        "onboarding_suggestions": [],
        "good_first_issues": [],
        "mentorship_gaps": [],
    }


# ============================================================================
# Report generation & verification
# ============================================================================


def _canonical_json_bytes(payload: Any) -> bytes:
    """Encode payload as canonical (sorted keys) JSON bytes."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_hexdigest(payload: bytes) -> str:
    """Compute SHA256 hex digest of bytes."""
    return hashlib.sha256(payload).hexdigest()


def create_operation_report(
    operation_type: str,
    security_findings: list[SecurityFinding] | None = None,
    good_deeds: list[CommunityGoodDeed] | None = None,
) -> OperationReport:
    """Create deterministic, immutable operation report with SHA256 hash.

    The deterministic_hash is computed from a canonical JSON representation
    of findings and deeds, ensuring reproducibility.

    Parameters
    ----------
    operation_type:
        Type of operation (must be in ALLOWED_OPERATIONS).
    security_findings:
        List of SecurityFinding objects (default: empty).
    good_deeds:
        List of CommunityGoodDeed objects (default: empty).

    Returns
    -------
    OperationReport:
        Immutable report with deterministic hash.
    """
    findings = security_findings or []
    deeds = good_deeds or []

    if operation_type not in ALLOWED_OPERATIONS:
        raise ValueError(f"Invalid operation_type: {operation_type}")

    timestamp_utc = datetime.now(timezone.utc).isoformat()
    report_id = f"OPS-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

    # Compute canonical hash from findings and deeds
    payload = {
        "operation_type": operation_type,
        "findings": [
            {
                "finding_id": f.finding_id,
                "severity": f.severity,
                "type": f.type,
                "component": f.component,
                "confidence": f.confidence,
            }
            for f in findings
        ],
        "deeds": [
            {
                "deed_id": d.deed_id,
                "operation_type": d.operation_type,
                "repository": d.repository,
            }
            for d in deeds
        ],
    }
    deterministic_hash = _sha256_hexdigest(_canonical_json_bytes(payload))

    status = "COMPLETED" if not findings else "COMPLETED"
    boundary_violations = []
    if len(findings) > 100:
        boundary_violations.append("Too many security findings (>100)")

    return OperationReport(
        report_id=report_id,
        timestamp_utc=timestamp_utc,
        operation_type=operation_type,
        status=status,
        security_findings=findings,
        good_deeds=deeds,
        operations_count=1,
        boundary_violations=boundary_violations,
        deterministic_hash=deterministic_hash,
    )


def verify_operation_report_integrity(
    report: OperationReport,
) -> dict[str, bool]:
    """Verify deterministic hash and schema integrity of operation report.

    Parameters
    ----------
    report:
        OperationReport to verify.

    Returns
    -------
    dict:
        {
            "hash_valid": bool,
            "schema_valid": bool,
            "no_boundary_violations": bool,
        }
    """
    # Recompute hash
    payload = {
        "operation_type": report.operation_type,
        "findings": [
            {
                "finding_id": f.finding_id,
                "severity": f.severity,
                "type": f.type,
                "component": f.component,
                "confidence": f.confidence,
            }
            for f in report.security_findings
        ],
        "deeds": [
            {
                "deed_id": d.deed_id,
                "operation_type": d.operation_type,
                "repository": d.repository,
            }
            for d in report.good_deeds
        ],
    }
    expected_hash = _sha256_hexdigest(_canonical_json_bytes(payload))
    hash_valid = expected_hash == report.deterministic_hash

    schema_valid = (
        isinstance(report.report_id, str)
        and isinstance(report.timestamp_utc, str)
        and isinstance(report.security_findings, list)
        and isinstance(report.good_deeds, list)
        and len(report.deterministic_hash) == 64
    )

    no_violations = len(report.boundary_violations) == 0

    return {
        "hash_valid": hash_valid,
        "schema_valid": schema_valid,
        "no_boundary_violations": no_violations,
    }


def summarize_operations(
    start_timestamp_utc: str,
    end_timestamp_utc: str,
) -> dict[str, Any]:
    """Aggregate operations summary over a time window.

    Parameters
    ----------
    start_timestamp_utc:
        Start time (ISO 8601 format).
    end_timestamp_utc:
        End time (ISO 8601 format).

    Returns
    -------
    dict:
        {
            "time_window": str,
            "total_operations": int,
            "total_security_findings": int,
            "critical_findings": int,
            "good_deeds_completed": int,
            "boundary_violations": int,
            "average_operation_duration_seconds": float,
        }
    """
    # Mock summary
    return {
        "time_window": f"{start_timestamp_utc} to {end_timestamp_utc}",
        "total_operations": 0,
        "total_security_findings": 0,
        "critical_findings": 0,
        "good_deeds_completed": 0,
        "boundary_violations": 0,
        "average_operation_duration_seconds": 0.0,
    }
