# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from oracle.engine.epistemic_tagger import ADJACENT_PILLARS, HARDGATE_PILLARS, batch_tag, tag_claim
from oracle.engine.multi_model_consensus import ConsensusResult, format_consensus_report, simulate_consensus


@pytest.mark.parametrize(
    ('pillar', 'expected'),
    [
        ('P001', 'HARDGATE'),
        ('P208', 'HARDGATE'),
        ('P209', 'ADJACENT'),
        ('P785', 'ADJACENT'),
        ('P999', 'OPEN'),
        (None, 'OPEN'),
    ],
)
def test_tag_claim_uses_pillar_registry(pillar, expected):
    assert tag_claim('Test claim', pillar)['tag'] == expected


def test_tag_claim_parses_pillar_from_text():
    result = tag_claim('Claim tied to Pillar 57 and its derivation.')
    assert result['tag'] == 'HARDGATE'
    assert result['pillar'] == 'P057'


def test_tag_claim_preserves_text():
    text = 'β prediction remains registered.'
    assert tag_claim(text, 'P001')['text'] == text


def test_tag_claim_sets_hardgate_confidence_and_caveat():
    result = tag_claim('Hardgate claim', 'P004')
    assert result['confidence'] == pytest.approx(0.98)
    assert 'external falsifiers' in result['caveat']


def test_tag_claim_sets_adjacent_confidence_and_caveat():
    result = tag_claim('Adjacent claim', 'P300')
    assert result['confidence'] == pytest.approx(0.78)
    assert 'adjacent track' in result['caveat']


def test_tag_claim_sets_open_confidence_and_caveat():
    result = tag_claim('Open claim', 'P900')
    assert result['confidence'] == pytest.approx(0.42)
    assert 'explicitly open' in result['caveat']


def test_tag_claim_normalises_numeric_pillar_ids():
    assert tag_claim('Hardgate claim', '7')['pillar'] == 'P007'


def test_batch_tag_handles_text_and_claim_text_keys():
    results = batch_tag([
        {'text': 'A', 'pillar_id': 'P001'},
        {'claim_text': 'B', 'pillar': 'P400'},
    ])
    assert [item['tag'] for item in results] == ['HARDGATE', 'ADJACENT']


def test_batch_tag_defaults_missing_fields_to_open():
    result = batch_tag([{}])[0]
    assert result['tag'] == 'OPEN'
    assert result['text'] == ''


def test_hardgate_pillar_range_is_complete():
    assert min(HARDGATE_PILLARS) == 1
    assert max(HARDGATE_PILLARS) == 208
    assert len(HARDGATE_PILLARS) == 208


def test_adjacent_pillar_range_is_complete():
    assert min(ADJACENT_PILLARS) == 209
    assert max(ADJACENT_PILLARS) == 785
    assert len(ADJACENT_PILLARS) == 577


def test_consensus_result_is_dataclass_instance():
    result = simulate_consensus('Claim', 3)
    assert isinstance(result, ConsensusResult)


def test_simulate_consensus_is_deterministic():
    first = simulate_consensus('Same claim', 5)
    second = simulate_consensus('Same claim', 5)
    assert first == second


def test_simulate_consensus_respects_model_count():
    result = simulate_consensus('Model count claim', 4)
    assert len(result.tags) == 4


def test_simulate_consensus_rejects_non_positive_counts():
    with pytest.raises(ValueError):
        simulate_consensus('bad', 0)


def test_simulate_consensus_agreement_score_is_bounded():
    result = simulate_consensus('Agreement bounds', 7)
    assert 0.0 <= result.agreement_score <= 1.0


def test_simulate_consensus_uses_known_tags_only():
    result = simulate_consensus('Known tags only', 12)
    assert set(result.tags) <= {'HARDGATE', 'ADJACENT', 'OPEN'}


def test_simulate_consensus_can_follow_hardgate_base_signal():
    result = simulate_consensus('Pillar 4 closes the metric chain.', 6)
    assert 'HARDGATE' in result.tags


def test_format_consensus_report_contains_all_sections():
    report = format_consensus_report(simulate_consensus('Formatted claim', 3))
    assert 'Claim:' in report
    assert 'Tags:' in report
    assert 'Agreement:' in report
    assert 'Verdict:' in report


def test_format_consensus_report_includes_percentage():
    report = format_consensus_report(simulate_consensus('Percent claim', 3))
    assert '%' in report


def test_consensus_verdict_mentions_consensus_wording():
    result = simulate_consensus('Verdict wording claim', 3)
    assert 'consensus' in result.verdict.lower()


def test_consensus_with_single_model_is_unanimous():
    result = simulate_consensus('Single model claim', 1)
    assert result.agreement_score == 1.0
    assert result.verdict.startswith('Unanimous')
