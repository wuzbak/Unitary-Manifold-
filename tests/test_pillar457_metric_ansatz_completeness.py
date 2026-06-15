# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 457 — metric ansatz completeness audit."""
import pytest

from src.core.pillar457_metric_ansatz_completeness import (
    PILLAR_STATUS,
    VERSION,
    constraint_c1_eh_stationarity,
    constraint_c2_kk_gauge_covariance,
    constraint_c3_z2_parity,
    constraint_c4_radion_normalization,
    joint_sufficiency_test,
    named_residual_c5_lambda,
    completeness_certificate,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'METRIC_ANSATZ_COMPLETENESS_CERTIFIED'

    def test_version(self):
        assert VERSION == 'v14.0'


class TestConstraintC1:
    def test_constraint_name(self):
        assert constraint_c1_eh_stationarity()['constraint'] == 'C1_EH_STATIONARITY'

    def test_surviving_blocks(self):
        assert constraint_c1_eh_stationarity()['surviving_blocks'] == ['G_munu', 'G_mu5', 'G_55']

    def test_equation_present(self):
        assert 'δS_EH/δG_AB' in constraint_c1_eh_stationarity()['equation']


class TestConstraintC2:
    def test_constraint_name(self):
        assert constraint_c2_kk_gauge_covariance()['constraint'] == 'C2_KK_GAUGE_COVARIANCE'

    def test_unique_form(self):
        assert constraint_c2_kk_gauge_covariance()['unique_form'] == 'G_{μ5} = λφB_μ'

    def test_gauge_shift_present(self):
        assert 'B_μ → B_μ + ∂_μα' in constraint_c2_kk_gauge_covariance()['gauge_shift']


class TestConstraintC3:
    def test_constraint_name(self):
        assert constraint_c3_z2_parity()['constraint'] == 'C3_Z2_PARITY'

    def test_odd_sector(self):
        assert constraint_c3_z2_parity()['odd_sector'] == ['G_mu5']

    def test_even_sector(self):
        assert constraint_c3_z2_parity()['even_sector'] == ['G_munu', 'G_55']


class TestConstraintC4:
    def test_constraint_name(self):
        assert constraint_c4_radion_normalization()['constraint'] == 'C4_RADION_NORMALIZATION'

    def test_unique_form(self):
        assert constraint_c4_radion_normalization()['unique_form'] == 'G_55 = φ²'

    def test_canonical_term(self):
        assert '(∂φ)^2 / 2' in constraint_c4_radion_normalization()['canonical_term']


class TestJointSufficiency:
    def test_discrete_uniqueness_true(self):
        assert joint_sufficiency_test()['discrete_family_uniqueness'] is True

    def test_continuous_uniqueness_false(self):
        assert joint_sufficiency_test()['continuous_functional_uniqueness'] is False

    def test_jointly_sufficient_for_discrete_families(self):
        assert joint_sufficiency_test()['jointly_sufficient_for_discrete_families'] is True

    def test_not_globally_complete(self):
        assert joint_sufficiency_test()['jointly_sufficient_over_full_functional_space'] is False

    def test_named_residual(self):
        assert joint_sufficiency_test()['named_residual'] == 'LAMBDA_NORMALIZATION_REQUIRES_10D_UV_COMPLETION'

    def test_result_string(self):
        assert joint_sufficiency_test()['result'] == 'YES_FOR_DISCRETE_FAMILIES__NO_FOR_CONTINUOUS_FAMILY'

    @pytest.mark.parametrize('name', ['nonlinear_Gmu5', 'wrong_radion_power', 'extra_tensor_block', 'even_parity_Gmu5'])
    def test_discrete_alternatives_eliminated(self, name):
        assert joint_sufficiency_test()['discrete_alternative_families'][name] is False

    @pytest.mark.parametrize('name', ['lambda_rescaling_family', 'uv_fixed_normalization_required'])
    def test_continuous_residual_named(self, name):
        assert joint_sufficiency_test()['continuous_residual_family'][name] is True


class TestNamedResidual:
    def test_name(self):
        assert named_residual_c5_lambda()['name'] == 'LAMBDA_NORMALIZATION_REQUIRES_10D_UV_COMPLETION'

    def test_residual_mentions_lambda(self):
        assert 'λ' in named_residual_c5_lambda()['residual']

    def test_c5_candidate_mentions_uv_completion(self):
        assert 'UV completion' in named_residual_c5_lambda()['c5_candidate']

    def test_closure_type(self):
        assert named_residual_c5_lambda()['closure_type'] == 'UV_COMPLETION'


class TestCertificate:
    def test_pillar_number(self):
        assert completeness_certificate()['pillar'] == 457

    def test_status(self):
        assert completeness_certificate()['status'] == PILLAR_STATUS

    def test_certificate_contains_all_constraints(self):
        cert = completeness_certificate()
        for key in ['c1', 'c2', 'c3', 'c4']:
            assert key in cert

    def test_joint_test_present(self):
        assert 'joint_test' in completeness_certificate()

    def test_named_residual_present(self):
        assert 'named_residual' in completeness_certificate()

    def test_certificate_statement_mentions_lambda(self):
        assert 'λ normalization' in completeness_certificate()['certificate_statement']


class TestConstraintStatements:
    @pytest.mark.parametrize(
        'text',
        [
            constraint_c1_eh_stationarity()['statement'],
            constraint_c2_kk_gauge_covariance()['statement'],
            constraint_c3_z2_parity()['statement'],
            constraint_c4_radion_normalization()['statement'],
        ],
    )
    def test_statements_nonempty(self, text):
        assert len(text) > 20

    def test_c1_mentions_block_form(self):
        assert 'block form' in constraint_c1_eh_stationarity()['statement']

    def test_c2_mentions_off_diagonal(self):
        assert 'off-diagonal block' in constraint_c2_kk_gauge_covariance()['statement']

    def test_c3_mentions_orbifold(self):
        assert 'orbifold' in constraint_c3_z2_parity()['statement']

    def test_c4_mentions_scalar_block(self):
        assert 'scalar block' in constraint_c4_radion_normalization()['statement']


class TestPillarReport:
    def test_pillar_number(self):
        assert pillar_report()['pillar'] == 457

    def test_status(self):
        assert pillar_report()['status'] == PILLAR_STATUS

    def test_certificate_present(self):
        assert 'certificate' in pillar_report()
