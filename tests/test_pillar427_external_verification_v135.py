# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 427 — External Verification Package v13.5."""
import pytest

from src.core.pillar427_external_verification_v135 import (
    PILLAR_STATUS,
    VERSION,
    CANONICAL_TEST_COUNT,
    admissions_status_table,
    architecture_limits_table,
    predictions_table,
    falsification_protocol,
    verify_unitary_manifold,
    external_verification_report,
)

ADMISSIONS = admissions_status_table()
LIMITS = architecture_limits_table()
PREDICTIONS = predictions_table()


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'EXTERNAL_VERIFICATION_COMPLETE_V135'

    def test_version(self):
        assert VERSION == 'v13.5'

    def test_canonical_test_count_large(self):
        assert CANONICAL_TEST_COUNT >= 42000


class TestAdmissionsStatusTable:
    def test_returns_thirteen_entries(self):
        assert len(ADMISSIONS) == 13

    @pytest.mark.parametrize('number', list(range(1, 14)))
    def test_each_admission_number_present(self, number):
        assert any(a['number'] == number for a in ADMISSIONS)

    @pytest.mark.parametrize('idx', list(range(13)))
    def test_each_has_required_fields(self, idx):
        entry = ADMISSIONS[idx]
        for field in ['number', 'name', 'status', 'mechanism', 'pillar', 'callable']:
            assert field in entry

    @pytest.mark.parametrize('idx', list(range(13)))
    def test_none_open(self, idx):
        assert ADMISSIONS[idx]['status'] != 'OPEN'

    def test_admission1_observationally_selected(self):
        a1 = next(a for a in ADMISSIONS if a['number'] == 1)
        assert a1['status'] == 'OBSERVATIONALLY_SELECTED'

    def test_admission7_closed(self):
        a7 = next(a for a in ADMISSIONS if a['number'] == 7)
        assert a7['status'] == 'CLOSED'

    def test_admission10_constrained_bounded(self):
        a10 = next(a for a in ADMISSIONS if a['number'] == 10)
        assert a10['status'] == 'CONSTRAINED_BOUNDED'


class TestArchitectureLimitsTable:
    def test_returns_at_least_six_entries(self):
        assert len(LIMITS) >= 6

    @pytest.mark.parametrize('idx', list(range(8)))
    def test_each_has_domain(self, idx):
        assert 'domain' in LIMITS[idx]

    @pytest.mark.parametrize('idx', list(range(8)))
    def test_each_has_name(self, idx):
        assert 'name' in LIMITS[idx]

    @pytest.mark.parametrize('idx', list(range(8)))
    def test_each_has_honest_statement(self, idx):
        assert 'honest_statement' in LIMITS[idx]
        assert len(LIMITS[idx]['honest_statement']) > 20

    def test_baryogenesis_entry_present(self):
        assert any('baryogenesis' in l['domain'].lower() for l in LIMITS)

    def test_gluon_channel_entry_present(self):
        assert any('LHC' in l['domain'] for l in LIMITS)


class TestPredictionsTable:
    def test_returns_at_least_six_entries(self):
        assert len(PREDICTIONS) >= 6

    @pytest.mark.parametrize('idx', list(range(8)))
    def test_each_has_required_fields(self, idx):
        pred = PREDICTIONS[idx]
        for field in ['prediction', 'symbol', 'um_value', 'current_data', 'status']:
            assert field in pred

    def test_spectral_index_confirmed(self):
        ns = next(p for p in PREDICTIONS if 'spectral' in p['prediction'].lower())
        assert ns['status'] == 'CONFIRMED'

    def test_birefringence_consistent(self):
        beta = next(p for p in PREDICTIONS if 'irefringence' in p['prediction'])
        assert beta['status'] == 'CONSISTENT'

    def test_dark_energy_high_tension(self):
        de = next(p for p in PREDICTIONS if 'dark energy' in p['prediction'].lower())
        assert de['status'] == 'HIGH_TENSION'


class TestFalsificationProtocol:
    def test_returns_dict(self):
        assert isinstance(falsification_protocol(), dict)

    def test_has_primary_falsifier(self):
        assert 'primary_falsifier' in falsification_protocol()

    def test_primary_falsifier_is_litebird(self):
        pf = falsification_protocol()['primary_falsifier']
        assert 'LiteBIRD' in pf['name']

    def test_primary_falsifier_year(self):
        pf = falsification_protocol()['primary_falsifier']
        assert pf['expected_year'] == 2032

    def test_has_three_beta_outcomes(self):
        pf = falsification_protocol()['primary_falsifier']
        assert len(pf['three_outcomes']) == 3

    def test_has_secondary_falsifiers(self):
        fp = falsification_protocol()
        assert 'secondary_falsifiers' in fp
        assert len(fp['secondary_falsifiers']) >= 2


class TestVerifyUnitaryManifold:
    def test_returns_dict(self):
        assert isinstance(verify_unitary_manifold(), dict)

    def test_status(self):
        assert verify_unitary_manifold()['status'] == 'EXTERNAL_VERIFICATION_COMPLETE_V135'

    @pytest.mark.parametrize('key', ['admissions', 'architecture_limits', 'predictions',
                                     'falsification', 'overall_verdict'])
    def test_expected_keys(self, key):
        assert key in verify_unitary_manifold()

    def test_no_open_admissions(self):
        result = verify_unitary_manifold()
        assert result['admissions']['open'] == 0

    def test_thirteen_admissions_closed(self):
        result = verify_unitary_manifold()
        assert result['admissions']['closed_or_assessed'] == 13

    def test_some_predictions_confirmed(self):
        result = verify_unitary_manifold()
        assert result['predictions']['confirmed'] >= 3

    def test_overall_verdict_is_string(self):
        assert isinstance(verify_unitary_manifold()['overall_verdict'], str)


class TestExternalVerificationReport:
    def test_returns_string(self):
        assert isinstance(external_verification_report(), str)

    def test_non_empty(self):
        assert external_verification_report().strip()

    def test_contains_status(self):
        assert 'EXTERNAL_VERIFICATION_COMPLETE_V135' in external_verification_report()

    def test_contains_version(self):
        assert 'v13.5' in external_verification_report()

    def test_contains_litebird(self):
        assert 'LiteBIRD' in external_verification_report()
