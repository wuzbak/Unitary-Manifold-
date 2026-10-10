# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_holographic_condensed_matter_comparator import (
    KNOWN_HOLOGRAPHIC_BENCHMARKS,
    correlation_decay_exponent,
    compare_kk_level_to_benchmark,
    compare_kk_tower_to_all_benchmarks,
    closest_benchmark,
)


def test_correlation_decay_exponent_doubles_delta():
    assert correlation_decay_exponent(2.0) == pytest.approx(4.0)


def test_benchmarks_have_names_and_sources():
    assert len(KNOWN_HOLOGRAPHIC_BENCHMARKS) == 3
    for b in KNOWN_HOLOGRAPHIC_BENCHMARKS:
        assert b.name
        assert b.source
        assert b.delta > 0


def test_compare_kk_level_to_benchmark_n1():
    benchmark = KNOWN_HOLOGRAPHIC_BENCHMARKS[0]
    result = compare_kk_level_to_benchmark(1, benchmark)
    assert result["n"] == 1
    assert result["um_delta"] == pytest.approx(6.0)  # 4 + 2*1
    assert result["delta_gap"] == pytest.approx(6.0 - benchmark.delta)


def test_compare_kk_level_decay_exponent_consistency():
    benchmark = KNOWN_HOLOGRAPHIC_BENCHMARKS[1]
    result = compare_kk_level_to_benchmark(2, benchmark)
    assert result["um_decay_exponent"] == pytest.approx(2.0 * result["um_delta"])


def test_compare_kk_tower_to_all_benchmarks_count():
    comparisons = compare_kk_tower_to_all_benchmarks(n_max=3)
    assert len(comparisons) == 3 * len(KNOWN_HOLOGRAPHIC_BENCHMARKS)


def test_closest_benchmark_returns_minimal_gap():
    result = closest_benchmark(1)
    all_comparisons = [compare_kk_level_to_benchmark(1, b) for b in KNOWN_HOLOGRAPHIC_BENCHMARKS]
    min_gap = min(abs(c["delta_gap"]) for c in all_comparisons)
    assert abs(result["delta_gap"]) == pytest.approx(min_gap)


def test_kk_dimensions_increase_with_n():
    comparisons = [compare_kk_level_to_benchmark(n, KNOWN_HOLOGRAPHIC_BENCHMARKS[0]) for n in range(1, 4)]
    deltas = [c["um_delta"] for c in comparisons]
    assert deltas == sorted(deltas)
    assert len(set(deltas)) == 3
