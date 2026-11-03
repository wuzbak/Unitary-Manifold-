# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Holographic condensed-matter comparator — Phase 1 of article-354
direction #10 ("Holographic dictionary -> condensed-matter comparison").

`src/holography/dual_cft_spectrum.py`'s `kk_tower_to_cft_operators()`
already produces approximate spin-2 boundary-operator conformal dimensions
(Delta_n ~ 4 + 2n) for the RS1 KK graviton tower. This module compares
those dimensions against illustrative or user-supplied reference dimensions
and computes 2*Delta as a scaling exponent. This numerical comparison does
not identify scalar and spin-2 operators or compare tensor structures.

Honest status: the reference benchmark table below is **illustrative**.
Its reading references are background, not verified extractions of the
specific numbers or evidence of a material correspondence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from ._repo import ensure_repo_on_path

_REPO_ROOT = ensure_repo_on_path()

from src.holography.dual_cft_spectrum import kk_tower_to_cft_operators

MAX_LEVELS = 100


def validate_level_count(n: int) -> None:
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= MAX_LEVELS:
        raise ValueError(f"level count must be an integer from 1 to {MAX_LEVELS}")


@dataclass(frozen=True)
class HolographicBenchmark:
    """One reference dimension with a provenance label, not a verified claim."""

    name: str
    delta: float
    source: str
    provenance: str = "illustrative"


#: Illustrative reference benchmarks (not fit to any real compound).
KNOWN_HOLOGRAPHIC_BENCHMARKS: List[HolographicBenchmark] = [
    HolographicBenchmark(
        "marginal_scalar", 3.0,
        "Illustrative Delta=3 scalar example; background: Hartnoll arXiv:0903.3246. "
        "Not a verified extraction.",
    ),
    HolographicBenchmark(
        "bcs_like_order_parameter", 1.5,
        "Illustrative Delta=1.5 example; legacy name does not establish a BCS "
        "correspondence. Background: Hartnoll arXiv:0903.3246, not a verified extraction.",
    ),
    HolographicBenchmark(
        "minimal_scalar_hair", 2.0,
        "Illustrative Delta=2 scalar example; background: Gubser arXiv:0801.2977. "
        "Not a verified extraction.",
    ),
]


def correlation_decay_exponent(delta: float) -> float:
    """Scalar two-point function <O(x)O(0)> ~ 1/x^(2*Delta) in a CFT."""
    return 2.0 * delta


def compare_kk_level_to_benchmark(n: int, benchmark: HolographicBenchmark) -> Dict[str, object]:
    """Compare one KK-tower operator level's conformal dimension against a
    named holographic-superconductor reference benchmark."""
    validate_level_count(n)
    levels = kk_tower_to_cft_operators(n_max=n)["operator_levels"]
    level = levels[n - 1]
    return _compare_level(level, benchmark)


def _compare_level(level: dict, benchmark: HolographicBenchmark) -> Dict[str, object]:
    um_delta = level["conformal_dimension"]
    return {
        "n": level["n"],
        "um_delta": um_delta,
        "um_decay_exponent": correlation_decay_exponent(um_delta),
        "benchmark_name": benchmark.name,
        "benchmark_delta": benchmark.delta,
        "benchmark_decay_exponent": correlation_decay_exponent(benchmark.delta),
        "delta_gap": um_delta - benchmark.delta,
        "source": benchmark.source,
        "provenance": benchmark.provenance,
    }


def compare_kk_tower_to_all_benchmarks(
    n_max: int = 5, benchmarks: Sequence[HolographicBenchmark] | None = None,
) -> List[Dict[str, object]]:
    """Compare every KK-tower level up to n_max against every benchmark."""
    validate_level_count(n_max)
    references = KNOWN_HOLOGRAPHIC_BENCHMARKS if benchmarks is None else benchmarks
    levels = kk_tower_to_cft_operators(n_max=n_max)["operator_levels"]
    return [_compare_level(level, benchmark) for level in levels for benchmark in references]


def closest_benchmark(n: int) -> Dict[str, object]:
    """Return the benchmark whose conformal dimension is closest to the
    n-th KK-tower level's dimension."""
    comparisons = [compare_kk_level_to_benchmark(n, b) for b in KNOWN_HOLOGRAPHIC_BENCHMARKS]
    return min(comparisons, key=lambda c: abs(c["delta_gap"]))
