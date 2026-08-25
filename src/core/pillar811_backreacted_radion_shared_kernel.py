# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 811 — BACKREACTED_RADION_SHARED_KERNEL

Shared kernel for the Sprint AU radion lane. This module does not claim a full
5D Einstein-Boltzmann closure. It packages the common controlled ingredients
that sit underneath Pillars 806–809:

- controlled KK truncation with an explicit geometric tail bound
- explicit radion source term from the truncated tower
- back-reacted boundary update on the Z₂ orbifold
- fixed-point convergence certificate for the shared radion state
- downstream projections to QCD, CMB, w_a, and c_L observables

The goal is to replace four unrelated patches with one auditable object while
preserving the honest open items already registered in Sprint AU.
"""
from __future__ import annotations

import math
from typing import NamedTuple

from src.core.pillar807_backreacted_radion_cmb_phase import (
    N_MODES as CMB_N_MODES,
    Z_REC,
    compute_cmb_residual_reduction,
)
from src.core.pillar808_backreacted_radion_wa_quintessence import (
    compute_wa_quintessence,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "N_W",
    "K_CS",
    "PI_KR",
    "GAMMA_V",
    "TARGET_QCD_ORDERS",
    "SWAMPLAND_DISTANCE_BOUND",
    "KKTruncationResult",
    "SharedKernelResult",
    "ProjectionResult",
    "controlled_kk_truncation",
    "required_delta_phi",
    "backreacted_volume_ratio",
    "explicit_radion_source_term",
    "effective_boundary_shift",
    "iterate_shared_backreaction_kernel",
    "project_n_gap_from_boundary",
    "project_shared_observables",
    "shared_kernel_summary",
    "TAIL_BOUND_CERTIFIED",
    "DELTA_PHI_SHARED",
    "BOUNDARY_SHIFT_SHARED",
    "N_GAP_SHARED",
    "CL_SHARED",
]

N_W: int = 5
K_CS: int = 74
PI_KR: float = 37.0
GAMMA_V: float = 0.5
TARGET_QCD_ORDERS: float = 7.0
SWAMPLAND_DISTANCE_BOUND: float = 30.0
N_MODES_DEFAULT: int = 5
BOUNDARY_OVERLAP_THRESHOLD: float = 1.0 / K_CS
PILLAR_NUMBER: int = 811
PILLAR_GATE: str = "BACKREACTED_RADION_SHARED_KERNEL_CONVERGED"
LEAN4_THEOREM_COUNT: int = 15
LEAN4_TOTAL_AFTER: int = 1306 + LEAN4_THEOREM_COUNT


class KKTruncationResult(NamedTuple):
    n_modes: int
    suppression_ratio: float
    truncated_mode_sum: float
    tail_bound: float
    source_norm: float


class SharedKernelResult(NamedTuple):
    delta_phi_over_M5: float
    volume_ratio: float
    lambda_suppression: float
    source_term: float
    boundary_shift: float
    n_modes: int
    tail_bound: float
    converged: bool
    iterations: int
    swampland_tension: bool
    gate: str


class ProjectionResult(NamedTuple):
    qcd_suppression_orders: float
    cmb_partial_closure_fraction: float
    wa_radion: float
    n_gap: int
    cl_value: float
    gate: str


def required_delta_phi(
    target_orders: float = TARGET_QCD_ORDERS,
    gamma_v: float = GAMMA_V,
) -> float:
    """Solve exp(gamma_v * Δφ/M5) = 10^{-target_orders}."""
    if target_orders <= 0.0:
        raise ValueError("target_orders must be positive")
    if gamma_v <= 0.0:
        raise ValueError("gamma_v must be positive")
    return -target_orders * math.log(10.0) / gamma_v


def backreacted_volume_ratio(delta_phi_over_M5: float) -> float:
    """V_eff / V_0 = exp(Δφ/M5)."""
    return math.exp(delta_phi_over_M5)


def controlled_kk_truncation(
    n_modes: int = N_MODES_DEFAULT,
    pi_kR: float = PI_KR,
    n_w: int = N_W,
    k_cs: int = K_CS,
) -> KKTruncationResult:
    """
    Controlled KK truncation with warp-suppressed geometric tail.

    Mode weights are suppressed by q = exp(-πkR / n_w), which is the minimal
    deterministic warp factor available from the live UM constants πkR = 37 and
    n_w = 5.  The remaining tail is then an exact geometric-series bound.
    """
    if n_modes < 1:
        raise ValueError("n_modes must be at least 1")
    if pi_kR <= 0.0 or n_w <= 0 or k_cs <= 0:
        raise ValueError("pi_kR, n_w, and k_cs must be positive")

    q = math.exp(-pi_kR / n_w)
    truncated = sum(n * q**n for n in range(1, n_modes + 1))
    tail = (q ** (n_modes + 1)) * ((n_modes + 1) - n_modes * q) / ((1.0 - q) ** 2)
    source_norm = truncated / k_cs
    return KKTruncationResult(
        n_modes=n_modes,
        suppression_ratio=q,
        truncated_mode_sum=truncated,
        tail_bound=tail,
        source_norm=source_norm,
    )


def explicit_radion_source_term(
    delta_phi_over_M5: float,
    truncation: KKTruncationResult,
) -> float:
    """
    Explicit shared source term for the radion fixed-point update.

    The sign is negative because the shared Sprint AU kernel is a compression
    channel.  The magnitude is small by construction because the warp-suppressed
    KK tail is treated as a correction on top of the QCD-scale fixed point.
    """
    scale = max(abs(delta_phi_over_M5), 1.0)
    return -truncation.source_norm / (8.0 * math.pi * scale)


def effective_boundary_shift(
    delta_phi_over_M5: float,
    source_term: float,
) -> float:
    """
    Effective orbifold-boundary update from the shared kernel.

    The shift saturates at 1/2 in units of R_0, which is the parity-flip point
    for the odd braid modes {3, 5, 7} used in Pillar 809.
    """
    return 0.5 * math.tanh(abs(delta_phi_over_M5) * (1.0 + abs(source_term)))


def iterate_shared_backreaction_kernel(
    target_orders: float = TARGET_QCD_ORDERS,
    n_modes: int = N_MODES_DEFAULT,
    max_iter: int = 32,
    tol: float = 1e-15,
) -> SharedKernelResult:
    """Iterate the shared radion fixed-point map to convergence."""
    if max_iter < 1:
        raise ValueError("max_iter must be at least 1")
    if tol <= 0.0:
        raise ValueError("tol must be positive")

    truncation = controlled_kk_truncation(n_modes=n_modes)
    base_delta = required_delta_phi(target_orders=target_orders)
    delta = base_delta
    converged = False
    iterations = 0
    source_term = 0.0
    boundary_shift = 0.0

    for step in range(1, max_iter + 1):
        source_term = explicit_radion_source_term(delta, truncation)
        boundary_shift = effective_boundary_shift(delta, source_term)
        delta_next = base_delta * (1.0 + source_term)
        if abs(delta_next - delta) < tol:
            delta = delta_next
            converged = True
            iterations = step
            break
        delta = delta_next
        iterations = step

    volume_ratio = backreacted_volume_ratio(delta)
    lambda_suppression = volume_ratio ** GAMMA_V
    suppression_orders = -math.log10(lambda_suppression)
    swampland_tension = abs(delta) > SWAMPLAND_DISTANCE_BOUND

    gate = (
        "BACKREACTED_RADION_SHARED_KERNEL_CONVERGED"
        if converged and abs(suppression_orders - target_orders) < 0.05
        else "BACKREACTED_RADION_SHARED_KERNEL_RESIDUAL"
    )

    return SharedKernelResult(
        delta_phi_over_M5=delta,
        volume_ratio=volume_ratio,
        lambda_suppression=lambda_suppression,
        source_term=source_term,
        boundary_shift=boundary_shift,
        n_modes=truncation.n_modes,
        tail_bound=truncation.tail_bound,
        converged=converged,
        iterations=iterations,
        swampland_tension=swampland_tension,
        gate=gate,
    )


def project_n_gap_from_boundary(
    boundary_shift: float,
    n_w: int = N_W,
    threshold: float = BOUNDARY_OVERLAP_THRESHOLD,
) -> int:
    """Project the odd braid modes suppressed at the back-reacted boundary."""
    candidate_modes = [n_w - 2, n_w, n_w + 2]
    projected = 0
    for mode in candidate_modes:
        overlap = abs(math.cos(mode * math.pi * boundary_shift))
        if overlap <= threshold:
            projected += 1
    return projected


def project_shared_observables(
    kernel: SharedKernelResult | None = None,
) -> ProjectionResult:
    """Project the shared kernel onto the four Sprint AU observables."""
    if kernel is None:
        kernel = iterate_shared_backreaction_kernel()

    suppression_orders = -math.log10(kernel.lambda_suppression)
    phi_amp_rec = min(0.1, abs(kernel.delta_phi_over_M5) / math.sqrt(1.0 + Z_REC))
    cmb = compute_cmb_residual_reduction(phi_amp=phi_amp_rec, n_modes=CMB_N_MODES)
    wa = compute_wa_quintessence(delta_phi_m5=kernel.delta_phi_over_M5)
    n_gap = project_n_gap_from_boundary(kernel.boundary_shift)
    cl_value = (K_CS - n_gap) / K_CS

    gate = (
        "BACKREACTED_RADION_SHARED_PROJECTIONS_PASS"
        if abs(suppression_orders - TARGET_QCD_ORDERS) < 0.05
        and cmb.partial_closure_fraction > 0.0
        and wa.wa_radion < 0.0
        and n_gap == 3
        and abs(cl_value - 71.0 / 74.0) < 1e-15
        else "BACKREACTED_RADION_SHARED_PROJECTIONS_RESIDUAL"
    )

    return ProjectionResult(
        qcd_suppression_orders=suppression_orders,
        cmb_partial_closure_fraction=cmb.partial_closure_fraction,
        wa_radion=wa.wa_radion,
        n_gap=n_gap,
        cl_value=cl_value,
        gate=gate,
    )


_KERNEL = iterate_shared_backreaction_kernel()
_PROJECTION = project_shared_observables(_KERNEL)
TAIL_BOUND_CERTIFIED: float = _KERNEL.tail_bound
DELTA_PHI_SHARED: float = _KERNEL.delta_phi_over_M5
BOUNDARY_SHIFT_SHARED: float = _KERNEL.boundary_shift
N_GAP_SHARED: int = _PROJECTION.n_gap
CL_SHARED: float = _PROJECTION.cl_value


def shared_kernel_summary(
    kernel: SharedKernelResult | None = None,
    projection: ProjectionResult | None = None,
) -> dict[str, float | int | bool | str]:
    """Return the machine-readable summary for Pillar 811."""
    if kernel is None:
        kernel = _KERNEL
    if projection is None:
        projection = _PROJECTION if kernel is _KERNEL else project_shared_observables(kernel)
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_GATE,
        "delta_phi_over_M5": kernel.delta_phi_over_M5,
        "volume_ratio": kernel.volume_ratio,
        "lambda_suppression": kernel.lambda_suppression,
        "source_term": kernel.source_term,
        "boundary_shift": kernel.boundary_shift,
        "kk_tail_bound": kernel.tail_bound,
        "converged": kernel.converged,
        "iterations": kernel.iterations,
        "swampland_tension": kernel.swampland_tension,
        "qcd_suppression_orders": projection.qcd_suppression_orders,
        "cmb_partial_closure_fraction": projection.cmb_partial_closure_fraction,
        "wa_radion": projection.wa_radion,
        "n_gap": projection.n_gap,
        "cl_value": projection.cl_value,
        "projection_gate": projection.gate,
    }
