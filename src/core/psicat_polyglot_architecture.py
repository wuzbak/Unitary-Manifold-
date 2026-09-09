# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""PsiCat polyglot execution-role blueprint with fallback-aware readiness."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Tuple

from .polyglot_dependency_health import polyglot_stack_health_report
from .polyglot_execution_matrix import polyglot_lane_matrix


@dataclass(frozen=True)
class PsiCatRoleLane:
    role: str
    primary_stack: Tuple[str, ...]
    fallback_chain: Tuple[str, ...]
    available_now: bool
    status: str


def _lang_ok(health: Dict[str, object], key: str) -> bool:
    return bool(
        health.get("languages", {}).get(key, {}).get("available", False)
    )


def _bin_ok(section: Dict[str, object], key: str) -> bool:
    return bool(section.get(key, {}).get("available", False))


def psicat_polyglot_blueprint() -> Dict[str, object]:
    """Return operational role mapping for PsiCat with graceful fallback chains."""
    health = polyglot_stack_health_report()
    lanes = polyglot_lane_matrix()

    execution_compute = health.get("execution_compute", {})
    verification_logic = health.get("verification_logic", {})
    docs_pipelines = health.get("docs_pipelines", {})

    role_map = {
        "high_performance_compute_core": PsiCatRoleLane(
            role="4D→5D→4D tensors, Christoffel/Ricci, PDE integrators",
            primary_stack=("julia", "mojo", "c++/cuda"),
            fallback_chain=("julia_cpu", "python_reference"),
            available_now=bool(lanes["julia_acceleration"]["available"]),
            status=str(lanes["julia_acceleration"]["status"]),
        ),
        "orchestration_interface_layer": PsiCatRoleLane(
            role="API compatibility and workflow dispatch",
            primary_stack=("python",),
            fallback_chain=("python",),
            available_now=_lang_ok(health, "python"),
            status="ACTIVE",
        ),
        "formal_analytic_verification": PsiCatRoleLane(
            role="Lean4/Wolfram/SymPy/Z3 proof + symbolic checks",
            primary_stack=("lean4", "wolfram", "sympy", "z3"),
            fallback_chain=("sympy", "z3"),
            available_now=bool(
                _bin_ok(verification_logic, "lean4")
                or bool(verification_logic.get("z3", {}).get("available", False))
            ),
            status="ACTIVE_WITH_FALLBACK",
        ),
        "safety_monitoring_runtime_guards": PsiCatRoleLane(
            role="memory-safe sidecar guards and sentinels",
            primary_stack=("rust", "pyo3"),
            fallback_chain=("python_threaded_guards",),
            available_now=_lang_ok(health, "rust"),
            status="STAGED",
        ),
        "frontend_visualization": PsiCatRoleLane(
            role="typed dashboard + shader rendering + web delivery",
            primary_stack=("typescript", "wgsl/glsl", "wasm"),
            fallback_chain=("typescript_canvas_fallback",),
            available_now=bool(
                _lang_ok(health, "typescript")
                and _bin_ok(execution_compute, "wasm_runtime")
            ),
            status="ACTIVE_PARTIAL",
        ),
        "data_storage_relational_auditing": PsiCatRoleLane(
            role="parameter ledgers, scan outputs, binary array persistence",
            primary_stack=("duckdb", "polars", "arrow", "zarr", "parquet"),
            fallback_chain=("duckdb", "pyarrow"),
            available_now=bool(
                health.get("data_storage", {}).get("duckdb", {}).get("available", False)
                and health.get("data_storage", {}).get("pyarrow", {}).get("available", False)
            ),
            status="ACTIVE_OPTIONAL",
        ),
    }

    return {
        "psicat_role_map": {k: asdict(v) for k, v in role_map.items()},
        "graceful_degradation_policy": {
            "compute": "julia_cuda -> julia_cpu -> python_reference",
            "verification": "lean4/wolfram -> sympy/z3",
            "visualization": "wasm+shaders -> typed dashboard fallback",
            "docs_pipeline": "quarto -> markdown/plaintext",
        },
        "bootstrap_ready": bool(
            _bin_ok(execution_compute, "wasm_runtime")
            and _bin_ok(docs_pipelines, "quarto")
        ),
    }

