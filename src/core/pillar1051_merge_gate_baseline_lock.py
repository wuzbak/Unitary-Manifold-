# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1051 — merge-gated baseline lock for Sprint CB."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Dict

PILLAR_NUMBER: int = 1051
PILLAR_GATE: str = "MERGE_GATE_BASELINE_LOCK"
PILLAR_STATUS: str = "MERGE_GATE_BASELINE_LOCK_COMPLETE"

VERSION: str = "v35.8"
SPRINT_NAME: str = "CB"
NEXT_PILLAR_SLOT: int = 1058

HOUSEKEEPING_MERGE_ENV: str = "UM_HOUSEKEEPING_MERGED"
HOUSEKEEPING_MERGE_MARKER: str = ".housekeeping_merge_ready"

_ROOT = Path(__file__).resolve().parents[2]
STATUS_SURFACES: Dict[str, Path] = {
    "status": _ROOT / "STATUS.md",
    "fallibility": _ROOT / "FALLIBILITY.md",
    "mas_tracker": _ROOT / "docs/mas_tracker.yml",
    "claim_master_board": _ROOT / "docs/CLAIM_MASTER_BOARD.md",
    "gatekeeper_summary": _ROOT / "docs/GATEKEEPER_SUMMARY.md",
    "truth_layer": _ROOT / "docs/TRUTH_LAYER.md",
    "wave_changelog": _ROOT / "docs/WAVE_CHANGELOG.md",
    "sprint_plan": _ROOT / "docs/SPRINT_PLAN.md",
}


def _truthy_env(raw: str) -> bool:
    return str(raw or "").strip().lower() in {"1", "true", "yes", "on"}


def _sha256_text(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _merge_gate_state() -> Dict[str, Any]:
    env_value = os.environ.get(HOUSEKEEPING_MERGE_ENV, "")
    marker_path = _ROOT / HOUSEKEEPING_MERGE_MARKER
    merged = _truthy_env(env_value) or marker_path.exists()
    return {
        "housekeeping_merged": bool(merged),
        "freeze_new_claim_promotion": not bool(merged),
        "env_flag": HOUSEKEEPING_MERGE_ENV,
        "env_value": str(env_value),
        "marker_file": str(marker_path),
        "marker_present": marker_path.exists(),
    }


def _baseline_surface_snapshot() -> Dict[str, Any]:
    snapshots: Dict[str, Dict[str, Any]] = {}
    for name, path in STATUS_SURFACES.items():
        snapshots[name] = {
            "path": str(path),
            "exists": path.exists(),
            "sha256": _sha256_text(path),
            "size_bytes": path.stat().st_size if path.exists() else 0,
        }
    return {
        "surfaces": snapshots,
        "all_surfaces_exist": all(item["exists"] for item in snapshots.values()),
        "surface_count": len(snapshots),
    }


def merge_gate_baseline_lock() -> Dict[str, Any]:
    gate = _merge_gate_state()
    baseline = _baseline_surface_snapshot()
    baseline_audit_required = bool(gate["housekeeping_merged"])
    baseline_audit_complete = bool(baseline["all_surfaces_exist"])
    valid = bool(
        baseline["all_surfaces_exist"]
        and (
            gate["freeze_new_claim_promotion"]
            or (baseline_audit_required and baseline_audit_complete)
        )
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "merge_gate": gate,
        "baseline_lock": {
            "required": baseline_audit_required,
            "complete": baseline_audit_complete,
            "snapshot": baseline,
        },
        "valid": valid,
        "interpretation": (
            "Claim promotion is frozen until housekeeping merge is acknowledged; once merged, "
            "canonical status surfaces are hash-locked as the Sprint CB starting baseline."
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(merge_gate_baseline_lock()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1051_summary() -> Dict[str, Any]:
    report = merge_gate_baseline_lock()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Merge-Gate Baseline Lock",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "housekeeping_merged": report["merge_gate"]["housekeeping_merged"],
        "freeze_new_claim_promotion": report["merge_gate"]["freeze_new_claim_promotion"],
    }
