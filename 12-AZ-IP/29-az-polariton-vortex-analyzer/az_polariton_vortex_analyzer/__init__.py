# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Polariton Vortex Analyzer — Product 29.

Phase-0 signal-processing pipeline for article-354 direction #2: extracts a
measured polariton feature velocity, as a function of wavefront half-angle,
from femtosecond pump-probe frame data, and compares it against the braided
sound-speed critical-angle prediction in `src/materials/polariton_vortex.py`
(c_s = 12/37, θ_c ≈ 18.93°).

Epistemic status: this is analysis software only. It makes no claim about
any specific hBN dataset; it is built and unit-tested against synthetic
data so that it is ready the moment a real pump-probe dataset (e.g. from
Kaminer et al., Nature 2026) is available for comparison.
"""

from .pipeline import (
    PumpProbeFrame,
    FeatureVelocityCurve,
    extract_feature_velocity_curve,
    compare_to_prediction,
)
from .api import API_ENDPOINTS, dispatch_api_request

__all__ = [
    "PumpProbeFrame",
    "FeatureVelocityCurve",
    "extract_feature_velocity_curve",
    "compare_to_prediction",
    "API_ENDPOINTS",
    "dispatch_api_request",
]

__version__ = "1.1.0"
