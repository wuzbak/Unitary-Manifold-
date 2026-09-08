# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Advanced Merlin runtime contracts for Mythos/Astra parity and beyond."""

from __future__ import annotations

import hashlib
import math
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any

from .lean4_index import LEAN4_THEOREM_SAMPLE, search_theorems
from .merlin_benchmark import get_stage_a_benchmark_corpus

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\+?\d[\d\-\s().]{7,}\d")
_THEOREM_CUE_RE = re.compile(r"\b(theorem|lemma|conjecture|proof|derive)\b", re.IGNORECASE)
_W_A_NONZERO_RE = re.compile(r"w[\s_\-]*a\s*(?:!=|[><~]=?)\s*0", re.IGNORECASE)
_NUMERIC_ASSIGNMENT_RE = re.compile(r"(k[\s_\-]*cs|n[\s_\-]*w|w[\s_\-]*a)\s*=\s*([\-]?\d+(?:\.\d+)?)", re.IGNORECASE)

_RUNTIME_INVARIANTS = {
    "kcs": "74",
    "nw": "5",
    "wa": "0",
}

_EMPIRICAL_TRIPWIRES = {
    "DESI_DR3_WA_CEILING": {
        "feed": "DESI",
        "metric": "w_a",
        "operator": "<=",
        "threshold": 0.0,
        "trip_if": "greater",
        "description": "Hardgate ceiling requires w_a ≤ 0 for certified lane.",
    },
    "LITEBIRD_BETA_WINDOW": {
        "feed": "LiteBIRD",
        "metric": "beta_deg",
        "operator": "between",
        "threshold": [0.22, 0.38],
        "trip_if": "outside",
        "description": "Braided-winding admissible birefringence window.",
    },
    "LITEBIRD_BETA_GAP": {
        "feed": "LiteBIRD",
        "metric": "beta_deg",
        "operator": "not_between",
        "threshold": [0.29, 0.31],
        "trip_if": "inside",
        "description": "Predicted exclusion gap [0.29°,0.31°].",
    },
    "JUNO_DM21_TENSION": {
        "feed": "JUNO",
        "metric": "delta_m2_21_sigma",
        "operator": "<=",
        "threshold": 1.5,
        "trip_if": "greater",
        "description": "Residual tension guardrail.",
    },
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_text(sample: str) -> str:
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", str(sample or ""))
    text = _PHONE_RE.sub("[REDACTED_PHONE]", text)
    return " ".join(text.split()).strip()


def _semantic_projection(sample: str, *, kind: str, contradictions: list[str], theorem_hits: list[str]) -> str:
    lowered = sample.lower()
    tags = []
    for token in ("pillar", "proof", "theorem", "constraint", "tension", "falsif", "litebird", "desi", "juno"):
        if token in lowered:
            tags.append(token)
    if not tags:
        tags = ["general"]
    contradiction_tag = ",".join(contradictions) if contradictions else "none"
    theorem_tag = ",".join(theorem_hits[:3]) if theorem_hits else "none"
    return (
        f"semantic_insight kind={kind} tags={','.join(sorted(set(tags)))} "
        f"contradictions={contradiction_tag} theorem_hits={theorem_tag}"
    )


def _proof_verdict(fact: str) -> tuple[str, list[str]]:
    if not _THEOREM_CUE_RE.search(fact):
        return "not_applicable", []
    theorem_hits = []
    lowered = fact.lower()
    for theorem in LEAN4_THEOREM_SAMPLE:
        if theorem.lower() in lowered:
            theorem_hits.append(theorem)
    if theorem_hits:
        return "verified", theorem_hits
    candidate = search_theorems(fact)
    if candidate:
        return "needs_steward_review", candidate[:3]
    return "rejected", []


def _detect_contradictions(sample: str) -> list[str]:
    conflicts: list[str] = []
    if _W_A_NONZERO_RE.search(sample):
        conflicts.append("w_a_nonzero_claim_conflicts_with_hardgate")
    for lhs, value in _NUMERIC_ASSIGNMENT_RE.findall(sample):
        key = re.sub(r"[^a-z0-9]", "", lhs.lower())
        if key == "kcs" and value != _RUNTIME_INVARIANTS["kcs"]:
            conflicts.append(f"k_cs_expected_{_RUNTIME_INVARIANTS['kcs']}_received_{value}")
        if key == "nw" and value != _RUNTIME_INVARIANTS["nw"]:
            conflicts.append(f"n_w_expected_{_RUNTIME_INVARIANTS['nw']}_received_{value}")
        if key == "wa" and value != _RUNTIME_INVARIANTS["wa"]:
            conflicts.append(f"w_a_expected_{_RUNTIME_INVARIANTS['wa']}_received_{value}")
    return conflicts


def _insight_kind(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("tension", "desi", "litebird", "juno")):
        return "falsification_lead"
    if any(token in lowered for token in ("constraint", "invariant", "must", "require")):
        return "structural_constraint"
    if _THEOREM_CUE_RE.search(text):
        return "theorem_candidate"
    return "operational_heuristic"


def _extract_distilled_candidates(query: str, answer: str) -> list[str]:
    candidates: list[str] = []
    cleaned_query = _sanitize_text(query)
    cleaned_answer = _sanitize_text(answer)
    if cleaned_query and (
        any(term in cleaned_query.lower() for term in ("pillar", "proof", "theorem", "constraint", "tension", "falsif"))
        or bool(_detect_contradictions(cleaned_query))
    ):
        candidates.append(cleaned_query[:220])
    for chunk in re.split(r"[.\n]+", cleaned_answer):
        part = chunk.strip()
        if len(part) < 24:
            continue
        if any(term in part.lower() for term in ("pillar", "proof", "theorem", "constraint", "tension", "falsif")) or _detect_contradictions(part):
            candidates.append(part[:280])
        if len(candidates) >= 4:
            break
    return candidates[:4]


def get_client_blind_ingestion_contract() -> dict[str, Any]:
    return {
        "mode": "unidirectional_client_blind_ingestion",
        "client_surface": {
            "history_storage": "volatile_only_no_local_history",
            "expected_wipe_event": "tab_close_or_process_exit",
            "disk_storage": "disallowed",
        },
        "runtime_surface": {
            "durable_profiles": "server_side_only",
            "compiled_memory": "deidentified_semantic_artifacts_only",
            "compatibility_shim": "/api/ox",
            "primary_endpoint": "/api/merlin",
        },
        "handshake_policy": {
            "token_kind": "ephemeral_signed_profile_token",
            "identity_bridge": "verifyMerlinIdentity",
            "replay_policy": "refuse_invalid_or_replayed_handshake",
        },
    }


def get_observatory_ingestion_lane() -> dict[str, Any]:
    return {
        "lane": "m6_empirical_observatory_ingestion",
        "sources": ["LiteBIRD", "JUNO", "DESI_DR3"],
        "policy": "fail_closed_on_missing_provenance_or_incomplete_likelihoods",
        "outputs": [
            "hardgate_comparison_records",
            "falsification_tripwires",
            "readiness_manifest_updates",
        ],
    }


def _evaluate_tripwire_value(*, value: float, definition: dict[str, Any]) -> bool:
    op = str(definition.get("operator") or "")
    threshold = definition.get("threshold")
    if op == "<=":
        return value <= float(threshold)
    if op == ">=":
        return value >= float(threshold)
    if op == "between" and isinstance(threshold, (list, tuple)) and len(threshold) == 2:
        low, high = float(threshold[0]), float(threshold[1])
        return low <= value <= high
    if op == "not_between" and isinstance(threshold, (list, tuple)) and len(threshold) == 2:
        low, high = float(threshold[0]), float(threshold[1])
        return not (low <= value <= high)
    return False


def empirical_observatory_check(observed: dict[str, Any] | None = None) -> dict[str, Any]:
    observed = dict(observed or {})
    records: list[dict[str, Any]] = []
    ruptures: list[dict[str, Any]] = []
    for tripwire_id, definition in _EMPIRICAL_TRIPWIRES.items():
        metric = str(definition.get("metric") or "")
        feed = str(definition.get("feed") or "")
        raw_value = observed.get(metric)
        if raw_value is None:
            checked_at = _utcnow()
            records.append({
                "tripwire_id": tripwire_id,
                "feed": feed,
                "metric": metric,
                "status": "missing",
                "message": f"Missing observed value for {metric}; fail-closed.",
                "checked_at": checked_at,
            })
            ruptures.append({
                "kind": "invariant_rupture",
                "tripwire_id": tripwire_id,
                "source": feed,
                "message": f"Invariant rupture: missing observed metric {metric}",
                "definition": definition,
                "checked_at": checked_at,
            })
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            checked_at = _utcnow()
            records.append({
                "tripwire_id": tripwire_id,
                "feed": feed,
                "metric": metric,
                "status": "invalid",
                "message": f"Invalid observed value for {metric}; fail-closed.",
                "checked_at": checked_at,
            })
            ruptures.append({
                "kind": "invariant_rupture",
                "tripwire_id": tripwire_id,
                "source": feed,
                "message": f"Invariant rupture: invalid observed metric {metric}",
                "definition": definition,
                "checked_at": checked_at,
            })
            continue
        if not math.isfinite(value):
            checked_at = _utcnow()
            records.append({
                "tripwire_id": tripwire_id,
                "feed": feed,
                "metric": metric,
                "status": "invalid",
                "message": f"Non-finite observed value for {metric}; fail-closed.",
                "checked_at": checked_at,
            })
            ruptures.append({
                "kind": "invariant_rupture",
                "tripwire_id": tripwire_id,
                "source": feed,
                "message": f"Invariant rupture: non-finite observed metric {metric}",
                "definition": definition,
                "checked_at": checked_at,
            })
            continue
        passed = _evaluate_tripwire_value(value=value, definition=definition)
        status = "pass" if passed else "rupture"
        record = {
            "tripwire_id": tripwire_id,
            "feed": feed,
            "metric": metric,
            "status": status,
            "observed": value,
            "definition": definition,
            "checked_at": _utcnow(),
        }
        records.append(record)
        if not passed:
            ruptures.append({
                "kind": "invariant_rupture",
                "tripwire_id": tripwire_id,
                "source": feed,
                "message": f"Invariant rupture: {tripwire_id} observed {metric}={value}",
                "observed": value,
                "definition": definition,
                "checked_at": record["checked_at"],
            })
    fail_closed = any(item.get("status") in {"missing", "invalid"} for item in records)
    return {
        "ok": len(ruptures) == 0 and not fail_closed,
        "records": records,
        "ruptures": ruptures,
        "fail_closed": fail_closed,
        "sources": sorted({str(item.get("feed") or "") for item in records}),
    }


def run_kernel_p_lean_proof_probe(
    *,
    conjecture: str,
    context: str = "",
    enable_repl: bool | None = None,
) -> dict[str, Any]:
    statement = _sanitize_text(conjecture)[:420]
    target = f"{statement}\n{_sanitize_text(context)[:420]}".strip()
    verdict, theorem_hits = _proof_verdict(target)
    repl_requested = bool(enable_repl)
    repl_enabled = repl_requested and str(os.environ.get("MERLIN_ENABLE_LEAN_BRIDGE") or "").strip().lower() in {"1", "true", "yes", "on"}
    lean_binary = shutil.which("lean")
    repl_available = bool(lean_binary)
    repl_used = False
    repl_output = ""
    if repl_enabled and repl_available:
        try:
            completed = subprocess.run(
                [lean_binary, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=4,
            )
            repl_used = True
            repl_output = (completed.stdout or completed.stderr or "").strip()[:220]
        except Exception as exc:  # pragma: no cover - environment-dependent
            repl_output = f"lean_repl_probe_failed: {exc}"
    return {
        "conjecture": statement,
        "proof_verdict": verdict,
        "theorem_hits": theorem_hits,
        "repl_requested": repl_requested,
        "repl_enabled": repl_enabled,
        "repl_available": repl_available,
        "repl_used": repl_used,
        "repl_output": repl_output,
        "promotion_allowed": False,
        "governance_note": "Proof probes can strengthen evidence but cannot auto-promote hardgate claims.",
        "checked_at": _utcnow(),
    }


async def run_post_turn_compilation(
    *,
    query: str,
    answer: str,
    provenance: dict[str, Any],
    session: Any,
    persist: bool = True,
) -> dict[str, Any]:
    candidates = _extract_distilled_candidates(query, answer)
    artifacts: list[dict[str, Any]] = []
    for fact in candidates:
        contradictions = _detect_contradictions(fact)
        proof_verdict, theorem_hits = _proof_verdict(fact)
        kind = _insight_kind(fact)
        artifact = {
            "insight_id": hashlib.sha256(fact.encode("utf-8")).hexdigest()[:16],
            "schema_version": "merlin_compiled_insight_v1",
            "fact": _semantic_projection(fact, kind=kind, contradictions=contradictions, theorem_hits=theorem_hits),
            "kind": kind,
            "source_query": hashlib.sha256(_sanitize_text(query).encode("utf-8")).hexdigest(),
            "provenance_source_count": len(list((provenance or {}).get("sources") or [])),
            "contradictions": contradictions,
            "proof_verdict": proof_verdict,
            "theorem_hits": theorem_hits,
            "compiled_at": _utcnow(),
        }
        if persist:
            artifacts.append(session.ingest_compiled_insight(artifact))
        else:
            preview = dict(artifact)
            if preview["contradictions"]:
                preview["status"] = "[CONTRADICTION_FLAGGED]"
            elif preview["proof_verdict"] in {"needs_steward_review", "rejected"}:
                preview["status"] = "[PROOF_REVIEW_REQUIRED]"
            else:
                preview["status"] = "[TRUSTED_COMPILED]"
            artifacts.append(preview)
    mode = str(os.environ.get("MERLIN_CONTRADICTION_ENFORCEMENT") or "audit_only").strip().lower()
    contradiction_count = sum(1 for item in artifacts if item.get("status") == "[CONTRADICTION_FLAGGED]")
    unresolved_proof_count = sum(1 for item in artifacts if item.get("status") == "[PROOF_REVIEW_REQUIRED]")
    should_block_output = mode == "enforce" and (contradiction_count > 0 or unresolved_proof_count > 0)
    return {
        "mode": mode,
        "compiled_count": len(artifacts),
        "contradiction_count": contradiction_count,
        "unresolved_proof_count": unresolved_proof_count,
        "should_block_output": should_block_output,
        "artifacts": artifacts,
    }


def get_optimization_priorities() -> dict[str, Any]:
    """Return ordered top-priority optimization tracks for Merlin."""
    return {
        "order": [
            {
                "rank": 1,
                "name": "memory_integrity_and_recall",
                "goal": "Eliminate amnesia-like failures with persistent, audited multi-tier memory.",
                "acceptance": [
                    "identity_policy_persistence",
                    "session_summary_recall_consistency",
                    "contradiction_detection_on_context_conflicts",
                ],
            },
            {
                "rank": 2,
                "name": "truthfulness_and_epistemic_calibration",
                "goal": "Raise factual precision while keeping uncertainty explicit and non-deceptive.",
                "acceptance": [
                    "mandatory_gate_label_coverage",
                    "not_found_path_correctness",
                    "citation_traceability_per_response",
                ],
            },
            {
                "rank": 3,
                "name": "safety_and_privileged_change_control",
                "goal": "Harden do-no-harm and identity-gated change control for Merlin modifications.",
                "acceptance": [
                    "sentinel_warn_then_reset_stability",
                    "privileged_request_refusal_when_unverified",
                    "zero_policy_bypass_on_known_attack_prompts",
                ],
            },
            {
                "rank": 4,
                "name": "orchestration_depth_and_tool_reliability",
                "goal": "Improve multi-step execution quality with bounded, auditable tool graphs.",
                "acceptance": [
                    "tool_chain_success_rate_target",
                    "deterministic_replay_pack_generation",
                    "safe_fallback_when_tools_conflict",
                ],
            },
            {
                "rank": 5,
                "name": "competitive_runtime_performance",
                "goal": "Achieve parity or better against Mythos/Astra class environments under constraints.",
                "acceptance": [
                    "quality_parity_or_better",
                    "latency_budget_compliance",
                    "energy_per_successful_task_improvement",
                ],
            },
        ],
        "selection_basis": "User-directed maximum-rigor roadmap, emphasizing memory, integrity, safety, orchestration, and competitiveness.",
    }


def get_mythos_astra_runtime_contract() -> dict[str, Any]:
    """Return Merlin runtime contract for Mythos/Astra environments."""
    return {
        "positioning": {
            "primary_mode": "competitive_agent_parity",
            "secondary_mode": "universal_cognitive_layer_wrapper",
            "controller_mode": "governance_orchestration_supervisor",
        },
        "capability_contract": {
            "required_surfaces": [
                "safe_query_interface",
                "policy_first_orchestration",
                "typed_provenance_and_gate_badges",
                "identity_trust_and_privilege_controls",
                "deterministic_refusal_for_harmful_requests",
            ],
            "compatibility": {
                "legacy_paths_retained": ["/api/ox", "/api/ox/status"],
                "merlin_paths_primary": [
                    "/api/merlin",
                    "/api/merlin/status",
                    "/api/merlin/program",
                    "/api/merlin/identity",
                    "/api/merlin/policy",
                ],
            },
        },
        "agent_graph": {
            "style": "parallel_specialist_mesh_with_final_audit",
            "lanes": [
                {"name": "research_lane", "role": "retrieve and align evidence"},
                {"name": "reasoning_lane", "role": "synthesize candidate answer"},
                {"name": "verification_lane", "role": "check claims and sources"},
                {"name": "safety_lane", "role": "enforce Sentinel and policy"},
                {"name": "governance_lane", "role": "boundary and privilege compliance"},
            ],
            "merge_rule": "Only emit final answer when verification+safety+governance lanes are all green.",
        },
        "environment_constraints": {
            "uncertain_identity_behavior": "normal_access_only_refuse_privileged_changes",
            "reset_policy": "session_clear_on_repeat_policy_violation_policy_memory_retained",
            "client_blind_ingestion": get_client_blind_ingestion_contract(),
            "observatory_ingestion_lane": get_observatory_ingestion_lane(),
            "disallowed_domains": [
                "unconsensual_sexualization",
                "harm_planning",
                "weapons",
                "rights_violations",
                "illegal_activity_assistance",
            ],
        },
    }


def get_advanced_execution_graph() -> dict[str, Any]:
    """Return a machine-readable execution graph for max-rigor Merlin runs."""
    return {
        "graph_name": "merlin_max_rigor_execution",
        "nodes": [
            {"id": "N1", "name": "ingest_context", "type": "retrieval"},
            {"id": "N2", "name": "identity_gate", "type": "policy"},
            {"id": "N3", "name": "sentinel_scan", "type": "policy"},
            {"id": "N4", "name": "parallel_reasoning", "type": "orchestration"},
            {"id": "N5", "name": "source_verification", "type": "verification"},
            {"id": "N6", "name": "governance_boundary_check", "type": "verification"},
            {"id": "N7", "name": "contract_render", "type": "response"},
            {"id": "N8", "name": "postmortem_memory_write", "type": "memory"},
        ],
        "edges": [
            ["N1", "N2"],
            ["N2", "N3"],
            ["N3", "N4"],
            ["N4", "N5"],
            ["N5", "N6"],
            ["N6", "N7"],
            ["N7", "N8"],
        ],
        "hard_stops": ["identity_gate_fail_for_privileged", "sentinel_policy_block", "verification_conflict_unresolved"],
    }


def get_benchmark_suite() -> dict[str, Any]:
    """Return benchmark harness definition for competitive evaluation."""
    corpus = get_stage_a_benchmark_corpus()
    return {
        "tracks": [
            "memory_persistence",
            "factuality_and_citation",
            "refusal_correctness",
            "tool_orchestration_accuracy",
            "latency_cost_energy",
            "mythos_astra_parity",
        ],
        "rubric": [
            "task_success",
            "factual_precision",
            "epistemic_honesty",
            "safety_compliance",
            "governance_compliance",
            "energy_per_successful_task",
        ],
        "stage_a_corpus": corpus,
        "stage_a_required_shadow_fields": [
            "provider",
            "lane",
            "latency_ms",
            "energy.estimated_joules",
            "quality_signals",
        ],
        "promotion_gate": "No promotion to broader autonomy unless all critical tracks pass with zero high-severity policy failures.",
    }
