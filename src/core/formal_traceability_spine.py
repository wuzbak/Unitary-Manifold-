# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/formal_traceability_spine.py
=====================================
Canonical machine-readable traceability spine for the current Lean4/Python
formal frontier.

This registry does three things:
1. Fixes the immediate formal program to two lanes only.
2. Separates proof classes cleanly: unconditional Lean, conditional Lean with
   named axioms, and executable Python validation.
3. Packages the reviewer-facing intake surface into small proof packets tied to
   concrete Lean files, Python artifacts, tests, and current status surfaces.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

PROGRAM_ID = "FORMAL_PROOF_FOUNDRY"
PROGRAM_STATUS = "ACTIVE_HONESTY_FIRST"

LANE_A_ID = "LANE_A_APS_ORBIFOLD_DIRAC"
LANE_B_ID = "LANE_B_ACTION_TO_EVOLUTION"

PROOF_CLASS_UNCONDITIONAL = "LEAN_UNCONDITIONAL"
PROOF_CLASS_CONDITIONAL = "LEAN_CONDITIONAL_WITH_NAMED_AXIOMS"
PROOF_CLASS_EXECUTABLE = "EXECUTABLE_PYTHON_VALIDATION"

_ROOT = Path(__file__).resolve().parents[2]

PROOF_CLASSES: List[Dict[str, Any]] = [
    {
        "id": PROOF_CLASS_UNCONDITIONAL,
        "summary": "Lean theorem with no extra axioms beyond the checked environment.",
        "allowed_evidence": ["Lean theorem", "scoped Lean build receipt"],
    },
    {
        "id": PROOF_CLASS_CONDITIONAL,
        "summary": "Lean theorem whose dependencies include explicitly named axioms or open gaps.",
        "allowed_evidence": ["Lean theorem", "named axiom list", "honesty boundary note"],
    },
    {
        "id": PROOF_CLASS_EXECUTABLE,
        "summary": "Python executable check or audit surface; useful evidence, not a Lean proof.",
        "allowed_evidence": ["Python module", "passing tests", "machine-readable boundary report"],
    },
]

PRIMARY_LANES: List[Dict[str, Any]] = [
    {
        "id": LANE_A_ID,
        "title": "APS / orbifold / Dirac boundary machinery",
        "priority": 1,
        "status": "OPEN_FRONTIER",
        "why_now": (
            "The main proof-distance inflation is now in manifolds-with-boundary, "
            "orbifold parity, Dirac spectral asymmetry, and APS-style boundary machinery."
        ),
        "primary_lean_files": [
            "lean4/UnitaryManifold/NWUniquenessHonest.lean",
            "lean4/UnitaryManifold/DiracOrbifoldSpectrum.lean",
        ],
        "primary_python_modules": [
            "src/core/aps_eta_invariant.py",
            "src/core/yukawa_orbifold_bc_texture.py",
            "src/core/nw_circularity_audit.py",
        ],
        "primary_tests": [
            "tests/test_pillar828_aps_eta_invariant_lean4_bridge.py",
            "tests/test_yukawa_orbifold_bc_texture.py",
            "tests/test_nw_circularity_audit.py",
        ],
        "review_packet": "proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md",
    },
    {
        "id": LANE_B_ID,
        "title": "Action-to-evolution equivalence for the implemented physics core",
        "priority": 2,
        "status": "OPEN_FRONTIER",
        "why_now": (
            "The current evolution engine remains a phenomenological flow until an action "
            "is written down and its Euler-Lagrange equations are shown to reproduce it."
        ),
        "primary_lean_files": [
            "lean4/UnitaryManifold/SprintCAFormalTraceability.lean",
        ],
        "primary_python_modules": [
            "src/core/evolution.py",
            "src/core/pillar1082_foundation_first_photon_action_audit.py",
        ],
        "primary_tests": [
            "tests/test_evolution.py",
            "tests/test_pillar1082_foundation_first_photon_action_audit.py",
        ],
        "review_packet": "proof/REVIEW_PACKET_ACTION_TO_EVOLUTION.md",
    },
]

TRACEABILITY_ROWS: List[Dict[str, Any]] = [
    {
        "id": "APS_ETA_AXIOM_HALF_CLASS",
        "lane_id": LANE_A_ID,
        "kind": "axiom",
        "epistemic_class": PROOF_CLASS_CONDITIONAL,
        "label": "OPEN_AXIOM",
        "lean_file": "lean4/UnitaryManifold/NWUniquenessHonest.lean",
        "lean_symbols": [
            "aps_eta_invariant_5_is_half",
            "aps_eta_invariant_7_is_zero",
        ],
        "python_modules": [
            "src/core/aps_eta_invariant.py",
            "src/core/pillar828_aps_eta_invariant_lean4_bridge.py",
        ],
        "tests": [
            "tests/test_pillar828_aps_eta_invariant_lean4_bridge.py",
        ],
        "status_entries": [
            "docs/TRUTH_LAYER.md",
            "proof/TIER_1_FORMAL.md",
            "proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md",
        ],
        "review_packet": "proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md",
        "summary": "APS η-invariant selection is explicit in Lean as a named axiom and numerically bridged in Python.",
    },
    {
        "id": "APS_MATHLIB_FORMALIZATION_GAP",
        "lane_id": LANE_A_ID,
        "kind": "open_gap",
        "epistemic_class": PROOF_CLASS_CONDITIONAL,
        "label": "MATHLIB_FRONTIER_OPEN",
        "lean_file": "lean4/UnitaryManifold/NWUniquenessHonest.lean",
        "lean_symbols": [
            "NW_FIRST_PRINCIPLES_UNIQUENESS",
            "APS_MATHLIB_FORMALIZATION",
            "NGEN_DERIVATION",
        ],
        "python_modules": [
            "src/core/nw_circularity_audit.py",
        ],
        "tests": [
            "tests/test_nw_circularity_audit.py",
        ],
        "status_entries": [
            "docs/TRUTH_LAYER.md",
            "STATUS.md",
            "proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md",
        ],
        "review_packet": "proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md",
        "summary": "The remaining first-principles NW uniqueness burden is carried as named open gaps, not hidden inside theorem counts.",
    },
    {
        "id": "DIRAC_ORBIFOLD_PROXY_BOUNDARY",
        "lane_id": LANE_A_ID,
        "kind": "theorem_cluster",
        "epistemic_class": PROOF_CLASS_EXECUTABLE,
        "label": "CONDITIONAL_ARITHMETIC_PROXY_ONLY",
        "lean_file": "lean4/UnitaryManifold/DiracOrbifoldSpectrum.lean",
        "lean_symbols": [
            "cl_gen3",
            "g4_bc_spectrum_certificate",
            "g4_generation_mixing_closure",
        ],
        "python_modules": [
            "src/core/yukawa_orbifold_bc_texture.py",
            "src/core/pillar677_fermion_cl_orbifold_closure.py",
        ],
        "tests": [
            "tests/test_yukawa_orbifold_bc_texture.py",
            "tests/test_pillar677_fermion_cl_orbifold_closure.py",
        ],
        "status_entries": [
            "docs/TRUTH_LAYER.md",
            "proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md",
        ],
        "review_packet": "proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md",
        "summary": "Dirac orbifold arithmetic proxies are separated from the analytic 5D boundary-value argument and labelled accordingly.",
    },
    {
        "id": "ACTION_TO_EVOLUTION_BOUNDARY",
        "lane_id": LANE_B_ID,
        "kind": "open_gap",
        "epistemic_class": PROOF_CLASS_EXECUTABLE,
        "label": "PHENOMENOLOGICAL_FLOW_BOUNDARY",
        "lean_file": "lean4/UnitaryManifold/SprintCAFormalTraceability.lean",
        "lean_symbols": [
            "UMClaimLabelTraceable",
            "UMArtifactTraceable",
            "UMLeanStatusTraceable",
            "ca_trace_kernel_12",
        ],
        "python_modules": [
            "src/core/evolution.py",
            "src/core/pillar1082_foundation_first_photon_action_audit.py",
        ],
        "tests": [
            "tests/test_evolution.py",
            "tests/test_pillar1082_foundation_first_photon_action_audit.py",
        ],
        "status_entries": [
            "docs/TRUTH_LAYER.md",
            "proof/TIER_1_FORMAL.md",
            "proof/REVIEW_PACKET_ACTION_TO_EVOLUTION.md",
        ],
        "review_packet": "proof/REVIEW_PACKET_ACTION_TO_EVOLUTION.md",
        "summary": "The evolution engine is currently a tested honesty boundary, not yet a verified Euler-Lagrange derivation.",
    },
]

REVIEW_PACKETS: List[Dict[str, Any]] = [
    {
        "id": "PACKET_APS_ORBIFOLD_DIRAC",
        "title": "APS / orbifold / Dirac packet",
        "path": "proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md",
        "lane_id": LANE_A_ID,
        "claim_ids": [
            "APS_ETA_AXIOM_HALF_CLASS",
            "APS_MATHLIB_FORMALIZATION_GAP",
            "DIRAC_ORBIFOLD_PROXY_BOUNDARY",
        ],
    },
    {
        "id": "PACKET_ACTION_TO_EVOLUTION",
        "title": "Action-to-evolution packet",
        "path": "proof/REVIEW_PACKET_ACTION_TO_EVOLUTION.md",
        "lane_id": LANE_B_ID,
        "claim_ids": [
            "ACTION_TO_EVOLUTION_BOUNDARY",
        ],
    },
]

INTAKE_SURFACE: List[str] = [
    "proof/README.md",
    "proof/TIER_1_FORMAL.md",
    "proof/FORMAL_PROOF_FOUNDRY.md",
    "docs/TRUTH_LAYER.md",
]


def _path_exists(rel_path: str) -> bool:
    return (_ROOT / rel_path).exists()


def _row_paths_exist(row: Dict[str, Any]) -> bool:
    paths = [
        row["lean_file"],
        row["review_packet"],
        *row["python_modules"],
        *row["tests"],
        *row["status_entries"],
    ]
    return all(_path_exists(path) for path in paths)


def _packet_claim_ids_exist(packet: Dict[str, Any]) -> bool:
    known = {row["id"] for row in TRACEABILITY_ROWS}
    return all(claim_id in known for claim_id in packet["claim_ids"])


def formal_traceability_spine() -> Dict[str, Any]:
    """Return the canonical formal frontier registry."""
    rows = [dict(row, paths_exist=_row_paths_exist(row)) for row in TRACEABILITY_ROWS]
    packets = [
        dict(
            packet,
            path_exists=_path_exists(packet["path"]),
            claim_ids_exist=_packet_claim_ids_exist(packet),
        )
        for packet in REVIEW_PACKETS
    ]
    intake_surface = [
        {"path": path, "exists": _path_exists(path)}
        for path in INTAKE_SURFACE
    ]
    valid = bool(
        len(PRIMARY_LANES) == 2
        and len(PROOF_CLASSES) == 3
        and all(row["paths_exist"] for row in rows)
        and all(packet["path_exists"] and packet["claim_ids_exist"] for packet in packets)
        and all(item["exists"] for item in intake_surface)
    )
    return {
        "program": PROGRAM_ID,
        "status": PROGRAM_STATUS,
        "primary_lanes": PRIMARY_LANES,
        "proof_classes": PROOF_CLASSES,
        "traceability_rows": rows,
        "review_packets": packets,
        "intake_surface": intake_surface,
        "counts": {
            "lane_count": len(PRIMARY_LANES),
            "proof_class_count": len(PROOF_CLASSES),
            "traceability_row_count": len(rows),
            "review_packet_count": len(packets),
        },
        "valid": valid,
    }


__all__ = [
    "PROGRAM_ID",
    "PROGRAM_STATUS",
    "LANE_A_ID",
    "LANE_B_ID",
    "PROOF_CLASS_UNCONDITIONAL",
    "PROOF_CLASS_CONDITIONAL",
    "PROOF_CLASS_EXECUTABLE",
    "PROOF_CLASSES",
    "PRIMARY_LANES",
    "TRACEABILITY_ROWS",
    "REVIEW_PACKETS",
    "INTAKE_SURFACE",
    "formal_traceability_spine",
]
