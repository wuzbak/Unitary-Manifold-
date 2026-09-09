# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Polyglot execution matrix and rollout gates for accelerated UM lanes."""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from typing import Dict


PARITY_RTOL_DEFAULT: float = 1e-7
PARITY_ATOL_DEFAULT: float = 1e-10
MIN_SPEEDUP_TARGET_DEFAULT: float = 1.10


@dataclass(frozen=True)
class PolyglotExecutionConfig:
    """Runtime config for staged backend promotion and no-regression gates."""

    core_backend: str = "python"
    use_cuda: bool = False
    parity_rtol: float = PARITY_RTOL_DEFAULT
    parity_atol: float = PARITY_ATOL_DEFAULT
    min_speedup_target: float = MIN_SPEEDUP_TARGET_DEFAULT
    require_zero_failures: bool = True


@dataclass(frozen=True)
class PromotionGateResult:
    passed: bool
    reasons: tuple[str, ...]
    speedup: float
    parity_passed: bool
    pytest_failures: int
    cuda_required: bool
    cuda_available: bool


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def load_polyglot_execution_config() -> PolyglotExecutionConfig:
    """Load polyglot execution settings from environment variables."""
    backend = os.getenv("UM_CORE_BACKEND", "python").strip().lower()
    if backend not in {"python", "julia"}:
        backend = "python"
    return PolyglotExecutionConfig(
        core_backend=backend,
        use_cuda=_truthy_env("UM_JULIA_USE_CUDA"),
        parity_rtol=float(os.getenv("UM_PARITY_RTOL", PARITY_RTOL_DEFAULT)),
        parity_atol=float(os.getenv("UM_PARITY_ATOL", PARITY_ATOL_DEFAULT)),
        min_speedup_target=float(
            os.getenv("UM_MIN_SPEEDUP_TARGET", MIN_SPEEDUP_TARGET_DEFAULT)
        ),
        require_zero_failures=not _truthy_env("UM_ALLOW_TEST_FAILURES"),
    )


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def polyglot_lane_matrix() -> Dict[str, Dict[str, object]]:
    """Return machine-readable readiness for each polyglot lane."""
    cfg = load_polyglot_execution_config()
    from .julia_acceleration import julia_runtime_status

    jl = julia_runtime_status(use_cuda=cfg.use_cuda)
    return {
        "julia_acceleration": {
            "stage": "ACTIVE_WAVE2",
            "default_backend": cfg.core_backend,
            "available": jl.juliacall_available,
            "status": jl.status,
        },
        "julia_cuda_scaling": {
            "stage": "ACTIVE_GATED",
            "requested": cfg.use_cuda,
            "available": jl.cuda_functional if cfg.use_cuda else jl.juliacall_available,
        },
        "lean4_formal_lane": {
            "stage": "ACTIVE",
            "available": os.path.isdir("lean4"),
        },
        "symbolic_validation_lane": {
            "stage": "ACTIVE_WITH_FALLBACK",
            "sympy_available": _module_available("sympy"),
            "wolfram_client_available": _module_available("wolframclient"),
        },
        "rust_safety_lane": {
            "stage": "STAGED",
            "available": os.path.isdir("12-AZ-IP/02-az-kernel"),
        },
        "typescript_dashboard_lane": {
            "stage": "ACTIVE_PARTIAL",
            "available": os.path.isdir("12-AZ-IP"),
        },
        "shader_visual_lane": {
            "stage": "STAGED",
            "wgsl_available": False,
            "glsl_available": False,
        },
        "duckdb_ledger_lane": {
            "stage": "ACTIVE_OPTIONAL",
            "available": _module_available("duckdb"),
        },
        "mojo_lane": {
            "stage": "EVIDENCE_REQUIRED",
            "available": False,
        },
        "cpp_cuda_lane": {
            "stage": "EVIDENCE_REQUIRED",
            "available": False,
        },
    }


def no_regression_gate(pytest_failures: int) -> bool:
    """Return True if no-regression gate passes under configured policy."""
    cfg = load_polyglot_execution_config()
    if not cfg.require_zero_failures:
        return pytest_failures >= 0
    return pytest_failures == 0


def evaluate_promotion_gate(
    *,
    parity_passed: bool,
    speedup: float,
    pytest_failures: int,
    cuda_required: bool,
    cuda_available: bool,
) -> PromotionGateResult:
    """Evaluate deterministic backend-promotion gates for Wave-2 rollout."""
    cfg = load_polyglot_execution_config()
    reasons: list[str] = []
    if not parity_passed:
        reasons.append("parity_failed")
    if speedup < cfg.min_speedup_target:
        reasons.append("speedup_below_target")
    if not no_regression_gate(pytest_failures):
        reasons.append("regression_gate_failed")
    if cuda_required and not cuda_available:
        reasons.append("cuda_unavailable")
    return PromotionGateResult(
        passed=len(reasons) == 0,
        reasons=tuple(reasons),
        speedup=float(speedup),
        parity_passed=bool(parity_passed),
        pytest_failures=int(pytest_failures),
        cuda_required=bool(cuda_required),
        cuda_available=bool(cuda_available),
    )
