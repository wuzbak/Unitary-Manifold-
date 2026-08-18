from __future__ import annotations

from src.core.pillar707_higgs_mass_gap_decomposition import (
    M_H_5D_GEV,
    M_H_PDG_GEV,
    PILLAR_NUMBER,
    gap_decomposition_table,
    higgs_gap_certification,
    mechanism_survey_result,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 707


def test_gap_table_has_five_rows():
    assert len(gap_decomposition_table()) == 5


def test_gap_table_mechanisms_present():
    mechanisms = {row['mechanism'] for row in gap_decomposition_table()}
    assert mechanisms == {
        'GHU 5D ceiling',
        '6D radiative',
        '7D radiative',
        'Hosotani orbifold',
        'Combined estimate',
    }


def test_5d_row_matches_input_ceiling():
    row = next(row for row in gap_decomposition_table() if row['mechanism'] == 'GHU 5D ceiling')
    assert row['m_h_gev'] == M_H_5D_GEV


def test_combined_is_best_mechanism():
    survey = mechanism_survey_result()
    assert survey['best_mechanism']['mechanism'] == 'Combined estimate'


def test_hosotani_is_worst_mechanism():
    survey = mechanism_survey_result()
    assert survey['worst_mechanism']['mechanism'] == 'Hosotani orbifold'


def test_all_gaps_exceed_thirty_percent():
    survey = mechanism_survey_result()
    assert survey['all_paths_leave_gt_30pct_gap'] is True


def test_gap_fractions_well_defined():
    for row in gap_decomposition_table():
        assert 0.0 < row['gap_fraction'] < 1.1


def test_combined_gap_still_large():
    row = next(row for row in gap_decomposition_table() if row['mechanism'] == 'Combined estimate')
    assert row['gap_gev'] > 50.0
    assert row['gap_fraction'] > 0.4


def test_survey_result_status():
    survey = mechanism_survey_result()
    assert survey['status'] == 'IRREDUCIBLE_AT_5D'
    assert survey['architecture_limit_certified'] is True


def test_gap_certification_status():
    cert = higgs_gap_certification()
    assert cert['status'] == 'IRREDUCIBLE_AT_5D'
    assert cert['certification'] == 'ARCHITECTURE_LIMIT_CERTIFIED'


def test_gap_certification_summary_mentions_residual_gap():
    cert = higgs_gap_certification()
    assert '30%' in cert['summary']
    assert str(M_H_PDG_GEV) in cert['summary']
