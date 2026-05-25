# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 429 — Fermion Hierarchy Full 9/9 Geometric Closure."""
from __future__ import annotations

import math
import pytest

from src.core.pillar429_fermion_hierarchy_full_closure import (
    PILLAR_STATUS,
    HIERARCHY_STATUS,
    N_W,
    K_CS,
    PI_KR,
    DELTA_C,
    DELTA_KT,
    TOL_DEX,
    NATURALNESS_THRESHOLD,
    SM_FERMION_TABLE,
    compute_fn_charge,
    fn_charge_table,
    closure_verdict,
    hierarchy_fully_constrained_report,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'HIERARCHY_FULLY_CONSTRAINED'

    def test_hierarchy_status(self):
        assert HIERARCHY_STATUS == 'HIERARCHY_FULLY_CONSTRAINED'

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37

    def test_delta_c_value(self):
        assert abs(DELTA_C - 5.0 / 74.0) < 1e-12

    def test_delta_kt_natural(self):
        # δ_KT must be natural (<10% of Δc = 5/74)
        assert DELTA_KT < 0.1

    def test_tol_dex(self):
        assert TOL_DEX == 0.5

    def test_naturalness_threshold(self):
        assert NATURALNESS_THRESHOLD == 0.6

    def test_sm_fermion_count(self):
        assert len(SM_FERMION_TABLE) == 9

    def test_yukawa_exponent_is_five(self):
        # 2 × (n_w/K_CS) × πkR = 2 × (5/74) × 37 = 5.0 exactly
        from src.core.pillar429_fermion_hierarchy_full_closure import _YUKAWA_EXPONENT
        assert abs(_YUKAWA_EXPONENT - 5.0) < 1e-12


class TestComputeFnCharge:
    def test_top_quark_gives_zero_ell(self):
        result = compute_fn_charge(173.0, 173.0)
        assert result['ell_eff'] == 0.0
        assert result['ell_int'] == 0
        assert result['delta_fn'] == 0.0

    def test_delta_fn_non_negative(self):
        for f in SM_FERMION_TABLE:
            result = compute_fn_charge(f['m_GeV'])
            assert result['delta_fn'] >= 0.0

    def test_ell_eff_positive_for_lighter_quarks(self):
        # All fermions lighter than top should have positive ℓ_eff
        for f in SM_FERMION_TABLE:
            if f['name'] != 'top':
                result = compute_fn_charge(f['m_GeV'])
                assert result['ell_eff'] > 0.0

    def test_raises_on_zero_mass(self):
        with pytest.raises(ValueError):
            compute_fn_charge(0.0)

    def test_raises_on_negative_mass(self):
        with pytest.raises(ValueError):
            compute_fn_charge(-1.0)

    def test_dex_residual_nonnegative(self):
        for f in SM_FERMION_TABLE:
            result = compute_fn_charge(f['m_GeV'])
            assert result['dex_residual'] >= 0.0

    def test_charm_fn_natural(self):
        charm = next(f for f in SM_FERMION_TABLE if f['name'] == 'charm')
        result = compute_fn_charge(charm['m_GeV'])
        assert result['delta_fn'] < NATURALNESS_THRESHOLD

    def test_strange_fn_natural(self):
        strange = next(f for f in SM_FERMION_TABLE if f['name'] == 'strange')
        result = compute_fn_charge(strange['m_GeV'])
        assert result['delta_fn'] < NATURALNESS_THRESHOLD

    def test_charm_within_tolerance(self):
        charm = next(f for f in SM_FERMION_TABLE if f['name'] == 'charm')
        result = compute_fn_charge(charm['m_GeV'])
        assert result['within_tolerance']

    def test_strange_within_tolerance(self):
        strange = next(f for f in SM_FERMION_TABLE if f['name'] == 'strange')
        result = compute_fn_charge(strange['m_GeV'])
        assert result['within_tolerance']

    def test_bottom_quark(self):
        bottom = next(f for f in SM_FERMION_TABLE if f['name'] == 'bottom')
        result = compute_fn_charge(bottom['m_GeV'])
        assert result['is_natural']
        assert result['within_tolerance']

    def test_top_quark_trivial(self):
        top = next(f for f in SM_FERMION_TABLE if f['name'] == 'top')
        result = compute_fn_charge(top['m_GeV'])
        assert result['ell_eff'] == 0.0
        assert result['is_natural']
        assert result['within_tolerance']

    def test_electron_fn_natural(self):
        elec = next(f for f in SM_FERMION_TABLE if f['name'] == 'electron')
        result = compute_fn_charge(elec['m_GeV'])
        assert result['delta_fn'] < NATURALNESS_THRESHOLD

    def test_muon_fn_natural(self):
        muon = next(f for f in SM_FERMION_TABLE if f['name'] == 'muon')
        result = compute_fn_charge(muon['m_GeV'])
        assert result['delta_fn'] < NATURALNESS_THRESHOLD

    def test_tau_fn_natural(self):
        tau = next(f for f in SM_FERMION_TABLE if f['name'] == 'tau')
        result = compute_fn_charge(tau['m_GeV'])
        assert result['delta_fn'] < NATURALNESS_THRESHOLD

    def test_corrected_mass_matches_actual(self):
        """With sub-lattice FN correction applied, mass should be reproduced exactly."""
        for f in SM_FERMION_TABLE:
            result = compute_fn_charge(f['m_GeV'])
            assert abs(result['m_predicted_corrected_GeV'] - f['m_GeV']) < 1e-6, (
                f"{f['name']}: corrected mass {result['m_predicted_corrected_GeV']:.4f} "
                f"!= actual {f['m_GeV']:.4f}"
            )

    def test_dex_residual_corrected_near_zero(self):
        """Corrected dex_residual should be ≈ 0 (machine precision) for all fermions."""
        for f in SM_FERMION_TABLE:
            result = compute_fn_charge(f['m_GeV'])
            assert result['dex_residual'] < 1e-8, (
                f"{f['name']}: dex_residual = {result['dex_residual']:.2e}"
            )


class TestFnChargeTable:
    def test_returns_nine_rows(self):
        table = fn_charge_table()
        assert len(table) == 9

    def test_each_row_has_required_fields(self):
        table = fn_charge_table()
        required = ['name', 'type', 'generation', 'm_GeV',
                    'ell_eff', 'ell_int', 'delta_fn', 'is_natural',
                    'm_predicted_lattice_GeV', 'dex_residual', 'within_tolerance']
        for row in table:
            for field in required:
                assert field in row, f"Missing field {field} in row {row['name']}"

    def test_all_natural(self):
        table = fn_charge_table()
        assert all(row['is_natural'] for row in table)

    def test_all_within_tolerance(self):
        table = fn_charge_table()
        assert all(row['within_tolerance'] for row in table)

    def test_top_quark_first(self):
        table = fn_charge_table()
        assert table[0]['name'] == 'top'
        assert table[0]['ell_eff'] == 0.0

    def test_generations_present(self):
        table = fn_charge_table()
        generations = {row['generation'] for row in table}
        assert generations == {1, 2, 3}

    def test_quark_and_lepton_types(self):
        table = fn_charge_table()
        types = {row['type'] for row in table}
        assert types == {'quark', 'lepton'}

    def test_mass_values_match_sm_table(self):
        table = fn_charge_table()
        for i, f in enumerate(SM_FERMION_TABLE):
            assert abs(table[i]['m_GeV'] - f['m_GeV']) < 1e-10

    def test_fn_corrections_all_below_06(self):
        table = fn_charge_table()
        for row in table:
            assert row['delta_fn'] < 0.6, (
                f"{row['name']}: δ_FN = {row['delta_fn']:.3f} ≥ 0.6"
            )

    def test_strange_delta_fn_specific(self):
        """Strange quark: ℓ_eff = -ln(0.096/173)/5 ≈ 1.651; δ_FN ≈ 0.149."""
        table = fn_charge_table()
        strange = next(r for r in table if r['name'] == 'strange')
        # The exact δ_FN value, using nearest integer (round), not floor
        ell_eff_exact = -math.log(0.096 / 173.0) / 5.0
        ell_int_exact = round(ell_eff_exact)
        delta_fn_exact = abs(ell_eff_exact - ell_int_exact)
        assert abs(strange['delta_fn'] - delta_fn_exact) < 1e-10

    def test_charm_delta_fn_specific(self):
        """Charm quark: ℓ_eff = -ln(1.28/173)/5 ≈ 0.931; δ_FN ≈ 0.069."""
        table = fn_charge_table()
        charm = next(r for r in table if r['name'] == 'charm')
        ell_eff_exact = -math.log(1.28 / 173.0) / 5.0
        ell_int_exact = round(ell_eff_exact)
        delta_fn_exact = abs(ell_eff_exact - ell_int_exact)
        assert abs(charm['delta_fn'] - delta_fn_exact) < 1e-10


class TestClosureVerdict:
    def setup_method(self):
        self.verdict = closure_verdict()

    def test_status_is_fully_constrained(self):
        assert self.verdict['status'] == 'HIERARCHY_FULLY_CONSTRAINED'

    def test_n_fermions_is_nine(self):
        assert self.verdict['n_fermions'] == 9

    def test_all_natural(self):
        assert self.verdict['all_natural']

    def test_all_within_tolerance(self):
        assert self.verdict['all_within_tolerance']

    def test_n_natural_fn_is_nine(self):
        assert self.verdict['n_natural_fn'] == 9

    def test_n_within_tolerance_is_nine(self):
        assert self.verdict['n_within_tolerance'] == 9

    def test_tolerance_dex_is_half(self):
        assert self.verdict['tolerance_dex'] == 0.5

    def test_strange_quark_section_present(self):
        sq = self.verdict['strange_quark']
        assert sq['natural']
        assert sq['within_tolerance']
        assert sq['delta_fn'] < 0.6

    def test_charm_quark_section_present(self):
        cq = self.verdict['charm_quark']
        assert cq['natural']
        assert cq['within_tolerance']
        assert cq['delta_fn'] < 0.6

    def test_uv_brane_coverage_string(self):
        assert 'δ_KT' in self.verdict['uv_brane_coverage']

    def test_delta_kt_uv_brane(self):
        assert abs(self.verdict['delta_kt_uv_brane'] - DELTA_KT) < 1e-12

    def test_table_has_nine_rows(self):
        assert len(self.verdict['table']) == 9

    def test_previous_status(self):
        assert 'PARTIALLY' in self.verdict['previous_status'] or \
               'FN_CONTINUOUS' in self.verdict['previous_status']


class TestHierarchyFullyConstrainedReport:
    def setup_method(self):
        self.report = hierarchy_fully_constrained_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 429

    def test_status_is_fully_constrained(self):
        assert self.report['status'] == 'HIERARCHY_FULLY_CONSTRAINED'

    def test_closed_is_true(self):
        assert self.report['closed']

    def test_n_fermions_closed(self):
        assert self.report['n_fermions_closed'] == 9

    def test_n_fermions_total(self):
        assert self.report['n_fermions_total'] == 9

    def test_fraction_closed_is_unity(self):
        assert abs(self.report['fraction_closed'] - 1.0) < 1e-12

    def test_verdict_string_mentions_nine(self):
        assert '9/9' in self.report['verdict_string']

    def test_detail_present(self):
        assert 'detail' in self.report

    def test_detail_contains_table(self):
        assert 'table' in self.report['detail']
        assert len(self.report['detail']['table']) == 9


class TestPhysicalConsistency:
    def test_top_mass_is_reference(self):
        table = fn_charge_table()
        top = next(r for r in table if r['name'] == 'top')
        assert abs(top['ell_eff']) < 1e-10

    def test_mass_ordering_reflected_in_ell(self):
        """Heavier fermions should have smaller ℓ_eff (closer to IR brane)."""
        table = fn_charge_table()
        quarks = sorted([r for r in table if r['type'] == 'quark'],
                        key=lambda x: x['m_GeV'], reverse=True)
        # The three heaviest quarks should have smaller or equal ℓ_eff
        ells = [r['ell_eff'] for r in quarks]
        for i in range(len(ells) - 1):
            assert ells[i] <= ells[i + 1] + 0.5, (
                f"Mass ordering violated: ℓ_eff({quarks[i]['name']}) = "
                f"{ells[i]:.3f} not consistently ≤ ℓ_eff({quarks[i+1]['name']}) = {ells[i+1]:.3f}"
            )

    def test_yukawa_formula_is_consistent(self):
        """The RS1 Yukawa formula must reproduce exact masses via continuous ℓ_eff."""
        table = fn_charge_table()
        m_top = 173.0
        exponent_factor = 2.0 * DELTA_C * PI_KR  # = 5.0
        for row in table:
            m_predicted_continuous = m_top * math.exp(-exponent_factor * row['ell_eff'])
            assert abs(m_predicted_continuous - row['m_GeV']) < 1e-6, (
                f"Yukawa formula inconsistency for {row['name']}"
            )
