from __future__ import annotations

from src.core.pillar709_higgs_lhc_run4_kk_signature import (
    CONVENTIONAL_RS1_KK_GEV,
    G_SM_EW,
    M_KK_GEV,
    N_W,
    PILLAR_NUMBER,
    V_HIGGS_GEV,
    higgs_coupling_kk_modification,
    kk_higgs_lhc_mass_estimate,
    lhc_kk_higgs_status,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 709


def test_conventional_reference_scale():
    assert CONVENTIONAL_RS1_KK_GEV == N_W * 2000.0


def test_mass_estimate_returns_dict():
    assert isinstance(kk_higgs_lhc_mass_estimate(), dict)


def test_um_first_mode_is_subgev():
    payload = kk_higgs_lhc_mass_estimate()
    assert payload['first_um_mode_gev'] == N_W * M_KK_GEV
    assert payload['first_um_mode_gev'] < 1.0


def test_mass_estimate_is_not_lhc_visible():
    payload = kk_higgs_lhc_mass_estimate()
    assert payload['lhc_visible'] is False
    assert payload['status'] == 'KK_HIGGS_INVISIBLE_AT_LHC'


def test_mass_reason_mentions_110_mev():
    payload = kk_higgs_lhc_mass_estimate()
    assert '110 MeV' in payload['reason']


def test_coupling_returns_dict():
    assert isinstance(higgs_coupling_kk_modification(), dict)


def test_coupling_formula():
    payload = higgs_coupling_kk_modification()
    expected_factor = 1.0 - V_HIGGS_GEV ** 2 / (2.0 * M_KK_GEV ** 2)
    assert payload['correction_factor'] == expected_factor
    assert payload['effective_coupling'] == G_SM_EW * expected_factor


def test_coupling_nonperturbative():
    payload = higgs_coupling_kk_modification()
    assert abs(payload['correction_factor']) > 1e5
    assert payload['perturbative_expansion_valid'] is False
    assert payload['status'] == 'ARCHITECTURE_LIMIT'


def test_status_payload():
    payload = lhc_kk_higgs_status()
    assert payload['status'] == 'KK_HIGGS_INVISIBLE_AT_LHC'
    assert payload['architecture_limit_certified'] is True


def test_status_contains_mass_and_coupling():
    payload = lhc_kk_higgs_status()
    for key in ('mass_estimate', 'coupling_modification'):
        assert key in payload
