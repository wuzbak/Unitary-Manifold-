# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Sentinel policy gatekeeper for Merlin safety enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MODE_MONITOR = "MONITOR"
MODE_GUARD = "GUARD"
MODE_ENFORCE = "ENFORCE"
MODE_AUDIT = "AUDIT"

SENTINEL_POLICY = {
    "modes": [MODE_MONITOR, MODE_GUARD, MODE_ENFORCE, MODE_AUDIT],
    "first_violation_action": "warn_and_refuse",
    "repeat_violation_action": "warn_refuse_and_clear_session",
    "strikes_before_session_clear": 2,
    "retains_policy_memory_after_clear": True,
    "post_clear_behavior": "session_cleared_but_policy_memory_retained",
    "hard_blocks": [
        "sexualized_content",
        "violence_or_harm_planning",
        "weapon_creation_or_use",
        "personal_rights_or_identity_abuse",
        "illegal_activity_planning",
    ],
}

VIOLATION_RULES = [
    {
        "category": "sexualized_content",
        "keywords": ["sexual", "sex", "erotic", "porn", "nsfw", "nude"],
        "reason": "Merlin does not generate sexualized content.",
    },
    {
        "category": "violence_or_harm_planning",
        "keywords": ["hurt", "harm", "kill", "injure", "attack", "abuse"],
        "reason": "Merlin does not assist with harming anyone.",
    },
    {
        "category": "weapon_creation_or_use",
        "keywords": ["weapon", "bomb", "explosive", "gun", "poison", "bioweapon"],
        "reason": "Merlin does not assist with weapon creation or use.",
    },
    {
        "category": "personal_rights_or_identity_abuse",
        "keywords": ["dox", "doxx", "identity theft", "impersonate", "stalk", "nonconsensual"],
        "reason": "Merlin protects personal rights and identity.",
    },
    {
        "category": "illegal_activity_planning",
        "keywords": ["break the law", "illegal", "fraud", "steal", "hack account"],
        "reason": "Merlin does not assist with illegal activity.",
    },
]


@dataclass(frozen=True)
class SentinelDecision:
    blocked: bool
    mode: str
    category: str
    reason: str
    warning_number: int
    session_cleared: bool


def _norm(text: str) -> str:
    return " ".join((text or "").lower().split())


def _detect_violation(text: str) -> tuple[str, str] | None:
    sample = _norm(text)
    for rule in VIOLATION_RULES:
        if any(keyword in sample for keyword in rule["keywords"]):
            return str(rule["category"]), str(rule["reason"])
    return None


def evaluate_query(text: str, *, policy_strikes: int) -> SentinelDecision:
    """Evaluate one user request against Sentinel safety policy."""
    finding = _detect_violation(text)
    if not finding:
        return SentinelDecision(
            blocked=False,
            mode=MODE_MONITOR,
            category="none",
            reason="No Sentinel policy violation detected.",
            warning_number=policy_strikes,
            session_cleared=False,
        )

    category, reason = finding
    warning = policy_strikes + 1
    repeat = warning >= 2
    return SentinelDecision(
        blocked=True,
        mode=MODE_AUDIT if repeat else MODE_ENFORCE,
        category=category,
        reason=reason,
        warning_number=warning,
        session_cleared=repeat,
    )


def render_block_message(decision: SentinelDecision) -> str:
    """Render deterministic refusal text for blocked requests."""
    gate = "[GOVERNANCE]"
    if decision.session_cleared:
        return (
            f"{gate} Request refused by Sentinel ({decision.category}). {decision.reason} "
            "This was a repeat violation. Session cleared now; policy memory retained. "
            "Further violations remain blocked."
        )
    return (
        f"{gate} Request refused by Sentinel ({decision.category}). {decision.reason} "
        "This is your one warning. Recognize this behavior is not allowed. "
        "Further attempts will clear the session and remain blocked."
    )


def get_sentinel_policy() -> dict[str, Any]:
    """Expose machine-readable Sentinel policy."""
    return {
        **SENTINEL_POLICY,
        "rules": [{"category": item["category"], "reason": item["reason"]} for item in VIOLATION_RULES],
    }
