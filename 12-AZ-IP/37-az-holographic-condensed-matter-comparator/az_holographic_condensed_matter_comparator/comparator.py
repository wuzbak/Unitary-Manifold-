# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Holographic condensed-matter comparator — Phase 1 of article-354
direction #10 ("Holographic dictionary -> condensed-matter comparison").

`src/holography/dual_cft_spectrum.py`'s `kk_tower_to_cft_operators()`
already produces boundary-operator conformal dimensions
(Delta_n ~ 4 + 2n) for the RS1 KK graviton tower. This module compares
those dimensions against well-known reference values from the
holographic-superconductor literature (not fit to any specific real
material or compound), computing the scalar two-point correlation decay
exponent (2*Delta) each dimension implies, so the two "scaffolds" can be
placed side by side.

Honest status: the reference benchmark table below is **illustrative**
— standard order-parameter dimensions quoted in the holographic-
superconductor literature (Hartnoll, "Lectures on holographic methods for
condensed matter physics", arXiv:0903.3246; Gubser, "Breaking an Abelian
gauge symmetry near a black hole horizon", arXiv:0801.2977). It is not a
fit to any specific compound's measured critical exponents.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ._repo import ensure_repo_on_path

_REPO_ROOT = ensure_repo_on_path()

from src.holography.dual_cft_spectrum import kk_tower_to_cft_operators


@dataclass(frozen=True)
class HolographicBenchmark:
    """One reference operator dimension from the holographic-superconductor
    literature. Illustrative only; see module docstring."""

    name: str
    delta: float
    source: str


#: Illustrative reference benchmarks (not fit to any real compound).
KNOWN_HOLOGRAPHIC_BENCHMARKS: List[HolographicBenchmark] = [
    HolographicBenchmark(
        "marginal_scalar", 3.0,
        "Hartnoll arXiv:0903.3246 - marginal operator, Delta = d - 1 = 3 in AdS4/CFT3",
    ),
    HolographicBenchmark(
        "bcs_like_order_parameter", 1.5,
        "Hartnoll arXiv:0903.3246 Sec. 2 - canonical holographic-superconductor "
        "condensate dimension used in worked examples",
    ),
    HolographicBenchmark(
        "minimal_scalar_hair", 2.0,
        "Gubser arXiv:0801.2977 - minimal charged scalar condensate dimension "
        "in the simplest holographic superconductor model",
    ),
]


def correlation_decay_exponent(delta: float) -> float:
    """Scalar two-point function <O(x)O(0)> ~ 1/x^(2*Delta) in a CFT."""
    return 2.0 * delta


def compare_kk_level_to_benchmark(n: int, benchmark: HolographicBenchmark) -> Dict[str, object]:
    """Compare one KK-tower operator level's conformal dimension against a
    named holographic-superconductor reference benchmark."""
    levels = kk_tower_to_cft_operators(n_max=n)["operator_levels"]
    level = levels[n - 1]
    um_delta = level["conformal_dimension"]
    return {
        "n": n,
        "um_delta": um_delta,
        "um_decay_exponent": correlation_decay_exponent(um_delta),
        "benchmark_name": benchmark.name,
        "benchmark_delta": benchmark.delta,
        "benchmark_decay_exponent": correlation_decay_exponent(benchmark.delta),
        "delta_gap": um_delta - benchmark.delta,
        "source": benchmark.source,
    }


def compare_kk_tower_to_all_benchmarks(n_max: int = 5) -> List[Dict[str, object]]:
    """Compare every KK-tower level up to n_max against every benchmark."""
    comparisons = []
    for n in range(1, n_max + 1):
        for benchmark in KNOWN_HOLOGRAPHIC_BENCHMARKS:
            comparisons.append(compare_kk_level_to_benchmark(n, benchmark))
    return comparisons


def closest_benchmark(n: int) -> Dict[str, object]:
    """Return the benchmark whose conformal dimension is closest to the
    n-th KK-tower level's dimension."""
    comparisons = [compare_kk_level_to_benchmark(n, b) for b in KNOWN_HOLOGRAPHIC_BENCHMARKS]
    return min(comparisons, key=lambda c: abs(c["delta_gap"]))
