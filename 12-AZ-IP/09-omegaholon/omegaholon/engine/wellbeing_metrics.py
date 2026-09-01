# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Wellbeing metric helpers for OmegaHolon."""
from __future__ import annotations

import math
import statistics

PHI = (1 + 5 ** 0.5) / 2
PSYCHOLOGY_PILLARS = {'cognition': 'P024', 'behavior': 'P024', 'social': 'P024'}


def compute_phi_coherence(metrics: dict) -> float:
    """Compute a bounded coherence score from normalized wellbeing metrics."""
    raw_numeric = [float(value) for value in metrics.values() if isinstance(value, (int, float))]
    if not raw_numeric:
        return 0.0
    scale = 10.0 if any(value > 1.0 for value in raw_numeric) else 1.0
    numeric = [min(1.0, max(0.0, value / scale)) for value in raw_numeric]
    mean_value = statistics.fmean(numeric)
    variance = statistics.pvariance(numeric) if len(numeric) > 1 else 0.0
    balance = 1.0 / (1.0 + variance * PHI * 4.0)
    coherence = 0.7 * mean_value + 0.3 * balance
    return round(min(1.0, max(0.0, coherence)), 6)
