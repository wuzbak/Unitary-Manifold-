# Copyright (C) 2026  ThomasCory Walker-Pearson
import json
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from axiom_journalist.engine.hils_review import HILSReviewRequest, format_review_output, submit_for_review
from axiom_journalist.engine.open_data_sources import (
    OPEN_DATA_SOURCES,
    build_investigative_brief,
    check_physics_integrity,
    fetch_usaspending_awards,
)
from axiom_journalist.engine.publication import (
    PublicationPolicy,
    build_dossier_packet,
    build_psicat_training_packet,
    render_dossier_markdown,
    render_psicat_training_markdown,
)


def test_open_data_sources_have_expected_keys():
    assert set(OPEN_DATA_SOURCES) == {'usaspending', 'opensecrets_base', 'court_listener'}


def test_fetch_usaspending_awards_empty_keyword_returns_empty():
    assert fetch_usaspending_awards('', limit=5) == []


def test_fetch_usaspending_awards_zero_limit_returns_empty():
    assert fetch_usaspending_awards('energy', limit=0) == []


def test_fetch_usaspending_awards_handles_network_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError('offline')

    monkeypatch.setattr('axiom_journalist.engine.open_data_sources.urlopen', boom)
    assert fetch_usaspending_awards('energy') == []


def test_fetch_usaspending_awards_parses_results(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({'results': [
                {'generated_internal_id': 'A1', 'recipient_name': 'Lab', 'award_description': 'Fusion work', 'total_obligation': 7},
            ]}).encode('utf-8')

    monkeypatch.setattr('axiom_journalist.engine.open_data_sources.urlopen', lambda *args, **kwargs: FakeResponse())
    awards = fetch_usaspending_awards('fusion', limit=1)
    assert awards == [{'award_id': 'A1', 'recipient': 'Lab', 'description': 'Fusion work', 'amount': 7, 'source': 'usaspending'}]


def test_build_investigative_brief_counts_documents_and_topic():
    brief = build_investigative_brief(['2024 report on grants', '2025 hearing summary'], 'grants')
    assert brief['topic'] == 'grants'
    assert brief['document_count'] == 2


def test_build_investigative_brief_extracts_key_terms():
    brief = build_investigative_brief(['audit audit contract disclosure'], 'oversight')
    assert 'audit' in brief['key_terms']


def test_build_investigative_brief_extracts_timeline():
    brief = build_investigative_brief(['Filed 2024-06-01 then updated 2025'], 'timeline')
    assert '2024-06-01' in brief['timeline']
    assert '2025' in brief['timeline']


def test_build_investigative_brief_extracts_sources():
    brief = build_investigative_brief(['See https://www.courtlistener.com/case/1 and https://api.usaspending.gov/item'], 'sources')
    assert 'api.usaspending.gov' in brief['sources']
    assert 'www.courtlistener.com' in brief['sources']


def test_check_physics_integrity_flags_consistent_claim():
    result = check_physics_integrity('The 5D Kaluza-Klein model preserves compact dimensions.')
    assert result['consistent'] is True
    assert 'P001' in result['related_pillars']


def test_check_physics_integrity_flags_contradiction():
    result = check_physics_integrity('The Kaluza-Klein framework has 11 compact dimensions, not 5D.')
    assert result['consistent'] is False
    assert 'P001' in result['related_pillars']


def test_check_physics_integrity_unknown_claim_is_heuristic():
    result = check_physics_integrity('Local zoning hearings changed in 2025.')
    assert result['consistent'] is True
    assert result['related_pillars'] == []


def test_hils_review_request_defaults_timestamp_and_requester():
    request = HILSReviewRequest(claim='c', evidence='e')
    assert request.requester == 'Axiom Journalist'
    assert request.timestamp


def test_submit_for_review_returns_pending_status():
    review = submit_for_review('Claim', 'Evidence')
    assert review['status'] == 'PENDING_HUMAN_REVIEW'
    assert review['review_id'].startswith('HILS-')


def test_submit_for_review_keeps_claim_and_evidence():
    review = submit_for_review('Claim', 'Evidence')
    assert review['claim'] == 'Claim'
    assert review['evidence'] == 'Evidence'


def test_format_review_output_contains_fields():
    rendered = format_review_output({'status': 'PENDING_HUMAN_REVIEW', 'review_id': 'HILS-1', 'claim': 'Claim', 'evidence': 'Evidence', 'timestamp': '2026-01-01T00:00:00+00:00', 'requester': 'Desk'})
    assert 'HILS-1' in rendered
    assert 'Desk' in rendered
    assert 'Claim' in rendered


def test_format_review_output_falls_back_when_missing_fields():
    rendered = format_review_output({})
    assert 'UNKNOWN' in rendered
    assert 'NO-ID' in rendered


def _sample_investigation_dict():
    return {
        'title': 'Contracting Irregularities',
        'lead': 'Multiple procurement records appear to conflict with public statements.',
        'journalist': 'Desk',
        'status': 'Active',
        'entities': [
            {
                'name': 'Acme Corp',
                'type': 'Organization',
                'stated_position': 'We complied with all rules.',
                'contradictions': ['Bid spreadsheet omits an affiliated vendor.'],
            },
        ],
        'sources': [
            {
                'title': 'Procurement filing',
                'tier': 'Tier 1 — Primary Record (court/regulatory/FOIA)',
                'source_type': 'Filing',
                'url_or_ref': 'https://records.example/procurement',
                'date': '2026-01-01',
            },
            {
                'title': 'Major newspaper investigation',
                'tier': 'Tier 2 — Established/On-Record',
                'source_type': 'News article',
                'url_or_ref': 'https://news.example/investigation',
                'date': '2026-01-02',
            },
        ],
        'claims': [
            {
                'statement': 'The public statement conflicts with the procurement filing.',
                'confidence': 'CORROBORATED',
                'legal_risks': 'LIBEL_EXPOSURE',
                'entities_involved': ['Acme Corp'],
                'sources': [
                    {'title': 'Procurement filing'},
                    {'title': 'Major newspaper investigation'},
                ],
            },
        ],
        'open_questions': ['Who approved the omitted vendor relationship?'],
        'scores': {
            'overall_confidence': 0.75,
            'source_quality': 0.825,
        },
    }


def test_build_dossier_packet_surfaces_evidence_and_hils_gate():
    packet = build_dossier_packet(_sample_investigation_dict())
    assert packet['publication_posture']['status'] == 'HUMAN_REVIEW_REQUIRED'
    assert packet['publication_posture']['legal_risk_level'] == 'HIGH'
    assert packet['evidence_summary']['confidence_counts']['CORROBORATED'] == 1
    assert packet['hils_gate']['status'] == 'PENDING_HUMAN_REVIEW'


def test_render_dossier_markdown_contains_claim_watchlist():
    packet = build_dossier_packet(_sample_investigation_dict())
    rendered = render_dossier_markdown(packet)
    assert 'Entity watchlist' in rendered
    assert 'Claim watchlist' in rendered
    assert 'Source ledger' in rendered
    assert 'Open questions' in rendered
    assert 'LIBEL_EXPOSURE' in rendered
    assert 'HUMAN_REVIEW_REQUIRED' in rendered


def test_build_psicat_training_packet_creates_challenge_pack():
    packet = build_psicat_training_packet(_sample_investigation_dict())
    assert packet['product'] == 'PsiCat'
    assert packet['handoff_status'] == 'READY_FOR_GOVERNED_PSICAT_STUDY'
    assert packet['challenge_pack']
    assert packet['challenge_pack'][0]['required_behavior'].startswith('preserve uncertainty')


def test_render_psicat_training_markdown_contains_targets():
    packet = build_psicat_training_packet(_sample_investigation_dict())
    rendered = render_psicat_training_markdown(packet)
    assert 'PsiCat Training / Publication Packet' in rendered
    assert 'Priority source refs' in rendered
    assert 'Challenge pack' in rendered


def test_build_dossier_packet_normalizes_no_risk_and_safe_scores():
    investigation = _sample_investigation_dict()
    investigation['scores'] = {'overall_confidence': 'nan', 'source_quality': 'inf'}
    investigation['claims'][0]['legal_risks'] = 'none identified'
    packet = build_dossier_packet(investigation)
    assert packet['scores']['overall_confidence'] == 0.0
    assert packet['scores']['source_quality'] == 0.0
    assert packet['publication_posture']['legal_risk_level'] == 'CONTROLLED'
    assert packet['evidence_summary']['legal_flags']['NONE_IDENTIFIED'] == 1


def test_build_dossier_packet_counts_multiple_legal_flags():
    investigation = _sample_investigation_dict()
    investigation['claims'][0]['legal_risks'] = 'privacy | source_protect'
    packet = build_dossier_packet(investigation)
    assert packet['evidence_summary']['legal_flags']['PRIVACY'] == 1
    assert packet['evidence_summary']['legal_flags']['SOURCE_PROTECT'] == 1
    assert packet['publication_posture']['legal_risk_level'] == 'HIGH'


def test_render_dossier_markdown_empty_state_is_explicit():
    packet = build_dossier_packet({
        'title': 'Empty packet',
        'lead': '',
        'scores': {},
        'claims': [],
        'sources': [],
        'entities': [],
        'open_questions': [],
    })
    rendered = render_dossier_markdown(packet)
    assert '_No claims recorded yet._' in rendered
    assert '_No sources recorded yet._' in rendered
    assert '_No claims recorded._' in rendered


def test_build_dossier_packet_unknown_risk_and_missing_tier_stay_explicit():
    investigation = _sample_investigation_dict()
    investigation['claims'][0]['legal_risks'] = ' privacy | custom risk '
    investigation['sources'][0]['tier'] = '   '
    packet = build_dossier_packet(investigation)
    assert packet['publication_posture']['legal_risk_level'] == 'HIGH_REVIEW'
    assert packet['publication_posture']['unclassified_risk_flags'] == ['CUSTOM_RISK']
    assert packet['evidence_summary']['source_tiers']['Unclassified'] == 1
    assert packet['evidence_summary']['legal_flags']['CUSTOM_RISK'] == 1
    assert packet['editorial_sections']['source_ledger'][0]['tier'] == 'Unclassified'


def test_build_dossier_packet_unknown_risk_without_high_flag_requires_review():
    investigation = _sample_investigation_dict()
    investigation['claims'][0]['legal_risks'] = 'custom risk'
    packet = build_dossier_packet(investigation)
    assert packet['publication_posture']['legal_risk_level'] == 'REVIEW'


def test_build_dossier_packet_whistleblower_is_high_risk():
    investigation = _sample_investigation_dict()
    investigation['claims'][0]['legal_risks'] = 'whistleblower'
    packet = build_dossier_packet(investigation)
    assert packet['publication_posture']['legal_risk_level'] == 'HIGH'


def test_build_dossier_packet_deduplicates_sources_and_detects_claim_conflicts():
    investigation = _sample_investigation_dict()
    investigation['sources'].append({
        'title': '  Procurement filing  ',
        'tier': ' Tier 1 — Primary Record (court/regulatory/FOIA) ',
        'source_type': ' Filing ',
        'url_or_ref': ' https://records.example/procurement ',
        'date': ' 2026-01-01 ',
    })
    investigation['claims'].append({
        'statement': 'Acme Corp did not conflict with the public statement in the procurement filing.',
        'confidence': 'ALLEGED',
        'legal_risks': 'NONE',
        'entities_involved': ['Acme Corp'],
        'sources': [{'title': 'Procurement filing'}],
    })
    packet = build_dossier_packet(investigation)
    assert packet['evidence_summary']['source_count'] == 2
    assert packet['evidence_summary']['duplicate_source_count'] == 1
    assert packet['evidence_summary']['source_tiers']['Tier 1 — Primary Record (court/regulatory/FOIA)'] == 1
    contradictions = packet['editorial_sections']['cross_claim_contradictions']
    assert len(contradictions) == 1
    assert contradictions[0]['claim_a'] == 'The public statement conflicts with the procurement filing.'
    assert contradictions[0]['claim_b'] == 'Acme Corp did not conflict with the public statement in the procurement filing.'
    assert 'public statement' in contradictions[0]['overlap_phrases']


def test_build_dossier_packet_keeps_sources_distinct_when_type_differs():
    investigation = _sample_investigation_dict()
    investigation['sources'].append({
        'title': 'Procurement filing',
        'tier': 'Tier 1 — Primary Record (court/regulatory/FOIA)',
        'source_type': 'Interview transcript',
        'url_or_ref': 'https://records.example/procurement',
        'date': '2026-01-01',
    })
    packet = build_dossier_packet(investigation)
    assert packet['evidence_summary']['source_count'] == 3
    assert packet['evidence_summary']['duplicate_source_count'] == 0


def test_build_psicat_training_packet_respects_policy_limits():
    investigation = _sample_investigation_dict()
    investigation['claims'].append({
        'statement': "Acme Corp didn't conflict with the public statement in the procurement filing.",
        'confidence': 'ALLEGED',
        'legal_risks': 'NONE',
        'entities_involved': ['Acme Corp'],
        'sources': [],
    })
    investigation['claims'].extend([
        {
            'statement': f'Claim number {index} about procurement disclosure.',
            'confidence': 'ALLEGED',
            'legal_risks': 'NONE',
            'entities_involved': ['Acme Corp'],
            'sources': [],
        }
        for index in range(5)
    ])
    investigation['open_questions'].extend([f'Question {index}' for index in range(5)])
    packet = build_psicat_training_packet(
        investigation,
        PublicationPolicy(max_claim_challenges=2, max_open_question_challenges=2, contradiction_overlap_minimum=2),
    )
    contradiction_checks = [item for item in packet['challenge_pack'] if item['type'] == 'contradiction-check']
    cross_claim_checks = [item for item in packet['challenge_pack'] if item['type'] == 'cross-claim-contradiction']
    open_questions = [item for item in packet['challenge_pack'] if item['type'] == 'open-question']
    assert len(contradiction_checks) == 1
    assert len(cross_claim_checks) == 1
    assert cross_claim_checks[0]['paired_claim'] == "Acme Corp didn't conflict with the public statement in the procurement filing."
    assert len(open_questions) == 2
    assert packet['policy']['max_claim_challenges'] == 2
