# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Real-time differentiable cosmology slider — Phase 1 of article-354
direction #9 ("Differentiable backend -> education slider").

Wraps `src/core/jax_backend.grad_spectral_index(phi0, n_w)` into a
slider-ready API: given a (phi0, n_w) position, return not just n_s but
the local gradient, so a UI slider can show which direction decreases the
gap to the Planck 2018 measurement in real time.

JAX is an optional dependency throughout this repository; this module
follows the same guarded-import convention used elsewhere (e.g.
`src/core/jax_backend.py` requires `jax` to be installed, but downstream
consumers of *this* module should not hard-fail at import time if JAX is
unavailable in their environment).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import islice
from typing import Optional

from ._repo import ensure_repo_on_path

_REPO_ROOT = ensure_repo_on_path()

try:
    from src.core.jax_backend import grad_spectral_index as _grad_spectral_index
    JAX_AVAILABLE = True
    _IMPORT_ERROR: Optional[str] = None
except Exception as exc:  # pragma: no cover - exercised only when JAX missing
    _grad_spectral_index = None
    JAX_AVAILABLE = False
    _IMPORT_ERROR = str(exc)

#: Planck 2018 measured scalar spectral index (source: src/core/cmb_polarisation.py).
N_S_PLANCK_2018 = 0.9649

#: UM canonical winding-number prediction (source: multiple pillar modules).
N_S_UM_CANONICAL = 0.9635
MIN_PHI0 = 1.0
MAX_PHI0 = 30.0
MIN_N_W = -100.0
MAX_N_W = 100.0


@dataclass(frozen=True)
class SliderReading:
    """One slider position: inputs, prediction, gradient, and distance
    to the Planck 2018 measured value."""

    phi0: float
    n_w: float
    n_s: float
    dn_s_dphi0: float
    dn_s_dnw: float
    gap_to_planck: float

    @property
    def closer_if_phi0_increases(self) -> bool:
        """True if increasing phi0 moves n_s towards the Planck value."""
        moving_toward = (N_S_PLANCK_2018 - self.n_s) * self.dn_s_dphi0
        return moving_toward > 0


def require_jax() -> None:
    if not JAX_AVAILABLE:
        raise RuntimeError(
            "JAX is not available in this environment "
            f"(import failed with: {_IMPORT_ERROR}). "
            "Install the 'jax' package to use the live slider."
        )


def slider_reading(phi0: float, n_w: float) -> SliderReading:
    """Evaluate the slider at a given (phi0, n_w) position."""
    try:
        phi0 = float(phi0)
        n_w = float(n_w)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("phi0 and n_w must be finite numbers") from exc
    if not math.isfinite(phi0) or not MIN_PHI0 <= phi0 <= MAX_PHI0:
        raise ValueError(f"phi0 must be finite and in {MIN_PHI0:g}..{MAX_PHI0:g}")
    if not math.isfinite(n_w) or not MIN_N_W <= n_w <= MAX_N_W:
        raise ValueError(f"n_w must be finite and in {MIN_N_W:g}..{MAX_N_W:g}")
    require_jax()
    n_s, dn_s_dphi0, dn_s_dnw = _grad_spectral_index(phi0, n_w)
    return SliderReading(
        phi0=float(phi0),
        n_w=float(n_w),
        n_s=n_s,
        dn_s_dphi0=dn_s_dphi0,
        dn_s_dnw=dn_s_dnw,
        gap_to_planck=n_s - N_S_PLANCK_2018,
    )


def sweep_phi0(n_w: float, phi0_values) -> list:
    """Evaluate the slider at a sequence of phi0 values for one n_w,
    suitable for driving a continuous UI slider widget."""
    try:
        values = list(islice(iter(phi0_values), 202))
    except TypeError as exc:
        raise ValueError("phi0_values must be an iterable of positions") from exc
    if not values or len(values) > 201:
        raise ValueError("phi0_values must contain 1..201 positions")
    return [slider_reading(phi0, n_w) for phi0 in values]
