# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable proof-first Merlin packet for the Kawamura residual burden."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict, Protocol

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


class _MerlinProgramProtocol(Protocol):
    def get_proof_first_closure_charter(self) -> dict[str, Any]: ...

    def get_kawamura_closure_burden_ledger(self) -> dict[str, Any]: ...

    def get_merlin_cross_review_packet(self) -> dict[str, Any]: ...


def _load_program_module() -> _MerlinProgramProtocol:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module("ox_navigator.engine.merlin_program")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


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


def _normalize_article_contract(charter: dict[str, Any], article_text: str) -> tuple[str, dict[str, bool], bool]:
    target_gap_id = str(charter.get("target_gap_id", ""))
    article_contract = charter.get("article_contract") or {}
    required_sections_raw = article_contract.get("required_sections")
    required_sections = required_sections_raw if isinstance(required_sections_raw, list) else []
    required_sections_valid = isinstance(required_sections_raw, list)
    article_sections = _article_section_hits(article_text, required_sections)
    return target_gap_id, article_sections, required_sections_valid


def _normalize_ledger(ledger: dict[str, Any], target_gap_id: str) -> tuple[list[dict[str, Any]], bool, bool]:
    classification_buckets_raw = ledger.get("classification_buckets")
    classification_buckets = (
        classification_buckets_raw if isinstance(classification_buckets_raw, dict) else {}
    )
    open_residuals_raw = classification_buckets.get("open_residuals")
    open_items = open_residuals_raw if isinstance(open_residuals_raw, list) else []
    open_items_valid = isinstance(classification_buckets_raw, dict) and isinstance(open_residuals_raw, list)
    residual_match = any(str(item.get("gap_id", "")) == target_gap_id for item in open_items)
    return open_items, open_items_valid, residual_match


def _lean4_state(lean_text: str) -> dict[str, Any]:
    theorem_count = _count_theorems(lean_text)
    marker_hits = {marker: marker in lean_text for marker in _SEMANTIC_MARKERS}
    return {
        "file": _display_path(_LEAN4_FILE),
        "exists": _LEAN4_FILE.exists(),
        "theorem_count": theorem_count,
        "expected_theorem_count": _EXPECTED_THEOREM_COUNT,
        "semantic_markers": marker_hits,
    }


def _substack_state(article_sections: dict[str, bool]) -> dict[str, Any]:
    return {
        "path": _display_path(_SUBSTACK_POST),
        "exists": _SUBSTACK_POST.exists(),
        "required_sections": article_sections,
    }


def merlin_proof_first_kawamura_packet() -> Dict[str, Any]:
    program = _load_program_module()
    charter = program.get_proof_first_closure_charter()
    ledger = program.get_kawamura_closure_burden_ledger()
    cross_review = program.get_merlin_cross_review_packet()
    lean_text = _read_text(_LEAN4_FILE)
    article_text = _read_text(_SUBSTACK_POST)
    target_gap_id, article_sections, required_sections_valid = _normalize_article_contract(
        charter, article_text
    )
    open_items, open_items_valid, residual_match = _normalize_ledger(ledger, target_gap_id)
    lean4 = _lean4_state(lean_text)
    substack_article = _substack_state(article_sections)
    stewardship = charter.get("stewardship") or {}
    reconciliation_policy = cross_review.get("reconciliation_policy") or {}

    valid = bool(
        bool(target_gap_id)
        and required_sections_valid
        and open_items_valid
        and stewardship.get("default_final_verdict_until_residual_is_discharged") == "still_open"
        and ledger.get("target_gap_id") == target_gap_id
        and ledger.get("final_verdict_if_executed_today") == "still_open"
        and residual_match
        and reconciliation_policy.get("final_verdict_if_unresolved_objection") == "still_open"
        and lean4["exists"]
        and lean4["theorem_count"] == lean4["expected_theorem_count"]
        and all(lean4["semantic_markers"].values())
        and substack_article["exists"]
        and all(substack_article["required_sections"].values())
    )

    return {
        "target_gap_id": target_gap_id,
        "charter": charter,
        "burden_ledger": ledger,
        "cross_review_packet": cross_review,
        "open_residual_count": len(open_items),
        "lean4": lean4,
        "substack_article": substack_article,
        "final_verdict": "still_open",
        "valid": valid,
    }
