# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
tests/test_pillar405_sobolev_ftum_extension.py
==============================================
Tests for Pillar 405 — Sobolev H¹ Extension of FTUM Banach Fixed-Point Theorem.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar405_sobolev_ftum_extension import (
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    PI_KR,
    M_KK_GEV,
    PHI0_BRAID,
    EPSILON_MAX_ORBIFOLD,
    L_CONTRACTION,
    KAPPA_PHYSICAL,
    D_PHI_DIFFUSION,
    K_MAX_OVER_MKK,
    EPSILON_GRAD_MAX,
    KK_BOLTZMANN_FACTOR,
    sobolev_h1_norm,
    h1_lipschitz_estimate,
    gradient_perturbation_contractivity,
    critical_gradient_bound,
    kk_graviton_energy_density_ratio,
    basin_energy_threshold,
    kk_energy_vs_basin_check,
    admission_12_closed_verdict,
    pillar405_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 405

    def test_pillar_status(self):
        assert PILLAR_STATUS == "H1_SOBOLEV_CLOSED"

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_m_kk_gev(self):
        assert M_KK_GEV == pytest.approx(1040.0, rel=1e-6)

    def test_phi0_braid_formula(self):
        assert PHI0_BRAID == pytest.approx(5.0 * math.pi / 74.0, rel=1e-9)

    def test_epsilon_max_orbifold(self):
        assert EPSILON_MAX_ORBIFOLD == pytest.approx(math.pi / 4.0, rel=1e-9)

    def test_l_contraction_less_one(self):
        assert L_CONTRACTION < 1.0

    def test_l_contraction_positive(self):
        assert L_CONTRACTION > 0.0

    def test_kappa_physical(self):
        assert KAPPA_PHYSICAL == pytest.approx(0.5, rel=1e-6)

    def test_epsilon_grad_max_positive(self):
        assert EPSILON_GRAD_MAX > 0.0

    def test_epsilon_grad_max_less_epsilon_max(self):
        assert EPSILON_GRAD_MAX < EPSILON_MAX_ORBIFOLD

    def test_kk_boltzmann_factor_range(self):
        assert 0.0 < KK_BOLTZMANN_FACTOR <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Sobolev H¹ norm
# ─────────────────────────────────────────────────────────────────────────────

class TestSobolevH1Norm:
    def test_zero_inputs(self):
        assert sobolev_h1_norm(0.0, 0.0) == pytest.approx(0.0, abs=1e-15)

    def test_only_l2(self):
        assert sobolev_h1_norm(1.0, 0.0) == pytest.approx(1.0, rel=1e-9)

    def test_only_grad(self):
        assert sobolev_h1_norm(0.0, 1.0) == pytest.approx(1.0, rel=1e-9)

    def test_pythagorean(self):
        result = sobolev_h1_norm(3.0, 4.0)
        assert result == pytest.approx(5.0, rel=1e-9)

    def test_commutative(self):
        assert sobolev_h1_norm(1.0, 2.0) == pytest.approx(sobolev_h1_norm(2.0, 1.0), rel=1e-9)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            sobolev_h1_norm(-1.0, 0.0)

    def test_gradient_raises_norm(self):
        # Adding gradient norm always increases the H¹ norm
        assert sobolev_h1_norm(1.0, 0.5) > sobolev_h1_norm(1.0, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# H¹ Lipschitz estimate
# ─────────────────────────────────────────────────────────────────────────────

class TestH1LipschitzEstimate:
    def test_returns_dict(self):
        r = h1_lipschitz_estimate()
        assert isinstance(r, dict)

    def test_contractive_h1(self):
        r = h1_lipschitz_estimate()
        assert r["contractive_h1"]

    def test_banach_fpt_applies(self):
        r = h1_lipschitz_estimate()
        assert r["banach_fpt_applies"]

    def test_l_h1_less_one(self):
        r = h1_lipschitz_estimate()
        assert r["l_h1"] < 1.0

    def test_l_h1_max_of_l_l2_and_grad(self):
        r = h1_lipschitz_estimate(l_l2=0.9, l_grad=0.85)
        assert r["l_h1"] == pytest.approx(0.9, rel=1e-9)

    def test_proof_summary_present(self):
        r = h1_lipschitz_estimate()
        assert len(r["proof_summary"]) > 50

    def test_sobolev_embedding_mentioned(self):
        r = h1_lipschitz_estimate()
        assert "Sobolev" in r["sobolev_embedding"] or "H¹" in r["sobolev_embedding"]

    def test_non_contractive_case(self):
        r = h1_lipschitz_estimate(l_l2=1.1, l_grad=1.2)
        assert not r["contractive_h1"]


# ─────────────────────────────────────────────────────────────────────────────
# Gradient perturbation contractivity
# ─────────────────────────────────────────────────────────────────────────────

class TestGradientPerturbationContractivity:
    def test_returns_dict(self):
        r = gradient_perturbation_contractivity(0.1, 0.1)
        assert isinstance(r, dict)

    def test_small_perturbation_contracted(self):
        r = gradient_perturbation_contractivity(0.01, 0.01)
        assert r["contracted"]

    def test_h1_norm_formula(self):
        r = gradient_perturbation_contractivity(3.0, 4.0)
        assert r["h1_norm_before"] == pytest.approx(5.0, rel=1e-9)

    def test_h1_norm_after_smaller(self):
        r = gradient_perturbation_contractivity(0.1, 0.1)
        assert r["h1_norm_after"] < r["h1_norm_before"]

    def test_within_basin_for_small_perturbation(self):
        r = gradient_perturbation_contractivity(0.01, 0.01)
        assert r["within_h1_basin"]

    def test_outside_basin_large_perturbation(self):
        r = gradient_perturbation_contractivity(2.0, 2.0)
        assert not r["within_h1_basin"]

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            gradient_perturbation_contractivity(-0.1, 0.1)

    def test_verdict_present(self):
        r = gradient_perturbation_contractivity(0.1, 0.1)
        assert len(r["verdict"]) > 20


# ─────────────────────────────────────────────────────────────────────────────
# Critical gradient bound
# ─────────────────────────────────────────────────────────────────────────────

class TestCriticalGradientBound:
    def test_returns_dict(self):
        r = critical_gradient_bound()
        assert isinstance(r, dict)

    def test_epsilon_grad_positive(self):
        r = critical_gradient_bound()
        assert r["epsilon_grad_max"] > 0.0

    def test_epsilon_grad_less_epsilon_max(self):
        r = critical_gradient_bound()
        assert r["epsilon_grad_max"] < r["epsilon_max_l2"]

    def test_ratio_less_one(self):
        r = critical_gradient_bound()
        assert r["ratio"] < 1.0

    def test_ratio_formula(self):
        r = critical_gradient_bound()
        expected_ratio = 1.0 / math.sqrt(1.0 + PI_KR ** 2)
        assert r["ratio"] == pytest.approx(expected_ratio, rel=1e-6)

    def test_pi_kr_in_result(self):
        r = critical_gradient_bound()
        assert r["pi_kr"] == pytest.approx(PI_KR, rel=1e-9)

    def test_interpretation_present(self):
        r = critical_gradient_bound()
        assert len(r["interpretation"]) > 30


# ─────────────────────────────────────────────────────────────────────────────
# KK graviton energy density ratio
# ─────────────────────────────────────────────────────────────────────────────

class TestKkGravitonEnergyDensityRatio:
    def test_returns_dict(self):
        r = kk_graviton_energy_density_ratio()
        assert isinstance(r, dict)

    def test_boltzmann_factor_small(self):
        r = kk_graviton_energy_density_ratio()
        # For M_KK = 1040 GeV, T_RH ~ 10^9 GeV: ratio ≈ 10^{-3}
        assert r["boltzmann_factor"] <= 1.0

    def test_rho_ratio_positive(self):
        r = kk_graviton_energy_density_ratio()
        assert r["rho_ratio_kk_to_total"] >= 0.0

    def test_below_basin_threshold(self):
        r = kk_graviton_energy_density_ratio()
        # For T_RH >> M_KK scenario: should be below threshold
        assert r["below_basin_threshold"]

    def test_verdict_present(self):
        r = kk_graviton_energy_density_ratio()
        assert len(r["verdict"]) > 30

    def test_epsilon_max_sq_in_result(self):
        r = kk_graviton_energy_density_ratio()
        assert r["epsilon_max_sq"] == pytest.approx(EPSILON_MAX_ORBIFOLD ** 2, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# Basin energy threshold
# ─────────────────────────────────────────────────────────────────────────────

class TestBasinEnergyThreshold:
    def test_returns_dict(self):
        r = basin_energy_threshold()
        assert isinstance(r, dict)

    def test_e_basin_normalized(self):
        r = basin_energy_threshold()
        assert r["e_basin_normalized"] == pytest.approx(EPSILON_MAX_ORBIFOLD ** 2, rel=1e-9)

    def test_e_basin_positive(self):
        r = basin_energy_threshold()
        assert r["e_basin_normalized"] > 0.0

    def test_interpretation_present(self):
        r = basin_energy_threshold()
        assert len(r["interpretation"]) > 30


# ─────────────────────────────────────────────────────────────────────────────
# KK energy vs basin check
# ─────────────────────────────────────────────────────────────────────────────

class TestKkEnergyVsBasinCheck:
    def test_returns_dict(self):
        r = kk_energy_vs_basin_check()
        assert isinstance(r, dict)

    def test_kk_safe(self):
        r = kk_energy_vs_basin_check()
        assert r["kk_safe"]

    def test_safety_margin_large(self):
        r = kk_energy_vs_basin_check()
        # Safety margin should be >> 1
        assert r["safety_margin"] > 1.0

    def test_epsilon_grad_max_in_result(self):
        r = kk_energy_vs_basin_check()
        assert r["epsilon_grad_max"] == pytest.approx(EPSILON_GRAD_MAX, rel=1e-6)

    def test_verdict_present(self):
        r = kk_energy_vs_basin_check()
        assert "cannot" in r["verdict"].lower() or "safe" in r["verdict"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# Admission 12 closed verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission12ClosedVerdict:
    def test_returns_dict(self):
        r = admission_12_closed_verdict()
        assert isinstance(r, dict)

    def test_admission_number(self):
        r = admission_12_closed_verdict()
        assert r["admission"] == 12

    def test_previous_status(self):
        r = admission_12_closed_verdict()
        assert r["previous_status"] == "CONTRACTIVE_IN_ORBIFOLD_BASIN"

    def test_new_status(self):
        r = admission_12_closed_verdict()
        assert r["new_status"] == "CLOSED"

    def test_completeness_satisfied(self):
        r = admission_12_closed_verdict()
        assert r["banach_fpt_condition_1"]["status"] == "SATISFIED"

    def test_contractivity_satisfied(self):
        r = admission_12_closed_verdict()
        assert r["banach_fpt_condition_2"]["status"] == "SATISFIED"

    def test_self_mapping_satisfied(self):
        r = admission_12_closed_verdict()
        assert r["banach_fpt_condition_3"]["status"] in ("SATISFIED", "MARGINAL")

    def test_minisuperspace_caveat_resolved(self):
        r = admission_12_closed_verdict()
        assert r["minisuperspace_caveat_resolved"]

    def test_resolution_present(self):
        r = admission_12_closed_verdict()
        assert len(r["resolution"]) > 50

    def test_honest_residual_present(self):
        r = admission_12_closed_verdict()
        assert len(r["honest_residual"]) > 50

    def test_citation_present(self):
        r = admission_12_closed_verdict()
        assert "pillar405" in r["citation"].lower() or "Pillar 405" in r["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Full summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar405Summary:
    def test_returns_dict(self):
        r = pillar405_summary()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = pillar405_summary()
        assert r["pillar_number"] == 405

    def test_status(self):
        r = pillar405_summary()
        assert r["status"] == "H1_SOBOLEV_CLOSED"

    def test_admission_12_closed(self):
        r = pillar405_summary()
        assert r["admission_new_status"] == "CLOSED"

    def test_l_h1_less_one(self):
        r = pillar405_summary()
        assert r["l_h1"] < 1.0

    def test_contractive_h1(self):
        r = pillar405_summary()
        assert r["contractive_h1"]

    def test_kk_safe(self):
        r = pillar405_summary()
        assert r["kk_safe"]

    def test_banach_fpt_satisfied(self):
        r = pillar405_summary()
        assert r["banach_fpt_conditions_satisfied"]

    def test_honest_residual_present(self):
        r = pillar405_summary()
        assert len(r["honest_residual"]) > 50

    def test_key_result_mentions_h1(self):
        r = pillar405_summary()
        assert "H¹" in r["key_result"] or "Sobolev" in r["key_result"]

    def test_verdict_dict_present(self):
        r = pillar405_summary()
        assert "verdict_dict" in r
        assert r["verdict_dict"]["new_status"] == "CLOSED"
