# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import json

import pytest

from delphi.engine.hypothesis_explorer import ORACLE_CHANNELS, explore_hypothesis, get_uncertainty_quantification
from delphi.engine.open_science_mode import export_hypothesis_as_json, submit_hypothesis


def test_oracle_channels_has_five_entries():
    assert len(ORACLE_CHANNELS) == 5


def test_oracle_channels_have_required_keys():
    required = {'id', 'name', 'pillar', 'prediction', 'falsifier'}
    for channel in ORACLE_CHANNELS:
        assert required <= set(channel)


def test_oracle_channels_include_birefringence_spec():
    channel = next(item for item in ORACLE_CHANNELS if item['id'] == 'birefringence')
    assert channel['pillar'] == 'P001'
    assert channel['prediction'] == 'β ∈ [0.22°, 0.38°]'
    assert channel['falsifier'] == 'LiteBIRD 2032'


def test_explore_hypothesis_returns_expected_shape():
    result = explore_hypothesis('Test hypothesis', 'geo')
    assert set(result) == {
        'hypothesis', 'channel', 'supporting_pillars', 'contradicting_pillars', 'confidence_interval', 'status'
    }


def test_explore_hypothesis_uses_requested_channel_id():
    assert explore_hypothesis('Question', 'desi')['channel'] == 'desi'


def test_explore_hypothesis_raises_for_unknown_channel():
    with pytest.raises(ValueError):
        explore_hypothesis('Question', 'unknown')


def test_explore_hypothesis_returns_supporting_pillars():
    result = explore_hypothesis('metric chain', 'geo')
    assert 'P858' in result['supporting_pillars']
    assert 'P859' in result['supporting_pillars']


def test_explore_hypothesis_returns_contradicting_pillars_for_desi():
    result = explore_hypothesis('dark-energy test', 'desi')
    assert 'P860' in result['contradicting_pillars']


def test_explore_hypothesis_keeps_birefringence_interval():
    result = explore_hypothesis('β window test', 'birefringence')
    assert result['confidence_interval'] == 'β ∈ [0.22°, 0.38°]'


def test_explore_hypothesis_marks_stressed_claims_open():
    result = explore_hypothesis('This channel is falsified by outside data.', 'geo')
    assert result['status'] == 'OPEN'
    assert 'P858' in result['contradicting_pillars']


def test_explore_hypothesis_keeps_yukawa_adjacent_status():
    result = explore_hypothesis('Yukawa texture route', 'yukawa')
    assert result['status'] == 'ADJACENT'


def test_get_uncertainty_quantification_returns_shape():
    result = get_uncertainty_quantification(1)
    assert set(result) == {'pillar', 'status', 'confidence', 'caveat'}


def test_get_uncertainty_quantification_hardgate_default_closed():
    result = get_uncertainty_quantification(4)
    assert result['status'] == 'CLOSED'
    assert result['confidence'] == pytest.approx(0.91)


def test_get_uncertainty_quantification_adjacent_default_partial():
    result = get_uncertainty_quantification(300)
    assert result['status'] == 'PARTIAL'
    assert result['confidence'] == pytest.approx(0.62)


def test_get_uncertainty_quantification_unknown_is_open():
    result = get_uncertainty_quantification(900)
    assert result['status'] == 'OPEN'
    assert result['confidence'] == pytest.approx(0.35)


def test_get_uncertainty_quantification_override_for_837():
    result = get_uncertainty_quantification(837)
    assert result['status'] == 'PARTIAL'
    assert 'c₁ = 3' in result['caveat']


def test_get_uncertainty_quantification_override_for_849():
    result = get_uncertainty_quantification(849)
    assert result['status'] == 'CLOSED'
    assert result['confidence'] == pytest.approx(0.86)


def test_submit_hypothesis_requires_nonempty_hypothesis():
    with pytest.raises(ValueError):
        submit_hypothesis('', 'evidence')


def test_submit_hypothesis_handles_missing_evidence():
    result = submit_hypothesis('Hypothesis', '')
    assert result['status'] == 'insufficient_evidence'
    assert result['evidence_score'] == pytest.approx(0.0)


def test_submit_hypothesis_detects_numeric_signal():
    result = submit_hypothesis('Hypothesis', 'Measured residual = 0.12 in test 4.')
    assert result['has_numeric_signal'] is True


def test_submit_hypothesis_detects_citation_signal():
    result = submit_hypothesis('Hypothesis', 'See doi:10.5281/zenodo.19584531 and table 2.')
    assert result['has_citation_signal'] is True


def test_submit_hypothesis_ready_for_review_on_strong_evidence():
    evidence = 'doi:10.5281/zenodo.19584531 table 2 test residual 0.12 ' * 6
    result = submit_hypothesis('Hypothesis', evidence)
    assert result['status'] == 'ready_for_review'


def test_submit_hypothesis_needs_more_evidence_for_short_note():
    result = submit_hypothesis('Hypothesis', 'Qualitative note only.')
    assert result['status'] == 'needs_more_evidence'


def test_export_hypothesis_as_json_round_trips():
    payload = submit_hypothesis('Hypothesis', 'test 1 with 0.2 residual')
    encoded = export_hypothesis_as_json(payload)
    assert json.loads(encoded) == payload


def test_export_hypothesis_as_json_is_pretty_printed():
    encoded = export_hypothesis_as_json({'b': 1, 'a': 2})
    assert '\n' in encoded
    assert encoded.index('"a"') < encoded.index('"b"')
