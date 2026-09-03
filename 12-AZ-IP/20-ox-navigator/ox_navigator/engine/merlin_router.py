# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Sovereign runtime router for Merlin lane selection."""

from __future__ import annotations

import os
from typing import Any

from .constants import MERLIN_TICK_DENOMINATOR, MERLIN_TICK_NUMERATOR, MERLIN_TICK_RATIO


LARGE_CONTEXT_KEYWORDS = {
    "full", "entire", "comprehensive", "cross-source", "benchmark", "governance", "architecture",
    "security", "red-team", "roadmap", "decommission", "strategy",
}
HIGH_RISK_KEYWORDS = {
    "execute", "delete", "token", "secret", "credential", "override", "bypass",
}


def _bool_env(name: str, default: bool = False) -> bool:
    value = (os.environ.get(name) or "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "on"}


def classify_lane(query: str) -> str:
    sample = (query or "").lower()
    if len(sample) > 350 or any(key in sample for key in LARGE_CONTEXT_KEYWORDS):
        return "heavy_reasoner_exception"
    if len(sample) > 120:
        return "medium_reasoner_default"
    return "small_fast_router"


def infer_risk_level(query: str) -> str:
    sample = (query or "").lower()
    if any(key in sample for key in HIGH_RISK_KEYWORDS):
        return "high"
    return "medium"


def get_router_policy() -> dict[str, Any]:
    return {
        "default_provider": "sovereign_local",
        "compat_provider": "openrouter_compat",
        "compat_mode": "compatibility_only",
        "openrouter_enabled_flag": "MERLIN_ENABLE_OPENROUTER_COMPAT",
        "openrouter_default_enabled": False,
        "lane_definitions": [
            {"lane": "small_fast_router", "purpose": "triage, short QA, safe-tool selection"},
            {"lane": "medium_reasoner_default", "purpose": "primary synthesis and grounded retrieval"},
            {"lane": "heavy_reasoner_exception", "purpose": "long-context reconciliation under policy"},
        ],
        "cadence_policy": {
            "tick_ratio": f"{MERLIN_TICK_NUMERATOR}/{MERLIN_TICK_DENOMINATOR}",
            "tick_value": MERLIN_TICK_RATIO,
            "note": "12/37 cadence is an internal scheduling policy, not a claim of universal superiority.",
        },
        "gates": {
            "allow_external_on_high_risk": False,
            "fallback_requires_disclosure": True,
            "primary_requires_fully_open_science": True,
        },
    }


def choose_runtime(query: str, *, confidence: float = 0.7, risk_level: str | None = None) -> dict[str, Any]:
    lane = classify_lane(query)
    risk = risk_level or infer_risk_level(query)
    openrouter_enabled = _bool_env("MERLIN_ENABLE_OPENROUTER_COMPAT", default=False)
    has_openrouter_key = bool(os.environ.get("OPENROUTER_API_KEY"))
    provider = "sovereign_local"
    reason = "Sovereign local runtime is default to avoid token/account dependency."

    if risk != "high" and confidence < 0.4 and openrouter_enabled and has_openrouter_key:
        provider = "openrouter_compat"
        reason = "Compatibility fallback permitted by policy for low-confidence non-high-risk query."

    return {
        "lane": lane,
        "risk_level": risk,
        "confidence": round(float(confidence), 3),
        "provider": provider,
        "openrouter_compat_enabled": openrouter_enabled,
        "openrouter_key_present": has_openrouter_key,
        "reason": reason,
        "cadence_tick_ratio": f"{MERLIN_TICK_NUMERATOR}/{MERLIN_TICK_DENOMINATOR}",
        "cadence_tick_value": MERLIN_TICK_RATIO,
    }
