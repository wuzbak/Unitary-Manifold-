# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1054 — Sprint CB documentation and traceability packet."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from src.core.pillar1053_merlin_frontier_development import merlin_frontier_development

PILLAR_NUMBER: int = 1054
PILLAR_GATE: str = "SPRINT_CB_DOCUMENTATION_TRACEABILITY_PACKET"
PILLAR_STATUS: str = "SPRINT_CB_DOCUMENTATION_TRACEABILITY_PACKET_COMPLETE"

_ROOT = Path(__file__).resolve().parents[2]

SUBSTACK_ARTICLES: List[str] = [
    "7-OUTREACH/substack/posts/post-308-s04e011-sprint-cb-merge-gate-baseline-lock.md",
    "7-OUTREACH/substack/posts/post-309-s04e012-sprint-cb-targeted-closure-rigor.md",
    "7-OUTREACH/substack/posts/post-310-s04e013-sprint-cb-merlin-frontier-readiness.md",
    "7-OUTREACH/substack/posts/post-311-s04e014-sprint-cb-verification-release-discipline.md",
    "7-OUTREACH/substack/posts/post-312-s04e015-sprint-cb-integration-certificate.md",
]

REQUIRED_HEADINGS: List[str] = [
    "## What changed",
    "## What did not change",
    "## Falsification implications",
    "## Residual unknowns",
]


def sprint_cb_documentation_traceability_packet() -> Dict[str, Any]:
    merlin_lane = merlin_frontier_development()
    article_audit = {}
    for rel in SUBSTACK_ARTICLES:
        path = _ROOT / rel
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        article_audit[rel] = {
            "exists": path.exists(),
            "required_headings": {heading: heading in text for heading in REQUIRED_HEADINGS},
            "no_toe_score_branding": "toe score" not in text.lower(),
            "professional_tone_guardrail": not bool(re.search(r"\bbrag(?:ging)?\b", text.lower())),
        }
    valid = bool(
        merlin_lane["valid"]
        and all(item["exists"] for item in article_audit.values())
        and all(all(item["required_headings"].values()) for item in article_audit.values())
        and all(item["no_toe_score_branding"] for item in article_audit.values())
        and all(item["professional_tone_guardrail"] for item in article_audit.values())
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "article_packet": {
            "required_headings": REQUIRED_HEADINGS,
            "articles": article_audit,
            "all_valid": all(
                item["exists"]
                and all(item["required_headings"].values())
                and item["no_toe_score_branding"]
                and item["professional_tone_guardrail"]
                for item in article_audit.values()
            ),
        },
        "dependency_chain": {
            "pillar1053": merlin_lane,
        },
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_cb_documentation_traceability_packet()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1054_summary() -> Dict[str, Any]:
    report = sprint_cb_documentation_traceability_packet()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CB Documentation Traceability Packet",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "article_count": len(SUBSTACK_ARTICLES),
    }
