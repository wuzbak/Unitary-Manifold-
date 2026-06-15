# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 525 — JUNO Phase 1 Formal Response (2026-06-12).

Status: JUNO_PHASE1_CONSISTENT
"""

from __future__ import annotations

import math
import pytest

from src.core.pillar525_juno_phase1_response import (
    JUNO_NORMAL_ORDERING_SIGMA,
    JUNO_PHASE1_ARXIV,
    JUNO_PHASE1_DATE,
    JUNO_PHASE1_PRECISION_DM31_PCT,
    JUNO_PHASE1_PRECISION_SOLAR_PCT,
    JUNO_SOLAR_REACTOR_TENSION_SIGMA,
    PDG_DM21,
    PDG_DM31,
    PDG_THETA12_SIN2,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    UM_DM21_PRED,
    UM_DM31_BASELINE,
    UM_DM31_NLO,
    UM_THETA12_DEG,
    UM_THETA12_SIN2,
    UM_THETA23_DEG,
    full_phase1_verdict,
    juno_phase1_dm21_verdict,
    juno_phase1_dm31_verdict,
    juno_phase1_ordering_verdict,
    juno_phase1_theta12_verdict,
    juno_solar_reactor_routing,
    pillar525_report,
)


# ── Module metadata ────────────────────────────────────────────────────────────

class TestPillarMetadata:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 525

    def test_pillar_status(self):
        assert PILLAR_STATUS == "JUNO_PHASE1_CONSISTENT"

    def test_pillar_title_contains_juno(self):
        assert "JUNO" in PILLAR_TITLE

    def test_pillar_date(self):
        assert JUNO_PHASE1_DATE == "2026-06-12"

    def test_arxiv_reference(self):
        assert JUNO_PHASE1_ARXIV == "2511.14590"


# ── UM prediction constants ────────────────────────────────────────────────────

class TestUMPredictions:
    def test_dm21_prediction_positive(self):
        assert UM_DM21_PRED > 0

    def test_dm21_close_to_pdg(self):
        residual = abs(UM_DM21_PRED - PDG_DM21) / PDG_DM21
        assert residual < 0.01, f"Δm²₂₁ residual {residual:.4%} too large"

    def test_dm31_baseline_in_range(self):
        assert 2.3e-3 < UM_DM31_BASELINE < 2.5e-3

    def test_dm31_nlo_close_to_pdg(self):
        residual = abs(UM_DM31_NLO - PDG_DM31) / PDG_DM31
        assert residual < 0.001, f"Δm²₃₁ NLO residual {residual:.6%} too large"

    def test_theta12_sin2_in_physical_range(self):
        assert 0.0 < UM_THETA12_SIN2 < 1.0

    def test_theta12_deg_consistent_with_sin2(self):
        computed = math.degrees(math.asin(math.sqrt(UM_THETA12_SIN2)))
        assert abs(computed - UM_THETA12_DEG) < 1e-9

    def test_theta23_in_octant(self):
        assert 40.0 < UM_THETA23_DEG < 55.0

    def test_normal_ordering_preference_positive(self):
        assert JUNO_NORMAL_ORDERING_SIGMA > 0

    def test_solar_reactor_tension_positive(self):
        assert JUNO_SOLAR_REACTOR_TENSION_SIGMA > 0


# ── Δm²₂₁ verdict ─────────────────────────────────────────────────────────────

class TestDm21Verdict:
    def setup_method(self):
        self.v = juno_phase1_dm21_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_observable_key(self):
        assert self.v["observable"] == "delta_m2_21"

    def test_um_prediction_matches_constant(self):
        assert self.v["um_prediction_eV2"] == UM_DM21_PRED

    def test_residual_pct_small(self):
        assert self.v["residual_pct"] < 1.0

    def test_sigma_value_within_juno_precision(self):
        assert self.v["sigma"] < 2.0

    def test_verdict_consistent(self):
        assert self.v["verdict"] == "CONSISTENT"

    def test_note_present(self):
        assert "note" in self.v
        assert len(self.v["note"]) > 0


# ── Δm²₃₁ verdict ─────────────────────────────────────────────────────────────

class TestDm31Verdict:
    def setup_method(self):
        self.v = juno_phase1_dm31_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_observable_key(self):
        assert self.v["observable"] == "delta_m2_31"

    def test_baseline_residual_large(self):
        # 2.18% baseline residual
        assert self.v["residual_baseline_pct"] > 1.5

    def test_nlo_residual_small(self):
        # NLO residual < 0.1%
        assert self.v["residual_nlo_pct"] < 0.1

    def test_nlo_sigma_well_inside_window(self):
        # At Phase 1 1% precision, NLO residual ~0.04σ
        assert self.v["sigma_nlo"] < 1.0

    def test_verdict_not_falsified(self):
        assert self.v["verdict"] in ("CONSISTENT", "MONITOR")

    def test_decision_window_flagged(self):
        assert "2027" in self.v["decision_window"]

    def test_note_mentions_decision_grade(self):
        assert "decision" in self.v["note"].lower()


# ── θ₁₂ verdict ───────────────────────────────────────────────────────────────

class TestTheta12Verdict:
    def setup_method(self):
        self.v = juno_phase1_theta12_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_observable_key(self):
        assert self.v["observable"] == "sin2_theta12"

    def test_um_prediction_matches_constant(self):
        assert abs(self.v["um_prediction"] - UM_THETA12_SIN2) < 1e-8

    def test_residual_pct_positive(self):
        assert self.v["residual_pct"] > 0

    def test_solar_reactor_tension_recorded(self):
        assert "solar_reactor_tension_sigma" in self.v
        assert self.v["solar_reactor_tension_sigma"] > 0

    def test_routing_pillar_is_533(self):
        assert self.v["routing_pillar"] == 533

    def test_verdict_not_falsified(self):
        assert self.v["verdict"] not in ("FALSIFIED", "RISK_FALSIFICATION")


# ── Mass ordering verdict ──────────────────────────────────────────────────────

class TestOrderingVerdict:
    def setup_method(self):
        self.v = juno_phase1_ordering_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_observable_key(self):
        assert self.v["observable"] == "mass_ordering"

    def test_um_predicts_normal(self):
        assert self.v["um_prediction"] == "NORMAL"

    def test_juno_prefers_normal(self):
        assert self.v["juno_phase1_preference"] == "NORMAL"

    def test_consistent(self):
        assert self.v["consistent"] is True

    def test_verdict_consistent(self):
        assert self.v["verdict"] == "CONSISTENT"

    def test_preference_sigma_above_2(self):
        assert self.v["juno_preference_sigma"] >= 2.0

    def test_derivation_pillar_is_60(self):
        assert self.v["derivation_pillar"] == 60


# ── Solar-reactor routing ──────────────────────────────────────────────────────

class TestSolarReactorRouting:
    def setup_method(self):
        self.r = juno_solar_reactor_routing()

    def test_returns_dict(self):
        assert isinstance(self.r, dict)

    def test_um_sin2_matches_constant(self):
        assert abs(self.r["um_sin2_theta12"] - UM_THETA12_SIN2) < 1e-5

    def test_reactor_pdg_sin2_in_range(self):
        assert 0.28 < self.r["reactor_pdg_sin2"] < 0.33

    def test_solar_msw_higher_than_reactor(self):
        assert self.r["solar_msw_sin2"] > self.r["reactor_pdg_sin2"]

    def test_solar_reactor_delta_positive(self):
        assert self.r["solar_reactor_delta_sin2"] > 0

    def test_reactor_residual_smaller_than_solar_residual(self):
        # UM is closer to the reactor value
        assert self.r["residual_vs_reactor_pct"] < self.r["residual_vs_solar_pct"]

    def test_correct_comparison_is_reactor(self):
        assert self.r["correct_comparison_target"] == "REACTOR"

    def test_verdict_reactor_comparison(self):
        assert "REACTOR" in self.r["verdict"]

    def test_pillar_533_action_present(self):
        assert "pillar_533_action" in self.r
        assert "MSW" in self.r["pillar_533_action"]


# ── Full Phase 1 verdict ───────────────────────────────────────────────────────

class TestFullPhase1Verdict:
    def setup_method(self):
        self.v = full_phase1_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_pillar_number(self):
        assert self.v["pillar"] == PILLAR_NUMBER

    def test_overall_not_falsified(self):
        assert self.v["overall_verdict"] not in ("RISK_FALSIFICATION", "FALSIFIED")

    def test_contains_all_observables(self):
        for key in ("dm21", "dm31", "theta12", "ordering", "solar_reactor_routing"):
            assert key in self.v

    def test_summary_present(self):
        assert "summary" in self.v
        assert len(self.v["summary"]) > 50

    def test_next_action_juno_2027(self):
        assert "2027" in self.v["next_action"]

    def test_pillar_533_pending(self):
        assert self.v["pillar_533_pending"] is True

    def test_date_matches(self):
        assert self.v["date"] == JUNO_PHASE1_DATE

    def test_arxiv_reference(self):
        assert self.v["arxiv"] == JUNO_PHASE1_ARXIV


# ── pillar525_report ───────────────────────────────────────────────────────────

class TestPillar525Report:
    def setup_method(self):
        self.r = pillar525_report()

    def test_returns_dict(self):
        assert isinstance(self.r, dict)

    def test_pillar_number(self):
        assert self.r["pillar"] == 525

    def test_status(self):
        assert self.r["status"] == "JUNO_PHASE1_CONSISTENT"

    def test_juno_phase1_verdict_present(self):
        assert "juno_phase1_verdict" in self.r

    def test_juno_phase1_verdict_is_dict(self):
        assert isinstance(self.r["juno_phase1_verdict"], dict)

    def test_overall_not_falsified(self):
        assert self.r["juno_phase1_verdict"]["overall_verdict"] not in (
            "RISK_FALSIFICATION",
            "FALSIFIED",
        )


# ── Edge-case and physics sanity ───────────────────────────────────────────────

class TestPhysicsSanity:
    def test_dm31_nlo_closer_to_pdg_than_baseline(self):
        res_base = abs(UM_DM31_BASELINE - PDG_DM31) / PDG_DM31
        res_nlo = abs(UM_DM31_NLO - PDG_DM31) / PDG_DM31
        assert res_nlo < res_base, "NLO should be tighter than baseline"

    def test_um_theta12_below_pdg(self):
        # Route A gives 1.55% below PDG — should be below
        assert UM_THETA12_SIN2 < PDG_THETA12_SIN2

    def test_juno_precision_dm31_at_one_pct(self):
        assert 0.5 < JUNO_PHASE1_PRECISION_DM31_PCT <= 1.5

    def test_juno_solar_precision_sub_pct(self):
        assert JUNO_PHASE1_PRECISION_SOLAR_PCT < 1.0

    def test_normal_ordering_sigma_above_two(self):
        assert JUNO_NORMAL_ORDERING_SIGMA >= 2.0

    def test_dm21_pred_matches_pdg_exactly(self):
        # WS-III +52 closure reproduces PDG exactly at this precision
        assert abs(UM_DM21_PRED - PDG_DM21) < 1e-8
