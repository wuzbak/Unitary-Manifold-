# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 418 — Kawamura Z₂ internal derivation."""
import pytest

from src.core.pillar418_kawamura_z2_internal import (
    PILLAR_STATUS,
    KAWAMURA_STATUS,
    kawamura_parity_matrix,
    bmu_z2_parity_constraint,
    su5_zero_mode_spectrum,
    kawamura_derivation_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'DERIVATION_PATH_IDENTIFIED'

    def test_kawamura_status(self):
        assert KAWAMURA_STATUS == 'DERIVATION_PATH_IDENTIFIED'


class TestKawamuraParityMatrix:
    def test_returns_list(self):
        assert isinstance(kawamura_parity_matrix(), list)

    def test_exact_entries(self):
        assert kawamura_parity_matrix() == [1, 1, 1, -1, -1]

    def test_three_plus_two_split(self):
        P = kawamura_parity_matrix()
        assert P.count(1) == 3
        assert P.count(-1) == 2


class TestBmuParityConstraint:
    def test_returns_dict(self):
        assert isinstance(bmu_z2_parity_constraint(), dict)

    def test_bmu_is_odd(self):
        assert bmu_z2_parity_constraint()['bmu_parity'] == -1

    def test_forced_matrix_matches(self):
        assert bmu_z2_parity_constraint()['forced_parity_matrix'] == kawamura_parity_matrix()

    def test_constraint_status(self):
        assert bmu_z2_parity_constraint()['constraint_status'] == 'UNIQUE_CANONICAL_CHOICE'


class TestSu5ZeroModeSpectrum:
    def test_returns_dict(self):
        assert isinstance(su5_zero_mode_spectrum(kawamura_parity_matrix()), dict)

    def test_sm_group_preserved(self):
        assert su5_zero_mode_spectrum(kawamura_parity_matrix())['zero_mode_group'] == 'SU(3)×SU(2)×U(1)'

    def test_su3_zero_modes(self):
        assert su5_zero_mode_spectrum(kawamura_parity_matrix())['su3_zero_modes'] == 8

    def test_su2_zero_modes(self):
        assert su5_zero_mode_spectrum(kawamura_parity_matrix())['su2_zero_modes'] == 3

    def test_u1_zero_mode(self):
        assert su5_zero_mode_spectrum(kawamura_parity_matrix())['u1_zero_modes'] == 1

    def test_xy_broken(self):
        assert su5_zero_mode_spectrum(kawamura_parity_matrix())['broken_xy_generators'] == 12

    def test_noncanonical_pattern_not_sm(self):
        assert su5_zero_mode_spectrum([1, -1, 1, -1, 1])['zero_mode_group'] == 'non-canonical'


class TestVerdict:
    def test_returns_dict(self):
        assert isinstance(kawamura_derivation_verdict(), dict)

    def test_status(self):
        assert kawamura_derivation_verdict()['status'] == 'DERIVATION_PATH_IDENTIFIED'

    def test_previous_status(self):
        assert kawamura_derivation_verdict()['previous_status'] == 'OPEN'

    def test_new_status(self):
        assert kawamura_derivation_verdict()['new_status'] == 'DERIVATION_PATH_IDENTIFIED'

    def test_parity_matrix_exported(self):
        assert kawamura_derivation_verdict()['parity_matrix'] == [1, 1, 1, -1, -1]

    def test_zero_mode_group_exported(self):
        assert kawamura_derivation_verdict()['zero_mode_group'] == 'SU(3)×SU(2)×U(1)'

    def test_verdict_mentions_kawamura(self):
        assert 'Kawamura' in kawamura_derivation_verdict()['verdict']
