# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 712 — Simons Observatory DR1 drill."""
from __future__ import annotations

import re

import pytest

from src.core.pillar712_simons_obs_dr1_drill import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    R_UM,
    SO_SIGMA_R,
    so_dr1_mock_drill,
    so_dr1_readiness,
    so_preregistration,
)

READINESS = so_dr1_readiness()
MOCK = so_dr1_mock_drill()
PREREG = so_preregistration()


class TestConstants:
    def test_identity(self):
        assert PILLAR_NUMBER == 712
        assert PILLAR_STATUS == "SO_DR1_READINESS_DRILL_CERTIFIED"
        assert PILLAR_TITLE == "Simons Observatory DR1 Drill"

    def test_r_constant(self):
        assert R_UM == pytest.approx(0.0315)
        assert SO_SIGMA_R == pytest.approx(0.005)


class TestMockDrill:
    def test_default_mock_is_consistent(self):
        assert MOCK["branch"] == "CONSISTENT"
        assert MOCK["status"] == "CONSISTENT"
        assert MOCK["sigma_tension"] == pytest.approx(abs(0.028 - R_UM) / 0.006)

    def test_branch_a(self):
        result = so_dr1_mock_drill(0.018, 0.006)
        assert result["branch"] == "ACT_IRREDUCIBILITY_CONFIRMED"
        assert result["status"] == "TENSION"
        assert result["architecture_limit_triggered"] is True

    def test_branch_c(self):
        result = so_dr1_mock_drill(0.042, 0.006)
        assert result["branch"] == "FALSIFIED"
        assert result["status"] == "FALSIFIED"

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            so_dr1_mock_drill(0.028, 0.0)


class TestReadiness:
    def test_readiness_contains_routes(self):
        assert set(READINESS["routing"]) == {"A", "B", "C"}

    def test_readiness_embeds_mock(self):
        assert READINESS["mock_drill"]["branch"] == "CONSISTENT"


class TestPreregistration:
    def test_hash_shape(self):
        assert re.fullmatch(r"[0-9a-f]{64}", PREREG["sha256"]) is not None

    def test_prediction_string_mentions_um(self):
        assert "0.0315" in PREREG["prediction_string"]
