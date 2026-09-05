# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1055 — Sprint CB verification and release discipline."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from src.core.pillar1054_sprint_cb_documentation_traceability_packet import sprint_cb_documentation_traceability_packet

PILLAR_NUMBER: int = 1055
PILLAR_GATE: str = "SPRINT_CB_VERIFICATION_RELEASE_DISCIPLINE"
PILLAR_STATUS: str = "SPRINT_CB_VERIFICATION_RELEASE_DISCIPLINE_COMPLETE"

_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOW = _ROOT / ".github" / "workflows" / "merlin-benchmark-gate.yml"
_STATUS = _ROOT / "STATUS.md"

TARGETED_SUITES: List[str] = [
    "python -m pytest tests/test_pillar1051_merge_gate_baseline_lock.py -q",
    "python -m pytest tests/test_pillar1052_targeted_closure_deterministic_rigor.py -q",
    "python -m pytest tests/test_pillar1053_merlin_frontier_development.py -q",
    "python -m pytest 12-AZ-IP/20-merlin-navigator/tests/test_merlin_v1.py -q",
    "python -m pytest 12-AZ-IP/20-merlin-navigator/tests/test_merlin_memory_and_telemetry.py -q",
]
FULL_REGRESSION_SUITE: str = "python3 -m pytest tests/ recycling/ \"5-GOVERNANCE/Unitary Pentad/\" -q"



def _status_has_zero_failures() -> bool:
    text = _STATUS.read_text(encoding="utf-8") if _STATUS.exists() else ""
    top_window = "\n".join(text.lstrip().splitlines()[:20])
    return bool(re.search(r"\b0\s+failed\b", top_window))


def _active_yaml_lines(text: str) -> List[str]:
    lines: List[str] = []
    for raw in text.splitlines():
        uncommented = raw.split("#", 1)[0].rstrip()
        if uncommented.strip():
            lines.append(uncommented)
    return lines


def _workflow_has_schedule_trigger(lines: List[str]) -> bool:
    in_on_block = False
    for line in lines:
        if re.match(r"^[^\s]", line):
            if re.match(r"^on\s*:", line):
                in_on_block = True
                if re.search(r"\bschedule\b", line):
                    return True
                continue
            if in_on_block:
                break
        if in_on_block and re.match(r"^\s+schedule\s*:", line):
            return True
    return False


def sprint_cb_verification_release_discipline() -> Dict[str, Any]:
    docs = sprint_cb_documentation_traceability_packet()
    workflow_text = _WORKFLOW.read_text(encoding="utf-8") if _WORKFLOW.exists() else ""
    workflow_lines = _active_yaml_lines(workflow_text)
    schedule_present = _workflow_has_schedule_trigger(workflow_lines)
    upload_artifact_present = any(
        re.search(r"^\s*uses:\s*actions/upload-artifact@", line)
        for line in workflow_lines
    )
    artifacts_scripts = [
        "12-AZ-IP/20-merlin-navigator/tools/export_merlin_stage_a_artifacts.py",
        "12-AZ-IP/20-merlin-navigator/tools/export_merlin_training_artifacts.py",
        "12-AZ-IP/20-merlin-navigator/tools/export_merlin_training_jsonl.py",
        "12-AZ-IP/20-merlin-navigator/tools/export_merlin_mlflow_manifests.py",
        "12-AZ-IP/20-merlin-navigator/tools/run_merlin_stage_a_benchmarks.py",
        "12-AZ-IP/20-merlin-navigator/tools/run_merlin_stage_bc_benchmarks.py",
    ]
    script_checks = {p: (_ROOT / p).exists() for p in artifacts_scripts}

    valid = bool(
        docs["valid"]
        and _WORKFLOW.exists()
        and schedule_present
        and upload_artifact_present
        and _status_has_zero_failures()
        and all(script_checks.values())
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "dependency_chain": {
            "pillar1054": docs,
        },
        "targeted_suites": TARGETED_SUITES,
        "full_regression_suite": FULL_REGRESSION_SUITE,
        "workflow_checks": {
            "path": str(_WORKFLOW),
            "exists": _WORKFLOW.exists(),
            "schedule_present": schedule_present,
            "upload_artifact_present": upload_artifact_present,
        },
        "status_gate": {
            "zero_failures_in_header": _status_has_zero_failures(),
        },
        "artifact_script_checks": script_checks,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_cb_verification_release_discipline()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1055_summary() -> Dict[str, Any]:
    report = sprint_cb_verification_release_discipline()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CB Verification Release Discipline",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
    }
