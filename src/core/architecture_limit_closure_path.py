# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Architecture-limit closure path packet for A3 and SC4.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

from src.core.flux_landscape_extended_scan import sc4_closure_summary
from src.core.higgs_naturalness_extended import higgs_naturalness_extended_report

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "architecture_limit_closure_path_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"


def architecture_limit_closure_path_report() -> dict[str, object]:
    """Return explicit closure path, owner, and stop-condition for A3 and SC4."""
    a3 = higgs_naturalness_extended_report()
    sc4 = sc4_closure_summary()

    return {
        "report_id": "ARCHITECTURE_LIMIT_CLOSURE_PATH",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "A3": {
            "verdict": a3["overall_verdict"],
            "closure_blocker": a3["closure_blocker"],
            "owner": a3["blocker_owner"],
            "stop_condition": a3["stop_condition"],
        },
        "SC4": {
            "verdict": sc4["global_verdict"],
            "closure_blocker": sc4["closure_blocker"],
            "owner": sc4["blocker_owner"],
            "stop_condition": sc4["stop_condition"],
        },
    }
