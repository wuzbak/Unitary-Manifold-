# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 824 — DESI DR3 Pre-Registration."""
from __future__ import annotations

import pytest

from src.core.pillar824_desi_dr3_preregistration import (
    DESI_DR2_TENSION_SIGMA,
    DESI_DR2_WA_CENTRAL,
    DESI_DR2_WA_SIGMA,
    DESI_DR3_PROTOCOL,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PREREGISTRATION_DATE,
    THRESHOLD_FALSIFIED,
    THRESHOLD_HIGH_TENSION,
    THRESHOLD_TENSION,
    UM_WA_PREDICTION,
    compute_tension_sigma,
    desi_dr3_verdict,
    evaluate_current_dr2_status,
    route_desi_verdict,
)


class TestPillar824Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 824

    def test_gate(self):
        assert PILLAR_GATE == "DESI_DR3_PREREGISTERED"

    def test_um_wa_prediction(self):
        assert UM_WA_PREDICTION == 0.0

    def test_threshold_ordering(self):
        assert THRESHOLD_TENSION < THRESHOLD_HIGH_TENSION < THRESHOLD_FALSIFIED

    def test_threshold_falsified(self):
        assert THRESHOLD_FALSIFIED == 5.0

    def test_threshold_high_tension(self):
        assert THRESHOLD_HIGH_TENSION == 3.0

    def test_threshold_tension(self):
        assert THRESHOLD_TENSION == 2.0

    def test_desi_dr2_tension(self):
        assert abs(DESI_DR2_TENSION_SIGMA - 2.75) < 0.01

    def test_preregistration_date(self):
        assert PREREGISTRATION_DATE == "2026-08-26"

    def test_lean4_count(self):
        assert LEAN4_THEOREM_COUNT == 15

    def test_lean4_total_before(self):
        assert LEAN4_TOTAL_BEFORE == 1491

    def test_lean4_total_after(self):
        assert LEAN4_TOTAL_AFTER == LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT


class TestComputeTensionSigma:
    def test_basic_computation(self):
        sigma = compute_tension_sigma(-0.62, 0.226)
        assert abs(sigma - 0.62 / 0.226) < 1e-6

    def test_zero_wa_gives_zero(self):
        """UM prediction exactly: tension = 0."""
        sigma = compute_tension_sigma(0.0, 1.0)
        assert sigma == 0.0

    def test_positive_wa_tension(self):
        sigma = compute_tension_sigma(0.5, 0.1)
        assert abs(sigma - 5.0) < 1e-10

    def test_negative_wa_tension(self):
        sigma = compute_tension_sigma(-1.0, 0.25)
        assert abs(sigma - 4.0) < 1e-10

    def test_raises_on_zero_sigma(self):
        with pytest.raises(ValueError):
            compute_tension_sigma(-0.5, 0.0)

    def test_raises_on_negative_sigma(self):
        with pytest.raises(ValueError):
            compute_tension_sigma(-0.5, -0.1)


class TestRouteDesiVerdict:
    def test_pass(self):
        assert route_desi_verdict(0.5) == "PASS"
        assert route_desi_verdict(1.9) == "PASS"

    def test_tension(self):
        assert route_desi_verdict(2.0) == "TENSION"
        assert route_desi_verdict(2.75) == "TENSION"
        assert route_desi_verdict(2.99) == "TENSION"

    def test_high_tension(self):
        assert route_desi_verdict(3.0) == "HIGH_TENSION"
        assert route_desi_verdict(4.5) == "HIGH_TENSION"
        assert route_desi_verdict(4.99) == "HIGH_TENSION"

    def test_falsified(self):
        assert route_desi_verdict(5.0) == "FALSIFIED"
        assert route_desi_verdict(6.0) == "FALSIFIED"

    def test_exactly_at_thresholds(self):
        assert route_desi_verdict(THRESHOLD_TENSION) == "TENSION"
        assert route_desi_verdict(THRESHOLD_HIGH_TENSION) == "HIGH_TENSION"
        assert route_desi_verdict(THRESHOLD_FALSIFIED) == "FALSIFIED"


class TestEvaluateDR2Status:
    def test_runs(self):
        result = evaluate_current_dr2_status()
        assert result is not None

    def test_wa_desi(self):
        result = evaluate_current_dr2_status()
        assert abs(result.wa_desi - DESI_DR2_WA_CENTRAL) < 1e-10

    def test_wa_sigma(self):
        result = evaluate_current_dr2_status()
        assert abs(result.wa_sigma - DESI_DR2_WA_SIGMA) < 1e-10

    def test_wa_um(self):
        result = evaluate_current_dr2_status()
        assert result.wa_um == UM_WA_PREDICTION

    def test_tension_sigma(self):
        result = evaluate_current_dr2_status()
        expected = abs(DESI_DR2_WA_CENTRAL) / DESI_DR2_WA_SIGMA
        assert abs(result.tension_sigma - expected) < 1e-6

    def test_verdict_is_tension(self):
        """DR2 status should be TENSION (2.75σ < 3.0σ HIGH_TENSION threshold)."""
        result = evaluate_current_dr2_status()
        assert result.verdict == "TENSION"

    def test_not_falsified(self):
        result = evaluate_current_dr2_status()
        assert result.verdict != "FALSIFIED"

    def test_pre_registered(self):
        result = evaluate_current_dr2_status()
        assert result.pre_registered is True


class TestDesiDR3Verdict:
    def test_verdict_runs_no_dr3(self):
        verdict = desi_dr3_verdict()
        assert verdict is not None

    def test_verdict_gate(self):
        verdict = desi_dr3_verdict()
        assert verdict["gate"] == PILLAR_GATE

    def test_verdict_pillar(self):
        verdict = desi_dr3_verdict()
        assert verdict["pillar"] == 824

    def test_verdict_preregistration_date(self):
        verdict = desi_dr3_verdict()
        assert verdict["preregistration_date"] == "2026-08-26"

    def test_verdict_um_prediction(self):
        verdict = desi_dr3_verdict()
        assert verdict["um_prediction_wa"] == 0.0

    def test_verdict_dr3_awaiting(self):
        verdict = desi_dr3_verdict()
        assert verdict["desi_dr3_status"] == "AWAITING_DATA"

    def test_verdict_routing_thresholds(self):
        verdict = desi_dr3_verdict()
        thresholds = verdict["routing_thresholds"]
        assert "FALSIFIED" in thresholds
        assert "HIGH_TENSION" in thresholds
        assert "TENSION" in thresholds
        assert "PASS" in thresholds

    def test_verdict_dr2_tension(self):
        verdict = desi_dr3_verdict()
        dr2 = verdict["desi_dr2_status"]
        assert dr2["verdict"] == "TENSION"

    def test_verdict_with_dr3_data_pass(self):
        """Simulate DR3 data consistent with UM (wₐ close to 0)."""
        verdict = desi_dr3_verdict(wa_dr3=0.1, wa_dr3_sigma=0.3)
        dr3 = verdict["desi_dr3_status"]
        assert isinstance(dr3, dict)
        assert dr3["verdict"] == "PASS"

    def test_verdict_with_dr3_data_high_tension(self):
        verdict = desi_dr3_verdict(wa_dr3=-1.0, wa_dr3_sigma=0.25)
        dr3 = verdict["desi_dr3_status"]
        assert dr3["verdict"] == "HIGH_TENSION"

    def test_verdict_with_dr3_data_falsified(self):
        verdict = desi_dr3_verdict(wa_dr3=-2.0, wa_dr3_sigma=0.3)
        dr3 = verdict["desi_dr3_status"]
        assert dr3["verdict"] == "FALSIFIED"

    def test_verdict_lean4(self):
        verdict = desi_dr3_verdict()
        assert verdict["lean4_theorems"] == 15
        assert verdict["lean4_total"] == 1506

    def test_verdict_observable(self):
        verdict = desi_dr3_verdict()
        assert "wₐ" in verdict["observable"] or "w_a" in verdict["observable"]


class TestDesiDR3ModuleSingleton:
    def test_protocol_exists(self):
        assert DESI_DR3_PROTOCOL is not None

    def test_protocol_gate(self):
        assert DESI_DR3_PROTOCOL["gate"] == PILLAR_GATE

    def test_protocol_pillar(self):
        assert DESI_DR3_PROTOCOL["pillar"] == 824
