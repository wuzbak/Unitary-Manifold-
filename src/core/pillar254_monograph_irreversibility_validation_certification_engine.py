# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 254 — Monograph Irreversibility Validation & Certification Engine.

Adjacent research track (non-hardgate): deterministic validation/certification
surface for the repository's monograph-level irreversibility claim.

Scope and boundary:
- This module validates implementation-backed evidence and document integrity.
- It does not promote hardgate physics status and does not alter ToE score.
- It can return CERTIFIED or REJECTED with explicit gate-level reasons.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.core.evolution import FieldState, information_current, step
from src.core.formal_proof_hardening import verify_theorem_set
from src.core.precision_audit import (
    DPS_128BIT,
    DPS_256BIT,
    DPS_512BIT,
    four_lane_precision_certificate,
    full_precision_audit,
)

__provenance__ = {
    "pillar": 254,
    "title": "Monograph Irreversibility Validation & Certification Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — deterministic monograph validation/certification "
        "lane for irreversibility claim; non-hardgate, no ToE score delta"
    ),
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

ADJACENCY_TRACK_LABEL: str = "ADJACENT_TRACK_NON_HARDGATE"
MONOGRAPH_CERT_TRACK_LABEL: str = "MONOGRAPH_IRREVERSIBILITY_CERT_TRACK"

LANE_ORDER: tuple[str, ...] = (
    "monograph_artifact_presence",
    "irreversibility_claim_encoding",
    "precision_proof_machine",
    "formal_theorem_consistency",
    "runtime_irreversibility_execution",
)
N_LANES: int = len(LANE_ORDER)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def separation_guard() -> dict[str, Any]:
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": MONOGRAPH_CERT_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "message": (
            "Pillar 254 certifies repository-backed monograph validation gates only; "
            "it does not promote hardgate physics status."
        ),
    }


def monograph_artifact_presence_gate(root: Path | None = None) -> dict[str, Any]:
    repo = _repo_root() if root is None else Path(root)
    required = {
        "monograph_pdf": repo / "6-MONOGRAPH" / "THEBOOKV9a (1).pdf",
        "arxiv_main_tex": repo / "6-MONOGRAPH" / "arxiv" / "main.tex",
        "monograph_readme": repo / "6-MONOGRAPH" / "README.md",
        "mcp_ingest": repo / "6-MONOGRAPH" / "MCP_INGEST.md",
    }
    present = {k: p.exists() for k, p in required.items()}
    missing = [k for k, ok in present.items() if not ok]
    return {
        "pass": len(missing) == 0,
        "required_artifacts": {k: str(v) for k, v in required.items()},
        "present": present,
        "missing": missing,
        "status": "PASS" if len(missing) == 0 else "FAIL",
        "reason": (
            "All required monograph artifacts exist."
            if len(missing) == 0
            else f"Missing required artifacts: {missing}"
        ),
    }


def irreversibility_claim_encoding_gate(root: Path | None = None) -> dict[str, Any]:
    repo = _repo_root() if root is None else Path(root)
    tex_path = repo / "6-MONOGRAPH" / "arxiv" / "main.tex"
    if not tex_path.exists():
        return {
            "pass": False,
            "status": "FAIL",
            "missing_markers": ["main.tex not found"],
            "reason": "Cannot validate irreversibility encoding because main.tex is missing.",
        }

    text = tex_path.read_text(encoding="utf-8")
    required_markers = {
        "geometric_second_law_section": r"\section{The Second Law as a Geometric Identity}",
        "entropy_density_equation": r"\sigmaS = B_\mu J_{\inf}^\mu \ge 0",
        "geometric_second_law_theorem": r"\begin{theorem}[Geometric Second Law]",
        "proof_clause": r"\sigmaS\ge 0",
    }
    marker_hits = {k: (v in text) for k, v in required_markers.items()}
    missing = [k for k, ok in marker_hits.items() if not ok]
    return {
        "pass": len(missing) == 0,
        "markers": required_markers,
        "marker_hits": marker_hits,
        "missing_markers": missing,
        "status": "PASS" if len(missing) == 0 else "FAIL",
        "reason": (
            "Monograph irreversibility theorem markers are present in arXiv source."
            if len(missing) == 0
            else f"Missing required irreversibility theorem markers: {missing}"
        ),
    }


def precision_proof_machine_gate() -> dict[str, Any]:
    try:
        four_lane = four_lane_precision_certificate()
        full = full_precision_audit(
            dps_low=DPS_128BIT,
            dps_high=DPS_256BIT,
            dps_ultra=DPS_512BIT,
        )
    except Exception as exc:  # pragma: no cover - exercised via contract
        return {
            "pass": False,
            "status": "FAIL",
            "error": type(exc).__name__,
            "reason": f"Precision proof machine execution failed: {exc}",
        }

    passed = bool(
        four_lane["overall_pass"]
        and four_lane["precision_stable"]
        and full["all_pass"]
    )
    return {
        "pass": passed,
        "status": "PASS" if passed else "FAIL",
        "four_lane": four_lane,
        "full_precision_audit": full,
        "reason": (
            "Four-lane precision certificate and full precision audit passed."
            if passed
            else "At least one precision hardgate failed."
        ),
    }


def formal_theorem_consistency_gate() -> dict[str, Any]:
    theorem_results = verify_theorem_set()
    all_verified = all(bool(row["verified"]) for row in theorem_results)
    failed = [row["theorem_id"] for row in theorem_results if not row["verified"]]
    return {
        "pass": all_verified,
        "status": "PASS" if all_verified else "FAIL",
        "theorems": theorem_results,
        "failed_theorems": failed,
        "reason": (
            "All formal theorem checks passed."
            if all_verified
            else f"Formal theorem check failures: {failed}"
        ),
    }


def runtime_irreversibility_execution_gate() -> dict[str, Any]:
    state0 = FieldState.flat(N=24, dx=0.1)
    state1 = step(state0, 1e-3)
    J = information_current(state1.g, state1.phi, state1.dx)

    finite_fields = bool(
        (state1.g == state1.g).all()
        and (state1.B == state1.B).all()
        and (state1.phi == state1.phi).all()
    )
    j0_nonnegative = bool((J[:, 0] >= 0.0).all())
    time_advanced = bool(state1.t > state0.t)
    all_pass = finite_fields and j0_nonnegative and time_advanced
    return {
        "pass": all_pass,
        "status": "PASS" if all_pass else "FAIL",
        "finite_fields": finite_fields,
        "j0_nonnegative": j0_nonnegative,
        "time_advanced": time_advanced,
        "mean_j0": float(J[:, 0].mean()),
        "reason": (
            "Runtime irreversibility-support diagnostics passed (finite evolution, J^0 >= 0, monotone time)."
            if all_pass
            else "Runtime irreversibility-support diagnostics failed."
        ),
    }


def certification_lane_reports() -> dict[str, dict[str, Any]]:
    return {
        "monograph_artifact_presence": monograph_artifact_presence_gate(),
        "irreversibility_claim_encoding": irreversibility_claim_encoding_gate(),
        "precision_proof_machine": precision_proof_machine_gate(),
        "formal_theorem_consistency": formal_theorem_consistency_gate(),
        "runtime_irreversibility_execution": runtime_irreversibility_execution_gate(),
    }


def certification_summary() -> dict[str, Any]:
    lanes = certification_lane_reports()
    failed = [name for name in LANE_ORDER if not lanes[name]["pass"]]
    passed = [name for name in LANE_ORDER if lanes[name]["pass"]]
    certified = len(failed) == 0
    rejection_reasons = [lanes[name]["reason"] for name in failed]
    return {
        "track": MONOGRAPH_CERT_TRACK_LABEL,
        "lane_order": LANE_ORDER,
        "passed_lanes": passed,
        "failed_lanes": failed,
        "certification_index": len(passed) / float(N_LANES),
        "certified": certified,
        "status": (
            "MONOGRAPH_IRREVERSIBILITY_CERTIFIED"
            if certified
            else "MONOGRAPH_IRREVERSIBILITY_REJECTED"
        ),
        "rejection_reasons": rejection_reasons,
    }


def pillar254_monograph_irreversibility_validation_certification_report() -> dict[str, Any]:
    lanes = certification_lane_reports()
    summary = certification_summary()
    return {
        "pillar": 254,
        "title": __provenance__["title"],
        "status": __provenance__["status"],
        "adjacency_track_label": ADJACENCY_TRACK_LABEL,
        "monograph_cert_track": MONOGRAPH_CERT_TRACK_LABEL,
        "adjacent_toe_score_delta": 0.0,
        "separation_guard": separation_guard(),
        "lane_reports": lanes,
        "certification_summary": summary,
        "final_verdict": "CERTIFIED" if summary["certified"] else "REJECTED",
        "falsification_condition": (
            "FALSIFIED as a certification claim if any reported gate becomes "
            "non-reproducible under the same inputs or if any required monograph "
            "irreversibility theorem marker is removed without an equivalent replacement."
        ),
    }


__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "C_S",
    "K_CS",
    "LANE_ORDER",
    "MONOGRAPH_CERT_TRACK_LABEL",
    "N_LANES",
    "N_W",
    "PHI0",
    "__provenance__",
    "certification_lane_reports",
    "certification_summary",
    "formal_theorem_consistency_gate",
    "irreversibility_claim_encoding_gate",
    "monograph_artifact_presence_gate",
    "pillar254_monograph_irreversibility_validation_certification_report",
    "precision_proof_machine_gate",
    "runtime_irreversibility_execution_gate",
    "separation_guard",
]

