# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Standalone regression tests for Product 20: OX Navigator."""

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from ox_navigator.engine import constants
from ox_navigator.engine.client import OxApiKeyMissingError, OxClient
from ox_navigator.engine.flashcard import filter_by_category, get_categories, load_flashcards
from ox_navigator.engine.gate_parser import classify_response, extract_gate_badges
from ox_navigator.engine.interrogator import get_tension_map_data, load_kb, search_kb
from ox_navigator.engine.session import OxSession

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
UI_ROOT = PRODUCT_ROOT / 'ui'
KB_PATH = UI_ROOT / 'interrogator-kb.json'
README_PATH = PRODUCT_ROOT / 'README.md'
RUN_PATH = PRODUCT_ROOT / 'run.py'


@pytest.fixture(scope='module')
def entries():
    return load_kb(KB_PATH)


@pytest.fixture(scope='module')
def cards():
    return load_flashcards()


@pytest.mark.parametrize(
    ('name', 'value'),
    [
        ('WINDING_NUMBER', 5),
        ('K_CS', 74),
        ('N_S', 0.9635),
        ('R_BRAIDED', 0.0315),
        ('BETA_C1', 0.273),
        ('BETA_C2', 0.331),
        ('MODEL_ID', 'stealth/ox-alpha'),
        ('API_BASE', 'https://openrouter.ai/api/v1'),
        ('MAX_HISTORY', 12),
        ('DEFAULT_TEMPERATURE', 0.3),
    ],
)
def test_constants_exact(name, value):
    assert getattr(constants, name) == value


def test_gate_labels_exact():
    assert constants.GATE_LABELS == ['HARDGATE', 'ADJACENT_TRACK', 'OPEN_GAP', 'ARCHITECTURE_LIMIT', 'GOVERNANCE']


def test_example_queries_count():
    assert len(constants.EXAMPLE_QUERIES) == 8


@pytest.mark.parametrize('query', constants.EXAMPLE_QUERIES)
def test_example_queries_nonempty(query):
    assert isinstance(query, str) and len(query) > 10


@pytest.mark.parametrize(
    ('text', 'expected'),
    [
        ('HARDGATE and OPEN_GAP are both present.', ['HARDGATE', 'OPEN_GAP']),
        ('adjacent_track then governance', ['ADJACENT_TRACK', 'GOVERNANCE']),
        ('Architecture_limit only', ['ARCHITECTURE_LIMIT']),
        ('No badges here', []),
        ('HARDGATE HARDGATE OPEN_GAP', ['HARDGATE', 'OPEN_GAP']),
    ],
)
def test_extract_gate_badges(text, expected):
    assert extract_gate_badges(text) == expected


def test_classify_response_returns_shape():
    result = classify_response('HARDGATE in Pillar 4 with Lean4 theorem support and P789 context.')
    assert set(result) == {'gates', 'pillars', 'has_lean4'}


def test_classify_response_detects_details():
    result = classify_response('HARDGATE. See Pillar 4, P789, and Lean4 theorem notes.')
    assert result['gates'] == ['HARDGATE']
    assert result['pillars'] == [4, 789]
    assert result['has_lean4'] is True


def test_classify_response_handles_suffix_pillars():
    result = classify_response('GOVERNANCE note at Pillar 70-B and P70-C.')
    assert result['gates'] == ['GOVERNANCE']
    assert result['pillars'] == [70]


def test_session_initial_state():
    session = OxSession()
    assert session.get_history() == []
    assert session.to_prompt_context() == 'No prior conversation.'


def test_session_add_turn_and_get_history():
    session = OxSession()
    session.add_turn('q1', 'a1')
    history = session.get_history()
    assert len(history) == 1
    assert history[0]['query'] == 'q1'
    assert history[0]['response'] == 'a1'
    assert 'timestamp' in history[0]


def test_session_clear():
    session = OxSession()
    session.add_turn('q1', 'a1')
    session.clear()
    assert session.get_history() == []


def test_session_to_prompt_context_string():
    session = OxSession()
    session.add_turn('what is n_s?', 'HARDGATE. n_s = 0.9635.')
    text = session.to_prompt_context()
    assert isinstance(text, str)
    assert 'Turn 1 User:' in text
    assert 'Turn 1 Assistant:' in text


def test_session_max_history_trim():
    session = OxSession()
    for idx in range(20):
        session.add_turn(f'q{idx}', f'a{idx}')
    history = session.get_history()
    assert len(history) == constants.MAX_HISTORY
    assert history[0]['query'] == 'q8'
    assert history[-1]['query'] == 'q19'


def test_ox_client_raises_without_key_env():
    with patch.dict(os.environ, {'OPENROUTER_API_KEY': ''}, clear=False):
        with pytest.raises(OxApiKeyMissingError):
            OxClient()


def test_ox_client_accepts_explicit_key():
    client = OxClient(api_key='test-key')
    assert client.api_key == 'test-key'
    assert client.model == constants.MODEL_ID


def test_ox_client_uses_env_key():
    with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'env-key'}, clear=False):
        client = OxClient()
        assert client.api_key == 'env-key'


class _MockResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _MockAsyncClient:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, path, json=None, headers=None):
        assert path == '/chat/completions'
        assert json['model'] == constants.MODEL_ID
        assert headers['Authorization'].startswith('Bearer ')
        return _MockResponse({'choices': [{'message': {'content': 'HARDGATE response from mock'}}]})

    async def get(self, path, headers=None):
        assert path == '/models'
        return _MockResponse({'data': [{'id': constants.MODEL_ID}, {'id': 'other/model'}]})


def test_ox_client_query_mocked():
    client = OxClient(api_key='test-key')
    session = OxSession()
    with patch('ox_navigator.engine.client.httpx.AsyncClient', _MockAsyncClient):
        answer = asyncio.run(client.query('Explain P4.', 0.3, session))
    assert answer == 'HARDGATE response from mock'


def test_ox_client_check_status_mocked():
    client = OxClient(api_key='test-key')
    with patch('ox_navigator.engine.client.httpx.AsyncClient', _MockAsyncClient):
        status = asyncio.run(client.check_status())
    assert status['ok'] is True
    assert status['model'] == constants.MODEL_ID


def test_load_kb_returns_list(entries):
    assert isinstance(entries, list)
    assert len(entries) >= 15


def test_load_kb_contains_birefringence(entries):
    assert any(e.get('id') == 'BIREFRINGENCE' for e in entries)


@pytest.mark.parametrize('term', ['birefringence', 'LiteBIRD', 'dark energy', 'neutrino', 'Planck'])
def test_search_kb_returns_results(entries, term):
    results = search_kb(entries, term)
    assert isinstance(results, list)
    assert len(results) >= 1


def test_search_kb_blank_query_returns_all(entries):
    results = search_kb(entries, '')
    assert len(results) == len(entries)


def test_tension_map_data_shape(entries):
    data = get_tension_map_data(entries)
    assert isinstance(data, list)
    assert len(data) == len(entries)
    sample = data[0]
    assert 'sigma' in sample and 'confidence' in sample and 'label' in sample


def test_tension_map_has_confidence_range(entries):
    data = get_tension_map_data(entries)
    assert all(0.0 <= point['confidence'] <= 1.0 for point in data)


def test_tension_map_has_sigma_numbers(entries):
    data = get_tension_map_data(entries)
    assert all(isinstance(point['sigma'], float) for point in data)


def test_load_flashcards_count(cards):
    assert len(cards) == 60


def test_flashcards_are_dicts(cards):
    assert all(isinstance(card, dict) for card in cards)


@pytest.mark.parametrize('field', ['id', 'category', 'front', 'back'])
def test_flashcards_have_required_fields(cards, field):
    assert all(field in card for card in cards)


@pytest.mark.parametrize('category', ['constants', 'predictions', 'gates', 'geometry', 'experiments', 'lean4', 'architecture_limits'])
def test_filter_by_category_nonempty(cards, category):
    filtered = filter_by_category(cards, category)
    assert len(filtered) >= 1
    assert all(card['category'] == category for card in filtered)


def test_get_categories(cards):
    categories = get_categories(cards)
    assert categories == ['architecture_limits', 'constants', 'experiments', 'gates', 'geometry', 'lean4', 'predictions']


@pytest.mark.parametrize('card_id', list(range(1, 61)))
def test_flashcard_ids_complete(cards, card_id):
    assert any(card['id'] == card_id for card in cards)


@pytest.mark.parametrize(
    ('card_id', 'snippet'),
    [
        (1, 'n_w = 5'),
        (2, '74'),
        (3, '12/37'),
        (9, '0.9635'),
        (10, '0.0315'),
        (11, '0.273'),
        (12, '0.351'),
        (13, 'LiteBIRD'),
        (17, 'hardgated'),
        (18, 'non-hardgate'),
        (41, 'has_lean4'),
        (49, 'OxApiKeyMissingError'),
    ],
)
def test_specific_flashcard_content(cards, card_id, snippet):
    card = next(card for card in cards if card['id'] == card_id)
    assert snippet.lower() in card['back'].lower()


@pytest.mark.parametrize('path_name', [
    'ox-navigator.html',
    'ox-navigator.js',
    'interrogator.html',
    'interrogator.js',
    'flashcard-trainer.html',
    'flashcard-trainer.js',
    'interrogator-kb.json',
    'flashcard-deck.json',
])
def test_ui_files_exist(path_name):
    assert (UI_ROOT / path_name).exists()


def test_ui_css_files_exist():
    assert (UI_ROOT / 'css' / 'main.css').exists()
    assert (UI_ROOT / 'css' / 'az-apps.css').exists()


def test_flashcard_deck_matches_python_cards(cards):
    payload = json.loads((UI_ROOT / 'flashcard-deck.json').read_text(encoding='utf-8'))
    assert 'cards' in payload
    assert len(payload['cards']) == len(cards)


def test_run_py_exists():
    assert RUN_PATH.exists()


def test_readme_exists_and_long_enough():
    assert README_PATH.exists()
    text = README_PATH.read_text(encoding='utf-8')
    assert len(text) >= 1000
    assert len(text.splitlines()) >= 600


def test_readme_mentions_required_topics():
    text = README_PATH.read_text(encoding='utf-8')
    for snippet in ['stealth/ox-alpha', '/api/ox', '/api/ox/status', 'temperature', 'session history', 'Interrogator', 'Flashcard Trainer']:
        assert snippet in text


def test_requirements_exact():
    req_text = (PRODUCT_ROOT / 'requirements.txt').read_text(encoding='utf-8').strip().splitlines()
    assert req_text == ['numpy>=1.24', 'scipy>=1.11', 'httpx>=0.26.0']
