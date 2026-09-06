# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable proof-first Merlin packet for the Kawamura residual burden."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-merlin-navigator"
_LEAN4_FILE = _ROOT / "lean4" / "UnitaryManifold" / "MerlinProofFirstKawamuraLedger.lean"
_SUBSTACK_POST = _ROOT / "7-OUTREACH" / "substack" / "posts" / "post-320-s04e023-merlin-proof-first-kawamura-sprint.md"
_EXPECTED_THEOREM_COUNT = 8
_SEMANTIC_MARKERS = [
    "KawamuraResidualStillOpen",
    "NoTraceabilityEqualsClosure",
    "DualLoopVerdictAgreementRequired",
    "ExternalImportBoundaryPreserved",
]

_SECTION_HEADINGS = {
    "target_gap": "## The target gap",
    "method": "## The method",
    "merlin_contribution": "## What Merlin contributed",
    "cross_audit_result": "## What survived cross-audit",
    "remaining_residuals": "## What remains unresolved",
}


def _load_program_module():
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module("ox_navigator.engine.merlin_program")


def _count_theorems(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip().startswith("theorem mpf_kawamura_kernel_"))


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(_ROOT))
    except ValueError:
        return str(path)


def _article_section_hits(article_text: str, required_sections: list[str]) -> dict[str, bool]:
    return {
        section: _SECTION_HEADINGS.get(section, f"## {section.replace('_', ' ')}") in article_text
        for section in required_sections
    }


def merlin_proof_first_kawamura_packet() -> Dict[str, Any]:
    program = _load_program_module()
    charter = program.get_proof_first_closure_charter()
    ledger = program.get_kawamura_closure_burden_ledger()
    cross_review = program.get_merlin_cross_review_packet()
    lean_text = _LEAN4_FILE.read_text(encoding="utf-8") if _LEAN4_FILE.exists() else ""
    article_text = _SUBSTACK_POST.read_text(encoding="utf-8") if _SUBSTACK_POST.exists() else ""
    theorem_count = _count_theorems(lean_text)
    marker_hits = {marker: marker in lean_text for marker in _SEMANTIC_MARKERS}
    target_gap_id = str(charter.get("target_gap_id", ""))
    required_sections = list(charter.get("article_contract", {}).get("required_sections") or [])
    article_sections = _article_section_hits(article_text, required_sections)
    open_items = ledger["classification_buckets"]["open_residuals"]
    residual_match = any(str(item.get("gap_id", "")) == target_gap_id for item in open_items)

    valid = bool(
        bool(target_gap_id)
        and charter["stewardship"]["default_final_verdict_until_residual_is_discharged"] == "still_open"
        and ledger.get("target_gap_id") == target_gap_id
        and ledger["final_verdict_if_executed_today"] == "still_open"
        and residual_match
        and cross_review["reconciliation_policy"]["final_verdict_if_unresolved_objection"] == "still_open"
        and _LEAN4_FILE.exists()
        and theorem_count == _EXPECTED_THEOREM_COUNT
        and all(marker_hits.values())
        and _SUBSTACK_POST.exists()
        and all(article_sections.values())
    )

    return {
        "target_gap_id": charter["target_gap_id"],
        "charter": charter,
        "burden_ledger": ledger,
        "cross_review_packet": cross_review,
        "lean4": {
            "file": _display_path(_LEAN4_FILE),
            "exists": _LEAN4_FILE.exists(),
            "theorem_count": theorem_count,
            "expected_theorem_count": _EXPECTED_THEOREM_COUNT,
            "semantic_markers": marker_hits,
        },
        "substack_article": {
            "path": _display_path(_SUBSTACK_POST),
            "exists": _SUBSTACK_POST.exists(),
            "required_sections": article_sections,
        },
        "final_verdict": "still_open",
        "valid": valid,
    }
