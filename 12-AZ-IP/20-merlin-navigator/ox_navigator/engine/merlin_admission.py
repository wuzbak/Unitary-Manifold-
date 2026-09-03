# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Open-science model admission policy for Merlin."""

from __future__ import annotations

from typing import Any


OPENNESS_TIERS = (
    "fully_open_science",
    "partially_open",
    "proprietary",
)


def get_model_admission_policy() -> dict[str, Any]:
    return {
        "tiers": list(OPENNESS_TIERS),
        "doctrine": {
            "primary_lane_requirement": "fully_open_science",
            "fully_open_science_definition": (
                "Weights, code, training data access, training methodology, and reproducible recipe are all available."
            ),
            "epistemic_honesty": "Model openness tier must be disclosed in user-visible responses and governance artifacts.",
        },
        "required_fields": [
            "name",
            "openness_tier",
            "has_weights",
            "has_code",
            "has_training_data_access",
            "has_training_methodology",
            "license",
            "reproducible_recipe",
        ],
    }


def evaluate_model_admission(model: dict[str, Any]) -> dict[str, Any]:
    policy = get_model_admission_policy()
    errors: list[str] = []
    warnings: list[str] = []
    name = str(model.get("name") or "").strip()
    tier = str(model.get("openness_tier") or "").strip().lower()

    if not name:
        errors.append("name is required")
    if tier not in OPENNESS_TIERS:
        errors.append(f"openness_tier must be one of {', '.join(OPENNESS_TIERS)}")

    def _as_bool(key: str) -> bool:
        return bool(model.get(key))

    has_weights = _as_bool("has_weights")
    has_code = _as_bool("has_code")
    has_training_data_access = _as_bool("has_training_data_access")
    has_training_methodology = _as_bool("has_training_methodology")
    reproducible_recipe = _as_bool("reproducible_recipe")
    license_name = str(model.get("license") or "").strip()
    if not license_name:
        errors.append("license is required")

    if tier == "fully_open_science":
        if not all([has_weights, has_code, has_training_data_access, has_training_methodology, reproducible_recipe]):
            errors.append("fully_open_science tier requires weights, code, training data access, training methodology, and reproducible recipe")
    elif tier == "partially_open":
        if not has_weights and not has_code:
            warnings.append("partially_open model should provide at least weights or code")
    elif tier == "proprietary":
        warnings.append("proprietary models are fallback-only and cannot be primary")

    admission_ok = not errors
    allowed_as_primary = admission_ok and tier == "fully_open_science"
    fallback_only = admission_ok and not allowed_as_primary
    return {
        "ok": admission_ok,
        "model": {
            "name": name,
            "openness_tier": tier or "unknown",
        },
        "allowed_as_primary": allowed_as_primary,
        "fallback_only": fallback_only,
        "errors": errors,
        "warnings": warnings,
        "policy": policy,
    }
