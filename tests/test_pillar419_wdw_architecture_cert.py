# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 419 — WdW architecture limit certificate."""
import math
import pytest

from src.core.pillar419_wdw_architecture_cert import (
    PILLAR_STATUS,
    T3_STATUS,
    wdw_superspace_dimension,
    kk_truncation_error,
    t3_architecture_limit_certificate,
    wdw_closing_mechanism,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'ARCHITECTURE_LIMIT_WDW'

    def test_t3_status(self):
        assert T3_STATUS == 'ARCHITECTURE_LIMIT_WDW'


class TestWdwSuperspaceDimension:
    def test_truncated_dimension(self):
        assert wdw_superspace_dimension() == 3

    def test_full_dimension_infinite(self):
        assert math.isinf(wdw_superspace_dimension(False))


class TestKkTruncationError:
    def test_positive(self):
        assert kk_truncation_error() > 0

    def test_tiny(self):
        assert kk_truncation_error() < 1e-30

    def test_expected_scale(self):
        assert kk_truncation_error() == pytest.approx((1040.0 / 1.22e19) ** 2)


class TestClosingMechanism:
    def test_returns_string(self):
        assert isinstance(wdw_closing_mechanism(), str)

    def test_mentions_full_5d(self):
        assert 'Full 5D canonical quantization' in wdw_closing_mechanism()


class TestCertificate:
    def test_returns_dict(self):
        assert isinstance(t3_architecture_limit_certificate(), dict)

    def test_status(self):
        assert t3_architecture_limit_certificate()['status'] == 'ARCHITECTURE_LIMIT_WDW'

    def test_dimensions(self):
        cert = t3_architecture_limit_certificate()
        assert cert['truncated_dimension'] == 3
        assert math.isinf(cert['full_dimension'])

    def test_error_matches_function(self):
        assert t3_architecture_limit_certificate()['kk_truncation_error'] == pytest.approx(kk_truncation_error())

    def test_mechanism_matches_function(self):
        assert t3_architecture_limit_certificate()['closing_mechanism'] == wdw_closing_mechanism()

    def test_certificate_mentions_architectural_limit(self):
        assert 'architectural limit' in t3_architecture_limit_certificate()['certificate'].lower()
