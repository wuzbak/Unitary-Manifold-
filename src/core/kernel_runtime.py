# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Backend-aware kernel runtime scaffolding for UM metric/evolution parity."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import importlib.util
import platform

import numpy as np

from .metric import compute_curvature
from .triton_kernels import (
    benchmark_kk_4x4_block,
    benchmark_outer_bb,
    kk_4x4_block_reference,
    triton_kk_4x4_block,
    triton_outer_bb,
)

try:  # Optional dependency.
    from .jax_metric import JAX_AVAILABLE as _JAX_METRIC_AVAILABLE, jax_compute_curvature
except Exception:  # pragma: no cover - optional backend may be unavailable.
    _JAX_METRIC_AVAILABLE = False
    jax_compute_curvature = None


@dataclass(frozen=True)
class KernelContract:
    contract_id: str
    operation: str
    inputs: dict[str, str]
    outputs: dict[str, str]
    tolerance: float
    precision_mode: str


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _detect_torch_backend() -> dict[str, Any]:
    if not _module_available("torch"):
        return {"available": False}
    try:
        import torch  # type: ignore

        cuda_visible = bool(torch.cuda.is_available())
        hip_version = str(getattr(torch.version, "hip", "") or "")
        cuda_version = str(getattr(torch.version, "cuda", "") or "")
        backend_kind = "cpu"
        vendor = "unknown"
        device_name = "cpu"
        if cuda_visible:
            backend_kind = "rocm" if hip_version else "cuda"
            vendor = "amd" if hip_version else "nvidia"
            try:
                device_name = str(torch.cuda.get_device_name(0))
            except Exception:
                device_name = "gpu"
        return {
            "available": True,
            "cuda_visible": cuda_visible,
            "backend_kind": backend_kind,
            "vendor": vendor,
            "device_name": device_name,
            "cuda_version": cuda_version,
            "hip_version": hip_version,
            "mps_available": bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()),
        }
    except Exception as exc:  # pragma: no cover
        return {"available": False, "error": str(exc)}


def _detect_jax_backend() -> dict[str, Any]:
    if not _module_available("jax"):
        return {"available": False}
    try:
        import jax  # type: ignore

        devices = list(jax.devices())
        first = devices[0] if devices else None
        platform_name = str(getattr(first, "platform", "cpu")) if first else "cpu"
        device_kind = str(getattr(first, "device_kind", "cpu")) if first else "cpu"
        vendor = "unknown"
        lower_kind = device_kind.lower()
        if "nvidia" in lower_kind:
            vendor = "nvidia"
        elif "amd" in lower_kind or "radeon" in lower_kind or "instinct" in lower_kind:
            vendor = "amd"
        return {
            "available": True,
            "platform": platform_name,
            "device_kind": device_kind,
            "device_count": len(devices),
            "vendor": vendor,
        }
    except Exception as exc:  # pragma: no cover
        return {"available": False, "error": str(exc)}


def detect_backend_capability() -> dict[str, Any]:
    torch_info = _detect_torch_backend()
    jax_info = _detect_jax_backend()
    triton_available = _module_available("triton")
    selected = "numpy_cpu"
    if torch_info.get("available") and torch_info.get("cuda_visible"):
        selected = "triton_candidate" if triton_available else str(torch_info.get("backend_kind"))
    elif jax_info.get("available") and str(jax_info.get("platform")) in {"gpu", "tpu"}:
        selected = "jax_xla"
    wavefront_hint = "unknown"
    if str(torch_info.get("vendor")) == "nvidia":
        wavefront_hint = "warp32"
    elif str(torch_info.get("vendor")) == "amd":
        wavefront_hint = "wave32_or_wave64_runtime_detect"
    return {
        "selected_backend": selected,
        "triton_available": triton_available,
        "jax_metric_available": bool(_JAX_METRIC_AVAILABLE),
        "wavefront_hint": wavefront_hint,
        "torch": torch_info,
        "jax": jax_info,
        "host": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
    }


def kernel_contract_schema() -> dict[str, Any]:
    contracts = [
        KernelContract(
            contract_id="metric.curvature.v1",
            operation="compute_curvature(g,B,phi,dx)",
            inputs={"g": "(N,4,4)", "B": "(N,4)", "phi": "(N,)", "dx": "float"},
            outputs={"Gamma": "(N,4,4,4)", "Riemann": "(N,4,4,4,4)", "Ricci": "(N,4,4)", "R": "(N,)"},
            tolerance=1e-8,
            precision_mode="float64",
        ),
        KernelContract(
            contract_id="evolution.step.rk4.v1",
            operation="step(state, dt)",
            inputs={"state.g": "(N,4,4)", "state.B": "(N,4)", "state.phi": "(N,)", "dt": "float"},
            outputs={"state_next.g": "(N,4,4)", "state_next.B": "(N,4)", "state_next.phi": "(N,)"},
            tolerance=1e-7,
            precision_mode="float64",
        ),
    ]
    return {
        "schema_version": "kernel_contracts_v1",
        "contracts": [asdict(item) for item in contracts],
        "governance": {
            "preserve_reference_behavior": True,
            "unchecked_bypass_forbidden": True,
            "handshake_and_allowlist_required_for_runtime_execution": True,
        },
    }


def _sample_fields(points: int = 8, seed: int = 7) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    points = max(3, int(points))
    rng = np.random.default_rng(seed)
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (points, 1, 1)) + 1e-3 * rng.standard_normal((points, 4, 4))
    g = 0.5 * (g + np.transpose(g, (0, 2, 1)))
    B = 1e-3 * rng.standard_normal((points, 4))
    phi = 1.0 + 1e-3 * rng.standard_normal(points)
    dx = 0.125
    return g, B, phi, dx


def build_kernel_parity_receipt(points: int = 8, seed: int = 7) -> dict[str, Any]:
    g, B, phi, dx = _sample_fields(points=points, seed=seed)
    _, _, _, r_numpy = compute_curvature(g, B, phi, dx)
    lanes: dict[str, Any] = {
        "numpy_reference": {
            "ok": True,
            "backend": "numpy_cpu",
            "scalar_count": int(r_numpy.shape[0]),
        },
    }
    gate = {"parity_pass": False, "fail_closed": True, "required_tolerance": 1e-8}
    if _JAX_METRIC_AVAILABLE and jax_compute_curvature is not None:
        _, _, _, r_jax = jax_compute_curvature(g, B, phi, dx)
        r_jax_np = np.asarray(r_jax)
        max_abs_error = float(np.max(np.abs(r_numpy - r_jax_np)))
        parity_pass = bool(max_abs_error <= gate["required_tolerance"])
        lanes["jax_xla"] = {
            "ok": True,
            "backend": "jax_xla",
            "max_abs_error_vs_numpy": max_abs_error,
            "parity_pass": parity_pass,
        }
        gate["parity_pass"] = parity_pass
        gate["fail_closed"] = not parity_pass
    else:
        lanes["jax_xla"] = {
            "ok": False,
            "backend": "jax_xla",
            "reason": "jax_metric_backend_unavailable",
            "parity_pass": False,
        }
    capability = detect_backend_capability()
    triton_outer, triton_status = triton_outer_bb(B)
    reference_outer = np.einsum("ni,nj->nij", B, B)
    triton_outer_error = float(np.max(np.abs(reference_outer - triton_outer)))
    triton_tolerance = 1e-6
    triton_parity_pass = bool(triton_outer_error <= triton_tolerance)
    lanes["triton_compiled"] = {
        "ok": bool(triton_status.get("ok", False)),
        "backend": str(triton_status.get("backend", "triton_compiled")),
        "reason": str(triton_status.get("reason", "")),
        "max_abs_error_vs_numpy_outer_bb": triton_outer_error,
        "required_tolerance": triton_tolerance,
        "parity_pass": triton_parity_pass,
    }
    triton_kk_block, triton_kk_status = triton_kk_4x4_block(g, B, phi, lam=1.0)
    reference_kk_block = kk_4x4_block_reference(g, B, phi, lam=1.0)
    triton_kk_error = float(np.max(np.abs(reference_kk_block - triton_kk_block)))
    triton_kk_tolerance = 1e-6
    triton_kk_parity_pass = bool(triton_kk_error <= triton_kk_tolerance)
    lanes["triton_metric_block_compiled"] = {
        "ok": bool(triton_kk_status.get("ok", False)),
        "backend": str(triton_kk_status.get("backend", "triton_compiled")),
        "reason": str(triton_kk_status.get("reason", "")),
        "max_abs_error_vs_numpy_kk_4x4_block": triton_kk_error,
        "required_tolerance": triton_kk_tolerance,
        "parity_pass": triton_kk_parity_pass,
    }
    triton_required = bool(
        capability.get("triton_available")
        and bool((capability.get("torch") or {}).get("available"))
        and bool((capability.get("torch") or {}).get("cuda_visible"))
    )
    triton_failures = []
    if not triton_parity_pass:
        triton_failures.append("outer_bb")
    if not triton_kk_parity_pass:
        triton_failures.append("kk_4x4_metric_block")
    if triton_required and triton_failures:
        gate["parity_pass"] = False
        gate["fail_closed"] = True
        gate["triton_gate"] = "required_and_failed"
        gate["triton_failed_hotspots"] = triton_failures
    else:
        gate["triton_gate"] = "optional_or_passed"
    return {
        "ok": True,
        "contract": "metric.curvature.v1",
        "capability": capability,
        "lanes": lanes,
        "gate": gate,
        "honesty_note": (
            "This receipt validates parity against canonical NumPy behavior and "
            "reports unavailable compiled lanes explicitly; it does not claim that "
            "all kernels are already compiled."
        ),
    }


def build_kernel_benchmark_receipt(points: int = 128, seed: int = 11, repeats: int = 5) -> dict[str, Any]:
    g, B, phi, _ = _sample_fields(points=points, seed=seed)
    bench_outer = benchmark_outer_bb(B, repeats=repeats)
    bench_metric = benchmark_kk_4x4_block(g, B, phi, lam=1.0, repeats=repeats)
    capability = detect_backend_capability()
    return {
        "ok": True,
        "benchmarks": {
            "outer_bb_hotspot": bench_outer,
            "kk_4x4_metric_block_hotspot": bench_metric,
        },
        "capability": capability,
        "policy": {
            "compiled_lane_claim_requires_parity": True,
            "compiled_lane_claim_requires_visible_receipt": True,
        },
    }


def run_epistemic_compactification_sanity(
    mas_tracker_path: str | Path,
    fallibility_path: str | Path,
) -> dict[str, Any]:
    mas_path = Path(mas_tracker_path)
    fall_path = Path(fallibility_path)
    mas_text = mas_path.read_text(encoding="utf-8") if mas_path.exists() else ""
    fall_text = fall_path.read_text(encoding="utf-8") if fall_path.exists() else ""
    checks = [
        {"id": "mas_tracker_exists", "ok": mas_path.exists()},
        {"id": "fallibility_exists", "ok": fall_path.exists()},
        {"id": "mas_tracker_remaining_open", "ok": "remaining_open:" in mas_text},
        {"id": "mas_tracker_observational_falsifiers", "ok": "observational_falsifiers_unchanged" in mas_text},
        {"id": "fallibility_open_limits_note", "ok": "no additional physics closure is claimed" in fall_text.lower()},
        {"id": "fallibility_scientific_limit_note", "ok": "does not remove the scientific limitations" in fall_text.lower()},
    ]
    ok = all(bool(item["ok"]) for item in checks)
    return {
        "ok": ok,
        "check_count": len(checks),
        "checks": checks,
        "fail_closed": not ok,
        "sources": [str(mas_path), str(fall_path)],
        "policy": {
            "compactification_mode": "sanitized_functional_ingest",
            "unchecked_bypass_forbidden": True,
            "epistemic_label_visibility_required": True,
        },
    }
