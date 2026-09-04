# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1036 — Merlin self-hosted replacement milestone."""

from __future__ import annotations

import json
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-merlin-navigator"

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "merlin_self_hosted_replacement_milestone",
    "pillar1036_summary",
]

PILLAR_NUMBER: int = 1036
PILLAR_GATE: str = "MERLIN_SELF_HOSTED_REPLACEMENT_MILESTONE"
PILLAR_STATUS: str = "MERLIN_SELF_HOSTED_REPLACEMENT_MILESTONE_COMPLETE"


def _ensure_merlin_package_loaded() -> None:
    if "ox_navigator" in sys.modules:
        return
    package_root = _PRODUCT_ROOT / "ox_navigator"
    spec = importlib.util.spec_from_file_location(
        "ox_navigator",
        package_root / "__init__.py",
        submodule_search_locations=[str(package_root)],
    )
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load ox_navigator package")
    module = importlib.util.module_from_spec(spec)
    sys.modules["ox_navigator"] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop("ox_navigator", None)
        raise


def _run_merlin_helper(module_name: str, function_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    _ensure_merlin_package_loaded()
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    return json.loads(json.dumps(function(**kwargs)))


def merlin_self_hosted_replacement_milestone() -> Dict[str, Any]:
    """Return the Sprint BX Merlin self-hosted replacement milestone report."""
    readiness = _run_merlin_helper(
        "ox_navigator.engine.merlin_benchmark",
        "build_stage_a_replacement_readiness",
        {"limit": 3},
    )
    sync_checks = _run_merlin_helper(
        "ox_navigator.engine.merlin_program",
        "run_sync_checks",
        {},
    )
    valid = bool(
        readiness["ok"]
        and readiness["packet"]["decision"] in {"REPLACEMENT_APPROVED", "REPLACEMENT_NOT_APPROVED"}
        and readiness["packet"]["decision"] != "REPLACEMENT_EVIDENCE_REQUIRED"
        and sync_checks["ok"]
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "self_hosted_stage_a_ready": readiness["ok"],
        "evidence_present": readiness["packet"]["checks"]["evidence_present"],
        "readiness_decision": readiness["packet"]["decision"],
        "comparable_run_count": readiness["packet"]["empirical_gate"]["metrics"]["comparable_runs"],
        "sync_checks_ok": sync_checks["ok"],
        "interpretation": (
            "Sprint BX upgrades Merlin from policy-only replacement intent to a concrete "
            "self-hosted Stage A receipt and readiness surface. Approval is still evidence-gated."
        ),
    }


PILLAR_VALID: bool | None = None


def pillar1036_summary() -> Dict[str, Any]:
    """Return concise Pillar 1036 summary."""
    report = merlin_self_hosted_replacement_milestone()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Merlin Self-Hosted Replacement Milestone",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "readiness_decision": report["readiness_decision"],
        "evidence_present": report["evidence_present"],
        "comparable_run_count": report["comparable_run_count"],
    }
