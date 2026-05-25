# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 481 — External Engagement Package / arXiv v14.1."""
from __future__ import annotations

from src.core.pillar481_arxiv_v141_external_engagement import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    VERSION,
    V141_CHANGELOG,
    arxiv_abstract_v141,
    arxiv_metadata_v141,
    reviewer_briefing,
    falsification_challenge_document,
    external_verification_api,
    ai_review_capability_registry,
    engagement_protocol,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'ARXIV_V141_EXTERNAL_ENGAGEMENT_READY'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 481

    def test_version(self):
        assert VERSION == 'v14.1'

    def test_changelog_from(self):
        assert V141_CHANGELOG['from_version'] == 'v14.0'

    def test_changelog_to(self):
        assert V141_CHANGELOG['to_version'] == 'v14.1'

    def test_changelog_range(self):
        assert V141_CHANGELOG['pillar_range'] == (475, 481)

    def test_n_new_pillars(self):
        assert V141_CHANGELOG['n_new_pillars'] == 7

    def test_zero_admissions(self):
        assert V141_CHANGELOG['admissions_open'] == 0

    def test_test_count_high(self):
        assert V141_CHANGELOG['test_count_min'] >= 44700


class TestArxivAbstract:
    def setup_method(self):
        self.abstract = arxiv_abstract_v141()

    def test_returns_string(self):
        assert isinstance(self.abstract, str)

    def test_substantial_length(self):
        assert len(self.abstract) > 500

    def test_mentions_n_w_5(self):
        assert 'n_w' in self.abstract or 'n_w = 5' in self.abstract

    def test_mentions_litebird(self):
        assert 'LiteBIRD' in self.abstract

    def test_mentions_preregistered(self):
        assert 'preregistered' in self.abstract.lower() or 'SHA-256' in self.abstract

    def test_mentions_birefringence(self):
        assert 'birefringence' in self.abstract.lower()

    def test_mentions_481_pillars(self):
        assert '481' in self.abstract


class TestArxivMetadata:
    def setup_method(self):
        self.meta = arxiv_metadata_v141()

    def test_returns_dict(self):
        assert isinstance(self.meta, dict)

    def test_has_title(self):
        assert 'title' in self.meta
        assert 'v14.1' in self.meta['title']

    def test_has_authors(self):
        assert 'authors' in self.meta
        assert len(self.meta['authors']) > 0

    def test_author_name(self):
        assert any('Walker' in a or 'Pearson' in a for a in self.meta['authors'])

    def test_has_categories(self):
        cats = self.meta['categories']
        assert 'hep-th' in cats

    def test_has_repo(self):
        assert 'repo' in self.meta
        assert 'github' in self.meta['repo']

    def test_has_abstract(self):
        assert 'abstract' in self.meta
        assert len(self.meta['abstract']) > 100


class TestReviewerBriefing:
    def setup_method(self):
        self.briefing = reviewer_briefing()

    def test_returns_dict(self):
        assert isinstance(self.briefing, dict)

    def test_has_title(self):
        assert 'title' in self.briefing

    def test_has_three_things(self):
        assert 'three_things_to_check' in self.briefing
        assert len(self.briefing['three_things_to_check']) >= 3

    def test_has_primary_prediction(self):
        assert 'most_checkable_prediction' in self.briefing

    def test_mentions_litebird(self):
        assert 'LiteBIRD' in self.briefing['most_checkable_prediction']

    def test_has_contact(self):
        assert 'contact' in self.briefing
        assert 'github' in self.briefing['contact'].lower()


class TestFalsificationChallenge:
    def setup_method(self):
        self.doc = falsification_challenge_document()

    def test_returns_dict(self):
        assert isinstance(self.doc, dict)

    def test_has_title(self):
        assert 'title' in self.doc

    def test_immediate_challenges(self):
        challenges = self.doc['immediate_theoretical_challenges']
        assert len(challenges) >= 4

    def test_experimental_falsifiers(self):
        exp_f = self.doc['experimental_falsifiers_2027']
        assert len(exp_f) >= 3

    def test_primary_falsifier_2032(self):
        pf = self.doc['primary_falsifier_2032']
        assert 'LiteBIRD' in pf['experiment']
        assert 'gap' in pf['falsified_if'].lower() or '0.29' in pf['falsified_if']

    def test_has_contact(self):
        assert 'contact' in self.doc

    def test_has_reward(self):
        assert 'reward' in self.doc
        assert 'falsif' in self.doc['reward'].lower()


class TestExternalVerificationAPI:
    def setup_method(self):
        self.api = external_verification_api()

    def test_returns_dict(self):
        assert isinstance(self.api, dict)

    def test_has_endpoints(self):
        assert 'endpoints' in self.api
        assert len(self.api['endpoints']) >= 5

    def test_each_endpoint_has_command(self):
        for ep in self.api['endpoints']:
            assert 'command' in ep
            assert 'returns' in ep

    def test_has_requirements(self):
        assert 'requirements' in self.api
        assert 'numpy' in self.api['requirements']

    def test_has_repo(self):
        assert 'repo' in self.api


class TestAIReviewCapabilityRegistry:
    def setup_method(self):
        self.reg = ai_review_capability_registry()

    def test_returns_dict(self):
        assert isinstance(self.reg, dict)

    def test_has_capabilities(self):
        assert 'mathematical_capabilities_needed' in self.reg
        assert len(self.reg['mathematical_capabilities_needed']) >= 5

    def test_has_key_claims(self):
        assert 'key_claims_for_review' in self.reg
        assert len(self.reg['key_claims_for_review']) >= 5

    def test_mentions_n_w_theorem(self):
        claims = self.reg['key_claims_for_review']
        assert any('n_w=5' in c or 'pure theorem' in c for c in claims)

    def test_has_entry_point(self):
        assert 'review_entry_point' in self.reg


class TestEngagementProtocol:
    def setup_method(self):
        self.proto = engagement_protocol()

    def test_returns_dict(self):
        assert isinstance(self.proto, dict)

    def test_five_paths(self):
        assert len(self.proto['paths']) == 5

    def test_has_path_a_arxiv(self):
        path_ids = [p['path'][0] for p in self.proto['paths']]
        assert 'A' in path_ids

    def test_arxiv_ready(self):
        path_a = next(p for p in self.proto['paths'] if p['path'].startswith('A'))
        assert 'READY' in path_a['status']

    def test_has_priority_order(self):
        assert 'priority_order' in self.proto
        assert 'A' in self.proto['priority_order']

    def test_has_principle(self):
        assert 'principle' in self.proto
        assert 'compromise' in self.proto['principle'].lower()


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 481

    def test_status(self):
        assert self.report['status'] == 'ARXIV_V141_EXTERNAL_ENGAGEMENT_READY'

    def test_has_all_sections(self):
        required = [
            'arxiv_metadata', 'reviewer_briefing', 'falsification_challenges',
            'verification_api', 'ai_registry', 'engagement_protocol', 'summary',
        ]
        for key in required:
            assert key in self.report, f"Missing section: {key}"

    def test_summary_mentions_arXiv(self):
        assert 'arXiv' in self.report['summary']

    def test_summary_mentions_zero_admissions(self):
        assert '0' in self.report['summary'] and 'admissions' in self.report['summary']
