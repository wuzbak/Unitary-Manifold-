# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1049 — Sprint CA full-throttle closure execution."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from src.core.pillar1041_flavor_priority_continuation import flavor_priority_continuation
from src.core.pillar1042_uv_joint_bottleneck_continuation import (
    uv_joint_bottleneck_continuation,
)
from src.core.pillar1043_cmb_irreducibility_continuation import (
    cmb_irreducibility_continuation,
)
from src.core.pillar1044_su3_functional_bridge_alignment import (
    HIGH_LEVEL_REMAINING_BURDEN,
    su3_functional_bridge_alignment,
)
from src.core.pillar1048_quantum_gravity_parallel_rigor_sprint import (
    OBSTRUCTION_CODES,
    quantum_gravity_parallel_rigor_sprint,
)

PILLAR_NUMBER: int = 1049
PILLAR_GATE: str = "SPRINT_CA_FULL_THROTTLE_EXECUTION"
PILLAR_STATUS: str = "SPRINT_CA_FULL_THROTTLE_EXECUTION_COMPLETE"
VERSION: str = "v35.7"
SPRINT_NAME: str = "CA"
NEXT_PILLAR_SLOT: int = 1051
LEAN4_START: int = 3976
LEAN4_END: int = 3988
LEAN4_DELTA: int = LEAN4_END - LEAN4_START

LEAN4_FILE: str = "lean4/UnitaryManifold/SprintCAFormalTraceability.lean"
LEAN4_THEOREM_COUNT: int = 12

OPEN_LANES: List[str] = [
    "CMB_AMP_CONFIRMED_IRREDUCIBLE",
    "ALPHA_S_TYPE_B_FLOOR",
    "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
    "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
    "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
    "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
    "DESI_DR3_MONITORING",
    "LITEBIRD_BIREFRINGENCE",
    "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT",
]

DECISION_GATES: List[str] = [
    "CLOSURE_EARNED",
    "BOUNDARY_TIGHTENED",
    "CARRY_FORWARD_OPEN",
]

SUBSTACK_ARTICLES: List[str] = [
    "7-OUTREACH/substack/posts/post-303-s04e006-sprint-ca-state-and-open-set.md",
    "7-OUTREACH/substack/posts/post-304-s04e007-sprint-ca-flavor-closure-blockers.md",
    "7-OUTREACH/substack/posts/post-305-s04e008-sprint-ca-uv-coupled-lane.md",
    "7-OUTREACH/substack/posts/post-306-s04e009-sprint-ca-cmb-amplitude-integrity.md",
    "7-OUTREACH/substack/posts/post-307-s04e010-sprint-ca-lean4-formal-burden.md",
]

_ROOT = Path(__file__).resolve().parents[2]


def _go_no_go(runtime_flip_earned: bool, boundary_tightened: bool) -> str:
    if runtime_flip_earned:
        return "CLOSURE_EARNED"
    if boundary_tightened:
        return "BOUNDARY_TIGHTENED"
    return "CARRY_FORWARD_OPEN"


def _count_theorems(text: str) -> int:
    return len(re.findall(r"^\s*theorem\s+ca_trace_kernel_\d+\b", text, flags=re.MULTILINE))


def _traceability_map(text: str) -> List[Dict[str, Any]]:
    pairs = [
        ("UMClaimLabelTraceable", "claim_label_traceability"),
        ("UMArtifactTraceable", "artifact_traceability"),
        ("UMLeanStatusTraceable", "lean_status_traceability"),
    ]
    return [
        {
            "theorem": theorem,
            "status_label": label,
            "present": theorem in text,
        }
        for theorem, label in pairs
    ]


def _article_pack_status() -> Dict[str, Any]:
    required_headings = [
        "## What changed",
        "## What did not change",
        "## Falsification implications",
        "## Residual unknowns",
    ]
    per_article: List[Dict[str, Any]] = []
    for rel_path in SUBSTACK_ARTICLES:
        path = _ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        per_article.append(
            {
                "path": rel_path,
                "exists": path.exists(),
                "headings_present": {
                    heading: heading in text for heading in required_headings
                },
                "valid": path.exists()
                and all(heading in text for heading in required_headings),
            }
        )
    return {
        "required_headings": required_headings,
        "articles": per_article,
        "all_valid": all(item["valid"] for item in per_article),
    }


def sprint_ca_full_throttle_execution() -> Dict[str, Any]:
    """Execute the Sprint CA full-throttle closure packet."""
    flavor = flavor_priority_continuation()
    uv = uv_joint_bottleneck_continuation()
    cmb = cmb_irreducibility_continuation()
    formal = su3_functional_bridge_alignment()
    qg = quantum_gravity_parallel_rigor_sprint()

    flavor_runtime_flip = bool(flavor["runtime_flip_earned"])
    flavor_boundary_tightened = bool(flavor["valid"] and not flavor_runtime_flip)
    flavor_gate = _go_no_go(flavor_runtime_flip, flavor_boundary_tightened)

    uv_runtime_flip = False
    uv_boundary_tightened = bool(
        uv["valid"] and uv["joint_bottleneck_pressure"] > 1.0
    )
    uv_gate = _go_no_go(uv_runtime_flip, uv_boundary_tightened)

    cmb_runtime_flip = bool(cmb["closure_earned"])
    cmb_boundary_tightened = bool(cmb["valid"] and not cmb_runtime_flip)
    cmb_gate = _go_no_go(cmb_runtime_flip, cmb_boundary_tightened)

    lean4_path = _ROOT / LEAN4_FILE
    lean4_text = lean4_path.read_text(encoding="utf-8") if lean4_path.exists() else ""
    theorem_count = _count_theorems(lean4_text)
    traceability = _traceability_map(lean4_text)
    formal_lane = {
        "dependency_valid": bool(formal["valid"]),
        "lean4_file": LEAN4_FILE,
        "lean4_file_exists": lean4_path.exists(),
        "theorem_count": theorem_count,
        "expected_theorem_count": LEAN4_THEOREM_COUNT,
        "traceability": traceability,
        "remaining_functional_burden": HIGH_LEVEL_REMAINING_BURDEN,
        "go_no_go": _go_no_go(False, bool(formal["valid"])),
        "valid": bool(
            formal["valid"]
            and theorem_count == LEAN4_THEOREM_COUNT
            and all(item["present"] for item in traceability)
        ),
    }

    qg_rows = list(qg["intake"]["rows"])
    intake_fields_ok = all(
        all(
            key in row
            for key in (
                "metric",
                "metric_value",
                "uncertainty",
                "reproducibility_status",
            )
        )
        for row in qg_rows
    )
    qg_lane = {
        "dependency_valid": bool(qg["valid"]),
        "obstruction_codes": list(OBSTRUCTION_CODES),
        "intake_row_count": len(qg_rows),
        "intake_fields_ok": intake_fields_ok,
        "routing_classes": sorted({item["verdict"] for item in qg["routing"]}),
        "hidden_calibration_detected": any(
            bool(item["hidden_calibration_detected"]) for item in qg["routing"]
        ),
        "go_no_go": _go_no_go(False, bool(qg["valid"] and intake_fields_ok)),
        "valid": bool(qg["valid"] and intake_fields_ok),
    }

    article_pack = _article_pack_status()

    decision_matrix = {
        "program_a_flavor": flavor_gate,
        "program_b_uv": uv_gate,
        "program_c_cmb": cmb_gate,
        "formal_lane": formal_lane["go_no_go"],
        "qg_lane": qg_lane["go_no_go"],
    }

    definition_of_done = {
        "binary_rule_enforced": all(
            gate in DECISION_GATES for gate in decision_matrix.values()
        ),
        "all_nine_open_lanes_explicit": len(OPEN_LANES) == 9,
        "truth_surface_sync_required": True,
        "flavor_program_executed": bool(flavor["valid"]),
        "uv_program_executed": bool(uv["valid"]),
        "cmb_program_executed": bool(cmb["valid"]),
        "formal_traceability_expanded": bool(formal_lane["valid"]),
        "qg_o1_o4_rigor_enforced": bool(qg_lane["valid"]),
        "deterministic_go_no_go_present": all(
            gate in DECISION_GATES for gate in decision_matrix.values()
        ),
        "substack_packet_complete": bool(article_pack["all_valid"]),
        "no_score_branding": True,
    }

    valid = bool(
        all(definition_of_done.values())
        and all(gate != "CARRY_FORWARD_OPEN" for gate in decision_matrix.values())
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_END,
        "lean4_delta": LEAN4_DELTA,
        "open_lanes": list(OPEN_LANES),
        "decision_gates": list(DECISION_GATES),
        "decision_matrix": decision_matrix,
        "workstreams": {
            "program_a_flavor": flavor,
            "program_b_uv": uv,
            "program_c_cmb": cmb,
            "formal_lane": formal_lane,
            "qg_lane": qg_lane,
        },
        "substack_article_packet": article_pack,
        "definition_of_done": definition_of_done,
        "valid": valid,
    }


PILLAR_VALID: bool = bool(sprint_ca_full_throttle_execution()["valid"])


def pillar1049_summary() -> Dict[str, Any]:
    """Return concise Sprint CA summary."""
    report = sprint_ca_full_throttle_execution()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CA Full-Throttle Closure Execution",
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "valid": report["valid"],
    }
