# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 225 — JUNO/Hyper-K neutron oscillation readiness brief.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

from typing import Dict, List

ADJACENCY_TRACK_LABEL = "NON_HARDGATE_ADJACENT"


def readiness_components() -> List[Dict[str, object]]:
    return [
        {"lane": "detector_uptime", "score": 0.86, "status": "READY"},
        {"lane": "timing_calibration", "score": 0.83, "status": "READY"},
        {"lane": "background_modeling", "score": 0.78, "status": "WATCH"},
        {"lane": "cross_experiment_schema", "score": 0.82, "status": "READY"},
    ]


def pillar225_readiness_brief() -> Dict[str, object]:
    comps = readiness_components()
    avg = sum(float(c["score"]) for c in comps) / len(comps)
    return {
        "pillar": 225,
        "title": "JUNO/Hyper-K Neutron Oscillation Readiness Brief",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "components": comps,
        "readiness_index": avg,
        "status": "READY" if avg >= 0.8 else "PARTIAL_READINESS",
        "non_hardgate_statement": "Adjacent observatory readiness packet only; no hardgate claim promotion.",
    }
