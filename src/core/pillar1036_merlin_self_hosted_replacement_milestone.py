# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1036 — Merlin self-hosted replacement milestone."""

from __future__ import annotations

import importlib
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-merlin-navigator"
_MERLIN_IMPORT_LOCK = threading.RLock()

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


@contextmanager
def _merlin_import_path() -> Iterator[None]:
    product_root = str(_PRODUCT_ROOT)
    inserted = False
    if product_root not in sys.path:
        sys.path.insert(0, product_root)
        inserted = True
    try:
        yield
    finally:
        if inserted:
            try:
                sys.path.remove(product_root)
            except ValueError:
                pass


def _load_merlin_helpers() -> tuple[Any, Any]:
    with _MERLIN_IMPORT_LOCK:
        with _merlin_import_path():
            benchmark = importlib.import_module("ox_navigator.engine.merlin_benchmark")
            program = importlib.import_module("ox_navigator.engine.merlin_program")
    return benchmark.build_stage_a_replacement_readiness, program.run_sync_checks


def merlin_self_hosted_replacement_milestone() -> Dict[str, Any]:
    """Return the Sprint BX Merlin self-hosted replacement milestone report."""
    build_stage_a_replacement_readiness, run_sync_checks = _load_merlin_helpers()
    readiness = build_stage_a_replacement_readiness(limit=3)
    sync_checks = run_sync_checks()
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


_REPORT = merlin_self_hosted_replacement_milestone()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1036_summary() -> Dict[str, Any]:
    """Return concise Pillar 1036 summary."""
    report = merlin_self_hosted_replacement_milestone()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Merlin Self-Hosted Replacement Milestone",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "readiness_decision": report["readiness_decision"],
        "evidence_present": report["evidence_present"],
        "comparable_run_count": report["comparable_run_count"],
    }
