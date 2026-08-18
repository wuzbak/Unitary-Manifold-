# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 655 — JUNO 2027 final countdown package."""
from __future__ import annotations

import pytest

from src.core.pillar655_juno_2027_final_countdown_package import (
    ADJACENT_TRACK,
    DM31_JUNO_EV2,
    DM31_PDG_EV2,
    DM31_TENSION_FINAL,
    DM31_UM_EV2,
    DM31_WINDOW_HIGH,
    DM31_WINDOW_LOW,
    DUNE_CP_DELTA_RAD,
    JUNO_PHASE2_PRECISION,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    dune_cp_joint_verdict,
    juno_phase2_verdict,
    pillar_report,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
JUNO_PASS = juno_phase2_verdict(2.41095e-3)
JUNO_TENSION = juno_phase2_verdict(2.4250e-3)
JUNO_FAIL = juno_phase2_verdict(2.5000e-3)
DUNE_PASS = dune_cp_joint_verdict(1.22, 0.1)
DUNE_TENSION = dune_cp_joint_verdict(1.6, 0.2)
DUNE_FAIL = dune_cp_joint_verdict(2.5, 0.2)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 655

    def test_status(self):
        assert PILLAR_STATUS == 'JUNO_2027_FINAL_COUNTDOWN_PREREGISTERED'

    def test_version(self):
        assert VERSION == 'v21.0'

    def test_dm31_values(self):
        assert DM31_WINDOW_LOW < DM31_UM_EV2 < DM31_WINDOW_HIGH
        assert DM31_WINDOW_LOW < DM31_PDG_EV2 < DM31_WINDOW_HIGH
        assert DM31_WINDOW_LOW < DM31_JUNO_EV2 < DM31_WINDOW_HIGH

    def test_precision(self):
        assert JUNO_PHASE2_PRECISION == pytest.approx(0.005)

    def test_tension_final_nonnegative(self):
        assert DM31_TENSION_FINAL >= 0.0

    def test_adjacent_track(self):
        assert ADJACENT_TRACK is False


class TestFunctions:
    def test_juno_pass_branch(self):
        assert JUNO_PASS['branch'] == 'CLOSED_CONFIRMED'
        assert JUNO_PASS['sigma_tension'] < 1.0

    def test_juno_tension_branch(self):
        assert JUNO_TENSION['branch'] == 'TENSION'
        assert 1.0 <= JUNO_TENSION['sigma_tension'] < 3.0

    def test_juno_falsified_branch(self):
        assert JUNO_FAIL['branch'] == 'FALSIFIED'
        assert JUNO_FAIL['sigma_tension'] >= 3.0

    def test_juno_outside_window(self):
        verdict = juno_phase2_verdict(2.8e-3)
        assert verdict['outside_window'] is True
        assert verdict['branch'] == 'FALSIFIED'

    def test_juno_invalid_precision(self):
        with pytest.raises(ValueError):
            juno_phase2_verdict(DM31_UM_EV2, 0.0)

    def test_dune_pass_branch(self):
        assert DUNE_PASS['branch'] == 'CLOSED_CONFIRMED'

    def test_dune_tension_branch(self):
        assert DUNE_TENSION['branch'] == 'TENSION'

    def test_dune_falsified_branch(self):
        assert DUNE_FAIL['branch'] == 'FALSIFIED'

    def test_dune_prediction_constant(self):
        assert DUNE_PASS['delta_cp_um_rad'] == pytest.approx(DUNE_CP_DELTA_RAD)

    def test_dune_invalid_sigma(self):
        with pytest.raises(ValueError):
            dune_cp_joint_verdict(1.2, 0.0)


class TestReport:
    def test_report_keys(self):
        for key in [
            'pillar', 'title', 'status', 'version', 'adjacent_track',
            'dm31_um_ev2', 'dm31_pdg_ev2', 'dm31_juno_ev2',
            'dm31_tension_final_sigma', 'juno_phase2_precision',
            'dune_cp_delta_rad', 'what_is_claimed', 'what_is_NOT_claimed',
            'toe_score_delta', 'hardgate_score_delta',
        ]:
            assert key in REPORT

    def test_toe_delta(self):
        assert REPORT['toe_score_delta'] == 0.0
        assert REPORT['hardgate_score_delta'] == 0.0

    def test_claim_lists(self):
        assert len(what_is_claimed()) >= 5
        assert len(what_is_NOT_claimed()) >= 4
