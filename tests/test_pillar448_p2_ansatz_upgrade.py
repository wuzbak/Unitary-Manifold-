# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 448 — Postulate P2 Upgrade Audit."""
import pytest
from src.core.pillar448_p2_ansatz_upgrade_audit import (
    PILLAR_STATUS, VERSION, P2_STATUS, RESIDUAL_NAME,
    CONSTRAINTS,
    test_class_a_scalar_function as _class_a_scalar_function,
    test_class_b_radion_power as _class_b_radion_power,
    test_class_c_g55_power as _class_c_g55_power,
    test_class_d_tensor_mixing as _class_d_tensor_mixing,
    test_class_e_two_b_fields as _class_e_two_b_fields,
    run_all_ansatz_tests,
    p2_upgrade_verdict, pillar_report,
)


class TestMetadata:
    def test_status(self):
        assert 'DERIVED' in PILLAR_STATUS or 'ANSATZ' in PILLAR_STATUS

    def test_version(self):
        assert VERSION == 'v13.8'

    def test_p2_status_upgraded(self):
        assert 'DERIVED' in P2_STATUS

    def test_residual_name(self):
        assert 'LAMBDA' in RESIDUAL_NAME or 'NORMALIZATION' in RESIDUAL_NAME

    def test_constraints_have_c1_c5(self):
        for key in ['C1', 'C2', 'C3', 'C4', 'C5']:
            assert key in CONSTRAINTS


class TestClassA:
    def test_uniqueness(self):
        r = _class_a_scalar_function()
        assert 'UNIQUE' in r['verdict'] or 'unique' in str(r['survivors'])

    def test_class_label(self):
        r = _class_a_scalar_function()
        assert r['class'] == 'A'

    def test_survivors_single(self):
        r = _class_a_scalar_function()
        # Only f(φ) = λφ should survive
        assert len(r['survivors']) == 1


class TestClassB:
    def test_n1_unique(self):
        r = _class_b_radion_power()
        assert 'UNIQUE' in r['verdict'] or r['unique_power'] == 1

    def test_class_label(self):
        r = _class_b_radion_power()
        assert r['class'] == 'B'

    def test_unique_power_is_1(self):
        r = _class_b_radion_power()
        assert r['unique_power'] == 1


class TestClassC:
    def test_m2_unique(self):
        r = _class_c_g55_power()
        assert 'UNIQUE' in r['verdict'] or r['unique_power'] == 2

    def test_class_label(self):
        r = _class_c_g55_power()
        assert r['class'] == 'C'

    def test_unique_power_is_2(self):
        r = _class_c_g55_power()
        assert r['unique_power'] == 2


class TestClassD:
    def test_excluded_by_z2(self):
        r = _class_d_tensor_mixing()
        assert 'EXCLUDED' in r['verdict']

    def test_class_label(self):
        r = _class_d_tensor_mixing()
        assert r['class'] == 'D'


class TestClassE:
    def test_excluded_single_compact(self):
        r = _class_e_two_b_fields()
        assert 'EXCLUDED' in r['verdict']

    def test_class_label(self):
        r = _class_e_two_b_fields()
        assert r['class'] == 'E'


class TestAllAnsatzTests:
    def test_all_eliminated(self):
        r = run_all_ansatz_tests()
        assert r['all_alternatives_eliminated'] is True

    def test_five_classes_tested(self):
        r = run_all_ansatz_tests()
        assert r['classes_tested'] == 5

    def test_unique_surviving_form(self):
        r = run_all_ansatz_tests()
        form = r['unique_surviving_form']
        assert 'φ²' in form.get('G_55', '') or 'phi' in str(form).lower()

    def test_named_residual_present(self):
        r = run_all_ansatz_tests()
        assert 'named_residual' in r
        assert r['named_residual'] == RESIDUAL_NAME


class TestUpgradeVerdict:
    def test_upgraded(self):
        v = p2_upgrade_verdict()
        assert v['verdict'] == 'UPGRADED'

    def test_p2_postulate_label(self):
        v = p2_upgrade_verdict()
        assert v['postulate'] == 'P2'

    def test_new_status_derived(self):
        v = p2_upgrade_verdict()
        assert 'DERIVED' in v['new_status']

    def test_residual_documented(self):
        v = p2_upgrade_verdict()
        assert v['named_residual'] is not None


class TestPillarReport:
    def test_pillar_number(self):
        r = pillar_report()
        assert r['pillar'] == 448

    def test_status(self):
        r = pillar_report()
        assert r['status'] == PILLAR_STATUS
