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
    hotspot = dict((benchmark_receipt.get("benchmarks") or {}).get("outer_bb_hotspot") or {})
    lane = dict(hotspot.get("lane") or {})
    benchmark_error = float(hotspot.get("max_abs_error_vs_reference", 1.0))
    benchmark_error_tolerance = 1e-6

    checks = [
        {
            "id": "parity_gate",
            "pass": bool((parity_receipt.get("gate") or {}).get("parity_pass")),
            "reason": "Kernel parity against canonical NumPy reference must pass.",
        },
        {
            "id": "benchmark_error_gate",
            "pass": benchmark_error <= benchmark_error_tolerance,
            "reason": "Benchmark lane output must stay within bounded error tolerance.",
            "max_abs_error": benchmark_error,
            "required_tolerance": benchmark_error_tolerance,
        },
        {
            "id": "compactification_sanity_gate",
            "pass": bool(compactification.get("ok")),
            "reason": "Compactification sanity checks must remain green against canonical epistemic files.",
        },
    ]
    required_pass = all(bool(item.get("pass")) for item in checks)
    compiled_lane_active = bool(lane.get("ok"))
    if not required_pass:
        gate_verdict = "fail_closed"
    elif compiled_lane_active:
        gate_verdict = "pass"
    else:
        gate_verdict = "hold"

    return {
        "ok": gate_verdict != "fail_closed",
        "gate_verdict": gate_verdict,
        "policy": "Fail closed on parity/sanity/error failures; hold when compiled lane evidence is absent.",
        "compiled_lane_active": compiled_lane_active,
        "checks": checks,
        "artifacts": {
            "parity": parity_payload,
            "benchmark": benchmark_payload,
            "compactification_sanity": compactification,
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
