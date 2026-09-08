# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable proof-first Merlin packet for the Kawamura residual burden."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Protocol

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-phicat-navigator"
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
    get_proof_first_closure_charter: Callable[[], dict[str, Any]]
    get_kawamura_closure_burden_ledger: Callable[[], dict[str, Any]]
    get_merlin_cross_review_packet: Callable[[], dict[str, Any]]


@dataclass
class _PacketState:
    target_gap_id: str = ""
    charter: dict[str, Any] = field(default_factory=dict)
    ledger: dict[str, Any] = field(default_factory=dict)
    cross_review: dict[str, Any] = field(default_factory=dict)
    article_path: Path = _SUBSTACK_POST
    article_sections: dict[str, bool] = field(default_factory=dict)


def _load_program_module() -> _MerlinProgramProtocol:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module("ox_navigator.engine.merlin_program")


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


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


def _resolve_repo_path(path_value: str | None, default: Path) -> tuple[Path, bool]:
    if path_value is None:
        return default, True
    if not isinstance(path_value, str) or not path_value:
        return default, False
    candidate = (_ROOT / path_value).resolve()
    try:
        candidate.relative_to(_ROOT)
    except ValueError:
        return default, False
    return candidate, True


def _normalize_article_contract(charter: dict[str, Any]) -> tuple[str, Path, bool, list[str], bool]:
    target_gap_id = str(charter.get("target_gap_id", ""))
    article_contract = charter.get("article_contract") or {}
    configured_path, configured_path_valid = _resolve_repo_path(
        article_contract.get("path"), _SUBSTACK_POST
    )
    required_sections_raw = article_contract.get("required_sections")
    required_sections = required_sections_raw if isinstance(required_sections_raw, list) else []
    required_sections_valid = isinstance(required_sections_raw, list)
    return target_gap_id, configured_path, configured_path_valid, required_sections, required_sections_valid


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


def _substack_state(article_path: Path, article_sections: dict[str, bool]) -> dict[str, Any]:
    return {
        "path": _display_path(article_path),
        "exists": article_path.exists(),
        "required_sections": article_sections,
    }


def _fail_closed_packet(state: _PacketState) -> Dict[str, Any]:
    classification_buckets = state.ledger.get("classification_buckets") or {}
    open_residuals = (
        classification_buckets.get("open_residuals") if isinstance(classification_buckets, dict) else None
    )
    open_residual_count = len(open_residuals) if isinstance(open_residuals, list) else 0
    return {
        "target_gap_id": state.target_gap_id,
        "charter": state.charter,
        "burden_ledger": state.ledger,
        "cross_review_packet": state.cross_review,
        "open_residual_count": open_residual_count,
        "lean4": _lean4_state(_read_text(_LEAN4_FILE)),
        "substack_article": _substack_state(state.article_path, state.article_sections),
        "final_verdict": "still_open",
        "valid": False,
    }


def merlin_proof_first_kawamura_packet() -> Dict[str, Any]:
    state = _PacketState()
    try:
        program = _load_program_module()
    except (ImportError, ModuleNotFoundError, FileNotFoundError):
        return _fail_closed_packet(state)

    try:
        state.charter = program.get_proof_first_closure_charter()
        state.ledger = program.get_kawamura_closure_burden_ledger()
        state.cross_review = program.get_merlin_cross_review_packet()
    except Exception:
        return _fail_closed_packet(state)

    lean_text = _read_text(_LEAN4_FILE)
    (
        state.target_gap_id,
        state.article_path,
        article_path_valid,
        required_sections,
        required_sections_valid,
    ) = _normalize_article_contract(state.charter)
    article_text = _read_text(state.article_path)
    state.article_sections = _article_section_hits(article_text, required_sections)
    open_items, open_items_valid, residual_match = _normalize_ledger(
        state.ledger, state.target_gap_id
    )
    lean4 = _lean4_state(lean_text)
    substack_article = _substack_state(state.article_path, state.article_sections)
    stewardship = state.charter.get("stewardship") or {}
    reconciliation_policy = state.cross_review.get("reconciliation_policy") or {}

    valid = bool(
        bool(state.target_gap_id)
        and article_path_valid
        and required_sections_valid
        and open_items_valid
        and stewardship.get("default_final_verdict_until_residual_is_discharged") == "still_open"
        and state.ledger.get("target_gap_id") == state.target_gap_id
        and state.ledger.get("final_verdict_if_executed_today") == "still_open"
        and residual_match
        and state.cross_review.get("target_gap_id") == state.target_gap_id
        and reconciliation_policy.get("final_verdict_if_unresolved_objection") == "still_open"
        and lean4["exists"]
        and lean4["theorem_count"] == lean4["expected_theorem_count"]
        and all(lean4["semantic_markers"].values())
        and substack_article["exists"]
        and all(substack_article["required_sections"].values())
    )

    return {
        "target_gap_id": state.target_gap_id,
        "charter": state.charter,
        "burden_ledger": state.ledger,
        "cross_review_packet": state.cross_review,
        "open_residual_count": len(open_items),
        "lean4": lean4,
        "substack_article": substack_article,
        "final_verdict": "still_open",
        "valid": valid,
    }
