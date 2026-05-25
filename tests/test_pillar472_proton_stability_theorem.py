# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 472 — proton stability geometric theorem."""
from __future__ import annotations

import pytest

from src.core.pillar472_proton_stability_theorem import (
    PILLAR_STATUS,
    VERSION,
    falsification_condition,
    gut_scale_gev,
    hyperk_discriminability,
    kk_scale_mev,
    named_limitations,
    pillar_report,
    proton_lifetime_years,
    proton_stability_theorem,
    warp_factor_exponent,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'PROTON_STABILITY_GEOMETRIC_THEOREM_DERIVED'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_kk_scale_exact(self):
        assert kk_scale_mev() == pytest.approx(110.13)


class TestWarpFactorExponent:
    def test_positive(self):
        assert warp_factor_exponent() > 0.0

    def test_reasonable_range(self):
        assert 3.0 < warp_factor_exponent() < 4.0

    def test_formula_value(self):
        expected = (74 - 3) / (2.0 * 3.141592653589793 ** 2)
        assert warp_factor_exponent() == pytest.approx(expected)

    def test_reject_nonpositive_nw(self):
        with pytest.raises(ValueError):
            warp_factor_exponent(n_w=0)

    def test_reject_nonpositive_kcs(self):
        with pytest.raises(ValueError):
            warp_factor_exponent(k_cs=0)


class TestGutScale:
    def test_positive(self):
        assert gut_scale_gev() > 0.0

    def test_above_1e15(self):
        assert gut_scale_gev() > 1.0e15

    def test_below_planck(self):
        assert gut_scale_gev() < 1.22e19

    def test_in_standard_gut_window(self):
        assert 1.0e16 < gut_scale_gev() < 1.0e17

    def test_increases_with_kcs(self):
        assert gut_scale_gev(k_cs=90) > gut_scale_gev(k_cs=74)

    def test_increases_with_mkk(self):
        assert gut_scale_gev(m_kk_mev=220.26) > gut_scale_gev(m_kk_mev=110.13)

    def test_reject_bad_nw(self):
        with pytest.raises(ValueError):
            gut_scale_gev(n_w=0)

    def test_reject_bad_kcs(self):
        with pytest.raises(ValueError):
            gut_scale_gev(k_cs=0)

    def test_reject_bad_mkk(self):
        with pytest.raises(ValueError):
            gut_scale_gev(m_kk_mev=0.0)


class TestProtonLifetime:
    def test_positive(self):
        assert proton_lifetime_years() > 0.0

    def test_above_current_limit(self):
        assert proton_lifetime_years() > 1.66e34

    def test_above_hyperk_target(self):
        assert proton_lifetime_years() > 1.0e35

    def test_scales_up_with_mkk(self):
        assert proton_lifetime_years(m_kk_mev=220.26) > proton_lifetime_years()

    def test_scales_down_with_smaller_kcs(self):
        assert proton_lifetime_years(k_cs=60) < proton_lifetime_years(k_cs=74)

    def test_gut_scale_fourth_power_behavior(self):
        tau1 = proton_lifetime_years(m_kk_mev=110.13)
        tau2 = proton_lifetime_years(m_kk_mev=440.52)
        assert tau2 > tau1


class TestTheoremPackage:
    def setup_method(self):
        self.result = proton_stability_theorem()

    def test_statement_mentions_tau(self):
        assert 'tau_p >=' in self.result['statement']

    def test_status_conditional(self):
        assert self.result['status'] == 'DERIVED_CONDITIONAL'

    def test_contains_beta(self):
        assert 'beta' in self.result['inputs']

    def test_contains_mgut(self):
        assert self.result['derived_quantities']['m_gut_gev'] == pytest.approx(gut_scale_gev())

    def test_contains_tau(self):
        assert self.result['derived_quantities']['tau_p_years'] == pytest.approx(proton_lifetime_years())

    def test_result_mentions_stable(self):
        assert 'Stable' in self.result['result']


class TestHyperKDiscriminability:
    def setup_method(self):
        self.result = hyperk_discriminability()

    def test_satisfies_current_limit(self):
        assert self.result['satisfies_current_limit'] is True

    def test_not_directly_sensitive(self):
        assert self.result['hyperk_directly_sensitive'] is False

    def test_borderline_window_bool(self):
        assert isinstance(self.result['hyperk_borderline_window'], bool)

    def test_summary_mentions_o1_prefactor(self):
        assert 'O(1) prefactor' in self.result['summary']


class TestFalsificationCondition:
    def setup_method(self):
        self.result = falsification_condition()

    def test_channel(self):
        assert self.result['channel'] == 'p -> e+ pi0'

    def test_significance(self):
        assert self.result['significance_requirement'] == '>=3 sigma'

    def test_threshold_matches_prediction(self):
        assert self.result['falsified_if_tau_below_years'] == pytest.approx(proton_lifetime_years())


class TestLimitations:
    def setup_method(self):
        self.result = named_limitations()

    def test_status(self):
        assert self.result['status'] == 'NAMED_LIMITATIONS'

    def test_has_three_assumptions(self):
        assert len(self.result['assumptions']) == 3

    def test_mentions_su5_embedding(self):
        assert 'SU(5)⊃SM embedding' in self.result['assumptions'][0]

    def test_mentions_softened_uplift(self):
        assert 'softened uplift' in self.result['assumptions'][1]


class TestReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 472

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_contains_beta(self):
        assert self.report['beta'] == pytest.approx(warp_factor_exponent())

    def test_contains_mgut(self):
        assert self.report['m_gut_gev'] == pytest.approx(gut_scale_gev())

    def test_contains_tau(self):
        assert self.report['tau_p_years'] == pytest.approx(proton_lifetime_years())

    def test_contains_theorem(self):
        assert 'theorem' in self.report

    def test_contains_hyperk(self):
        assert 'hyperk' in self.report

    def test_contains_falsification(self):
        assert 'falsification' in self.report

    def test_contains_limitations(self):
        assert 'limitations' in self.report
