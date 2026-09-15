# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Kernel runtime surfaces for governed compiled-kernel migration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.core.kernel_runtime import (
    build_kernel_benchmark_receipt,
    build_kernel_parity_receipt,
    detect_backend_capability,
    kernel_contract_schema,
    run_epistemic_compactification_sanity,
)
from src.core.adjacent_topology_prototypes import topology_adjacent_summary

REPO_ROOT = Path(__file__).resolve().parents[4]


def _kernel_escalation_profile(gate_verdict: str, severity: str, health_score: float) -> dict[str, Any]:
    if gate_verdict == "fail_closed":
        return {
            "tier": "T3_BLOCK",
            "lane_routing_hint": "validation_resilience",
            "priority": "highest",
            "requires_human_review": True,
        }
    if gate_verdict == "hold" or severity == "medium" or health_score < 1.0:
        return {
            "tier": "T2_HOLD",
            "lane_routing_hint": "benchmark_operations",
            "priority": "high",
            "requires_human_review": False,
        }
    return {
        "tier": "T1_MONITOR",
        "lane_routing_hint": "physics_compute",
        "priority": "high",
        "requires_human_review": False,
    }


def get_kernel_runtime_board() -> dict[str, Any]:
    capability = detect_backend_capability()
    contract = kernel_contract_schema()
    return {
        "board_id": "psicat_kernel_runtime_board_v1",
        "ok": True,
        "capability": capability,
        "kernel_contracts": contract,
        "policy": {
            "preferred_lane_order": ["triton_compiled", "jax_xla", "numpy_cpu"],
            "hard_bypass_forbidden": True,
            "governed_local_execution_required": True,
            "backend_detection_note": "Backend identity is explicit; CUDA-visible ROCm environments are treated separately.",
        },
    }


def get_kernel_execution_receipts(points: int = 8, seed: int = 7) -> dict[str, Any]:
    receipt = build_kernel_parity_receipt(points=points, seed=seed)
    return {
        "ok": bool(receipt.get("ok")),
        "receipt": receipt,
        "governance": {
            "fail_closed": bool((receipt.get("gate") or {}).get("fail_closed", True)),
            "unchecked_or_unlogged_execution_forbidden": True,
        },
    }


def get_compactification_sanity_receipt() -> dict[str, Any]:
    return run_epistemic_compactification_sanity(
        mas_tracker_path=REPO_ROOT / "docs" / "mas_tracker.yml",
        fallibility_path=REPO_ROOT / "FALLIBILITY.md",
    )


def get_kernel_benchmark_receipts(points: int = 128, seed: int = 11, repeats: int = 5) -> dict[str, Any]:
    receipt = build_kernel_benchmark_receipt(points=points, seed=seed, repeats=repeats)
    return {
        "ok": bool(receipt.get("ok")),
        "receipt": receipt,
        "governance": {
            "fail_closed": False,
            "performance_claim_note": "Benchmark speedup claims require matching parity receipts.",
        },
    }


def get_kernel_promotion_gate_summary(points: int = 32, seed: int = 13, repeats: int = 3) -> dict[str, Any]:
    parity_payload = get_kernel_execution_receipts(points=points, seed=seed)
    benchmark_payload = get_kernel_benchmark_receipts(points=max(points, 32), seed=seed, repeats=repeats)
    compactification = get_compactification_sanity_receipt()

    parity_receipt = dict(parity_payload.get("receipt") or {})
    benchmark_receipt = dict(benchmark_payload.get("receipt") or {})
    benchmarks = dict(benchmark_receipt.get("benchmarks") or {})
    hotspot_outer = dict(benchmarks.get("outer_bb_hotspot") or {})
    hotspot_metric = dict(benchmarks.get("kk_4x4_metric_block_hotspot") or {})
    lane_outer = dict(hotspot_outer.get("lane") or {})
    lane_metric = dict(hotspot_metric.get("lane") or {})
    benchmark_error_outer = float(hotspot_outer.get("max_abs_error_vs_reference", 1.0))
    benchmark_error_metric = float(hotspot_metric.get("max_abs_error_vs_reference", 1.0))
    benchmark_error_tolerance = 1e-6

    checks = [
        {
            "id": "parity_gate",
            "pass": bool((parity_receipt.get("gate") or {}).get("parity_pass")),
            "reason": "Kernel parity against canonical NumPy reference must pass.",
        },
        {
            "id": "benchmark_outer_error_gate",
            "pass": benchmark_error_outer <= benchmark_error_tolerance,
            "reason": "Outer-product benchmark lane output must stay within bounded error tolerance.",
            "max_abs_error": benchmark_error_outer,
            "required_tolerance": benchmark_error_tolerance,
        },
        {
            "id": "benchmark_metric_block_error_gate",
            "pass": benchmark_error_metric <= benchmark_error_tolerance,
            "reason": "KK 4x4 metric-block benchmark lane output must stay within bounded error tolerance.",
            "max_abs_error": benchmark_error_metric,
            "required_tolerance": benchmark_error_tolerance,
        },
        {
            "id": "compactification_sanity_gate",
            "pass": bool(compactification.get("ok")),
            "reason": "Compactification sanity checks must remain green against canonical epistemic files.",
        },
    ]
    remediation_map = {
        "parity_gate": "Re-run parity receipts and inspect canonical-vs-compiled lane drift before any promotion claim.",
        "benchmark_outer_error_gate": "Tighten or disable outer-product compiled lane until benchmark error returns within tolerance.",
        "benchmark_metric_block_error_gate": "Tighten or disable KK metric-block compiled lane until benchmark error returns within tolerance.",
        "compactification_sanity_gate": "Restore compactification sanity invariants in canonical epistemic files before proceeding.",
    }
    required_pass = all(bool(item.get("pass")) for item in checks)
    compiled_lane_active = bool(lane_outer.get("ok") or lane_metric.get("ok"))
    failed_checks = [str(item.get("id") or "") for item in checks if not bool(item.get("pass"))]
    remediation_actions = [remediation_map[item] for item in failed_checks if item in remediation_map]
    passed_count = len(checks) - len(failed_checks)
    health_score = float(passed_count / len(checks)) if checks else 0.0
    if not required_pass:
        gate_verdict = "fail_closed"
        reason = "required_kernel_checks_failed"
        severity = "high"
    elif compiled_lane_active:
        gate_verdict = "pass"
        reason = "all_kernel_cross_lane_checks_passed"
        severity = "low"
    else:
        gate_verdict = "hold"
        reason = "compiled_lane_unavailable_hold"
        severity = "medium"
    escalation = _kernel_escalation_profile(
        gate_verdict=gate_verdict,
        severity=severity,
        health_score=health_score,
    )

    return {
        "ok": gate_verdict != "fail_closed",
        "gate_verdict": gate_verdict,
        "reason": reason,
        "failed_checks": failed_checks,
        "remediation_actions": remediation_actions,
        "health_score": health_score,
        "severity": severity,
        "escalation_tier": str(escalation.get("tier") or ""),
        "lane_routing_hint": str(escalation.get("lane_routing_hint") or ""),
        "escalation_priority": str(escalation.get("priority") or ""),
        "requires_human_review": bool(escalation.get("requires_human_review", False)),
        "blocking_pass": gate_verdict != "fail_closed",
        "promotion_blocking": gate_verdict == "fail_closed",
        "policy": "Fail closed on parity/sanity/error failures; hold when compiled lane evidence is absent.",
        "compiled_lane_active": compiled_lane_active,
        "checks": checks,
        "artifacts": {
            "parity": parity_payload,
            "benchmark": benchmark_payload,
            "compactification_sanity": compactification,
        },
    }


def get_kernel_risk_summary(points: int = 32, seed: int = 13, repeats: int = 3) -> dict[str, Any]:
    gate = get_kernel_promotion_gate_summary(points=points, seed=seed, repeats=repeats)
    return {
        "ok": bool(gate.get("ok", False)),
        "risk_id": "psicat_kernel_risk_summary_v1",
        "gate_verdict": str(gate.get("gate_verdict") or ""),
        "severity": str(gate.get("severity") or ""),
        "escalation_tier": str(gate.get("escalation_tier") or ""),
        "lane_routing_hint": str(gate.get("lane_routing_hint") or ""),
        "escalation_priority": str(gate.get("escalation_priority") or ""),
        "requires_human_review": bool(gate.get("requires_human_review", False)),
        "health_score": float(gate.get("health_score", 0.0) or 0.0),
        "failed_checks": list(gate.get("failed_checks") or []),
        "remediation_actions": list(gate.get("remediation_actions") or []),
        "blocking_pass": bool(gate.get("blocking_pass", False)),
        "promotion_blocking": bool(gate.get("promotion_blocking", False)),
        "source_surface": "getKernelPromotionGateSummary",
    }


def get_kernel_escalation_packet(points: int = 32, seed: int = 13, repeats: int = 3) -> dict[str, Any]:
    risk = get_kernel_risk_summary(points=points, seed=seed, repeats=repeats)
    lane = str(risk.get("lane_routing_hint") or "")
    tier = str(risk.get("escalation_tier") or "")
    lane_actions = {
        "validation_resilience": [
            "Freeze compiled-lane promotion claims.",
            "Route remediation actions through validation resilience board.",
            "Require human review sign-off before re-running promotion gate.",
        ],
        "benchmark_operations": [
            "Run benchmark receipt refresh with bounded repeats.",
            "Re-check parity and metric-block error tolerances.",
            "Keep promotion state at hold until compiled evidence is green.",
        ],
        "physics_compute": [
            "Monitor compiled lane receipts on regular cadence.",
            "Keep parity receipts attached to all speedup claims.",
        ],
    }
    return {
        "ok": bool(risk.get("ok", False)),
        "packet_id": "psicat_kernel_escalation_packet_v1",
        "risk_surface": "getMerlinKernelRiskSummary",
        "gate_verdict": str(risk.get("gate_verdict") or ""),
        "severity": str(risk.get("severity") or ""),
        "escalation_tier": tier,
        "lane_routing_hint": lane,
        "escalation_priority": str(risk.get("escalation_priority") or ""),
        "requires_human_review": bool(risk.get("requires_human_review", False)),
        "health_score": float(risk.get("health_score", 0.0) or 0.0),
        "failed_checks": list(risk.get("failed_checks") or []),
        "remediation_actions": list(risk.get("remediation_actions") or []),
        "lane_actions": list(lane_actions.get(lane, [])),
        "policy": {
            "tier_order": ["T1_MONITOR", "T2_HOLD", "T3_BLOCK"],
            "promotion_claims_require_kernel_gate_pass": True,
            "human_review_required_when_t3": tier == "T3_BLOCK",
        },
    }


def get_topology_adjacent_board() -> dict[str, Any]:
    summary = topology_adjacent_summary()
    return {
        "ok": True,
        "board_id": "psicat_topology_adjacent_board_v1",
        "summary": summary,
        "policy": {
            "claim_scope": "adjacent_track_only",
            "hardgate_promotion_requires_independent_evidence": True,
        },
    }
