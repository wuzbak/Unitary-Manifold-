# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1002 — 6D projection/counting branch rule.

Use the checked-in 6D generation-count machinery to show why the recurring
"6" is naturally the counting-side companion to the shared 5D core.
"""

from __future__ import annotations

from typing import Any, Dict

from src.core.pillar1001_shared_5d_bifurcation_core import shared_5d_bifurcation_core
from src.sixd.generation_count_6d import generation_count_audit, pillar_6d_1_summary

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "sixd_projection_branch_rule",
]

PILLAR_NUMBER: int = 1002
PILLAR_GATE: str = "SIXD_PROJECTION_BRANCH_RULE"
PILLAR_STATUS: str = "SIXD_PROJECTION_BRANCH_RULE_COMPLETE"


def sixd_projection_branch_rule() -> Dict[str, Any]:
    """Return the 6D counting branch packet."""
    core = shared_5d_bifurcation_core()
    audit = generation_count_audit()
    summary = pillar_6d_1_summary()
    n_gen_6d = int(summary["n_gen_6d_derived"])
    branch_pair = (int(core["shared_core"]["n_w"]), 2 * n_gen_6d)
    gates = {
        "sixd_kill_switch_pass": bool(summary["kill_switch_pass"]),
        "anchor_burned": bool(summary["anchor_burned"]),
        "branch_matches_shared_lower_shadow": tuple(branch_pair) == tuple(core["shadow_realizations"][0]["pair"]),
        "counting_rule_recovers_six": branch_pair[1] == 6,
        "verdict_mentions_completion": "COMPLETE" in str(audit["verdict"]),
    }
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": all(gates.values()),
        "branch_pair": branch_pair,
        "counting_rule": "n2_6d = 2 × N_gen(T²/Z₃ fixed points)",
        "n_gen_6d": n_gen_6d,
        "source_summary": summary,
        "source_audit": audit,
        "non_negotiable_consistency_gates": gates,
        "interpretation": (
            "The 6D lift explains the recurring 6 as a counting-side companion: "
            "N_gen=3 from T²/Z₃ gives 2×3=6, matching the lower shared-core branch."
        ),
    }


PILLAR_VALID: bool = sixd_projection_branch_rule()["valid"]
