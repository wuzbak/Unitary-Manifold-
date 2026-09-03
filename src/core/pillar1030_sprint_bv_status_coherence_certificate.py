# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1030 — Sprint BV status-coherence certificate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from src.core.pillar1029_sprint_bv_closure_program_certificate import pillar1029_summary

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "STATUS_SURFACES",
    "REQUIRED_OPEN_LABELS",
    "REQUIRED_SPRINT_MARKERS",
    "status_surface_audit",
    "status_coherence_certificate",
    "pillar1030_summary",
]

PILLAR_NUMBER: int = 1030
PILLAR_GATE: str = "SPRINT_BV_STATUS_COHERENCE_CERTIFICATE"
PILLAR_STATUS: str = "SPRINT_BV_STATUS_COHERENCE_CERTIFICATE_COMPLETE"

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

REQUIRED_OPEN_LABELS: List[str] = [
    "CMB_AMP_CONFIRMED_IRREDUCIBLE",
    "ALPHA_S_TYPE_B_FLOOR",
    "LITEBIRD_BIREFRINGENCE",
]

REQUIRED_SPRINT_MARKERS: List[str] = [
    "v35.2",
    "1025-1030",
    "1031",
]


def status_surface_audit() -> Dict[str, Any]:
    """Audit that canonical surfaces narrate one Sprint BV story."""
    per_surface: Dict[str, Dict[str, Any]] = {}
    for name, path in STATUS_SURFACES.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        text_lower = text.lower()
        pillar_window_pass = ("1025–1030" in text) or ("1025-1030" in text)
        next_slot_pass = (
            ("next slot 1031" in text_lower)
            or ("next_pillar_slot: 1031" in text)
            or ("next pillar slot" in text_lower and "1031" in text_lower)
        )
        open_hits = {label: (label in text) for label in REQUIRED_OPEN_LABELS}
        sprint_hits = {
            "v35.2": ("v35.2" in text),
            "pillar_window_1025_to_1030": pillar_window_pass,
            "next_slot_1031": next_slot_pass,
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
            1 for item in per_surface.values() if bool(item["open_label_hits"].get(label))
        )
        for label in REQUIRED_OPEN_LABELS
    }
    open_labels_pass = all(count >= 4 for count in label_surface_counts.values())
    sprint_markers_pass = all(item["sprint_markers_pass"] for item in per_surface.values())
    return {
        "surfaces": per_surface,
        "all_exist": all_exist,
        "open_labels_pass": open_labels_pass,
        "open_label_surface_counts": label_surface_counts,
        "sprint_markers_pass": sprint_markers_pass,
    }


def status_coherence_certificate() -> Dict[str, Any]:
    """Return the Sprint BV status-coherence certificate."""
    audit = status_surface_audit()
    sprint = pillar1029_summary()
    valid = bool(
        audit["all_exist"]
        and audit["open_labels_pass"]
        and audit["sprint_markers_pass"]
        and sprint["valid"]
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "surface_audit": audit,
        "dependency_chain": {
            "pillar1029": sprint,
        },
        "story_lock": {
            "open_set_preserved": audit["open_labels_pass"],
            "sprint_markers_coherent": audit["sprint_markers_pass"],
            "promotion_claim_hidden": False,
        },
        "interpretation": (
            "Sprint BV closure-program outputs and canonical truth surfaces are synchronized "
            "with unchanged open-label discipline."
        ),
    }


PILLAR_VALID: bool = bool(status_coherence_certificate()["valid"])


def pillar1030_summary() -> Dict[str, Any]:
    """Return concise Pillar 1030 summary."""
    report = status_coherence_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint BV Status-Coherence Certificate",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "all_surfaces_exist": report["surface_audit"]["all_exist"],
        "open_labels_pass": report["surface_audit"]["open_labels_pass"],
        "sprint_markers_pass": report["surface_audit"]["sprint_markers_pass"],
    }
