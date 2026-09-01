# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 841 — 6D baryogenesis neutron-EDM tightening."""
from __future__ import annotations

import math

import pytest

from src.core.pillar841_6d_baryogenesis_dn_prediction import (
    D_N_CENTRAL_ECM,
    D_N_LOWER_ECM,
    D_N_UNCERTAINTY_FRAC,
    D_N_UPPER_ECM,
    GATE,
    LEAN4_COUNT,
    LEAN4_PRIOR,
    LEAN4_TOTAL,
    M_SIGMA_GEV,
    PILLAR,
    TESTABLE_NEDM_SNS,
    THETA_6,
    baryogenesis_6d_summary,
    baryogenesis_dn_estimate,
)


class TestPillar841Constants:
    def test_pillar_number(self): assert PILLAR == 841
    def test_gate(self): assert GATE == "BARYOGENESIS_6D_DN_TIGHTENED"
    def test_sigma_mass(self): assert M_SIGMA_GEV == 650.0
    def test_theta(self): assert THETA_6 == pytest.approx(math.pi / 4.0, rel=1e-15)
    def test_central_value(self): assert D_N_CENTRAL_ECM == 7.8e-27
    def test_uncertainty(self): assert D_N_UNCERTAINTY_FRAC == 0.20
    def test_lean4_count(self): assert LEAN4_COUNT == 20
    def test_lean4_total(self): assert LEAN4_TOTAL == 1951
    def test_lean4_accumulates(self): assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT


class TestDnEstimate:
    def test_band_is_ordered(self):
        assert D_N_LOWER_ECM < D_N_CENTRAL_ECM < D_N_UPPER_ECM

    def test_band_values(self):
        assert D_N_LOWER_ECM == pytest.approx(6.24e-27, rel=1e-12)
        assert D_N_UPPER_ECM == pytest.approx(9.36e-27, rel=1e-12)

    def test_raw_estimate_positive(self):
        assert baryogenesis_dn_estimate()["raw_loop_estimate_ecm"] > 0.0

    def test_matching_factor_positive(self):
        assert baryogenesis_dn_estimate()["hadronic_matching_factor"] > 0.0

    def test_testable_flag(self):
        assert TESTABLE_NEDM_SNS is True and baryogenesis_dn_estimate()["testable_at_sns"] is True


class TestPillar841Summary:
    def test_summary_pillar(self):
        assert baryogenesis_6d_summary()["pillar"] == 841

    def test_summary_within_current_bound(self):
        assert baryogenesis_6d_summary()["within_current_bound"] is True

    def test_summary_honest_status(self):
        assert "unobserved" in baryogenesis_6d_summary()["honest_status"].lower()

    def test_summary_remaining_open(self):
        assert "COLLIDER" in baryogenesis_6d_summary()["remaining_open"][0]
