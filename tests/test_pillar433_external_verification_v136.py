# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 433 — External Verification Package v13.6."""
from __future__ import annotations

import pytest

from src.core.pillar433_external_verification_v136 import (
    PILLAR_STATUS,
    VERSION,
    CANONICAL_TEST_COUNT,
    SPRINT_PILLARS,
    admissions_status_table,
    architecture_limits_table,
    predictions_table,
    falsification_protocol,
    sprint_delta,
    verify_unitary_manifold,
    external_verification_report,
)

ADMISSIONS = admissions_status_table()
LIMITS = architecture_limits_table()
PREDICTIONS = predictions_table()


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'EXTERNAL_VERIFICATION_COMPLETE_V136'

    def test_version(self):
        assert VERSION == 'v13.6'

    def test_canonical_test_count_large(self):
        assert CANONICAL_TEST_COUNT >= 42000

    def test_sprint_pillars_count(self):
        assert len(SPRINT_PILLARS) == 6

    def test_sprint_pillar_numbers(self):
        numbers = {p['pillar'] for p in SPRINT_PILLARS}
        assert numbers == {428, 429, 430, 431, 432, 433}


class TestSprintPillars:
    def test_each_has_required_fields(self):
        for p in SPRINT_PILLARS:
            for field in ['pillar', 'title', 'status', 'label_delta', 'adjacency']:
                assert field in p

    def test_adjacency_flags_correct(self):
        # P431 and P432 are adjacent tracks
        p431 = next(p for p in SPRINT_PILLARS if p['pillar'] == 431)
        p432 = next(p for p in SPRINT_PILLARS if p['pillar'] == 432)
        assert p431['adjacency']
        assert p432['adjacency']

    def test_non_adjacency_flags_correct(self):
        # P429, P430, P433 are hardgate
        for pillar_num in [429, 430, 433]:
            p = next(p for p in SPRINT_PILLARS if p['pillar'] == pillar_num)
            assert not p['adjacency']

    def test_p429_status(self):
        p429 = next(p for p in SPRINT_PILLARS if p['pillar'] == 429)
        assert p429['status'] == 'HIERARCHY_FULLY_CONSTRAINED'

    def test_p430_status(self):
        p430 = next(p for p in SPRINT_PILLARS if p['pillar'] == 430)
        assert p430['status'] == 'GLUON_CHANNEL_BESSEL_EXACT'

    def test_p431_status(self):
        p431 = next(p for p in SPRINT_PILLARS if p['pillar'] == 431)
        assert p431['status'] == 'LATTICE_BRAID_QFT_FORMALLY_SCOPED'

    def test_p432_status(self):
        p432 = next(p for p in SPRINT_PILLARS if p['pillar'] == 432)
        assert p432['status'] == 'SIXD_BARYOGENESIS_EXTENSION_SCOPED'

    def test_p433_status(self):
        p433 = next(p for p in SPRINT_PILLARS if p['pillar'] == 433)
        assert p433['status'] == 'EXTERNAL_VERIFICATION_COMPLETE_V136'


class TestAdmissionsStatusTable:
    def test_returns_thirteen_entries(self):
        assert len(ADMISSIONS) == 13

    @pytest.mark.parametrize('number', list(range(1, 14)))
    def test_each_admission_number_present(self, number):
        assert any(a['number'] == number for a in ADMISSIONS)

    @pytest.mark.parametrize('idx', list(range(13)))
    def test_each_has_required_fields(self, idx):
        entry = ADMISSIONS[idx]
        for field in ['number', 'name', 'status', 'mechanism', 'pillar', 'callable', 'v136_note']:
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

    def test_admission10_updated_in_v136(self):
        a10 = next(a for a in ADMISSIONS if a['number'] == 10)
        # Admission 10 should be updated to reflect Bessel-exact from P430
        assert 'BESSEL' in a10['status'] or 'CONSTRAINED' in a10['status']
        # P430 should be in the pillar reference
        assert '430' in a10['pillar']

    def test_admission10_v136_note_updated(self):
        a10 = next(a for a in ADMISSIONS if a['number'] == 10)
        assert 'UPDATED' in a10['v136_note']

    def test_all_admissions_have_callable(self):
        for a in ADMISSIONS:
            assert len(a['callable']) > 0


class TestArchitectureLimitsTable:
    def test_at_least_seven_limits(self):
        assert len(LIMITS) >= 7

    def test_each_has_required_keys(self):
        for limit in LIMITS:
            for key in ['domain', 'name', 'status', 'certifying_pillar',
                        'honest_statement', 'v136_note']:
                assert key in limit

    def test_baryogenesis_limit_present(self):
        domains = [l['domain'] for l in LIMITS]
        assert 'baryogenesis' in domains

    def test_lhc_gluon_updated_in_v136(self):
        lhc = next((l for l in LIMITS if l['domain'] == 'LHC'), None)
        if lhc:
            assert 'UPDATED' in lhc['v136_note']

    def test_cmb_spectral_limit_present(self):
        domains = [l['domain'] for l in LIMITS]
        assert 'CMB spectral index' in domains or 'CMB' in str(domains)

    def test_l2_gamma_limit_v136_note(self):
        l2 = next((l for l in LIMITS if 'L2' in l['name'] or 'γ gap' in l['name']), None)
        if l2:
            assert 'P431' in l2['v136_note']

    def test_dark_energy_limit_present(self):
        domains = [l['domain'] for l in LIMITS]
        assert 'dark energy' in domains

    def test_baryogenesis_v136_note_mentions_p432(self):
        bary = next((l for l in LIMITS if l['domain'] == 'baryogenesis'), None)
        if bary:
            assert 'P432' in bary['v136_note']


class TestPredictionsTable:
    def test_eight_predictions(self):
        assert len(PREDICTIONS) == 8

    def test_each_has_required_keys(self):
        for pred in PREDICTIONS:
            for key in ['prediction', 'symbol', 'um_value', 'current_data',
                        'agreement', 'status', 'falsification_window']:
                assert key in pred

    def test_four_confirmed(self):
        n_confirmed = sum(1 for p in PREDICTIONS if p['status'] == 'CONFIRMED')
        assert n_confirmed == 4

    def test_two_high_tension(self):
        n_tension = sum(1 for p in PREDICTIONS if p['status'] == 'HIGH_TENSION')
        assert n_tension == 2

    def test_ns_confirmed(self):
        ns = next(p for p in PREDICTIONS if p['symbol'] == 'nₛ')
        assert ns['status'] == 'CONFIRMED'

    def test_r_high_tension(self):
        r = next(p for p in PREDICTIONS if p['symbol'] == 'r')
        assert r['status'] == 'HIGH_TENSION'

    def test_dark_energy_updated_in_v136(self):
        de = next(p for p in PREDICTIONS if 'w₀' in p['symbol'])
        assert 'P428' in de['um_value'] or 'frozen' in de['um_value']

    def test_birefringence_present(self):
        symbols = [p['symbol'] for p in PREDICTIONS]
        assert 'β' in symbols


class TestFalsificationProtocol:
    def setup_method(self):
        self.fp = falsification_protocol()

    def test_primary_falsifier_present(self):
        assert 'primary_falsifier' in self.fp

    def test_litebird_is_primary(self):
        assert 'LiteBIRD' in self.fp['primary_falsifier']['name']

    def test_three_outcomes(self):
        assert len(self.fp['primary_falsifier']['three_outcomes']) == 3

    def test_secondary_falsifiers_present(self):
        assert 'secondary_falsifiers' in self.fp
        assert len(self.fp['secondary_falsifiers']) >= 2

    def test_v136_additions_present(self):
        assert 'v136_additions' in self.fp
        assert len(self.fp['v136_additions']) >= 2

    def test_nedm_in_v136_additions(self):
        names = [a['name'] for a in self.fp['v136_additions']]
        assert any('nEDM' in n or 'EDM' in n for n in names)

    def test_primary_falsifier_year(self):
        assert self.fp['primary_falsifier']['expected_year'] == 2032

    def test_desi_in_secondary(self):
        names = [f['name'] for f in self.fp['secondary_falsifiers']]
        assert any('DESI' in n for n in names)


class TestSprintDelta:
    def setup_method(self):
        self.delta = sprint_delta()

    def test_version_from_v135(self):
        assert self.delta['version_from'] == 'v13.5'

    def test_version_to_v136(self):
        assert self.delta['version_to'] == 'v13.6'

    def test_pillars_added_list(self):
        assert set(self.delta['pillars_added']) == {428, 429, 430, 431, 432, 433}

    def test_adjacent_track_pillars(self):
        assert set(self.delta['adjacent_track_pillars']) == {431, 432}

    def test_hardgate_changes_present(self):
        assert len(self.delta['hardgate_claim_changes']) >= 2

    def test_label_deltas_present(self):
        assert len(self.delta['label_deltas']) >= 2


class TestVerifyUnitaryManifold:
    def setup_method(self):
        self.result = verify_unitary_manifold()

    def test_status(self):
        assert self.result['status'] == 'EXTERNAL_VERIFICATION_COMPLETE_V136'

    def test_version(self):
        assert self.result['version'] == 'v13.6'

    def test_canonical_test_count(self):
        assert self.result['canonical_test_count'] >= 42000

    def test_admissions_zero_open(self):
        assert self.result['admissions']['open'] == 0

    def test_thirteen_admissions(self):
        assert self.result['admissions']['total'] == 13

    def test_eight_limits(self):
        assert self.result['architecture_limits']['total'] == 8

    def test_four_confirmed_predictions(self):
        assert self.result['predictions']['confirmed'] == 4

    def test_two_high_tension(self):
        assert self.result['predictions']['high_tension'] == 2

    def test_framework_health_pass(self):
        assert self.result['health']['framework_health'] == 'PASS'

    def test_sprint_present(self):
        assert 'sprint' in self.result
        assert len(self.result['sprint']) == 6


class TestExternalVerificationReport:
    def setup_method(self):
        self.report = external_verification_report()

    def test_returns_string(self):
        assert isinstance(self.report, str)

    def test_mentions_v136(self):
        assert 'v13.6' in self.report

    def test_mentions_status(self):
        assert 'EXTERNAL_VERIFICATION_COMPLETE_V136' in self.report

    def test_mentions_sprint_pillars(self):
        for num in [428, 429, 430, 431, 432, 433]:
            assert f'P{num}' in self.report

    def test_mentions_adjacent_track(self):
        assert '🔵' in self.report

    def test_mentions_test_count(self):
        assert '42' in self.report  # Canonical test count starts with 42xxx
