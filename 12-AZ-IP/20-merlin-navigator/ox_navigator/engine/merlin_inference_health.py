# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Dedicated inference-health surface for Merlin."""

from __future__ import annotations

from typing import Any

from .merlin_local_inference import get_inference_health as _get_inference_health
from .merlin_local_inference import get_inference_providers


def get_merlin_inference_health(provider_name: str | None = None) -> dict[str, Any]:
    payload = _get_inference_health(provider_name=provider_name)
    providers = get_inference_providers()
    payload.setdefault("provider_count", len(providers))
    payload.setdefault(
        "kernel_lane_policy",
        {
            "small_fast_router": "deterministic_retrieval",
            "medium_reasoner_default": "local_small_or_deterministic_retrieval",
            "heavy_reasoner_exception": "local_medium_or_local_small_or_deterministic_retrieval",
        },
    )
    payload.setdefault("deterministic_routing", "active")
    return payload
