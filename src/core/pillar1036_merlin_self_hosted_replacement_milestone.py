# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1036 — Merlin self-hosted replacement milestone."""

from __future__ import annotations

import json
import os
import subprocess
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


def _run_merlin_helper(module_name: str, function_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    code = """
import json
from {module_name} import {function_name}
print(json.dumps({function_name}(**json.loads({payload!r}))))
""".format(
        module_name=module_name,
        function_name=function_name,
        payload=json.dumps(kwargs),
    )
    env = dict(os.environ)
    prior_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{_PRODUCT_ROOT}:{prior_path}" if prior_path else str(_PRODUCT_ROOT)
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(_PRODUCT_ROOT),
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return json.loads(completed.stdout)


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
