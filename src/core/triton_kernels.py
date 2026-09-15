# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Optional Triton hotspot kernels with deterministic NumPy fallback."""

from __future__ import annotations

from typing import Any
import importlib.util
import time

import numpy as np


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


TRITON_AVAILABLE = _module_available("triton")
TORCH_AVAILABLE = _module_available("torch")

if TRITON_AVAILABLE:  # pragma: no cover - exercised only when triton is installed.
    import triton  # type: ignore
    import triton.language as tl  # type: ignore

    @triton.jit
    def _outer_bb_kernel(
        b_ptr,
        out_ptr,
        n_elements,
        d_elements,
        stride_bn,
        stride_bd,
        stride_on,
        stride_oi,
        stride_oj,
        BLOCK_N: tl.constexpr,
    ):
        pid_n = tl.program_id(0)
        pid_i = tl.program_id(1)
        pid_j = tl.program_id(2)

        offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
        mask_n = offs_n < n_elements
        in_bounds = (pid_i < d_elements) & (pid_j < d_elements)

        b_i = tl.load(
            b_ptr + offs_n * stride_bn + pid_i * stride_bd,
            mask=mask_n & in_bounds,
            other=0.0,
        )
        b_j = tl.load(
            b_ptr + offs_n * stride_bn + pid_j * stride_bd,
            mask=mask_n & in_bounds,
            other=0.0,
        )
        product = b_i * b_j
        tl.store(
            out_ptr + offs_n * stride_on + pid_i * stride_oi + pid_j * stride_oj,
            product,
            mask=mask_n & in_bounds,
        )

    @triton.jit
    def _kk_4x4_block_kernel(
        g_ptr,
        b_ptr,
        phi_ptr,
        out_ptr,
        n_elements,
        d_elements,
        lam_squared,
        stride_gn,
        stride_gi,
        stride_gj,
        stride_bn,
        stride_bd,
        stride_pn,
        stride_on,
        stride_oi,
        stride_oj,
        BLOCK_N: tl.constexpr,
    ):
        pid_n = tl.program_id(0)
        pid_i = tl.program_id(1)
        pid_j = tl.program_id(2)

        offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
        mask_n = offs_n < n_elements
        in_bounds = (pid_i < d_elements) & (pid_j < d_elements)

        g_ij = tl.load(
            g_ptr + offs_n * stride_gn + pid_i * stride_gi + pid_j * stride_gj,
            mask=mask_n & in_bounds,
            other=0.0,
        )
        b_i = tl.load(
            b_ptr + offs_n * stride_bn + pid_i * stride_bd,
            mask=mask_n & in_bounds,
            other=0.0,
        )
        b_j = tl.load(
            b_ptr + offs_n * stride_bn + pid_j * stride_bd,
            mask=mask_n & in_bounds,
            other=0.0,
        )
        phi = tl.load(phi_ptr + offs_n * stride_pn, mask=mask_n & in_bounds, other=0.0)
        out_val = g_ij + (lam_squared * phi * phi) * b_i * b_j
        tl.store(
            out_ptr + offs_n * stride_on + pid_i * stride_oi + pid_j * stride_oj,
            out_val,
            mask=mask_n & in_bounds,
        )


def outer_bb_reference(B: np.ndarray) -> np.ndarray:
    """Reference hotspot contraction: (N,4) -> (N,4,4) via outer product."""
    return np.einsum("ni,nj->nij", B, B)


def kk_4x4_block_reference(g: np.ndarray, B: np.ndarray, phi: np.ndarray, lam: float = 1.0) -> np.ndarray:
    """Reference KK 4x4 block contraction: g + λ²φ²(B⊗B)."""
    g = np.asarray(g, dtype=np.float64)
    B = np.asarray(B, dtype=np.float64)
    phi = np.asarray(phi, dtype=np.float64)
    if g.ndim != 3 or g.shape[1:] != (4, 4):
        raise ValueError("g must have shape (N, 4, 4)")
    if B.ndim != 2 or B.shape[1] != 4:
        raise ValueError("B must have shape (N, 4)")
    if phi.ndim != 1:
        raise ValueError("phi must have shape (N,)")
    if not (g.shape[0] == B.shape[0] == phi.shape[0]):
        raise ValueError("g, B, and phi must have matching N dimension")
    return g + ((lam * phi) ** 2)[:, None, None] * np.einsum("ni,nj->nij", B, B)


def triton_outer_bb(B: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    """Execute Triton outer-product hotspot lane when available, else fallback."""
    B = np.asarray(B, dtype=np.float64)
    if B.ndim != 2:
        raise ValueError("B must have shape (N, D)")
    if B.shape[0] < 1:
        raise ValueError("B must have at least one row")

    fallback = outer_bb_reference(B)
    if not (TRITON_AVAILABLE and TORCH_AVAILABLE):
        return fallback, {
            "ok": False,
            "backend": "numpy_fallback",
            "reason": "triton_or_torch_unavailable",
        }
    try:
        import torch  # type: ignore

        if not torch.cuda.is_available():
            return fallback, {
                "ok": False,
                "backend": "numpy_fallback",
                "reason": "cuda_not_visible_for_triton_lane",
            }
        device = torch.device("cuda")
        b_t = torch.tensor(B, dtype=torch.float32, device=device)
        n, d = b_t.shape
        out = torch.empty((n, d, d), dtype=torch.float32, device=device)
        block_n = 64
        grid = (triton.cdiv(n, block_n), d, d)
        _outer_bb_kernel[grid](
            b_t,
            out,
            n,
            d,
            b_t.stride(0),
            b_t.stride(1),
            out.stride(0),
            out.stride(1),
            out.stride(2),
            BLOCK_N=block_n,
        )
        out = out.detach().cpu().numpy().astype(np.float64)
        return out, {
            "ok": True,
            "backend": "triton_jit_outer_bb",
            "reason": "triton_kernel_executed",
        }
    except Exception as exc:  # pragma: no cover
        return fallback, {
            "ok": False,
            "backend": "numpy_fallback",
            "reason": f"triton_lane_error:{exc}",
        }


def triton_kk_4x4_block(
    g: np.ndarray,
    B: np.ndarray,
    phi: np.ndarray,
    lam: float = 1.0,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Execute Triton KK 4x4 block contraction lane when available, else fallback."""
    fallback = kk_4x4_block_reference(g, B, phi, lam=lam)
    if not (TRITON_AVAILABLE and TORCH_AVAILABLE):
        return fallback, {
            "ok": False,
            "backend": "numpy_fallback",
            "reason": "triton_or_torch_unavailable",
        }
    try:
        import torch  # type: ignore

        if not torch.cuda.is_available():
            return fallback, {
                "ok": False,
                "backend": "numpy_fallback",
                "reason": "cuda_not_visible_for_triton_lane",
            }
        device = torch.device("cuda")
        g_t = torch.tensor(np.asarray(g, dtype=np.float64), dtype=torch.float32, device=device)
        b_t = torch.tensor(np.asarray(B, dtype=np.float64), dtype=torch.float32, device=device)
        phi_t = torch.tensor(np.asarray(phi, dtype=np.float64), dtype=torch.float32, device=device)
        n, d, _ = g_t.shape
        out = torch.empty((n, d, d), dtype=torch.float32, device=device)
        block_n = 64
        grid = (triton.cdiv(n, block_n), d, d)
        _kk_4x4_block_kernel[grid](
            g_t,
            b_t,
            phi_t,
            out,
            n,
            d,
            float(lam * lam),
            g_t.stride(0),
            g_t.stride(1),
            g_t.stride(2),
            b_t.stride(0),
            b_t.stride(1),
            phi_t.stride(0),
            out.stride(0),
            out.stride(1),
            out.stride(2),
            BLOCK_N=block_n,
        )
        out_np = out.detach().cpu().numpy().astype(np.float64)
        return out_np, {
            "ok": True,
            "backend": "triton_jit_kk_4x4_block",
            "reason": "triton_kernel_executed",
        }
    except Exception as exc:  # pragma: no cover
        return fallback, {
            "ok": False,
            "backend": "numpy_fallback",
            "reason": f"triton_lane_error:{exc}",
        }


def benchmark_outer_bb(B: np.ndarray, repeats: int = 5) -> dict[str, Any]:
    """Return reference and Triton-lane timing receipt for outer-product hotspot."""
    B = np.asarray(B, dtype=np.float64)
    repeats = max(1, int(repeats))
    reference_time = 0.0
    for _ in range(repeats):
        start = time.perf_counter()
        _ = outer_bb_reference(B)
        reference_time += time.perf_counter() - start
    triton_time = 0.0
    lane_status: dict[str, Any] = {"ok": False, "backend": "numpy_fallback", "reason": "not_run"}
    out = outer_bb_reference(B)
    for _ in range(repeats):
        start = time.perf_counter()
        out, lane_status = triton_outer_bb(B)
        triton_time += time.perf_counter() - start
    error = float(np.max(np.abs(out - outer_bb_reference(B))))
    return {
        "ok": True,
        "repeats": repeats,
        "reference_mean_seconds": reference_time / repeats,
        "lane_mean_seconds": triton_time / repeats,
        "speedup_vs_reference": (reference_time / triton_time) if triton_time > 0 else 0.0,
        "lane": lane_status,
        "max_abs_error_vs_reference": error,
    }


def benchmark_kk_4x4_block(
    g: np.ndarray,
    B: np.ndarray,
    phi: np.ndarray,
    lam: float = 1.0,
    repeats: int = 5,
) -> dict[str, Any]:
    """Return timing/error receipt for the KK 4x4 block contraction hotspot."""
    repeats = max(1, int(repeats))
    reference_time = 0.0
    for _ in range(repeats):
        start = time.perf_counter()
        _ = kk_4x4_block_reference(g, B, phi, lam=lam)
        reference_time += time.perf_counter() - start
    triton_time = 0.0
    lane_status: dict[str, Any] = {"ok": False, "backend": "numpy_fallback", "reason": "not_run"}
    out = kk_4x4_block_reference(g, B, phi, lam=lam)
    for _ in range(repeats):
        start = time.perf_counter()
        out, lane_status = triton_kk_4x4_block(g, B, phi, lam=lam)
        triton_time += time.perf_counter() - start
    error = float(np.max(np.abs(out - kk_4x4_block_reference(g, B, phi, lam=lam))))
    return {
        "ok": True,
        "repeats": repeats,
        "reference_mean_seconds": reference_time / repeats,
        "lane_mean_seconds": triton_time / repeats,
        "speedup_vs_reference": (reference_time / triton_time) if triton_time > 0 else 0.0,
        "lane": lane_status,
        "max_abs_error_vs_reference": error,
    }
