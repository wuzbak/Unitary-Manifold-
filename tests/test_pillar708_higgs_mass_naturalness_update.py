from __future__ import annotations

import math

from src.core.pillar708_higgs_mass_naturalness_update import (
    DELTA_5D,
    DELTA_6D_NLO,
    G_SM_EW,
    K_CS,
    M_H_PDG_GEV,
    M_KK_GEV,
    N_W,
    PILLAR_NUMBER,
    naturalness_7d_correction,
    naturalness_combined,
    naturalness_status,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 708


def test_delta_6d_nlo_is_natural():
    assert DELTA_6D_NLO < 100.0


def test_7d_correction_returns_dict():
    assert isinstance(naturalness_7d_correction(), dict)


def test_7d_delta_formula():
    payload = naturalness_7d_correction()
    expected_m2 = ((G_SM_EW ** 2 / (N_W ** 2)) / (16.0 * math.pi ** 2)) * (M_KK_GEV ** 2) * (N_W ** 2) / K_CS
    expected_delta = expected_m2 / (M_H_PDG_GEV ** 2)
    assert abs(payload['delta_m_h_sq_7d_gev2'] - expected_m2) < 1e-18
    assert abs(payload['delta_7d'] - expected_delta) < 1e-24


def test_7d_delta_is_tiny():
    payload = naturalness_7d_correction()
    assert payload['delta_7d'] < 1e-9
    assert payload['subdominant'] is True


def test_combined_returns_dict():
    assert isinstance(naturalness_combined(), dict)


def test_combined_formula():
    payload = naturalness_combined()
    expected = math.sqrt(DELTA_5D ** 2 + DELTA_6D_NLO ** 2 + naturalness_7d_correction()['delta_7d'] ** 2)
    assert abs(payload['delta_total'] - expected) < 1e-15


def test_combined_status_natural():
    payload = naturalness_combined()
    assert payload['status'] == 'NATURAL'
    assert payload['technically_natural'] is True


def test_combined_dominated_by_6d_term():
    payload = naturalness_combined()
    assert payload['delta_total'] > DELTA_6D_NLO
    assert payload['delta_total'] < 10.0


def test_status_payload():
    payload = naturalness_status()
    assert payload['status'] == 'NATURAL'
    assert payload['architecture_limit'] is False


def test_status_contains_subreports():
    payload = naturalness_status()
    for key in ('delta_7d', 'combined'):
        assert key in payload
