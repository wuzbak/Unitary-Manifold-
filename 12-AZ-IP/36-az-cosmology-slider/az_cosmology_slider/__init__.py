# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Differentiable Cosmology Slider — Product 36.

Phase 1 of article-354 direction #9: a real-time slider-ready API over
`src/core/jax_backend.grad_spectral_index`, so a UI can show (n_s, gradient)
for any (phi0, n_w) position and how far it is from the Planck 2018
measurement.

Epistemic status: this product does not ship a UI. It provides the
differentiable backend contract a slider widget would call; building the
actual interactive front-end (Phase 2 in the article's language) is out
of scope here.
"""

from .slider import (
    JAX_AVAILABLE,
    N_S_PLANCK_2018,
    N_S_UM_CANONICAL,
    SliderReading,
    require_jax,
    slider_reading,
    sweep_phi0,
)

__all__ = [
    "JAX_AVAILABLE",
    "N_S_PLANCK_2018",
    "N_S_UM_CANONICAL",
    "SliderReading",
    "require_jax",
    "slider_reading",
    "sweep_phi0",
]

__version__ = "1.0.0"
