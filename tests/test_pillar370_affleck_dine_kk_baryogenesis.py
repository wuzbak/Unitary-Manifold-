# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar370_affleck_dine_kk_baryogenesis.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar370_affleck_dine_kk_baryogenesis import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    ETA_B_OBSERVED, PHI0_PLANCK_UNITS, M_KK_GEV, T_EW_GEV, M_PL_GEV,
    N_W, K_CS, RHO_BRAID, DELTA_CP_KK,
    separation_guard, ad_cp_violation_estimate, radion_decay_rate,
    condensate_survival_check, ad_kk_eta_b_estimate,
    cp_violation_inventory, affleck_dine_assessment, pillar370_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 370
    def test_status(self): assert PILLAR_STATUS == "ARCHITECTURE_LIMIT_NARROWED"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_eta_b_observed(self): assert abs(ETA_B_OBSERVED - 6.1e-10) < 1e-11
    def test_phi0(self): assert abs(PHI0_PLANCK_UNITS - 10.0 * math.pi) < 1e-6
    def test_k_cs(self): assert K_CS == 74
    def test_n_w(self): assert N_W == 5
    def test_rho_braid(self): assert abs(RHO_BRAID - 70.0 / 74.0) < 1e-6
    def test_delta_cp_positive(self): assert DELTA_CP_KK > 0
    def test_delta_cp_range(self): assert 0.0 < DELTA_CP_KK < math.pi / 2.0 + 0.1


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_mentions_architecture(self): assert "ARCHITECTURE" in separation_guard()


class TestAdCpViolationEstimate:
    def test_returns_dict(self): assert isinstance(ad_cp_violation_estimate(), dict)
    def test_rho_braid_present(self):
        r = ad_cp_violation_estimate()
        assert "rho_braid" in r
    def test_rho_braid_correct(self):
        r = ad_cp_violation_estimate()
        assert abs(r["rho_braid"] - RHO_BRAID) < 1e-4
    def test_epsilon_cp_o1(self):
        r = ad_cp_violation_estimate()
        assert r["epsilon_cp_sin"] > 0.5    # O(1) CP violation
    def test_verdict_present(self):
        r = ad_cp_violation_estimate()
        assert "verdict" in r
    def test_delta_cp_close_to_expected(self):
        r = ad_cp_violation_estimate()
        assert abs(r["delta_cp_kk_rad"] - DELTA_CP_KK) < 1e-4


class TestRadionDecayRate:
    def test_returns_dict(self): assert isinstance(radion_decay_rate(), dict)
    def test_decay_rate_positive(self):
        r = radion_decay_rate()
        assert r["decay_rate_gev"] > 0
    def test_survives_to_ew_key_present(self):
        r = radion_decay_rate()
        assert "survives_to_ew" in r
    def test_custom_mass(self):
        r = radion_decay_rate(m_phi_gev=100.0)
        assert r["m_phi_gev"] == 100.0
    def test_verdict_present(self):
        r = radion_decay_rate()
        assert "verdict" in r


class TestCondensateSurvivalCheck:
    def test_returns_dict(self): assert isinstance(condensate_survival_check(), dict)
    def test_survives_to_ew_false(self):
        r = condensate_survival_check()
        # m_phi ~ M_KK >> T_EW → condensate does NOT survive
        assert r["survives_to_ew"] is False
    def test_obstruction_present(self):
        r = condensate_survival_check()
        assert "obstruction" in r
    def test_alternative_path_present(self):
        r = condensate_survival_check()
        assert "alternative_path" in r
    def test_h_ew_positive(self):
        r = condensate_survival_check()
        assert r["h_ew_gev"] > 0


class TestAdKkEtaBEstimate:
    def test_returns_dict(self): assert isinstance(ad_kk_eta_b_estimate(), dict)
    def test_eta_b_radion_small(self):
        r = ad_kk_eta_b_estimate()
        assert r["eta_b_radion_estimate"] < ETA_B_OBSERVED
    def test_gap_radion_large(self):
        r = ad_kk_eta_b_estimate()
        assert r["gap_radion_from_observed"] > 1000
    def test_status_architecture_limit(self):
        r = ad_kk_eta_b_estimate()
        assert "ARCHITECTURE_LIMIT" in r["status"]
    def test_epsilon_cp_o1(self):
        r = ad_kk_eta_b_estimate()
        assert r["epsilon_cp"] > 0.5


class TestCpViolationInventory:
    def test_returns_list(self): assert isinstance(cp_violation_inventory(), list)
    def test_at_least_3_sources(self): assert len(cp_violation_inventory()) >= 3
    def test_each_has_source(self):
        for item in cp_violation_inventory():
            assert "source" in item
    def test_each_has_status(self):
        for item in cp_violation_inventory():
            assert "status" in item
    def test_kk_braid_o1(self):
        items = cp_violation_inventory()
        kk = next(i for i in items if "braid" in i["source"].lower())
        assert "O(1)" in kk["status"]


class TestAffleckDineAssessment:
    def test_returns_dict(self): assert isinstance(affleck_dine_assessment(), dict)
    def test_pillar(self): assert affleck_dine_assessment()["pillar"] == 370
    def test_status(self): assert affleck_dine_assessment()["status"] == "ARCHITECTURE_LIMIT_NARROWED"
    def test_verdict_present(self): assert "verdict" in affleck_dine_assessment()
    def test_cp_inventory_present(self): assert "cp_inventory" in affleck_dine_assessment()
    def test_obstruction_present(self): assert "obstruction" in affleck_dine_assessment()
    def test_requirements_check_present(self): assert "ad_requirements_check" in affleck_dine_assessment()
    def test_flat_direction_present(self):
        r = affleck_dine_assessment()
        assert "PRESENT" in r["ad_requirements_check"]["flat_direction"]
    def test_cp_violation_present(self):
        r = affleck_dine_assessment()
        assert "PRESENT" in r["ad_requirements_check"]["cp_violation"]
    def test_condensate_obstructed(self):
        r = affleck_dine_assessment()
        assert "OBSTRUCTED" in r["ad_requirements_check"]["long_lived_condensate"]


class TestPillar370Summary:
    def test_pillar(self): assert pillar370_summary()["pillar"] == 370
    def test_status(self): assert pillar370_summary()["status"] == "ARCHITECTURE_LIMIT_NARROWED"
    def test_cp_violation_available(self): assert pillar370_summary()["cp_violation_available"] is True
    def test_condensate_survives_false(self): assert pillar370_summary()["condensate_survives_to_ew"] is False
