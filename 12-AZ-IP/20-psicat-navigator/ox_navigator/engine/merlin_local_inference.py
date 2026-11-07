# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Provider registry for Merlin's sovereign local inference lane."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .merlin_local_provider import generate_local_response

MAX_LOCAL_CONTEXT_MESSAGES = 64
MAX_LOCAL_CONTEXT_CHARACTERS = 48_000
DEFAULT_LOCAL_TIMEOUT_SECONDS = 30
MAX_LOCAL_TIMEOUT_SECONDS = 1800


def local_context_parity_enabled() -> bool:
    return _bool_env("MERLIN_LOCAL_CONTEXT_PARITY")


def _bool_env(name: str, default: bool = False) -> bool:
    value = str(os.environ.get(name) or "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "on"}


def _clean_url(value: str) -> str:
    return str(value or "").strip().rstrip("/")


def _clean_chat_path(value: str) -> str:
    sample = str(value or "").strip()
    if not sample:
        return "v1/chat/completions"
    return sample.lstrip("/")


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
    chat_path: str = "v1/chat/completions",
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
        "chat_path": chat_path,
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
        chat_path = _clean_chat_path(os.environ.get(f"{env_prefix}_CHAT_PATH", "v1/chat/completions"))
        model = str(os.environ.get(f"{env_prefix}_MODEL", "")).strip()
        enabled = _bool_env(f"{env_prefix}_ENABLED", default=bool(endpoint and model))
        timeout_env = f"{env_prefix}_TIMEOUT_SECONDS"
        timeout_text = os.environ.get(timeout_env, "").strip()
        timeout_digits = timeout_text.lstrip("0")
        timeout_valid = not timeout_text or (
            timeout_text.isascii() and timeout_text.isdecimal()
            and 1 <= len(timeout_digits) <= 4 and int(timeout_digits) <= MAX_LOCAL_TIMEOUT_SECONDS
        )
        timeout = int(timeout_digits) if timeout_text and timeout_valid else DEFAULT_LOCAL_TIMEOUT_SECONDS
        available = bool(enabled and endpoint and model and timeout_valid)
        if not timeout_valid:
            reason = f"{timeout_env} must be an integer from 1 to {MAX_LOCAL_TIMEOUT_SECONDS}."
        elif not available:
            reason = f"Set {env_prefix}_BASE_URL and {env_prefix}_MODEL to enable this lane."
        else:
            reason = ""
        provider = _provider_record(
            name=name,
            provider_kind="local_openai_compat",
            available=available,
            health="ready" if available else ("invalid_config" if not timeout_valid else "not_configured"),
            summary="Optional self-hosted OpenAI-compatible local endpoint for sovereign inference.",
            lane_targets=lanes,
            model=model,
            endpoint=endpoint,
            chat_path=chat_path,
            reason=reason,
        )
        provider["timeout_seconds"] = timeout if timeout_valid else None
        providers.append(provider)
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
    chat_path: str,
    model: str,
    prompt: str,
    temperature: float,
    messages: list[dict[str, str]] | None = None,
    timeout_seconds: int = DEFAULT_LOCAL_TIMEOUT_SECONDS,
) -> str:
    payload = {
        "model": model,
        "temperature": float(temperature),
        "messages": messages if messages is not None else [{"role": "user", "content": prompt}],
    }
    endpoint_url = f"{base_url.rstrip('/')}/{chat_path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=float(timeout_seconds)) as client:
        response = await client.post(endpoint_url, json=payload)
        response.raise_for_status()
        data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Local inference response must be a JSON object.")
    choices = data.get("choices", [])
    if not isinstance(choices, list):
        raise ValueError("Local inference choices must be a JSON array.")
    if not choices:
        return ""
    if not isinstance(choices[0], dict) or not isinstance(choices[0].get("message"), dict):
        raise ValueError("Local inference choice must contain a message object.")
    message = choices[0]["message"]
    content = message.get("content", "")
    if isinstance(content, list):
        if any(not isinstance(part, dict) or not isinstance(part.get("text"), str) for part in content):
            raise ValueError("Local inference content parts must contain text strings.")
        return "".join(part["text"] for part in content)
    if not isinstance(content, str):
        raise ValueError("Local inference content must be a string or text-part array.")
    return content


def _build_grounded_prompt(
    *,
    query: str,
    context: dict[str, Any],
    persona_mode: str,
    fourth_wall: bool,
    deterministic_body: str,
    lane: str,
) -> str:
    context_blocks: list[str] = []
    kb_match = dict(context.get("kb_match") or {})
    if kb_match:
        context_blocks.append(
            "[KNOWLEDGE BASE MATCH]\n"
            f"Topic: {kb_match.get('topic', '')}\n"
            f"Status: {kb_match.get('status', '')}\n"
            f"Answer: {kb_match.get('answer', '')}\n"
            f"Sources: {', '.join(kb_match.get('sources', []))}"
        )
    pillar_lines = []
    for pillar in list(context.get("pillars") or [])[:5]:
        pillar_lines.append(
            f"Pillar {pillar.get('id', '')} | {pillar.get('gate', '')} | {pillar.get('name', '')} | {pillar.get('text', '')}"
        )
    if pillar_lines:
        context_blocks.append("[RETRIEVED PILLAR CONTEXT]\n" + "\n".join(pillar_lines))
    interrogator_lines = []
    for hit in list(context.get("interrogator_hits") or [])[:3]:
        interrogator_lines.append(
            f"{hit.get('id', 'unknown')} | {hit.get('gate', hit.get('status', 'UNKNOWN'))} | {hit.get('claim', hit.get('prediction', ''))}"
        )
    if interrogator_lines:
        context_blocks.append("[INTERROGATOR MATCHES]\n" + "\n".join(interrogator_lines))
    grounded_context = "\n\n".join(context_blocks) if context_blocks else "No retrieved context was available for this turn."
    persona_line = f"Persona mode: {persona_mode}."
    fourth_wall_line = "Fourth-wall explanations requested." if fourth_wall else "No fourth-wall framing requested."
    lane_guidance = (
        "Heavy-lane policy: reconcile conflicting evidence, preserve typed provenance, keep escalation bounded, and state rollback or demotion triggers explicitly."
        if lane == "heavy_reasoner_exception"
        else "Lane policy: stay concise, grounded, and contract-complete."
    )
    return "\n\n".join(
        [
            "You are Merlin running in sovereign local mode. Stay grounded in repository evidence and preserve explicit gate labels and uncertainty.",
            persona_line,
            fourth_wall_line,
            lane_guidance,
            f"User query:\n{query}",
            f"Repository context:\n{grounded_context}",
            f"Deterministic fallback baseline:\n{deterministic_body}",
        ]
    ).strip()


async def generate_inference_response(
    *,
    query: str,
    context: dict[str, Any],
    persona_mode: str,
    fourth_wall: bool,
    lane: str,
    preferred_provider: str | None = None,
    temperature: float = 0.2,
    messages: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    deterministic = generate_local_response(
        query=query,
        context=context,
        persona_mode=persona_mode,
        fourth_wall=fourth_wall,
    )
    target = preferred_provider or choose_inference_provider(lane)
    context_transport = {
        "requested_context_mode": "assembled_messages" if messages is not None else "grounded_prompt",
        "context_mode": "deterministic_retrieval",
        "submitted_message_count": len(messages) if isinstance(messages, list) else 0,
        "sent_message_count": 0,
    }
    provider = get_inference_provider(target)
    if not isinstance(provider, dict):
        return {
            **deterministic,
            **context_transport,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
            "fallback_reason": "unknown_provider",
        }
    if provider["name"] == "deterministic_retrieval":
        return {
            **deterministic,
            **context_transport,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
        }
    if not provider.get("available"):
        return {
            **deterministic,
            **context_transport,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
            "fallback_reason": provider.get("reason", "provider_unavailable"),
        }
    if messages is not None:
        invalid_context = (
            not isinstance(messages, list)
            or not messages
            or any(
                not isinstance(message, dict)
                or set(message) != {"role", "content"}
                or not isinstance(message["role"], str)
                or message["role"] not in {"system", "user", "assistant"}
                or not isinstance(message["content"], str)
                for message in messages
            )
        )
        over_budget = not invalid_context and (
            len(messages) > MAX_LOCAL_CONTEXT_MESSAGES
            or sum(len(message["content"]) for message in messages) > MAX_LOCAL_CONTEXT_CHARACTERS
        )
        if invalid_context or over_budget:
            return {
                **deterministic,
                **context_transport,
                "provider_variant": "deterministic_retrieval",
                "requested_provider_variant": target,
                "fallback_reason": "invalid_context_messages" if invalid_context else "context_budget_exceeded",
            }
    context_transport["sent_message_count"] = len(messages) if messages is not None else 1
    try:
        body = await _call_local_chat(
            base_url=str(provider.get("endpoint") or ""),
            chat_path=str(provider.get("chat_path") or "v1/chat/completions"),
            model=str(provider.get("model") or ""),
            prompt=_build_grounded_prompt(
                query=query,
                context=context,
                persona_mode=persona_mode,
                fourth_wall=fourth_wall,
                deterministic_body=str(deterministic.get("body") or ""),
                lane=lane,
            ),
            temperature=temperature,
            messages=messages,
            timeout_seconds=provider["timeout_seconds"],
        )
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        return {
            **deterministic,
            **context_transport,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
            "fallback_reason": f"{provider['name']}_request_failed: {exc}",
        }
    if not str(body).strip():
        return {
            **deterministic,
            **context_transport,
            "provider_variant": "deterministic_retrieval",
            "requested_provider_variant": target,
            "fallback_reason": f"{provider['name']}_empty_response",
        }
    return {
        **context_transport,
        "context_mode": context_transport["requested_context_mode"],
        "provider": "sovereign_local_model",
        "provider_variant": provider["name"],
        "requested_provider_variant": target,
        "body": str(body).strip(),
        "confidence": 0.58 if provider["name"] == "local_small" else 0.64,
    }
