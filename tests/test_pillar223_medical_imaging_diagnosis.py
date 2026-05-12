# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar223_medical_imaging_diagnosis.py — Pillar 223 test suite."""
import pytest

from src.core.pillar223_medical_imaging_diagnosis import (
    N_W,
    K_CS,
    PHI0,
    SOUND_SPEED_SOFT_TISSUE,
    CT_RISK_PER_MSV_ADULT,
    ultrasound_axial_resolution,
    ct_effective_risk,
    bayes_ppv_npv,
    fused_diagnostic_probability,
    diagnostic_triage,
    cross_pillar_alignment_score,
    pillar223_summary,
)


class TestConstants:
    def test_core(self):
        assert N_W == 5
        assert K_CS == 74
        assert abs(PHI0 - 0.739085) < 1e-6

    def test_imaging_constants(self):
        assert SOUND_SPEED_SOFT_TISSUE == 1540.0
        assert CT_RISK_PER_MSV_ADULT > 0


class TestUltrasoundResolution:
    def test_resolution_positive(self):
        r = ultrasound_axial_resolution(5.0, 0.6)
        assert r["axial_resolution_mm"] > 0

    def test_higher_freq_better_resolution(self):
        low = ultrasound_axial_resolution(3.0, 0.6)["axial_resolution_mm"]
        high = ultrasound_axial_resolution(10.0, 0.6)["axial_resolution_mm"]
        assert high < low

    def test_invalid_bandwidth_raises(self):
        with pytest.raises(ValueError):
            ultrasound_axial_resolution(5.0, 0.0)


class TestCtRisk:
    def test_risk_nonnegative(self):
        r = ct_effective_risk(5.0, 40.0)
        assert r["estimated_excess_cancer_risk"] >= 0

    def test_higher_dose_higher_risk(self):
        r1 = ct_effective_risk(2.0, 40.0)["estimated_excess_cancer_risk"]
        r2 = ct_effective_risk(8.0, 40.0)["estimated_excess_cancer_risk"]
        assert r2 > r1

    def test_younger_higher_risk(self):
        y = ct_effective_risk(5.0, 12.0)["estimated_excess_cancer_risk"]
        o = ct_effective_risk(5.0, 70.0)["estimated_excess_cancer_risk"]
        assert y > o


class TestBayes:
    def test_ppv_npv_range(self):
        r = bayes_ppv_npv(0.1, 0.9, 0.9)
        assert 0 <= r["ppv"] <= 1
        assert 0 <= r["npv"] <= 1

    def test_low_prevalence_low_ppv(self):
        r = bayes_ppv_npv(0.01, 0.9, 0.9)
        assert r["ppv"] < 0.2

    def test_high_prevalence_high_ppv(self):
        r = bayes_ppv_npv(0.5, 0.9, 0.9)
        assert r["ppv"] > 0.8


class TestFusionAndTriage:
    def test_fused_probability_in_range(self):
        f = fused_diagnostic_probability({"us": 0.6, "mri": 0.8, "lab": 0.7})
        assert 0 <= f["fused_probability"] <= 1

    def test_weighted_fusion(self):
        f = fused_diagnostic_probability({"a": 0.2, "b": 0.8}, {"a": 1.0, "b": 3.0})
        assert f["fused_probability"] > 0.5

    def test_triage_urgent_for_critical(self):
        t = diagnostic_triage(0.1, 0.99, 0.9)
        assert t["action"] == "urgent_imaging_and_specialist_review"

    def test_triage_watchful(self):
        t = diagnostic_triage(0.15, 0.97, 0.2)
        assert t["action"] == "watchful_waiting_with_followup"

    def test_cross_pillar_alignment_range(self):
        a = cross_pillar_alignment_score(0.8, 35.0, 0.7)
        assert 0 <= a["alignment_score"] <= 1

    def test_higher_mi_reduces_safety(self):
        low = cross_pillar_alignment_score(0.5, 35.0, 0.7)["safety_component"]
        high = cross_pillar_alignment_score(1.8, 35.0, 0.7)["safety_component"]
        assert high < low


class TestSummary:
    def test_summary_shape(self):
        s = pillar223_summary()
        assert s["pillar"] == 223
        assert 0 <= s["fused_probability_example"] <= 1
        assert 0 <= s["cross_pillar_alignment_score"] <= 1
        assert isinstance(s["epistemic_note"], str)
