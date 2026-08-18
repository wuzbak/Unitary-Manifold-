# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 713 — JUNO Phase 2 2027 drill."""
from __future__ import annotations

import pytest

from src.core.pillar713_juno_phase2_2027_drill import (
    DM31_UM_EV2,
    JUNO_SIGMA_EV2,
    PDG_DM31_EV2,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    dm31_um_tension_juno,
    juno_2027_verdict_projection,
    juno_phase2_drill,
)

TENSION = dm31_um_tension_juno()
DRILL = juno_phase2_drill()
PROJECTION = juno_2027_verdict_projection()


class TestConstants:
    def test_identity(self):
        assert PILLAR_NUMBER == 713
        assert PILLAR_STATUS == "JUNO_PHASE2_2027_DRILL_CERTIFIED"
        assert PILLAR_TITLE == "JUNO Phase 2 2027 Drill"

    def test_values(self):
        assert DM31_UM_EV2 == pytest.approx(2.4109e-3)
        assert PDG_DM31_EV2 == pytest.approx(2.453e-3)
        assert JUNO_SIGMA_EV2 == pytest.approx(0.012e-3)


class TestTension:
    def test_projected_tension(self):
        assert TENSION["tension_sigma"] == pytest.approx((PDG_DM31_EV2 - DM31_UM_EV2) / JUNO_SIGMA_EV2)
        assert TENSION["status"] == "TENSION"
        assert TENSION["inside_two_sigma_window"] is False
        assert TENSION["would_fail_live_3sigma_cut"] is True

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            dm31_um_tension_juno(PDG_DM31_EV2, 0.0)


class TestDrill:
    def test_drill_status(self):
        assert DRILL["status"] == "TENSION"
        assert DRILL["inside_two_sigma_window"] is False

    def test_two_sigma_window_values(self):
        low, high = DRILL["two_sigma_window"]
        assert low == pytest.approx(2.429e-3)
        assert high == pytest.approx(2.477e-3)


class TestProjection:
    def test_survival_window(self):
        low, high = PROJECTION["survival_window_3sigma"]
        assert low == pytest.approx(DM31_UM_EV2 - 3 * JUNO_SIGMA_EV2)
        assert high == pytest.approx(DM31_UM_EV2 + 3 * JUNO_SIGMA_EV2)

    def test_current_pdg_not_in_um_window(self):
        assert PROJECTION["current_pdg_central_inside_window"] is False
