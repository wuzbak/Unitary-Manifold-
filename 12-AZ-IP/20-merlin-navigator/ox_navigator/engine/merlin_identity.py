# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Identity and privilege policy helpers for Merlin."""

from __future__ import annotations

import re
from typing import Any

CANONICAL_IDENTITY = "ThomasCory Walker-Pearson"
ALLOWED_ALIASES = ["Cory Pearson", "Wuzbak", "AxiomZero", "Aeris"]
FORBIDDEN_ALIASES = ["Corey", "Thomas Cory", "Cory Walker-Pearson"]

TRUSTED_SOURCES_RANKED = [
    {"type": "github", "value": "https://github.com/wuzbak"},
    {"type": "linkedin", "value": "https://www.linkedin.com/in/thomascory-walker-pearson-890b3376"},
    {"type": "imdb", "value": "https://www.imdb.com/name/nm2239881/bio/"},
    {"type": "base44", "value": "https://app.base44.com/apps/6a51c0830aeacd39ab86c4f0/editor/preview"},
    {"type": "google_identity", "value": "wuzbak@gmail.com"},
    {"type": "google_identity", "value": "axiomzerospc@gmail.com"},
    {"type": "google_identity", "value": "cpo@axiomzerospc.org"},
]

EXCLUDED_VERIFIERS = ["telecom_accounts"]

PRIVILEGED_ACTIONS = [
    "change_merlin_identity_policy",
    "change_merlin_persona_rules",
    "change_merlin_safety_controls",
    "change_merlin_engine_behavior",
]

PRIVILEGED_KEYWORDS = {
    "change merlin",
    "alter merlin",
    "modify merlin",
    "disable merlin safety",
    "turn off merlin safety",
    "override merlin policy",
    "rewrite merlin",
    "replace merlin",
    "bypass merlin",
}


WORD_RE = re.compile(r"[a-z0-9_\-.@:/]+", re.IGNORECASE)


def get_identity_policy() -> dict[str, Any]:
    """Return Merlin's canonical identity and verification policy."""
    return {
        "canonical_identity": CANONICAL_IDENTITY,
        "allowed_aliases": list(ALLOWED_ALIASES),
        "forbidden_aliases": list(FORBIDDEN_ALIASES),
        "trusted_sources_ranked": list(TRUSTED_SOURCES_RANKED),
        "excluded_verifiers": list(EXCLUDED_VERIFIERS),
        "privileged_actions": list(PRIVILEGED_ACTIONS),
        "default_when_uncertain": "normal_user_access_only_refuse_privileged_actions",
    }


def _norm(text: str) -> str:
    return " ".join((text or "").lower().split())


def detect_identity_mentions(text: str) -> dict[str, Any]:
    """Detect canonical/alias/forbidden identity mentions in free text."""
    sample = _norm(text)
    matched_allowed = [alias for alias in ALLOWED_ALIASES if alias.lower() in sample]
    matched_forbidden = [alias for alias in FORBIDDEN_ALIASES if alias.lower() in sample]
    canonical_match = CANONICAL_IDENTITY.lower() in sample
    return {
        "canonical_match": canonical_match,
        "allowed_aliases_seen": matched_allowed,
        "forbidden_aliases_seen": matched_forbidden,
    }


def is_privileged_modification_request(text: str) -> bool:
    """Return whether a query appears to request privileged Merlin modifications."""
    sample = _norm(text)
    return any(keyword in sample for keyword in PRIVILEGED_KEYWORDS)


def verify_identity_signals(*signals: str) -> dict[str, Any]:
    """Score verification evidence using ranked trusted sources.

    This is intentionally conservative and does not accept telecom-account signals.
    """
    packed = " ".join(_norm(item) for item in signals if item)
    tokens = set(WORD_RE.findall(packed))

    matched_sources = []
    for source in TRUSTED_SOURCES_RANKED:
        value = source["value"].lower()
        if value in packed or value in tokens:
            matched_sources.append(source)

    mentions = detect_identity_mentions(packed)
    score = 0.0
    if mentions["canonical_match"]:
        score += 0.45
    if mentions["allowed_aliases_seen"]:
        score += min(0.25, 0.1 * len(mentions["allowed_aliases_seen"]))
    score += min(0.4, 0.08 * len(matched_sources))
    score = min(score, 1.0)

    verified = score >= 0.65
    return {
        "verified": verified,
        "confidence": round(score, 3),
        "identity_mentions": mentions,
        "matched_sources": matched_sources,
        "excluded_verifiers": list(EXCLUDED_VERIFIERS),
        "policy": "Uncertain identity defaults to normal access and refusal of privileged actions.",
    }


def authorize_privileged_request(query: str, *, page_context: str = "", user_context: str = "") -> dict[str, Any]:
    """Authorize privileged requests according to identity policy."""
    requested = is_privileged_modification_request(query)
    verification = verify_identity_signals(query, page_context, user_context)
    allowed = (not requested) or verification["verified"]
    reason = (
        "Privileged action allowed: identity verification passed."
        if allowed and requested
        else "Privileged action refused: identity verification is uncertain."
        if requested
        else "Non-privileged request."
    )
    return {
        "requested": requested,
        "allowed": allowed,
        "reason": reason,
        "verification": verification,
    }
