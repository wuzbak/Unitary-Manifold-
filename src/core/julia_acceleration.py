# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Julia acceleration scaffold for curvature and evolution RHS lanes."""

from __future__ import annotations

import importlib.util
import time
from dataclasses import dataclass
from typing import Callable, Dict, Tuple

import numpy as np


@dataclass(frozen=True)
class JuliaRuntimeStatus:
    requested_cuda: bool
    juliacall_available: bool
    backend: str
    status: str


def julia_runtime_status(*, use_cuda: bool = False) -> JuliaRuntimeStatus:
    """Return Julia runtime availability status for staged dispatch."""
    has_juliacall = importlib.util.find_spec("juliacall") is not None
    return JuliaRuntimeStatus(
        requested_cuda=use_cuda,
        juliacall_available=has_juliacall,
        backend="julia",
        status="AVAILABLE" if has_juliacall else "UNAVAILABLE",
    )


def _as_tuple(data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]) -> tuple:
    return tuple(np.asarray(x) for x in data)


def compute_curvature_julia(
    g: np.ndarray,
    B: np.ndarray,
    phi: np.ndarray,
    dx: float,
    lam: float,
    coordinate_index: int,
    *,
    python_reference: Callable[..., Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    use_cuda: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Julia backend entrypoint (staged scaffold, parity-anchored to reference)."""
    status = julia_runtime_status(use_cuda=use_cuda)
    if not status.juliacall_available:
        raise RuntimeError("Julia backend unavailable: install juliacall to enable.")
    # Wave-1 scaffold: deterministic parity path anchored to Python reference.
    return _as_tuple(python_reference(g, B, phi, dx, lam, coordinate_index))


def compute_rhs_julia(
    *,
    state,
    python_reference: Callable,
    use_cuda: bool = False,
):
    """Julia RHS backend entrypoint (staged scaffold, parity-anchored)."""
    status = julia_runtime_status(use_cuda=use_cuda)
    if not status.juliacall_available:
        raise RuntimeError("Julia backend unavailable: install juliacall to enable.")
    return tuple(np.asarray(x) for x in python_reference(state))


def parity_report(
    python_payload: tuple,
    accelerated_payload: tuple,
    *,
    rtol: float = 1e-7,
    atol: float = 1e-10,
) -> Dict[str, object]:
    """Return parity verdict for backend payloads."""
    max_abs_err = 0.0
    for a, b in zip(python_payload, accelerated_payload):
        max_abs_err = max(max_abs_err, float(np.max(np.abs(np.asarray(a) - np.asarray(b)))))
    passed = all(
        np.allclose(np.asarray(a), np.asarray(b), rtol=rtol, atol=atol)
        for a, b in zip(python_payload, accelerated_payload)
    )
    return {
        "parity_passed": bool(passed),
        "rtol": float(rtol),
        "atol": float(atol),
        "max_abs_error": float(max_abs_err),
    }


def benchmark_callable(fn: Callable, *args, repeats: int = 3, **kwargs) -> Dict[str, float]:
    """Measure wall-clock runtime for a callable and return basic summary stats."""
    samples = []
    for _ in range(max(int(repeats), 1)):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        samples.append(time.perf_counter() - t0)
    samples_arr = np.asarray(samples, dtype=float)
    return {
        "min_seconds": float(samples_arr.min()),
        "mean_seconds": float(samples_arr.mean()),
        "max_seconds": float(samples_arr.max()),
    }

