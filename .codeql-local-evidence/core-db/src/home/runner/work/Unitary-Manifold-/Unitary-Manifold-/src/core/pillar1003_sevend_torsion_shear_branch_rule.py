# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1003 — 7D torsion/shear branch rule.

Use the checked-in 7D discrete-torsion and shear artifacts to show why the
recurring 7 belongs to the phase/shear side of the shared 5D core.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from src.core.pillar1001_shared_5d_bifurcation_core import shared_5d_bifurcation_core
from src.core.pillar682_thirteen_dimensional_itheory_engine import (
    theorem_682_3_dual_sector_phase_angle,
)
from src.sevend.discrete_torsion_cp import discrete_torsion_summary
from src.sevend.pillar863_cp_violation_7d_torsion import cp_violation_7d_summary

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "sevend_torsion_shear_branch_rule",
]

PILLAR_NUMBER: int = 1003
PILLAR_GATE: str = "SEVEND_TORSION_SHEAR_BRANCH_RULE"
PILLAR_STATUS: str = "SEVEND_TORSION_SHEAR_BRANCH_RULE_COMPLETE"


def sevend_torsion_shear_branch_rule() -> Dict[str, Any]:
    """Return the 7D torsion/shear branch packet."""
    core = shared_5d_bifurcation_core()
    torsion = discrete_torsion_summary()
    cp7 = cp_violation_7d_summary()
    shear = theorem_682_3_dual_sector_phase_angle()
    upper_pair = tuple(core["shadow_realizations"][1]["pair"])
    lower_pair = tuple(core["shadow_realizations"][0]["pair"])
    shear_source = tuple(shear["n_primary"])
    shear_target = tuple(shear["n_shadow"])
    gates = {
        "torsion_kill_switch_pass": bool(torsion["kill_switch"]["kill_switch_pass"]),
        "supplementary_phase_locked": math.isclose(
            float(torsion["canonical_result"]["delta_cp_geo_rad"]), math.pi / 3.0, abs_tol=1e-12
        ),
        "shear_verified": bool(shear["shear_verified"]),
        "shear_source_matches_upper_branch": shear_source == upper_pair,
        "shear_target_matches_lower_branch": shear_target == lower_pair,
        "cp_nlo_improves": bool(cp7["nlo_improves"]),
    }
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": all(gates.values()),
        "upper_branch_pair": upper_pair,
        "lower_branch_pair": lower_pair,
        "torsion_summary": torsion,
        "cp_violation_summary": cp7,
        "shear_summary": shear,
        "non_negotiable_consistency_gates": gates,
        "interpretation": (
            "The 7D lift explains the phase/shear side: the canonical torsion phase is π/3, "
            "the shared upper branch is (5,7), and the checked-in SL(2,R) shear carries it to (5,6) "
            "as a one-quantum topological shift rather than a separate origin."
        ),
    }


PILLAR_VALID: bool = sevend_torsion_shear_branch_rule()["valid"]
