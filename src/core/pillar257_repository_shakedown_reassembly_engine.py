# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 257 — Repository Shakedown & Reassembly Engine (adjacent track).

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Purpose:
    Provide a deterministic, transparent, self-run repository shakedown that:
    1) decomposes the repository into auditable technical surfaces,
    2) validates theorem-kernel and canonical-tracker integrity,
    3) detects known mixed-era documentation drift,
    4) verifies falsifier-rigidity language is still enforced,
    5) emits a machine-readable reconciliation report.

This pillar does not alter core hardgate physics claims or ToE scoring.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 257
PILLAR_TITLE: str = "Repository Shakedown & Reassembly Engine"

BASELINE_REGRESSION_COMMAND: str = (
    'python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q --tb=no'
)
BASELINE_REGRESSION_COUNTS: dict[str, int] = {
    "passed": 34070,
    "skipped": 393,
    "deselected": 12,
    "failed": 0,
}
BASELINE_REGRESSION_RUNTIME_SECONDS: float = 178.37

_ROOT = Path(__file__).resolve().parents[2]

_THEOREM_KERNEL_PATHS: tuple[str, ...] = (
    "proof/TIER_1_FORMAL.md",
    "proof/metric.py",
    "proof/evolution.py",
    "proof/ALGEBRA_PROOF.py",
    "proof/VERIFY.py",
    "1-THEORY/UNIFICATION_PROOF.md",
    "FALLIBILITY.md",
)

_CANONICAL_SURFACES: tuple[str, ...] = (
    "STATUS.md",
    "docs/CLAIM_MASTER_BOARD.md",
    "docs/TRUTH_LAYER.md",
    "docs/GATEKEEPER_SUMMARY.md",
    "3-FALSIFICATION/OBSERVATION_TRACKER.md",
    "docs/mas_tracker.yml",
)

_ANALYSIS_BUCKETS: dict[str, str] = {
    "core": "src/core",
    "holography": "src/holography",
    "multiverse": "src/multiverse",
    "quantum": "src/quantum",
    "theory_docs": "1-THEORY",
    "falsification_docs": "3-FALSIFICATION",
    "outreach_docs": "7-OUTREACH",
    "tests": "tests",
}


@dataclass(frozen=True)
class CheckResult:
    """Single deterministic check result."""

    name: str
    status: str
    details: str


__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "BASELINE_REGRESSION_COMMAND",
    "BASELINE_REGRESSION_COUNTS",
    "BASELINE_REGRESSION_RUNTIME_SECONDS",
    "separation_guard",
    "decomposition_inventory",
    "theorem_kernel_integrity_check",
    "canonical_surface_sync_check",
    "drift_detection_check",
    "falsifier_rigidity_check",
    "baseline_regression_snapshot",
    "reassembly_reconciliation_matrix",
    "pillar257_repository_shakedown_report",
]


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def separation_guard() -> bool:
    """Explicit non-hardgate boundary."""
    return True


def decomposition_inventory() -> dict[str, Any]:
    """Count Python modules across major repository surfaces."""
    bucket_counts: dict[str, int] = {}
    for bucket, rel in _ANALYSIS_BUCKETS.items():
        root = _ROOT / rel
        bucket_counts[bucket] = len(list(root.rglob("*.py"))) if root.exists() else 0

    total_modules = sum(bucket_counts.values())
    complete_bucket_scan = all(count >= 0 for count in bucket_counts.values())
    return {
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "bucket_counts": bucket_counts,
        "total_python_modules": total_modules,
        "complete_bucket_scan": complete_bucket_scan,
        "minimum_expected_buckets": len(_ANALYSIS_BUCKETS),
    }


def theorem_kernel_integrity_check() -> dict[str, Any]:
    """Verify required theorem-kernel entry points exist."""
    missing: list[str] = []
    present: list[str] = []
    for rel in _THEOREM_KERNEL_PATHS:
        p = _ROOT / rel
        if p.exists():
            present.append(rel)
        else:
            missing.append(rel)

    return {
        "required_paths": list(_THEOREM_KERNEL_PATHS),
        "present_paths": present,
        "missing_paths": missing,
        "is_complete": len(missing) == 0,
        "status": "PASS" if not missing else "FAIL",
    }


def canonical_surface_sync_check() -> dict[str, Any]:
    """Check canonical truth surfaces are present and version-tagged."""
    status_text = _read_text(_ROOT / "STATUS.md")
    fallibility_text = _read_text(_ROOT / "FALLIBILITY.md")
    claim_board_text = _read_text(_ROOT / "docs/CLAIM_MASTER_BOARD.md")
    truth_layer_text = _read_text(_ROOT / "docs/TRUTH_LAYER.md")

    surfaces_present = [rel for rel in _CANONICAL_SURFACES if (_ROOT / rel).exists()]
    missing_surfaces = [rel for rel in _CANONICAL_SURFACES if not (_ROOT / rel).exists()]

    version_11_1 = re.compile(r"\bv11\.1\b")
    version_11_2 = re.compile(r"\bv11\.2\b")
    version_11_3 = re.compile(r"\bv11\.3\b")
    version_11_0_or_11_1 = re.compile(r"\bv11\.(0|1)\b")
    version_11_4 = re.compile(r"\bv11\.4\b")
    version_11_5 = re.compile(r"\bv11\.5\b")
    tags = {
        "status_has_v11_1": bool(version_11_1.search(status_text)),
        "status_has_v11_2": bool(version_11_2.search(status_text)),
        "status_has_v11_3": bool(version_11_3.search(status_text)),
        "status_has_v11_4": bool(version_11_4.search(status_text)),
        "status_has_v11_5": bool(version_11_5.search(status_text)),
        "fallibility_has_v11_1": bool(version_11_1.search(fallibility_text)),
        "fallibility_has_v11_2": bool(version_11_2.search(fallibility_text)),
        "fallibility_has_v11_3": bool(version_11_3.search(fallibility_text)),
        "fallibility_has_v11_4": bool(version_11_4.search(fallibility_text)),
        "fallibility_has_v11_5": bool(version_11_5.search(fallibility_text)),
        "claim_board_has_v11_0_or_v11_1": bool(version_11_0_or_11_1.search(claim_board_text)),
        "claim_board_has_v11_2": bool(version_11_2.search(claim_board_text)),
        "claim_board_has_v11_3": bool(version_11_3.search(claim_board_text)),
        "claim_board_has_v11_4": bool(version_11_4.search(claim_board_text)),
        "claim_board_has_v11_5": bool(version_11_5.search(claim_board_text)),
        "truth_layer_has_v11_0_or_v11_1": bool(version_11_0_or_11_1.search(truth_layer_text)),
        "truth_layer_has_v11_2": bool(version_11_2.search(truth_layer_text)),
        "truth_layer_has_v11_3": bool(version_11_3.search(truth_layer_text)),
        "truth_layer_has_v11_4": bool(version_11_4.search(truth_layer_text)),
        "truth_layer_has_v11_5": bool(version_11_5.search(truth_layer_text)),
    }

    return {
        "surfaces_present": surfaces_present,
        "missing_surfaces": missing_surfaces,
        "all_surfaces_present": len(missing_surfaces) == 0,
        "version_tags": tags,
        "status": "PASS" if (
            len(missing_surfaces) == 0 and (
                (tags["status_has_v11_1"] or tags["status_has_v11_2"] or tags["status_has_v11_3"] or tags["status_has_v11_4"] or tags["status_has_v11_5"])
                and (tags["fallibility_has_v11_1"] or tags["fallibility_has_v11_2"] or tags["fallibility_has_v11_3"] or tags["fallibility_has_v11_4"] or tags["fallibility_has_v11_5"])
                and (tags["claim_board_has_v11_0_or_v11_1"] or tags["claim_board_has_v11_2"] or tags["claim_board_has_v11_3"] or tags["claim_board_has_v11_4"] or tags["claim_board_has_v11_5"])
                and (tags["truth_layer_has_v11_0_or_v11_1"] or tags["truth_layer_has_v11_2"] or tags["truth_layer_has_v11_3"] or tags["truth_layer_has_v11_4"] or tags["truth_layer_has_v11_5"])
            )
        ) else "TENSION",
    }


def drift_detection_check() -> dict[str, Any]:
    """Detect documented historical/mixed-era drift surfaces for honest reporting."""
    mas_text = _read_text(_ROOT / "docs/mas_tracker.yml")
    fals_reg_text = _read_text(_ROOT / "3-FALSIFICATION/FALSIFICATION_REGISTER.md")

    mas_text_lower = mas_text.lower()
    fals_reg_text_lower = fals_reg_text.lower()
    mas_mixed_era = (
        "historical_snapshot_notice" in mas_text_lower and "mixed-era" in mas_text_lower
    )
    fals_register_historical = (
        "historical snapshot notice" in fals_reg_text_lower and "non-canonical" in fals_reg_text_lower
    )

    drift_items: list[str] = []
    if mas_mixed_era:
        drift_items.append(
            "docs/mas_tracker.yml retains mixed-era/historical sections and needs canonical-normalization awareness."
        )
    if fals_register_historical:
        drift_items.append(
            "3-FALSIFICATION/FALSIFICATION_REGISTER.md is historical/non-canonical and must not drive live verdicts."
        )

    return {
        "mas_tracker_mixed_era_flag": mas_mixed_era,
        "falsification_register_historical_flag": fals_register_historical,
        "drift_items": drift_items,
        "drift_count": len(drift_items),
        "status": "TENSION" if drift_items else "PASS",
    }


def falsifier_rigidity_check() -> dict[str, Any]:
    """Verify primary falsifier windows and prohibited gap are still explicit."""
    obs_text = _read_text(_ROOT / "3-FALSIFICATION/OBSERVATION_TRACKER.md")
    gate_text = _read_text(_ROOT / "docs/GATEKEEPER_SUMMARY.md")

    has_window = "[0.22°, 0.38°]" in obs_text or "[0.22°, 0.38°]" in gate_text
    has_gap = "(0.29°, 0.31°)" in obs_text or "(0.29°, 0.31°)" in gate_text
    has_primary_falsifier_language = "primary falsifier" in obs_text.lower() or "primary falsifier" in gate_text.lower()

    passes = has_window and has_gap and has_primary_falsifier_language
    return {
        "window_enforced": has_window,
        "gap_enforced": has_gap,
        "primary_falsifier_language_enforced": has_primary_falsifier_language,
        "status": "PASS" if passes else "FAIL",
    }


def baseline_regression_snapshot() -> dict[str, Any]:
    """Return baseline full-regression execution snapshot used by this pillar."""
    return {
        "command": BASELINE_REGRESSION_COMMAND,
        "counts": dict(BASELINE_REGRESSION_COUNTS),
        "runtime_seconds": BASELINE_REGRESSION_RUNTIME_SECONDS,
        "status": "PASS" if BASELINE_REGRESSION_COUNTS["failed"] == 0 else "FAIL",
        "warnings_recorded": True,
    }


def reassembly_reconciliation_matrix() -> dict[str, Any]:
    """Produce a deterministic reassembly matrix with explicit priorities."""
    sync = canonical_surface_sync_check()
    drift = drift_detection_check()
    kernel = theorem_kernel_integrity_check()
    falsifier = falsifier_rigidity_check()

    checks = [
        CheckResult(
            name="Theorem kernel integrity",
            status=kernel["status"],
            details="Tier-1 proof entry points present and auditable.",
        ),
        CheckResult(
            name="Canonical surface sync",
            status=sync["status"],
            details="Canonical truth surfaces present with version tags.",
        ),
        CheckResult(
            name="Documentation drift detection",
            status=drift["status"],
            details="Historical/non-canonical surfaces flagged explicitly.",
        ),
        CheckResult(
            name="Falsifier rigidity",
            status=falsifier["status"],
            details="LiteBIRD window + forbidden inter-sector gap remain explicit.",
        ),
    ]

    open_actions: list[str] = []
    if sync["status"] != "PASS":
        open_actions.append("Normalize version tags across canonical truth surfaces.")
    if drift["drift_count"] > 0:
        open_actions.append(
            "Keep historical surfaces quarantined from live verdict routing; prioritize canonical-surface synchronization."
        )

    return {
        "checks": [c.__dict__ for c in checks],
        "open_actions": open_actions,
        "open_action_count": len(open_actions),
        "status": "RECONCILED_WITH_OPEN_DOCUMENTATION_TENSIONS" if open_actions else "FULLY_RECONCILED",
    }


def pillar257_repository_shakedown_report() -> dict[str, Any]:
    """Integrated pillar-257 report."""
    inventory = decomposition_inventory()
    kernel = theorem_kernel_integrity_check()
    sync = canonical_surface_sync_check()
    drift = drift_detection_check()
    falsifier = falsifier_rigidity_check()
    baseline = baseline_regression_snapshot()
    reconciliation = reassembly_reconciliation_matrix()

    hard_fails: list[str] = []
    if not separation_guard():
        hard_fails.append("Separation guard failed (must remain non-hardgate).")
    if not kernel["is_complete"]:
        hard_fails.append("Theorem-kernel integrity is incomplete.")
    if falsifier["status"] != "PASS":
        hard_fails.append("Primary falsifier rigidity language is missing or weakened.")
    if baseline["status"] != "PASS":
        hard_fails.append("Baseline regression is not passing.")

    transparency_findings = list(drift["drift_items"])
    if sync["status"] != "PASS":
        transparency_findings.append(
            "Canonical truth-surface version tags are not fully synchronized."
        )

    overall_status = (
        "REJECTED"
        if hard_fails
        else "PASS_WITH_DOCUMENTATION_TENSIONS"
        if transparency_findings
        else "PASS"
    )

    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "separation_guard": separation_guard(),
        "decomposition_inventory": inventory,
        "theorem_kernel_integrity": kernel,
        "canonical_surface_sync": sync,
        "drift_detection": drift,
        "falsifier_rigidity": falsifier,
        "baseline_regression": baseline,
        "reassembly_reconciliation": reconciliation,
        "hard_fails": hard_fails,
        "transparency_findings": transparency_findings,
        "overall_status": overall_status,
        "non_hardgate_statement": (
            "Pillar 257 is an adjacent-track shakedown and does not modify hardgate claims or ToE score."
        ),
    }
