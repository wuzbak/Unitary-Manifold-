# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Shared fetch -> normalize -> fallback -> verdict harness — Phase 1 of
article-354 direction #13 ("Live-public-data pattern -> shared harness").

`src/data/fetch_planck.py` and `12-AZ-IP/21-geo-monitor/geo_monitor/engine/feeds.py`
and `12-AZ-IP/19-falsification-observatory`'s routing functions all repeat
the same shape by hand: attempt a live network fetch, normalize the raw
payload into a typed record, fall back to a known offline value when the
network call fails, and compare the resulting measured value against a
prediction to reach a verdict. This module extracts that shape into one
reusable harness.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class FetchSource(str, Enum):
    LIVE = "live"
    FALLBACK = "fallback"


@dataclass
class FetchResult(Generic[T]):
    """The outcome of a fetch-with-fallback attempt."""

    value: T
    source: FetchSource
    error: Optional[str] = None


def fetch_with_fallback(
    fetch_fn: Callable[[], T],
    fallback_value: T,
) -> FetchResult[T]:
    """Attempt `fetch_fn()`; on any exception, fall back to
    `fallback_value` and record why. Mirrors the pattern
    `fetch_planck.fetch_planck_bestfit()` implements implicitly (it
    never attempts a live call and always returns the hard-coded
    fallback) and `USGSFeedParser.fetch()` implements explicitly (a real
    `urlopen` call with no fallback on failure)."""
    try:
        value = fetch_fn()
        return FetchResult(value=value, source=FetchSource.LIVE, error=None)
    except Exception as exc:
        return FetchResult(value=fallback_value, source=FetchSource.FALLBACK, error=str(exc))


class VerdictLabel(str, Enum):
    CONSISTENT = "CONSISTENT"
    INCONSISTENT = "INCONSISTENT"
    AWAITING_DATA = "AWAITING_DATA"


@dataclass
class Verdict:
    """Generalizes `compute_um_residuals()`'s sigma-pull comparison and
    `falsification_observatory`'s routing-verdict shape into one record."""

    predicted: float
    measured: float
    sigma: Optional[float]
    residual: float
    sigma_pull: Optional[float]
    label: VerdictLabel
    note: str = ""


def compute_verdict(
    predicted: float,
    measured: Optional[float],
    sigma: Optional[float] = None,
    sigma_threshold: float = 2.0,
    note: str = "",
) -> Verdict:
    """Compare a prediction against a measured value.

    If `measured` is None, the verdict is AWAITING_DATA (mirrors
    `falsification_observatory.routing`'s no-args default behavior).
    If `sigma` is supplied, consistency is judged by sigma-pull against
    `sigma_threshold` (mirrors `fetch_planck.compute_um_residuals()`'s
    `ns_within_2sigma` check). Otherwise consistency falls back to an
    exact-sign/zero residual check.
    """
    if measured is None:
        return Verdict(
            predicted=predicted, measured=float("nan"), sigma=sigma,
            residual=float("nan"), sigma_pull=None,
            label=VerdictLabel.AWAITING_DATA, note=note or "no measurement available",
        )

    residual = measured - predicted
    if sigma is not None and sigma > 0:
        sigma_pull = residual / sigma
        label = VerdictLabel.CONSISTENT if abs(sigma_pull) < sigma_threshold else VerdictLabel.INCONSISTENT
    else:
        sigma_pull = None
        label = VerdictLabel.CONSISTENT if residual == 0 else VerdictLabel.INCONSISTENT

    return Verdict(
        predicted=predicted, measured=measured, sigma=sigma,
        residual=residual, sigma_pull=sigma_pull, label=label, note=note,
    )
