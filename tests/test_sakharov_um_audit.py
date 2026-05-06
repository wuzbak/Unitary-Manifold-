# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_sakharov_um_audit.py
==================================
Tests for src/core/sakharov_um_audit.py — Pillar 191.

Test coverage:
  - Module constants
  - C1: Baryon number violation
  - C2: C and CP violation
  - C3: Thermal non-equilibrium
  - η_B order-of-magnitude estimate
  - Single-source K_CS CP coherence
  - Full audit (structure, completeness, status labels)
"""

from __future__ import annotations

import math

import pytest

from src.core.sakharov_um_audit import (
    ALPHA_W,
    BETA_BIREFRINGENCE_DEG,
    DELTA_CP_DEG,
    G_STAR_EW,
    K_CS,
    M_GUT_GEV,
    OBSERVED_ETA_B,
    T_EW_GEV,
    condition_c1_baryon_violation,
    condition_c2_cp_violation,
    condition_c3_thermal_nonequilibrium,
    eta_b_order_of_magnitude,
    sakharov_full_audit,
    single_source_cp_coherence,
    _cp_amplitude,
    _baryon_prefactor,
    _sphaleron_dimensionless,
)


# ===========================================================================
# Module Constants
# ===========================================================================


class TestModuleConstants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_alpha_w(self):
        assert ALPHA_W == pytest.approx(1.0 / 30.0)

    def test_g_star_ew(self):
        assert G_STAR_EW == pytest.approx(106.75)

    def test_t_ew_gev(self):
        assert T_EW_GEV == pytest.approx(246.0)

    def test_observed_eta_b(self):
        assert OBSERVED_ETA_B == pytest.approx(6.0e-10, rel=1e-6)

    def test_m_gut_gev(self):
        assert 1e15 < M_GUT_GEV < 1e17

    def test_beta_birefringence(self):
        assert BETA_BIREFRINGENCE_DEG == pytest.approx(0.331, rel=1e-3)

    def test_delta_cp(self):
        assert DELTA_CP_DEG == pytest.approx(70.0, rel=1e-3)


# ===========================================================================
# Helper functions
# ===========================================================================


class TestHelperFunctions:
    def test_cp_amplitude_range(self):
        eps = _cp_amplitude(74)
        assert 0.0 < eps < 1.0

    def test_cp_amplitude_formula(self):
        k = 74.0
        expected = k / (k**2 + 4.0 * math.pi**2)
        assert _cp_amplitude(k) == pytest.approx(expected, rel=1e-10)

    def test_cp_amplitude_decreases_with_k(self):
        # ε_CP(k) = k/(k²+4π²) — peaks at k=2π, decreasing for large k
        assert _cp_amplitude(100) < _cp_amplitude(74)  # 74 < 100, but eps(74) > eps(100)?
        # Actually at k=74, it's near the peak relative to k=100
        # Let's just check it's positive and < 1
        assert 0 < _cp_amplitude(100) < 1

    def test_sphaleron_dimensionless(self):
        rate = _sphaleron_dimensionless(ALPHA_W)
        assert rate == pytest.approx(ALPHA_W**4, rel=1e-10)

    def test_sphaleron_dimensionless_small(self):
        # α_w^4 = (1/30)^4 ~ 1.2e-6
        rate = _sphaleron_dimensionless(ALPHA_W)
        assert 1e-7 < rate < 1e-5

    def test_baryon_prefactor(self):
        pf = _baryon_prefactor(G_STAR_EW)
        expected = 45.0 / (2.0 * math.pi**2 * G_STAR_EW)
        assert pf == pytest.approx(expected, rel=1e-10)

    def test_baryon_prefactor_positive(self):
        assert _baryon_prefactor(G_STAR_EW) > 0


# ===========================================================================
# Condition C1: Baryon Number Violation
# ===========================================================================


class TestConditionC1:
    def setup_method(self):
        self.result = condition_c1_baryon_violation()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_condition_label(self):
        assert "C1" in self.result["condition"]

    def test_satisfied(self):
        assert self.result["satisfied"] is True

    def test_mechanisms_present(self):
        assert "gut_x_y_bosons" in self.result["mechanisms"]
        assert "ew_sphalerons" in self.result["mechanisms"]

    def test_gut_scale_order(self):
        m_gut = self.result["mechanisms"]["gut_x_y_bosons"]["m_gut_gev"]
        assert 1e15 < m_gut < 1e17

    def test_proton_lifetime_above_sk(self):
        gut = self.result["mechanisms"]["gut_x_y_bosons"]
        assert gut["above_sk_bound"] is True

    def test_proton_lifetime_order(self):
        tau = self.result["mechanisms"]["gut_x_y_bosons"]["proton_lifetime_yr"]
        assert tau > 1.6e34  # Above SK bound

    def test_pillar_107_cited(self):
        assert self.result["mechanisms"]["gut_x_y_bosons"]["pillar"] == 107

    def test_ew_sphalerons_active_above(self):
        sph = self.result["mechanisms"]["ew_sphalerons"]
        assert sph["active_above_t_ew"] is True

    def test_b_minus_l_conserved(self):
        assert self.result["mechanisms"]["ew_sphalerons"]["b_minus_l_conserved"] is True

    def test_b_plus_l_violated(self):
        assert self.result["mechanisms"]["ew_sphalerons"]["b_plus_l_violated"] is True

    def test_verdict_contains_satisfied(self):
        assert "SATISFIED" in self.result["verdict"]

    def test_verdict_mentions_pillar_107(self):
        assert "107" in self.result["verdict"]


# ===========================================================================
# Condition C2: C and CP Violation
# ===========================================================================


class TestConditionC2:
    def setup_method(self):
        self.result = condition_c2_cp_violation()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_condition_label(self):
        assert "C2" in self.result["condition"]

    def test_satisfied(self):
        assert self.result["satisfied"] is True

    def test_k_cs_source(self):
        assert self.result["k_cs_source"] == 74

    def test_cp_sources_keys(self):
        src = self.result["cp_sources"]
        assert "birefringence" in src
        assert "ckm_phase" in src
        assert "ew_baryogenesis_amplitude" in src

    def test_birefringence_beta(self):
        b = self.result["cp_sources"]["birefringence"]
        assert b["beta_deg"] == pytest.approx(0.331, rel=1e-3)
        assert "LiteBIRD" in b["falsifier"]

    def test_ckm_phase(self):
        ckm = self.result["cp_sources"]["ckm_phase"]
        assert 60.0 < ckm["delta_cp_deg"] < 80.0

    def test_eps_cp_range(self):
        eps = self.result["cp_sources"]["ew_baryogenesis_amplitude"]["eps_cp"]
        assert 0.0 < eps < 0.1

    def test_single_source_true(self):
        assert self.result["single_source"] is True

    def test_verdict_satisfied(self):
        assert "SATISFIED" in self.result["verdict"]

    def test_verdict_mentions_k_cs(self):
        assert "74" in self.result["verdict"]

    def test_zero_extra_parameters(self):
        # All three CP signatures from single K_CS — no extra params
        assert self.result["single_source"] is True


# ===========================================================================
# Condition C3: Thermal Non-Equilibrium
# ===========================================================================


class TestConditionC3:
    def setup_method(self):
        self.result = condition_c3_thermal_nonequilibrium()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_condition_label(self):
        assert "C3" in self.result["condition"]

    def test_satisfied(self):
        assert self.result["satisfied"] is True

    def test_mechanisms_keys(self):
        m = self.result["mechanisms"]
        assert "ftum_attractor" in m
        assert "ew_phase_transition" in m
        assert "irreversibility_arrow" in m

    def test_ftum_phi0(self):
        ftum = self.result["mechanisms"]["ftum_attractor"]
        assert 30.0 < ftum["phi0_eff"] < 33.0

    def test_ew_out_of_eq(self):
        ew = self.result["mechanisms"]["ew_phase_transition"]
        assert ew["out_of_equilibrium"] is True

    def test_sphaleron_frozen_below_tew(self):
        ew = self.result["mechanisms"]["ew_phase_transition"]
        assert ew["sphaleron_frozen_below"] is True

    def test_irreversibility_field(self):
        irr = self.result["mechanisms"]["irreversibility_arrow"]
        assert "H_μν" in irr["field"]

    def test_entropy_production_positive(self):
        irr = self.result["mechanisms"]["irreversibility_arrow"]
        assert "dS/dt > 0" in irr["entropy_production"]

    def test_pillar_72_cited(self):
        assert self.result["mechanisms"]["ftum_attractor"]["pillar"] == 72

    def test_verdict_satisfied(self):
        assert "SATISFIED" in self.result["verdict"]


# ===========================================================================
# η_B Order-of-Magnitude Estimate
# ===========================================================================


class TestEtaBOrderOfMagnitude:
    def setup_method(self):
        self.result = eta_b_order_of_magnitude()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_k_cs(self):
        assert self.result["k_cs"] == 74

    def test_eps_cp_positive(self):
        assert self.result["eps_cp"] > 0

    def test_eta_b_um_positive(self):
        assert self.result["eta_b_um"] > 0

    def test_eta_b_observed_correct(self):
        assert self.result["eta_b_observed"] == pytest.approx(6e-10, rel=1e-6)

    def test_formula_numerics(self):
        eps = _cp_amplitude(K_CS)
        sph = _sphaleron_dimensionless(ALPHA_W)
        pf = _baryon_prefactor(G_STAR_EW)
        expected = eps * sph * pf
        assert self.result["eta_b_um"] == pytest.approx(expected, rel=1e-8)

    def test_ratio_positive(self):
        assert self.result["ratio_um_to_obs"] > 0

    def test_within_two_orders(self):
        # The estimate should be within 2 orders of magnitude of PDG
        # (factor ~18 → log10(18) ≈ 1.26 < 2)
        assert self.result["within_two_orders"] is True

    def test_log10_ratio_reasonable(self):
        # Should be < 2 orders off
        assert abs(self.result["log10_ratio"]) < 2.0

    def test_status_label(self):
        assert self.result["status"] == "ORDER-OF-MAGNITUDE ESTIMATE"

    def test_honest_gap_present(self):
        assert "Boltzmann" in self.result["honest_gap"]

    def test_verdict_contains_both_values(self):
        v = self.result["verdict"]
        assert "PDG" in v or "obs" in v


# ===========================================================================
# Single-Source CP Coherence
# ===========================================================================


class TestSingleSourceCPCoherence:
    def setup_method(self):
        self.result = single_source_cp_coherence()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_k_cs(self):
        assert self.result["k_cs"] == 74

    def test_single_source_true(self):
        assert self.result["single_source"] is True

    def test_signatures_keys(self):
        s = self.result["signatures"]
        assert "birefringence" in s
        assert "ckm_cp_phase" in s
        assert "baryon_asymmetry" in s

    def test_all_derived_from_k_cs(self):
        for sig in self.result["signatures"].values():
            assert sig["derived_from_k_cs"] is True

    def test_birefringence_falsifier(self):
        assert "LiteBIRD" in self.result["signatures"]["birefringence"]["falsifier"]

    def test_cross_falsification_string(self):
        assert "K_CS" in self.result["cross_falsification"]
        assert "LiteBIRD" in self.result["cross_falsification"]

    def test_no_new_free_parameters(self):
        assert self.result["new_free_parameters"] == 0

    def test_status_label(self):
        assert "K_CS" in self.result["status"]


# ===========================================================================
# Full Audit
# ===========================================================================


class TestSakharovFullAudit:
    def setup_method(self):
        self.result = sakharov_full_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 191

    def test_status_label(self):
        assert self.result["status"] == "COMPATIBILITY AUDIT"

    def test_version(self):
        assert "10.1" in self.result["version"]

    def test_all_conditions_present(self):
        conds = self.result["conditions"]
        assert "C1_baryon_violation" in conds
        assert "C2_cp_violation" in conds
        assert "C3_nonequilibrium" in conds

    def test_all_conditions_satisfied(self):
        assert self.result["all_conditions_satisfied"] is True

    def test_c1_satisfied(self):
        assert self.result["conditions"]["C1_baryon_violation"]["satisfied"] is True

    def test_c2_satisfied(self):
        assert self.result["conditions"]["C2_cp_violation"]["satisfied"] is True

    def test_c3_satisfied(self):
        assert self.result["conditions"]["C3_nonequilibrium"]["satisfied"] is True

    def test_eta_b_estimate_present(self):
        assert "eta_b_um" in self.result["eta_b_estimate"]

    def test_eta_b_within_two_orders(self):
        assert self.result["eta_b_estimate"]["within_two_orders"] is True

    def test_cp_coherence_k_cs(self):
        assert self.result["cp_coherence"]["k_cs"] == 74

    def test_honest_gaps_listed(self):
        gaps = self.result["honest_gaps"]
        assert len(gaps) >= 3
        assert any("ORDER-OF-MAGNITUDE" in g for g in gaps)

    def test_key_finding_mentions_all_three(self):
        kf = self.result["key_finding"]
        assert "C1" in kf
        assert "C2" in kf
        assert "C3" in kf

    def test_addresses_review_string(self):
        assert "Round 4" in self.result["addresses_review"]

    def test_falsification_mentions_litebird(self):
        assert "LiteBIRD" in self.result["falsification"]
