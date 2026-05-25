# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 459 — final L2 non-perturbative closure."""
import pytest

from src.core.pillar459_l2_np_final_closure import (
    PILLAR_STATUS,
    VERSION,
    lattice_braid_qft_requirement,
    irreducible_residual_statement,
    remaining_gap_quantification,
    lattice_observable_specification,
    beyond_5d_eft_statement,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'L2_FINAL_2PCT_NAMED_IRREDUCIBLE'

    def test_version(self):
        assert VERSION == 'v14.0'


class TestRequirement:
    def test_required_model(self):
        assert lattice_braid_qft_requirement()['required_model'] == 'SU(2)_74 WZW on a braid lattice'

    def test_k_cs(self):
        assert lattice_braid_qft_requirement()['k_cs'] == 74

    def test_goal_mentions_g_braid(self):
        assert 'g_braid' in lattice_braid_qft_requirement()['goal']

    def test_method_mentions_lattice(self):
        assert 'Lattice' in lattice_braid_qft_requirement()['method'] or 'lattice' in lattice_braid_qft_requirement()['method']


class TestResidualStatement:
    def test_status(self):
        assert irreducible_residual_statement()['status'] == PILLAR_STATUS

    def test_fraction(self):
        assert irreducible_residual_statement()['residual_fraction'] == pytest.approx(0.02)

    def test_name(self):
        assert irreducible_residual_statement()['name'] == 'LATTICE_BRAID_QFT_REQUIRED'

    def test_statement_mentions_5d_eft(self):
        assert '5D EFT' in irreducible_residual_statement()['residual_statement']


class TestGapQuantification:
    def test_gamma_gap(self):
        assert remaining_gap_quantification()['gamma_gap'] == pytest.approx(0.031)

    def test_phase2_fraction(self):
        assert remaining_gap_quantification()['phase2_covered_fraction'] == pytest.approx(0.98)

    def test_remaining_fraction(self):
        assert remaining_gap_quantification()['remaining_fraction'] == pytest.approx(0.02)

    def test_remaining_absolute_gap(self):
        assert remaining_gap_quantification()['remaining_absolute_gap'] == pytest.approx(0.031 * 0.02)

    def test_gap_fraction_of_theory_above_ten_percent(self):
        assert remaining_gap_quantification()['gamma_gap_fraction_of_theory'] > 0.1


class TestObservableSpecification:
    def test_target_parameter(self):
        assert lattice_observable_specification()['target_parameter'] == 'g_braid'

    def test_observable_mentions_connected_two_point(self):
        assert 'connected 2-point function' in lattice_observable_specification()['observable']

    def test_observable_mentions_gamma_lat(self):
        assert 'γ_lat' in lattice_observable_specification()['observable']

    def test_use_mentions_two_percent(self):
        assert '2%' in lattice_observable_specification()['use']


class TestBeyond5DEFT:
    def test_flag_true(self):
        assert beyond_5d_eft_statement()['beyond_5d_eft'] is True

    def test_statement_mentions_lattice(self):
        assert 'lattice' in beyond_5d_eft_statement()['statement'].lower()

    def test_reason_mentions_anomalous_dimension(self):
        assert 'anomalous dimension' in beyond_5d_eft_statement()['reason']


class TestQuantitativeConsistency:
    @pytest.mark.parametrize('key', ['gamma_fit', 'gamma_theory', 'gamma_gap'])
    def test_quantification_keys_present(self, key):
        assert key in remaining_gap_quantification()

    def test_gap_equals_fit_minus_theory(self):
        q = remaining_gap_quantification()
        assert q['gamma_gap'] == pytest.approx(q['gamma_fit'] - q['gamma_theory'])

    def test_phase2_plus_remaining_equals_one(self):
        q = remaining_gap_quantification()
        assert q['phase2_covered_fraction'] + q['remaining_fraction'] == pytest.approx(1.0)

    def test_remaining_is_small(self):
        assert remaining_gap_quantification()['remaining_absolute_gap'] < 0.001

    def test_residual_mentions_two_percent(self):
        assert '2%' in irreducible_residual_statement()['residual_statement']

    @pytest.mark.parametrize('snippet', ['SU(2)_74', 'connected 2-point function', 'γ_lat'])
    def test_observable_contains_required_snippets(self, snippet):
        assert snippet in lattice_observable_specification()['observable']

    def test_requirement_goal_nonempty(self):
        assert len(lattice_braid_qft_requirement()['goal']) > 20

    def test_requirement_method_nonempty(self):
        assert len(lattice_braid_qft_requirement()['method']) > 20

    def test_beyond_5d_eft_reason_nonempty(self):
        assert len(beyond_5d_eft_statement()['reason']) > 20

    def test_report_version(self):
        assert pillar_report()['version'] == VERSION

    def test_report_quantification_matches_function(self):
        assert pillar_report()['quantification'] == remaining_gap_quantification()

    def test_report_observable_matches_function(self):
        assert pillar_report()['observable'] == lattice_observable_specification()

    def test_report_requirement_matches_function(self):
        assert pillar_report()['requirement'] == lattice_braid_qft_requirement()

    def test_report_residual_matches_function(self):
        assert pillar_report()['residual'] == irreducible_residual_statement()

    def test_report_beyond_5d_matches_function(self):
        assert pillar_report()['beyond_5d_eft'] == beyond_5d_eft_statement()

    @pytest.mark.parametrize('field', ['status', 'residual_fraction', 'residual_statement', 'name'])
    def test_residual_fields_present(self, field):
        assert field in irreducible_residual_statement()

    @pytest.mark.parametrize('field', ['required_model', 'k_cs', 'goal', 'method'])
    def test_requirement_fields_present(self, field):
        assert field in lattice_braid_qft_requirement()

    @pytest.mark.parametrize('field', ['observable', 'target_parameter', 'use'])
    def test_observable_fields_present(self, field):
        assert field in lattice_observable_specification()

    @pytest.mark.parametrize('field', ['beyond_5d_eft', 'statement', 'reason'])
    def test_beyond_5d_fields_present(self, field):
        assert field in beyond_5d_eft_statement()


class TestPillarReport:
    def test_pillar_number(self):
        assert pillar_report()['pillar'] == 459

    def test_status(self):
        assert pillar_report()['status'] == PILLAR_STATUS

    def test_sections_present(self):
        report = pillar_report()
        for key in ['requirement', 'residual', 'quantification', 'observable', 'beyond_5d_eft']:
            assert key in report
