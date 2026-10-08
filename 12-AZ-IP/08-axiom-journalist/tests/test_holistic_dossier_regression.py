# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Regression tests against the real AXIOM holistic investigation artifacts."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from axiom_journalist.engine.publication import (
    build_dossier_packet,
    build_story_packet,
    render_dossier_markdown,
    render_story_markdown,
)
from axiom_journalist.engine.source_ingest import parse_source_bundle
from core.investigator import Investigation, SourceTier
from db import cases as db


PRODUCT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PRODUCT_ROOT / 'output'
CASE_PATH = OUTPUT / 'holistic_axiom_case_export_2026-10-08.json'
BUNDLE_PATH = OUTPUT / 'holistic_public_record_source_bundle_2026-10-08.jsonl'
NARRATIVE_PATHS = (
    OUTPUT / 'holistic_dossier_1_cloud_platforms_and_emergency_systems_2026-10-08.md',
    OUTPUT / 'holistic_dossier_2_capital_banks_and_accountability_2026-10-08.md',
    OUTPUT / 'holistic_expose_part_1_the_data_path_2026-10-08.md',
    OUTPUT / 'holistic_expose_part_2_the_money_path_2026-10-08.md',
    OUTPUT / 'holistic_expose_part_3_the_accountability_gap_2026-10-08.md',
)


@pytest.fixture(scope='module')
def investigation():
    return json.loads(CASE_PATH.read_text(encoding='utf-8'))


def _source_identity(source):
    return tuple(
        ' '.join(str(source.get(key) or '').split()).casefold()
        for key in ('title', 'url_or_ref', 'source_type', 'date')
    )


def test_holistic_case_citations_resolve_to_its_source_ledger(investigation):
    source_ids = {_source_identity(source) for source in investigation['sources']}
    dangling = [
        (claim['id'], source.get('title', ''))
        for claim in investigation['claims']
        for source in claim.get('sources', [])
        if _source_identity(source) not in source_ids
    ]

    assert dangling == []


def test_holistic_case_builds_a_human_review_packet_without_upgrading_leads(investigation):
    assert len(investigation['entities']) == 23
    assert len(investigation['sources']) == 32
    assert len(investigation['claims']) == 52
    assert all(source.get('authentication_status') == 'NOT_RETRIEVED' for source in investigation['sources'])
    assert all(claim['confidence'] == 'UNVERIFIED' for claim in investigation['claims'])
    assert all(
        claim.get('source_capture_state') == 'SOURCE_LOCATORS_PRESENT; SOURCE_CONTENT_NOT_RETRIEVED'
        for claim in investigation['claims']
    )

    packet = build_dossier_packet(investigation)
    unlinked_claim_count = sum(not claim.get('entities_involved') for claim in investigation['claims'])

    assert packet['publication_posture']['status'] == 'HUMAN_REVIEW_REQUIRED'
    assert packet['evidence_summary']['confidence_counts'] == {'UNVERIFIED': 52}
    assert packet['evidence_summary']['source_count'] == 32
    assert packet['evidence_summary']['claims_without_linked_entities'] == unlinked_claim_count
    assert len(packet['editorial_sections']['claim_watchlist']) == 52
    assert f'Claims without linked entities: {unlinked_claim_count}' in render_dossier_markdown(packet)
    assert '2007 Epstein NPA' in next(c['statement'] for c in investigation['claims'] if c['id'] == 'EP-01')
    assert 'CIVIL ADJUDICATION; APPELLATE LOCATOR IDENTIFIED, CURRENT DOCKET UNCHECKED' in next(
        c['ledger_status'] for c in investigation['claims'] if c['id'] == 'FIN-02'
    )
    assert 'TWO DISTINCT NYDFS RECORD LOCATORS IDENTIFIED' in next(
        c['ledger_status'] for c in investigation['claims'] if c['id'] == 'FIN-04'
    )

    saved_packet = (OUTPUT / 'holistic_axiom_governed_dossier_packet_2026-10-08.md').read_text(
        encoding='utf-8'
    )
    assert 'en banc Doe opinion' not in saved_packet
    assert '*In re Wild*, 994 F.3d 1244' in saved_packet
    assert saved_packet.rstrip() == render_dossier_markdown(packet).rstrip()
    story_packet = (OUTPUT / 'holistic_axiom_story_packet_2026-10-08.md').read_text(encoding='utf-8')
    assert 'en banc Doe opinion' not in story_packet
    assert '*In re Wild*, 994 F.3d 1244' in story_packet
    assert story_packet.rstrip() == render_story_markdown(build_story_packet(investigation)).rstrip()
    assert re.search(r'\.;|(?<!\.)\.\.(?!\.)', story_packet) is None
    ledger = (OUTPUT / 'holistic_master_claim_and_money_flow_ledger_2026-10-08.md').read_text(
        encoding='utf-8'
    )
    assert '19 targeted queries (76 requests' in ledger


def test_holistic_source_bundle_preserves_provenance_in_sqlite(tmp_path):
    parsed = parse_source_bundle(BUNDLE_PATH.read_text(encoding='utf-8'))
    assert len(parsed) == 32
    assert all(row.get('notes') for row in parsed)
    assert any('not evidence' in row['notes'].casefold() for row in parsed)
    investigation = Investigation('Fixture import', 'Provenance path')
    investigation.add_source(
        parsed[0]['title'],
        SourceTier.TIER_3,
        parsed[0]['source_type'],
        parsed[0]['url_or_ref'],
        parsed[0]['date'],
        parsed[0]['excerpt'],
        parsed[0]['notes'],
    )
    assert investigation.sources[0].to_dict()['notes'] == parsed[0]['notes']

    database = tmp_path / 'axiom_cases.db'
    db.init_db(database)
    case_id = db.create_case('Holistic artifact regression', 'Fixture import', db_path=database)
    db.add_sources(case_id, parsed, db_path=database)

    stored = db.list_sources(case_id, db_path=database)
    assert len(stored) == 32
    assert [row['notes'] for row in stored] == [row['notes'] for row in parsed]


@pytest.mark.parametrize('path', NARRATIVE_PATHS, ids=lambda path: path.name)
def test_holistic_dossiers_and_exposes_keep_publication_hold_and_evidence_limits(path):
    text = path.read_text(encoding='utf-8').casefold()

    assert re.search(r'\*\*publication status:\*\*\s*hold\b', text)
    assert any(term in text for term in ('unverified', 'not retrieved', 'not established', 'not yet'))


def test_holistic_live_scan_fixture_distinguishes_dns_failures_from_no_hits():
    diagnostics = json.loads(
        (OUTPUT / 'holistic_axiom_live_scan_diagnostics_2026-10-08.json').read_text(encoding='utf-8')
    )

    assert diagnostics['queries'] == 19
    assert diagnostics['connector_attempts'] == 76
    assert diagnostics['total_records'] == 0
    assert diagnostics['run_status_counts'] == {'PARTIAL': 19}
    assert all(
        counts['ERROR'] == diagnostics['queries']
        for counts in diagnostics['connector_status_counts'].values()
    )
    assert len(diagnostics['error_summary']) == 1
    error, count = next(iter(diagnostics['error_summary'].items()))
    assert count == diagnostics['connector_attempts']
    assert 'gaierror' in error.casefold()
