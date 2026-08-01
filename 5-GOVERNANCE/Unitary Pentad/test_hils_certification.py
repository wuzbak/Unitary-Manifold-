# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for HILS Certification Protocol v1.0."""

from __future__ import annotations

import os
import sys

import pytest

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from hils_certification import (
    HIL_PHASE_SHIFT_THRESHOLD,
    SENTINEL_CAPACITY,
    HILOperator,
    HILSCertificationPipeline,
)


@pytest.fixture()
def pipeline():
    return HILSCertificationPipeline()


def _operator(idx: int, score: float = 0.8, domain: str = "governance") -> HILOperator:
    return HILOperator(operator_id=f"op-{idx:02d}", domain=domain, alignment_score=score)


class TestOperatorDataclass:
    def test_fields_round_trip(self):
        operator = _operator(1, 0.9, "safety")
        assert operator.operator_id == "op-01"
        assert operator.domain == "safety"
        assert operator.alignment_score == pytest.approx(0.9)


class TestAlignmentCounting:
    @pytest.mark.parametrize("count", [0, 1, 2, 3, 4, 5, 6, 7])
    def test_counts_aligned_operators_below_pending(self, pipeline, count):
        for idx in range(count):
            pipeline.submit_operator(_operator(idx))
        assert pipeline.get_alignment_count() == count

    @pytest.mark.parametrize("count", [8, 9, 10, 11, 12, 13, 14, 15])
    def test_counts_aligned_operators_across_thresholds(self, pipeline, count):
        for idx in range(count):
            pipeline.submit_operator(_operator(idx))
        assert pipeline.get_alignment_count() == count

    def test_unaligned_operator_not_counted(self, pipeline):
        pipeline.submit_operator(_operator(1, 0.69))
        assert pipeline.get_alignment_count() == 0

    def test_duplicate_operator_replaces_entry(self, pipeline):
        pipeline.submit_operator(_operator(1, 0.9))
        pipeline.submit_operator(_operator(1, 0.6))
        assert pipeline.get_alignment_count() == 0


class TestCertificationStates:
    @pytest.mark.parametrize("count", range(0, 8))
    def test_insufficient_below_pending_band(self, pipeline, count):
        for idx in range(count):
            pipeline.submit_operator(_operator(idx))
        assert pipeline.certify() == "INSUFFICIENT"

    @pytest.mark.parametrize("count", range(8, 15))
    def test_pending_in_middle_band(self, pipeline, count):
        for idx in range(count):
            pipeline.submit_operator(_operator(idx))
        assert pipeline.certify() == "PENDING"

    @pytest.mark.parametrize("count", [15, 16, 17, 18, 19, 20])
    def test_certified_at_threshold_and_above(self, pipeline, count):
        for idx in range(count):
            pipeline.submit_operator(_operator(idx))
        assert pipeline.certify() == "CERTIFIED"


class TestEntropySaturation:
    @pytest.mark.parametrize("count", [0, 3, 6, 9, 12, 15])
    def test_entropy_saturation_fraction(self, pipeline, count):
        for idx in range(count):
            pipeline.submit_operator(_operator(idx))
        expected = min(count / HIL_PHASE_SHIFT_THRESHOLD, 1.0)
        assert pipeline.get_entropy_saturation() == pytest.approx(expected)

    def test_sentinel_capacity_constant(self):
        assert SENTINEL_CAPACITY == pytest.approx(12 / 37)


class TestCertificateReport:
    def test_certificate_contains_expected_keys(self, pipeline):
        cert = pipeline.get_certificate()
        for key in [
            "status",
            "threshold",
            "sentinel_capacity",
            "alignment_count",
            "operator_count",
            "entropy_saturation",
            "aligned_operator_ids",
            "operators",
        ]:
            assert key in cert

    def test_certificate_status_matches_pipeline(self, pipeline):
        for idx in range(15):
            pipeline.submit_operator(_operator(idx))
        cert = pipeline.get_certificate()
        assert cert["status"] == pipeline.certify()

    def test_certificate_aligned_ids_sorted(self, pipeline):
        for idx in [3, 1, 2]:
            pipeline.submit_operator(_operator(idx))
        cert = pipeline.get_certificate()
        assert cert["aligned_operator_ids"] == ["op-01", "op-02", "op-03"]

    def test_certificate_operator_count(self, pipeline):
        for idx in range(4):
            pipeline.submit_operator(_operator(idx))
        assert pipeline.get_certificate()["operator_count"] == 4

    def test_certificate_includes_operator_payload(self, pipeline):
        pipeline.submit_operator(_operator(1, 0.95, "medicine"))
        operator = pipeline.get_certificate()["operators"][0]
        assert operator["domain"] == "medicine"
