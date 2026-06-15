# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 461 — PMNS-to-p_R derivation attempt."""
import pytest

from src.core.pillar461_pmns_pr_derived import (
    PILLAR_STATUS,
    VERSION,
    pmns_angles_from_geometry,
    pr_from_pmns_angles,
    pr_central_value,
    pr_interval_from_neutrino_uncertainties,
    derivation_chain_status,
    named_residual_pr,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'PMNS_PR_DERIVATION_ATTEMPTED__NAMED_RESIDUAL'

    def test_version(self):
        assert VERSION == 'v14.0'


class TestPMNSAngles:
    def test_theta12(self):
        assert pmns_angles_from_geometry()['theta12'] == pytest.approx(33.82)

    def test_theta23(self):
        assert pmns_angles_from_geometry()['theta23'] == pytest.approx(48.3)

    def test_theta13(self):
        assert pmns_angles_from_geometry()['theta13'] == pytest.approx(8.57)

    def test_three_angles_present(self):
        assert set(pmns_angles_from_geometry()) == {'theta12', 'theta23', 'theta13'}


class TestPROutput:
    def test_pr_positive(self):
        a = pmns_angles_from_geometry()
        assert pr_from_pmns_angles(a['theta12'], a['theta23'], a['theta13']) > 0

    def test_pr_less_than_one(self):
        a = pmns_angles_from_geometry()
        assert pr_from_pmns_angles(a['theta12'], a['theta23'], a['theta13']) < 1

    def test_central_value_close_to_expected(self):
        assert pr_central_value() == pytest.approx(0.365, abs=0.01)

    def test_central_value_inside_interval(self):
        low, high = pr_interval_from_neutrino_uncertainties()
        assert low <= pr_central_value() <= high

    @pytest.mark.parametrize('theta12,theta23,theta13', [(33.82, 48.3, 8.57), (34.0, 48.0, 8.6), (33.5, 48.8, 8.4)])
    def test_variants_remain_physical(self, theta12, theta23, theta13):
        value = pr_from_pmns_angles(theta12, theta23, theta13)
        assert 0.0 < value < 1.0


class TestInterval:
    def test_interval_exact(self):
        assert pr_interval_from_neutrino_uncertainties() == (0.30, 0.43)

    def test_low_less_than_high(self):
        low, high = pr_interval_from_neutrino_uncertainties()
        assert low < high


class TestDerivationChain:
    def test_pmns_angles_derived(self):
        assert derivation_chain_status()['pmns_angles_derived'] is True

    def test_leading_order_mapping_used(self):
        assert derivation_chain_status()['leading_order_pr_mapping_used'] is True

    def test_central_value_in_interval(self):
        assert derivation_chain_status()['central_value_in_interval'] is True

    def test_fully_derived_false(self):
        assert derivation_chain_status()['fully_derived'] is False

    def test_status(self):
        assert derivation_chain_status()['status'] == PILLAR_STATUS


class TestNamedResidual:
    def test_name(self):
        assert named_residual_pr()['name'] == 'THREE_GENERATION_RS_DIRAC_SYSTEM_NOT_FULLY_SOLVED'

    def test_residual_mentions_5d_dirac_equation(self):
        assert '5D Dirac equation' in named_residual_pr()['residual']

    def test_closure_path_mentions_coupled_system(self):
        assert 'coupled 5D neutrino Dirac/Majorana system' in named_residual_pr()['closure_path']


class TestAngleRelations:
    def test_theta12_larger_than_theta13(self):
        angles = pmns_angles_from_geometry()
        assert angles['theta12'] > angles['theta13']

    def test_theta23_larger_than_theta12(self):
        angles = pmns_angles_from_geometry()
        assert angles['theta23'] > angles['theta12']

    @pytest.mark.parametrize('key', ['theta12', 'theta23', 'theta13'])
    def test_angles_positive(self, key):
        assert pmns_angles_from_geometry()[key] > 0

    @pytest.mark.parametrize('key', ['theta12', 'theta23', 'theta13'])
    def test_angles_below_ninety(self, key):
        assert pmns_angles_from_geometry()[key] < 90


class TestPROutputDetails:
    @pytest.mark.parametrize('delta', [-0.5, 0.0, 0.5])
    def test_small_theta13_variations_keep_value_in_window(self, delta):
        angles = pmns_angles_from_geometry()
        value = pr_from_pmns_angles(angles['theta12'], angles['theta23'], angles['theta13'] + delta)
        assert 0.25 < value < 0.45

    @pytest.mark.parametrize('delta', [-1.0, 0.0, 1.0])
    def test_small_theta12_variations_keep_value_positive(self, delta):
        angles = pmns_angles_from_geometry()
        value = pr_from_pmns_angles(angles['theta12'] + delta, angles['theta23'], angles['theta13'])
        assert value > 0

    @pytest.mark.parametrize('delta', [-1.0, 0.0, 1.0])
    def test_small_theta23_variations_keep_value_positive(self, delta):
        angles = pmns_angles_from_geometry()
        value = pr_from_pmns_angles(angles['theta12'], angles['theta23'] + delta, angles['theta13'])
        assert value > 0

    def test_central_value_matches_chain_status(self):
        assert derivation_chain_status()['pr_central_value'] == pytest.approx(pr_central_value())

    def test_interval_width(self):
        low, high = pr_interval_from_neutrino_uncertainties()
        assert (high - low) == pytest.approx(0.13)

    def test_central_value_near_midpoint(self):
        low, high = pr_interval_from_neutrino_uncertainties()
        midpoint = 0.5 * (low + high)
        assert abs(pr_central_value() - midpoint) < 0.02

    def test_chain_interval_matches_function(self):
        assert derivation_chain_status()['interval'] == pr_interval_from_neutrino_uncertainties()

    def test_report_central_value_matches_function(self):
        assert pillar_report()['pr_central_value'] == pytest.approx(pr_central_value())

    def test_report_interval_matches_function(self):
        assert pillar_report()['interval'] == pr_interval_from_neutrino_uncertainties()

    def test_report_chain_status_matches_function(self):
        assert pillar_report()['chain_status'] == derivation_chain_status()

    @pytest.mark.parametrize('field', ['name', 'residual', 'closure_path'])
    def test_named_residual_fields_present(self, field):
        assert field in named_residual_pr()

    def test_named_residual_mentions_simultaneously(self):
        assert 'simultaneously' in named_residual_pr()['residual']

    def test_chain_status_fields_present(self):
        chain = derivation_chain_status()
        for key in ['pmns_angles_derived', 'leading_order_pr_mapping_used', 'pr_central_value', 'interval', 'central_value_in_interval', 'fully_derived', 'status']:
            assert key in chain


class TestPillarReport:
    def test_pillar_number(self):
        assert pillar_report()['pillar'] == 461

    def test_status(self):
        assert pillar_report()['status'] == PILLAR_STATUS

    def test_angles_present(self):
        assert 'angles' in pillar_report()

    def test_named_residual_present(self):
        assert 'named_residual' in pillar_report()
