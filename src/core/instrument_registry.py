# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Lane 1 — Measurement confrontation: Instrument Registry.

Machine-readable binding of every named prediction to its decisive instrument(s),
with strict pass/fail semantics.  Provides:

  - load_instrument_registry()  — parse docs/falsification/instrument_registry.yml
  - check_all_statuses()        — return per-prediction status summary
  - has_high_tension_or_falsified() — sentinel for immediate escalation
  - validate_registry_integrity()   — structural validator for CI

The registry is the authoritative source; this module only reads it.
No prediction promotion happens here — that is Lane 2 (closure_quality_gate.py).

Usage:
    python src/core/instrument_registry.py

See also:
    docs/falsification/instrument_registry.yml
    3-FALSIFICATION/OBSERVATION_TRACKER.md
    src/core/falsification_check.py  (LiteBIRD-specific self-executing check)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "falsification" / "instrument_registry.yml"

REQUIRED_PREDICTION_FIELDS = {"id", "description", "pass_condition", "fail_condition",
                               "current_status", "instruments"}
VALID_STATUSES = {"PENDING", "CONSISTENT", "HIGH_TENSION", "FALSIFIED"}

__all__ = [
    "REGISTRY_PATH",
    "load_instrument_registry",
    "check_all_statuses",
    "has_high_tension_or_falsified",
    "validate_registry_integrity",
]


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML file, preferring PyYAML; fall back to manual parse for CI."""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        pass
    # Minimal fallback: return raw text wrapped so callers know it's unparsed
    raise ImportError(
        "PyYAML is required to parse instrument_registry.yml. "
        "Install with: pip install pyyaml"
    )


def load_instrument_registry() -> Dict[str, Any]:
    """Load and return the instrument registry YAML.

    Returns
    -------
    dict
        Parsed registry with keys: version, date, predictions, governance.

    Raises
    ------
    FileNotFoundError
        If the registry file does not exist.
    ImportError
        If PyYAML is not installed.
    """
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(
            f"Instrument registry not found at {REGISTRY_PATH}. "
            "Run from repository root."
        )
    data = _load_yaml(REGISTRY_PATH)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid registry format at {REGISTRY_PATH}")
    return data


def validate_registry_integrity(registry: Dict[str, Any] | None = None) -> List[str]:
    """Validate structural integrity of the instrument registry.

    Parameters
    ----------
    registry:
        Pre-loaded registry dict, or None to load from disk.

    Returns
    -------
    list of str
        List of violation strings.  Empty list means PASS.
    """
    if registry is None:
        registry = load_instrument_registry()

    violations: List[str] = []

    predictions = registry.get("predictions", [])
    if not predictions:
        violations.append("Registry contains no predictions.")
        return violations

    seen_ids: set[str] = set()
    for pred in predictions:
        pid = pred.get("id", "<no-id>")

        # Duplicate IDs
        if pid in seen_ids:
            violations.append(f"Duplicate prediction ID: {pid}")
        seen_ids.add(pid)

        # Required fields
        for field in REQUIRED_PREDICTION_FIELDS:
            if field not in pred:
                violations.append(f"[{pid}] Missing required field: {field}")

        # Valid status
        status = pred.get("current_status", "")
        if status not in VALID_STATUSES:
            violations.append(
                f"[{pid}] Invalid current_status '{status}'. "
                f"Must be one of: {sorted(VALID_STATUSES)}"
            )

        # At least one instrument
        instruments = pred.get("instruments", [])
        if not isinstance(instruments, list) or len(instruments) == 0:
            violations.append(f"[{pid}] Must have at least one instrument entry.")

        # fail_condition must be non-empty
        fail_cond = pred.get("fail_condition", "")
        if not fail_cond or not fail_cond.strip():
            violations.append(f"[{pid}] fail_condition is empty — required.")

        # pass_condition must be non-empty
        pass_cond = pred.get("pass_condition", "")
        if not pass_cond or not pass_cond.strip():
            violations.append(f"[{pid}] pass_condition is empty — required.")

        # last_updated must be present
        if "last_updated" not in pred:
            violations.append(f"[{pid}] Missing last_updated field.")

    # Governance block
    gov = registry.get("governance", {})
    if not gov:
        violations.append("Registry is missing governance block.")
    else:
        for gfield in ("update_obligation", "escalation", "machine_ingest"):
            if gfield not in gov:
                violations.append(f"governance block missing field: {gfield}")

    return violations


def check_all_statuses(registry: Dict[str, Any] | None = None) -> Dict[str, str]:
    """Return a mapping of prediction ID → current_status.

    Parameters
    ----------
    registry:
        Pre-loaded registry dict, or None to load from disk.
    """
    if registry is None:
        registry = load_instrument_registry()
    return {
        pred["id"]: pred.get("current_status", "UNKNOWN")
        for pred in registry.get("predictions", [])
        if "id" in pred
    }


def has_high_tension_or_falsified(registry: Dict[str, Any] | None = None) -> bool:
    """Return True if any prediction is in HIGH_TENSION or FALSIFIED state.

    Used as a sentinel for automated escalation checks.
    """
    statuses = check_all_statuses(registry)
    return any(s in {"HIGH_TENSION", "FALSIFIED"} for s in statuses.values())


def _report(registry: Dict[str, Any]) -> None:
    """Print a human-readable status report."""
    statuses = check_all_statuses(registry)
    version = registry.get("version", "?")
    date = registry.get("date", "?")
    print(f"Instrument Registry — {version} ({date})")
    print(f"{'ID':<12} {'Status'}")
    print("-" * 32)
    for pid, status in sorted(statuses.items()):
        marker = "⚠️ " if status == "HIGH_TENSION" else ("❌ " if status == "FALSIFIED" else "   ")
        print(f"  {marker}{pid:<10} {status}")
    print()
    if has_high_tension_or_falsified(registry):
        print("ACTION REQUIRED: One or more predictions are in HIGH_TENSION or FALSIFIED.")
        print("Update CLAIM_MASTER_BOARD.md and WAVE_CHANGELOG.md same day.")
    else:
        print("All predictions CONSISTENT or PENDING — no escalation required.")


if __name__ == "__main__":
    try:
        reg = load_instrument_registry()
    except (FileNotFoundError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    violations = validate_registry_integrity(reg)
    if violations:
        print("Registry integrity FAIL:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        sys.exit(1)

    _report(reg)
