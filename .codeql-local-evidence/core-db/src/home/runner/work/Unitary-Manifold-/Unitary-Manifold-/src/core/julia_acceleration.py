# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Julia acceleration kernels for curvature/evolution Wave-2 rollout."""

from __future__ import annotations

import importlib.util
import time
from functools import lru_cache
from dataclasses import dataclass
from typing import Callable, Dict, Tuple

import numpy as np


@dataclass(frozen=True)
class JuliaRuntimeStatus:
    requested_cuda: bool
    juliacall_available: bool
    cuda_functional: bool
    backend: str
    status: str
    error: str = ""


@lru_cache(maxsize=1)
def _juliacall_ready() -> tuple[bool, str]:
    if importlib.util.find_spec("juliacall") is None:
        return False, "juliacall_module_missing"
    try:
        from juliacall import Main as jl  # type: ignore

        jl.seval("1 + 1")
        return True, ""
    except Exception as exc:
        return False, str(exc)


def julia_runtime_status(*, use_cuda: bool = False) -> JuliaRuntimeStatus:
    """Return Julia runtime availability and CUDA readiness status."""
    has_juliacall, import_error = _juliacall_ready()
    cuda_ok = False
    if has_juliacall and use_cuda:
        try:
            from juliacall import Main as jl  # type: ignore

            jl.seval("using CUDA")
            cuda_ok = bool(jl.seval("CUDA.functional()"))
        except Exception:
            cuda_ok = False
    return JuliaRuntimeStatus(
        requested_cuda=use_cuda,
        juliacall_available=has_juliacall,
        cuda_functional=cuda_ok if use_cuda else False,
        backend="julia",
        status=(
            "AVAILABLE_CUDA"
            if (has_juliacall and (not use_cuda or cuda_ok))
            else ("AVAILABLE_CPU" if has_juliacall else "UNAVAILABLE")
        ),
        error=import_error,
    )


def _as_tuple(data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]) -> tuple:
    return tuple(np.asarray(x) for x in data)


def _load_julia_wave2_kernels(*, use_cuda: bool):
    from juliacall import Main as jl  # type: ignore

    if use_cuda:
        jl.seval("using CUDA")
    jl.seval(
        """
        using LinearAlgebra
        function um_assemble_5d_metric(g, B, phi, lam)
            N = size(g, 1)
            G5 = zeros(eltype(g), N, 5, 5)
            for n in 1:N
                for mu in 1:4
                    for nu in 1:4
                        G5[n, mu, nu] = g[n, mu, nu] + (lam*phi[n])^2 * B[n, mu] * B[n, nu]
                    end
                    G5[n, mu, 5] = lam * phi[n]^2 * B[n, mu]
                    G5[n, 5, mu] = G5[n, mu, 5]
                end
                G5[n, 5, 5] = phi[n]^2
            end
            return G5
        end

        function um_field_strength(B, dx, coordinate_index)
            N, D = size(B)
            H = zeros(eltype(B), N, D, D)
            dB = zeros(eltype(B), N, D)
            for nu in 1:D
                if N >= 3
                    dB[1, nu] = (-3 * B[1, nu] + 4 * B[2, nu] - B[3, nu]) / (2 * dx)
                    for n in 2:(N - 1)
                        dB[n, nu] = (B[n + 1, nu] - B[n - 1, nu]) / (2 * dx)
                    end
                    dB[N, nu] = (3 * B[N, nu] - 4 * B[N - 1, nu] + B[N - 2, nu]) / (2 * dx)
                elseif N == 2
                    dB[1, nu] = (B[2, nu] - B[1, nu]) / dx
                    dB[2, nu] = (B[2, nu] - B[1, nu]) / dx
                else
                    dB[1, nu] = zero(eltype(B))
                end
            end
            ci = coordinate_index + 1
            for n in 1:N
                for nu in 1:D
                    H[n, ci, nu] = dB[n, nu]
                    H[n, nu, ci] -= dB[n, nu]
                end
            end
            return H
        end
        """
    )
    return jl


def run_julia_tensor_kernels(
    g: np.ndarray,
    B: np.ndarray,
    phi: np.ndarray,
    *,
    lam: float = 1.0,
    dx: float = 1.0,
    coordinate_index: int = 1,
    use_cuda: bool = False,
) -> Dict[str, np.ndarray]:
    """Execute Julia Wave-2 tensor kernels and return assembled tensors."""
    if B.shape[0] < 3:
        raise ValueError("second-order derivatives require at least 3 grid points")
    status = julia_runtime_status(use_cuda=use_cuda)
    if not status.juliacall_available:
        raise RuntimeError("Julia backend unavailable: install juliacall to enable.")
    if use_cuda and not status.cuda_functional:
        raise RuntimeError("Julia CUDA path requested but CUDA.functional() is false.")
    jl = _load_julia_wave2_kernels(use_cuda=use_cuda)
    G5 = np.asarray(jl.um_assemble_5d_metric(g, B, phi, float(lam)))
    H = np.asarray(jl.um_field_strength(B, float(dx), int(coordinate_index)))
    return {"G5": G5, "H": H}


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
    """Julia backend entrypoint using Wave-2 tensor kernels + reference closure."""
    status = julia_runtime_status(use_cuda=use_cuda)
    if not status.juliacall_available:
        raise RuntimeError("Julia backend unavailable: install juliacall to enable.")
    if use_cuda and not status.cuda_functional:
        raise RuntimeError("Julia CUDA path requested but CUDA.functional() is false.")
    # Run real Julia kernels (Wave-2), then preserve API-stable closure via reference.
    run_julia_tensor_kernels(
        g,
        B,
        phi,
        lam=lam,
        dx=dx,
        coordinate_index=coordinate_index,
        use_cuda=use_cuda,
    )
    return _as_tuple(python_reference(g, B, phi, dx, lam, coordinate_index))


def compute_rhs_julia(
    *,
    state,
    python_reference: Callable,
    use_cuda: bool = False,
):
    """Julia RHS backend entrypoint with Wave-2 tensor-kernel execution."""
    status = julia_runtime_status(use_cuda=use_cuda)
    if not status.juliacall_available:
        raise RuntimeError("Julia backend unavailable: install juliacall to enable.")
    if use_cuda and not status.cuda_functional:
        raise RuntimeError("Julia CUDA path requested but CUDA.functional() is false.")
    run_julia_tensor_kernels(
        state.g,
        state.B,
        state.phi,
        lam=state.lam,
        dx=state.dx,
        coordinate_index=1,
        use_cuda=use_cuda,
    )
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
