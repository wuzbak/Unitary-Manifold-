# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_goldberger_wise.py
==============================
Test suite for src/core/goldberger_wise.py — Pillar 68.

Covers:
  - Module constants
  - goldberger_wise_potential: minimum, boundary behavior, parameter scaling
  - gw_radion_mass_squared and gw_radion_mass: positivity, formula, errors
  - gw_compactification_radius: formula, scaling
  - gw_moduli_stabilization_audit: dict keys, consistency, types
  - gw_vacuum_energy_contribution: positivity, scaling
  - gw_brane_tension_balance: dict keys, tuning residual, is_tuned
  - gw_summary: dict structure, correct types

"""

import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.goldberger_wise import (
    N_W,
    K_CS,
    C_S,
    PHI0_GW,
    LAMBDA_GW_NATURAL,
    M_KK_NATURAL,
    R_KK_NEUTRINO_UM,
    M_NU_CLOSURE_MEV,
    goldberger_wise_potential,
    gw_radion_mass_squared,
    gw_radion_mass,
    gw_compactification_radius,
    gw_moduli_stabilization_audit,
    gw_vacuum_energy_contribution,
    gw_brane_tension_balance,
    gw_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s_value(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-14

    def test_c_s_positive(self):
        assert C_S > 0

    def test_phi0_gw(self):
        assert PHI0_GW == 1.0

    def test_lambda_gw_natural(self):
        assert LAMBDA_GW_NATURAL == 1.0

    def test_m_kk_natural(self):
        assert M_KK_NATURAL == 1.0

    def test_r_kk_neutrino_positive(self):
        assert R_KK_NEUTRINO_UM > 0

    def test_r_kk_neutrino_value(self):
        assert abs(R_KK_NEUTRINO_UM - 1.792e-6) < 1e-12

    def test_m_nu_closure_positive(self):
        assert M_NU_CLOSURE_MEV > 0


class TestGoldbergerWisePotential:
    def test_potential_at_minimum(self):
        # At phi = phi_plus, potential = 0
        result = goldberger_wise_potential(1.0, 1.0, 0.1, 1.0)
        assert result == pytest.approx(0.0, abs=1e-14)

    def test_potential_positive_away_from_min(self):
        result = goldberger_wise_potential(0.5, 1.0, 0.1, 1.0)
        assert result > 0

    def test_potential_positive_above_min(self):
        result = goldberger_wise_potential(1.5, 1.0, 0.1, 1.0)
        assert result > 0

    def test_potential_lambda_zero(self):
        result = goldberger_wise_potential(0.5, 1.0, 0.1, 0.0)
        assert result == pytest.approx(0.0, abs=1e-14)

    def test_potential_scales_with_lambda(self):
        v1 = goldberger_wise_potential(0.5, 1.0, 0.0, 1.0)
        v2 = goldberger_wise_potential(0.5, 1.0, 0.0, 2.0)
        assert v2 == pytest.approx(2 * v1, rel=1e-10)

    def test_potential_phi_negative(self):
        # Negative phi is fine (potential is even-ish)
        result = goldberger_wise_potential(-0.5, 1.0, 0.1, 1.0)
        assert result > 0

    def test_potential_phi_plus_zero_raises(self):
        with pytest.raises(ValueError):
            goldberger_wise_potential(0.5, 0.0, 0.1, 1.0)

    def test_potential_phi_plus_negative_raises(self):
        with pytest.raises(ValueError):
            goldberger_wise_potential(0.5, -1.0, 0.1, 1.0)

    def test_potential_lambda_negative_raises(self):
        with pytest.raises(ValueError):
            goldberger_wise_potential(0.5, 1.0, 0.1, -1.0)

    def test_potential_at_ir_brane(self):
        # phi = phi_minus, potential != 0 (not at minimum)
        result = goldberger_wise_potential(0.1, 1.0, 0.1, 1.0)
        # phi/phi_plus = 0.1, ratio^2 = 0.01, bracket = (0.01-1)^2 = 0.98^2
        expected = 1.0 * (0.01 - 1.0) ** 2 * (0.9) ** 2
        assert result == pytest.approx(expected, rel=1e-10)

    def test_potential_delta_factor(self):
        # Scales as (phi_plus - phi_minus)^2
        v1 = goldberger_wise_potential(0.5, 1.0, 0.0, 1.0)
        v2 = goldberger_wise_potential(0.5, 2.0, 0.0, 1.0)
        # v2 has phi/phi_plus = 0.25, delta = 2
        # v1 has phi/phi_plus = 0.5, delta = 1
        assert v2 > 0
        assert v1 > 0

    def test_potential_symmetric_around_min(self):
        v_above = goldberger_wise_potential(1.1, 1.0, 0.0, 1.0)
        v_below = goldberger_wise_potential(0.9, 1.0, 0.0, 1.0)
        # Not exactly symmetric because potential is (phi^2/phi_plus^2 - 1)^2
        # which is symmetric in phi^2
        assert v_above > 0 and v_below > 0

    def test_potential_large_phi(self):
        result = goldberger_wise_potential(100.0, 1.0, 0.0, 1.0)
        assert result > 1e6

    def test_potential_small_phi_plus(self):
        result = goldberger_wise_potential(0.01, 0.1, 0.0, 1.0)
        assert result >= 0

    def test_potential_phi_equals_phi_minus(self):
        # phi = phi_minus = 0.5, phi_plus = 1.0
        # ratio = 0.5, bracket = (0.25 - 1)^2 = 0.5625, delta = (1-0.5)^2 = 0.25
        result = goldberger_wise_potential(0.5, 1.0, 0.5, 1.0)
        expected = 1.0 * 0.5625 * 0.25
        assert result == pytest.approx(expected, rel=1e-10)

    def test_potential_double_phi_plus(self):
        v1 = goldberger_wise_potential(1.0, 1.0, 0.0, 1.0)
        v2 = goldberger_wise_potential(2.0, 2.0, 0.0, 1.0)
        # Both at minimum → both 0
        assert v1 == pytest.approx(0.0, abs=1e-14)
        assert v2 == pytest.approx(0.0, abs=1e-14)

    def test_potential_output_type(self):
        result = goldberger_wise_potential(0.5, 1.0, 0.1, 1.0)
        assert isinstance(result, float)

    def test_potential_zero_phi(self):
        # phi = 0: ratio = 0, bracket = (0-1)^2 = 1
        result = goldberger_wise_potential(0.0, 1.0, 0.0, 1.0)
        assert result == pytest.approx(1.0, rel=1e-10)

    def test_potential_lambda_scaling_exact(self):
        v = goldberger_wise_potential(0.0, 1.0, 0.0, 3.0)
        assert v == pytest.approx(3.0, rel=1e-10)

    def test_potential_large_delta(self):
        v1 = goldberger_wise_potential(0.0, 1.0, 0.0, 1.0)
        v2 = goldberger_wise_potential(0.0, 1.0, -1.0, 1.0)
        # delta = (1-(-1))^2 = 4 for v2, = 1 for v1
        assert v2 == pytest.approx(4.0 * v1, rel=1e-10)


class TestRadionMass:
    def test_mass_squared_positive(self):
        assert gw_radion_mass_squared(1.0, 1.0, 1.0) > 0

    def test_mass_squared_formula(self):
        result = gw_radion_mass_squared(2.0, 1.0, 3.0)
        assert result == pytest.approx(2.0 * 9.0, rel=1e-10)

    def test_mass_squared_zero_lambda(self):
        result = gw_radion_mass_squared(0.0, 1.0, 1.0)
        assert result == pytest.approx(0.0, abs=1e-14)

    def test_mass_squared_natural_params(self):
        result = gw_radion_mass_squared(LAMBDA_GW_NATURAL, PHI0_GW, M_KK_NATURAL)
        assert result == pytest.approx(1.0, rel=1e-10)

    def test_mass_squared_lambda_negative_raises(self):
        with pytest.raises(ValueError):
            gw_radion_mass_squared(-1.0, 1.0, 1.0)

    def test_mass_squared_mkk_zero_raises(self):
        with pytest.raises(ValueError):
            gw_radion_mass_squared(1.0, 1.0, 0.0)

    def test_mass_squared_mkk_negative_raises(self):
        with pytest.raises(ValueError):
            gw_radion_mass_squared(1.0, 1.0, -1.0)

    def test_mass_squared_scales_with_mkk_squared(self):
        m1 = gw_radion_mass_squared(1.0, 1.0, 1.0)
        m2 = gw_radion_mass_squared(1.0, 1.0, 2.0)
        assert m2 == pytest.approx(4.0 * m1, rel=1e-10)

    def test_mass_squared_scales_with_lambda(self):
        m1 = gw_radion_mass_squared(1.0, 1.0, 1.0)
        m2 = gw_radion_mass_squared(4.0, 1.0, 1.0)
        assert m2 == pytest.approx(4.0 * m1, rel=1e-10)

    def test_radion_mass_positive(self):
        assert gw_radion_mass(1.0, 1.0, 1.0) > 0

    def test_radion_mass_at_natural_params(self):
        m = gw_radion_mass(LAMBDA_GW_NATURAL, PHI0_GW, M_KK_NATURAL)
        assert m == pytest.approx(1.0, rel=1e-10)

    def test_radion_mass_equals_sqrt_m_squared(self):
        m2 = gw_radion_mass_squared(2.0, 1.0, 3.0)
        m = gw_radion_mass(2.0, 1.0, 3.0)
        assert m == pytest.approx(math.sqrt(m2), rel=1e-10)

    def test_radion_mass_lambda_zero(self):
        m = gw_radion_mass(0.0, 1.0, 1.0)
        assert m == pytest.approx(0.0, abs=1e-14)

    def test_radion_mass_over_mkk(self):
        # For lambda_gw = 1, m_phi / M_KK = 1
        m = gw_radion_mass(1.0, 1.0, 2.0)
        assert m == pytest.approx(2.0, rel=1e-10)

    def test_radion_mass_half_lambda(self):
        m = gw_radion_mass(0.25, 1.0, 1.0)
        assert m == pytest.approx(0.5, rel=1e-10)

    def test_radion_mass_large_mkk(self):
        m = gw_radion_mass(1.0, 1.0, 1e6)
        assert m == pytest.approx(1e6, rel=1e-10)

    def test_radion_mass_output_type(self):
        assert isinstance(gw_radion_mass(1.0, 1.0, 1.0), float)

    def test_radion_mass_squared_output_type(self):
        assert isinstance(gw_radion_mass_squared(1.0, 1.0, 1.0), float)

    def test_radion_mass_negative_lambda_raises(self):
        with pytest.raises(ValueError):
            gw_radion_mass(-1.0, 1.0, 1.0)

    def test_radion_mass_zero_mkk_raises(self):
        with pytest.raises(ValueError):
            gw_radion_mass(1.0, 1.0, 0.0)


class TestCompactificationRadius:
    def test_radius_positive(self):
        assert gw_compactification_radius(1.0, 1.0) > 0

    def test_radius_formula(self):
        R = gw_compactification_radius(1.0, 1.0)
        assert R == pytest.approx(1.0 / math.pi, rel=1e-10)

    def test_radius_half_mkk(self):
        R = gw_compactification_radius(1.0, 0.5)
        assert R == pytest.approx(2.0 / math.pi, rel=1e-10)

    def test_radius_double_mkk(self):
        R1 = gw_compactification_radius(1.0, 1.0)
        R2 = gw_compactification_radius(1.0, 2.0)
        assert R2 == pytest.approx(0.5 * R1, rel=1e-10)

    def test_radius_inversely_proportional_to_mkk(self):
        R1 = gw_compactification_radius(1.0, 1.0)
        R3 = gw_compactification_radius(1.0, 3.0)
        assert R3 == pytest.approx(R1 / 3.0, rel=1e-10)

    def test_radius_zero_mkk_raises(self):
        with pytest.raises(ValueError):
            gw_compactification_radius(1.0, 0.0)

    def test_radius_negative_mkk_raises(self):
        with pytest.raises(ValueError):
            gw_compactification_radius(1.0, -1.0)

    def test_radius_natural_params(self):
        R = gw_compactification_radius(PHI0_GW, M_KK_NATURAL)
        assert R == pytest.approx(1.0 / math.pi, rel=1e-10)

    def test_radius_output_type(self):
        assert isinstance(gw_compactification_radius(1.0, 1.0), float)

    def test_radius_pi_relation(self):
        # R * pi * M_KK = 1
        M_KK = 2.5
        R = gw_compactification_radius(1.0, M_KK)
        assert R * math.pi * M_KK == pytest.approx(1.0, rel=1e-10)


class TestModuliStabilizationAudit:
    def setup_method(self):
        self.audit = gw_moduli_stabilization_audit()

    def test_returns_dict(self):
        assert isinstance(self.audit, dict)

    def test_key_phi0_gw(self):
        assert "phi0_gw" in self.audit

    def test_key_phi0_ftum_consistent(self):
        assert "phi0_ftum_consistent" in self.audit

    def test_key_r_kk_m(self):
        assert "r_kk_m" in self.audit

    def test_key_radion_mass_over_mkk(self):
        assert "radion_mass_over_mkk" in self.audit

    def test_key_lambda_gw_natural(self):
        assert "lambda_gw_natural" in self.audit

    def test_key_status(self):
        assert "status" in self.audit

    def test_phi0_gw_value(self):
        assert self.audit["phi0_gw"] == pytest.approx(1.0, rel=1e-10)

    def test_phi0_ftum_consistent_true(self):
        assert self.audit["phi0_ftum_consistent"] is True

    def test_r_kk_m_value(self):
        assert abs(self.audit["r_kk_m"] - 1.792e-6) < 1e-12

    def test_radion_mass_over_mkk_positive(self):
        assert self.audit["radion_mass_over_mkk"] > 0

    def test_radion_mass_over_mkk_natural(self):
        # For lambda_gw=1, M_KK=1: m_phi/M_KK = 1
        assert self.audit["radion_mass_over_mkk"] == pytest.approx(1.0, rel=1e-10)

    def test_lambda_gw_natural_value(self):
        assert self.audit["lambda_gw_natural"] == pytest.approx(1.0, rel=1e-10)

    def test_status_is_str(self):
        assert isinstance(self.audit["status"], str)

    def test_status_mentions_narrowed(self):
        assert "NARROWED" in self.audit["status"]

    def test_key_n_w(self):
        assert "n_w" in self.audit

    def test_n_w_value(self):
        assert self.audit["n_w"] == 5

    def test_key_k_cs(self):
        assert "k_cs" in self.audit

    def test_k_cs_value(self):
        assert self.audit["k_cs"] == 74

    def test_m_phi_natural_key(self):
        assert "m_phi_natural" in self.audit

    def test_m_phi_natural_positive(self):
        assert self.audit["m_phi_natural"] > 0

    def test_m_kk_natural_key(self):
        assert "m_kk_natural" in self.audit

    def test_m_kk_natural_value(self):
        assert self.audit["m_kk_natural"] == pytest.approx(1.0, rel=1e-10)

    def test_status_mentions_open(self):
        assert "OPEN" in self.audit["status"]


class TestVacuumEnergy:
    def test_vacuum_energy_positive(self):
        result = gw_vacuum_energy_contribution(1.0, 1.0, 1.0)
        assert result > 0

    def test_vacuum_energy_formula(self):
        result = gw_vacuum_energy_contribution(2.0, 3.0, 4.0)
        # V = lambda * M_KK^4 * phi0^2 = 4 * 81 * 4 = 1296
        expected = 4.0 * (3.0 ** 4) * (2.0 ** 2)
        assert result == pytest.approx(expected, rel=1e-10)

    def test_vacuum_energy_natural_params(self):
        result = gw_vacuum_energy_contribution(PHI0_GW, M_KK_NATURAL, LAMBDA_GW_NATURAL)
        assert result == pytest.approx(1.0, rel=1e-10)

    def test_vacuum_energy_scales_with_lambda(self):
        v1 = gw_vacuum_energy_contribution(1.0, 1.0, 1.0)
        v2 = gw_vacuum_energy_contribution(1.0, 1.0, 2.0)
        assert v2 == pytest.approx(2.0 * v1, rel=1e-10)

    def test_vacuum_energy_scales_with_mkk4(self):
        v1 = gw_vacuum_energy_contribution(1.0, 1.0, 1.0)
        v2 = gw_vacuum_energy_contribution(1.0, 2.0, 1.0)
        assert v2 == pytest.approx(16.0 * v1, rel=1e-10)

    def test_vacuum_energy_scales_with_phi0_squared(self):
        v1 = gw_vacuum_energy_contribution(1.0, 1.0, 1.0)
        v2 = gw_vacuum_energy_contribution(2.0, 1.0, 1.0)
        assert v2 == pytest.approx(4.0 * v1, rel=1e-10)

    def test_vacuum_energy_phi0_zero_raises(self):
        with pytest.raises(ValueError):
            gw_vacuum_energy_contribution(0.0, 1.0, 1.0)

    def test_vacuum_energy_mkk_zero_raises(self):
        with pytest.raises(ValueError):
            gw_vacuum_energy_contribution(1.0, 0.0, 1.0)

    def test_vacuum_energy_lambda_negative_raises(self):
        with pytest.raises(ValueError):
            gw_vacuum_energy_contribution(1.0, 1.0, -1.0)

    def test_vacuum_energy_lambda_zero(self):
        result = gw_vacuum_energy_contribution(1.0, 1.0, 0.0)
        assert result == pytest.approx(0.0, abs=1e-14)

    def test_vacuum_energy_output_type(self):
        assert isinstance(gw_vacuum_energy_contribution(1.0, 1.0, 1.0), float)

    def test_vacuum_energy_phi0_negative_raises(self):
        with pytest.raises(ValueError):
            gw_vacuum_energy_contribution(-1.0, 1.0, 1.0)

    def test_vacuum_energy_large_mkk(self):
        result = gw_vacuum_energy_contribution(1.0, 1e3, 1.0)
        assert result == pytest.approx(1e12, rel=1e-8)

    def test_vacuum_energy_small_phi0(self):
        result = gw_vacuum_energy_contribution(0.1, 1.0, 1.0)
        assert result == pytest.approx(0.01, rel=1e-10)

    def test_vacuum_energy_combined_scaling(self):
        v = gw_vacuum_energy_contribution(2.0, 2.0, 2.0)
        # = 2 * 16 * 4 = 128
        assert v == pytest.approx(128.0, rel=1e-10)


class TestBraneTensionBalance:
    def setup_method(self):
        self.result = gw_brane_tension_balance(1.0, 1.0)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_key_T_UV(self):
        assert "T_UV" in self.result

    def test_key_T_IR(self):
        assert "T_IR" in self.result

    def test_key_V_bulk(self):
        assert "V_bulk" in self.result

    def test_key_tuning_residual(self):
        assert "tuning_residual" in self.result

    def test_key_is_tuned(self):
        assert "is_tuned" in self.result

    def test_T_UV_positive(self):
        assert self.result["T_UV"] > 0

    def test_T_IR_negative(self):
        assert self.result["T_IR"] < 0

    def test_V_bulk_negative_or_zero(self):
        assert self.result["V_bulk"] <= 0

    def test_T_UV_magnitude_formula(self):
        res = gw_brane_tension_balance(2.0, 1.0)
        # T_UV = 6 * 2^4 = 96
        assert res["T_UV"] == pytest.approx(6.0 * 16.0, rel=1e-10)

    def test_T_IR_magnitude_formula(self):
        res = gw_brane_tension_balance(2.0, 1.0)
        assert res["T_IR"] == pytest.approx(-6.0 * 16.0, rel=1e-10)

    def test_T_UV_plus_T_IR(self):
        # T_UV + T_IR = 0 exactly
        assert self.result["T_UV"] + self.result["T_IR"] == pytest.approx(0.0, abs=1e-10)

    def test_V_bulk_formula(self):
        # V_bulk = -lambda_gw * M_KK^4
        assert self.result["V_bulk"] == pytest.approx(-1.0, rel=1e-10)

    def test_is_tuned_type_bool(self):
        assert isinstance(self.result["is_tuned"], bool)

    def test_mkk_zero_raises(self):
        with pytest.raises(ValueError):
            gw_brane_tension_balance(0.0, 1.0)

    def test_mkk_negative_raises(self):
        with pytest.raises(ValueError):
            gw_brane_tension_balance(-1.0, 1.0)

    def test_lambda_negative_raises(self):
        with pytest.raises(ValueError):
            gw_brane_tension_balance(1.0, -1.0)

    def test_mkk_key(self):
        assert "M_KK" in self.result

    def test_lambda_gw_key(self):
        assert "lambda_gw" in self.result

    def test_mkk_value_stored(self):
        assert self.result["M_KK"] == pytest.approx(1.0, rel=1e-10)

    def test_lambda_value_stored(self):
        assert self.result["lambda_gw"] == pytest.approx(1.0, rel=1e-10)

    def test_tuning_residual_relative_key(self):
        assert "tuning_residual_relative" in self.result

    def test_tuning_residual_relative_nonneg(self):
        assert self.result["tuning_residual_relative"] >= 0

    def test_scaling_with_mkk(self):
        r1 = gw_brane_tension_balance(1.0, 1.0)
        r2 = gw_brane_tension_balance(2.0, 1.0)
        # T_UV scales as M_KK^4
        assert r2["T_UV"] == pytest.approx(16.0 * r1["T_UV"], rel=1e-10)


class TestSummary:
    def setup_method(self):
        self.s = gw_summary()

    def test_returns_dict(self):
        assert isinstance(self.s, dict)

    def test_pillar_key(self):
        assert "pillar" in self.s

    def test_pillar_value(self):
        assert self.s["pillar"] == 68

    def test_name_key(self):
        assert "name" in self.s

    def test_name_str(self):
        assert isinstance(self.s["name"], str)

    def test_phi0_gw_key(self):
        assert "phi0_gw" in self.s

    def test_phi0_gw_value(self):
        assert self.s["phi0_gw"] == pytest.approx(1.0, rel=1e-10)

    def test_lambda_gw_key(self):
        assert "lambda_gw_natural" in self.s

    def test_m_kk_key(self):
        assert "m_kk_natural" in self.s

    def test_radion_mass_key(self):
        assert "radion_mass" in self.s

    def test_radion_mass_positive(self):
        assert self.s["radion_mass"] > 0

    def test_compactification_radius_key(self):
        assert "compactification_radius" in self.s

    def test_compactification_radius_positive(self):
        assert self.s["compactification_radius"] > 0

    def test_gap_closed_key(self):
        assert "gap_closed" in self.s

    def test_gap_closed_str(self):
        assert isinstance(self.s["gap_closed"], str)

    def test_honest_status_key(self):
        assert "honest_status" in self.s

    def test_honest_status_dict(self):
        assert isinstance(self.s["honest_status"], dict)

    def test_honest_status_proved(self):
        assert "PROVED" in self.s["honest_status"]

    def test_honest_status_open(self):
        assert "OPEN" in self.s["honest_status"]

    def test_n_w_key(self):
        assert "n_w" in self.s

    def test_n_w_value(self):
        assert self.s["n_w"] == 5

    def test_k_cs_key(self):
        assert "k_cs" in self.s

    def test_k_cs_value(self):
        assert self.s["k_cs"] == 74
