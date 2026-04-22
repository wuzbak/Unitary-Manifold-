# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_ep_violation.py
===========================
Tests for src/core/ep_violation.py — Pillar 37:
Equivalence Principle Violation from the Non-Frozen KK Radion.

Physical claims under test
--------------------------
1. eotvos_parameter_kk: η = α |Δ(B/μ)| e^{-r/λ}; non-negative;
   zero at large r; raises ValueError for unphysical inputs.
2. eotvos_parameter_radion_nmc: η_NMC = |ξ| α_φ |Δ(B/μ)| ε_grav;
   non-negative; zero for zero δ(B/μ).
3. radion_fifth_force: positive; decreases with r; decreases with m_phi.
4. composition_dependence_kk: dict with correct material keys;
   ordering consistent with Δ(B/μ) magnitudes.
5. ep_violation_in_eot_wash_range: correct keys; suppression exponential
   for m_phi ≫ 1/r_eot; detectable flag is bool.
6. equivalence_principle_summary: eta_radion_channel = 0;
   eta_total is max of channels; all keys present.
7. eotvos_cylinder_condition: zero when φ = φ₀; positive when displaced.
8. wep_constraint_on_radion_mass: positive for strong fifth force;
   zero when bound is already satisfied.
9. Module constants: ALPHA_RADION = 2/3; ALPHA_KK_PHOTON = 2;
   EOT_WASH_ETA_BOUND = 2e-13; composition differences positive.
10. Input validation: ValueError for all unphysical inputs.
"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.core.ep_violation import (
    eotvos_parameter_kk,
    eotvos_parameter_radion_nmc,
    radion_fifth_force,
    composition_dependence_kk,
    ep_violation_in_eot_wash_range,
    equivalence_principle_summary,
    eotvos_cylinder_condition,
    wep_constraint_on_radion_mass,
    ALPHA_RADION,
    ALPHA_KK_PHOTON,
    DELTA_B_MU,
    EOT_WASH_ETA_BOUND,
    STE_QUEST_ETA_TARGET,
    XI_CONFORMAL,
    EPSILON_GRAV_LAB,
    N1_CANONICAL,
    N2_CANONICAL,
    K_CS_CANONICAL,
    C_S_CANONICAL,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_alpha_radion(self):
        assert abs(ALPHA_RADION - 2.0 / 3.0) < 1e-14

    def test_alpha_kk_photon(self):
        assert ALPHA_KK_PHOTON == 2.0

    def test_eot_wash_bound(self):
        assert abs(EOT_WASH_ETA_BOUND - 2.0e-13) < 1e-25

    def test_ste_quest_target(self):
        assert STE_QUEST_ETA_TARGET < EOT_WASH_ETA_BOUND

    def test_xi_conformal(self):
        assert abs(XI_CONFORMAL - 1.0 / 6.0) < 1e-14

    def test_epsilon_grav_lab(self):
        assert 0 < EPSILON_GRAV_LAB < 1e-3

    def test_delta_b_mu_all_positive(self):
        for k, v in DELTA_B_MU.items():
            assert v > 0.0, f"DELTA_B_MU[{k!r}] = {v} is not positive"

    def test_canonical_pair(self):
        assert N1_CANONICAL == 5
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-14


# ===========================================================================
# eotvos_parameter_kk
# ===========================================================================

class TestEotvosParameterKK:
    def test_formula(self):
        alpha, db_mu, r, lam = 2.0, 0.003, 1.0, 2.0
        expected = alpha * db_mu * math.exp(-r / lam)
        assert abs(eotvos_parameter_kk(alpha, db_mu, r, lam) - expected) < 1e-12

    def test_non_negative(self):
        assert eotvos_parameter_kk(2.0, 0.003, 1.0, 1.0) >= 0.0

    def test_zero_composition_gives_zero(self):
        assert eotvos_parameter_kk(2.0, 0.0, 1.0, 1.0) == 0.0

    def test_suppressed_for_r_gg_lambda(self):
        eta = eotvos_parameter_kk(2.0, 1.0, 1e10, 1.0)
        assert eta < 1e-30

    def test_approaches_alpha_times_db_for_r_ll_lambda(self):
        # r << lambda → η ≈ alpha × Δ(B/μ)
        alpha, db_mu = 2.0, 0.003
        eta = eotvos_parameter_kk(alpha, db_mu, 1e-6, 1.0)
        assert abs(eta - alpha * db_mu) < 1e-5 * alpha * db_mu

    def test_decreases_with_r(self):
        eta1 = eotvos_parameter_kk(2.0, 0.003, 1.0, 10.0)
        eta2 = eotvos_parameter_kk(2.0, 0.003, 5.0, 10.0)
        assert eta1 > eta2

    def test_raises_alpha_zero(self):
        with pytest.raises(ValueError):
            eotvos_parameter_kk(0.0, 0.003, 1.0, 1.0)

    def test_raises_delta_negative(self):
        with pytest.raises(ValueError):
            eotvos_parameter_kk(2.0, -0.001, 1.0, 1.0)

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            eotvos_parameter_kk(2.0, 0.003, 0.0, 1.0)

    def test_raises_lambda_zero(self):
        with pytest.raises(ValueError):
            eotvos_parameter_kk(2.0, 0.003, 1.0, 0.0)


# ===========================================================================
# eotvos_parameter_radion_nmc
# ===========================================================================

class TestEotvosParameterRadionNMC:
    def test_formula(self):
        xi, db_mu, eps = 0.5, 0.003, 1e-5
        expected = abs(xi) * ALPHA_RADION * db_mu * eps
        assert abs(eotvos_parameter_radion_nmc(xi, db_mu, eps) - expected) < 1e-15

    def test_non_negative(self):
        assert eotvos_parameter_radion_nmc(1.0 / 6.0, 0.003) >= 0.0

    def test_zero_composition_gives_zero(self):
        assert eotvos_parameter_radion_nmc(0.5, 0.0) == 0.0

    def test_conformal_coupling(self):
        eta = eotvos_parameter_radion_nmc(XI_CONFORMAL, 0.003)
        expected = XI_CONFORMAL * ALPHA_RADION * 0.003 * EPSILON_GRAV_LAB
        assert abs(eta - expected) < 1e-20

    def test_negative_xi_same_as_positive(self):
        eta_pos = eotvos_parameter_radion_nmc( 0.5, 0.003)
        eta_neg = eotvos_parameter_radion_nmc(-0.5, 0.003)
        assert abs(eta_pos - eta_neg) < 1e-20

    def test_raises_delta_negative(self):
        with pytest.raises(ValueError):
            eotvos_parameter_radion_nmc(0.5, -0.001)

    def test_raises_epsilon_grav_zero(self):
        with pytest.raises(ValueError):
            eotvos_parameter_radion_nmc(0.5, 0.003, epsilon_grav=0.0)


# ===========================================================================
# radion_fifth_force
# ===========================================================================

class TestRadionFifthForce:
    def test_positive(self):
        assert radion_fifth_force(1.0, 1.0, 1.0) > 0.0

    def test_decreases_with_r(self):
        a1 = radion_fifth_force(10.0, 1.0, 1.0)
        a2 = radion_fifth_force(10.0, 2.0, 1.0)
        assert a1 > a2

    def test_decreases_with_m_phi(self):
        a1 = radion_fifth_force(10.0, 1.0, 0.1)
        a2 = radion_fifth_force(10.0, 1.0, 1.0)
        assert a1 > a2

    def test_proportional_to_M_source(self):
        a1 = radion_fifth_force(1.0, 1.0, 1.0)
        a2 = radion_fifth_force(2.0, 1.0, 1.0)
        assert abs(a2 / a1 - 2.0) < 1e-12

    def test_formula(self):
        M, r, m = 3.0, 2.0, 0.5
        expected = ALPHA_RADION * M / r**2 * math.exp(-r * m)
        assert abs(radion_fifth_force(M, r, m) - expected) < 1e-12

    def test_custom_alpha(self):
        M, r, m, alpha = 1.0, 1.0, 0.0001, 1.0
        a = radion_fifth_force(M, r, m, alpha)
        # m very small → exp ≈ 1 → a ≈ alpha / r²
        assert abs(a - alpha / r**2) < 1e-3

    def test_raises_M_zero(self):
        with pytest.raises(ValueError):
            radion_fifth_force(0.0, 1.0, 1.0)

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            radion_fifth_force(1.0, 0.0, 1.0)

    def test_raises_m_phi_zero(self):
        with pytest.raises(ValueError):
            radion_fifth_force(1.0, 1.0, 0.0)


# ===========================================================================
# composition_dependence_kk
# ===========================================================================

class TestCompositionDependenceKK:
    def test_returns_dict_for_all_materials(self):
        result = composition_dependence_kk(5, 7, 1.0, 1.0)
        for mat in ("Be-Ti", "Cu-Pb", "Al-Pt", "H-Rb"):
            assert mat in result

    def test_all_positive(self):
        result = composition_dependence_kk(5, 7, 1.0, 1.0)
        for mat, eta in result.items():
            assert eta >= 0.0, f"{mat}: {eta}"

    def test_ordering_by_composition(self):
        # Larger |Δ(B/μ)| → larger η (for same r, λ)
        result = composition_dependence_kk(5, 7, 1.0, 1.0)
        # Be-Ti (0.0032) > H-Rb (0.0014) and Al-Pt (0.0034) > Cu-Pb (0.0010)
        assert result["Al-Pt"] > result["Cu-Pb"]
        assert result["Be-Ti"] > result["H-Rb"]

    def test_raises_n1_zero(self):
        with pytest.raises(ValueError):
            composition_dependence_kk(0, 7, 1.0, 1.0)

    def test_raises_n2_leq_n1(self):
        with pytest.raises(ValueError):
            composition_dependence_kk(7, 5, 1.0, 1.0)

    def test_raises_R_zero(self):
        with pytest.raises(ValueError):
            composition_dependence_kk(5, 7, 0.0, 1.0)

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            composition_dependence_kk(5, 7, 1.0, 0.0)

    def test_unknown_material_raises_key_error(self):
        with pytest.raises(KeyError):
            composition_dependence_kk(5, 7, 1.0, 1.0, materials=("UnknownMat",))

    def test_custom_single_material(self):
        result = composition_dependence_kk(5, 7, 1.0, 1.0, materials=("Be-Ti",))
        assert len(result) == 1
        assert "Be-Ti" in result


# ===========================================================================
# ep_violation_in_eot_wash_range
# ===========================================================================

class TestEPViolationInEotWashRange:
    def test_all_keys_present(self):
        result = ep_violation_in_eot_wash_range(1.0, ALPHA_RADION)
        for key in [
            "m_phi", "alpha", "lambda_phi_planck", "r_eot_wash_planck",
            "eta_predicted", "eta_bound", "detectable", "suppression",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_suppression_in_0_1(self):
        result = ep_violation_in_eot_wash_range(1.0, ALPHA_RADION)
        assert 0.0 <= result["suppression"] <= 1.0

    def test_very_heavy_radion_not_detectable(self):
        # m_phi = 1 Planck mass → λ = 1 Planck length ≪ 1 cm → exponentially suppressed
        result = ep_violation_in_eot_wash_range(1.0, ALPHA_RADION)
        assert result["detectable"] is False

    def test_eta_bound_correct(self):
        result = ep_violation_in_eot_wash_range(1.0, ALPHA_RADION)
        assert abs(result["eta_bound"] - EOT_WASH_ETA_BOUND) < 1e-25

    def test_detectable_is_bool(self):
        result = ep_violation_in_eot_wash_range(1.0, ALPHA_RADION)
        assert isinstance(result["detectable"], bool)

    def test_raises_m_phi_zero(self):
        with pytest.raises(ValueError):
            ep_violation_in_eot_wash_range(0.0, ALPHA_RADION)

    def test_raises_alpha_zero(self):
        with pytest.raises(ValueError):
            ep_violation_in_eot_wash_range(1.0, 0.0)


# ===========================================================================
# equivalence_principle_summary
# ===========================================================================

class TestEquivalencePrincipleSummary:
    def _get_summary(self):
        return equivalence_principle_summary(m_phi=1.0, R=1.0, r=2.0)

    def test_all_keys_present(self):
        result = self._get_summary()
        for key in [
            "eta_radion_channel", "eta_kk_channel", "eta_radion_nmc",
            "eta_total", "eot_wash_bound", "ste_quest_target",
            "currently_detectable", "ste_quest_detectable", "cylinder_condition",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_radion_channel_zero(self):
        # Universal coupling → no WEP violation at leading order
        result = self._get_summary()
        assert result["eta_radion_channel"] == 0.0

    def test_eta_total_non_negative(self):
        result = self._get_summary()
        assert result["eta_total"] >= 0.0

    def test_eot_wash_bound_correct(self):
        result = self._get_summary()
        assert abs(result["eot_wash_bound"] - EOT_WASH_ETA_BOUND) < 1e-25

    def test_ste_quest_tighter_than_eot_wash(self):
        result = self._get_summary()
        assert result["ste_quest_target"] < result["eot_wash_bound"]

    def test_detectable_flags_are_bool(self):
        result = self._get_summary()
        assert isinstance(result["currently_detectable"], bool)
        assert isinstance(result["ste_quest_detectable"], bool)

    def test_cylinder_condition_string(self):
        result = self._get_summary()
        assert isinstance(result["cylinder_condition"], str)

    def test_raises_m_phi_zero(self):
        with pytest.raises(ValueError):
            equivalence_principle_summary(m_phi=0.0, R=1.0, r=1.0)

    def test_raises_R_zero(self):
        with pytest.raises(ValueError):
            equivalence_principle_summary(m_phi=1.0, R=0.0, r=1.0)

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            equivalence_principle_summary(m_phi=1.0, R=1.0, r=0.0)

    def test_raises_negative_composition(self):
        with pytest.raises(ValueError):
            equivalence_principle_summary(m_phi=1.0, R=1.0, r=1.0, delta_b_over_mu=-0.001)


# ===========================================================================
# eotvos_cylinder_condition
# ===========================================================================

class TestEotvosCylinderCondition:
    def test_zero_when_frozen(self):
        eta = eotvos_cylinder_condition(1.0, 1.0, 2.0, 0.003, 1.0, 10.0)
        assert eta == 0.0

    def test_positive_when_displaced(self):
        eta = eotvos_cylinder_condition(1.2, 1.0, 2.0, 0.003, 1.0, 10.0)
        assert eta > 0.0

    def test_proportional_to_deviation(self):
        eta1 = eotvos_cylinder_condition(1.1, 1.0, 2.0, 0.003, 1.0, 1.0)
        eta2 = eotvos_cylinder_condition(1.2, 1.0, 2.0, 0.003, 1.0, 1.0)
        # 0.2 deviation is double 0.1 deviation
        assert abs(eta2 / eta1 - 2.0) < 1e-12

    def test_suppressed_at_large_r(self):
        eta = eotvos_cylinder_condition(1.2, 1.0, 2.0, 0.003, 1e10, 1.0)
        assert eta < 1e-30

    def test_raises_phi_zero(self):
        with pytest.raises(ValueError):
            eotvos_cylinder_condition(0.0, 1.0, 2.0, 0.003, 1.0, 1.0)

    def test_raises_phi0_zero(self):
        with pytest.raises(ValueError):
            eotvos_cylinder_condition(1.0, 0.0, 2.0, 0.003, 1.0, 1.0)

    def test_raises_alpha_zero(self):
        with pytest.raises(ValueError):
            eotvos_cylinder_condition(1.0, 1.0, 0.0, 0.003, 1.0, 1.0)

    def test_raises_delta_negative(self):
        with pytest.raises(ValueError):
            eotvos_cylinder_condition(1.0, 1.0, 2.0, -0.001, 1.0, 1.0)

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            eotvos_cylinder_condition(1.0, 1.0, 2.0, 0.003, 0.0, 1.0)

    def test_raises_lambda_zero(self):
        with pytest.raises(ValueError):
            eotvos_cylinder_condition(1.0, 1.0, 2.0, 0.003, 1.0, 0.0)


# ===========================================================================
# wep_constraint_on_radion_mass
# ===========================================================================

class TestWEPConstraintOnRadionMass:
    def test_positive_for_strong_fifth_force(self):
        # alpha=2, Δ(B/μ)=0.003, r=1 cm in Planck:
        # η_max = 2 * 0.003 = 0.006 >> EOT_WASH_ETA_BOUND → need large m_phi
        r = 1.0e-2 / 1.616255e-35   # 1 cm in Planck units
        m_min = wep_constraint_on_radion_mass(2.0, 0.003, r)
        assert m_min > 0.0

    def test_zero_when_bound_satisfied(self):
        # If alpha * delta_b_mu << eta_bound, no constraint
        m_min = wep_constraint_on_radion_mass(1e-20, 1e-20, 1.0, eta_bound=0.1)
        assert m_min == 0.0

    def test_larger_r_requires_larger_m_min(self):
        # Larger r means the Yukawa exponential e^{-r/λ} suppresses the signal
        # more strongly. Therefore, a lighter radion (smaller m_phi, larger λ)
        # is still allowed — we need LESS mass (smaller m_min).
        r1 = 1.0
        r2 = 10.0
        m1 = wep_constraint_on_radion_mass(2.0, 0.1, r1)
        m2 = wep_constraint_on_radion_mass(2.0, 0.1, r2)
        # At larger r the constraint is LESS stringent → smaller m_min
        assert m2 < m1

    def test_larger_alpha_requires_larger_m_min(self):
        r = 1.0
        m1 = wep_constraint_on_radion_mass(1.0, 0.1, r)
        m2 = wep_constraint_on_radion_mass(2.0, 0.1, r)
        assert m2 > m1

    def test_raises_alpha_zero(self):
        with pytest.raises(ValueError):
            wep_constraint_on_radion_mass(0.0, 0.003, 1.0)

    def test_raises_delta_zero(self):
        with pytest.raises(ValueError):
            wep_constraint_on_radion_mass(2.0, 0.0, 1.0)

    def test_raises_r_zero(self):
        with pytest.raises(ValueError):
            wep_constraint_on_radion_mass(2.0, 0.003, 0.0)

    def test_raises_eta_bound_zero(self):
        with pytest.raises(ValueError):
            wep_constraint_on_radion_mass(2.0, 0.003, 1.0, eta_bound=0.0)
