# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 489 — CMB peak-3 EFT irreducibility."""
from __future__ import annotations

import math

import pytest

from src.core.pillar489_cmb_peak3_eft_irreducible import (
    A_S_FREE_PARAMETER,
    ELL_KK,
    PEAK3_SIGMA,
    PEAK_POSITIONS,
    PILLAR_LABEL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    amplitude_residual_assessment,
    eft_cap_certificate,
    irreducibility_proof,
    kk_transfer_suppression,
    peak_location_summary,
    status_report,
)


class TestConstants:
    def test_label(self):
        assert PILLAR_LABEL == 'CMB_PEAK3_FIVE_D_EFT_IRREDUCIBLE'

    def test_status(self):
        assert PILLAR_STATUS == PILLAR_LABEL

    def test_number(self):
        assert PILLAR_NUMBER == 489

    def test_version(self):
        assert VERSION == 'v15.0'

    def test_peak3_sigma(self):
        assert PEAK3_SIGMA == pytest.approx(3.1)

    def test_ell_kk(self):
        assert ELL_KK == pytest.approx(1800.0)

    def test_free_parameter(self):
        assert A_S_FREE_PARAMETER == 'alpha_GW'


@pytest.mark.parametrize('name, expected', PEAK_POSITIONS.items())
def test_peak_locations(name, expected):
    assert peak_location_summary(name)['ell'] == expected


@pytest.mark.parametrize('name', list(PEAK_POSITIONS))
def test_all_listed_peaks_are_accessible(name):
    assert peak_location_summary(name)['within_5d_window'] is True


@pytest.mark.parametrize('ell', [220.0, 540.0, 800.0, 1060.0, 1350.0, 1700.0])
def test_suppression_between_zero_and_one(ell):
    assert 0.0 < kk_transfer_suppression(ell) < 1.0


@pytest.mark.parametrize(
    'low, high',
    [(220.0, 540.0), (540.0, 800.0), (800.0, 1060.0), (1060.0, 1350.0), (1350.0, 1700.0)],
)
def test_suppression_monotone(low, high):
    assert kk_transfer_suppression(low) > kk_transfer_suppression(high)


class TestResidualAndEFTCap:
    def test_peak3_summary_distance(self):
        assert peak_location_summary('peak3')['distance_to_kk_cap'] == pytest.approx(1000.0)

    def test_peak3_summary_suppression_formula(self):
        assert peak_location_summary('peak3')['suppression_factor'] == pytest.approx(math.exp(-800.0 / 1800.0))

    def test_residual_peak_name(self):
        assert amplitude_residual_assessment()['peak'] == 'peak3'

    def test_residual_ell(self):
        assert amplitude_residual_assessment()['ell'] == 800

    def test_residual_sigma(self):
        assert amplitude_residual_assessment()['sigma_residual'] == pytest.approx(3.1)

    def test_residual_status(self):
        assert amplitude_residual_assessment()['status'] == 'NAMED_IRREDUCIBLE_5D_EFT_CAP'

    def test_residual_requires_uv(self):
        assert amplitude_residual_assessment()['requires_uv_warp_factor'] is True

    def test_eft_cap_law(self):
        assert eft_cap_certificate()['suppression_law'] == 'exp(-ell / ell_KK)'

    def test_eft_cap_highest_peak(self):
        assert eft_cap_certificate()['highest_accessible_peak'] == 'peak6'

    def test_eft_cap_peak3_accessible(self):
        assert eft_cap_certificate()['peak3_is_accessible'] is True

    def test_eft_cap_accessible_count(self):
        assert len(eft_cap_certificate()['accessible_peaks']) == 6


class TestIrreducibilityProof:
    def test_peak3_accessible_inside_5d(self):
        assert irreducibility_proof()['peak3_accessible_inside_5d'] is True

    def test_high_ell_tail_more_suppressed(self):
        assert irreducibility_proof()['high_ell_tail_suppressed'] is True

    def test_requires_uv_completion(self):
        assert irreducibility_proof()['amplitude_normalization_requires_uv_completion'] is True

    def test_irreducible_status(self):
        assert irreducibility_proof()['status'] == 'GENUINE_IRREDUCIBLE_GAP'

    def test_irreducible_statement_mentions_3p1sigma(self):
        assert '3.1σ' in irreducibility_proof()['irreducible_gap']

    def test_status_report_pillar(self):
        assert status_report()['pillar'] == 489

    def test_status_report_contains_peak_positions(self):
        assert len(status_report()['peak_positions']) == 6

    def test_status_report_contains_irreducibility(self):
        assert status_report()['irreducibility']['status'] == 'GENUINE_IRREDUCIBLE_GAP'
