# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_live_data_harness import (
    FetchSource,
    fetch_with_fallback,
    VerdictLabel,
    compute_verdict,
    fetch_planck_n_s_via_harness,
    planck_n_s_verdict,
)


def test_fetch_with_fallback_returns_live_on_success():
    result = fetch_with_fallback(lambda: 42, fallback_value=0)
    assert result.value == 42
    assert result.source == FetchSource.LIVE
    assert result.error is None


def test_fetch_with_fallback_returns_fallback_on_failure():
    def _boom():
        raise RuntimeError("network down")

    result = fetch_with_fallback(_boom, fallback_value=99)
    assert result.value == 99
    assert result.source == FetchSource.FALLBACK
    assert "network down" in result.error


def test_compute_verdict_awaiting_data_when_measured_none():
    verdict = compute_verdict(predicted=1.0, measured=None)
    assert verdict.label == VerdictLabel.AWAITING_DATA


def test_compute_verdict_consistent_within_sigma():
    verdict = compute_verdict(predicted=1.0, measured=1.01, sigma=0.1)
    assert verdict.label == VerdictLabel.CONSISTENT
    assert verdict.sigma_pull == pytest.approx(0.1)


def test_compute_verdict_inconsistent_beyond_sigma():
    verdict = compute_verdict(predicted=1.0, measured=2.0, sigma=0.1, sigma_threshold=2.0)
    assert verdict.label == VerdictLabel.INCONSISTENT


def test_compute_verdict_without_sigma_uses_exact_residual():
    assert compute_verdict(predicted=1.0, measured=1.0).label == VerdictLabel.CONSISTENT
    assert compute_verdict(predicted=1.0, measured=1.5).label == VerdictLabel.INCONSISTENT


def test_fetch_planck_n_s_via_harness_falls_back_in_sandbox():
    # Network access is blocked in this sandboxed environment, so the
    # harness must genuinely exercise its fallback path here.
    result = fetch_planck_n_s_via_harness()
    assert result.source == FetchSource.FALLBACK
    assert result.value == pytest.approx(0.9649)


def test_planck_n_s_verdict_matches_known_sigma_pull():
    verdict = planck_n_s_verdict(um_ns=0.9635)
    expected_pull = (0.9649 - 0.9635) / 0.0042
    assert verdict.sigma_pull == pytest.approx(expected_pull, rel=1e-6)
    assert verdict.label == VerdictLabel.CONSISTENT
