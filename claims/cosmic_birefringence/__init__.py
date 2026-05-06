# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""claims/cosmic_birefringence — Machine-readable falsification claim.

Cosmic birefringence β is the primary falsification target of the
Unitary Manifold.  This module provides a machine-readable
``FALSIFICATION_CONDITION`` dict that can be queried by external tools.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from .claim import (
    FALSIFICATION_CONDITION,
    BETA_CANONICAL_DEG,
    BETA_ALTERNATE_DEG,
    KILL_ZONE_LOW_DEG,
    KILL_ZONE_HIGH_DEG,
    ADMISSIBLE_LOW_DEG,
    ADMISSIBLE_HIGH_DEG,
    evaluate_measurement,
)

__all__ = [
    "FALSIFICATION_CONDITION",
    "BETA_CANONICAL_DEG",
    "BETA_ALTERNATE_DEG",
    "KILL_ZONE_LOW_DEG",
    "KILL_ZONE_HIGH_DEG",
    "ADMISSIBLE_LOW_DEG",
    "ADMISSIBLE_HIGH_DEG",
    "evaluate_measurement",
]
