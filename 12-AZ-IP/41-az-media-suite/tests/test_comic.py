# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_media_suite.comic import (
    UnsupportedComicFormatError,
    create_comic_archive,
    inspect_comic_archive,
    read_comic_page,
)

_PIXEL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
    b"\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_create_and_inspect_comic_archive(tmp_path):
    path = tmp_path / "book.cbz"
    inspection = create_comic_archive(
        path,
        [("page_0001.png", _PIXEL_PNG), ("page_0002.png", _PIXEL_PNG)],
        metadata={"Title": "Test Book", "Writer": "Copilot"},
    )
    assert inspection.page_count == 2
    assert [p.name for p in inspection.pages] == ["page_0001.png", "page_0002.png"]
    assert inspection.metadata["Title"] == "Test Book"
    assert inspection.metadata["Writer"] == "Copilot"


def test_inspect_comic_archive_round_trip(tmp_path):
    path = tmp_path / "book.cbz"
    create_comic_archive(path, [("page_0001.png", _PIXEL_PNG)])
    inspection = inspect_comic_archive(path)
    assert inspection.page_count == 1
    assert inspection.pages[0].size_bytes == len(_PIXEL_PNG)


def test_read_comic_page_returns_bytes(tmp_path):
    path = tmp_path / "book.cbz"
    create_comic_archive(path, [("page_0001.png", _PIXEL_PNG), ("page_0002.png", _PIXEL_PNG)])
    assert read_comic_page(path, 0) == _PIXEL_PNG
    assert read_comic_page(path, 1) == _PIXEL_PNG
    with pytest.raises(IndexError):
        read_comic_page(path, 2)


def test_create_comic_archive_rejects_non_image_page(tmp_path):
    path = tmp_path / "book.cbz"
    with pytest.raises(ValueError):
        create_comic_archive(path, [("notes.txt", b"hello")])


def test_create_comic_archive_requires_pages(tmp_path):
    path = tmp_path / "book.cbz"
    with pytest.raises(ValueError):
        create_comic_archive(path, [])


def test_inspect_comic_archive_rejects_cbr(tmp_path):
    path = tmp_path / "book.cbr"
    path.write_bytes(b"not actually a zip")
    with pytest.raises(UnsupportedComicFormatError):
        inspect_comic_archive(path)


def test_inspect_comic_archive_rejects_non_zip(tmp_path):
    path = tmp_path / "book.cbz"
    path.write_bytes(b"not a zip file at all")
    with pytest.raises(UnsupportedComicFormatError):
        inspect_comic_archive(path)
