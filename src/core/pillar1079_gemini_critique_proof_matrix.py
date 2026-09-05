# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1079 — Gemini critique-to-proof execution matrix.

Builds a canonical, machine-readable mapping from each major external critique to:
  - current repository claim state,
  - evidence label (PROVED / CONSTRAINED / OPEN / INCORRECT_CRITIQUE),
  - required executable tightening work,
  - exact stop condition/falsifier.

Also includes a confabulation register for outdated/incorrect external claims and
an immutable-baseline guard for the already-published formal response artifacts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

PILLAR_NUMBER: int = 1079
PILLAR_GATE: str = "GEMINI_CRITIQUE_PROOF_MATRIX"
PILLAR_STATUS: str = "GEMINI_CRITIQUE_PROOF_MATRIX_COMPLETE"
VERSION: str = "v36.4"
SPRINT: str = "CH"
NEXT_PILLAR_SLOT: int = 1080

EVIDENCE_STATUS_ENUM = {
    "PROVED",
    "CONSTRAINED",
    "OPEN",
    "INCORRECT_CRITIQUE",
}

ROUTING_ENUM = {"PASS", "TENSION", "FALSIFIED"}

_ROOT = Path(__file__).resolve().parents[2]
_BASELINE_FORMAL_REVIEW = (
    _ROOT / "docs" / "reviews" / "GEMINI_REVIEW_FORMAL_RESPONSE_v36_3.md"
)
_BASELINE_SUBSTACK_RESPONSE = (
    _ROOT
    / "7-OUTREACH"
    / "substack"
    / "posts"
    / "post-314-s04e017-gemini-red-team-review-resolution.md"
)


def _baseline_lock() -> Dict[str, Any]:
    return {
        "formal_review_exists": _BASELINE_FORMAL_REVIEW.exists(),
        "substack_response_exists": _BASELINE_SUBSTACK_RESPONSE.exists(),
        "status": (
            "PASS"
            if _BASELINE_FORMAL_REVIEW.exists() and _BASELINE_SUBSTACK_RESPONSE.exists()
            else "FAIL"
        ),
    }


def _route_from_evidence_status(evidence_status: str) -> str:
    if evidence_status == "INCORRECT_CRITIQUE":
        return "PASS"
    if evidence_status in {"PROVED", "CONSTRAINED", "OPEN"}:
        return "TENSION"
    return "FALSIFIED"


def _matrix_rows() -> List[Dict[str, Any]]:
    rows = [
        {
            "critique_id": "G-1",
            "critique": "Λ_QCD omitted / unresolved ×10^7 core gap",
            "current_repository_claim": "Three-path Λ_QCD treatment exists (geometric primary + SM-RGE cross-check + perturbative suppressed path).",
            "evidence_status": "INCORRECT_CRITIQUE",
            "required_executable_work": "Keep three-path reconciliation and α_s architecture-limit lane explicitly separated in executable ledgers.",
            "exact_stop_condition_or_falsifier": "Any canonical ledger re-labels Λ_QCD as omitted/unimplemented without source changes.",
            "evidence_links": [
                "FALLIBILITY.md §ΛQCD STATUS BOX",
                "src/core/qcd_geometry_primary.py",
                "src/core/omega_qcd_phase_a.py",
            ],
            "lane_focus": "UV/QCD accounting",
            "formal_proof_links": [
                "lean4/UnitaryManifold/SprintCFTrackAFloorTheorems.lean",
            ],
        },
        {
            "critique_id": "G-2",
            "critique": "Fermion masses are fitted (c_L parameterization), not fully first-principles derived.",
            "current_repository_claim": "Charged-fermion c_L remains calibration-dependent; structural constraints improved, full derivation still open.",
            "evidence_status": "OPEN",
            "required_executable_work": "Tighten flavor blocker routing with deterministic shared-root packet and explicit unresolved-object carry-forward.",
            "exact_stop_condition_or_falsifier": "Runtime flavor lane flips to closure without a zero-external-input derivation artifact.",
            "evidence_links": [
                "FALLIBILITY.md §III Yukawa honesty note",
                "1-THEORY/DERIVATION_STATUS.md (first-principles c_L row)",
                "src/core/pillar1058_flavor_execution_packet.py",
            ],
            "lane_focus": "Flavor/c_L",
            "formal_proof_links": [
                "lean4/UnitaryManifold/DiracOrbifoldSpectrum.lean",
                "lean4/UnitaryManifold/OrbifoldBCUniqueness.lean",
            ],
        },
        {
            "critique_id": "G-3",
            "critique": "Neutrino sector remains incomplete.",
            "current_repository_claim": "Neutrino lane has partial closures and live external-gate dependencies; not fully zero-parameter closed.",
            "evidence_status": "CONSTRAINED",
            "required_executable_work": "Enforce observation-gated neutrino dependency routing and block narrative closure ahead of JUNO data.",
            "exact_stop_condition_or_falsifier": "IH confirmed >3σ or Δm²₂₁ excludes tracked UM support window.",
            "evidence_links": [
                "9-INFRASTRUCTURE/um_live_status.json (EXP-3)",
                "FALLIBILITY.md neutrino sections",
                "docs/CLAIM_MASTER_BOARD.md open-tension lanes",
            ],
            "lane_focus": "Neutrino dependencies",
            "formal_proof_links": [
                "lean4/UnitaryManifold/SprintBEBridge.lean",
            ],
        },
        {
            "critique_id": "G-4",
            "critique": "Dark-energy w_a=0 in unresolved DESI tension.",
            "current_repository_claim": "DESI tension is explicit and observation-gated; below canonical ≥3σ falsifier threshold in current ledgers.",
            "evidence_status": "CONSTRAINED",
            "required_executable_work": "Preserve deterministic DESI routing and no-post-hoc-softening threshold semantics across truth surfaces.",
            "exact_stop_condition_or_falsifier": "w_a ≠ 0 sustained at ≥3σ by pre-registered DESI criteria.",
            "evidence_links": [
                "docs/CLAIM_MASTER_BOARD.md (T1 row)",
                "src/core/pillar1075_desi_wa_rigidity_theorem.py",
                "src/core/observational_lane_freeze_registry.py",
            ],
            "lane_focus": "DESI external gate",
            "formal_proof_links": [
                "lean4/UnitaryManifold/SprintCFTrackCFalsifiers.lean",
            ],
        },
        {
            "critique_id": "G-5",
            "critique": "Tier-2/3 analogy modules and cold-fusion vertex gap are not hardgate derivations.",
            "current_repository_claim": "Formal-analogy boundary is explicit; cold-fusion lane keeps unresolved vertex/scale mismatch honest and open.",
            "evidence_status": "OPEN",
            "required_executable_work": "Keep explicit non-hardgate separation plus unresolved cold-fusion vertex/scale statements in canonical ledgers.",
            "exact_stop_condition_or_falsifier": "Any claim promotes analogy/cold-fusion lanes to hardgate without executable field-theoretic coupling closure.",
            "evidence_links": [
                "FALLIBILITY.md §XIV.4",
                "docs/CLAIM_MASTER_BOARD.md (adjacent-track labels)",
            ],
            "lane_focus": "Boundary integrity",
            "formal_proof_links": [
                "lean4/UnitaryManifold/SprintCAFormalTraceability.lean",
            ],
        },
    ]
    for row in rows:
        row["deterministic_routing"] = _route_from_evidence_status(
            str(row["evidence_status"])
        )
    return rows


def _confabulation_register(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    register = []
    for row in rows:
        if row["evidence_status"] != "INCORRECT_CRITIQUE":
            continue
        register.append(
            {
                "critique_id": row["critique_id"],
                "claim": row["critique"],
                "reason": "Claim is outdated/incorrect against canonical repository evidence.",
                "replaced_with": row["current_repository_claim"],
                "status": "CORRECTED",
            }
        )
    return register


def gemini_critique_proof_matrix() -> Dict[str, Any]:
    rows = _matrix_rows()
    baseline = _baseline_lock()
    confab = _confabulation_register(rows)
    evidence_ok = all(row["evidence_status"] in EVIDENCE_STATUS_ENUM for row in rows)
    routing_ok = all(row["deterministic_routing"] in ROUTING_ENUM for row in rows)
    structure_ok = all(
        bool(row["required_executable_work"]) and bool(row["exact_stop_condition_or_falsifier"])
        for row in rows
    )
    valid = (
        baseline["status"] == "PASS"
        and len(rows) == 5
        and evidence_ok
        and routing_ok
        and structure_ok
        and len(confab) >= 1
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "immutable_baseline_lock": baseline,
        "rows": rows,
        "confabulation_register": confab,
        "counts": {
            "pass": sum(1 for row in rows if row["deterministic_routing"] == "PASS"),
            "tension": sum(
                1 for row in rows if row["deterministic_routing"] == "TENSION"
            ),
            "falsified": sum(
                1 for row in rows if row["deterministic_routing"] == "FALSIFIED"
            ),
        },
        "valid": valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(gemini_critique_proof_matrix()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1079_summary() -> Dict[str, Any]:
    report = gemini_critique_proof_matrix()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Gemini Critique-to-Proof Execution Matrix",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "confabulation_entries": len(report["confabulation_register"]),
        "routing_counts": report["counts"],
    }

