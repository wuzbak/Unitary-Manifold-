# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Merlin query pipeline for the standalone Product 20 shell."""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any

import httpx

from .constants import API_BASE, DEFAULT_TEMPERATURE, MODEL_ID
from .gate_parser import extract_gate_badges
from .merlin_identity import authorize_privileged_request, get_identity_policy
from .merlin_local_inference import generate_inference_response
from .merlin_memory import MerlinSession
from .merlin_persona import (
    build_system_prompt,
    detect_persona_mode,
    extract_urls,
    is_internal_question,
    persona_governance_violations,
)
from .merlin_router import choose_runtime
from .merlin_rag import build_rag_context, closest_pillar, lookup_kb, retrieve_context
from .merlin_rag import build_status_response
from .merlin_runtime import run_post_turn_compilation
from .merlin_sentinel import evaluate_query, render_block_message
from .merlin_telemetry import build_run_telemetry
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


def _source_id(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(label or "").lower()).strip("_") or "source"


def _build_provenance(
    context: dict[str, Any],
    crawled: list[dict[str, Any]],
    *,
    matched_memory: list[dict[str, Any]] | None = None,
    policy_sources: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    kb_match = context.get("kb_match")
    if kb_match:
        for index, source in enumerate(kb_match.get("sources", [])[:3], start=1):
            sources.append({
                "source_id": f"kb_{index}_{_source_id(source)}",
                "label": source,
                "path": source,
                "kind": "knowledge_base",
                "claim_class": "knowledge_base_match",
                "confidence_tier": "retrieved",
                "gate": kb_match.get("status", "ARCHITECTURE_LIMIT"),
                "description": kb_match.get("topic", ""),
            })
    for pillar in context.get("pillars", [])[:3]:
        sources.append({
            "source_id": f"pillar_{pillar['id']}",
            "label": f"Pillar {pillar['id']}",
            "path": "",
            "kind": "pillar",
            "claim_class": "pillar_context",
            "confidence_tier": "retrieved",
            "gate": pillar["gate"],
            "description": pillar["name"],
        })
    for item in matched_memory or []:
        sources.append({
            "source_id": f"memory_{_source_id(item['fact'])}",
            "label": item["fact"],
            "path": item["source"],
            "kind": "memory",
            "claim_class": "durable_memory",
            "confidence_tier": "session",
            "gate": "GOVERNANCE",
            "description": f"{item['scope']} memory",
        })
    for item in crawled:
        if item.get("ok"):
            sources.append({
                "source_id": f"crawl_{_source_id(item['url'])}",
                "label": item["url"],
                "path": item["url"],
                "kind": "web",
                "claim_class": "external_context",
                "confidence_tier": "external",
                "gate": "ARCHITECTURE_LIMIT",
                "description": item.get("title", item["url"]),
            })
    for item in policy_sources or []:
        sources.append({
            "source_id": f"policy_{_source_id(item['label'])}",
            "label": item["label"],
            "path": item.get("label", ""),
            "kind": "policy",
            "claim_class": "policy_enforcement",
            "confidence_tier": "runtime",
            "gate": item.get("type", "GOVERNANCE"),
            "description": item.get("description", ""),
        })
    return {
        "schema_version": "v1",
        "complete": bool(sources),
        "sources": sources,
    }


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


def _retrieval_hit_count(context: dict[str, Any]) -> int:
    return (
        len(context.get("pillars") or [])
        + len(context.get("interrogator_hits") or [])
        + (1 if context.get("kb_match") else 0)
    )


def _post_process_answer(
    text: str,
    query: str,
    context: dict[str, Any],
    crawled: list[dict[str, Any]],
    persona_mode: str,
    fourth_wall: bool,
    *,
    matched_memory: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    cleaned = strip_tool_call(text)
    sections = cleaned.split("\n---\n", 1)
    body = sections[0].strip() if sections else cleaned.strip()
    followups = _default_followups(query, context)
    sources = _default_sources(context, crawled)
    provenance = _build_provenance(context, crawled, matched_memory=matched_memory)
    if not body:
        body = _fallback_body(query, context, persona_mode, fourth_wall)
    answer = _render_contract(body, followups, sources)
    violations = persona_governance_violations(answer)
    if violations:
        answer += "\n\n[GOVERNANCE] Persona guardrails adjusted output to preserve epistemic honesty and boundary discipline."
    gate_badges = extract_gate_badges(answer)
    if not gate_badges:
        gate_badges = [pillar["gate"] for pillar in context.get("pillars", [])[:3]]
    return {
        "answer": answer,
        "body": body,
        "followups": followups,
        "sources": sources,
        "provenance": provenance,
        "gate_badges": gate_badges,
        "persona_governance_violations": violations,
    }


def _policy_contract_response(body: str, *, sources: list[dict[str, str]]) -> dict[str, Any]:
    followups = [
        "Do you want a safe alternative framed as a legitimate governance or research task?",
        "Should Merlin show the exact policy section that triggered this refusal?",
        "Do you want to continue with normal user-access actions?",
    ]
    answer = _render_contract(body, followups, sources)
    gate_badges = extract_gate_badges(answer) or ["GOVERNANCE"]
    provenance = _build_provenance({}, [], policy_sources=sources)
    return {
        "answer": answer,
        "body": body,
        "followups": followups,
        "sources": sources,
        "provenance": provenance,
        "gate_badges": gate_badges,
    }


def _build_max_rigor_audit(
    *,
    privilege_requested: bool,
    privilege_allowed: bool,
    sentinel_blocked: bool,
    processed: dict[str, Any],
) -> dict[str, Any]:
    verification_ok = bool((processed.get("provenance") or {}).get("complete"))
    violations = list(processed.get("persona_governance_violations") or [])
    blocking_violations = [item for item in violations if not str(item).startswith("pillar_reference_missing_gate_marker")]
    governance_ok = not bool(blocking_violations)
    safety_ok = not sentinel_blocked
    identity_ok = (not privilege_requested) or privilege_allowed
    checks = {
        "identity_gate": identity_ok,
        "sentinel_scan": safety_ok,
        "source_verification": verification_ok,
        "governance_boundary_check": governance_ok,
    }
    return {
        "graph": "merlin_max_rigor_execution",
        "nodes": {
            "N2_identity_gate": {"ok": checks["identity_gate"]},
            "N3_sentinel_scan": {"ok": checks["sentinel_scan"]},
            "N5_source_verification": {"ok": checks["source_verification"]},
            "N6_governance_boundary_check": {"ok": checks["governance_boundary_check"]},
        },
        "all_green": all(checks.values()),
        "checks": checks,
        "violations": violations,
        "blocking_violations": blocking_violations,
        "hard_stops": [
            key
            for key, condition in {
                "identity_gate_fail_for_privileged": checks["identity_gate"],
                "sentinel_policy_block": checks["sentinel_scan"],
                "verification_conflict_unresolved": checks["source_verification"] and checks["governance_boundary_check"],
            }.items()
            if not condition
        ],
    }


def _enforce_max_rigor(
    *,
    processed: dict[str, Any],
    privilege_requested: bool,
    privilege_allowed: bool,
    sentinel_blocked: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    audit = _build_max_rigor_audit(
        privilege_requested=privilege_requested,
        privilege_allowed=privilege_allowed,
        sentinel_blocked=sentinel_blocked,
        processed=processed,
    )
    if audit["all_green"]:
        return processed, audit
    blocked = _policy_contract_response(
        "[ARCHITECTURE_LIMIT] Max-rigor execution halted because verification/safety/governance checks were not all green.",
        sources=[
            {"label": "Merlin Execution Graph", "type": "GOVERNANCE", "description": "verification + safety + governance must all pass"},
            {"label": "Max-Rigor Hard Stop", "type": "ARCHITECTURE_LIMIT", "description": ", ".join(audit["hard_stops"]) or "unknown"},
        ],
    )
    blocked["persona_governance_violations"] = list(processed.get("persona_governance_violations") or [])
    return blocked, audit


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
    runtime_mode: str = "merlin",
) -> dict[str, Any]:
    """Run a Merlin query and return a structured response."""
    started = time.perf_counter()
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
        audit = {
            "query": text,
            "timestamp": "",
            "matched_memory_count": 0,
            "matched_scopes": [],
            "matched_facts": [],
            "matched_memory": [],
        }
        telemetry = build_run_telemetry(
            query=text,
            answer=processed["answer"],
            router_decision={"provider": "sovereign_local", "lane": "small_fast_router"},
            context_source="policy_block",
            tool_rounds=0,
            used_websearch=False,
            provenance=processed["provenance"],
            gate_badges=processed["gate_badges"],
            memory_hits=audit["matched_memory_count"],
            contradiction_events=len(session.contradiction_events),
            latency_ms=(time.perf_counter() - started) * 1000,
            retrieval_hit_count=0,
            contract_pass_rate=1.0,
            boundary_violation_rate=0.0,
            contradiction_miss_rate=0.0,
            tool_call_precision=1.0,
        )
        session.record_run(telemetry)
        ingestion = await run_post_turn_compilation(
            query=text,
            answer=processed["answer"],
            provenance=processed["provenance"],
            session=session,
        )
        max_rigor = _build_max_rigor_audit(
            privilege_requested=False,
            privilege_allowed=True,
            sentinel_blocked=True,
            processed=processed,
        )
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
            "memory_audit": audit,
            "telemetry": telemetry,
            "compile_time_ingestion": ingestion,
            "max_rigor": max_rigor,
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
        audit = {
            "query": text,
            "timestamp": "",
            "matched_memory_count": 0,
            "matched_scopes": [],
            "matched_facts": [],
            "matched_memory": [],
        }
        telemetry = build_run_telemetry(
            query=text,
            answer=processed["answer"],
            router_decision={"provider": "sovereign_local", "lane": "small_fast_router"},
            context_source="privilege_block",
            tool_rounds=0,
            used_websearch=False,
            provenance=processed["provenance"],
            gate_badges=processed["gate_badges"],
            memory_hits=audit["matched_memory_count"],
            contradiction_events=len(session.contradiction_events),
            latency_ms=(time.perf_counter() - started) * 1000,
            contract_pass_rate=1.0,
            boundary_violation_rate=0.0,
            contradiction_miss_rate=0.0,
            tool_call_precision=1.0,
        )
        session.record_run(telemetry)
        ingestion = await run_post_turn_compilation(
            query=text,
            answer=processed["answer"],
            provenance=processed["provenance"],
            session=session,
        )
        max_rigor = _build_max_rigor_audit(
            privilege_requested=True,
            privilege_allowed=False,
            sentinel_blocked=False,
            processed=processed,
        )
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
            "memory_audit": audit,
            "telemetry": telemetry,
            "compile_time_ingestion": ingestion,
            "max_rigor": max_rigor,
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
    audit = session.audit_memory(text)
    compressed = session.compressed(text, matched_memory=audit.get("matched_memory"))
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
    context_source = "sovereign_local_model"
    tool_rounds = 0
    kb_score = float((context.get("kb_match") or {}).get("score") or 0.0)
    interrogator_scores = [
        float(item.get("confidence", 0.0))
        for item in (context.get("interrogator_hits") or [])
        if isinstance(item, dict)
    ]
    route_confidence = max([kb_score, *interrogator_scores], default=0.7)
    if runtime_mode == "incumbent_compat":
        response_text = _fallback_body(text, context, persona_mode, fourth_wall)
        router_decision = {
            "provider": "incumbent_compat",
            "lane": "medium_reasoner_default",
            "risk_level": "medium",
            "confidence": 0.5,
            "reason": "Incumbent compatibility baseline.",
            "openrouter_compat_enabled": False,
            "openrouter_key_present": False,
            "cadence_tick_ratio": "12/37",
            "cadence_tick_value": 12 / 37,
        }
        context_source = "incumbent_compat"
    else:
        router_decision = choose_runtime(
            text,
            confidence=route_confidence,
        )
        local_candidate = await generate_inference_response(
            query=text,
            context=context,
            persona_mode=persona_mode,
            fourth_wall=fourth_wall,
            lane=str(router_decision.get("lane") or "medium_reasoner_default"),
            preferred_provider=str(router_decision.get("inference_provider") or ""),
            temperature=temperature,
        )
        response_text = local_candidate["body"]
        router_decision["local_candidate_provider"] = str(local_candidate.get("provider_variant") or "deterministic_retrieval")
        if local_candidate.get("fallback_reason"):
            router_decision["local_candidate_fallback_reason"] = str(local_candidate.get("fallback_reason"))
        if (
            router_decision["provider"] == "openrouter_compat"
            and os.environ.get("OPENROUTER_API_KEY")
            and bool(router_decision.get("openrouter_compat_enabled"))
        ):
            if on_status is not None:
                on_status.append("model")
            try:
                response_text = await _call_openrouter(
                    messages,
                    model=model_override or MODEL_ID,
                    temperature=temperature,
                )
                context_source = "openrouter_compat" if not used_websearch else "openrouter_compat_web_aligned"
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
                context_source = "sovereign_local_model"

    initial_processed = _post_process_answer(
        response_text,
        text,
        context,
        crawled,
        persona_mode,
        fourth_wall,
        matched_memory=compressed.get("matched_memory"),
    )
    processed, max_rigor = _enforce_max_rigor(
        processed=initial_processed,
        privilege_requested=bool(privilege.get("requested")),
        privilege_allowed=bool(privilege.get("allowed")),
        sentinel_blocked=bool(sentinel.blocked),
    )
    preflight_ingestion = await run_post_turn_compilation(
        query=text,
        answer=processed["answer"],
        provenance=processed["provenance"],
        session=session,
        persist=False,
    )
    for artifact in preflight_ingestion.get("artifacts", []):
        session.ingest_compiled_insight(dict(artifact))
    ingestion = {
        **preflight_ingestion,
        "persisted_from_preflight": True,
        "source_answer": "original_candidate_answer",
        "served_response_rewritten": False,
    }
    if preflight_ingestion["should_block_output"]:
        processed = _policy_contract_response(
            "[OPEN_GAP] Response withheld by contradiction/proof gate. Candidate memory was quarantined and routed to Falsification Lab.",
            sources=[
                {"label": "Compile-Time Ingestion Gate", "type": "GOVERNANCE", "description": "Contradiction/proof enforcement"},
                {"label": "Falsification Lab Tripwire", "type": "ARCHITECTURE_LIMIT", "description": "Unverified or contradictory claims cannot auto-promote"},
            ],
        )
        served_preview = await run_post_turn_compilation(
            query=text,
            answer=processed["answer"],
            provenance=processed["provenance"],
            session=session,
            persist=False,
        )
        ingestion["served_response_rewritten"] = True
        ingestion["served_response_preview"] = {
            "compiled_count": served_preview["compiled_count"],
            "contradiction_count": served_preview["contradiction_count"],
            "unresolved_proof_count": served_preview["unresolved_proof_count"],
        }
    session.add_turn(text, processed["answer"], gates=processed["gate_badges"])
    telemetry = build_run_telemetry(
        query=text,
        answer=processed["answer"],
        router_decision=router_decision,
        context_source=context_source,
        tool_rounds=tool_rounds,
        used_websearch=used_websearch,
        provenance=processed["provenance"],
        gate_badges=processed["gate_badges"],
        memory_hits=audit["matched_memory_count"],
        contradiction_events=len(session.contradiction_events),
        latency_ms=(time.perf_counter() - started) * 1000,
        retrieval_hit_count=_retrieval_hit_count(context),
        boundary_violation_rate=1.0 if max_rigor.get("blocking_violations") else 0.0,
        contradiction_miss_rate=(
            1.0
            if int(preflight_ingestion.get("contradiction_count", 0) or 0) > 0
            and not bool(ingestion.get("served_response_rewritten"))
            else 0.0
        ),
        tool_call_precision=1.0,
    )
    session.record_run(telemetry)
    return {
        **processed,
        "persona_mode": persona_mode,
        "used_websearch": used_websearch,
        "tool_rounds": tool_rounds,
        "context_source": context_source,
        "crawled_urls": [item["url"] for item in crawled if item.get("ok")],
        "epistemic_note": "Merlin response grounded in canonical UM context. Not found paths remain explicit.",
        "live_status": live_status,
        "router_decision": router_decision,
        "sentinel": {
            "mode": sentinel.mode,
            "category": sentinel.category,
            "warning_number": session.policy_strikes,
            "session_cleared": False,
        },
        "identity_check": privilege["verification"],
        "memory_audit": audit,
        "telemetry": telemetry,
        "compile_time_ingestion": ingestion,
        "benchmark_eval": None,
        "max_rigor": max_rigor,
    }
