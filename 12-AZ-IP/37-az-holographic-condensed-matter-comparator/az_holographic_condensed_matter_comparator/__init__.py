# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Holographic Condensed-Matter Comparator — Product 37.

Phase 1 of article-354 direction #10: compares
`src/holography/dual_cft_spectrum.py`'s KK-tower boundary-operator
dimensions against illustrative reference values from the
holographic-superconductor literature.

Epistemic status: the benchmark table is illustrative only (standard
textbook/lecture-note values, not a fit to any real compound). No claim
is made that the UM KK-tower matches any specific laboratory material.
"""

from .comparator import (
    HolographicBenchmark,
    KNOWN_HOLOGRAPHIC_BENCHMARKS,
    correlation_decay_exponent,
    compare_kk_level_to_benchmark,
    compare_kk_tower_to_all_benchmarks,
    closest_benchmark,
)

__all__ = [
    "HolographicBenchmark",
    "KNOWN_HOLOGRAPHIC_BENCHMARKS",
    "correlation_decay_exponent",
    "compare_kk_level_to_benchmark",
    "compare_kk_tower_to_all_benchmarks",
    "closest_benchmark",
]

__version__ = "1.0.0"
