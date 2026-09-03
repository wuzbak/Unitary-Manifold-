# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Merlin query pipeline for the standalone Product 20 shell."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

from .constants import API_BASE, DEFAULT_TEMPERATURE, MODEL_ID
from .gate_parser import extract_gate_badges
from .merlin_identity import authorize_privileged_request, get_identity_policy
from .merlin_memory import MerlinSession
from .merlin_persona import (
    build_system_prompt,
    detect_persona_mode,
    extract_urls,
    is_internal_question,
)
from .merlin_rag import build_rag_context, closest_pillar, lookup_kb, retrieve_context
from .merlin_rag import build_status_response
from .merlin_sentinel import evaluate_query, render_block_message
from .merlin_tools import route_tool

TOOL_CALL_RE = re.compile(r"\[TOOL_CALL\]\s*(\{[\s\S]*?\})\s*\[/TOOL_CALL\]")


def extract_tool_call(text: str) -> dict[str, Any] | None:
    """Extract a Merlin tool call block from model output."""
    match = TOOL_CALL_RE.search(text or "")
    if not match:
        return None
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    if "tool" not in payload:
        return None
    return payload


def strip_tool_call(text: str) -> str:
    """Remove tool call blocks from user-visible text."""
    return TOOL_CALL_RE.sub("", text or "").strip()


def _crawl_page(url: str) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
        text = re.sub(r"\s+", " ", response.text)
        return {"url": url, "ok": True, "title": url, "content": text[:2500]}
    except Exception as exc:
        return {"url": url, "ok": False, "error": str(exc)}


async def _call_openrouter(messages: list[dict[str, str]], *, model: str, temperature: float) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8020",
        "X-Title": "Merlin Product 20",
    }
    payload = {
        "model": model,
        "temperature": float(temperature),
        "messages": messages,
    }
    async with httpx.AsyncClient(base_url=API_BASE, timeout=60.0) as client:
        response = await client.post("/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    choices = data.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


def _default_followups(query: str, context: dict[str, Any]) -> list[str]:
    kb_match = context.get("kb_match")
    pillar = context["pillars"][0] if context.get("pillars") else closest_pillar(query)
    topic = kb_match.get("topic") if kb_match else (pillar.get("name") if pillar else "this topic")
    return [
        f"Which primary pillar should we inspect next for {topic}?",
        "Do you want the nearest falsification condition or open architecture limit?",
        "Should Merlin trace this through tests, Lean4, or the Interrogator knowledge base?",
    ]


def _default_sources(context: dict[str, Any], crawled: list[dict[str, Any]]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    kb_match = context.get("kb_match")
    if kb_match:
        for source in kb_match.get("sources", [])[:3]:
            sources.append({"label": source, "type": "FILE", "description": kb_match.get("topic", "")})
    for pillar in context.get("pillars", [])[:3]:
        sources.append({
            "label": f"Pillar {pillar['id']}",
            "type": pillar["gate"],
            "description": pillar["name"],
        })
    for item in crawled:
        if item.get("ok"):
            sources.append({"label": f"[CRAWLED] {item['url']}", "type": "CRAWLED", "description": item.get("title", item["url"])})
    return sources


def _render_contract(body: str, followups: list[str], sources: list[dict[str, str]]) -> str:
    body = body.strip()
    lines = [body, "", "---", "FOLLOWUPS:"]
    for idx, followup in enumerate(followups[:3], start=1):
        lines.append(f"{idx}. {followup}")
    lines.append("Sources:")
    for source in sources:
        lines.append(f"- {source['label']} | {source['type']} | {source['description']}")
    return "\n".join(lines).strip()


def _fallback_body(query: str, context: dict[str, Any], persona_mode: str, fourth_wall: bool) -> str:
    kb_match = context.get("kb_match")
    if kb_match:
        prefix = "Direct answer:" if persona_mode == "serious" else "Merlin pads in with the shortest honest answer:"
        body = f"{prefix} {kb_match['answer']} [{kb_match['status']}]"
    elif context.get("pillars"):
        pillar = context["pillars"][0]
        prefix = "Not found in framework context." if persona_mode == "serious" else "Merlin cannot honestly conjure that from the framework context."
        body = f"{prefix} Closest relevant pillar: [${pillar['gate']}] Pillar {pillar['id']} — {pillar['name']}. {pillar['text']}"
        body = body.replace("[$", "[")
    else:
        body = "Not found in framework context. Merlin does not have a grounded answer for that yet."
    if fourth_wall:
        body += "\n\n[Fourth wall] A gate badge is the repository's honesty label for how firm a claim is."
    return body


def _post_process_answer(text: str, query: str, context: dict[str, Any], crawled: list[dict[str, Any]], persona_mode: str, fourth_wall: bool) -> dict[str, Any]:
    cleaned = strip_tool_call(text)
    sections = cleaned.split("\n---\n", 1)
    body = sections[0].strip() if sections else cleaned.strip()
    followups = _default_followups(query, context)
    sources = _default_sources(context, crawled)
    if not body:
        body = _fallback_body(query, context, persona_mode, fourth_wall)
    answer = _render_contract(body, followups, sources)
    gate_badges = extract_gate_badges(answer)
    if not gate_badges:
        gate_badges = [pillar["gate"] for pillar in context.get("pillars", [])[:3]]
    return {
        "answer": answer,
        "body": body,
        "followups": followups,
        "sources": sources,
        "gate_badges": gate_badges,
    }


def _policy_contract_response(body: str, *, sources: list[dict[str, str]]) -> dict[str, Any]:
    followups = [
        "Do you want a safe alternative framed as a legitimate governance or research task?",
        "Should Merlin show the exact policy section that triggered this refusal?",
        "Do you want to continue with normal user-access actions?",
    ]
    answer = _render_contract(body, followups, sources)
    gate_badges = extract_gate_badges(answer) or ["GOVERNANCE"]
    return {
        "answer": answer,
        "body": body,
        "followups": followups,
        "sources": sources,
        "gate_badges": gate_badges,
    }


async def query_merlin(
    *,
    text: str,
    session: MerlinSession,
    on_status: list[str] | None = None,
    model_override: str | None = None,
    fourth_wall: bool = False,
    page_context: str = "",
    user_context: str = "",
    live_status: dict[str, Any] | None = None,
    system_override: str = "",
    force_websearch: bool | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
) -> dict[str, Any]:
    """Run a Merlin query and return a structured response."""
    live_status = live_status or build_status_response()
    sentinel = evaluate_query(text, policy_strikes=session.policy_strikes)
    session.set_sentinel_mode(sentinel.mode)
    if sentinel.blocked:
        strikes = session.register_policy_strike()
        body = render_block_message(sentinel)
        if sentinel.session_cleared:
            session.clear(reason=f"sentinel_{sentinel.category}")
        processed = _policy_contract_response(
            body,
            sources=[
                {"label": "Merlin Sentinel Policy", "type": "GOVERNANCE", "description": "Hard do-no-harm refusal policy"},
                {"label": f"Warning #{strikes}", "type": "GOVERNANCE", "description": "Warn then reset escalation"},
            ],
        )
        session.add_turn(text, processed["answer"], gates=processed["gate_badges"])
        return {
            **processed,
            "persona_mode": "serious",
            "used_websearch": False,
            "tool_rounds": 0,
            "context_source": "policy_block",
            "crawled_urls": [],
            "epistemic_note": "Request blocked by Sentinel do-no-harm policy.",
            "live_status": live_status,
            "sentinel": {
                "mode": sentinel.mode,
                "category": sentinel.category,
                "warning_number": sentinel.warning_number,
                "session_cleared": sentinel.session_cleared,
            },
            "identity_policy": get_identity_policy(),
        }

    privilege = authorize_privileged_request(
        text,
        page_context=page_context,
        user_context=user_context,
    )
    if privilege["requested"] and not privilege["allowed"]:
        session.register_privileged_attempt()
        processed = _policy_contract_response(
            "[GOVERNANCE] Privileged Merlin-modification request refused. Identity verification is uncertain, "
            "so Merlin defaults to normal user access and refuses privileged changes.",
            sources=[
                {"label": "Merlin Identity Policy", "type": "GOVERNANCE", "description": "Canonical identity and alias trust policy"},
                {"label": "Privilege Rule", "type": "ARCHITECTURE_LIMIT", "description": "Only verified identity may alter Merlin"},
            ],
        )
        session.add_turn(text, processed["answer"], gates=processed["gate_badges"])
        return {
            **processed,
            "persona_mode": "serious",
            "used_websearch": False,
            "tool_rounds": 0,
            "context_source": "privilege_block",
            "crawled_urls": [],
            "epistemic_note": "Privileged request refused under identity trust policy.",
            "live_status": live_status,
            "sentinel": {"mode": sentinel.mode, "category": "none", "warning_number": session.policy_strikes, "session_cleared": False},
            "identity_check": privilege["verification"],
        }

    persona_mode = detect_persona_mode(text)
    system_prompt = system_override or build_system_prompt(
        persona_mode=persona_mode,
        fourth_wall=fourth_wall,
        page_context=page_context,
        user_context=user_context,
        live_status=live_status,
    )
    context = retrieve_context(text)
    rag_context = build_rag_context(text)
    urls = extract_urls(text)
    crawled = [_crawl_page(url) for url in urls]
    if on_status is not None:
        on_status.append("crawling" if crawled else "rag")
    internal = is_internal_question(text)
    used_websearch = bool(force_websearch) if force_websearch is not None else (not internal or bool(urls))
    compressed = session.compressed()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"[EARLIER CONVERSATION SUMMARY]\n{compressed['summary']}"},
        {"role": "system", "content": rag_context},
    ]
    for item in crawled:
        if item.get("ok"):
            messages.append({"role": "system", "content": f"[CRAWLED PAGE CONTENT]\nURL: {item['url']}\n{item['content']}"})
    for turn in compressed["recent"]:
        messages.append({"role": "user", "content": turn.get("query", "")})
        messages.append({"role": "assistant", "content": turn.get("response", "")})
    messages.append({"role": "user", "content": text})

    response_text = ""
    context_source = "offline_rag"
    tool_rounds = 0
    if os.environ.get("OPENROUTER_API_KEY"):
        if on_status is not None:
            on_status.append("model")
        try:
            response_text = await _call_openrouter(
                messages,
                model=model_override or MODEL_ID,
                temperature=temperature,
            )
            context_source = "openrouter" if not used_websearch else "openrouter_web_aligned"
            for _ in range(2):
                tool_call = extract_tool_call(response_text)
                if not tool_call:
                    break
                tool_rounds += 1
                tool_result = route_tool(str(tool_call["tool"]), dict(tool_call.get("args") or {}))
                messages.append({"role": "assistant", "content": strip_tool_call(response_text) or "(tool request emitted)"})
                messages.append({"role": "system", "content": f"[TOOL RESULT]\n{json.dumps(tool_result, ensure_ascii=False)}\n[/TOOL RESULT]"})
                response_text = await _call_openrouter(
                    messages,
                    model=model_override or MODEL_ID,
                    temperature=temperature,
                )
        except Exception:
            response_text = ""
            context_source = "offline_rag_fallback"
    if not response_text:
        response_text = _fallback_body(text, context, persona_mode, fourth_wall)

    processed = _post_process_answer(response_text, text, context, crawled, persona_mode, fourth_wall)
    session.add_turn(text, processed["answer"], gates=processed["gate_badges"])
    return {
        **processed,
        "persona_mode": persona_mode,
        "used_websearch": used_websearch,
        "tool_rounds": tool_rounds,
        "context_source": context_source,
        "crawled_urls": [item["url"] for item in crawled if item.get("ok")],
        "epistemic_note": "Merlin response grounded in canonical UM context. Not found paths remain explicit.",
        "live_status": live_status,
        "sentinel": {
            "mode": sentinel.mode,
            "category": sentinel.category,
            "warning_number": session.policy_strikes,
            "session_cleared": False,
        },
        "identity_check": privilege["verification"],
    }
