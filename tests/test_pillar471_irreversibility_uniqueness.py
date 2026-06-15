# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 471 — irreversibility uniqueness audit."""
from __future__ import annotations

from src.core.pillar471_irreversibility_uniqueness import (
    C_S,
    K_CS,
    N_GEN,
    N_W,
    PHI0,
    PILLAR_STATUS,
    VERSION,
    b_mu_uniqueness_within_discrete_family,
    entropy_functional_definition,
    irreversibility_identification_status,
    monotonicity_requirement,
    named_limitation,
    pillar_report,
    test_scalar_axion_alternative as scalar_axion_alternative,
    test_two_form_alternative as two_form_alternative,
    test_z2_even_vector_alternative as z2_even_vector_alternative,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'IRREVERSIBILITY_UNIQUENESS_BOUNDED'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_canonical_nw(self):
        assert N_W == 5

    def test_canonical_kcs(self):
        assert K_CS == 74

    def test_canonical_ngen(self):
        assert N_GEN == 3

    def test_phi0_positive(self):
        assert PHI0 > 30.0

    def test_sound_speed_positive(self):
        assert 0.0 < C_S < 1.0


class TestEntropyFunctional:
    def setup_method(self):
        self.result = entropy_functional_definition()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_area_law_true(self):
        assert self.result['area_law'] is True

    def test_formula_mentions_area(self):
        assert 'A_horizon' in self.result['functional']

    def test_formula_mentions_gn(self):
        assert 'G_N' in self.result['functional']

    def test_ftum_location(self):
        assert self.result['ftum_location'] == 'FTUM fixed point'

    def test_depends_on_phi(self):
        assert 'phi' in self.result['depends_on']


class TestMonotonicityRequirement:
    def setup_method(self):
        self.result = monotonicity_requirement()

    def test_condition_present(self):
        assert self.result['condition'] == 'partial_t S >= 0'

    def test_mentions_epsilon_density(self):
        assert 'epsilon' in self.result['cs_density']

    def test_requires_z2_odd(self):
        assert self.result['required_parity'] == 'Z2-odd'

    def test_requires_bulk_dissipation(self):
        assert 'positive-definite' in self.result['required_bulk_property']

    def test_requires_ghost_free(self):
        assert self.result['required_stability'] == 'ghost-free effective theory'

    def test_canonical_candidate(self):
        assert self.result['canonical_candidate'] == 'B_mu'


class TestScalarAxionAlternative:
    def setup_method(self):
        self.result = scalar_axion_alternative()

    def test_verdict_fails(self):
        assert self.result['verdict'] == 'FAILS'

    def test_field_type_scalar(self):
        assert self.result['field_type'] == 'scalar'

    def test_monotone_dissipation_false(self):
        assert self.result['monotone_dissipation'] is False

    def test_ghost_free_true(self):
        assert self.result['ghost_free'] is True

    def test_failure_mentions_entropy_can_decrease(self):
        assert 'entropy can decrease' in self.result['failure_mode']


class TestTwoFormAlternative:
    def setup_method(self):
        self.result = two_form_alternative()

    def test_verdict_fails(self):
        assert self.result['verdict'] == 'FAILS'

    def test_field_type_two_form(self):
        assert self.result['field_type'] == '2-form'

    def test_z2_requirement_true(self):
        assert self.result['z2_odd_requirement'] is True

    def test_monotone_dissipation_false(self):
        assert self.result['monotone_dissipation'] is False

    def test_failure_mentions_boundary_term(self):
        assert 'boundary term' in self.result['failure_mode']


class TestZ2EvenVectorAlternative:
    def setup_method(self):
        self.result = z2_even_vector_alternative()

    def test_verdict_fails(self):
        assert self.result['verdict'] == 'FAILS'

    def test_field_type_one_form(self):
        assert self.result['field_type'] == '1-form'

    def test_z2_requirement_false(self):
        assert self.result['z2_odd_requirement'] is False

    def test_ghost_free_false(self):
        assert self.result['ghost_free'] is False

    def test_failure_mentions_massless_zero_mode(self):
        assert 'massless zero mode' in self.result['failure_mode']


class TestBUniqueness:
    def setup_method(self):
        self.result = b_mu_uniqueness_within_discrete_family()

    def test_candidate_name(self):
        assert self.result['candidate'] == 'B_mu'

    def test_field_type(self):
        assert self.result['field_type'] == 'Z2-odd 1-form'

    def test_passes_z2(self):
        assert self.result['passes_z2_odd'] is True

    def test_passes_monotone(self):
        assert self.result['passes_monotone_dissipation'] is True

    def test_passes_ghost_free(self):
        assert self.result['passes_ghost_free'] is True

    def test_alternatives_count(self):
        assert len(self.result['alternatives_tested']) == 3

    def test_all_discrete_alternatives_fail(self):
        assert self.result['all_discrete_alternatives_fail'] is True

    def test_unique_within_discrete_family(self):
        assert self.result['unique_within_discrete_family'] is True

    def test_verdict_label(self):
        assert self.result['verdict'] == 'BOUNDED_UNIQUENESS_ESTABLISHED'


class TestLimitationAndUpgrade:
    def test_limitation_status(self):
        assert named_limitation()['status'] == 'NAMED_LIMITATION'

    def test_limitation_mentions_discrete_alternatives(self):
        assert 'discrete field-type alternatives' in named_limitation()['statement']

    def test_limitation_mentions_continuous_deformation(self):
        assert 'continuous deformation of B_mu' in named_limitation()['statement']

    def test_p3_prior_status(self):
        assert irreversibility_identification_status()['prior_status'] == 'CONJECTURAL'

    def test_p3_current_status(self):
        assert irreversibility_identification_status()['current_status'] == 'BOUNDED'

    def test_upgrade_reason_mentions_discrete_alternatives(self):
        assert 'Discrete scalar, two-form, and Z2-even vector alternatives are excluded.' == irreversibility_identification_status()['upgrade_reason']


class TestReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 471

    def test_status_matches(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_contains_entropy(self):
        assert 'entropy_functional' in self.report

    def test_contains_monotonicity(self):
        assert 'monotonicity_requirement' in self.report

    def test_contains_uniqueness(self):
        assert 'uniqueness' in self.report

    def test_contains_limitation(self):
        assert 'limitation' in self.report

    def test_contains_upgrade(self):
        assert 'p3_upgrade' in self.report
