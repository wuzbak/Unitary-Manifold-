# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1006 — CKM shadow promotion audit from the shared-5 bifurcation packet.

Run one proof-first downstream test: ask whether the already-checked 5D / 6D / 7D
branch packet materially upgrades the checked-in CKM shadow lane. The audit is
deliberately narrow and non-mythological. If the shared branch packet still lacks
the named missing CKM object, 13D stays demoted to a downstream organizational sink.
"""

from __future__ import annotations

from typing import Any, Dict

from src.core.pillar1001_shared_5d_bifurcation_core import shared_5d_bifurcation_core
from src.core.pillar1002_sixd_projection_branch_rule import sixd_projection_branch_rule
from src.core.pillar1003_sevend_torsion_shear_branch_rule import (
    sevend_torsion_shear_branch_rule,
)
from src.core.pillar1004_thirteen_dimensional_bifurcation_sink import (
    thirteen_dimensional_bifurcation_sink,
)
from src.core.pillar995_ckm_shadow_closure_binary import ckm_shadow_closure_binary

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "ckm_shadow_shared5_promotion_audit",
]

PILLAR_NUMBER: int = 1006
PILLAR_GATE: str = "CKM_SHADOW_SHARED5_PROMOTION_AUDIT"
PILLAR_STATUS: str = "CKM_SHADOW_SHARED5_PROMOTION_AUDIT_COMPLETE"
_NAMED_MISSING_OBJECT = "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR"


def _coverage_map(
    core: Dict[str, Any],
    sixd: Dict[str, Any],
    sevend: Dict[str, Any],
    baseline: Dict[str, Any],
) -> Dict[str, bool]:
    return {
        "shared_5d_source": bool(core["valid"]),
        "sixd_true_counting_projection": bool(sixd["valid"]),
        "sevend_true_phase_projection": bool(sevend["valid"]),
        "global_flavor_bundle_with_nonlocal_overlap_tensor": (
            baseline["named_missing_object"] == "NONE"
        ),
    }


def ckm_shadow_shared5_promotion_audit() -> Dict[str, Any]:
    """Return the proof-first CKM promotion verdict."""
    core = shared_5d_bifurcation_core()
    sixd = sixd_projection_branch_rule()
    sevend = sevend_torsion_shear_branch_rule()
    sink = thirteen_dimensional_bifurcation_sink()
    baseline = ckm_shadow_closure_binary()

    coverage = _coverage_map(core, sixd, sevend, baseline)
    covered_count = sum(int(flag) for flag in coverage.values())
    total_count = len(coverage)
    promotion_earned = all(coverage.values()) and bool(baseline["closed"])
    promotion_runtime_status = (
        "CKM_SHADOW_PROMOTED_FROM_SHARED5_BRANCH_PACKET"
        if promotion_earned
        else baseline["runtime_status"]
    )
    promotion_outcome = (
        "CKM_SHADOW_PROMOTION_EARNED"
        if promotion_earned
        else "CKM_SHADOW_PROMOTION_NOT_EARNED"
    )
    gates = {
        "shared_5d_core_valid": bool(core["valid"]),
        "sixd_branch_is_true_projection": sixd["branch_pair"]
        == tuple(core["shadow_realizations"][0]["pair"]),
        "sevend_branch_is_true_projection": tuple(sevend["upper_branch_pair"])
        == tuple(core["shadow_realizations"][1]["pair"]),
        "thirteen_d_remains_downstream_only": sink["sink_outcome"]
        == "THIRTEEN_D_ORGANIZATIONAL_SINK_ONLY",
        "baseline_ckm_lane_names_missing_object": baseline["named_missing_object"]
        == _NAMED_MISSING_OBJECT,
        "no_status_promotion_without_missing_object": (
            not coverage["global_flavor_bundle_with_nonlocal_overlap_tensor"]
            and promotion_runtime_status == baseline["runtime_status"]
        ),
    }

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": all(gates.values()),
        "binary_question": "DOES_SHARED5_BRANCH_PACKET_PROMOTE_CKM_13D",
        "baseline_runtime_status": baseline["runtime_status"],
        "baseline_closed": baseline["closed"],
        "baseline_errors": {
            "theta13_rel_error": baseline["theta13_rel_error"],
            "vub_rel_error": baseline["vub_rel_error"],
            "jarlskog_rel_error": baseline["jarlskog_rel_error"],
        },
        "promotion_runtime_status": promotion_runtime_status,
        "promotion_outcome": promotion_outcome,
        "status_change": promotion_runtime_status != baseline["runtime_status"],
        "named_blocker": baseline["named_missing_object"],
        "earned_input_coverage": coverage,
        "earned_input_coverage_ratio": covered_count / total_count,
        "shared_core": core["shared_core"],
        "sixd_branch_pair": sixd["branch_pair"],
        "sevend_upper_branch_pair": sevend["upper_branch_pair"],
        "sink_outcome": sink["sink_outcome"],
        "non_negotiable_consistency_gates": gates,
        "interpretation": (
            "The shared 5D core plus the checked-in 6D counting branch and 7D phase/shear branch "
            "do clarify the CKM target lane, but they do not supply the named missing object "
            f"{_NAMED_MISSING_OBJECT}. The checked-in branch therefore does not earn a CKM status "
            "promotion, and 13D remains downstream-only rather than explanatory by declaration."
        ),
    }


PILLAR_VALID: bool = ckm_shadow_shared5_promotion_audit()["valid"]
