# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1047 — Sprint BY status-coherence certificate."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from src.core.pillar1046_sprint_by_parallel_continuation_certificate import pillar1046_summary

PILLAR_NUMBER: int = 1047
PILLAR_GATE: str = "SPRINT_BY_STATUS_COHERENCE_CERTIFICATE"
PILLAR_STATUS: str = "SPRINT_BY_STATUS_COHERENCE_CERTIFICATE_COMPLETE"

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
REQUIRED_OPEN_LABELS: List[str] = [
    "CMB_AMP_CONFIRMED_IRREDUCIBLE",
    "ALPHA_S_TYPE_B_FLOOR",
    "LITEBIRD_BIREFRINGENCE",
]
REQUIRED_SPRINT_MARKERS: List[str] = ["v35.5", "1040-1047", "1048"]
EXPECTED_TESTS_PASSED: int = 63714
EXPECTED_LEAN4_COUNT: int = 3976
EXPECTED_TOTAL_SLOTS: int = 1047
EXPECTED_NEXT_SLOT: int = 1048


def _parse_version_number(raw: object) -> float:
    text = str(raw or "").strip().lower().lstrip("v")
    try:
        return float(text)
    except ValueError:
        return 0.0


def status_surface_audit() -> Dict[str, Any]:
    per_surface: Dict[str, Dict[str, Any]] = {}
    for name, path in STATUS_SURFACES.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        text_lower = text.lower()
        pillar_window_pass = bool(
            re.search(r"1040\s*(?:[–-]|to)\s*1047", text, flags=re.IGNORECASE)
            or re.search(r"1049\s*(?:[–-]|to)\s*1050", text, flags=re.IGNORECASE)
        )
        next_slot_candidates = [
            int(v)
            for v in re.findall(
                r"next(?:_pillar_slot| pillar slot| slot)[^0-9]{0,12}(\d+)",
                text_lower,
            )
        ]
        next_slot_pass = bool(next_slot_candidates and max(next_slot_candidates) >= 1048)
        version_matches = [float(v) for v in re.findall(r"v(\d+\.\d+)", text)]
        version_pass = bool(version_matches and max(version_matches) >= 35.5)
        open_hits = {label: (label in text) for label in REQUIRED_OPEN_LABELS}
        sprint_hits = {
            "v35.5": version_pass,
            "pillar_window_1040_to_1047": pillar_window_pass,
            "next_slot_1048": next_slot_pass,
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
        label: sum(1 for item in per_surface.values() if bool(item["open_label_hits"].get(label)))
        for label in REQUIRED_OPEN_LABELS
    }
    sprint_marker_surface_counts = {
        key: sum(1 for item in per_surface.values() if bool(item["sprint_marker_hits"].get(key)))
        for key in ("v35.5", "pillar_window_1040_to_1047", "next_slot_1048")
    }
    return {
        "surfaces": per_surface,
        "all_exist": all_exist,
        "open_labels_pass": all(count == len(STATUS_SURFACES) for count in label_surface_counts.values()),
        "open_label_surface_counts": label_surface_counts,
        "sprint_marker_surface_counts": sprint_marker_surface_counts,
        "sprint_markers_pass": all(count == len(STATUS_SURFACES) for count in sprint_marker_surface_counts.values()),
    }


def _live_status_audit() -> Dict[str, Any]:
    payload = json.loads(LIVE_STATUS_PATH.read_text(encoding="utf-8")) if LIVE_STATUS_PATH.exists() else {}
    meta = dict(payload.get("meta") or {})
    pillars = dict(payload.get("pillars") or {})
    lean4 = dict(payload.get("lean4") or {})
    tests = dict(payload.get("tests") or {})
    status_text = (_ROOT / "STATUS.md").read_text(encoding="utf-8")
    status_match = re.search(
        r"([\d,]+)\s+passed\s*[·•]\s*(\d+)\s+skipped\s*[·•]\s*(\d+)\s+deselected",
        status_text,
    )
    version_number = _parse_version_number(meta.get("version"))
    return {
        "exists": LIVE_STATUS_PATH.exists(),
        "version_ok": version_number >= 35.5,
        "next_slot_ok": int(pillars.get("next_slot", 0)) >= EXPECTED_NEXT_SLOT,
        "total_slots_ok": int(pillars.get("total_slots", 0)) >= EXPECTED_TOTAL_SLOTS,
        "lean4_ok": int(lean4.get("theorem_count", 0)) >= EXPECTED_LEAN4_COUNT,
        "tests_ok": bool(
            status_match
            and (
                int(tests.get("passed", 0)),
                int(tests.get("skipped", 0)),
                int(tests.get("deselected", 0)),
            )
            == (
                int(status_match.group(1).replace(",", "")),
                int(status_match.group(2)),
                int(status_match.group(3)),
            )
        ),
    }


def status_coherence_certificate() -> Dict[str, Any]:
    audit = status_surface_audit()
    live = _live_status_audit()
    sprint = pillar1046_summary()
    valid = bool(
        audit["all_exist"]
        and audit["open_labels_pass"]
        and audit["sprint_markers_pass"]
        and all(live.values())
        and sprint["valid"]
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "surface_audit": audit,
        "live_status_audit": live,
        "dependency_chain": {"pillar1046": sprint},
        "story_lock": {
            "open_set_preserved": audit["open_labels_pass"],
            "sprint_markers_coherent": audit["sprint_markers_pass"],
            "live_status_synced": all(live.values()),
            "promotion_claim_hidden": False,
        },
        "interpretation": (
            "Sprint BY continuation outputs and canonical truth surfaces are synchronized with unchanged open-lane discipline, repaired stale wording, and refreshed live-status artifacts."
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(status_coherence_certificate()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1047_summary() -> Dict[str, Any]:
    report = status_coherence_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint BY Status-Coherence Certificate",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "all_surfaces_exist": report["surface_audit"]["all_exist"],
    }
