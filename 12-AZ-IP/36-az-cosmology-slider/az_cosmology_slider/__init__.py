# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Differentiable Cosmology Slider — Product 36.

Phases 1-2 of article-354 direction #9: a real-time slider-ready API over
`src/core/jax_backend.grad_spectral_index`, so a UI can show (n_s, gradient)
for any (phi0, n_w) position and how far it is from the Planck 2018
measurement — plus the actual interactive front-end calling it over HTTP.

Epistemic status: this is an educational gradient display over an
already-tested differentiable backend; it introduces no new physics claim.
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
from .api import API_ENDPOINTS, dispatch_api_request

__all__ = [
    "JAX_AVAILABLE",
    "N_S_PLANCK_2018",
    "N_S_UM_CANONICAL",
    "SliderReading",
    "require_jax",
    "slider_reading",
    "sweep_phi0",
    "API_ENDPOINTS",
    "dispatch_api_request",
]

__version__ = "1.1.0"
