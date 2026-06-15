# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 464 — free-parameter census v14."""
from __future__ import annotations

import pytest

from src.core.pillar464_free_parameter_census_v14 import (
    FREE_PARAMETER_CENSUS,
    PILLAR_STATUS,
    VERSION,
    count_by_category,
    genuinely_derived_parameters,
    genuinely_free_parameters,
    pillar_report,
    summary_statement,
    v14_closures,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'FREE_PARAMETER_CENSUS_V14_COMPLETE'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_registry_size(self):
        assert len(FREE_PARAMETER_CENSUS) == 24

    def test_contains_alpha_gw(self):
        assert 'alpha_GW' in FREE_PARAMETER_CENSUS

    def test_contains_n_w(self):
        assert 'n_w' in FREE_PARAMETER_CENSUS


class TestRegistryEntries:
    def test_nw_now_structural(self):
        assert FREE_PARAMETER_CENSUS['n_w']['category'] == 'GENUINELY_DERIVED_FROM_FIRST_PRINCIPLES'

    def test_alpha_gw_is_free(self):
        assert FREE_PARAMETER_CENSUS['alpha_GW']['category'] == 'GENUINELY_FREE'

    def test_p_r_is_free(self):
        assert FREE_PARAMETER_CENSUS['p_R']['category'] == 'GENUINELY_FREE'

    def test_sigma_m_nu_observational(self):
        assert FREE_PARAMETER_CENSUS['Sigma_m_nu']['category'] == 'OBSERVATIONALLY_SELECTED_WITHIN_CONSTRAINED_SET'

    def test_cl_phys_partial(self):
        assert FREE_PARAMETER_CENSUS['c_L_phys']['category'] == 'PARTIALLY_DERIVED'

    def test_cr_phys_partial(self):
        assert FREE_PARAMETER_CENSUS['c_R_phys']['category'] == 'PARTIALLY_DERIVED'

    def test_lambda_gw_conditional(self):
        assert FREE_PARAMETER_CENSUS['lambda_GW']['category'] == 'DERIVED_CONDITIONAL_ON_ANSATZ'

    def test_beta_units(self):
        assert FREE_PARAMETER_CENSUS['beta']['units'] == 'degrees'

    def test_lambda_qcd_units(self):
        assert FREE_PARAMETER_CENSUS['Lambda_QCD']['units'] == 'MeV'

    def test_mh_units(self):
        assert FREE_PARAMETER_CENSUS['m_H']['units'] == 'GeV'


class TestCounts:
    def setup_method(self):
        self.counts = count_by_category()

    def test_genuinely_free_count(self):
        assert self.counts['GENUINELY_FREE'] == 2

    def test_derived_structural_count(self):
        assert self.counts['GENUINELY_DERIVED_FROM_FIRST_PRINCIPLES'] == 4

    def test_conditional_count(self):
        assert self.counts['DERIVED_CONDITIONAL_ON_ANSATZ'] == 15

    def test_observational_count(self):
        assert self.counts['OBSERVATIONALLY_SELECTED_WITHIN_CONSTRAINED_SET'] == 1

    def test_partial_count(self):
        assert self.counts['PARTIALLY_DERIVED'] == 2

    def test_counts_sum_to_total(self):
        assert sum(self.counts.values()) == len(FREE_PARAMETER_CENSUS)


class TestParameterLists:
    def test_genuinely_free_sorted(self):
        assert genuinely_free_parameters() == ['alpha_GW', 'p_R']

    def test_genuinely_derived_sorted(self):
        assert genuinely_derived_parameters() == ['N_gen', 'c_s', 'k_CS', 'n_w']

    def test_nw_not_free(self):
        assert 'n_w' not in genuinely_free_parameters()

    def test_alpha_gw_not_structural(self):
        assert 'alpha_GW' not in genuinely_derived_parameters()


class TestSummaryAndClosures:
    def test_summary_mentions_two_free(self):
        assert '2 genuinely free' in summary_statement()

    def test_summary_mentions_four_structural(self):
        assert '4 derived-structural' in summary_statement()

    def test_v14_closures_mentions_nw(self):
        assert 'n_w' in v14_closures()['changed_parameters']

    def test_v14_closures_remaining_free(self):
        assert v14_closures()['remaining_genuinely_free'] == ['alpha_GW', 'p_R']

    def test_v14_closures_total(self):
        assert v14_closures()['parameter_total'] == 24


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 464

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_contains_counts(self):
        assert 'counts' in self.report

    def test_contains_summary(self):
        assert 'summary_statement' in self.report

    def test_contains_closure_delta(self):
        assert 'v14_closures' in self.report
