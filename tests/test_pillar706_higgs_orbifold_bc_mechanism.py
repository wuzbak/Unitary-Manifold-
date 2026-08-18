from __future__ import annotations

import math

from src.core.pillar706_higgs_orbifold_bc_mechanism import (
    G_SM_EW,
    K_CS,
    M_H_PDG_GEV,
    M_KK_GEV,
    N_W,
    PILLAR_NUMBER,
    V_HIGGS_GEV,
    higgs_mass_hosotani,
    higgs_vev_hosotani,
    hosotani_phase,
    hosotani_status,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 706


def test_phase_formula():
    phase = hosotani_phase()
    assert abs(phase['theta_h'] - math.pi * N_W / K_CS) < 1e-15


def test_phase_fraction():
    phase = hosotani_phase()
    assert abs(phase['theta_h_over_pi'] - N_W / K_CS) < 1e-15


def test_mass_returns_dict():
    assert isinstance(higgs_mass_hosotani(), dict)


def test_shape_function_positive():
    mass = higgs_mass_hosotani()
    assert mass['shape_function'] > 0.0


def test_hosotani_mass_formula():
    theta = math.pi * N_W / K_CS
    shape = 2.0 * math.sin(theta) ** 2 * (2.0 + math.cos(2.0 * theta)) / (1.0 + math.cos(theta))
    expected = math.sqrt((G_SM_EW ** 2 * M_KK_GEV ** 2 / (16.0 * math.pi ** 2)) * shape)
    assert abs(higgs_mass_hosotani()['m_h_hosotani_gev'] - expected) < 1e-15


def test_hosotani_mass_is_tiny():
    mass = higgs_mass_hosotani()
    assert 0.0 < mass['m_h_hosotani_gev'] < 0.01


def test_hosotani_gap_is_large():
    mass = higgs_mass_hosotani()
    assert mass['m_h_hosotani_gev'] < M_H_PDG_GEV
    assert mass['gap_fraction'] > 0.99


def test_vev_returns_dict():
    assert isinstance(higgs_vev_hosotani(), dict)


def test_vev_formula():
    theta = math.pi * N_W / K_CS
    expected = M_KK_GEV * math.sin(theta) / (G_SM_EW * math.sqrt(2.0))
    assert abs(higgs_vev_hosotani()['v_h_hosotani_gev'] - expected) < 1e-15


def test_vev_far_below_sm_value():
    vev = higgs_vev_hosotani()
    assert vev['v_h_hosotani_gev'] < 1.0
    assert vev['vev_ratio_to_sm'] < 0.001
    assert V_HIGGS_GEV == 246.0


def test_status_architecture_limit():
    status = hosotani_status()
    assert status['status'] == 'ARCHITECTURE_LIMIT_CERTIFIED'
    assert status['architecture_limit_certified'] is True


def test_status_contains_phase_mass_vev():
    status = hosotani_status()
    for key in ('phase', 'mass', 'vev'):
        assert key in status
