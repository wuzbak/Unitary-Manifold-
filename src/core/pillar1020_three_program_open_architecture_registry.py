# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1020 — Three-program registry for the surviving open architecture lanes.

Group the six checked-in architecture-limit lanes into three auditable programs
instead of treating them as six disconnected holes.  The registry keeps all
lane labels unchanged and records both:

- bookkeeping program numbering (`Program 1` / `Program 2` / `Program 3`), and
- practical execution priority (flavor family first, then UV/global, then CMB).

This preserves the checked-in honesty rule: a program only earns promotion when
one of its downstream runtimes actually changes status.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar1009_cmb_nonperturbative_normalization_candidate import (
    cmb_nonperturbative_normalization_candidate,
)
from src.core.pillar977_higgs_mass_ceiling_sharpening import higgs_window_certificate
from src.core.pillar980_jarlskog_layer2_architecture_limit import pillar980_summary
from src.core.pillar982_architecture_limit_registry_runtime import (
    runtime_architecture_limit_registry,
)
from src.core.pillar995_ckm_shadow_closure_binary import ckm_shadow_closure_binary
from src.core.pillar996_fermion_magnitude_radii_closure_binary import (
    fermion_magnitude_radii_closure_binary,
)
from src.core.pillar999_cmb_amplitude_calibration_boundary import (
    cmb_amplitude_evidence_ledger,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "OPEN_ARCHITECTURE_LANES",
    "BOOKKEEPING_PROGRAM_ORDER",
    "PRACTICAL_PRIORITY_ORDER",
    "three_program_open_architecture_registry",
    "pillar1020_summary",
]

PILLAR_NUMBER: int = 1020
PILLAR_GATE: str = "THREE_PROGRAM_OPEN_ARCHITECTURE_REGISTRY"
PILLAR_STATUS: str = "THREE_PROGRAM_OPEN_ARCHITECTURE_REGISTRY_COMPLETE"

OPEN_ARCHITECTURE_LANES: List[str] = [
    "CMB_AMP_CONFIRMED_IRREDUCIBLE",
    "ALPHA_S_TYPE_B_FLOOR",
    "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
    "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
    "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
    "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
]

BOOKKEEPING_PROGRAM_ORDER: List[str] = [
    "PROGRAM_1_CMB_NORMALIZATION_MECHANISM",
    "PROGRAM_2_SHARED_UV_COMPACTIFICATION",
    "PROGRAM_3_SHARED_FLAVOR_GEOMETRY",
]

PRACTICAL_PRIORITY_ORDER: List[str] = [
    "PROGRAM_3_SHARED_FLAVOR_GEOMETRY",
    "PROGRAM_2_SHARED_UV_COMPACTIFICATION",
    "PROGRAM_1_CMB_NORMALIZATION_MECHANISM",
]


def _registry_rows() -> Dict[str, Dict[str, Any]]:
    rows = runtime_architecture_limit_registry()["rows"]
    return {str(row["lane"]): row for row in rows}


def _cmb_program() -> Dict[str, Any]:
    ledger = cmb_amplitude_evidence_ledger()
    candidate = cmb_nonperturbative_normalization_candidate()
    return {
        "program_id": "PROGRAM_1_CMB_NORMALIZATION_MECHANISM",
        "bookkeeping_index": 1,
        "practical_priority_rank": 3,
        "recommended_sprint_label": "SPRINT_A",
        "family": "CMB",
        "lanes": ["CMB_AMP_CONFIRMED_IRREDUCIBLE"],
        "shared_missing_objects": ledger["named_missing_objects"],
        "current_runtime_status": "CMB_AMP_CONFIRMED_IRREDUCIBLE",
        "current_evidence": {
            "terminal_eft_routes": ledger["terminal_eft_routes"],
            "latest_candidate_outcome": candidate["outcome"],
            "residual_budget_status": candidate["strengthened_certificate"]["status"],
        },
        "binary_success_criteria": {
            "uses_external_as_target": False,
            "new_fit_knobs_added": 0,
            "must_reduce_amplitude_deficit": True,
            "must_target_all_shared_missing_objects": True,
        },
        "failure_routing": (
            "If the candidate still misses either named object or does not reduce the deficit, "
            "tighten the residual-budget certificate again instead of widening the claim."
        ),
    }


def _uv_program(rows: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    alpha = rows["ALPHA_S_TYPE_B_FLOOR"]
    higgs = higgs_window_certificate()
    return {
        "program_id": "PROGRAM_2_SHARED_UV_COMPACTIFICATION",
        "bookkeeping_index": 2,
        "practical_priority_rank": 2,
        "recommended_sprint_label": "SPRINT_B",
        "family": "UV_GLOBAL_GEOMETRY",
        "lanes": [
            "ALPHA_S_TYPE_B_FLOOR",
            "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
        ],
        "shared_missing_objects": [
            *alpha["missing_objects"],
            "UV_HIGGS_MASS_GENERATING_OPERATOR",
        ],
        "current_runtime_status": "DUAL_LANE_ARCHITECTURE_LIMIT",
        "current_evidence": {
            "alpha_s_boundary_class": alpha["boundary_class"],
            "alpha_s_closure_test": alpha["closure_test"],
            "higgs_window_low": higgs["architecture_update"]["new_limit"]["window_low"],
            "higgs_window_high": higgs["architecture_update"]["new_limit"]["window_high"],
            "higgs_architecture_only": higgs["architecture_limit_only"],
        },
        "binary_success_criteria": {
            "shared_object_count": 1,
            "must_improve_alpha_s_and_higgs_together": True,
            "per_lane_rescue_parameters_allowed": 0,
            "separate_lane_rescues_forbidden": True,
        },
        "failure_routing": (
            "If one shared compactification object does not materially narrow both lanes together, "
            "keep both labels open and architecture-limited."
        ),
    }


def _flavor_program() -> Dict[str, Any]:
    ckm = ckm_shadow_closure_binary()
    fermion = fermion_magnitude_radii_closure_binary()
    jarlskog = pillar980_summary()
    return {
        "program_id": "PROGRAM_3_SHARED_FLAVOR_GEOMETRY",
        "bookkeeping_index": 3,
        "practical_priority_rank": 1,
        "recommended_sprint_label": "SPRINT_C",
        "family": "FLAVOR_FAMILY",
        "lanes": [
            "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
            "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
            "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
        ],
        "shared_missing_objects": [
            ckm["named_missing_object"],
            fermion["named_missing_object"],
            "HIGHER_ORDER_FLAVOR_TORSION_COMPLETION",
            "GLOBAL_CKM_PHASE_GEOMETRY_BEYOND_IN_EFT_CAP",
        ],
        "current_runtime_status": "FLAVOR_FAMILY_ROOT_NOT_YET_EARNED",
        "current_evidence": {
            "ckm_runtime_status": ckm["runtime_status"],
            "fermion_runtime_status": fermion["runtime_status"],
            "jarlskog_runtime_status": jarlskog["status"],
            "jarlskog_binary_outcome": jarlskog["binary_outcome"],
        },
        "binary_success_criteria": {
            "root_object_first": "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR",
            "must_change_downstream_runtime_state": True,
            "jarlskog_cannot_be_run_as_standalone_rescue_first": True,
        },
        "failure_routing": (
            "If the shared flavor geometry does not flip at least one downstream runtime, "
            "return another certified family boundary rather than a promotion."
        ),
    }


def three_program_open_architecture_registry() -> Dict[str, Any]:
    """Return the canonical three-program regrouping of the six open lanes."""
    rows = _registry_rows()
    programs = [
        _cmb_program(),
        _uv_program(rows),
        _flavor_program(),
    ]

    lanes_flat = [lane for program in programs for lane in program["lanes"]]
    all_lanes_covered_once = sorted(lanes_flat) == sorted(OPEN_ARCHITECTURE_LANES)
    bookkeeping_matches = [program["program_id"] for program in programs] == BOOKKEEPING_PROGRAM_ORDER
    priority_matches = [
        program["program_id"]
        for program in sorted(programs, key=lambda row: int(row["practical_priority_rank"]))
    ] == PRACTICAL_PRIORITY_ORDER
    unchanged_open_labels = all(
        lane in OPEN_ARCHITECTURE_LANES
        for lane in lanes_flat
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": all(
            (
                all_lanes_covered_once,
                bookkeeping_matches,
                priority_matches,
                unchanged_open_labels,
                len(programs) == 3,
            )
        ),
        "programs": programs,
        "n_programs": len(programs),
        "n_lanes": len(lanes_flat),
        "all_lanes_covered_once": all_lanes_covered_once,
        "unchanged_open_labels": unchanged_open_labels,
        "bookkeeping_program_order": BOOKKEEPING_PROGRAM_ORDER,
        "practical_priority_order": PRACTICAL_PRIORITY_ORDER,
        "program_number_is_not_execution_priority": True,
        "interpretation": (
            "The six surviving architecture-limit lanes are now grouped into three coupled programs. "
            "Program numbering is bookkeeping only; practical execution priority starts with the "
            "shared flavor-family root, then the shared UV compactification lane, and only then the CMB program."
        ),
    }


PILLAR_VALID: bool = bool(three_program_open_architecture_registry()["valid"])


def pillar1020_summary() -> Dict[str, Any]:
    """Return concise summary for Pillar 1020."""
    report = three_program_open_architecture_registry()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Three-Program Open Architecture Registry",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "n_programs": report["n_programs"],
        "n_lanes": report["n_lanes"],
        "bookkeeping_program_order": report["bookkeeping_program_order"],
        "practical_priority_order": report["practical_priority_order"],
    }
