# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""Sprint BA status registry for AxiomZero.

This module exposes the Sprint BA pillar window P837–P860 as structured,
honest status metadata for downstream orchestration, UI, and audit tooling.
Unknown or not-yet-integrated items remain OPEN by design.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

STATUS_LABELS = ("CLOSED", "PARTIAL", "OPEN")
_PILLAR_RANGE = range(837, 861)


def _default_entry(pillar_number: int) -> Dict[str, Any]:
    pillar_id = f"P{pillar_number}"
    return {
        "pillar": pillar_id,
        "status": "OPEN",
        "summary": "No Sprint BA closure record is integrated into AxiomZero for this pillar yet.",
        "notes": "The app preserves honest accounting: unresolved or untracked items stay OPEN.",
    }


_PILLARS: Dict[str, Dict[str, Any]] = {
    f"P{pillar_number}": _default_entry(pillar_number)
    for pillar_number in _PILLAR_RANGE
}

_PILLARS["P849"] = {
    "pillar": "P849",
    "status": "CLOSED",
    "summary": "k_CS = 74 is fixed by the 9D Green-Schwarz closure.",
    "artifact": "k_CS=74",
    "notes": "Sprint BA treats the 9D Green-Schwarz fixing of k_CS=74 as closed and ready for application use.",
}

_PILLARS["P853"] = {
    "pillar": "P853",
    "status": "PARTIAL",
    "summary": "φ₀ = 1 is tracked as a partial closure rather than a finished result.",
    "artifact": "phi0=1",
    "notes": "The unit normalisation is recorded, but the repository context explicitly labels this Sprint BA item PARTIAL.",
}

_PILLARS["P858"] = {
    "pillar": "P858",
    "status": "CLOSED",
    "summary": "The 7-step 11D→4D dimensional chain is closed in Sprint BA.",
    "artifact": "11D→10D→9D→8D→7D→6D→5D→4D",
    "step_count": 7,
    "notes": "AxiomZero exposes the full dimensional descent as closed integration metadata for Sprint BA-aware workflows.",
}


def _summary_counts(pillars: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    return {
        label: sum(1 for entry in pillars.values() if entry["status"] == label)
        for label in STATUS_LABELS
    }


SPRINT_BA_STATUS: Dict[str, Any] = {
    "app": "01-axiom-os",
    "module": "AxiomZero.sprint_ba_status",
    "repository_version": "v25.5",
    "sprint": "BA",
    "pillar_window": {"start": "P837", "end": "P860", "count": len(_PILLARS)},
    "status_labels": list(STATUS_LABELS),
    "pillars": _PILLARS,
    "summary": _summary_counts(_PILLARS),
}


def get_sprint_ba_status() -> Dict[str, Any]:
    """Return a defensive copy of the Sprint BA status registry."""
    return deepcopy(SPRINT_BA_STATUS)


def get_pillar_status(pillar_id: str) -> Dict[str, Any]:
    """Return a defensive copy of one Sprint BA pillar entry.

    Raises
    ------
    KeyError
        If the requested pillar lies outside the P837–P860 registry.
    """
    if pillar_id not in _PILLARS:
        raise KeyError(f"Unknown Sprint BA pillar: {pillar_id}")
    return deepcopy(_PILLARS[pillar_id])


def validate_sprint_ba_status(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Validate structure and labels for Sprint BA status payloads."""
    data = payload if payload is not None else SPRINT_BA_STATUS
    pillars = data["pillars"]
    labels_ok = all(entry["status"] in STATUS_LABELS for entry in pillars.values())
    key_range_ok = list(pillars) == [f"P{pillar_number}" for pillar_number in _PILLAR_RANGE]
    summary = _summary_counts(pillars)
    summary_ok = summary == data.get("summary", {})
    return {
        "valid": labels_ok and key_range_ok and summary_ok,
        "checks": {
            "labels_ok": labels_ok,
            "key_range_ok": key_range_ok,
            "summary_ok": summary_ok,
        },
        "summary": summary,
    }


__all__ = [
    "STATUS_LABELS",
    "SPRINT_BA_STATUS",
    "get_pillar_status",
    "get_sprint_ba_status",
    "validate_sprint_ba_status",
]