# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
PSICAT_ROOT = REPO_ROOT / "7-OUTREACH" / "A Z PsiCat Literature"
BOOKS_DIR = PSICAT_ROOT / "Books"
ARTICLES_DIR = PSICAT_ROOT / "Articles"
README_PATH = PSICAT_ROOT / "README.md"
ARCHIVE_DIR = PSICAT_ROOT / "Archive" / "2026-11-05-books-53-58"
EXPECTED_BOOK_COUNT = 50
EXPECTED_ARTICLE_COUNT = 357
EXPECTED_REWRITE_ARTICLE_COUNT = 355
EXPECTED_ORIGINAL_WORKS = {"51", "52", "53", "54", "55", "56", "57", "58", "59"}
EXPECTED_ORIGINAL_ARTICLES = {"353", "354"}

ORIGINAL_WORK_MARKERS = (
    "PsiCat Original Work v1 · Series/Season One",
    "AxiomZero Technologies & Consulting, SPC commissioned work: Investigated and written by PsiCat Ai.",
    "*Original-work provenance:",
)

REQUIRED_MARKERS = (
    "Merlin/PsiCat Rewrite v1 · Series/Season One",
    "AxiomZero Technologies & Consulting, SPC commissioned work: Edited and written by PsiCat Ai.",
    "### Gate Certification (v1)",
)

SOURCE_PATTERN = re.compile(r"^\*Grounded rewrite source:\s+`([^`]+)`\*$", re.MULTILINE)
BOOK_NUMBER_PATTERN = re.compile(r"^book-(\d+)-")
ARTICLE_NUMBER_PATTERN = re.compile(r"^article-(\d+)-")
ORIGINAL_COUNT_PATTERN = re.compile(r"Original works \(not rewrites\):\s+\*\*(\d+)\*\*")
COVERAGE_PATTERN = re.compile(
    r"Coverage so far:\s+\*\*(\d+)\s*/\s*(\d+)\s+(?:rewrite )?books\*\*,\s+\*\*(\d+)\s*/\s*(\d+)\s+articles\*\*\."
)


def _markdown_files(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.md"))


def _is_original_work(path: Path) -> bool:
    return ORIGINAL_WORK_MARKERS[0] in path.read_text(encoding="utf-8")


def _rewrite_books() -> list[Path]:
    return [path for path in _markdown_files(BOOKS_DIR) if not _is_original_work(path)]


def _original_book_files() -> list[Path]:
    return [path for path in _markdown_files(BOOKS_DIR) if _is_original_work(path)]


def _rewrite_articles() -> list[Path]:
    return [path for path in _markdown_files(ARTICLES_DIR) if not _is_original_work(path)]


def _original_article_files() -> list[Path]:
    return [path for path in _markdown_files(ARTICLES_DIR) if _is_original_work(path)]


def _assert_piece_contract(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# "), f"{path.name} must start with a markdown title"
    for marker in REQUIRED_MARKERS:
        assert marker in text, f"{path.name} is missing marker: {marker}"

    match = SOURCE_PATTERN.search(text)
    assert match, f"{path.name} is missing an exact Grounded rewrite source line"
    source_path = match.group(1)
    assert source_path.startswith("/7-OUTREACH/substack/"), (
        f"{path.name} must point to an exact source under /7-OUTREACH/substack/"
    )
    resolved = REPO_ROOT / source_path.lstrip("/")
    assert resolved.exists(), f"{path.name} references missing source file: {source_path}"


def _readme_coverage_totals() -> tuple[int, int]:
    readme = README_PATH.read_text(encoding="utf-8")
    match = COVERAGE_PATTERN.search(readme)
    assert match, "README coverage summary is missing"
    covered_books, total_books, covered_articles, total_articles = map(int, match.groups())
    assert covered_books == total_books
    assert covered_articles == total_articles
    return total_books, total_articles


def test_all_psicat_books_follow_curated_contract() -> None:
    files = _rewrite_books()
    assert len(files) == EXPECTED_BOOK_COUNT
    for path in files:
        _assert_piece_contract(path)


def test_all_psicat_articles_follow_curated_contract() -> None:
    files = _rewrite_articles()
    assert len(files) == EXPECTED_REWRITE_ARTICLE_COUNT
    for path in files:
        _assert_piece_contract(path)


def _check_original_lane(
    files: list[Path], number_pattern: re.Pattern[str], label: str
) -> set[str]:
    works = set()
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("# "), f"{path.name} must start with a markdown title"
        for marker in ORIGINAL_WORK_MARKERS:
            assert marker in text, f"{path.name} is missing original-work marker: {marker}"
        assert not SOURCE_PATTERN.search(text), (
            f"{path.name} is an original work and must not claim a grounded rewrite source"
        )
        match = number_pattern.match(path.name)
        assert match, f"{path.name} must follow the {label}-NN- naming scheme"
        works.add(match.group(1))
    return works


def test_psicat_original_works_follow_original_contract() -> None:
    book_files = _original_book_files()
    article_files = _original_article_files()

    book_works = _check_original_lane(book_files, BOOK_NUMBER_PATTERN, "book")
    article_works = _check_original_lane(article_files, ARTICLE_NUMBER_PATTERN, "article")

    assert book_works == EXPECTED_ORIGINAL_WORKS
    assert article_works == EXPECTED_ORIGINAL_ARTICLES

    readme = README_PATH.read_text(encoding="utf-8")
    count = ORIGINAL_COUNT_PATTERN.search(readme)
    assert count, "README original-works count is missing"
    assert int(count.group(1)) == len(EXPECTED_ORIGINAL_WORKS) + len(EXPECTED_ORIGINAL_ARTICLES)
    for number in EXPECTED_ORIGINAL_WORKS:
        primaries = [p for p in book_files if p.name.startswith(f"book-{number}-") and "-part-" not in p.name
                     and not p.name.endswith("-FULL.md")]
        assert len(primaries) == 1, f"Original work {number} must have exactly one primary file"
        assert f"`{primaries[0].name}`" in readme, f"README must list {primaries[0].name}"
    for number in EXPECTED_ORIGINAL_ARTICLES:
        primaries = [p for p in article_files if p.name.startswith(f"article-{number}-")]
        assert len(primaries) == 1, f"Original article {number} must have exactly one primary file"
        assert f"`{primaries[0].name}`" in readme, f"README must list {primaries[0].name}"


def test_psicat_readme_coverage_matches_actual_corpus() -> None:
    current_books = len(_rewrite_books())
    current_articles = len(_markdown_files(ARTICLES_DIR))

    expected_books, expected_articles = _readme_coverage_totals()
    assert expected_books == current_books
    assert expected_articles == current_articles
    assert expected_books == EXPECTED_BOOK_COUNT
    assert expected_articles == EXPECTED_ARTICLE_COUNT


def test_collection_has_exactly_59_individual_complete_books() -> None:
    books = _markdown_files(BOOKS_DIR)
    numbers = [int(BOOK_NUMBER_PATTERN.match(path.name).group(1)) for path in books]
    assert sorted(numbers) == list(range(1, 60))
    assert not any("-part-" in path.name or path.name.endswith("-FULL.md") for path in books)


def test_preassembly_sources_are_preserved_byte_for_byte() -> None:
    manifest = json.loads((ARCHIVE_DIR / "preservation_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 58
    names = [entry["archive_file"] for entry in manifest["files"]]
    assert len(names) == len(set(names))
    assert set(names) == {path.name for path in _markdown_files(ARCHIVE_DIR)}
    for entry in manifest["files"]:
        data = (ARCHIVE_DIR / entry["archive_file"]).read_bytes()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
        assert entry["original_path"] == str(
            (BOOKS_DIR / entry["archive_file"]).relative_to(REPO_ROOT)
        )


# Only these dated factual errata may differ from the immutable archived parts.
ASSEMBLY_ERRATA = {
    57: (
        "The local browser-storage model and explicit export mean data does not leave the device unless the player chooses to export it or deliberately points the coach at a local Product 20 endpoint.",
        "Progress is local by default, but an explicitly confirmed nonlocal coaching request can send the question, current briefing and gameplay-derived training packet to the selected endpoint; export is not the only off-device path.",
    ),
    58: (
        r"The six-dimensional track adds a \(T^2/\mathbb{Z}_3\) compact space alongside the \(S^1/\mathbb{Z}_2\) direction.",
        r"The lane named “six-dimensional” describes a \(T^2/\mathbb{Z}_3\) compact space alongside the \(S^1/\mathbb{Z}_2\) direction, but four extended dimensions plus that circle and two-torus total seven dimensions, not six. This is an unresolved inconsistency in the source description, not a dimensionally consistent six-dimensional construction established here.",
    ),
}


def _assembly_text(text: str, *, book_number: int | None = None) -> str:
    """Ignore navigation markup and heading nesting, not manuscript content."""
    text = re.sub(
        r"^\*Part file of Book [^\n]*(?:\n[^\n]+)*\n", "", text, flags=re.MULTILINE
    )
    text = text.replace(
        "carried in five companion catalog files "
        "(`book-56-part-08a-*.md` through `book-56-part-08e-*.md`), then name",
        "assembled in the five catalog sections below, then name",
    ).replace(
        "Five companion files carry Chapters 40 through 44",
        "The five catalog sections below carry Chapters 40 through 44",
    )
    text = re.sub(r"^#{1,6} ", "", text, flags=re.MULTILINE)
    if book_number in ASSEMBLY_ERRATA:
        original, correction = ASSEMBLY_ERRATA[book_number]
        text = text.replace(original, correction)
    text = re.sub(
        r"\[([^\]]+)\]\((?:book-\d+-part-[^()\s]+\.md|#book-\d+-part-[^()\s]+)\)",
        r"\1", text,
    )
    return " ".join(text.replace("`", "").split())


@pytest.mark.parametrize(
    ("number", "section_count"),
    [(53, 10), (54, 3), (55, 11), (56, 15), (57, 6), (58, 6)],
)
def test_individual_assemblies_include_every_source_in_order(
    number: int, section_count: int
) -> None:
    primary, = BOOKS_DIR.glob(f"book-{number}-*.md")
    manuscript = primary.read_text(encoding="utf-8")
    parts = sorted(ARCHIVE_DIR.glob(f"book-{number}-part-*.md"))
    assert len(parts) == section_count
    assert re.findall(r'<a id="([^"]+)"></a>', manuscript) == [p.stem for p in parts]
    for index, part in enumerate(parts):
        anchor = f'<a id="{part.stem}"></a>'
        assert manuscript.count(anchor) == 1
        assert f"](#{part.stem})" in manuscript, f"{part.name} missing from internal contents"
        section = manuscript.split(anchor, 1)[1]
        if index + 1 < len(parts):
            section = section.split(f'<a id="{parts[index + 1].stem}"></a>', 1)[0]
            section = section.rsplit("---", 1)[0]
        assert _assembly_text(section) == _assembly_text(
            part.read_text(encoding="utf-8"), book_number=number,
        )
    assert not re.search(r"\]\(book-\d+-part-", manuscript)
    assert len(re.findall(r"^# ", manuscript, re.MULTILINE)) == 1


@pytest.mark.parametrize("number", [57, 58])
def test_assembly_factual_errata_are_explicit_without_rewriting_archives(number):
    primary, = BOOKS_DIR.glob(f"book-{number}-*.md")
    manuscript = primary.read_text(encoding="utf-8")
    original, correction = ASSEMBLY_ERRATA[number]
    assert "**Editorial errata (2026-11-05):**" in manuscript
    assert original not in manuscript
    assert correction in manuscript
    assert sum(original in p.read_text(encoding="utf-8")
               for p in ARCHIVE_DIR.glob(f"book-{number}-part-*.md")) == 1


def test_assembly_comparison_preserves_external_citation_destinations():
    original = "[primary source](https://example.org/original)"
    mutated = "[primary source](https://example.org/replaced)"
    assert _assembly_text(original) != _assembly_text(mutated)
    assert _assembly_text(original) != _assembly_text("primary source")
    assert _assembly_text("[Part](book-54-part-01-the-cloud-record.md)") == _assembly_text(
        "[Part](#book-54-part-01-the-cloud-record)"
    )


@pytest.mark.parametrize(("number", "chapters"), [(53, 46), (55, 27), (56, 52)])
def test_assembled_chapter_numbering_is_complete_and_sequential(
    number: int, chapters: int
) -> None:
    primary, = BOOKS_DIR.glob(f"book-{number}-*.md")
    numbers = re.findall(r"^### Chapter (\d+)\b", primary.read_text(encoding="utf-8"), re.MULTILINE)
    assert list(map(int, numbers)) == list(range(1, chapters + 1))


def test_commissioned_books_have_complete_book_length_manuscripts() -> None:
    for number in ("57", "58"):
        primary, = BOOKS_DIR.glob(f"book-{number}-*.md")
        index = primary.read_text(encoding="utf-8")
        chapter_ids = re.findall(r"^#{2,3} ([A-F]\d+) ", index, re.MULTILINE)
        assert len(chapter_ids) >= 24, f"Book {number} is missing its detailed chapters"
        assert len(chapter_ids) == len(set(chapter_ids)), (
            f"Book {number} repeats chapter identifiers"
        )
        words = len(index.split())
        assert 30_000 <= words <= 50_000, (
            f"Book {number} has {words:,} words; commission requires 30,000–50,000"
        )
        assert "GitHub Copilot" in index
        assert "d9efc894947c8b45e584e74ed59ff809d407fb52" in index
        assert "095ae666b4ad3052c038d6a082bf535df07aa0be" in index


def test_applied_sciences_book_traces_all_commissioned_products() -> None:
    manuscript = (
        BOOKS_DIR / "book-57-axiomzero-applied-sciences-and-intellectual-properties.md"
    ).read_text(
        encoding="utf-8"
    )
    for number in range(1, 46):
        products = list((REPO_ROOT / "12-AZ-IP").glob(f"{number:02d}-*"))
        assert len(products) == 1, f"Canonical Product {number:02d} is ambiguous or missing"
        assert f"12-AZ-IP/{products[0].name}" in manuscript, (
            f"Book 57 must cite canonical Product {number:02d}: {products[0].name}"
        )
