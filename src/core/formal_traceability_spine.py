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

import re
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
_RUNTIME_ALIGNMENT_FILE_TARGETS: List[str] = [
    "src/core/evolution.py",
]
_RUNTIME_ALIGNMENT_DIR_TARGETS: List[str] = [
    "12-AZ-IP/20-psicat-navigator/ox_navigator/engine",
    "12-AZ-IP/20-psicat-navigator/ox_navigator/app",
    "12-AZ-IP/20-psicat-navigator/tools",
]

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
            "src/core/action_to_evolution_contract.py",
            "src/core/evolution.py",
            "src/core/pillar1082_foundation_first_photon_action_audit.py",
        ],
        "primary_tests": [
            "tests/test_action_to_evolution_contract.py",
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
            "src/core/action_to_evolution_contract.py",
            "src/core/evolution.py",
            "src/core/pillar1082_foundation_first_photon_action_audit.py",
        ],
        "tests": [
            "tests/test_action_to_evolution_contract.py",
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
    "proof/CURRY_HOWARD_WORKFLOW.md",
    "proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md",
    "proof/PSICAT_NAVIER_STOKES_CURRICULUM_PACKET.md",
    "proof/PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER_PACKET.md",
    "docs/TRUTH_LAYER.md",
]

CurryHowardRow = Dict[str, str]

CURRY_HOWARD_MATRIX: List[CurryHowardRow] = [
    {
        "logic_side": "Proposition",
        "program_side": "Type",
        "lean_surface": "Prop",
        "repository_example": "lean4/UnitaryManifold/NWUniquenessHonest.lean::proof_distance_map",
    },
    {
        "logic_side": "Proof",
        "program_side": "Term / value",
        "lean_surface": "theorem body / exact term",
        "repository_example": "lean4/UnitaryManifold/SprintCAFormalTraceability.lean::ca_trace_kernel_02",
    },
    {
        "logic_side": "Implication",
        "program_side": "Function type",
        "lean_surface": "A → B",
        "repository_example": "lean4/UnitaryManifold/SprintCAFormalTraceability.lean::ca_trace_kernel_02",
    },
    {
        "logic_side": "Conjunction",
        "program_side": "Product type",
        "lean_surface": "A ∧ B",
        "repository_example": "lean4/UnitaryManifold/NWUniquenessHonest.lean::proof_distance_map",
    },
    {
        "logic_side": "Disjunction",
        "program_side": "Sum type",
        "lean_surface": "A ∨ B",
        "repository_example": "lean4/UnitaryManifold/SprintCAFormalTraceability.lean::ca_trace_kernel_06",
    },
    {
        "logic_side": "Falsehood",
        "program_side": "Empty type",
        "lean_surface": "False / ¬ (p ∧ ¬ p)",
        "repository_example": "lean4/UnitaryManifold/SprintCAFormalTraceability.lean::ca_trace_kernel_07",
    },
]

PSICAT_TRAINING_MANIFEST: Dict[str, Any] = {
    "target_product": "12-AZ-IP/20-psicat-navigator",
    "training_corpus": [
        "proof/README.md",
        "proof/TIER_1_FORMAL.md",
        "proof/FORMAL_PROOF_FOUNDRY.md",
        "proof/CURRY_HOWARD_WORKFLOW.md",
        "proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md",
        "proof/REVIEW_PACKET_ACTION_TO_EVOLUTION.md",
        "proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md",
        "proof/PSICAT_NAVIER_STOKES_CURRICULUM_PACKET.md",
        "proof/PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER_PACKET.md",
        "docs/TRUTH_LAYER.md",
    ],
    "registry_sources": [
        "src/core/formal_traceability_spine.py",
        "src/core/lean_python_bridge_ir.py",
        "src/core/navier_stokes_method_transfer.py",
        "src/core/pythagorean_triples_sat_method_transfer.py",
        "tests/test_formal_traceability_spine.py",
    ],
    "export_tools": [
        "12-AZ-IP/20-psicat-navigator/tools/export_merlin_stage_a_artifacts.py",
        "12-AZ-IP/20-psicat-navigator/tools/export_merlin_lean_bridge_artifact.py",
        "12-AZ-IP/20-psicat-navigator/tools/export_merlin_training_artifacts.py",
        "12-AZ-IP/20-psicat-navigator/tools/export_merlin_training_jsonl.py",
        "12-AZ-IP/20-psicat-navigator/tools/export_merlin_mlflow_manifests.py",
    ],
    "benchmark_tools": [
        "12-AZ-IP/20-psicat-navigator/tools/run_merlin_stage_a_benchmarks.py",
        "12-AZ-IP/20-psicat-navigator/tools/run_merlin_stage_bc_benchmarks.py",
    ],
}


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


def _iter_runtime_alignment_candidates() -> List[Path]:
    candidates: List[Path] = []
    seen: set[Path] = set()
    for rel_path in _RUNTIME_ALIGNMENT_FILE_TARGETS:
        file_path = (_ROOT / rel_path).resolve()
        if file_path.is_file() and file_path not in seen:
            candidates.append(file_path)
            seen.add(file_path)
    for rel_dir in _RUNTIME_ALIGNMENT_DIR_TARGETS:
        base = (_ROOT / rel_dir).resolve()
        if not base.is_dir():
            continue
        for file_path in sorted(base.rglob("*.py")):
            resolved = file_path.resolve()
            if resolved in seen:
                continue
            candidates.append(resolved)
            seen.add(resolved)
    return candidates


def _detect_runtime_alignment() -> Dict[str, Any]:
    patterns = [
        re.compile(r"import\s+Lean\b"),
        re.compile(r"from\s+Lean\b"),
        re.compile(r"subprocess\..*lake"),
        re.compile(r"subprocess\..*lean"),
        re.compile(r"['\"]lake build['\"]"),
    ]
    scan_paths = _iter_runtime_alignment_candidates()
    hits: List[str] = []
    for path in scan_paths:
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if any(pattern.search(text) for pattern in patterns):
            hits.append(path.relative_to(_ROOT).as_posix())
    direct = bool(hits)
    return {
        "mode": "DIRECT_OR_HYBRID_INTEGRATION" if direct else "MANUAL_PORT_WITH_TRACEABILITY",
        "direct_lean_runtime_detected": direct,
        "evidence_files": hits,
        "scan_scope": {
            "file_targets": list(_RUNTIME_ALIGNMENT_FILE_TARGETS),
            "dir_targets": list(_RUNTIME_ALIGNMENT_DIR_TARGETS),
            "scanned_python_file_count": len(scan_paths),
        },
        "summary": (
            "Python runtime appears to invoke or reference Lean build/runtime artifacts directly."
            if direct
            else "No direct Lean-term runtime invocation was detected in Python; the current bridge is manual porting with explicit traceability."
        ),
    }


def formal_traceability_spine() -> Dict[str, Any]:
    """Return the canonical formal frontier registry."""
    from src.core.lean_python_bridge_ir import build_python_lean_bridge_contract

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
    runtime_alignment = _detect_runtime_alignment()
    bridge_contract = build_python_lean_bridge_contract(
        rows=rows,
        primary_lanes=PRIMARY_LANES,
        runtime_alignment=runtime_alignment,
    )
    psicat_training = {
        "target_product": PSICAT_TRAINING_MANIFEST["target_product"],
        "training_corpus": [
            {"path": path, "exists": _path_exists(path)}
            for path in PSICAT_TRAINING_MANIFEST["training_corpus"]
        ],
        "registry_sources": [
            {"path": path, "exists": _path_exists(path)}
            for path in PSICAT_TRAINING_MANIFEST["registry_sources"]
        ],
        "export_tools": [
            {"path": path, "exists": _path_exists(path)}
            for path in PSICAT_TRAINING_MANIFEST["export_tools"]
        ],
        "benchmark_tools": [
            {"path": path, "exists": _path_exists(path)}
            for path in PSICAT_TRAINING_MANIFEST["benchmark_tools"]
        ],
        "training_ready": True,
    }
    psicat_training["training_ready"] = bool(
        all(item["exists"] for item in psicat_training["training_corpus"])
        and all(item["exists"] for item in psicat_training["registry_sources"])
        and all(item["exists"] for item in psicat_training["export_tools"])
        and all(item["exists"] for item in psicat_training["benchmark_tools"])
    )
    valid = bool(
        len(PRIMARY_LANES) == 2
        and len(PROOF_CLASSES) == 3
        and all(row["paths_exist"] for row in rows)
        and all(packet["path_exists"] and packet["claim_ids_exist"] for packet in packets)
        and all(item["exists"] for item in intake_surface)
        and psicat_training["training_ready"]
    )
    return {
        "program": PROGRAM_ID,
        "status": PROGRAM_STATUS,
        "primary_lanes": PRIMARY_LANES,
        "proof_classes": PROOF_CLASSES,
        "curry_howard_matrix": CURRY_HOWARD_MATRIX,
        "runtime_alignment": runtime_alignment,
        "python_lean_bridge_contract": bridge_contract,
        "traceability_rows": rows,
        "review_packets": packets,
        "intake_surface": intake_surface,
        "psicat_training_manifest": psicat_training,
        "counts": {
            "lane_count": len(PRIMARY_LANES),
            "proof_class_count": len(PROOF_CLASSES),
            "curry_howard_row_count": len(CURRY_HOWARD_MATRIX),
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
    "CURRY_HOWARD_MATRIX",
    "PSICAT_TRAINING_MANIFEST",
    "formal_traceability_spine",
]
