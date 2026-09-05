# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1059 — Sprint CC status coherence certificate."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

from src.core.pillar1049_sprint_ca_full_throttle_execution import OPEN_LANES
from src.core.pillar1058_flavor_execution_packet import pillar1058_summary

PILLAR_NUMBER: int = 1059
PILLAR_GATE: str = "SPRINT_CC_STATUS_COHERENCE_CERTIFICATE"
PILLAR_STATUS: str = "SPRINT_CC_STATUS_COHERENCE_CERTIFICATE_COMPLETE"

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
LIVE_STATUS_PATH = _ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"

REQUIRED_SPRINT_MARKERS = ["v35.9", "1058-1059", "1060"]
EXPECTED_TESTS_PASSED_MIN: int = 63756
EXPECTED_LEAN4_COUNT: int = 4000
EXPECTED_TOTAL_SLOTS: int = 1059
EXPECTED_NEXT_SLOT: int = 1060


def _parse_version_components(raw: object) -> tuple[int, ...]:
    text = str(raw or "").strip().lower().lstrip("v")
    parts = [p for p in text.split(".") if p]
    if not parts:
        return tuple()
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return tuple()


def status_surface_audit() -> Dict[str, Any]:
    per_surface: Dict[str, Dict[str, Any]] = {}
    for name, path in STATUS_SURFACES.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        text_lower = text.lower()
        pillar_window_pass = bool(
            re.search(r"1058\s*(?:[–-]|to)\s*1059", text, flags=re.IGNORECASE)
        )
        next_slot_candidates = [
            int(v)
            for v in re.findall(
                r"next(?:_pillar_slot| pillar slot| slot)[^0-9]{0,12}(\d+)",
                text_lower,
            )
        ]
        next_slot_pass = bool(
            next_slot_candidates and max(next_slot_candidates) >= EXPECTED_NEXT_SLOT
        )
        open_hits = {label: (label in text) for label in OPEN_LANES}
        sprint_hits = {
            "v35.9": ("v35.9" in text),
            "pillar_window_1058_to_1059": pillar_window_pass,
            "next_slot_1060": next_slot_pass,
        }
        per_surface[name] = {
            "path": str(path),
            "exists": path.exists(),
            "open_label_hits": open_hits,
            "sprint_marker_hits": sprint_hits,
            "open_labels_pass": all(open_hits.values()) if path.exists() else False,
            "sprint_markers_pass": all(sprint_hits.values()) if path.exists() else False,
        }

    all_exist = all(item["exists"] for item in per_surface.values())
    label_surface_counts = {
        label: sum(
            1
            for item in per_surface.values()
            if bool(item["open_label_hits"].get(label))
        )
        for label in OPEN_LANES
    }
    sprint_marker_surface_counts = {
        key: sum(
            1
            for item in per_surface.values()
            if bool(item["sprint_marker_hits"].get(key))
        )
        for key in ("v35.9", "pillar_window_1058_to_1059", "next_slot_1060")
    }

    return {
        "surfaces": per_surface,
        "all_exist": all_exist,
        "open_labels_pass": all(
            count == len(STATUS_SURFACES) for count in label_surface_counts.values()
        ),
        "open_label_surface_counts": label_surface_counts,
        "sprint_marker_surface_counts": sprint_marker_surface_counts,
        "sprint_markers_pass": all(
            count == len(STATUS_SURFACES)
            for count in sprint_marker_surface_counts.values()
        ),
    }


def _live_status_audit() -> Dict[str, Any]:
    payload = (
        json.loads(LIVE_STATUS_PATH.read_text(encoding="utf-8"))
        if LIVE_STATUS_PATH.exists()
        else {}
    )
    meta = dict(payload.get("meta") or {})
    pillars = dict(payload.get("pillars") or {})
    lean4 = dict(payload.get("lean4") or {})
    tests = dict(payload.get("tests") or {})
    version_number = _parse_version_components(meta.get("version"))
    return {
        "exists": LIVE_STATUS_PATH.exists(),
        "version_ok": version_number >= (35, 9),
        "next_slot_ok": int(pillars.get("next_slot", 0)) >= EXPECTED_NEXT_SLOT,
        "total_slots_ok": int(pillars.get("total_slots", 0)) >= EXPECTED_TOTAL_SLOTS,
        "lean4_ok": int(lean4.get("theorem_count", 0)) >= EXPECTED_LEAN4_COUNT,
        "tests_ok": int(tests.get("passed", 0)) >= EXPECTED_TESTS_PASSED_MIN,
    }


def sprint_cc_status_coherence_certificate() -> Dict[str, Any]:
    audit = status_surface_audit()
    live = _live_status_audit()
    sprint = pillar1058_summary()

    live_semantic_pass = all(
        live.get(key, False)
        for key in (
            "version_ok",
            "next_slot_ok",
            "total_slots_ok",
            "lean4_ok",
            "tests_ok",
        )
    )

    valid = bool(
        audit["all_exist"]
        and audit["open_labels_pass"]
        and audit["sprint_markers_pass"]
        and live.get("exists", False)
        and live_semantic_pass
        and sprint["valid"]
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "surface_audit": audit,
        "live_status_audit": live,
        "dependency_chain": {"pillar1058": sprint},
        "story_lock": {
            "open_set_preserved": audit["open_labels_pass"],
            "sprint_markers_coherent": audit["sprint_markers_pass"],
            "live_status_synced": bool(live.get("exists", False) and live_semantic_pass),
            "promotion_claim_hidden": False,
        },
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_cc_status_coherence_certificate()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1059_summary() -> Dict[str, Any]:
    report = sprint_cc_status_coherence_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CC Status-Coherence Certificate",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "all_surfaces_exist": report["surface_audit"]["all_exist"],
    }
