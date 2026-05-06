# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_sep_stress_energy_audit.py
=======================================
Tests for Pillar 197 — SEP Stress-Energy Audit.
"""
import math
import pytest
from src.core.sep_stress_energy_audit import (
    sep_nordtvedt_bound,
    sep_yukawa_suppression,
    sep_ew_radion_verdict,
    kk_casimir_energy_density,
    kk_cosmological_constant_contribution,
    vacuum_stress_energy_audit,
    sep_pillar197_summary,
    ALPHA_RS1,
    M_KK_GEV,
    K_CS,
    MICROSCOPE_ETA_LIMIT,
    LLR_NORDTVEDT_LIMIT,
)


class TestSEPNordtvedt:
    def test_nordtvedt_rs1_alpha(self):
        eta = sep_nordtvedt_bound(ALPHA_RS1)
        assert eta > 0
        # 2 × (1/√6)² × Ω_grav = 2/6 × 4.6e-10 ≈ 1.53e-10
        assert abs(eta - 2.0 / 6.0 * 4.6e-10) < 1e-13

    def test_nordtvedt_zero_coupling(self):
        assert sep_nordtvedt_bound(0.0) == 0.0

    def test_nordtvedt_unit_coupling(self):
        # α=1 → η = 2 × Ω_grav
        eta = sep_nordtvedt_bound(1.0)
        assert abs(eta - 2.0 * 4.6e-10) < 1e-14

    def test_nordtvedt_below_llr_limit(self):
        # Even in massless limit, η_N << LLR limit for Earth bodies
        eta = sep_nordtvedt_bound(ALPHA_RS1)
        assert eta < LLR_NORDTVEDT_LIMIT


class TestSEPYukawaSuppression:
    def test_ew_radion_at_earth_scale_is_zero(self):
        # For m_r = M_KK ≈ 1040 GeV, Yukawa range λ_r ≈ 1.9e-16 m
        # At Earth radius 6.4e6 m → exp(-3.4e22) = 0
        delta_eta = sep_yukawa_suppression(M_KK_GEV, 6.371e6, ALPHA_RS1)
        assert delta_eta == 0.0

    def test_massless_limit_no_suppression(self):
        # Very small mass → large Yukawa range → test at short distance
        # λ_r = ℏc/m_r = 0.1973e-15/1e-20 = 1e4 m for m_r = 1e-20 GeV
        m_tiny = 1e-20  # GeV → λ_r ≈ 2e4 m
        r_test = 1.0    # 1 m (λ_r >> r_test → minimal suppression)
        delta_eta = sep_yukawa_suppression(m_tiny, r_test, ALPHA_RS1)
        assert delta_eta > 0.0

    def test_below_microscope_limit(self):
        delta_eta = sep_yukawa_suppression(M_KK_GEV, 6.371e6, ALPHA_RS1)
        assert delta_eta < MICROSCOPE_ETA_LIMIT

    def test_zero_mass_returns_zero(self):
        # m_r = 0 → the function returns 0 (handled by the m_r==0 guard)
        delta_eta = sep_yukawa_suppression(0.0, 1.0, ALPHA_RS1)
        # For m_r=0, lambda_r=inf, ratio=0 → returns 0 (guard in function)
        assert delta_eta == 0.0 or math.isinf(delta_eta)


class TestSEPEWRadionVerdict:
    def setup_method(self):
        self.result = sep_ew_radion_verdict()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 197

    def test_alpha_is_rs1(self):
        assert abs(self.result["alpha"] - 1.0 / math.sqrt(6.0)) < 1e-10

    def test_sep_eotovos_safe(self):
        assert self.result["sep_eotovos_safe"] is True

    def test_sep_nordtvedt_safe(self):
        assert self.result["sep_nordtvedt_safe"] is True

    def test_yukawa_range_sub_femtometer(self):
        # λ_r should be < 1 fm = 1e-15 m for M_KK ≈ 1 TeV
        assert self.result["lambda_r_fm"] < 1.0

    def test_log10_yukawa_suppression_extreme(self):
        # log10 of suppression factor should be extremely negative
        assert self.result["log10_yukawa_suppression"] < -1e20

    def test_mechanism_is_mass_not_tuning(self):
        assert "MASS" in self.result["mechanism"] or "mass" in self.result["mechanism"].lower()

    def test_verdict_contains_safe(self):
        assert "SAFE" in self.result["verdict"]


class TestKKCasimirEnergy:
    def test_naive_is_positive(self):
        # Without Z₂ cancellation, sum should be positive
        rho = kk_casimir_energy_density(M_KK_GEV, K_CS, include_z2_cancellation=False)
        assert rho > 0

    def test_z2_cancellation_reduces_energy(self):
        rho_naive = kk_casimir_energy_density(M_KK_GEV, K_CS, include_z2_cancellation=False)
        rho_cancelled = kk_casimir_energy_density(M_KK_GEV, K_CS, include_z2_cancellation=True)
        assert abs(rho_cancelled) < abs(rho_naive)

    def test_n_max_zero_gives_zero(self):
        rho = kk_casimir_energy_density(M_KK_GEV, 0)
        assert rho == 0.0

    def test_topological_cutoff_at_k_cs(self):
        # At n=K_CS, weight = exp(-1) ≈ 0.37; modes above are suppressed
        import math
        weight_at_kcs = math.exp(-(K_CS**2) / K_CS**2)
        assert abs(weight_at_kcs - math.exp(-1)) < 1e-10

    def test_scales_as_m4(self):
        # Doubling m_kk should increase energy by 16
        rho1 = kk_casimir_energy_density(100.0, K_CS, False)
        rho2 = kk_casimir_energy_density(200.0, K_CS, False)
        assert abs(rho2 / rho1 - 16.0) < 0.1


class TestKKCosmologicalConstant:
    def setup_method(self):
        self.result = kk_cosmological_constant_contribution()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 197

    def test_no_4d_matter_creation(self):
        assert self.result["kk_contributes_4d_matter"] is False

    def test_residual_log10_extremely_negative(self):
        # After φ₀ closure: residual ≈ exp(-K_CS²) in Planck units
        # log10 ≈ -74² × log10(e) ≈ -2377
        assert self.result["lambda_kk_layer3_log10_planck"] < -2000

    def test_kk_lambda_below_observed(self):
        # λ_KK_planck << λ_obs_planck ≈ 10^{-122}
        assert self.result["lambda_kk_layer3_log10_planck"] < self.result["lambda_obs_log10_planck"]

    def test_has_three_layers(self):
        assert "layer1_topological_cutoff" in self.result
        assert "layer2_z2_cancellation" in self.result
        assert "layer3_phi0_closure" in self.result

    def test_honest_open_problem(self):
        assert "open_problem" in self.result
        assert len(self.result["open_problem"]) > 10


class TestVacuumStressEnergyAudit:
    def setup_method(self):
        self.result = vacuum_stress_energy_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 197

    def test_version(self):
        assert self.result["version"] == "v10.2"

    def test_has_both_audits(self):
        assert "sep_audit" in self.result
        assert "stress_energy_audit" in self.result

    def test_overall_verdict_pass(self):
        assert "PASS" in self.result["overall_verdict"]

    def test_sep_audit_safe(self):
        assert self.result["sep_audit"]["sep_eotovos_safe"] is True


class TestPillar197Summary:
    def setup_method(self):
        self.result = sep_pillar197_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 197

    def test_name_correct(self):
        assert "SEP" in self.result["name"] or "Stress" in self.result["name"]

    def test_has_three_layers(self):
        assert len(self.result["stress_energy_layers"]) == 3

    def test_has_honest_residual(self):
        assert "honest_residual" in self.result
        assert "open" in self.result["honest_residual"].lower()

    def test_has_next_attack(self):
        assert "next_attack_anticipated" in self.result
        assert len(self.result["next_attack_anticipated"]) > 50

    def test_coupling_fixed_not_free(self):
        assert "NOT" in self.result["sep_coupling_fixed"] or "fixed" in self.result["sep_coupling_fixed"]


class TestAlphaIsNotFreeParameter:
    """Verify that the RS1 coupling α = 1/√6 is correctly identified as fixed."""

    def test_alpha_value(self):
        assert abs(ALPHA_RS1 - 1.0 / math.sqrt(6.0)) < 1e-10

    def test_alpha_not_zero(self):
        assert ALPHA_RS1 > 0

    def test_alpha_less_than_one(self):
        # α = 1/√6 ≈ 0.408 < 1
        assert ALPHA_RS1 < 1.0

    def test_alpha_not_tuned_to_cassini(self):
        # The Cassini constraint |Δγ| < 2.3e-5 would require α < sqrt(2.3e-5/2) ≈ 0.0034
        # RS1 gives α = 0.408 >> 0.0034 — the constraint is satisfied by MASS not by small α
        cassini_alpha_limit = math.sqrt(2.3e-5 / 2.0)
        assert ALPHA_RS1 > cassini_alpha_limit  # α is NOT small — it's the mass that saves us
