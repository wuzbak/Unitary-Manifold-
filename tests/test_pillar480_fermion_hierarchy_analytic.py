# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 480 — Fermion Hierarchy Analytic FN Charge Formula."""
from __future__ import annotations

import math

from src.core.pillar480_fermion_hierarchy_analytic import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    DELTA_C,
    DELTA_KT,
    M_TOP_GEV,
    SM_FERMION_MASSES,
    ell_eff,
    delta_fn,
    uv_correction,
    predicted_mass,
    residual_dex,
    fermion_assignment,
    all_fermion_assignments,
    naturalness_verdict,
    analytic_formula_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'FERMION_HIERARCHY_ANALYTIC_FORMULA_DERIVED'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 480

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_delta_c(self):
        assert abs(DELTA_C - 5.0/74.0) < 1e-10

    def test_delta_kt(self):
        assert abs(DELTA_KT - 0.053) < 1e-6

    def test_m_top(self):
        assert abs(M_TOP_GEV - 172.69) < 0.01

    def test_nine_fermions(self):
        assert len(SM_FERMION_MASSES) == 9

    def test_has_all_fermions(self):
        expected = {'top', 'bottom', 'charm', 'strange', 'up', 'down', 'tau', 'muon', 'electron'}
        assert set(SM_FERMION_MASSES.keys()) == expected


class TestEllEff:
    def test_top_is_zero(self):
        ell = ell_eff(M_TOP_GEV, M_TOP_GEV)
        assert abs(ell) < 1e-10

    def test_lighter_than_top(self):
        # All other fermions should have ell > 0
        for name, mass in SM_FERMION_MASSES.items():
            if name != 'top':
                ell = ell_eff(mass, M_TOP_GEV)
                assert ell > 0, f"ell({name}) should be > 0"

    def test_electron_large_ell(self):
        ell = ell_eff(SM_FERMION_MASSES['electron'], M_TOP_GEV)
        # electron is lightest charged fermion → largest ℓ_eff
        # -ln(0.000511/172.69)/5 = 12.73/5 = 2.546
        assert ell > 2.0

    def test_bottom_smaller_than_electron(self):
        ell_b = ell_eff(SM_FERMION_MASSES['bottom'], M_TOP_GEV)
        ell_e = ell_eff(SM_FERMION_MASSES['electron'], M_TOP_GEV)
        assert ell_b < ell_e

    def test_inverse_of_predicted_mass(self):
        # Should be exact inverse
        for name, mass in SM_FERMION_MASSES.items():
            ell = ell_eff(mass, M_TOP_GEV)
            m_back = predicted_mass(ell, M_TOP_GEV)
            assert abs(m_back / mass - 1.0) < 1e-10, f"Round-trip failed for {name}"

    def test_zero_mass_returns_zero(self):
        assert ell_eff(0.0) == 0.0


class TestDeltaFN:
    def test_returns_tuple(self):
        result = delta_fn(SM_FERMION_MASSES['bottom'])
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_frac_part_in_range(self):
        for name, mass in SM_FERMION_MASSES.items():
            _, dfn = delta_fn(mass)
            assert 0.0 <= dfn < 1.0, f"δ_FN({name}) = {dfn} not in [0,1)"

    def test_top_zero(self):
        ell_int, dfn = delta_fn(M_TOP_GEV)
        assert ell_int == 0
        assert abs(dfn) < 1e-10

    def test_integer_plus_frac(self):
        for name, mass in SM_FERMION_MASSES.items():
            ell = ell_eff(mass)
            ell_int, dfn = delta_fn(mass)
            assert abs(ell_int + dfn - ell) < 1e-10


class TestUVCorrection:
    def test_returns_float(self):
        assert isinstance(uv_correction(0.7), float)

    def test_uv_localized_positive(self):
        # c_f > 1/2: UV-localized → positive correction
        assert uv_correction(0.7) > 0.0

    def test_ir_localized_negative(self):
        # c_f < 1/2: IR-localized → negative correction
        assert uv_correction(0.3) < 0.0

    def test_at_boundary_zero(self):
        # c_f = 0.5: g(c_f) = 0
        assert abs(uv_correction(0.5)) < 1e-10

    def test_scale_with_delta_kt(self):
        d1 = uv_correction(0.7, delta_kt=0.05)
        d2 = uv_correction(0.7, delta_kt=0.10)
        assert d2 > d1


class TestPredictedMass:
    def test_at_zero_ell(self):
        assert abs(predicted_mass(0.0) - M_TOP_GEV) < 1e-10

    def test_positive(self):
        assert predicted_mass(2.0) > 0.0

    def test_decreases_with_ell(self):
        m1 = predicted_mass(1.0)
        m2 = predicted_mass(3.0)
        assert m1 > m2

    def test_exponential(self):
        # m = m_t × exp(-5ℓ)
        ell = 2.0
        expected = M_TOP_GEV * math.exp(-5.0 * ell)
        assert abs(predicted_mass(ell) - expected) < 1e-10


class TestResidualDex:
    def test_exact_match(self):
        assert residual_dex(1.0, 1.0) < 1e-10

    def test_factor_10(self):
        # log10(10) = 1.0 dex
        assert abs(residual_dex(10.0, 1.0) - 1.0) < 1e-10

    def test_factor_root10(self):
        # log10(√10) = 0.5 dex
        assert abs(residual_dex(10.0**0.5, 1.0) - 0.5) < 1e-10

    def test_symmetric(self):
        assert abs(residual_dex(0.1, 1.0) - residual_dex(10.0, 1.0)) < 1e-10


class TestFermionAssignment:
    def test_top_reference(self):
        a = fermion_assignment('top', M_TOP_GEV)
        assert a['ell_int'] == 0
        assert a['status'] == 'DERIVED'

    def test_returns_dict(self):
        a = fermion_assignment('bottom', SM_FERMION_MASSES['bottom'])
        assert isinstance(a, dict)

    def test_has_all_keys(self):
        a = fermion_assignment('charm', SM_FERMION_MASSES['charm'])
        required = ['ell_eff', 'ell_int', 'delta_fn', 'm_predicted_eff', 'residual_dex_eff']
        for k in required:
            assert k in a

    def test_eff_residual_zero(self):
        # Predicted mass from ell_eff should exactly reproduce measured mass
        for name, mass in SM_FERMION_MASSES.items():
            a = fermion_assignment(name, mass)
            assert a['residual_dex_eff'] < 1e-8, f"Effective residual for {name} should be ~0"


class TestAllFermionAssignments:
    def setup_method(self):
        self.assignments = all_fermion_assignments()

    def test_returns_list(self):
        assert isinstance(self.assignments, list)

    def test_nine_fermions(self):
        assert len(self.assignments) == 9

    def test_all_delta_fn_less_than_one(self):
        for a in self.assignments:
            assert a['delta_fn'] < 1.0, f"δ_FN({a['name']}) = {a['delta_fn']:.3f} >= 1.0"

    def test_all_eff_residual_near_zero(self):
        for a in self.assignments:
            assert a['residual_dex_eff'] < 1e-8

    def test_top_is_derived(self):
        top = next(a for a in self.assignments if a['name'] == 'top')
        assert top['status'] == 'DERIVED'


class TestNaturalnessVerdict:
    def setup_method(self):
        self.verdict = naturalness_verdict()

    def test_returns_dict(self):
        assert isinstance(self.verdict, dict)

    def test_nine_fermions(self):
        assert self.verdict['n_fermions'] == 9

    def test_all_geometric_natural(self):
        assert self.verdict['all_geometric'] is True

    def test_verdict_all_9(self):
        assert '9' in self.verdict['verdict']

    def test_analytic_formula_stated(self):
        assert 'ℓ_eff' in self.verdict['analytic_formula']
        assert 'n_w=5' in self.verdict['analytic_formula'] or 'n_w' in self.verdict['analytic_formula']

    def test_status_matches(self):
        assert self.verdict['status'] == PILLAR_STATUS


class TestAnalyticFormulaReport:
    def setup_method(self):
        self.report = analytic_formula_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_status(self):
        assert self.report['status'] == 'FERMION_HIERARCHY_ANALYTIC_FORMULA_DERIVED'

    def test_formula_present(self):
        assert 'formula' in self.report
        assert 'expression' in self.report['formula']

    def test_zero_free_parameters(self):
        assert self.report['formula']['free_parameters'] == 0

    def test_fermion_table_nine(self):
        assert len(self.report['fermion_table']) == 9

    def test_progression_shows_history(self):
        prog = self.report['progression']
        assert 'P411' in prog
        assert 'P480' in prog

    def test_all_geometric_natural(self):
        assert self.report['naturalness']['all_geometric'] is True
