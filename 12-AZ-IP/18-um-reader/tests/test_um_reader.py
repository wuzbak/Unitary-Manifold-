# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
import json
import os
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from um_reader.app.server import PRODUCT_ROOT as SERVER_PRODUCT_ROOT, REPO_ROOT as SERVER_REPO_ROOT, UI_ROOT, create_server
from um_reader.engine.constants import (
    BETA_HIGH,
    BETA_LOW,
    DEFAULT_PORT,
    N_S,
    K_CS,
    R_BRAIDED,
    TOPIC_CATEGORIES,
    TOPIC_NAMES,
    TOTAL_BOOKS,
    TOTAL_ENTRIES,
    TOTAL_POSTS,
    TTS_PITCH,
    TTS_RATE,
    WINDING_NUMBER,
)
from um_reader.engine.index import (
    DEFAULT_INDEX_PATH,
    filter_by_category,
    get_categories,
    get_entry_by_id,
    get_stats,
    load_index,
    search_entries,
    validate_entry,
)
from um_reader.engine.tts import chunk_text, estimate_reading_time, preprocess_math

INDEX_PATH = PRODUCT_ROOT / 'ui' / 'reader-index.json'
HTML_PATH = PRODUCT_ROOT / 'ui' / 'index.html'
JS_PATH = PRODUCT_ROOT / 'ui' / 'um-reader.js'
README_PATH = PRODUCT_ROOT / 'README.md'
RUN_PATH = PRODUCT_ROOT / 'run.py'


@pytest.fixture(scope='module')
def entries():
    return load_index(INDEX_PATH)


@pytest.mark.parametrize(
    ('name', 'value'),
    [
        ('WINDING_NUMBER', WINDING_NUMBER),
        ('K_CS', K_CS),
        ('N_S', N_S),
        ('R_BRAIDED', R_BRAIDED),
        ('BETA_LOW', BETA_LOW),
        ('BETA_HIGH', BETA_HIGH),
        ('TOTAL_ENTRIES', TOTAL_ENTRIES),
        ('TOTAL_POSTS', TOTAL_POSTS),
        ('TOTAL_BOOKS', TOTAL_BOOKS),
        ('TOPIC_CATEGORIES', TOPIC_CATEGORIES),
        ('TTS_RATE', TTS_RATE),
        ('TTS_PITCH', TTS_PITCH),
        ('DEFAULT_PORT', DEFAULT_PORT),
    ],
)
def test_constants_defined(name, value):
    assert value is not None, name


def test_total_entries_constant():
    assert TOTAL_ENTRIES == 302


def test_topic_categories_constant():
    assert TOPIC_CATEGORIES == 9


def test_tts_rate_constant():
    assert TTS_RATE == 0.95


def test_tts_pitch_constant():
    assert TTS_PITCH == 1.05


def test_n_s_constant():
    assert N_S == 0.9635


def test_k_cs_constant():
    assert K_CS == 74


def test_winding_number_constant():
    assert WINDING_NUMBER == 5


@pytest.mark.parametrize('category', TOPIC_NAMES)
def test_topic_name_values(category):
    assert isinstance(category, str)
    assert category


def test_load_index_returns_list(entries):
    assert isinstance(entries, list)


def test_load_index_non_empty(entries):
    assert entries


def test_load_index_matches_total(entries):
    assert len(entries) == TOTAL_ENTRIES


def test_load_index_default_path_exists():
    assert DEFAULT_INDEX_PATH.exists()


def test_entries_have_summary_and_url_aliases(entries):
    sample = entries[0]
    assert sample['summary']
    assert sample['url']
    assert sample['category']


@pytest.mark.parametrize('category', ['cosmology', 'particle physics', 'consciousness', 'governance', 'geometry'])
def test_filter_by_category_returns_matching_entries(entries, category):
    filtered = filter_by_category(entries, category)
    assert filtered
    assert all(entry['category'] == category for entry in filtered)


def test_filter_by_category_all(entries):
    assert len(filter_by_category(entries, 'all')) == len(entries)


@pytest.mark.parametrize(
    ('query', 'expected_id'),
    [
        ('calendar 2032', 'post-003-litebird-2032'),
        ('brain universe coupled oscillators', 'post-014-consciousness-coupling'),
        ('governance architecture', 'post-015-unitary-pentad-standalone'),
        ('fifth dimension', 'post-004-kaluza-klein'),
        ('black hole dies', 'post-013-black-hole-information'),
        ('AxiomZero ethically', 'post-000a-axiomzero'),
    ],
)
def test_search_entries_returns_expected_match(entries, query, expected_id):
    results = search_entries(entries, query)
    assert any(entry['id'] == expected_id for entry in results)


def test_search_entries_empty_query_returns_all(entries):
    assert len(search_entries(entries, '')) == len(entries)


def test_get_categories_returns_list(entries):
    categories = get_categories(entries)
    assert isinstance(categories, list)
    assert all(isinstance(item, str) for item in categories)


def test_get_categories_has_all_nine(entries):
    categories = get_categories(entries)
    assert len(categories) == 9
    assert set(categories) == set(TOPIC_NAMES)


@pytest.mark.parametrize('entry_id', ['post-003-litebird-2032', 'post-004-kaluza-klein', 'book-falsification-decade-2025-2035'])
def test_get_entry_by_id_finds_entries(entries, entry_id):
    assert get_entry_by_id(entries, entry_id)['id'] == entry_id


def test_get_entry_by_id_missing(entries):
    assert get_entry_by_id(entries, 'does-not-exist') is None


def test_validate_entry_accepts_normalized_shape():
    entry = validate_entry({'id': 'x', 'title': 'T', 'category': 'geometry', 'url': '/x.md', 'summary': 'S'})
    assert entry['id'] == 'x'


def test_validate_entry_accepts_raw_shape():
    entry = validate_entry({'id': 'x', 'title': 'T', 'topic': 'Foundation & Core Theory', 'path': '/x.md', 'preview': 'S'})
    assert entry['category'] == 'geometry'


@pytest.mark.parametrize(
    'payload',
    [
        {'title': 'T', 'category': 'geometry', 'url': '/x.md', 'summary': 'S'},
        {'id': 'x', 'category': 'geometry', 'url': '/x.md', 'summary': 'S'},
        {'id': 'x', 'title': 'T', 'url': '/x.md', 'summary': 'S'},
        {'id': 'x', 'title': 'T', 'category': 'geometry', 'summary': 'S'},
        {'id': 'x', 'title': 'T', 'category': 'geometry', 'url': '/x.md'},
    ],
)
def test_validate_entry_rejects_invalid_shapes(payload):
    with pytest.raises(ValueError):
        validate_entry(payload)


def test_get_stats_shape(entries):
    stats = get_stats(entries)
    assert set(stats) == {'total', 'by_category', 'type_counts'}


def test_get_stats_total(entries):
    stats = get_stats(entries)
    assert stats['total'] == TOTAL_ENTRIES


def test_get_stats_type_counts(entries):
    stats = get_stats(entries)
    assert stats['type_counts']['book'] == 2
    assert stats['type_counts']['post'] == 300


def test_get_stats_category_sum(entries):
    stats = get_stats(entries)
    assert sum(stats['by_category'].values()) == TOTAL_ENTRIES


@pytest.mark.parametrize(
    ('source', 'expected'),
    [
        ('$E=mc^2$', 'E=mc 2'),
        (r'$$\frac{1}{2}$$', '1 over 2'),
        (r'\(\phi_0\)', 'phi 0'),
        (r'\[\sqrt{x}\]', 'square root of x'),
        (r'Mass \to energy', 'goes to'),
        (r'Braided \Omega', 'Omega'),
    ],
)
def test_preprocess_math(source, expected):
    assert expected in preprocess_math(source)


def test_chunk_text_respects_max_chars():
    text = ' '.join(['word'] * 120)
    chunks = chunk_text(text, max_chars=80)
    assert chunks
    assert all(len(chunk) <= 80 for chunk in chunks)


def test_chunk_text_splits_on_word_boundaries():
    chunks = chunk_text('alpha beta gamma delta epsilon', max_chars=12)
    assert chunks == ['alpha beta', 'gamma delta', 'epsilon']


def test_chunk_text_empty_string():
    assert chunk_text('', max_chars=20) == []


def test_chunk_text_invalid_limit():
    with pytest.raises(ValueError):
        chunk_text('hello', max_chars=0)


def test_estimate_reading_time_positive():
    assert estimate_reading_time('one two three four five', wpm=180) > 0


def test_estimate_reading_time_empty():
    assert estimate_reading_time('', wpm=180) == 0.0


def test_estimate_reading_time_invalid_wpm():
    with pytest.raises(ValueError):
        estimate_reading_time('hello world', wpm=0)


def test_ui_index_exists():
    assert HTML_PATH.exists()


def test_ui_js_exists():
    assert JS_PATH.exists()


def test_ui_reader_index_exists():
    assert INDEX_PATH.exists()


def test_ui_reader_index_is_valid_json():
    data = json.loads(INDEX_PATH.read_text(encoding='utf-8'))
    assert isinstance(data, list)


def test_ui_reader_index_has_many_entries():
    data = json.loads(INDEX_PATH.read_text(encoding='utf-8'))
    assert len(data) >= 100


def test_run_py_exists():
    assert RUN_PATH.exists()


def test_readme_is_large_enough():
    assert README_PATH.exists()
    assert len(README_PATH.read_text(encoding='utf-8')) >= 1000


def test_server_roots_are_correct():
    assert UI_ROOT == PRODUCT_ROOT / 'ui'
    assert SERVER_PRODUCT_ROOT == PRODUCT_ROOT
    assert SERVER_REPO_ROOT == PRODUCT_ROOT.parents[1]


def test_create_server_binds_expected_port():
    server = create_server(0)
    try:
        assert server.server_address[0] == '127.0.0.1'
    finally:
        server.server_close()


def test_html_references_local_assets():
    html = HTML_PATH.read_text(encoding='utf-8')
    assert './um-reader.js' in html
    assert './main.css' in html
    assert './az-apps.css' in html


def test_js_references_local_index():
    js = JS_PATH.read_text(encoding='utf-8')
    assert './reader-index.json' in js


def test_copied_index_uses_root_relative_paths():
    data = json.loads(INDEX_PATH.read_text(encoding='utf-8'))
    assert data[0]['path'].startswith('/')
    assert data[0]['url'].startswith('/')


def test_os_module_available_for_runtime():
    assert os.path.exists(PRODUCT_ROOT)
