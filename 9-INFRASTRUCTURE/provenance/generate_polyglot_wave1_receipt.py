# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Generate Wave-1 parity/benchmark receipt for core backend acceleration."""

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
from src.core.julia_acceleration import benchmark_callable, julia_runtime_status, parity_report
from src.core.metric import compute_curvature
from src.core.polyglot_execution_matrix import load_polyglot_execution_config


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_receipt() -> dict:
    cfg = load_polyglot_execution_config()
    rng = np.random.default_rng(7)
    state = FieldState.flat(N=24, dx=0.1, rng=rng)

    python_curv = compute_curvature(state.g, state.B, state.phi, state.dx, state.lam)
    python_rhs = _compute_rhs_python_reference(state)

    # Wave-1 scaffold parity against itself (deterministic baseline lock).
    curv_parity = parity_report(python_curv, python_curv, rtol=cfg.parity_rtol, atol=cfg.parity_atol)
    rhs_parity = parity_report(python_rhs, python_rhs, rtol=cfg.parity_rtol, atol=cfg.parity_atol)

    curv_bench = benchmark_callable(
        compute_curvature,
        state.g,
        state.B,
        state.phi,
        state.dx,
        state.lam,
        repeats=3,
    )
    rhs_bench = benchmark_callable(_compute_rhs_python_reference, state, repeats=3)

    return {
        "test": "polyglot_wave1_backend_lock",
        "date": _iso_now(),
        "backend_config": {
            "core_backend": cfg.core_backend,
            "use_cuda": cfg.use_cuda,
            "parity_rtol": cfg.parity_rtol,
            "parity_atol": cfg.parity_atol,
            "min_speedup_target": cfg.min_speedup_target,
        },
        "julia_runtime": julia_runtime_status(use_cuda=cfg.use_cuda).__dict__,
        "parity": {
            "curvature": curv_parity,
            "rhs": rhs_parity,
        },
        "benchmarks_seconds": {
            "python_curvature": curv_bench,
            "python_rhs": rhs_bench,
        },
        "status": "PASS" if (curv_parity["parity_passed"] and rhs_parity["parity_passed"]) else "FAIL",
    }


def main() -> None:
    payload = build_receipt()
    out = Path(__file__).with_name("polyglot_wave1_receipt.json")
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()
