# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Bounded autonomous research cycle helpers for Merlin."""

from __future__ import annotations

import json
from typing import Any

from .merlin_counterexample import build_counterexample_digest
from .merlin_memory import MerlinSession
from .merlin_reasoning_graph import get_reasoning_chain
from .merlin_sentinel import evaluate_query, render_block_message
from .merlin_telemetry import estimate_energy_joules, estimate_token_count


def run_research_cycle(*, question: str, budget: int = 3, session: MerlinSession | None = None) -> dict[str, Any]:
    active_session = session if session is not None else MerlinSession()
    spend = max(1, min(int(budget or 3), 5))
    sentinel = evaluate_query(question, policy_strikes=active_session.policy_strikes)
    if sentinel.blocked:
        return {
            "ok": False,
            "question": question,
            "budget": spend,
            "sentinel": {
                "blocked": True,
                "mode": sentinel.mode,
                "category": sentinel.category,
            },
            "report": render_block_message(sentinel),
        }

    from .merlin_tools import route_tool

    steps: list[dict[str, Any]] = []
    plan = [
        "Identify the strongest repository-grounded anchor.",
        "Trace a multi-hop reasoning chain across nearby pillars.",
        "Audit memory and contradiction pressure before reporting.",
    ]
    knowledge: dict[str, Any] = {"result": {"data": {"match": None}}}
    reasoning: dict[str, Any] = {"ok": True, "chain": [], "proof_chain_confidence": 0.0}
    interrogator: dict[str, Any] = {"result": {"data": {"results": []}}}
    memory_audit: dict[str, Any] = {"matched_facts": []}
    contradictions: dict[str, Any] = {
        "ok": True,
        "total_events": 0,
        "quarantined_insight_count": 0,
        "kind_counts": {},
        "items": [],
        "stage_b_refresh_ready": False,
        "note": "not_run_due_to_budget",
    }

    if spend >= 1:
        knowledge = route_tool("searchKnowledgeBase", {"query": question}, session=active_session)
        steps.append({"step": 1, "tool": "searchKnowledgeBase", "ok": knowledge.get("ok", False)})
    if spend >= 2:
        reasoning = get_reasoning_chain(question, max_hops=min(4, spend + 1))
        steps.append({"step": 2, "tool": "getMerlinReasoningChain", "ok": reasoning.get("ok", False)})
    if spend >= 3:
        interrogator = route_tool("searchInterrogator", {"query": question}, session=active_session)
        steps.append({"step": 3, "tool": "searchInterrogator", "ok": interrogator.get("ok", False)})
    if spend >= 4:
        memory_audit = active_session.audit_memory(question)
        steps.append({"step": 4, "tool": "runMerlinMemoryAudit", "ok": True})
    if spend >= 5:
        contradictions = build_counterexample_digest(session=active_session, limit=spend)
        steps.append({"step": 5, "tool": "getMerlinCounterexampleDigest", "ok": contradictions.get("ok", False)})

    kb_match = ((knowledge.get("result") or {}).get("data") or {}).get("match")
    interrogator_hits = (((interrogator.get("result") or {}).get("data") or {}).get("results") or [])[:spend]
    chain = list(reasoning.get("chain") or [])
    open_gaps: list[str] = []
    if not kb_match:
        open_gaps.append("No strong canonical KB match; answer must stay pillar-grounded and cautious.")
    if spend >= 2 and not any(int(item.get("lean4_hit_count", 0)) > 0 for item in chain):
        open_gaps.append("No Lean4 hit surfaced in the retrieved chain; proof confidence remains limited.")
    if spend < 4:
        open_gaps.append("Memory audit was not executed because the cycle budget ended before that step.")
    if spend < 5:
        open_gaps.append("Counterexample digest was not executed because the cycle budget ended before that step.")
    if contradictions.get("total_events", 0):
        open_gaps.append("Recent contradiction events exist and should be reviewed before any promotion claim.")

    receipts = [{"tool": step["tool"], "ok": step["ok"]} for step in steps]
    serialized_findings = json.dumps(
        {
            "kb_match": kb_match,
            "chain": chain,
            "interrogator_hits": interrogator_hits,
            "memory_facts": memory_audit.get("matched_facts", []),
        },
        ensure_ascii=False,
    )
    energy_cost = {
        "estimated_joules": estimate_energy_joules(
            provider="sovereign_local",
            lane="medium_reasoner_default",
            input_tokens=estimate_token_count(question),
            output_tokens=estimate_token_count(serialized_findings),
            tool_rounds=len(receipts),
        ),
        "measurement_mode": "deterministic_estimate",
    }
    return {
        "ok": True,
        "question": question,
        "budget": spend,
        "sentinel": {
            "blocked": False,
            "mode": sentinel.mode,
            "category": sentinel.category,
        },
        "plan": plan,
        "steps": steps,
        "findings": {
            "kb_match": kb_match,
            "reasoning_chain": chain,
            "interrogator_hits": interrogator_hits,
            "memory_facts": memory_audit.get("matched_facts", []),
        },
        "contradictions": contradictions,
        "self_critique": {
            "open_gaps": open_gaps,
            "confidence": reasoning.get("proof_chain_confidence", 0.0),
            "next_question": "Inspect the top cited pillar or an unresolved contradiction before any stronger claim.",
        },
        "receipts": receipts,
        "energy_cost": energy_cost,
    }
