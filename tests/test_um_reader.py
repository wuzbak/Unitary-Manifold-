import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "public-site" / "data" / "reader-index.json"
HTML_PATH = REPO_ROOT / "public-site" / "az-apps" / "um-reader.html"
JS_PATH = REPO_ROOT / "public-site" / "js" / "um-reader.js"
PUBLIC_SITE_ROOT = REPO_ROOT / "public-site"

ALLOWED_TOPICS = {
    "Foundation & Core Theory",
    "Particle Physics & Standard Model",
    "Cosmology & Observation",
    "Philosophy & Consciousness",
    "AI, Ethics & Collaboration",
    "Applied Domains",
    "Mathematics & Formal Methods",
    "Open Science & Community",
    "Books",
}
REQUIRED_FIELDS = {"id", "title", "type", "topic", "path", "preview"}
EXPECTED_BOOK_IDS = {
    "book-falsification-decade-2025-2035",
    "book-two-time-physics-and-the-unitary-manifold-parent",
}


@pytest.fixture(scope="module")
def reader_entries():
    assert INDEX_PATH.exists(), "reader-index.json should exist"
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


@pytest.fixture(scope="module")
def html_text():
    assert HTML_PATH.exists(), "um-reader.html should exist"
    return HTML_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def js_text():
    assert JS_PATH.exists(), "um-reader.js should exist"
    return JS_PATH.read_text(encoding="utf-8")


def resolve_from_html(entry_path: str) -> Path:
    return (HTML_PATH.parent / entry_path).resolve()


def test_reader_index_file_exists():
    assert INDEX_PATH.exists()


def test_reader_index_is_valid_json(reader_entries):
    assert isinstance(reader_entries, list)


def test_reader_index_has_entries(reader_entries):
    assert len(reader_entries) >= 302


def test_reader_index_contains_both_books(reader_entries):
    ids = {entry["id"] for entry in reader_entries}
    assert EXPECTED_BOOK_IDS.issubset(ids)


def test_reader_index_contains_at_least_280_posts(reader_entries):
    posts = [entry for entry in reader_entries if entry["type"] == "post"]
    assert len(posts) >= 280


def test_reader_index_contains_exactly_two_books(reader_entries):
    books = [entry for entry in reader_entries if entry["type"] == "book"]
    assert len(books) == 2


def test_required_fields_present(reader_entries):
    for entry in reader_entries:
        assert REQUIRED_FIELDS.issubset(entry.keys())


@pytest.mark.parametrize("field_name", ["id", "title", "type", "topic", "path", "preview", "series", "number", "word_count"])
def test_each_required_value_is_nonempty(reader_entries, field_name):
    for entry in reader_entries:
        assert field_name in entry
        assert entry[field_name] not in (None, "")


def test_all_topics_allowed(reader_entries):
    for entry in reader_entries:
        assert entry["topic"] in ALLOWED_TOPICS


def test_book_entries_use_books_topic(reader_entries):
    for entry in reader_entries:
        if entry["type"] == "book":
            assert entry["topic"] == "Books"


def test_all_paths_reference_existing_files(reader_entries):
    missing = [entry["path"] for entry in reader_entries if not resolve_from_html(entry["path"]).exists()]
    assert not missing


def test_all_paths_point_to_markdown(reader_entries):
    for entry in reader_entries:
        assert entry["path"].endswith(".md")


def test_all_post_ids_start_with_post(reader_entries):
    for entry in reader_entries:
        if entry["type"] == "post":
            assert entry["id"].startswith("post") or entry["id"].startswith("epilog") or entry["id"].startswith("v")


def test_book_ids_start_with_book(reader_entries):
    for entry in reader_entries:
        if entry["type"] == "book":
            assert entry["id"].startswith("book-")


def test_previews_are_reasonable_length(reader_entries):
    for entry in reader_entries:
        assert 0 < len(entry["preview"]) <= 200


def test_word_counts_are_positive(reader_entries):
    for entry in reader_entries:
        assert isinstance(entry["word_count"], int)
        assert entry["word_count"] > 0


def test_series_include_books_and_general(reader_entries):
    series_values = {entry["series"] for entry in reader_entries}
    assert "book" in series_values
    assert "general" in series_values


def test_series_include_all_seasons(reader_entries):
    series_values = {entry["series"] for entry in reader_entries}
    assert {"s01", "s02", "s03"}.issubset(series_values)


def test_html_file_exists():
    assert HTML_PATH.exists()


@pytest.mark.parametrize(
    "snippet",
    [
        'id="readerSearch"',
        'id="readerTopicFilter"',
        'id="readerSeriesFilter"',
        'id="readerSort"',
        'id="readerList"',
        'id="readerContent"',
        'id="ttsPlay"',
        'id="ttsPause"',
        'id="ttsStop"',
        'id="ttsRate"',
        'id="ttsVoice"',
        'UM Reader',
        'marked.min.js',
        'katex.min.js',
        'Open in new tab',
    ],
)
def test_html_contains_required_elements(html_text, snippet):
    assert snippet in html_text


def test_html_contains_footer_text(html_text):
    assert "AxiomZero Technologies &amp; Consulting, SPC — UBI 606 239 876" in html_text


def test_js_file_exists():
    assert JS_PATH.exists()


@pytest.mark.parametrize(
    "class_name",
    ["class ReaderIndex", "class MarkdownViewer", "class TTSController", "class ReaderApp"],
)
def test_js_contains_required_classes(js_text, class_name):
    assert class_name in js_text


@pytest.mark.parametrize(
    "snippet",
    [
        "speechSynthesis",
        "SpeechSynthesisUtterance",
        "fetch(this.indexUrl",
        "fetch(entry.path",
        "ArrowLeft",
        "ArrowRight",
        "marked.parse",
        "katex.renderToString",
    ],
)
def test_js_contains_required_behavior(js_text, snippet):
    assert snippet in js_text


def test_html_module_reference_exists(html_text):
    assert '../js/um-reader.js' in html_text


def test_generated_paths_resolve_from_public_site(reader_entries):
    for entry in reader_entries:
        assert resolve_from_html(entry["path"]).is_file()


def test_books_are_present_in_renderable_files(reader_entries):
    paths = {resolve_from_html(entry["path"]).name for entry in reader_entries if entry["type"] == "book"}
    assert paths == {"book-falsification-decade-2025-2035.md", "book-two-time-physics-and-the-unitary-manifold-parent.md"}
