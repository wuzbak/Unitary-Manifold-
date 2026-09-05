# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Provider registry for Merlin's sovereign local inference lane."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .merlin_local_provider import generate_local_response


def _bool_env(name: str, default: bool = False) -> bool:
    value = str(os.environ.get(name) or "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "on"}


def _clean_url(value: str) -> str:
    return str(value or "").strip().rstrip("/")


def _provider_record(
    *,
    name: str,
    provider_kind: str,
    available: bool,
    summary: str,
    lane_targets: list[str],
    model: str = "",
    endpoint: str = "",
    health: str = "ready",
    reason: str = "",
) -> dict[str, Any]:
    return {
        "name": name,
        "provider_kind": provider_kind,
        "available": bool(available),
        "health": health,
        "summary": summary,
        "lane_targets": lane_targets,
        "model": model,
        "endpoint": endpoint,
        "reason": reason,
        "cost_policy": "zero_external_token_cost" if provider_kind != "compatibility" else "token_compatibility_only",
    }


def get_inference_providers() -> list[dict[str, Any]]:
    providers = [
        _provider_record(
            name="deterministic_retrieval",
            provider_kind="local_builtin",
            available=True,
            health="ready",
            summary="Deterministic repository-grounded responder with no external dependency.",
            lane_targets=["small_fast_router", "medium_reasoner_default", "heavy_reasoner_exception"],
        ),
    ]
    for name, env_prefix, lanes in (
        ("local_small", "MERLIN_LOCAL_SMALL", ["medium_reasoner_default", "heavy_reasoner_exception"]),
        ("local_medium", "MERLIN_LOCAL_MEDIUM", ["heavy_reasoner_exception"]),
    ):
        endpoint = _clean_url(os.environ.get(f"{env_prefix}_BASE_URL", ""))
        model = str(os.environ.get(f"{env_prefix}_MODEL", "")).strip()
        enabled = _bool_env(f"{env_prefix}_ENABLED", default=bool(endpoint and model))
        available = bool(enabled and endpoint and model)
        providers.append(
            _provider_record(
                name=name,
                provider_kind="local_openai_compat",
                available=available,
                health="ready" if available else "not_configured",
                summary="Optional self-hosted OpenAI-compatible local endpoint for sovereign inference.",
                lane_targets=lanes,
                model=model,
                endpoint=endpoint,
                reason="" if available else f"Set {env_prefix}_BASE_URL and {env_prefix}_MODEL to enable this lane.",
            )
        )
    providers.append(
        _provider_record(
            name="openrouter_compat",
            provider_kind="compatibility",
            available=_bool_env("MERLIN_ENABLE_OPENROUTER_COMPAT", default=False) and bool(os.environ.get("OPENROUTER_API_KEY")),
            health="compatibility_only",
            summary="Compatibility-only external fallback; off by default.",
            lane_targets=["medium_reasoner_default"],
            model=str(os.environ.get("OPENROUTER_MODEL", "")).strip(),
            reason="Requires MERLIN_ENABLE_OPENROUTER_COMPAT and OPENROUTER_API_KEY.",
        )
    )
    return providers


def get_inference_provider(name: str) -> dict[str, Any] | None:
    for provider in get_inference_providers():
        if provider["name"] == name:
            return provider
    return None


def choose_inference_provider(lane: str) -> str:
    if lane == "heavy_reasoner_exception":
        if (get_inference_provider("local_medium") or {}).get("available"):
            return "local_medium"
        if (get_inference_provider("local_small") or {}).get("available"):
            return "local_small"
        return "deterministic_retrieval"
    if lane == "medium_reasoner_default" and (get_inference_provider("local_small") or {}).get("available"):
        return "local_small"
    return "deterministic_retrieval"


def get_inference_health(provider_name: str | None = None) -> dict[str, Any]:
    providers = get_inference_providers()
    if provider_name:
        provider = next((item for item in providers if item["name"] == provider_name), None)
        if provider is None:
            return {
                "ok": False,
                "error": f"Unknown inference provider: {provider_name}",
                "available_providers": [item["name"] for item in providers],
            }
        return {
            "ok": True,
            "default_provider": "deterministic_retrieval",
            "provider": provider,
        }
    available = [item["name"] for item in providers if item["available"]]
    return {
        "ok": True,
        "default_provider": "deterministic_retrieval",
        "available_providers": available,
        "providers": providers,
        "lane_preferences": {
            "small_fast_router": "deterministic_retrieval",
            "medium_reasoner_default": choose_inference_provider("medium_reasoner_default"),
            "heavy_reasoner_exception": choose_inference_provider("heavy_reasoner_exception"),
        },
        "compatibility_policy": "openrouter_frozen_compatibility_only",
    }


async def _call_local_chat(
    *,
    base_url: str,
    model: str,
    prompt: str,
    temperature: float,
) -> str:
    payload = {
        "model": model,
        "temperature": float(temperature),
        "messages": [{"role": "user", "content": prompt}],
    }
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        response = await client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
    choices = list(data.get("choices") or [])
    if not choices:
        return ""
    message = dict(choices[0].get("message") or {})
    content = message.get("content", "")
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


async def generate_inference_response(
    *,
    query: str,
    context: dict[str, Any],
    persona_mode: str,
    fourth_wall: bool,
    lane: str,
    preferred_provider: str | None = None,
    temperature: float = 0.2,
) -> dict[str, Any]:
    deterministic = generate_local_response(
        query=query,
        context=context,
        persona_mode=persona_mode,
        fourth_wall=fourth_wall,
    )
    target = preferred_provider or choose_inference_provider(lane)
    provider = get_inference_provider(target)
    if not isinstance(provider, dict):
        return {
            **deterministic,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
            "fallback_reason": "unknown_provider",
        }
    if provider["name"] == "deterministic_retrieval":
        return {
            **deterministic,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
        }
    if not provider.get("available"):
        return {
            **deterministic,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
            "fallback_reason": provider.get("reason", "provider_unavailable"),
        }
    try:
        body = await _call_local_chat(
            base_url=str(provider.get("endpoint") or ""),
            model=str(provider.get("model") or ""),
            prompt=str(query or ""),
            temperature=temperature,
        )
    except Exception as exc:
        return {
            **deterministic,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
            "fallback_reason": f"{provider['name']}_request_failed: {exc}",
        }
    if not str(body).strip():
        return {
            **deterministic,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
            "fallback_reason": f"{provider['name']}_empty_response",
        }
    return {
        "provider": "sovereign_local_model",
        "provider_variant": provider["name"],
        "requested_provider_variant": target,
        "body": str(body).strip(),
        "confidence": 0.58 if provider["name"] == "local_small" else 0.64,
    }
