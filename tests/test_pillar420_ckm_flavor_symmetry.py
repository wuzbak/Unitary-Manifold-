# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 420 — CKM Flavor Symmetry Framework."""
import math
import pytest

from src.core.pillar420_ckm_flavor_symmetry import (
    PILLAR_STATUS,
    ADJACENT_TRACK,
    DELTA_ELL_12,
    DELTA_ELL_23,
    J_PDG,
    a4_vev_alignment,
    a4_ckm_predictions,
    a4_um_interface,
    a4_new_observables,
    flavor_symmetry_verdict,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'A4_FRAMEWORK_ESTABLISHED'

    def test_adjacent_track(self):
        assert ADJACENT_TRACK is True

    def test_delta_ell_12(self):
        assert DELTA_ELL_12 == pytest.approx(1.390)

    def test_delta_ell_23(self):
        assert DELTA_ELL_23 == pytest.approx(0.665)

    def test_j_pdg(self):
        assert J_PDG == pytest.approx(3.08e-5)


class TestA4VEVAlignment:
    @pytest.mark.parametrize('key', ['tan_theta_A4', 'theta_A4_deg', 'vev_direction', 'interpretation'])
    def test_expected_keys_present(self, key):
        assert key in a4_vev_alignment()

    def test_tan_theta_formula(self):
        assert a4_vev_alignment()['tan_theta_A4'] == pytest.approx(DELTA_ELL_23 / DELTA_ELL_12)

    def test_theta_range(self):
        assert 20.0 < a4_vev_alignment()['theta_A4_deg'] < 35.0

    def test_vev_direction_length(self):
        assert len(a4_vev_alignment()['vev_direction']) == 3

    @pytest.mark.parametrize('component', [1.0, 1.0, 1.0])
    def test_vev_direction_components(self, component):
        assert component in a4_vev_alignment()['vev_direction']

    def test_interpretation_mentions_um(self):
        assert 'UM' in a4_vev_alignment()['interpretation']


class TestA4CKMPredictions:
    @pytest.mark.parametrize('key', ['lambda_cabibbo', 'sin_theta_13', 'J_A4'])
    def test_expected_keys_present(self, key):
        assert key in a4_ckm_predictions()

    def test_lambda_range(self):
        value = a4_ckm_predictions()['lambda_cabibbo']
        assert 0.1 < value < 0.4

    def test_sin_theta_13_positive(self):
        assert a4_ckm_predictions()['sin_theta_13'] > 0.0

    def test_j_a4_positive(self):
        assert a4_ckm_predictions()['J_A4'] > 0.0

    def test_j_a4_same_order_as_j_pdg(self):
        ratio = a4_ckm_predictions()['J_A4'] / J_PDG
        assert 0.5 < ratio < 1.5


class TestA4UMInterface:
    @pytest.mark.parametrize('key', ['fn_charges', 'a4_vev_angle', 'connection_mechanism', 'closure_path'])
    def test_expected_keys_present(self, key):
        assert key in a4_um_interface()

    def test_angle_matches_alignment(self):
        assert a4_um_interface()['a4_vev_angle'] == pytest.approx(a4_vev_alignment()['theta_A4_deg'])

    def test_fn_charge_values(self):
        charges = a4_um_interface()['fn_charges']
        assert charges['delta_ell_12'] == pytest.approx(DELTA_ELL_12)
        assert charges['delta_ell_23'] == pytest.approx(DELTA_ELL_23)

    def test_connection_mechanism_mentions_fn(self):
        assert 'FN' in a4_um_interface()['connection_mechanism']

    def test_closure_path_mentions_a4(self):
        assert 'A4' in a4_um_interface()['closure_path']


class TestA4NewObservables:
    def test_returns_list(self):
        assert isinstance(a4_new_observables(), list)

    def test_at_least_four_observables(self):
        assert len(a4_new_observables()) >= 4

    @pytest.mark.parametrize('index', [0, 1, 2, 3])
    def test_each_entry_has_name(self, index):
        assert 'name' in a4_new_observables()[index]

    @pytest.mark.parametrize('index', [0, 1, 2, 3])
    def test_each_entry_has_sector(self, index):
        assert 'sector' in a4_new_observables()[index]

    @pytest.mark.parametrize('index', [0, 1, 2, 3])
    def test_each_entry_has_channel(self, index):
        assert 'channel' in a4_new_observables()[index]

    @pytest.mark.parametrize('index', [0, 1, 2, 3])
    def test_each_entry_has_description(self, index):
        assert 'description' in a4_new_observables()[index]


class TestFlavorSymmetryVerdict:
    @pytest.mark.parametrize('key', ['status', 'pillar_class', 'mechanism', 'required_extension', 'new_falsifiers'])
    def test_expected_keys_present(self, key):
        assert key in flavor_symmetry_verdict()

    def test_status(self):
        assert flavor_symmetry_verdict()['status'] == 'A4_FRAMEWORK_ESTABLISHED'

    def test_pillar_class(self):
        assert flavor_symmetry_verdict()['pillar_class'] == 'ADJACENT_TRACK'

    def test_new_falsifiers_nonempty(self):
        assert len(flavor_symmetry_verdict()['new_falsifiers']) >= 4

    def test_required_extension_mentions_flavor_symmetry(self):
        assert 'A4' in flavor_symmetry_verdict()['required_extension'] or 'S4' in flavor_symmetry_verdict()['required_extension']
