# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 421 — L2 γ Gap Budget Certificate."""
import pytest

from src.core.pillar421_l2_gamma_budget_certificate import (
    PILLAR_STATUS,
    GAMMA_THEORY,
    GAMMA_FIT,
    GAMMA_GAP,
    GAMMA_GAP_FRACTION,
    C1_TOTAL,
    C1_KM,
    C1_ZM,
    C1_IDENTIFIED,
    C1_NP_RESIDUAL,
    FRACTION_IDENTIFIED,
    FRACTION_NP_RESIDUAL,
    gamma_gap_report,
    budget_partition,
    np_residual_certificate,
    l2_budget_verdict,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'L2_GAMMA_BUDGET_CERTIFIED'

    def test_gamma_theory_reasonable(self):
        assert 0.20 < GAMMA_THEORY < 0.30

    def test_gamma_fit_reasonable(self):
        assert 0.25 < GAMMA_FIT < 0.35

    def test_gamma_gap_positive(self):
        assert GAMMA_GAP > 0.0

    def test_gamma_gap_consistent(self):
        assert abs(GAMMA_GAP - (GAMMA_FIT - GAMMA_THEORY)) < 1e-4

    def test_gamma_gap_fraction_positive(self):
        assert GAMMA_GAP_FRACTION > 0.0

    def test_gamma_gap_fraction_lt_one(self):
        assert GAMMA_GAP_FRACTION < 0.5

    def test_c1_km_positive(self):
        assert C1_KM > 0.0

    def test_c1_zm_positive(self):
        assert C1_ZM > 0.0

    def test_c1_identified_sum(self):
        assert abs(C1_IDENTIFIED - (C1_KM + C1_ZM)) < 0.01

    def test_c1_residual_positive(self):
        assert C1_NP_RESIDUAL > 0.0

    def test_c1_partition_sums_to_total(self):
        assert abs(C1_IDENTIFIED + C1_NP_RESIDUAL - C1_TOTAL) < 0.01

    def test_fraction_identified_range(self):
        assert 0.6 < FRACTION_IDENTIFIED < 0.9

    def test_fractions_sum_to_one(self):
        assert abs(FRACTION_IDENTIFIED + FRACTION_NP_RESIDUAL - 1.0) < 0.01

    def test_km_smaller_than_zm(self):
        assert C1_KM < C1_ZM


class TestGammaGapReport:
    def test_returns_dict(self):
        assert isinstance(gamma_gap_report(), dict)

    @pytest.mark.parametrize('key', ['gamma_theory', 'gamma_fit', 'gamma_gap',
                                     'gamma_gap_fraction', 'gamma_gap_percent'])
    def test_expected_keys(self, key):
        assert key in gamma_gap_report()

    def test_gap_positive(self):
        report = gamma_gap_report()
        assert report['gamma_gap'] > 0.0

    def test_gap_percent_consistent(self):
        report = gamma_gap_report()
        assert abs(report['gamma_gap_percent'] - report['gamma_gap_fraction'] * 100) < 0.1


class TestBudgetPartition:
    def test_returns_three_entries(self):
        assert len(budget_partition()) == 3

    @pytest.mark.parametrize('index', [0, 1, 2])
    def test_each_has_mechanism(self, index):
        assert 'mechanism' in budget_partition()[index]

    @pytest.mark.parametrize('index', [0, 1, 2])
    def test_each_has_value(self, index):
        assert 'value' in budget_partition()[index]
        assert budget_partition()[index]['value'] >= 0.0

    @pytest.mark.parametrize('index', [0, 1, 2])
    def test_each_has_status(self, index):
        assert 'status' in budget_partition()[index]

    def test_km_entry_status_computed(self):
        km = budget_partition()[0]
        assert km['status'] == 'COMPUTED'

    def test_zm_entry_status_computed(self):
        zm = budget_partition()[1]
        assert zm['status'] == 'COMPUTED'

    def test_np_entry_is_architecture_limit(self):
        np_entry = budget_partition()[2]
        assert np_entry['status'] == 'ARCHITECTURE_LIMIT'

    def test_values_sum_to_total(self):
        total = sum(e['value'] for e in budget_partition())
        assert abs(total - C1_TOTAL) < 0.1

    def test_fractions_sum_to_one(self):
        total_frac = sum(e['fraction_of_total'] for e in budget_partition())
        assert abs(total_frac - 1.0) < 0.02


class TestNpResidualCertificate:
    def test_returns_dict(self):
        assert isinstance(np_residual_certificate(), dict)

    def test_status_architecture_limit(self):
        assert np_residual_certificate()['status'] == 'ARCHITECTURE_LIMIT'

    def test_has_honest_statement(self):
        cert = np_residual_certificate()
        assert 'honest_statement' in cert
        assert len(cert['honest_statement']) > 50

    def test_has_perturbative_routes(self):
        cert = np_residual_certificate()
        assert 'perturbative_routes_ruled_out' in cert
        assert len(cert['perturbative_routes_ruled_out']) >= 3

    def test_c1_np_positive(self):
        cert = np_residual_certificate()
        assert cert['c1_np'] > 0.0


class TestL2BudgetVerdict:
    def test_returns_dict(self):
        assert isinstance(l2_budget_verdict(), dict)

    def test_status(self):
        assert l2_budget_verdict()['status'] == 'L2_GAMMA_BUDGET_CERTIFIED'

    @pytest.mark.parametrize('key', ['gamma_gap', 'budget_partition', 'np_residual',
                                     'total_identified_fraction', 'total_identified_percent', 'verdict'])
    def test_expected_keys(self, key):
        assert key in l2_budget_verdict()

    def test_identified_fraction_in_range(self):
        verdict = l2_budget_verdict()
        assert 0.6 < verdict['total_identified_fraction'] < 0.9

    def test_verdict_is_string(self):
        assert isinstance(l2_budget_verdict()['verdict'], str)

    def test_verdict_mentions_np(self):
        assert 'ARCHITECTURE_LIMIT' in l2_budget_verdict()['verdict'] or \
               'non-perturbative' in l2_budget_verdict()['verdict']
