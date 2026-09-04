# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1040 — Sprint BY precision lock and stale-surface audit."""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-merlin-navigator"

PILLAR_NUMBER: int = 1040
PILLAR_GATE: str = "SPRINT_BY_PRECISION_LOCK"
PILLAR_STATUS: str = "SPRINT_BY_PRECISION_LOCK_COMPLETE"
STATUS_SURFACES: Dict[str, Path] = {
    "status": _ROOT / "STATUS.md",
    "fallibility": _ROOT / "FALLIBILITY.md",
    "mas_tracker": _ROOT / "docs" / "mas_tracker.yml",
    "claim_master_board": _ROOT / "docs" / "CLAIM_MASTER_BOARD.md",
    "gatekeeper_summary": _ROOT / "docs" / "GATEKEEPER_SUMMARY.md",
    "truth_layer": _ROOT / "docs" / "TRUTH_LAYER.md",
    "wave_changelog": _ROOT / "docs" / "WAVE_CHANGELOG.md",
    "sprint_plan": _ROOT / "docs" / "SPRINT_PLAN.md",
}
LIVE_STATUS_PATH = _ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"
MERLIN_PROGRAM_PATH = _PRODUCT_ROOT / "ox_navigator" / "engine" / "merlin_program.py"
MERLIN_GATE_WORKFLOW = _ROOT / ".github" / "workflows" / "merlin-benchmark-gate.yml"
STATUS_DRIFT_WORKFLOW = _ROOT / ".github" / "workflows" / "status-drift-gate.yml"
REQUIRED_OPEN_LABELS: List[str] = [
    "CMB_AMP_CONFIRMED_IRREDUCIBLE",
    "ALPHA_S_TYPE_B_FLOOR",
    "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
    "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
    "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
    "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
    "DESI_DR3_MONITORING",
    "LITEBIRD_BIREFRINGENCE",
]


def _load_merlin_baseline() -> Dict[str, Any]:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    module = importlib.import_module("ox_navigator.engine.merlin_program")
    return json.loads(json.dumps(module.get_current_stack_baseline()))


def _surface_snapshot() -> Dict[str, Any]:
    status_text = STATUS_SURFACES["status"].read_text(encoding="utf-8") if STATUS_SURFACES["status"].exists() else ""
    fallibility_text = STATUS_SURFACES["fallibility"].read_text(encoding="utf-8") if STATUS_SURFACES["fallibility"].exists() else ""
    live_status = json.loads(LIVE_STATUS_PATH.read_text(encoding="utf-8")) if LIVE_STATUS_PATH.exists() else {}
    version_match = re.search(r"\*v([\d.]+) Sprint (\w+)", status_text)
    next_slot_match = re.search(r"next slot (\d+)", status_text)
    tests_match = re.search(
        r"([\d,]+) passed\s*[·•]\s*(\d+) skipped\s*[·•]\s*(\d+) deselected\s*[·•]\s*(\d+) failed",
        status_text,
    )
    return {
        "version": f"v{version_match.group(1)}" if version_match else "unknown",
        "sprint": version_match.group(2) if version_match else "unknown",
        "next_slot": int(next_slot_match.group(1)) if next_slot_match else 0,
        "tests_passed": int(tests_match.group(1).replace(",", "")) if tests_match else 0,
        "status_text": status_text,
        "fallibility_text": fallibility_text,
        "live_status": live_status,
    }


def sprint_by_precision_lock() -> Dict[str, Any]:
    """Audit Sprint BY precision lock across stale status and Merlin baseline surfaces."""
    snapshot = _surface_snapshot()
    baseline = _load_merlin_baseline()
    stale_phrase = "63,666 passed · 23 skipped · 12 deselected · 0 failed (v35.3"
    merlin_gate_text = MERLIN_GATE_WORKFLOW.read_text(encoding="utf-8") if MERLIN_GATE_WORKFLOW.exists() else ""
    status_drift_text = STATUS_DRIFT_WORKFLOW.read_text(encoding="utf-8") if STATUS_DRIFT_WORKFLOW.exists() else ""

    stale_checks = {
        "fallibility_stale_v35_3_removed": stale_phrase not in snapshot["fallibility_text"],
        "fallibility_latest_version_locked": snapshot["version"] in snapshot["fallibility_text"],
        "fallibility_latest_count_locked": f"{snapshot['tests_passed']:,} passed" in snapshot["fallibility_text"],
        "merlin_baseline_no_fake_corpus_gap": "no formal benchmark corpus" not in " ".join(baseline["gaps_to_replacement"]).lower(),
        "merlin_baseline_no_fake_ci_gap": "not yet attached to ci" not in " ".join(baseline["gaps_to_replacement"]).lower(),
        "merlin_baseline_tracks_artifact_gap_honestly": any("artifact" in gap.lower() or "longitudinal" in gap.lower() for gap in baseline["gaps_to_replacement"]),
    }
    workflow_checks = {
        "merlin_gate_exists": MERLIN_GATE_WORKFLOW.exists(),
        "merlin_gate_has_schedule": "schedule:" in merlin_gate_text,
        "merlin_gate_uploads_artifact": "upload-artifact" in merlin_gate_text,
        "status_drift_gate_exists": STATUS_DRIFT_WORKFLOW.exists(),
        "status_drift_gate_active": "check_status_drift.py" in status_drift_text,
    }
    surface_texts = {
        name: path.read_text(encoding="utf-8") if path.exists() else ""
        for name, path in STATUS_SURFACES.items()
    }
    open_set_checks = {
        label: all(label in text for text in surface_texts.values())
        for label in REQUIRED_OPEN_LABELS
    }
    live_status_checks = {
        "version_ok": str(snapshot["live_status"].get("meta", {}).get("version")) in {snapshot["version"], snapshot["version"].lstrip("v")},
        "next_slot_ok": int(snapshot["live_status"].get("pillars", {}).get("next_slot", 0)) == snapshot["next_slot"],
        "tests_ok": int(snapshot["live_status"].get("tests", {}).get("passed", 0)) == snapshot["tests_passed"],
        "failed_zero": int(snapshot["live_status"].get("tests", {}).get("failed", -1)) == 0,
    }
    valid = all(stale_checks.values()) and all(workflow_checks.values()) and all(open_set_checks.values()) and all(live_status_checks.values())
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "sprint": snapshot["sprint"],
        "version": snapshot["version"],
        "next_pillar_slot": snapshot["next_slot"],
        "stale_checks": stale_checks,
        "workflow_checks": workflow_checks,
        "open_set_checks": open_set_checks,
        "live_status_checks": live_status_checks,
        "merlin_baseline_gaps": list(baseline["gaps_to_replacement"]),
        "interpretation": (
            "Sprint BY begins by repairing stale-surface drift, locking the v35.5 truth surfaces, "
            "and forcing Merlin baseline language to match the implemented benchmark and workflow state."
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_by_precision_lock()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1040_summary() -> Dict[str, Any]:
    report = sprint_by_precision_lock()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint BY Precision Lock",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "version": report["version"],
        "next_pillar_slot": report["next_pillar_slot"],
    }
