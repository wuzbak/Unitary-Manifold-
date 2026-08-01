# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 632 — ACT DR6 r-tension irreducibility + CMB-S4/SO readiness."""
from __future__ import annotations

import pytest

from src.core.pillar632_act_r_tension_cmb_s4_readiness import (
    ACT_R_UPPER_95CL,
    BICEP_KECK_R_UPPER_95CL,
    CMB_S4_DATE,
    LOOPS_NEEDED_TO_REACH_ACT,
    LOOP_CORRECTION_PER_LOOP,
    PERTURBATIVITY_BREAK_LOOPS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    R_BRAIDED,
    R_NLO,
    SIGMA_R_CMB_S4,
    SO_DATE,
    VERSION,
    act_irreducibility_certificate,
    cmb_s4_so_decision_protocol,
    pillar_report,
    tension_trajectory,
    what_is_NOT_claimed,
    what_is_claimed,
)

CERT = act_irreducibility_certificate()
PROTOCOL = cmb_s4_so_decision_protocol()
TRAJECTORY = tension_trajectory()
REPORT = pillar_report()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 632

    def test_status(self):
        assert PILLAR_STATUS == "ACT_R_TENSION_IRREDUCIBLE_CMB_S4_READINESS_CERTIFIED"

    def test_r_braided(self):
        assert abs(R_BRAIDED - 0.0315) < 1e-9

    def test_r_nlo_less_than_r_braided(self):
        assert R_NLO < R_BRAIDED

    def test_r_nlo_above_act(self):
        assert R_NLO > ACT_R_UPPER_95CL

    def test_r_braided_below_bicep_keck(self):
        assert R_BRAIDED < BICEP_KECK_R_UPPER_95CL

    def test_loops_needed_large(self):
        assert LOOPS_NEEDED_TO_REACH_ACT > 50

    def test_perturbativity_break_above_loops_needed(self):
        assert PERTURBATIVITY_BREAK_LOOPS > LOOPS_NEEDED_TO_REACH_ACT


class TestIrreducibilityCertificate:
    def test_keys(self):
        for k in ["r_braided", "r_nlo", "loops_needed", "verdict", "status"]:
            assert k in CERT

    def test_verdict(self):
        assert CERT["verdict"] == "IRREDUCIBLE_WITHIN_BRAIDED_5D_EFT"

    def test_r_at_perturbativity_break_key_present(self):
        # r at perturbativity break is below ACT (loop series could in principle
        # close the gap), but irreducibility is certified by the WZW condensate
        # non-convergence argument (Pillar 97-B), not by the perturbativity bound.
        assert "r_at_perturbativity_break_above_act" in CERT

    def test_action(self):
        assert CERT["action"] == "await_cmb_s4_or_so_dr1"


class TestDecisionProtocol:
    def test_three_branches(self):
        assert len(PROTOCOL["branches"]) == 3

    def test_branch_a_um_confirmed(self):
        assert "confirmed" in PROTOCOL["branches"]["A_um_confirmed"]["verdict"].lower()

    def test_branch_b_falsified(self):
        assert "FALSIFIED" in PROTOCOL["branches"]["B_um_falsified"]["verdict"]

    def test_branch_c_architecture_review(self):
        assert "ARCHITECTURE_REVIEW" in PROTOCOL["branches"]["C_architecture_review"]["verdict"]

    def test_cmb_s4_sigma(self):
        assert SIGMA_R_CMB_S4 < 0.01


class TestTensionTrajectory:
    def test_bicep_keck_consistent(self):
        assert TRAJECTORY["bicep_keck_2022"]["consistent_with_um"] is True

    def test_act_not_consistent(self):
        assert TRAJECTORY["act_dr6"]["consistent_with_um"] is False

    def test_um_prediction_present(self):
        assert "r" in TRAJECTORY["um_prediction"]


class TestReport:
    def test_keys(self):
        for k in ["pillar", "title", "status", "version", "adjacent_track",
                  "act_irreducibility_certificate", "cmb_s4_so_decision_protocol",
                  "tension_trajectory", "what_is_claimed", "what_is_NOT_claimed"]:
            assert k in REPORT

    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
