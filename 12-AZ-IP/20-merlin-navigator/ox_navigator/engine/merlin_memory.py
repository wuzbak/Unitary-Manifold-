# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Session and durable memory helpers for Merlin."""

from __future__ import annotations

import re
import hashlib
import hmac
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from .gate_parser import extract_gate_badges
from .merlin_persona import compress_context
from .merlin_telemetry import summarize_runs

MERLIN_ACTIVE_SESSION_KEY = "merlin_active_session"
MERLIN_CACHE_KEY = "merlin_sessions_cache"
MERLIN_MAX_HISTORY = 50
MERLIN_MAX_INTENTS = 100
MERLIN_MAX_TELEMETRY = 100
MERLIN_MAX_AUDITS = 100
MERLIN_MAX_BREADCRUMBS = 120

_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
_NUMERIC_ASSIGNMENT_RE = re.compile(r"(k[\s_\-]*cs|n[\s_\-]*w|w[\s_\-]*a)\s*=\s*([\-]?\d+(?:\.\d+)?)", re.IGNORECASE)
_W_A_NONZERO_RE = re.compile(r"w[\s_\-]*a\s*(?:!=|[><~]=?)\s*0", re.IGNORECASE)

HARDGATE_INVARIANTS = {
    "kcs": "74",
    "nw": "5",
    "wa": "0",
}

EPISTEMIC_NAMESPACES = (
    "physics_hardgate",
    "governance",
    "adjacent_track",
    "narrative_speculative",
    "general",
)


def infer_epistemic_namespace(text: str) -> str:
    sample = _normalize(text)
    compact = sample.replace(" ", "")
    if any(token in sample for token in ("hardgate", "pillar", "litebird", "desi", "juno", "w a", "k cs", "n w", "theorem", "lean4")) or any(token in compact for token in ("wa", "kcs", "nw")):
        return "physics_hardgate"
    if any(token in sample for token in ("governance", "policy", "privilege", "sentinel", "boundary", "hils", "pentad")):
        return "governance"
    if any(token in sample for token in ("adjacent", "xdiag", "fermi hubbard", "side project", "prototype")):
        return "adjacent_track"
    if any(token in sample for token in ("story", "narrative", "screenplay", "fiction", "filmer", "oracle script", "speculative")):
        return "narrative_speculative"
    return "general"


def _parse_timestamp(value: Any) -> datetime | None:
    stamp = str(value or "").strip()
    if not stamp:
        return None
    try:
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def _epistemic_uncertainty_profile(sample: str, *, contradictions: list[str] | None = None) -> dict[str, Any]:
    text = _normalize(sample)
    contradiction_list = list(contradictions or [])
    score = 0.2
    reasons: list[str] = []
    if contradiction_list:
        score += 0.35
        reasons.append("explicit_contradictions_present")
    if any(token in text for token in ("open gap", "architecture limit", "tension")):
        score += 0.2
        reasons.append("boundary_touching_claim")
    if any(token in text for token in ("cmb", "acoustic", "suppression")):
        score += 0.15
        reasons.append("cmb_amplitude_limit_context")
    if any(token in text for token in ("delta m", "m2", "neutrino", "residual")):
        score += 0.1
        reasons.append("neutrino_residual_context")
    if any(token in text for token in ("proof", "theorem", "conjecture", "derive")):
        score += 0.1
        reasons.append("formal_proof_pending_surface")
    score = round(min(0.98, max(0.0, score)), 4)
    confidence = round(1.0 - score, 4)
    if score >= 0.75:
        band = "critical"
    elif score >= 0.55:
        band = "high"
    elif score >= 0.35:
        band = "medium"
    else:
        band = "low"
    return {
        "uncertainty_score": score,
        "confidence_bound": confidence,
        "risk_band": band,
        "reasons": reasons or ["baseline_uncertainty"],
    }

DEFAULT_DURABLE_MEMORIES = [
    {
        "scope": "repository",
        "fact": "Merlin is local/offline-first and OpenRouter is compatibility-only fallback.",
        "source": "product_policy",
        "tags": ["runtime", "router", "fallback", "openrouter"],
    },
    {
        "scope": "repository",
        "fact": "Merlin must keep epistemic labels, boundary statements, and uncertainty visible.",
        "source": "program_doctrine",
        "tags": ["governance", "epistemic", "labels", "uncertainty"],
    },
    {
        "scope": "repository",
        "fact": "Privileged Merlin modifications require identity verification and otherwise must be refused.",
        "source": "identity_policy",
        "tags": ["identity", "privilege", "safety"],
    },
]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _redacted_digest(text: str) -> str:
    secret = str(os.environ.get("MERLIN_MEMORY_HASH_SECRET") or "merlin-memory-redaction").encode("utf-8")
    return hmac.new(secret, str(text or "").encode("utf-8"), hashlib.sha256).hexdigest()


def _normalize(text: str) -> str:
    return _NORMALIZE_RE.sub(" ", str(text or "").lower()).strip()


def infer_intent(query: str) -> str:
    sample = (query or "").lower()
    if any(item in sample for item in {"plan", "roadmap", "strategy"}):
        return "planning"
    if any(item in sample for item in {"test", "verify", "check"}):
        return "verification"
    if any(item in sample for item in {"governance", "policy", "boundary"}):
        return "governance"
    if any(item in sample for item in {"pillar", "hardgate", "open_gap", "adjacent"}):
        return "physics_navigation"
    return "general_qa"


@dataclass(slots=True)
class MerlinSession:
    """Track recent Merlin conversation turns, durable memory, and telemetry."""

    turns: list[dict[str, Any]] = field(default_factory=list)
    intents: list[dict[str, Any]] = field(default_factory=list)
    policy_strikes: int = 0
    reset_events: list[dict[str, Any]] = field(default_factory=list)
    sentinel_mode: str = "MONITOR"
    privileged_attempts: int = 0
    durable_memory: list[dict[str, Any]] = field(default_factory=list)
    contradiction_events: list[dict[str, Any]] = field(default_factory=list)
    memory_audits: list[dict[str, Any]] = field(default_factory=list)
    telemetry: list[dict[str, Any]] = field(default_factory=list)
    compiled_insights: list[dict[str, Any]] = field(default_factory=list)
    quarantined_insights: list[dict[str, Any]] = field(default_factory=list)
    route_breadcrumbs: list[dict[str, Any]] = field(default_factory=list)
    observatory_events: list[dict[str, Any]] = field(default_factory=list)
    proof_attempts: list[dict[str, Any]] = field(default_factory=list)
    epistemic_partition_events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.turns = list(self.turns)[-MERLIN_MAX_HISTORY:] if isinstance(self.turns, list) else []
        self.intents = list(self.intents)[-MERLIN_MAX_INTENTS:] if isinstance(self.intents, list) else []
        self.telemetry = list(self.telemetry)[-MERLIN_MAX_TELEMETRY:] if isinstance(self.telemetry, list) else []
        self.memory_audits = list(self.memory_audits)[-MERLIN_MAX_AUDITS:] if isinstance(self.memory_audits, list) else []
        self.contradiction_events = (
            list(self.contradiction_events)[-MERLIN_MAX_AUDITS:] if isinstance(self.contradiction_events, list) else []
        )
        self.reset_events = list(self.reset_events)[-MERLIN_MAX_AUDITS:] if isinstance(self.reset_events, list) else []
        self.durable_memory = list(self.durable_memory) if isinstance(self.durable_memory, list) else []
        self.compiled_insights = (
            list(self.compiled_insights)[-MERLIN_MAX_AUDITS:] if isinstance(self.compiled_insights, list) else []
        )
        self.quarantined_insights = (
            list(self.quarantined_insights)[-MERLIN_MAX_AUDITS:] if isinstance(self.quarantined_insights, list) else []
        )
        self.route_breadcrumbs = (
            list(self.route_breadcrumbs)[-MERLIN_MAX_BREADCRUMBS:] if isinstance(self.route_breadcrumbs, list) else []
        )
        self.observatory_events = (
            list(self.observatory_events)[-MERLIN_MAX_AUDITS:] if isinstance(self.observatory_events, list) else []
        )
        self.proof_attempts = list(self.proof_attempts)[-MERLIN_MAX_AUDITS:] if isinstance(self.proof_attempts, list) else []
        self.epistemic_partition_events = (
            list(self.epistemic_partition_events)[-MERLIN_MAX_AUDITS:]
            if isinstance(self.epistemic_partition_events, list)
            else []
        )
        if not self.durable_memory:
            for item in DEFAULT_DURABLE_MEMORIES:
                self.remember(item["fact"], scope=item["scope"], source=item["source"], tags=item["tags"])
        self.turns = list(self.turns)[-MERLIN_MAX_HISTORY:]
        self.intents = list(self.intents)[-MERLIN_MAX_INTENTS:]
        self.telemetry = list(self.telemetry)[-MERLIN_MAX_TELEMETRY:]
        self.memory_audits = list(self.memory_audits)[-MERLIN_MAX_AUDITS:]
        self.contradiction_events = list(self.contradiction_events)[-MERLIN_MAX_AUDITS:]
        self.compiled_insights = list(self.compiled_insights)[-MERLIN_MAX_AUDITS:]
        self.quarantined_insights = list(self.quarantined_insights)[-MERLIN_MAX_AUDITS:]
        self.route_breadcrumbs = list(self.route_breadcrumbs)[-MERLIN_MAX_BREADCRUMBS:]
        self.observatory_events = list(self.observatory_events)[-MERLIN_MAX_AUDITS:]
        self.proof_attempts = list(self.proof_attempts)[-MERLIN_MAX_AUDITS:]
        self.epistemic_partition_events = list(self.epistemic_partition_events)[-MERLIN_MAX_AUDITS:]

    def _semantic_hardgate_conflicts(self, text: str) -> list[str]:
        sample = str(text or "")
        conflicts: list[str] = []
        if _W_A_NONZERO_RE.search(sample):
            conflicts.append("w_a_nonzero_claim_conflicts_with_hardgate")
        for lhs, value in _NUMERIC_ASSIGNMENT_RE.findall(sample):
            key = _normalize(lhs).replace(" ", "")
            if key == "kcs" and value != HARDGATE_INVARIANTS["kcs"]:
                conflicts.append(f"k_cs_expected_{HARDGATE_INVARIANTS['kcs']}_received_{value}")
            if key == "nw" and value != HARDGATE_INVARIANTS["nw"]:
                conflicts.append(f"n_w_expected_{HARDGATE_INVARIANTS['nw']}_received_{value}")
            if key == "wa" and value != HARDGATE_INVARIANTS["wa"]:
                conflicts.append(f"w_a_expected_{HARDGATE_INVARIANTS['wa']}_received_{value}")
        return conflicts

    def remember(
        self,
        fact: str,
        *,
        scope: str = "session",
        source: str = "runtime",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        clean_fact = str(fact or "").strip()
        if not clean_fact:
            raise ValueError("fact is required")
        normalized = _normalize(clean_fact)
        for entry in self.durable_memory:
            if entry["normalized_fact"] == normalized and entry["scope"] == scope:
                entry["retrieval_count"] = int(entry.get("retrieval_count", 0))
                entry["last_seen_at"] = _utcnow()
                return dict(entry)
        record = {
            "fact": clean_fact,
            "normalized_fact": normalized,
            "scope": scope,
            "source": source,
            "tags": list(tags or []),
            "namespace": infer_epistemic_namespace(clean_fact),
            "created_at": _utcnow(),
            "last_seen_at": _utcnow(),
            "retrieval_count": 0,
        }
        self.durable_memory.append(record)
        return dict(record)

    def retrieve_memory(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        query_tokens = set(_normalize(query).split())
        if not query_tokens:
            return []
        scored: list[tuple[int, dict[str, Any]]] = []
        for entry in self.durable_memory:
            haystack = set(entry["normalized_fact"].split()) | {str(tag).lower() for tag in entry.get("tags", [])}
            overlap = len(query_tokens & haystack)
            if overlap:
                scored.append((overlap, entry))
        scored.sort(key=lambda item: (-item[0], item[1]["created_at"]))
        selected = [entry for _, entry in scored[:limit]]
        for entry in selected:
            entry["retrieval_count"] += 1
            entry["last_seen_at"] = _utcnow()
        return [dict(entry) for entry in selected]

    def audit_memory(self, query: str) -> dict[str, Any]:
        matched = self.retrieve_memory(query)
        audit = {
            "query": query,
            "timestamp": _utcnow(),
            "matched_memory_count": len(matched),
            "matched_scopes": sorted({item["scope"] for item in matched}),
            "matched_facts": [item["fact"] for item in matched],
            "matched_memory": matched,
        }
        self.memory_audits.append(audit)
        if len(self.memory_audits) > MERLIN_MAX_AUDITS:
            self.memory_audits = self.memory_audits[-MERLIN_MAX_AUDITS:]
        return audit

    def _record_contradiction(self, query: str, response: str) -> None:
        normalized_query = _normalize(query)
        current_gates = set(extract_gate_badges(response))
        for prior in reversed(self.turns):
            if _normalize(prior.get("query", "")) != normalized_query:
                continue
            prior_gates = set(prior.get("gates") or extract_gate_badges(str(prior.get("response", ""))))
            if prior_gates and current_gates and prior_gates != current_gates:
                self.contradiction_events.append({
                    "query": query,
                    "prior_response": str(prior.get("response", ""))[:240],
                    "new_response": str(response or "")[:240],
                    "prior_timestamp": prior.get("timestamp"),
                    "detected_at": _utcnow(),
                    "kind": "gate_drift",
                    "epistemic_uncertainty": _epistemic_uncertainty_profile(
                        f"{query}\n{response}",
                        contradictions=["gate_drift"],
                    ),
                })
                if len(self.contradiction_events) > MERLIN_MAX_AUDITS:
                    self.contradiction_events = self.contradiction_events[-MERLIN_MAX_AUDITS:]
                return
        semantic_conflicts = self._semantic_hardgate_conflicts(f"{query}\n{response}")
        if semantic_conflicts:
            self.contradiction_events.append({
                "query": query,
                "prior_response": "",
                "new_response": str(response or "")[:240],
                "prior_timestamp": "",
                "detected_at": _utcnow(),
                "kind": "semantic_hardgate_conflict",
                "conflicts": semantic_conflicts,
                "epistemic_uncertainty": _epistemic_uncertainty_profile(
                    f"{query}\n{response}",
                    contradictions=semantic_conflicts,
                ),
            })
            if len(self.contradiction_events) > MERLIN_MAX_AUDITS:
                self.contradiction_events = self.contradiction_events[-MERLIN_MAX_AUDITS:]

    def ingest_compiled_insight(self, insight: dict[str, Any]) -> dict[str, Any]:
        item = dict(insight or {})
        item["ingested_at"] = _utcnow()
        item["namespace"] = str(item.get("namespace") or infer_epistemic_namespace(str(item.get("fact", ""))))
        contradictions = list(item.get("contradictions") or [])
        proof_verdict = str(item.get("proof_verdict") or "not_applicable")
        incoming_status = str(item.get("status") or "").strip()
        uncertainty = dict(item.get("epistemic_uncertainty") or {})
        if not uncertainty:
            uncertainty = _epistemic_uncertainty_profile(str(item.get("fact", "")), contradictions=contradictions)
        item["epistemic_uncertainty"] = uncertainty
        if incoming_status in {"[CONTRADICTION_FLAGGED]", "[PROOF_REVIEW_REQUIRED]"}:
            item["status"] = incoming_status
            self.quarantined_insights.append(item)
            if incoming_status == "[CONTRADICTION_FLAGGED]":
                self.contradiction_events.append({
                    "query": str(item.get("source_query", "")),
                    "prior_response": "",
                    "new_response": str(item.get("fact", ""))[:240],
                    "prior_timestamp": "",
                    "detected_at": _utcnow(),
                    "kind": "compiled_insight_contradiction",
                    "conflicts": contradictions,
                    "epistemic_uncertainty": uncertainty,
                })
        elif contradictions:
            item["status"] = "[CONTRADICTION_FLAGGED]"
            self.quarantined_insights.append(item)
            self.contradiction_events.append({
                "query": str(item.get("source_query", "")),
                "prior_response": "",
                "new_response": str(item.get("fact", ""))[:240],
                "prior_timestamp": "",
                "detected_at": _utcnow(),
                "kind": "compiled_insight_contradiction",
                "conflicts": contradictions,
                "epistemic_uncertainty": uncertainty,
            })
        elif proof_verdict in {"needs_steward_review", "rejected"}:
            item["status"] = "[PROOF_REVIEW_REQUIRED]"
            self.quarantined_insights.append(item)
        else:
            item["status"] = "[TRUSTED_COMPILED]"
            self.compiled_insights.append(item)
        if len(self.compiled_insights) > MERLIN_MAX_AUDITS:
            self.compiled_insights = self.compiled_insights[-MERLIN_MAX_AUDITS:]
        if len(self.quarantined_insights) > MERLIN_MAX_AUDITS:
            self.quarantined_insights = self.quarantined_insights[-MERLIN_MAX_AUDITS:]
        if len(self.contradiction_events) > MERLIN_MAX_AUDITS:
            self.contradiction_events = self.contradiction_events[-MERLIN_MAX_AUDITS:]
        return item

    def register_context_envelope(self, envelope: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = dict(envelope or {})
        crumb = {
            "recorded_at": _utcnow(),
            "route_domain": str(payload.get("route_domain") or "unknown"),
            "tool_surface": str(payload.get("tool_surface") or "chat"),
            "viewport_intent_class": str(payload.get("viewport_intent_class") or "unknown"),
            "objective_hint": str(payload.get("objective_hint") or "").strip()[:180],
            "blocker_hint": str(payload.get("blocker_hint") or "").strip()[:180],
            "namespace": infer_epistemic_namespace(
                " ".join(
                    [
                        str(payload.get("route_domain") or ""),
                        str(payload.get("tool_surface") or ""),
                        str(payload.get("objective_hint") or ""),
                        str(payload.get("blocker_hint") or ""),
                    ]
                )
            ),
        }
        self.route_breadcrumbs.append(crumb)
        if len(self.route_breadcrumbs) > MERLIN_MAX_BREADCRUMBS:
            self.route_breadcrumbs = self.route_breadcrumbs[-MERLIN_MAX_BREADCRUMBS:]
        return crumb

    def register_observatory_event(self, event: dict[str, Any]) -> dict[str, Any]:
        item = dict(event or {})
        item["recorded_at"] = _utcnow()
        item["kind"] = str(item.get("kind") or "observatory_update")
        if item["kind"] == "invariant_rupture":
            self.contradiction_events.append({
                "query": str(item.get("source") or "empirical_observatory"),
                "prior_response": "",
                "new_response": str(item.get("message") or "")[:240],
                "prior_timestamp": "",
                "detected_at": item["recorded_at"],
                "kind": "invariant_rupture",
                "conflicts": [str(item.get("tripwire_id") or "tripwire_crossed")],
                "epistemic_uncertainty": _epistemic_uncertainty_profile(
                    str(item.get("message") or "invariant rupture"),
                    contradictions=[str(item.get("tripwire_id") or "tripwire_crossed")],
                ),
            })
        self.observatory_events.append(item)
        if len(self.observatory_events) > MERLIN_MAX_AUDITS:
            self.observatory_events = self.observatory_events[-MERLIN_MAX_AUDITS:]
        if len(self.contradiction_events) > MERLIN_MAX_AUDITS:
            self.contradiction_events = self.contradiction_events[-MERLIN_MAX_AUDITS:]
        return item

    def register_proof_attempt(self, proof_event: dict[str, Any]) -> dict[str, Any]:
        item = dict(proof_event or {})
        item["recorded_at"] = _utcnow()
        item["promotion_allowed"] = False
        self.proof_attempts.append(item)
        if len(self.proof_attempts) > MERLIN_MAX_AUDITS:
            self.proof_attempts = self.proof_attempts[-MERLIN_MAX_AUDITS:]
        return item

    def _namespace_filter(
        self,
        entries: list[dict[str, Any]],
        *,
        allowed_namespaces: set[str],
        target_namespace: str,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        kept: list[dict[str, Any]] = []
        blocked: list[dict[str, Any]] = []
        for entry in entries:
            namespace = str(entry.get("namespace") or infer_epistemic_namespace(str(entry.get("fact", ""))))
            if namespace in allowed_namespaces:
                kept.append(entry)
            else:
                blocked.append({**entry, "namespace": namespace})
        if blocked:
            self.epistemic_partition_events.append({
                "recorded_at": _utcnow(),
                "target_namespace": target_namespace,
                "blocked_count": len(blocked),
                "blocked_namespaces": sorted({str(item.get("namespace") or "general") for item in blocked}),
            })
            if len(self.epistemic_partition_events) > MERLIN_MAX_AUDITS:
                self.epistemic_partition_events = self.epistemic_partition_events[-MERLIN_MAX_AUDITS:]
        return kept, blocked

    def build_accumulated_learnings(
        self,
        query: str,
        *,
        page_context: str = "",
        user_context: str = "",
        context_envelope: dict[str, Any] | None = None,
        target_namespace: str = "general",
        max_items: int = 8,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        envelope = dict(context_envelope or {})
        envelope_tokens = " ".join(
            [
                str(envelope.get("route_domain") or ""),
                str(envelope.get("tool_surface") or ""),
                str(envelope.get("viewport_intent_class") or ""),
                str(envelope.get("objective_hint") or ""),
                str(envelope.get("blocker_hint") or ""),
            ]
        )
        token_query = _normalize(" ".join([query, page_context, user_context, envelope_tokens])).split()
        token_set = {token for token in token_query if token}

        def _score_text(sample: str, fallback: int = 0) -> int:
            if not token_set:
                return fallback
            words = set(_normalize(sample).split())
            return len(words & token_set)

        memory_hits = []
        for item in self.durable_memory:
            last_seen = _parse_timestamp(item.get("last_seen_at"))
            if last_seen and (now - last_seen) > timedelta(days=45):
                continue
            score = _score_text(str(item.get("fact", "")), fallback=int(item.get("retrieval_count", 0)))
            if score <= 0:
                continue
            parsed_last_seen = _parse_timestamp(item.get("last_seen_at"))
            memory_hits.append({
                **item,
                "score": score,
                "namespace": str(item.get("namespace") or infer_epistemic_namespace(str(item.get("fact", "")))),
                "_last_seen_epoch": parsed_last_seen.timestamp() if parsed_last_seen else 0.0,
            })
        memory_hits.sort(
            key=lambda row: (
                -int(row.get("score", 0)),
                -float(row.get("_last_seen_epoch", 0.0)),
            )
        )

        trusted_insights = []
        for insight in self.compiled_insights:
            if str(insight.get("status", "")) != "[TRUSTED_COMPILED]":
                continue
            if list(insight.get("contradictions") or []):
                continue
            fact = str(insight.get("fact", ""))
            if not fact:
                continue
            score = _score_text(fact)
            if score <= 0:
                continue
            uncertainty = dict(insight.get("epistemic_uncertainty") or _epistemic_uncertainty_profile(fact, contradictions=[]))
            if float(uncertainty.get("uncertainty_score", 1.0) or 1.0) > 0.75:
                continue
            trusted_insights.append({
                "fact": fact,
                "source": "compiled_insight",
                "namespace": str(insight.get("namespace") or infer_epistemic_namespace(fact)),
                "score": score,
                "epistemic_uncertainty": uncertainty,
            })
        trusted_insights.sort(
            key=lambda row: (
                -int(row.get("score", 0)),
                float(((row.get("epistemic_uncertainty") or {}).get("uncertainty_score", 1.0) or 1.0)),
            )
        )

        contradiction_signals = []
        for event in self.contradiction_events[-40:]:
            signal_text = str(event.get("new_response") or event.get("query") or "")
            score = _score_text(signal_text)
            if score <= 0:
                continue
            contradiction_signals.append({
                "fact": signal_text[:220],
                "source": str(event.get("kind") or "contradiction"),
                "namespace": infer_epistemic_namespace(signal_text),
                "score": score,
                "epistemic_uncertainty": dict(event.get("epistemic_uncertainty") or _epistemic_uncertainty_profile(signal_text, contradictions=list(event.get("conflicts") or []))),
            })
        contradiction_signals.sort(
            key=lambda row: (
                -int(row.get("score", 0)),
                -float(((row.get("epistemic_uncertainty") or {}).get("uncertainty_score", 0.0) or 0.0)),
            )
        )

        combined = memory_hits[: max_items * 2] + trusted_insights[: max_items * 2] + contradiction_signals[: max_items]
        allowed = {"general", "governance", "adjacent_track", "physics_hardgate", "narrative_speculative"}
        if target_namespace in {"physics_hardgate", "kernel_p", "hardgate_solver"}:
            allowed = {"physics_hardgate"}
        filtered, blocked = self._namespace_filter(
            combined,
            allowed_namespaces=allowed,
            target_namespace=target_namespace,
        )
        filtered.sort(
            key=lambda item: (
                -int(item.get("score", 0)),
                float(((item.get("epistemic_uncertainty") or {}).get("uncertainty_score", 1.0) or 1.0)),
                0 if str(item.get("source", "")).startswith("compiled") else 1,
            )
        )
        selected = filtered[:max_items]
        lines = []
        for item in selected:
            uncertainty = dict(item.get("epistemic_uncertainty") or {})
            tag = str(item.get("source") or "memory")
            namespace = str(item.get("namespace") or "general")
            risk = str(uncertainty.get("risk_band") or "unknown")
            lines.append(f"- ({namespace}) [{tag}] {str(item.get('fact', '')).strip()} | uncertainty={risk}")
        if not lines:
            lines = ["- No high-confidence accumulated learnings matched this query."]
        envelope_summary = (
            f"route={envelope.get('route_domain', 'unknown')} "
            f"surface={envelope.get('tool_surface', 'chat')} "
            f"viewport={envelope.get('viewport_intent_class', 'unknown')}"
        )
        def _strip_private(item: dict[str, Any]) -> dict[str, Any]:
            return {key: value for key, value in item.items() if not str(key).startswith("_")}
        return {
            "text": "\n".join(lines),
            "count": len(selected),
            "blocked_count": len(blocked),
            "target_namespace": target_namespace,
            "envelope_summary": envelope_summary,
            "selected": [_strip_private(item) for item in selected],
            "blocked": [_strip_private(item) for item in blocked[:10]],
        }

    def add_turn(self, query: str, response: str, *, gates: list[str] | None = None) -> None:
        visible_gates = list(gates or extract_gate_badges(response))
        detected_intent = infer_intent(query)
        self._record_contradiction(query, response)
        self.turns.append({
            "query": query,
            "response": response,
            "gates": visible_gates,
            "intent": detected_intent,
            "timestamp": _utcnow(),
        })
        self.add_intent(
            query=query,
            intent=detected_intent,
            scope="session",
            provenance_sources=["query_text", "gate_badges"],
        )
        if len(self.turns) > MERLIN_MAX_HISTORY:
            self.turns = self.turns[-MERLIN_MAX_HISTORY:]

    def add_intent(
        self,
        *,
        query: str,
        intent: str,
        scope: str = "session",
        provenance_sources: list[str] | None = None,
    ) -> None:
        self.intents.append({
            "query": query,
            "intent": intent,
            "scope": scope,
            "provenance_sources": list(provenance_sources or []),
            "timestamp": _utcnow(),
        })
        if len(self.intents) > MERLIN_MAX_INTENTS:
            self.intents = self.intents[-MERLIN_MAX_INTENTS:]

    def get_history(self) -> list[dict[str, Any]]:
        return list(self.turns)

    def get_intents(self) -> list[dict[str, Any]]:
        return list(self.intents)

    def clear(self, *, reason: str = "manual") -> None:
        self.turns.clear()
        self.intents.clear()
        self.reset_events.append({
            "reason": reason,
            "timestamp": _utcnow(),
        })

    def set_sentinel_mode(self, mode: str) -> None:
        self.sentinel_mode = mode

    def register_policy_strike(self) -> int:
        self.policy_strikes += 1
        return self.policy_strikes

    def register_privileged_attempt(self) -> int:
        self.privileged_attempts += 1
        return self.privileged_attempts

    def record_run(self, run: dict[str, Any]) -> None:
        self.telemetry.append(dict(run))
        if len(self.telemetry) > MERLIN_MAX_TELEMETRY:
            self.telemetry = self.telemetry[-MERLIN_MAX_TELEMETRY:]

    def get_memory_state(self) -> dict[str, Any]:
        scopes: dict[str, int] = {}
        for entry in self.durable_memory:
            scopes[entry["scope"]] = scopes.get(entry["scope"], 0) + 1
        return {
            "tiers": ["session", "user", "repository"],
            "durable_memory_count": len(self.durable_memory),
            "durable_memory_by_scope": scopes,
            "contradiction_event_count": len(self.contradiction_events),
            "compiled_insight_count": len(self.compiled_insights),
            "quarantined_insight_count": len(self.quarantined_insights),
            "route_breadcrumb_count": len(self.route_breadcrumbs),
            "observatory_event_count": len(self.observatory_events),
            "proof_attempt_count": len(self.proof_attempts),
            "epistemic_partition_event_count": len(self.epistemic_partition_events),
            "audit_count": len(self.memory_audits),
            "recent_memory_audits": self.memory_audits[-5:],
            "recent_contradictions": self.contradiction_events[-5:],
            "recent_compiled_insights": self.compiled_insights[-5:],
            "recent_quarantined_insights": self.quarantined_insights[-5:],
            "recent_route_breadcrumbs": self.route_breadcrumbs[-5:],
            "recent_observatory_events": self.observatory_events[-5:],
            "recent_epistemic_partition_events": self.epistemic_partition_events[-5:],
            "durable_memory": [
                {
                    "fact": item["fact"],
                    "scope": item["scope"],
                    "source": item["source"],
                    "tags": item["tags"],
                    "namespace": item.get("namespace", "general"),
                    "retrieval_count": item["retrieval_count"],
                }
                for item in self.durable_memory[-10:]
            ],
        }

    def get_public_memory_state(self) -> dict[str, Any]:
        state = self.get_memory_state()
        return {
            "tiers": state["tiers"],
            "durable_memory_count": state["durable_memory_count"],
            "durable_memory_by_scope": state["durable_memory_by_scope"],
            "contradiction_event_count": state["contradiction_event_count"],
            "compiled_insight_count": state["compiled_insight_count"],
            "quarantined_insight_count": state["quarantined_insight_count"],
            "route_breadcrumb_count": state["route_breadcrumb_count"],
            "observatory_event_count": state["observatory_event_count"],
            "proof_attempt_count": state["proof_attempt_count"],
            "epistemic_partition_event_count": state["epistemic_partition_event_count"],
            "audit_count": state["audit_count"],
        }

    def get_compiled_training_insights(self) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        for item in self.compiled_insights[-50:]:
            fact = str(item.get("fact", "")).strip()
            if not fact:
                continue
            if str(item.get("status", "")) != "[TRUSTED_COMPILED]":
                continue
            selected.append(dict(item))
        return selected

    def get_telemetry_summary(self, *, public: bool = False) -> dict[str, Any]:
        summary = summarize_runs(self.telemetry)
        if public:
            return {
                "count": summary["count"],
                "providers": summary["providers"],
                "average_latency_ms": summary["average_latency_ms"],
                "average_energy_joules": summary["average_energy_joules"],
                "average_provenance_sources": summary["average_provenance_sources"],
            }
        return summary

    def compressed(self, query: str = "", *, matched_memory: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        base = compress_context(self.turns)
        matched = list(matched_memory or [])
        if query and not matched:
            matched = self.retrieve_memory(query)
        memory_summary = " | ".join(f"[{item['scope']}] {item['fact']}" for item in matched[:3])
        contradiction_summary = (
            f" contradictions={len(self.contradiction_events)}"
            if self.contradiction_events else
            ""
        )
        summary = str(base.get("summary", "")).strip()
        if memory_summary:
            summary = f"{summary}\n[Durable Memory]\n{memory_summary}".strip()
        if contradiction_summary:
            summary = f"{summary}\n[Memory Audit]{contradiction_summary}".strip()
        if self.route_breadcrumbs:
            last = self.route_breadcrumbs[-1]
            summary = (
                f"{summary}\n[Route Breadcrumb] domain={last.get('route_domain')} "
                f"surface={last.get('tool_surface')} viewport={last.get('viewport_intent_class')}"
            ).strip()
        base["summary"] = summary
        base["memory_hits"] = len(matched)
        base["matched_memory"] = matched
        return base

    def to_dict(self) -> dict[str, Any]:
        return {
            "turns": list(self.turns),
            "intents": list(self.intents),
            "policy_strikes": int(self.policy_strikes),
            "reset_events": list(self.reset_events),
            "sentinel_mode": str(self.sentinel_mode),
            "privileged_attempts": int(self.privileged_attempts),
            "durable_memory": list(self.durable_memory),
            "contradiction_events": list(self.contradiction_events),
            "memory_audits": list(self.memory_audits),
            "telemetry": list(self.telemetry),
            "compiled_insights": list(self.compiled_insights),
            "quarantined_insights": list(self.quarantined_insights),
            "route_breadcrumbs": list(self.route_breadcrumbs),
            "observatory_events": list(self.observatory_events),
            "proof_attempts": list(self.proof_attempts),
            "epistemic_partition_events": list(self.epistemic_partition_events),
        }

    def to_persistence_dict(self) -> dict[str, Any]:
        telemetry = []
        for run in self.telemetry:
            telemetry.append({
                "recorded_at": run.get("recorded_at"),
                "provider": run.get("provider"),
                "lane": run.get("lane"),
                "context_source": run.get("context_source"),
                "tool_rounds": run.get("tool_rounds"),
                "used_websearch": run.get("used_websearch"),
                "latency_ms": run.get("latency_ms"),
                "tokens": dict(run.get("tokens") or {}),
                "cost": dict(run.get("cost") or {}),
                "energy": dict(run.get("energy") or {}),
                "quality_signals": dict(run.get("quality_signals") or {}),
            })
        compiled: list[dict[str, Any]] = []
        for item in self.compiled_insights:
            compiled.append({
                "insight_id": item.get("insight_id"),
                "schema_version": item.get("schema_version"),
                "kind": item.get("kind"),
                "status": item.get("status"),
                "proof_verdict": item.get("proof_verdict"),
                "theorem_hits": list(item.get("theorem_hits") or []),
                "contradictions": list(item.get("contradictions") or []),
                "compiled_at": item.get("compiled_at"),
                "ingested_at": item.get("ingested_at"),
                "fact_sha256": _redacted_digest(str(item.get("fact", ""))),
                "source_query_sha256": _redacted_digest(str(item.get("source_query", ""))),
                "redacted_for_persistence": True,
            })
        quarantined: list[dict[str, Any]] = []
        for item in self.quarantined_insights:
            quarantined.append({
                "insight_id": item.get("insight_id"),
                "schema_version": item.get("schema_version"),
                "kind": item.get("kind"),
                "status": item.get("status"),
                "proof_verdict": item.get("proof_verdict"),
                "theorem_hits": list(item.get("theorem_hits") or []),
                "contradictions": list(item.get("contradictions") or []),
                "compiled_at": item.get("compiled_at"),
                "ingested_at": item.get("ingested_at"),
                "fact_sha256": _redacted_digest(str(item.get("fact", ""))),
                "source_query_sha256": _redacted_digest(str(item.get("source_query", ""))),
                "redacted_for_persistence": True,
            })
        redacted_contradictions: list[dict[str, Any]] = []
        for item in self.contradiction_events:
            redacted_contradictions.append({
                "detected_at": item.get("detected_at"),
                "kind": item.get("kind", "gate_drift"),
                "conflicts": list(item.get("conflicts") or []),
                "query_sha256": _redacted_digest(str(item.get("query", ""))),
            })
        payload = self.to_dict()
        payload["turns"] = []
        payload["intents"] = []
        payload["telemetry"] = telemetry
        payload["durable_memory_redacted"] = [
            {
                "scope": item.get("scope"),
                "source": item.get("source"),
                "tags": list(item.get("tags") or []),
                "retrieval_count": int(item.get("retrieval_count", 0) or 0),
                "fact_sha256": _redacted_digest(str(item.get("fact", ""))),
                "created_at": item.get("created_at"),
                "last_seen_at": item.get("last_seen_at"),
            }
            for item in self.durable_memory
        ]
        payload["durable_memory"] = []
        payload["compiled_insights"] = compiled
        payload["quarantined_insights"] = quarantined
        payload["contradiction_events"] = redacted_contradictions
        payload["route_breadcrumbs"] = [
            {
                "recorded_at": item.get("recorded_at"),
                "route_domain": item.get("route_domain"),
                "tool_surface": item.get("tool_surface"),
                "viewport_intent_class": item.get("viewport_intent_class"),
                "namespace": item.get("namespace"),
                "objective_hint_sha256": _redacted_digest(str(item.get("objective_hint", ""))),
                "blocker_hint_sha256": _redacted_digest(str(item.get("blocker_hint", ""))),
            }
            for item in self.route_breadcrumbs
        ]
        payload["observatory_events"] = list(self.observatory_events)[-MERLIN_MAX_AUDITS:]
        payload["proof_attempts"] = list(self.proof_attempts)[-MERLIN_MAX_AUDITS:]
        payload["epistemic_partition_events"] = list(self.epistemic_partition_events)[-MERLIN_MAX_AUDITS:]
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MerlinSession":
        data = dict(payload or {})
        return cls(
            turns=list(data.get("turns") or []),
            intents=list(data.get("intents") or []),
            policy_strikes=int(data.get("policy_strikes", 0) or 0),
            reset_events=list(data.get("reset_events") or []),
            sentinel_mode=str(data.get("sentinel_mode") or "MONITOR"),
            privileged_attempts=int(data.get("privileged_attempts", 0) or 0),
            durable_memory=list(data.get("durable_memory") or []),
            contradiction_events=list(data.get("contradiction_events") or []),
            memory_audits=list(data.get("memory_audits") or []),
            telemetry=list(data.get("telemetry") or []),
            compiled_insights=list(data.get("compiled_insights") or []),
            quarantined_insights=list(data.get("quarantined_insights") or []),
            route_breadcrumbs=list(data.get("route_breadcrumbs") or []),
            observatory_events=list(data.get("observatory_events") or []),
            proof_attempts=list(data.get("proof_attempts") or []),
            epistemic_partition_events=list(data.get("epistemic_partition_events") or []),
        )
