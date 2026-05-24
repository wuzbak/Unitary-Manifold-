# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 409 — Resonant Leptogenesis Degeneracy Window."""
import math
import pytest

from src.core.pillar409_resonant_leptogenesis import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_STATUS,
    BARYOGENESIS_STATUS,
    M_KK_GEV,
    N_W,
    K_CS,
    PI_KR,
    M_R1_GEV,
    ETA_B_OBS,
    G_STAR,
    KAPPA_F,
    yukawa_coupling_estimate,
    decay_width_estimate,
    required_cp_asymmetry,
    natural_mass_splitting,
    resonant_window_check,
    resonant_leptogenesis_verdict,
)


class TestConstants:
    def test_adjacency_label(self):
        assert "ADJACENT" in ADJACENCY_TRACK_LABEL

    def test_pillar_status(self):
        assert PILLAR_STATUS == "ARCHITECTURE_LIMIT_CONFIRMED_RL"

    def test_baryogenesis_status(self):
        assert BARYOGENESIS_STATUS == "ARCHITECTURE_LIMIT_CONFIRMED_ALL_PATHS"

    def test_m_kk_order_of_magnitude(self):
        # KK scale should be ~TeV
        assert 100 < M_KK_GEV < 10000

    def test_m_r1_formula(self):
        expected = M_KK_GEV * (N_W / K_CS) * (PI_KR / 2.0)
        assert abs(M_R1_GEV - expected) < 1.0

    def test_eta_b_observed(self):
        assert abs(ETA_B_OBS - 6.10e-10) < 1e-12

    def test_g_star(self):
        assert abs(G_STAR - 106.75) < 0.01


class TestYukawaCoupling:
    def test_positive(self):
        Y = yukawa_coupling_estimate()
        assert Y > 0

    def test_order_of_magnitude(self):
        # For m_nu ~ 0.05 eV, M_R ~ 1.25 TeV: Y ~ sqrt(5e-11 * 1250 / 246^2) ~ 1e-6
        Y = yukawa_coupling_estimate()
        assert 1e-8 < Y < 0.1

    def test_scales_with_mass(self):
        Y_small = yukawa_coupling_estimate(m_nu_eV=0.01)
        Y_large = yukawa_coupling_estimate(m_nu_eV=0.1)
        assert Y_large > Y_small

    def test_seesaw_relation(self):
        # y² × v² / M_R = m_nu (approx)
        m_nu_eV = 0.05
        M_R = M_R1_GEV
        v = 246.0
        Y = yukawa_coupling_estimate(m_nu_eV, M_R, v)
        m_nu_reconstructed = Y ** 2 * v ** 2 / M_R * 1e9  # GeV → eV
        assert abs(m_nu_reconstructed - m_nu_eV) / m_nu_eV < 0.01


class TestDecayWidth:
    def test_positive(self):
        Y = yukawa_coupling_estimate()
        Gamma = decay_width_estimate(Y)
        assert Gamma > 0

    def test_formula(self):
        Y = 0.03
        M_R = 1250.0
        expected = Y ** 2 * M_R / (8 * math.pi)
        result = decay_width_estimate(Y, M_R)
        assert abs(result - expected) < 1e-10


class TestRequiredCPAsymmetry:
    def test_positive(self):
        eps = required_cp_asymmetry()
        assert eps > 0

    def test_order_of_magnitude(self):
        # Required epsilon should be O(1e-5) to O(1e-4)
        eps = required_cp_asymmetry()
        assert 1e-6 < eps < 1e-3

    def test_formula(self):
        eta_B = 6.1e-10
        g_star = 106.75
        kappa = 0.01
        sphaleron = 28.0 / 79.0
        expected = eta_B * g_star / (sphaleron * kappa)
        result = required_cp_asymmetry(eta_B, sphaleron, g_star, kappa)
        assert abs(result - expected) < 1e-15


class TestNaturalMassSplitting:
    def test_returns_dict(self):
        data = natural_mass_splitting()
        assert isinstance(data, dict)

    def test_ratio_formula(self):
        delta_c = N_W / K_CS
        expected_ratio = 2.0 * delta_c * PI_KR
        data = natural_mass_splitting()
        assert abs(data["natural_delta_M_ratio"] - expected_ratio) < 0.01

    def test_ratio_order_5(self):
        # 2 × (5/74) × 37 = 5.0
        data = natural_mass_splitting()
        assert abs(data["natural_delta_M_ratio"] - 5.0) < 0.01

    def test_splitting_positive(self):
        data = natural_mass_splitting()
        assert data["natural_delta_M_GeV"] > 0


class TestResonantWindowCheck:
    def test_not_in_resonant_window(self):
        rw = resonant_window_check()
        assert rw["in_resonant_window"] is False

    def test_verdict_not_resonant(self):
        rw = resonant_window_check()
        assert rw["verdict"] == "NOT_IN_RESONANT_WINDOW"

    def test_natural_ratio_much_larger_than_resonant(self):
        rw = resonant_window_check()
        # Natural ratio >> required (by many orders)
        assert rw["natural_delta_M_ratio"] > rw["ratio_M_resonant"] * 100

    def test_required_epsilon_positive(self):
        rw = resonant_window_check()
        assert rw["required_epsilon1"] > 0

    def test_fine_tuning_large(self):
        rw = resonant_window_check()
        # Fine-tuning should be >> 1 (unnatural)
        assert rw["fine_tuning_required"] > 100


class TestResonantLeptogenesisVerdict:
    def test_pillar_status(self):
        v = resonant_leptogenesis_verdict()
        assert v["pillar_status"] == "ARCHITECTURE_LIMIT_CONFIRMED_RL"

    def test_baryogenesis_status(self):
        v = resonant_leptogenesis_verdict()
        assert v["baryogenesis_overall_status"] == "ARCHITECTURE_LIMIT_CONFIRMED_ALL_PATHS"

    def test_naturalness_verdict_unnatural(self):
        v = resonant_leptogenesis_verdict()
        assert v["naturalness_verdict"] == "UNNATURAL"

    def test_previous_paths_present(self):
        v = resonant_leptogenesis_verdict()
        assert "P365_minimal_KK" in v["previous_paths"]
        assert "P370_affleck_dine" in v["previous_paths"]
        assert "P371_kk_ewpt" in v["previous_paths"]
        assert "P409_resonant_RL" in v["previous_paths"]

    def test_all_paths_architecture_limit(self):
        v = resonant_leptogenesis_verdict()
        for key, val in v["previous_paths"].items():
            assert "ARCHITECTURE_LIMIT" in val

    def test_closure_verdict_present(self):
        v = resonant_leptogenesis_verdict()
        assert "ARCHITECTURE_LIMIT_CONFIRMED" in v["closure_verdict"]
