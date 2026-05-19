# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 247 — Unified observation ingest and verdict router.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

from typing import Dict

ADJACENCY_TRACK_LABEL = "NON_HARDGATE_ADJACENT"

_SUPPORTED = {"DESI", "LITEBIRD", "CMB-S4", "JUNO", "HYPER-K"}


def route_observation_packet(experiment: str, sigma: float, in_window: bool) -> Dict[str, object]:
    exp = experiment.strip().upper()
    if exp not in _SUPPORTED:
        raise ValueError(f"Unsupported experiment: input={experiment!r}, normalized={exp!r}, supported={sorted(_SUPPORTED)}")
    if sigma < 0:
        raise ValueError("sigma must be non-negative")

    if sigma >= 3.0 and not in_window:
        route = "FALSIFIED"
    elif sigma >= 2.0:
        route = "TENSION"
    else:
        route = "PASS"

    return {
        "pillar": 247,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "experiment": exp,
        "sigma": sigma,
        "in_window": in_window,
        "route": route,
        "status": "ROUTED",
        "non_hardgate_statement": "Unified adjacent-track ingest router only.",
    }


def pillar247_router_report() -> Dict[str, object]:
    return {
        "pillar": 247,
        "title": "Unified Observation Ingest & Verdict Routing Engine",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "supported_experiments": sorted(_SUPPORTED),
        "status": "READY",
    }
