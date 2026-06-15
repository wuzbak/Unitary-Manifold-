# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar368_so_dr1_joint_verdict.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar368_so_dr1_joint_verdict import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    R_UM_PREDICTION, SO_DR1_SIGMA_R, SO_FIVEYEAR_SIGMA_R,
    ACT_DR6_R_UPPER_BOUND, ACT_DR6_SIGMA_R,
    FALSIFICATION_R_THRESHOLD,
    separation_guard, detection_significance, so_dr1_joint_routing,
    joint_posterior_r, instrument_sensitivity_table,
    so_preregistration_checklist, pillar368_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 368
    def test_status(self): assert PILLAR_STATUS == "ROUTING_INFRASTRUCTURE"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_r_um_prediction(self): assert abs(R_UM_PREDICTION - 0.0315) < 1e-5
    def test_so_dr1_sigma(self): assert abs(SO_DR1_SIGMA_R - 0.006) < 1e-5
    def test_so_5yr_sigma(self): assert abs(SO_FIVEYEAR_SIGMA_R - 0.003) < 1e-5
    def test_falsification_threshold(self): assert abs(FALSIFICATION_R_THRESHOLD - 0.010) < 1e-5
    def test_act_dr6_bound(self): assert abs(ACT_DR6_R_UPPER_BOUND - 0.016) < 1e-5


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_mentions_routing(self): assert "ROUTING" in separation_guard().upper()


class TestDetectionSignificance:
    def test_zero_r_zero_sig(self): assert detection_significance(0.0, 0.1) == 0.0
    def test_5sigma_detection(self):
        sig = detection_significance(0.0315, 0.006)
        assert abs(sig - 5.25) < 0.1
    def test_zero_sigma_returns_zero(self): assert detection_significance(1.0, 0.0) == 0.0
    def test_positive_for_positive_r(self): assert detection_significance(0.01, 0.005) > 0


class TestSoDr1JointRouting:
    def test_returns_dict(self):
        r = so_dr1_joint_routing(0.0315, 0.006)
        assert isinstance(r, dict)

    def test_confirmed_at_um_prediction(self):
        r = so_dr1_joint_routing(0.0315, 0.006)
        assert r["verdict"] == "CONFIRMED"

    def test_falsified_at_low_r_3sigma(self):
        # r = 0.005, sigma = 0.003 → r + 3σ = 0.005 + 0.009 = 0.014 > 0.010
        # BUT lower_3sigma = 0.005 - 0.009 = -0.004 < 0.010 → FALSIFIED
        r = so_dr1_joint_routing(0.004, 0.003)
        assert r["verdict"] == "FALSIFIED"

    def test_consistent_at_upper_range(self):
        r = so_dr1_joint_routing(0.015, 0.008)
        assert r["verdict"] in ["CONSISTENT", "HIGH_TENSION", "TENSION"]

    def test_pillar_number_in_result(self):
        r = so_dr1_joint_routing(0.0315, 0.006)
        assert r["pillar"] == PILLAR_NUMBER

    def test_um_r_prediction_in_result(self):
        r = so_dr1_joint_routing(0.0315, 0.006)
        assert abs(r["um_r_prediction"] - R_UM_PREDICTION) < 1e-6

    def test_detection_significance_present(self):
        r = so_dr1_joint_routing(0.0315, 0.006)
        assert "detection_significance_sigma" in r

    def test_tension_from_um_present(self):
        r = so_dr1_joint_routing(0.0315, 0.006)
        assert "tension_from_um_sigma" in r

    def test_zero_tension_at_prediction(self):
        r = so_dr1_joint_routing(0.0315, 0.006)
        assert r["tension_from_um_sigma"] == 0.0

    def test_falsified_description_contains_word(self):
        r = so_dr1_joint_routing(0.004, 0.003)
        assert "FALSIFIED" in r["description"]


class TestJointPosteriorR:
    def test_single_measurement(self):
        p = joint_posterior_r([(0.0315, 0.006, 1.0)])
        assert abs(p["r_posterior"] - 0.0315) < 1e-4

    def test_two_equal_measurements(self):
        p = joint_posterior_r([(0.030, 0.006, 1.0), (0.033, 0.006, 1.0)])
        assert abs(p["r_posterior"] - 0.0315) < 0.002

    def test_empty_returns_none(self):
        p = joint_posterior_r([])
        assert p["r_posterior"] is None

    def test_sigma_shrinks_with_two(self):
        p1 = joint_posterior_r([(0.0315, 0.006, 1.0)])
        p2 = joint_posterior_r([(0.0315, 0.006, 1.0), (0.0315, 0.006, 1.0)])
        assert p2["sigma_posterior"] < p1["sigma_posterior"]

    def test_n_measurements_correct(self):
        p = joint_posterior_r([(0.0315, 0.006, 1.0), (0.0315, 0.006, 1.0)])
        assert p["n_measurements"] == 2


class TestInstrumentSensitivityTable:
    def test_returns_list(self): assert isinstance(instrument_sensitivity_table(), list)
    def test_at_least_4_instruments(self): assert len(instrument_sensitivity_table()) >= 4
    def test_so_dr1_present(self):
        names = [t["instrument"] for t in instrument_sensitivity_table()]
        assert any("Simons Observatory DR1" in n for n in names)
    def test_each_has_status(self):
        for t in instrument_sensitivity_table():
            assert "status" in t
    def test_act_dr6_high_tension(self):
        table = instrument_sensitivity_table()
        act = next(t for t in table if "ACT" in t["instrument"])
        assert "HIGH_TENSION" in act["status"] or "TENSION" in act["status"]


class TestPreregistrationChecklist:
    def test_returns_list(self): assert isinstance(so_preregistration_checklist(), list)
    def test_at_least_4_items(self): assert len(so_preregistration_checklist()) >= 4
    def test_each_has_item(self):
        for item in so_preregistration_checklist():
            assert "item" in item
    def test_each_has_status(self):
        for item in so_preregistration_checklist():
            assert "status" in item
    def test_open_item_for_so(self):
        items = so_preregistration_checklist()
        open_items = [i for i in items if "OPEN" in i["status"]]
        assert len(open_items) >= 1


class TestPillar368Summary:
    def test_pillar(self): assert pillar368_summary()["pillar"] == 368
    def test_status(self): assert pillar368_summary()["status"] == "ROUTING_INFRASTRUCTURE"
    def test_r_um_prediction(self): assert abs(pillar368_summary()["r_um_prediction"] - 0.0315) < 1e-5
    def test_preregistration_complete(self): assert pillar368_summary()["preregistration_complete"] is True
    def test_falsification_condition(self): assert "0.010" in pillar368_summary()["falsification_condition"]
