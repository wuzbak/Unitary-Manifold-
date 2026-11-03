# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Polariton Vortex Analyzer — Product 29.

Phase-0 tracked-feature pipeline for article-354 direction #2: extracts a
measured polariton feature velocity, as a function of wavefront half-angle,
from femtosecond pump-probe frame data, and compares it against the braided
sound-speed critical-angle prediction in `src/materials/polariton_vortex.py`
(c_s = 12/37, θ_c ≈ 18.93°).

Epistemic status: analysis software only, tested with constructed fixtures.
Accepts user-supplied tracked-feature JSON/CSV exports without independently
verifying their source or calibration. No real dataset is bundled and no
comparison validates UM or any hardgate physics claim.
"""

from .pipeline import (
    PumpProbeFrame,
    FeatureVelocityCurve,
    extract_feature_velocity_curve,
    compare_to_prediction,
)
from .api import API_ENDPOINTS, dispatch_api_request
from .measurement import analyze_measurement, analyze_measurement_file

__all__ = [
    "PumpProbeFrame",
    "FeatureVelocityCurve",
    "extract_feature_velocity_curve",
    "compare_to_prediction",
    "API_ENDPOINTS",
    "dispatch_api_request",
    "analyze_measurement",
    "analyze_measurement_file",
]

__version__ = "1.1.0"
