# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.integrations.webspace_bridge import (
    handle_webspace_bridge_request,
    load_psicat_state,
    receive_investigation,
    send_dossier,
    send_training_packet,
)


def _sample_investigation() -> dict:
    return {
        'title': 'Acme Review',
        'lead': 'Public filings conflict with statements.',
        'entities': [{'name': 'Acme Corp', 'type': 'Organization', 'stated_position': 'Nothing to see here.', 'contradictions': ['Filing says otherwise.']}],
        'sources': [{'title': 'Filing', 'tier': 'Tier 1 — Primary Record (court/regulatory/FOIA)', 'source_type': 'Filing', 'url_or_ref': 'https://records.example/acme', 'date': '2026-01-01'}],
        'claims': [{'statement': 'The filing conflicts with the statement.', 'confidence': 'CORROBORATED', 'legal_risks': 'NONE', 'entities_involved': ['Acme Corp'], 'sources': [{'title': 'Filing'}]}],
        'open_questions': ['Who approved the filing?'],
        'scores': {'overall_confidence': 0.75, 'source_quality': 1.0},
    }


def test_receive_investigation_persists_state(tmp_path):
    state_path = tmp_path / 'psicat_state.json'
    status, payload = receive_investigation(
        {'investigation': _sample_investigation(), 'investigation_id': 'acme'},
        provided_secret='shared',
        expected_secret='shared',
        path=state_path,
    )
    assert status == 200
    assert payload['investigation_id'] == 'acme'
    state = load_psicat_state(state_path)
    assert state['latest_investigation_id'] == 'acme'


def test_send_dossier_and_training_packet_require_auth(tmp_path):
    state_path = tmp_path / 'psicat_state.json'
    receive_investigation({'investigation': _sample_investigation(), 'investigation_id': 'acme'}, provided_secret='shared', expected_secret='shared', path=state_path)
    status, payload = send_dossier(provided_secret='wrong', expected_secret='shared', path=state_path)
    assert status == 401
    assert payload['ok'] is False
    status, payload = send_training_packet(provided_secret='shared', expected_secret='shared', path=state_path)
    assert status == 200
    assert payload['training_packet']['product'] == 'PsiCat'


def test_handle_webspace_bridge_request_routes_endpoints(tmp_path):
    state_path = tmp_path / 'psicat_state.json'
    status, payload = handle_webspace_bridge_request(
        'POST',
        '/api/psicat/receive_investigation',
        headers={'X-PsiCat-Shared-Secret': 'shared'},
        body={'investigation': _sample_investigation(), 'investigation_id': 'acme'},
        expected_secret='shared',
        state_path=state_path,
    )
    assert status == 200
    status, payload = handle_webspace_bridge_request(
        'GET',
        '/api/psicat/send_dossier',
        headers={'X-PsiCat-Shared-Secret': 'shared', 'X-Investigation-Id': 'acme'},
        body=None,
        expected_secret='shared',
        state_path=state_path,
    )
    assert status == 200
    assert payload['dossier']['title'] == 'Acme Review'
