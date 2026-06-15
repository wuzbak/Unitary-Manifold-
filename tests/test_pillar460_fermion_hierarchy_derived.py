# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 460 — partial fermion-hierarchy derivation."""
import math
import pytest

from src.core.pillar460_fermion_hierarchy_derived import (
    PILLAR_STATUS,
    VERSION,
    DELTA_KT,
    REPRESENTATION_WEIGHTS,
    SM_CHARGED_FERMIONS,
    cl_phys,
    cr_phys,
    yukawa_from_bulk_profiles,
    fermion_mass_derived,
    derive_all_nine_fermions,
    derivation_status_by_fermion,
    hierarchy_derivation_verdict,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'FERMION_HIERARCHY_PARTIALLY_DERIVED'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_delta_kt(self):
        assert DELTA_KT == pytest.approx(0.053)

    def test_three_sector_weights(self):
        assert set(REPRESENTATION_WEIGHTS) == {'up_quark', 'down_quark', 'lepton'}

    def test_nine_fermions(self):
        assert len(SM_CHARGED_FERMIONS) == 9


class TestCLPhys:
    @pytest.mark.parametrize('n,expected', [(0, 1.0), (1, 0.9), (2, 0.8)])
    def test_values(self, n, expected):
        assert cl_phys(n) == pytest.approx(expected)

    @pytest.mark.parametrize('n', [0, 1, 2])
    def test_monotone_decreasing(self, n):
        if n < 2:
            assert cl_phys(n) > cl_phys(n + 1)

    @pytest.mark.parametrize('n', [-1, 3, 4])
    def test_invalid_generation_raises(self, n):
        with pytest.raises(ValueError):
            cl_phys(n)


class TestCRPhys:
    @pytest.mark.parametrize('n,expected', [(0, 0.5), (1, 0.4), (2, 0.3)])
    def test_values(self, n, expected):
        assert cr_phys(n) == pytest.approx(expected)

    @pytest.mark.parametrize('n', [0, 1, 2])
    def test_monotone_decreasing(self, n):
        if n < 2:
            assert cr_phys(n) > cr_phys(n + 1)

    @pytest.mark.parametrize('n', [-1, 3, 4])
    def test_invalid_generation_raises(self, n):
        with pytest.raises(ValueError):
            cr_phys(n)


class TestYukawas:
    @pytest.mark.parametrize('n', [0, 1, 2])
    def test_positive(self, n):
        assert yukawa_from_bulk_profiles(n) > 0

    def test_generation_ordering(self):
        assert yukawa_from_bulk_profiles(0) < yukawa_from_bulk_profiles(1) < yukawa_from_bulk_profiles(2)

    def test_delta_kt_enhances_yukawa(self):
        assert yukawa_from_bulk_profiles(2, delta_kt=0.053) > yukawa_from_bulk_profiles(2, delta_kt=0.0)

    def test_formula_matches_manual(self):
        expected = math.exp(-37.0 * (cl_phys(2) + cr_phys(2) - 1.0)) * (1.0 + DELTA_KT)
        assert yukawa_from_bulk_profiles(2) == pytest.approx(expected)


class TestGenericMasses:
    @pytest.mark.parametrize('n', [0, 1, 2])
    def test_positive(self, n):
        assert fermion_mass_derived(n) > 0

    def test_generation_ordering(self):
        assert fermion_mass_derived(0) < fermion_mass_derived(1) < fermion_mass_derived(2)

    def test_generation_two_is_gev_scale(self):
        assert 4.0 < fermion_mass_derived(2) < 6.0

    def test_generation_zero_is_tiny(self):
        assert fermion_mass_derived(0) < 1e-4


class TestFullDerivationAudit:
    def test_derived_count(self):
        assert derive_all_nine_fermions()['derived_count'] == 3

    def test_natural_count(self):
        assert derive_all_nine_fermions()['natural_count'] == 6

    @pytest.mark.parametrize('fermion', ['t', 'b', 'tau'])
    def test_third_generation_derived(self, fermion):
        assert derive_all_nine_fermions()['fermions'][fermion]['status'] == 'DERIVED'

    @pytest.mark.parametrize('fermion', ['u', 'c', 'd', 's', 'e', 'mu'])
    def test_light_fermions_natural(self, fermion):
        assert derive_all_nine_fermions()['fermions'][fermion]['status'] == 'NATURAL'

    @pytest.mark.parametrize('fermion', ['u', 'd', 'e', 'c', 's', 'mu'])
    def test_light_fermions_need_fn(self, fermion):
        assert derive_all_nine_fermions()['fermions'][fermion]['needs_fn_sublattice'] is True

    @pytest.mark.parametrize('fermion', ['t', 'b', 'tau'])
    def test_third_generation_errors_small(self, fermion):
        assert derive_all_nine_fermions()['fermions'][fermion]['relative_error'] <= 0.2

    @pytest.mark.parametrize('fermion', ['t', 'b', 'tau'])
    def test_third_generation_generation_index_two(self, fermion):
        assert derive_all_nine_fermions()['fermions'][fermion]['generation'] == 2

    @pytest.mark.parametrize('fermion,sector', [('t', 'up_quark'), ('b', 'down_quark'), ('tau', 'lepton')])
    def test_sector_assignment(self, fermion, sector):
        assert derive_all_nine_fermions()['fermions'][fermion]['sector'] == sector

    @pytest.mark.parametrize('fermion,weight', [('t', REPRESENTATION_WEIGHTS['up_quark']), ('b', REPRESENTATION_WEIGHTS['down_quark']), ('tau', REPRESENTATION_WEIGHTS['lepton'])])
    def test_sector_weight_applied(self, fermion, weight):
        assert derive_all_nine_fermions()['fermions'][fermion]['sector_weight'] == pytest.approx(weight)


class TestStatusMap:
    def test_status_map_size(self):
        assert len(derivation_status_by_fermion()) == 9

    @pytest.mark.parametrize('fermion', ['t', 'b', 'tau'])
    def test_status_map_derived(self, fermion):
        assert derivation_status_by_fermion()[fermion] == 'DERIVED'

    @pytest.mark.parametrize('fermion', ['u', 'c', 'd', 's', 'e', 'mu'])
    def test_status_map_natural(self, fermion):
        assert derivation_status_by_fermion()[fermion] == 'NATURAL'


class TestVerdict:
    def test_verdict_status(self):
        assert hierarchy_derivation_verdict()['status'] == PILLAR_STATUS

    def test_verdict_label(self):
        assert hierarchy_derivation_verdict()['verdict'] == 'PARTIALLY_DERIVED'

    def test_derived_fermions(self):
        assert hierarchy_derivation_verdict()['derived_fermions'] == ['t', 'b', 'tau']

    def test_natural_count(self):
        assert hierarchy_derivation_verdict()['natural_count'] == 6

    def test_summary_mentions_fn(self):
        assert 'FN sub-lattice' in hierarchy_derivation_verdict()['summary']


class TestPillarReport:
    def test_pillar_number(self):
        assert pillar_report()['pillar'] == 460

    def test_status(self):
        assert pillar_report()['status'] == PILLAR_STATUS

    def test_audit_present(self):
        assert 'audit' in pillar_report()

    def test_verdict_present(self):
        assert 'verdict' in pillar_report()
