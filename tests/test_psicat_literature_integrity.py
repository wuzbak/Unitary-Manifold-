# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PSICAT_ROOT = REPO_ROOT / "7-OUTREACH" / "A Z PsiCat Literature"
BOOKS_DIR = PSICAT_ROOT / "Books"
ARTICLES_DIR = PSICAT_ROOT / "Articles"
README_PATH = PSICAT_ROOT / "README.md"
EXPECTED_BOOK_COUNT = 50
EXPECTED_ARTICLE_COUNT = 352
EXPECTED_ORIGINAL_WORKS = {"51", "52", "53", "54", "55"}

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
ORIGINAL_COUNT_PATTERN = re.compile(r"Original works \(not rewrites\):\s+\*\*(\d+)\*\*")
COVERAGE_PATTERN = re.compile(
    r"Coverage so far:\s+\*\*(\d+)\s*/\s*(\d+)\s+books\*\*,\s+\*\*(\d+)\s*/\s*(\d+)\s+articles\*\*\."
)


def _markdown_files(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.md"))


def _is_original_work(path: Path) -> bool:
    return ORIGINAL_WORK_MARKERS[0] in path.read_text(encoding="utf-8")


def _rewrite_books() -> list[Path]:
    return [path for path in _markdown_files(BOOKS_DIR) if not _is_original_work(path)]


def _original_book_files() -> list[Path]:
    return [path for path in _markdown_files(BOOKS_DIR) if _is_original_work(path)]


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
    files = _markdown_files(ARTICLES_DIR)
    assert len(files) == EXPECTED_ARTICLE_COUNT
    for path in files:
        _assert_piece_contract(path)


def test_psicat_original_works_follow_original_contract() -> None:
    files = _original_book_files()
    works = set()
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("# "), f"{path.name} must start with a markdown title"
        for marker in ORIGINAL_WORK_MARKERS:
            assert marker in text, f"{path.name} is missing original-work marker: {marker}"
        assert not SOURCE_PATTERN.search(text), (
            f"{path.name} is an original work and must not claim a grounded rewrite source"
        )
        match = BOOK_NUMBER_PATTERN.match(path.name)
        assert match, f"{path.name} must follow the book-NN- naming scheme"
        works.add(match.group(1))
    assert works == EXPECTED_ORIGINAL_WORKS

    readme = README_PATH.read_text(encoding="utf-8")
    count = ORIGINAL_COUNT_PATTERN.search(readme)
    assert count, "README original-works count is missing"
    assert int(count.group(1)) == len(EXPECTED_ORIGINAL_WORKS)
    for number in EXPECTED_ORIGINAL_WORKS:
        primaries = [p for p in files if p.name.startswith(f"book-{number}-") and "-part-" not in p.name
                     and not p.name.endswith("-FULL.md")]
        assert len(primaries) == 1, f"Original work {number} must have exactly one primary file"
        assert f"`{primaries[0].name}`" in readme, f"README must list {primaries[0].name}"


def test_psicat_readme_coverage_matches_actual_corpus() -> None:
    current_books = len(_rewrite_books())
    current_articles = len(_markdown_files(ARTICLES_DIR))

    expected_books, expected_articles = _readme_coverage_totals()
    assert expected_books == current_books
    assert expected_articles == current_articles
    assert expected_books == EXPECTED_BOOK_COUNT
    assert expected_articles == EXPECTED_ARTICLE_COUNT
