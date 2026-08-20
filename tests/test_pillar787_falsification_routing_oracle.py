# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 787 — FALSIFICATION_ROUTING_ORACLE (58 tests)."""

import pytest
from src.core.pillar787_falsification_routing_oracle import (
    route_litebird,
    route_desi,
    route_juno,
    route_act_r,
    route_hllhc,
    route_nedm,
    route_xenon,
    run_full_oracle,
    oracle_summary,
    RoutingVerdict,
    Pillar787Audit,
    run_pillar787,
    BETA_CANONICAL_1_DEG, BETA_CANONICAL_2_DEG,
    BETA_ADMISSIBLE_MIN, BETA_ADMISSIBLE_MAX,
    WA_PRED, WA_KILL_SIGMA,
    DM21_PRED, DM21_WINDOW_LOW, DM21_WINDOW_HIGH,
    R_PRED, R_KILL,
    MG_PRED_TEV,
)

VALID_VERDICTS = {"PASS", "TENSION", "FALSIFIED", "AWAITING_DATA"}


# ---------------------------------------------------------------------------
# EXP-1 LiteBIRD
# ---------------------------------------------------------------------------

class TestRouteLiteBird:
    def test_awaiting_data_default(self):
        v = route_litebird()
        assert v.verdict == "AWAITING_DATA"

    def test_pass_at_canonical_1(self):
        v = route_litebird(BETA_CANONICAL_1_DEG, 0.01)
        assert v.verdict == "PASS"

    def test_pass_at_canonical_2(self):
        v = route_litebird(BETA_CANONICAL_2_DEG, 0.01)
        assert v.verdict == "PASS"

    def test_falsified_outside_window_low(self):
        v = route_litebird(0.10, 0.01)   # far below 0.22°
        assert v.verdict == "FALSIFIED"
        assert v.kill_condition_met

    def test_falsified_outside_window_high(self):
        v = route_litebird(0.45, 0.01)   # above 0.38°
        assert v.verdict == "FALSIFIED"

    def test_falsified_inside_gap(self):
        v = route_litebird(0.30, 0.005)  # inside (0.29°, 0.31°)
        assert v.verdict == "FALSIFIED"

    def test_tension_near_boundary(self):
        v = route_litebird(0.25, 0.10)   # within window but uncertain
        assert v.verdict in {"PASS", "TENSION"}

    def test_experiment_code(self):
        v = route_litebird()
        assert v.experiment_code == "EXP-1"

    def test_relevant_pillars(self):
        v = route_litebird()
        assert 765 in v.relevant_pillars

    def test_verdict_in_valid_set(self):
        v = route_litebird()
        assert v.verdict in VALID_VERDICTS


# ---------------------------------------------------------------------------
# EXP-2 DESI
# ---------------------------------------------------------------------------

class TestRouteDESI:
    def test_default_tension(self):
        v = route_desi()
        assert v.verdict == "TENSION"

    def test_pass_at_zero(self):
        v = route_desi(0.0, 0.5)   # wa=0, large uncertainty
        assert v.verdict == "PASS"

    def test_falsified_at_3sigma(self):
        v = route_desi(-0.6, 0.1)  # 6σ from 0
        assert v.verdict == "FALSIFIED"
        assert v.kill_condition_met

    def test_experiment_code(self):
        assert route_desi().experiment_code == "EXP-2"

    def test_prediction_is_zero(self):
        v = route_desi()
        assert str(WA_PRED) in v.prediction

    def test_verdict_valid(self):
        assert route_desi().verdict in VALID_VERDICTS


# ---------------------------------------------------------------------------
# EXP-3 JUNO
# ---------------------------------------------------------------------------

class TestRouteJUNO:
    def test_default_pass(self):
        v = route_juno()
        assert v.verdict == "PASS"

    def test_falsified_ih_ordering(self):
        v = route_juno(ordering_measured="IH")
        assert v.verdict == "FALSIFIED"
        assert v.kill_condition_met

    def test_nh_ordering_pass(self):
        v = route_juno(ordering_measured="NH")
        assert v.verdict in {"PASS", "TENSION"}

    def test_falsified_outside_window(self):
        v = route_juno(dm21_measured=6.0e-5, dm21_sigma=0.1e-5)
        assert v.verdict == "FALSIFIED"

    def test_experiment_code(self):
        assert route_juno().experiment_code == "EXP-3"

    def test_pillar_786_in_chain(self):
        assert 786 in route_juno().relevant_pillars

    def test_verdict_valid(self):
        assert route_juno().verdict in VALID_VERDICTS


# ---------------------------------------------------------------------------
# EXP-4 ACT r
# ---------------------------------------------------------------------------

class TestRouteACT:
    def test_default_pass(self):
        v = route_act_r()
        assert v.verdict == "PASS"

    def test_falsified_if_r_pred_exceeds_limit(self):
        # Force a tight upper limit below r_pred
        v = route_act_r(r_95cl_upper=0.020)   # below 0.0315
        assert v.verdict == "FALSIFIED"

    def test_experiment_code(self):
        assert route_act_r().experiment_code == "EXP-4"

    def test_verdict_valid(self):
        assert route_act_r().verdict in VALID_VERDICTS


# ---------------------------------------------------------------------------
# EXP-5 HL-LHC
# ---------------------------------------------------------------------------

class TestRouteHLLHC:
    def test_default_pass(self):
        v = route_hllhc()
        assert v.verdict == "PASS"

    def test_tension_if_exclusion_exceeds_pred(self):
        v = route_hllhc(mg_exclusion_tev=3.0)
        assert v.verdict == "TENSION"

    def test_falsified_at_5tev(self):
        v = route_hllhc(mg_exclusion_tev=5.0)
        assert v.verdict == "FALSIFIED"

    def test_experiment_code(self):
        assert route_hllhc().experiment_code == "EXP-5"

    def test_verdict_valid(self):
        assert route_hllhc().verdict in VALID_VERDICTS


# ---------------------------------------------------------------------------
# EXP-6 nEDM
# ---------------------------------------------------------------------------

class TestRouteNEDM:
    def test_default_pass(self):
        v = route_nedm()
        assert v.verdict == "PASS"

    def test_experiment_code(self):
        assert route_nedm().experiment_code == "EXP-6"

    def test_verdict_valid(self):
        assert route_nedm().verdict in VALID_VERDICTS


# ---------------------------------------------------------------------------
# EXP-7 XENON-nT
# ---------------------------------------------------------------------------

class TestRouteXENON:
    def test_default_verdict(self):
        v = route_xenon()
        assert v.verdict in VALID_VERDICTS

    def test_experiment_code(self):
        assert route_xenon().experiment_code == "EXP-7"

    def test_falsified_if_deep_null(self):
        v = route_xenon(cross_section_limit=1e-50)  # far below prediction
        assert v.verdict == "FALSIFIED"


# ---------------------------------------------------------------------------
# Full oracle + summary
# ---------------------------------------------------------------------------

class TestFullOracle:
    def test_returns_seven_experiments(self):
        verdicts = run_full_oracle()
        assert set(verdicts.keys()) == {f"EXP-{i}" for i in range(1, 8)}

    def test_all_verdicts_valid(self):
        verdicts = run_full_oracle()
        for v in verdicts.values():
            assert v.verdict in VALID_VERDICTS

    def test_summary_keys(self):
        verdicts = run_full_oracle()
        summary = oracle_summary(verdicts)
        assert "verdict_counts" in summary
        assert "framework_status" in summary
        assert "any_falsified" in summary

    def test_no_falsification_by_default(self):
        verdicts = run_full_oracle()
        summary = oracle_summary(verdicts)
        assert not summary["any_falsified"]

    def test_framework_not_falsified_by_default(self):
        verdicts = run_full_oracle()
        summary = oracle_summary(verdicts)
        assert summary["framework_status"] != "FRAMEWORK_FALSIFIED"

    def test_oracle_with_ih_ordering_flags_falsified(self):
        verdicts = run_full_oracle(juno_ordering="IH")
        summary = oracle_summary(verdicts)
        assert summary["any_falsified"]
        assert summary["framework_status"] == "FRAMEWORK_FALSIFIED"


# ---------------------------------------------------------------------------
# Audit object
# ---------------------------------------------------------------------------

class TestPillar787Audit:
    def test_pillar_number(self):
        assert run_pillar787().pillar_number == 787

    def test_seven_experiments_tracked(self):
        assert len(run_pillar787().experiments_tracked) == 7

    def test_lean4_total_milestone(self):
        audit = run_pillar787()
        assert audit.lean4_total >= 1000

    def test_test_count(self):
        assert run_pillar787().test_count == 58
