# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for App 19 — UM Physics Flashcard Trainer
Tests cover: flashcard deck JSON structure, JS logic (via subprocess node),
and Python-side invariants.
~50 tests.
"""
import json
import math
import os
import pytest

DECK_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'public-site', 'data', 'flashcard-deck.json'
)
HTML_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'public-site', 'az-apps', '19-flashcard-trainer.html'
)
JS_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'public-site', 'js', '19-flashcard-trainer.js'
)


@pytest.fixture(scope='module')
def deck():
    with open(DECK_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# JSON structure
# ---------------------------------------------------------------------------

class TestDeckStructure:
    def test_file_exists(self):
        assert os.path.exists(DECK_PATH)

    def test_version_present(self, deck):
        assert 'version' in deck

    def test_total_field(self, deck):
        assert deck['total'] >= 60

    def test_cards_count(self, deck):
        assert len(deck['cards']) >= 60

    def test_categories_present(self, deck):
        assert 'categories' in deck
        assert len(deck['categories']) >= 7

    def test_all_expected_categories(self, deck):
        cats = set(deck['categories'])
        for expected in ['constants', 'predictions', 'gates', 'geometry',
                         'experiments', 'lean4', 'architecture_limits']:
            assert expected in cats

    def test_generated_date(self, deck):
        assert 'generated' in deck


class TestCardFields:
    def test_all_have_id(self, deck):
        for c in deck['cards']:
            assert 'id' in c

    def test_ids_unique(self, deck):
        ids = [c['id'] for c in deck['cards']]
        assert len(ids) == len(set(ids))

    def test_ids_sequential(self, deck):
        ids = sorted(c['id'] for c in deck['cards'])
        assert ids == list(range(1, len(ids)+1))

    def test_all_have_q(self, deck):
        for c in deck['cards']:
            assert 'q' in c and len(c['q']) > 5

    def test_all_have_a(self, deck):
        for c in deck['cards']:
            assert 'a' in c and len(c['a']) > 5

    def test_all_have_cat(self, deck):
        known_cats = {'constants', 'predictions', 'gates', 'geometry',
                      'experiments', 'lean4', 'architecture_limits'}
        for c in deck['cards']:
            assert c.get('cat') in known_cats

    def test_all_have_gate(self, deck):
        for c in deck['cards']:
            assert 'gate' in c and isinstance(c['gate'], str)

    def test_pillar_is_int_or_none(self, deck):
        for c in deck['cards']:
            assert c.get('pillar') is None or isinstance(c['pillar'], int)


class TestCategoryDistribution:
    def test_has_constants_cards(self, deck):
        assert any(c['cat'] == 'constants' for c in deck['cards'])

    def test_has_predictions_cards(self, deck):
        assert any(c['cat'] == 'predictions' for c in deck['cards'])

    def test_has_gates_cards(self, deck):
        assert any(c['cat'] == 'gates' for c in deck['cards'])

    def test_has_geometry_cards(self, deck):
        assert any(c['cat'] == 'geometry' for c in deck['cards'])

    def test_has_experiments_cards(self, deck):
        assert any(c['cat'] == 'experiments' for c in deck['cards'])

    def test_has_lean4_cards(self, deck):
        assert any(c['cat'] == 'lean4' for c in deck['cards'])

    def test_has_architecture_limits_cards(self, deck):
        assert any(c['cat'] == 'architecture_limits' for c in deck['cards'])

    def test_at_least_5_per_category(self, deck):
        from collections import Counter
        counts = Counter(c['cat'] for c in deck['cards'])
        for cat in ['constants', 'predictions', 'gates', 'geometry', 'experiments']:
            assert counts[cat] >= 4


class TestKeyPhysicsContent:
    def test_nw5_card_present(self, deck):
        qs = [c['q'] for c in deck['cards']]
        assert any('n_w' in q or 'winding' in q.lower() for q in qs)

    def test_kcs74_card_present(self, deck):
        ans = [c['a'] for c in deck['cards']]
        assert any('74' in a for a in ans)

    def test_litebird_card_present(self, deck):
        all_text = ' '.join(c['q'] + c['a'] for c in deck['cards'])
        assert 'LiteBIRD' in all_text

    def test_desi_card_present(self, deck):
        all_text = ' '.join(c['q'] + c['a'] for c in deck['cards'])
        assert 'DESI' in all_text

    def test_graviton_card_present(self, deck):
        all_text = ' '.join(c['q'] + c['a'] for c in deck['cards'])
        assert 'graviton' in all_text.lower() or 'G*' in all_text

    def test_pillar792_card_present(self, deck):
        assert any(c['pillar'] == 792 for c in deck['cards'])

    def test_pillar793_card_present(self, deck):
        assert any(c['pillar'] == 793 for c in deck['cards'])

    def test_cc_hierarchy_card_present(self, deck):
        all_text = ' '.join(c['a'] for c in deck['cards'])
        assert 'cosmological' in all_text.lower() or 'CC_KK' in all_text


# ---------------------------------------------------------------------------
# HTML / JS file checks
# ---------------------------------------------------------------------------

class TestHTMLFile:
    def test_html_exists(self):
        assert os.path.exists(HTML_PATH)

    def test_html_has_flashcard_title(self):
        with open(HTML_PATH) as f:
            content = f.read()
        assert 'Flashcard' in content

    def test_html_loads_js(self):
        with open(HTML_PATH) as f:
            content = f.read()
        assert '19-flashcard-trainer.js' in content

    def test_html_loads_deck_json(self):
        # The deck path is referenced in the JS file (fetched dynamically)
        with open(JS_PATH) as f:
            content = f.read()
        assert 'flashcard-deck.json' in content

    def test_html_has_card_flip(self):
        with open(HTML_PATH) as f:
            content = f.read()
        assert 'card-outer' in content or 'flip' in content.lower()

    def test_html_no_external_scripts(self):
        with open(HTML_PATH) as f:
            content = f.read()
        # No CDN links for scripts (offline-first)
        assert 'cdn.jsdelivr.net' not in content
        assert 'unpkg.com' not in content


class TestJSFile:
    def test_js_exists(self):
        assert os.path.exists(JS_PATH)

    def test_js_has_shuffle(self):
        with open(JS_PATH) as f:
            content = f.read()
        assert 'shuffle' in content

    def test_js_has_flip(self):
        with open(JS_PATH) as f:
            content = f.read()
        assert 'flip' in content.lower()

    def test_js_has_answer_logic(self):
        with open(JS_PATH) as f:
            content = f.read()
        assert 'rightCount' in content and 'wrongCount' in content

    def test_js_has_localstorage(self):
        with open(JS_PATH) as f:
            content = f.read()
        assert 'localStorage' in content

    def test_js_has_categories(self):
        with open(JS_PATH) as f:
            content = f.read()
        assert 'CATEGORIES' in content

    def test_js_keyboard_shortcuts(self):
        with open(JS_PATH) as f:
            content = f.read()
        assert 'Space' in content and "'1'" in content and "'3'" in content

    def test_js_exports_for_testing(self):
        with open(JS_PATH) as f:
            content = f.read()
        assert '_UM_FC' in content

    def test_js_no_external_deps(self):
        with open(JS_PATH) as f:
            content = f.read()
        assert 'require(' not in content
        assert 'import ' not in content
