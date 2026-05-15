# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable hardgate registry for ADM/KK closure discipline.

This module centralizes hard completion gates for:
- ADM full dynamical closure
- KK fermion-sector closure
- Orbifold-equivalence closure
- Braided referee hardening

It is intentionally operational: checkable artifacts, checkable tests, and
explicit promotion/falsifier rules.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "closure_hardgates.json"

__all__ = [
    "REGISTRY_PATH",
    "load_hardgate_registry",
    "hardgate_completion_report",
    "workstream_partition",
]


def load_hardgate_registry() -> Dict[str, object]:
    """Load the canonical hardgate registry JSON."""
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Hardgate registry file not found: {REGISTRY_PATH}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Hardgate registry JSON is invalid at {REGISTRY_PATH}: {exc}"
        ) from exc


def hardgate_completion_report(
    test_results: Dict[str, bool] | None = None,
) -> Dict[str, object]:
    """Return artifact/test completion state for every hardgate.

    Parameters
    ----------
    test_results:
        Optional mapping of ``test_path -> bool`` from external runners.
        If omitted, test evidence is treated as unavailable and completion stays open.
    """
    registry = load_hardgate_registry()
    gates = registry.get("gates", [])

    results: Dict[str, Dict[str, object]] = {}
    complete_count = 0

    for gate in gates:
        key = str(gate["key"])
        required_artifacts: List[str] = list(gate.get("required_artifacts", []))
        required_tests: List[str] = list(gate.get("required_tests", []))

        artifact_presence = {p: (ROOT / p).exists() for p in required_artifacts}
        artifacts_ready = bool(artifact_presence) and all(artifact_presence.values())

        if test_results is None:
            test_presence = {t: False for t in required_tests}
            tests_ready = False
        else:
            test_presence = {t: bool(test_results.get(t, False)) for t in required_tests}
            tests_ready = bool(test_presence) and all(test_presence.values())

        complete = artifacts_ready and tests_ready
        if complete:
            complete_count += 1

        results[key] = {
            "status_declared": gate.get("status"),
            "artifacts_ready": artifacts_ready,
            "tests_ready": tests_ready,
            "complete": complete,
            "artifact_presence": artifact_presence,
            "test_evidence": test_presence,
            "falsifier": gate.get("falsifier"),
            "promotion_rule": gate.get("promotion_rule"),
            "workstream": gate.get("workstream"),
        }

    return {
        "registry_path": str(REGISTRY_PATH),
        "gate_count": len(gates),
        "complete_count": complete_count,
        "all_complete": complete_count == len(gates) and len(gates) > 0,
        "results": results,
    }


def workstream_partition() -> Dict[str, List[str]]:
    """Return the mandatory A/B workstream split from the hardgate registry."""
    registry = load_hardgate_registry()
    out: Dict[str, List[str]] = {"A": [], "B": []}
    for gate in registry.get("gates", []):
        stream = str(gate.get("workstream", "")).strip().upper()
        if stream in out:
            out[stream].append(str(gate["key"]))
    return out
