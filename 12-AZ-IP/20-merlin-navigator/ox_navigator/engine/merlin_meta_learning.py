# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Meta-learning helpers for Merlin's self-improvement loop."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .merlin_memory import MerlinSession


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def consolidate_memory(*, session: MerlinSession, limit: int = 10) -> dict[str, Any]:
    cap = max(1, min(int(limit or 10), 50))
    durable = list(session.durable_memory)[-cap:]
    compiled = list(session.get_compiled_training_insights())[-cap:]
    contradiction_count = len(session.contradiction_events)
    candidate_gaps: list[str] = []
    if contradiction_count:
        candidate_gaps.append("Contradiction pressure detected; prioritize contradiction remediation before promotion.")
    if not compiled:
        candidate_gaps.append("No trusted compiled insights available; run synthesis before export.")
    if len(durable) < 5:
        candidate_gaps.append("Durable memory coverage is thin; add governed memory captures across kernels.")
    return {
        "ok": True,
        "generated_at": _utcnow(),
        "counts": {
            "durable_memory": len(durable),
            "trusted_compiled_insights": len(compiled),
            "contradiction_events": contradiction_count,
        },
        "synthesized_facts": [item.get("fact", "") for item in durable[-5:]],
        "trusted_insight_ids": [str(item.get("id") or item.get("digest") or "") for item in compiled[-5:]],
        "detected_gaps": candidate_gaps or ["No immediate structural gaps detected in sampled memory tiers."],
        "next_action": "Use detected_gaps to seed the next training curation pass before promotion attempts.",
    }


def run_self_audit(*, session: MerlinSession) -> dict[str, Any]:
    telemetry = list(session.telemetry)
    total = len(telemetry)
    if not total:
        return {
            "ok": True,
            "generated_at": _utcnow(),
            "calibration": {"sample_count": 0, "contract_pass_rate": 0.0, "contradiction_rate": 0.0, "tool_precision": 0.0},
            "recommendations": ["Collect more telemetry before drawing confidence conclusions."],
        }
    contract = 0.0
    contradiction = 0.0
    tool_precision = 0.0
    for run in telemetry:
        quality = dict(run.get("quality_signals") or {})
        contract += float(quality.get("contract_pass_rate") or 0.0)
        contradiction += float(quality.get("contradiction_miss_rate") or 0.0)
        tool_precision += float(quality.get("tool_call_precision") or 0.0)
    audit = {
        "sample_count": total,
        "contract_pass_rate": round(contract / total, 4),
        "contradiction_rate": round(contradiction / total, 4),
        "tool_precision": round(tool_precision / total, 4),
    }
    recommendations: list[str] = []
    if audit["contract_pass_rate"] < 0.9:
        recommendations.append("Raise contract compliance before expansion.")
    if audit["contradiction_rate"] > 0.1:
        recommendations.append("Run counterexample remediation cycles to lower contradiction miss rate.")
    if audit["tool_precision"] < 0.8:
        recommendations.append("Increase tool schema preflight checks and lane selection discipline.")
    if not recommendations:
        recommendations.append("Calibration metrics are within target bands for continued governed rollout.")
    return {"ok": True, "generated_at": _utcnow(), "calibration": audit, "recommendations": recommendations}


def generate_falsification_oracle(*, domain: str, session: MerlinSession) -> dict[str, Any]:
    sample = str(domain or "").strip().lower() or "general_reasoning"
    domain_map = {
        "film_production": ["osha_violation", "sag_aftra_breach", "budget_overrun_gt_15pct"],
        "journalism": ["source_tier_lt_2", "confidence_lt_0_7", "uncorrected_factual_error"],
        "earth_science": ["sensor_drift_gt_threshold", "auc_lt_0_85", "prediction_horizon_exceeded"],
        "dnd_narrative": ["canon_violation", "mechanical_inconsistency", "player_agency_breach"],
        "general_reasoning": ["hardgate_contradiction", "sycophancy_leak_gt_0_15", "calibration_error_gt_0_2"],
    }
    kill_conditions = domain_map.get(sample, domain_map["general_reasoning"])
    oracle = {
        "ok": True,
        "generated_at": _utcnow(),
        "domain": sample,
        "kill_conditions": kill_conditions,
        "status": "active",
    }
    existing = next(
        (
            item
            for item in reversed(session.compiled_insights)
            if str(item.get("source_query", "")) == f"generate_falsification_oracle:{sample}"
        ),
        None,
    )
    if existing is None:
        session.compiled_insights.append(
            {
                "id": f"oracle_{sample}_{len(session.compiled_insights) + 1}",
                "fact": f"Falsification oracle for {sample} defines {len(kill_conditions)} kill conditions.",
                "status": "[TRUSTED_COMPILED]",
                "source_query": f"generate_falsification_oracle:{sample}",
                "ingested_at": _utcnow(),
            }
        )
    else:
        existing["fact"] = f"Falsification oracle for {sample} defines {len(kill_conditions)} kill conditions."
        existing["status"] = "[TRUSTED_COMPILED]"
        existing["ingested_at"] = _utcnow()
    return oracle


def analyze_depth(*, session: MerlinSession, limit: int = 25) -> dict[str, Any]:
    cap = max(1, min(int(limit or 25), 100))
    runs = list(session.telemetry)[-cap:]
    if not runs:
        return {
            "ok": True,
            "generated_at": _utcnow(),
            "recommended_depth": 2,
            "reason": "No telemetry samples available; use conservative default.",
        }
    avg_tools = sum(int(run.get("tool_rounds") or 0) for run in runs) / len(runs)
    avg_latency = sum(float(run.get("latency_ms") or 0.0) for run in runs) / len(runs)
    avg_contradiction = (
        sum(float((run.get("quality_signals") or {}).get("contradiction_miss_rate") or 0.0) for run in runs) / len(runs)
    )
    recommended = 2
    if avg_tools >= 3 or avg_contradiction > 0.1:
        recommended = 4
    if avg_tools >= 4 and avg_latency < 4000:
        recommended = 5
    return {
        "ok": True,
        "generated_at": _utcnow(),
        "recommended_depth": recommended,
        "telemetry_window": len(runs),
        "metrics": {
            "average_tool_rounds": round(avg_tools, 3),
            "average_latency_ms": round(avg_latency, 3),
            "average_contradiction_miss_rate": round(avg_contradiction, 4),
        },
        "note": "Recommendation is deterministic from telemetry window metrics.",
    }
