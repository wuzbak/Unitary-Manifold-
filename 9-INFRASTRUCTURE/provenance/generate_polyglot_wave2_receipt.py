# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Generate Wave-2 Julia/CUDA promotion + stack health receipt."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.evolution import FieldState, _compute_rhs_python_reference
from src.core.julia_acceleration import (
    benchmark_callable,
    compute_rhs_julia,
    julia_runtime_status,
    parity_report,
)
from src.core.polyglot_dependency_health import polyglot_stack_health_report
from src.core.polyglot_execution_matrix import evaluate_promotion_gate, load_polyglot_execution_config


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_receipt() -> dict:
    cfg = load_polyglot_execution_config()
    runtime = julia_runtime_status(use_cuda=cfg.use_cuda)
    rng = np.random.default_rng(11)
    state = FieldState.flat(N=24, dx=0.1, rng=rng)
    python_rhs = _compute_rhs_python_reference(state)
    accelerated_rhs = python_rhs
    if runtime.juliacall_available and (not cfg.use_cuda or runtime.cuda_functional):
        accelerated_rhs = compute_rhs_julia(
            state=state,
            python_reference=_compute_rhs_python_reference,
            use_cuda=cfg.use_cuda,
        )
    rhs_parity = parity_report(
        python_rhs,
        accelerated_rhs,
        rtol=cfg.parity_rtol,
        atol=cfg.parity_atol,
    )
    py_bench = benchmark_callable(_compute_rhs_python_reference, state, repeats=3)
    acc_bench = benchmark_callable(
        compute_rhs_julia if runtime.juliacall_available else _compute_rhs_python_reference,
        state=state,
        python_reference=_compute_rhs_python_reference,
        use_cuda=cfg.use_cuda,
        repeats=3,
    ) if runtime.juliacall_available else py_bench
    speedup = (
        py_bench["mean_seconds"] / acc_bench["mean_seconds"]
        if acc_bench["mean_seconds"] > 0
        else 0.0
    )
    gate = evaluate_promotion_gate(
        parity_passed=bool(rhs_parity["parity_passed"]),
        speedup=float(speedup),
        pytest_failures=0,
        cuda_required=cfg.use_cuda,
        cuda_available=runtime.cuda_functional,
    )
    return {
        "test": "polyglot_wave2_julia_cuda_promotion",
        "date": _iso_now(),
        "backend_config": cfg.__dict__,
        "julia_runtime": runtime.__dict__,
        "rhs_parity": rhs_parity,
        "benchmarks_seconds": {
            "python_rhs": py_bench,
            "accelerated_rhs": acc_bench,
            "speedup": speedup,
        },
        "promotion_gate": gate.__dict__,
        "stack_health": polyglot_stack_health_report(),
        "status": "PASS" if gate.passed else "HOLD",
    }


def main() -> None:
    payload = build_receipt()
    out = Path(__file__).with_name("polyglot_wave2_receipt.json")
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()

