# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Comprehensive tests for the standalone Falsification Observatory product."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from falsification_observatory import (
    BETA_C1,
    BETA_C2,
    BETA_GAP_HI,
    BETA_GAP_LO,
    BETA_KILL_SIGMA,
    BETA_WIN_MAX,
    BETA_WIN_MIN,
    DM21_PRED,
    DM21_WIN_HI,
    DM21_WIN_LO,
    K_CS,
    KK_DM_CS,
    MG_KILL_TEV,
    MG_PRED_TEV,
    N_S_PRED,
    R_KILL,
    R_PRED,
    WA_KILL_SIGMA,
    WA_PRED,
    WINDING_NUMBER,
    XENON_SENS,
    VerdictResult,
    route_act,
    route_all,
    route_desi,
    route_hllhc,
    route_juno,
    route_litebird,
    route_nedm,
    route_xenon,
)

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / 'README.md'
RUN_PY = ROOT / 'run.py'
UI_INDEX = ROOT / 'ui' / 'index.html'
UI_JS = ROOT / 'ui' / 'falsification-observatory.js'
CSS_MAIN = ROOT / 'css' / 'main.css'
CSS_APPS = ROOT / 'css' / 'az-apps.css'


class TestConstants:
    def test_beta_c1(self): assert BETA_C1 == 0.273
    def test_beta_c2(self): assert BETA_C2 == 0.331
    def test_beta_window_min(self): assert BETA_WIN_MIN == 0.22
    def test_beta_window_max(self): assert BETA_WIN_MAX == 0.38
    def test_beta_gap_low(self): assert BETA_GAP_LO == 0.29
    def test_beta_gap_high(self): assert BETA_GAP_HI == 0.31
    def test_beta_kill_sigma(self): assert BETA_KILL_SIGMA == 3.0
    def test_wa_pred(self): assert WA_PRED == 0.0
    def test_wa_kill_sigma(self): assert WA_KILL_SIGMA == 3.0
    def test_dm21_pred(self): assert DM21_PRED == 7.53e-5
    def test_dm21_window_low(self): assert DM21_WIN_LO == 7.0e-5
    def test_dm21_window_high(self): assert DM21_WIN_HI == 8.1e-5
    def test_r_pred(self): assert R_PRED == 0.0315
    def test_r_kill(self): assert R_KILL == 0.036
    def test_ns_pred(self): assert N_S_PRED == 0.9635
    def test_mg_pred(self): assert MG_PRED_TEV == 2.5
    def test_mg_kill(self): assert MG_KILL_TEV == 5.0
    def test_dm_cross_section(self): assert KK_DM_CS == 1e-46
    def test_xenon_sensitivity(self): assert XENON_SENS == 5e-47
    def test_winding_number(self): assert WINDING_NUMBER == 5
    def test_k_cs(self): assert K_CS == 74


class TestVerdictSchema:
    def test_verdict_result_fields(self):
        result = route_litebird(0.273, 0.01)
        assert result.exp_id == 'EXP-1'
        assert result.name
        assert result.verdict
        assert result.prediction
        assert hasattr(result, 'measured')
        assert hasattr(result, 'sigma_deviation')
        assert result.kill_condition
        assert result.pillar_refs
        assert result.note

    def test_verdict_result_type(self):
        assert isinstance(route_desi(0.0, 0.1), VerdictResult)

    def test_pillar_refs_all_present(self):
        for result in route_all({}):
            assert isinstance(result.pillar_refs, tuple)
            assert len(result.pillar_refs) >= 1


class TestFiles:
    def test_ui_index_exists(self): assert UI_INDEX.is_file()
    def test_ui_js_exists(self): assert UI_JS.is_file()
    def test_run_py_exists(self): assert RUN_PY.is_file()
    def test_readme_exists(self): assert README.is_file()
    def test_readme_is_long_enough(self): assert len(README.read_text()) >= 1000
    def test_css_main_exists(self): assert CSS_MAIN.is_file()
    def test_css_apps_exists(self): assert CSS_APPS.is_file()
    def test_index_has_exp_grid(self): assert 'id="exp-grid"' in UI_INDEX.read_text()
    def test_index_references_local_js(self): assert './falsification-observatory.js' in UI_INDEX.read_text()
    def test_js_has_route_litebird(self): assert 'routeLiteBIRD' in UI_JS.read_text()


@pytest.mark.parametrize(
    'beta,beta_sigma,verdict',
    [
        (None, None, 'AWAITING_DATA'),
        (0.273, 0.01, 'PASS'),
        (0.331, 0.01, 'PASS'),
        (0.50, 0.01, 'FALSIFIED'),
        (0.30, 0.001, 'FALSIFIED'),
        (0.30, 0.05, 'TENSION'),
        (0.275, 0.0005, 'TENSION'),
        (0.275, 0.01, 'PASS'),
    ],
)
def test_route_litebird_cases(beta, beta_sigma, verdict):
    result = route_litebird(beta, beta_sigma)
    assert result.verdict == verdict


def test_route_litebird_notes_and_pillars():
    result = route_litebird(0.273, 0.01)
    assert 765 in result.pillar_refs
    assert 771 in result.pillar_refs
    assert 'Nearest canonical branch' in result.note


@pytest.mark.parametrize(
    'w_a,w_a_sigma,verdict',
    [
        (0.0, None, 'PASS'),
        (0.0, 0.1, 'PASS'),
        (-0.1, None, 'TENSION'),
        (-0.5, 0.1, 'FALSIFIED'),
        (-0.2, 0.1, 'TENSION'),
        (0.31, 0.2, 'TENSION'),
        (0.31, 0.05, 'FALSIFIED'),
        (None, None, 'AWAITING_DATA'),
    ],
)
def test_route_desi_cases(w_a, w_a_sigma, verdict):
    result = route_desi(w_a, w_a_sigma)
    assert result.verdict == verdict


def test_route_desi_pillars():
    result = route_desi(0.0, 0.1)
    assert 739 in result.pillar_refs
    assert 771 in result.pillar_refs


@pytest.mark.parametrize(
    'dm21,dm21_sigma,verdict',
    [
        (7.53e-5, None, 'PASS'),
        (7.53e-5, 0.1e-5, 'PASS'),
        (6.9e-5, None, 'TENSION'),
        (6.9e-5, 0.5e-5, 'TENSION'),
        (5.0e-5, 0.1e-5, 'FALSIFIED'),
        (8.2e-5, None, 'TENSION'),
        (8.2e-5, 0.1e-5, 'FALSIFIED'),
        (None, None, 'AWAITING_DATA'),
    ],
)
def test_route_juno_cases(dm21, dm21_sigma, verdict):
    result = route_juno(dm21, dm21_sigma)
    assert result.verdict == verdict


def test_route_juno_pillars():
    result = route_juno(7.53e-5, 0.1e-5)
    assert 786 in result.pillar_refs


@pytest.mark.parametrize(
    'n_s,n_s_sigma,verdict',
    [
        (0.9635, None, 'PASS'),
        (0.9635, 0.001, 'PASS'),
        (0.9640, None, 'PASS'),
        (0.9660, None, 'TENSION'),
        (0.9700, 0.001, 'FALSIFIED'),
        (0.9610, 0.001, 'TENSION'),
        (0.9500, 0.002, 'FALSIFIED'),
        (None, None, 'AWAITING_DATA'),
    ],
)
def test_route_act_cases(n_s, n_s_sigma, verdict):
    result = route_act(n_s, n_s_sigma)
    assert result.verdict == verdict


@pytest.mark.parametrize(
    'mass_tev,observed,verdict',
    [
        (None, False, 'AWAITING_DATA'),
        (1.8, False, 'PASS'),
        (2.5, False, 'TENSION'),
        (4.0, False, 'TENSION'),
        (5.1, False, 'PASS'),
        (2.5, True, 'TENSION'),
        (4.9, True, 'TENSION'),
        (5.2, True, 'PASS'),
    ],
)
def test_route_hllhc_cases(mass_tev, observed, verdict):
    result = route_hllhc(mass_tev, observed)
    assert result.verdict == verdict


@pytest.mark.parametrize(
    'd_e,d_e_sigma,verdict',
    [
        (None, None, 'AWAITING_DATA'),
        (1e-30, None, 'PASS'),
        (1e-30, 1e-31, 'PASS'),
        (5e-29, None, 'TENSION'),
        (5e-29, 1e-29, 'TENSION'),
        (1e-27, None, 'FALSIFIED'),
        (1e-29, 1e-30, 'FALSIFIED'),
        (2e-30, 2e-30, 'PASS'),
    ],
)
def test_route_nedm_cases(d_e, d_e_sigma, verdict):
    result = route_nedm(d_e, d_e_sigma)
    assert result.verdict == verdict


@pytest.mark.parametrize(
    'sigma_cm2,verdict',
    [
        (None, 'AWAITING_DATA'),
        (1e-46, 'PASS'),
        (8e-47, 'TENSION'),
        (5e-47, 'TENSION'),
        (1e-48, 'FALSIFIED'),
        (4e-47, 'FALSIFIED'),
        (2e-46, 'PASS'),
        (9e-47, 'TENSION'),
    ],
)
def test_route_xenon_cases(sigma_cm2, verdict):
    result = route_xenon(sigma_cm2)
    assert result.verdict == verdict


def test_route_all_empty_returns_seven():
    results = route_all({})
    assert len(results) == 7
    assert all(isinstance(item, VerdictResult) for item in results)


def test_route_all_populated_values():
    results = route_all(
        {
            'beta': 0.273,
            'beta_sigma': 0.01,
            'w_a': 0.0,
            'dm21': 7.53e-5,
            'n_s': 0.9635,
            'mass_tev': 2.5,
            'observed': True,
            'd_e': 1e-30,
            'sigma_cm2': 1e-46,
        }
    )
    assert [item.exp_id for item in results] == [f'EXP-{i}' for i in range(1, 8)]


@pytest.mark.parametrize('index,expected', list(enumerate([
    'LiteBIRD Cosmic Birefringence',
    'DESI Dark Energy',
    'JUNO Neutrino Mass',
    'ACT CMB Spectral Index',
    'HL-LHC KK Gluon',
    'nEDM Electric Dipole Moment',
    'XENON-nT Dark Matter',
])))
def test_route_all_names(index, expected):
    assert route_all({})[index].name == expected


def test_route_litebird_awaiting_data():
    assert route_litebird(None).verdict == 'AWAITING_DATA'


def test_route_litebird_reference_pass():
    assert route_litebird(0.273, 0.01).verdict == 'PASS'


def test_route_litebird_reference_outside_window_falsified():
    assert route_litebird(0.50, 0.01).verdict == 'FALSIFIED'


def test_route_litebird_reference_gap_falsified():
    assert route_litebird(0.30, 0.001).verdict == 'FALSIFIED'


def test_route_desi_reference_pass():
    assert route_desi(0.0).verdict == 'PASS'


def test_route_desi_reference_tension_or_falsified():
    assert route_desi(-0.5, 0.1).verdict in {'TENSION', 'FALSIFIED'}


def test_route_juno_reference_pass():
    assert route_juno(7.53e-5).verdict == 'PASS'


def test_route_act_reference_pass():
    assert route_act(0.9635).verdict == 'PASS'


def test_route_hllhc_reference_awaiting():
    assert route_hllhc(mass_tev=None).verdict == 'AWAITING_DATA'


def test_route_xenon_reference_falsified():
    assert route_xenon(1e-48).verdict == 'FALSIFIED'
