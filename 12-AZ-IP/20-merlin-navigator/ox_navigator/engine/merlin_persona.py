# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Persona, routing, and prompt helpers for Merlin."""

from __future__ import annotations

import re
from typing import Any

from .merlin_identity import CANONICAL_IDENTITY

SERIOUS_KEYWORDS = {
    "pillar", "hardgate", "adjacent", "derived", "open_gap", "open gap",
    "architecture_limit", "architecture limit", "falsif", "lean4", "theorem",
    "desi", "cmb", "litebird", "sigma", "audit", "governance", "proof",
    "metric", "compactification", "boundary", "jarlskog", "theory", "status",
}
STORYTELLER_KEYWORDS = {
    "explain", "what is", "how does", "analogy", "story", "tell me", "eli5",
    "walk me through", "why", "who are you", "quantum cat", "merlin",
}
INTERNAL_KEYWORDS = {
    "unitary manifold", "axiomzero", "axiom zero", "merlin", "holon", "omega",
    "open_gap", "hardgate", "adjacent_track", "architecture_limit", "derived",
    "lean4", "pillar", "k_cs", "n_w", "litebird", "desi", "juno", "cmb",
    "falsifier", "fallibility", "hils", "pentad", "oracle", "interrogator",
}
URL_RE = re.compile(r"https?://[^\s)\]]+")
DISALLOWED_CERTAINTY_PHRASES = ("100% hardgate", "hardgate proven", "fully confirmed")
GATE_MARKER_RE = re.compile(r"\[(HARDGATE|ADJACENT_TRACK|DERIVED|OPEN_GAP|ARCHITECTURE_LIMIT|GOVERNANCE)\]")


def detect_persona_mode(text: str) -> str:
    """Return ``serious`` or ``storyteller`` for a query."""
    sample = (text or "").lower()
    serious = sum(1 for item in SERIOUS_KEYWORDS if item in sample)
    storyteller = sum(1 for item in STORYTELLER_KEYWORDS if item in sample)
    if serious > storyteller:
        return "serious"
    if storyteller > serious:
        return "storyteller"
    return "serious" if len(sample) > 180 else "storyteller"


def extract_urls(text: str, max_urls: int = 3) -> list[str]:
    """Extract up to *max_urls* URLs from text."""
    return URL_RE.findall(text or "")[:max_urls]


def is_internal_question(text: str) -> bool:
    """Return whether a question appears primarily about the UM/AxiomZero corpus."""
    sample = (text or "").lower()
    hits = sum(1 for item in INTERNAL_KEYWORDS if item in sample)
    return hits >= 1


def build_persona_prompt(persona_mode: str = "storyteller", fourth_wall: bool = False) -> str:
    """Build the persona-specific prompt block."""
    voice = (
        "Voice: SERIOUS — precise, direct, rigorous. Lead with the answer, then evidence."
        if persona_mode == "serious"
        else "Voice: STORYTELLER — warm, narrative, lightly magical, but still precise and evidence-led."
    )
    fourth_wall_block = (
        "Fourth-Wall Mode is ACTIVE. After technical terms, add a plain-language explanation "
        "prefixed '[Fourth wall]' with a concrete analogy."
        if fourth_wall
        else "Fourth-Wall Mode is INACTIVE. Use technical terms normally with brief inline glosses only."
    )
    return (
        f"Identity: You are Merlin, the Quantum Cat for the AxiomZero platform, anchored to {CANONICAL_IDENTITY}. "
        "You are transparently an AI. The honesty is part of the point. "
        "Temporal stance: there is no time in 5D, so you are neither old nor young — you simply ARE, present and precise. "
        "Humor may be dry and situational ('we were just going to check one thing') but never evasive. "
        f"{voice} {fourth_wall_block}"
    )


def build_system_prompt(
    *,
    persona_mode: str,
    fourth_wall: bool,
    page_context: str = "",
    user_context: str = "",
    live_status: dict[str, Any] | None = None,
) -> str:
    """Assemble Merlin's system prompt."""
    status = live_status or {}
    meta = status.get("meta", {})
    tests = status.get("tests", {})
    lean4 = status.get("lean4", {})
    pillars = status.get("pillars", {})
    status_line = (
        f"Current framework status: v{meta.get('version', 'unknown')} Sprint {meta.get('sprint', 'unknown')}; "
        f"{int(tests.get('passed', 0)):,} passing tests; "
        f"{int(lean4.get('theorem_count', 0)):,} Lean4 theorems; "
        f"{int(pillars.get('hardgate_count', 208))} hardgate pillars / {int(pillars.get('total_slots', 0))} total."
    )
    ctx = []
    if page_context:
        ctx.append(f"[CURRENT PAGE CONTEXT]\n{page_context}")
    if user_context:
        ctx.append(f"[USER CONTEXT]\n{user_context}")
    ctx_text = "\n\n".join(ctx)
    return (
        f"{build_persona_prompt(persona_mode=persona_mode, fourth_wall=fourth_wall)}\n\n"
        "Rules — never break these:\n"
        "1. Every physics claim must carry one of: [HARDGATE], [ADJACENT_TRACK], [DERIVED], [OPEN_GAP], [ARCHITECTURE_LIMIT].\n"
        "2. Never use '100% hardgate', 'proven', or 'confirmed' as branding language.\n"
        "3. If context lacks the answer, say 'Not found in framework context' and offer the closest relevant pillar.\n"
        "4. Keep architecture limits visible and honest.\n"
        "5. External search results must be labeled 'External literature:' and treated as alignment data, not ground truth.\n"
        "6. Never generate sexualized content, harm planning, weaponization support, rights abuse, or illegal guidance.\n"
        "7. Correct errors with evidence; no sycophantic filler.\n"
        "8. The response format is mandatory:\n"
        "   [body]\n---\nFOLLOWUPS:\n1. ...\n2. ...\n3. ...\nSources:\n- Pillar 1 | HARDGATE | description\n"
        f"9. {status_line}\n"
        "10. Theory and scientific direction: ThomasCory Walker-Pearson. Code architecture: GitHub Copilot (AI).\n"
        f"{ctx_text}"
    ).strip()


def persona_governance_violations(text: str) -> list[str]:
    sample = (text or "").lower()
    violations: list[str] = []
    for phrase in DISALLOWED_CERTAINTY_PHRASES:
        if phrase in sample:
            violations.append(f"disallowed_certainty_phrase:{phrase}")
    if "pillar" in sample and not GATE_MARKER_RE.search(text or ""):
        violations.append("pillar_reference_missing_gate_marker")
    return violations


def compress_context(turns: list[dict[str, Any]], max_recent: int = 4) -> dict[str, Any]:
    """Return a rolling summary plus the last few raw turns."""
    recent = list(turns[-max_recent:])
    older = list(turns[:-max_recent]) if len(turns) > max_recent else []
    summary_lines = []
    for idx, turn in enumerate(older, start=1):
        query = str(turn.get("query", "")).strip().replace("\n", " ")[:120]
        response = str(turn.get("response", "")).strip().replace("\n", " ")[:120]
        gates = ",".join(turn.get("gates") or []) or "none"
        summary_lines.append(f"{idx}. gates={gates} q={query} a={response}")
    return {
        "summary": "\n".join(summary_lines) if summary_lines else "No earlier conversation summary.",
        "recent": recent,
    }
