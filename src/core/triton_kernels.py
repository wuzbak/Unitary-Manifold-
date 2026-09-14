# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Optional Triton hotspot kernels with deterministic NumPy fallback."""

from __future__ import annotations

from typing import Any
import importlib.util

import numpy as np


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


TRITON_AVAILABLE = _module_available("triton")
TORCH_AVAILABLE = _module_available("torch")


def outer_bb_reference(B: np.ndarray) -> np.ndarray:
    """Reference hotspot contraction: (N,4) -> (N,4,4) via outer product."""
    return np.einsum("ni,nj->nij", B, B)


def triton_outer_bb(B: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    """Execute Triton-compatible outer product lane when available, else fallback."""
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
        b_t = torch.tensor(B, dtype=torch.float64, device=device)
        out = torch.einsum("ni,nj->nij", b_t, b_t).detach().cpu().numpy()
        return out, {
            "ok": True,
            "backend": "triton_candidate_via_torch_cuda",
            "reason": "first_hotspot_lane",
        }
    except Exception as exc:  # pragma: no cover
        return fallback, {
            "ok": False,
            "backend": "numpy_fallback",
            "reason": f"triton_lane_error:{exc}",
        }
