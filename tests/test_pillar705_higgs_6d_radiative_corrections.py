from __future__ import annotations

import math

from src.core.pillar705_higgs_6d_radiative_corrections import (
    G_SM_EW,
    G_SM_EW_SQUARED,
    K_CS,
    M_H_5D_GEV,
    M_H_PDG_GEV,
    M_KK_GEV,
    N_W,
    PILLAR_NUMBER,
    higgs_6d_radiative,
    higgs_7d_radiative,
    higgs_combined_6d_7d,
    higgs_mass_6d_7d_status,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 705


def test_electroweak_alpha_matches_prompt():
    assert abs(G_SM_EW_SQUARED / (4.0 * math.pi) - 0.034) < 5e-4


def test_higgs_6d_returns_dict():
    assert isinstance(higgs_6d_radiative(), dict)


def test_higgs_6d_formula():
    result = higgs_6d_radiative()
    expected = ((G_SM_EW_SQUARED / N_W) / (16.0 * math.pi ** 2)) * (M_KK_GEV ** 2) * N_W * math.log(K_CS)
    assert abs(result['delta_m_h_sq_gev2'] - expected) < 1e-18


def test_higgs_6d_uplift_is_tiny():
    result = higgs_6d_radiative()
    assert 0.0 < result['uplift_gev'] < 1e-4


def test_higgs_6d_stays_far_below_observed():
    result = higgs_6d_radiative()
    assert result['m_h_6d_gev'] < M_H_PDG_GEV
    assert result['gap_fraction'] > 0.4


def test_higgs_7d_returns_dict():
    assert isinstance(higgs_7d_radiative(), dict)


def test_higgs_7d_formula():
    result = higgs_7d_radiative()
    expected = ((G_SM_EW_SQUARED / (N_W ** 2)) / (16.0 * math.pi ** 2)) * (M_KK_GEV ** 2) * (N_W ** 2) / K_CS
    assert abs(result['delta_m_h_sq_7d_gev2'] - expected) < 1e-18


def test_higgs_7d_smaller_than_6d():
    six_d = higgs_6d_radiative()
    seven_d = higgs_7d_radiative()
    assert seven_d['delta_m_h_sq_7d_gev2'] < six_d['delta_m_h_sq_gev2']


def test_combined_returns_dict():
    assert isinstance(higgs_combined_6d_7d(), dict)


def test_combined_mass_exceeds_5d_baseline_only_tiny_amount():
    combined = higgs_combined_6d_7d()
    assert combined['m_h_combined_gev'] > M_H_5D_GEV
    assert combined['uplift_gev'] < 1e-4


def test_combined_gap_remains_large():
    combined = higgs_combined_6d_7d()
    assert combined['gap_gev'] > 50.0
    assert combined['gap_fraction'] > 0.4


def test_status_is_architecture_limit_certified():
    status = higgs_mass_6d_7d_status()
    assert status['status'] == 'ARCHITECTURE_LIMIT_CERTIFIED'
    assert status['architecture_limit_certified'] is True


def test_status_contains_all_subreports():
    status = higgs_mass_6d_7d_status()
    for key in ('six_d', 'seven_d', 'combined'):
        assert key in status
