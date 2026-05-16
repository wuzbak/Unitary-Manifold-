# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Lane 2 — Closure quality gate.

Validates that every claim listed as DERIVED in the closure quality log
has a corresponding derivation artifact in src/ and a test in tests/.

The gate enforces the separation of derivation from narrative:
no promotion is accepted without (a) an artifact, (b) a test, and
(c) an honest promotion_grounds statement.

Rules (per docs/CLAIM_LABEL_STANDARD.md):
  - DERIVED claims require zero free parameters and a checkable proof.
  - Promotion grounds must not reference narrative pressure.
  - Every DERIVED claim must exist as a cert module in src/core/ or equivalent.

Usage:
    python src/core/closure_quality_gate.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "docs" / "closure_quality_gate.yml"

__all__ = [
    "GATE_PATH",
    "load_closure_gate",
    "validate_gate_integrity",
    "audit_artifact_presence",
    "full_audit",
]

NARRATIVE_PRESSURE_PHRASES = [
    "narrative pressure",
    "score inflation",
    "adjacent track",
    "without derivation",
    "because it looks like",
    "community expectation",
]


def _load_yaml(path: Path) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        raise ImportError("PyYAML required: pip install pyyaml")


def load_closure_gate() -> Dict[str, Any]:
    """Load docs/closure_quality_gate.yml."""
    if not GATE_PATH.exists():
        raise FileNotFoundError(
            f"Closure quality gate not found at {GATE_PATH}"
        )
    data = _load_yaml(GATE_PATH)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid closure gate format at {GATE_PATH}")
    return data


def validate_gate_integrity(gate: Dict[str, Any] | None = None) -> List[str]:
    """Validate structural integrity of the closure quality gate log.

    Returns list of violation strings; empty = PASS.
    """
    if gate is None:
        gate = load_closure_gate()

    violations: List[str] = []
    promotions = gate.get("promotions", [])

    if not promotions:
        violations.append("Closure gate contains no promotions.")
        return violations

    seen_ids: set[str] = set()
    for promo in promotions:
        pid = promo.get("id", "<no-id>")

        if pid in seen_ids:
            violations.append(f"Duplicate promotion ID: {pid}")
        seen_ids.add(pid)

        # Required fields
        for field in ("id", "parameter", "from_label", "to_label", "date",
                      "derivation_artifacts", "test_artifacts", "promotion_grounds",
                      "gatekeeper"):
            if field not in promo:
                violations.append(f"[{pid}] Missing field: {field}")

        # Artifacts must be non-empty lists
        for list_field in ("derivation_artifacts", "test_artifacts"):
            val = promo.get(list_field, [])
            if not isinstance(val, list) or len(val) == 0:
                violations.append(f"[{pid}] {list_field} must be a non-empty list")

        # Promotion grounds must not be narrative
        grounds = str(promo.get("promotion_grounds", "")).lower()
        for phrase in NARRATIVE_PRESSURE_PHRASES:
            if phrase in grounds:
                violations.append(
                    f"[{pid}] promotion_grounds contains prohibited phrase: '{phrase}'"
                )

        # Gatekeeper must be PASS
        gk = promo.get("gatekeeper", "")
        if gk != "PASS":
            violations.append(
                f"[{pid}] gatekeeper must be 'PASS'; got '{gk}'"
            )

        # to_label must be DERIVED or ALGEBRAIC
        to_label = promo.get("to_label", "")
        if to_label not in ("DERIVED", "ALGEBRAIC"):
            violations.append(
                f"[{pid}] to_label '{to_label}' is not a promotion target "
                "(only DERIVED or ALGEBRAIC are valid promotion targets)"
            )

    # Governance block
    gov = gate.get("governance", {})
    if not gov:
        violations.append("Closure gate missing governance block.")
    else:
        if "prohibition" not in gov:
            violations.append("governance block missing 'prohibition' field")

    return violations


def audit_artifact_presence(gate: Dict[str, Any] | None = None) -> List[str]:
    """Check that every derivation artifact cited in the gate actually exists on disk.

    Returns list of missing artifact strings; empty = all present.
    """
    if gate is None:
        gate = load_closure_gate()

    missing: List[str] = []
    for promo in gate.get("promotions", []):
        pid = promo.get("id", "<no-id>")
        for artifact in promo.get("derivation_artifacts", []):
            path = ROOT / artifact
            if not path.exists():
                missing.append(f"[{pid}] Missing derivation artifact: {artifact}")
        for artifact in promo.get("test_artifacts", []):
            path = ROOT / artifact
            if not path.exists():
                missing.append(f"[{pid}] Missing test artifact: {artifact}")
    return missing


def full_audit() -> Dict[str, Any]:
    """Run complete closure quality audit: integrity + artifact presence.

    Returns dict with:
        integrity_violations: list of str
        missing_artifacts: list of str
        pass: bool
    """
    gate = load_closure_gate()
    integrity = validate_gate_integrity(gate)
    missing = audit_artifact_presence(gate)
    return {
        "integrity_violations": integrity,
        "missing_artifacts": missing,
        "pass": not integrity and not missing,
    }


if __name__ == "__main__":
    try:
        result = full_audit()
    except (FileNotFoundError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if result["integrity_violations"]:
        print("Integrity violations:", file=sys.stderr)
        for v in result["integrity_violations"]:
            print(f"  - {v}", file=sys.stderr)

    if result["missing_artifacts"]:
        print("Missing artifacts (referenced in gate but not on disk):", file=sys.stderr)
        for v in result["missing_artifacts"]:
            print(f"  - {v}", file=sys.stderr)

    if result["pass"]:
        gate = load_closure_gate()
        n = len(gate.get("promotions", []))
        print(f"Closure quality gate PASS — {n} promotions logged, all artifacts present.")
        sys.exit(0)
    else:
        sys.exit(1)
