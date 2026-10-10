# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Comic-archive (CBZ) viewer: parse, list, read, and create.

Supports the de-facto "CBZ" convention (a zip archive of ordered page
images, optionally with a `ComicInfo.xml` ComicRack-style metadata file).
CBR (rar) archives are detected but not extracted — rar extraction needs a
non-stdlib unrar binary this repository does not bundle or depend on; a
clear, honest error is raised instead of silently failing.
"""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")
_METADATA_NAME = "ComicInfo.xml"


class UnsupportedComicFormatError(ValueError):
    """Raised for archive formats this module cannot safely parse."""


@dataclass(frozen=True)
class ComicPage:
    index: int
    name: str
    size_bytes: int


@dataclass(frozen=True)
class ComicInspection:
    path: str
    page_count: int
    pages: list[ComicPage]
    metadata: dict[str, Any] = field(default_factory=dict)


def _is_image(name: str) -> bool:
    return name.lower().endswith(_IMAGE_SUFFIXES)


def _parse_comic_info(data: bytes) -> dict[str, Any]:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return {}
    return {child.tag: (child.text or "").strip() for child in root}


def inspect_comic_archive(path: str | Path) -> ComicInspection:
    """Return page listing and optional ComicInfo.xml metadata for a CBZ file."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".cbr" or suffix == ".rar":
        raise UnsupportedComicFormatError(
            "CBR/RAR comic archives are not extracted by this module; "
            "re-package as CBZ (zip) to view or inspect it here."
        )
    if not zipfile.is_zipfile(path):
        raise UnsupportedComicFormatError(f"{path} is not a zip-based (CBZ) comic archive")

    with zipfile.ZipFile(path) as archive:
        names = sorted(n for n in archive.namelist() if _is_image(n))
        pages = [
            ComicPage(index=i, name=name, size_bytes=archive.getinfo(name).file_size)
            for i, name in enumerate(names)
        ]
        metadata: dict[str, Any] = {}
        if _METADATA_NAME in archive.namelist():
            metadata = _parse_comic_info(archive.read(_METADATA_NAME))

    return ComicInspection(path=str(path), page_count=len(pages), pages=pages, metadata=metadata)


def read_comic_page(path: str | Path, index: int) -> bytes:
    """Return the raw bytes of one page image, by position in sorted page order."""
    path = Path(path)
    with zipfile.ZipFile(path) as archive:
        names = sorted(n for n in archive.namelist() if _is_image(n))
        if index < 0 or index >= len(names):
            raise IndexError(f"page index {index} out of range for {len(names)} pages")
        return archive.read(names[index])


def create_comic_archive(
    output_path: str | Path,
    pages: list[tuple[str, bytes]],
    metadata: dict[str, Any] | None = None,
) -> ComicInspection:
    """Create a CBZ (zip) comic archive from ordered (name, bytes) page tuples.

    Pages are written using zero-padded names (`page_0001.jpg`-style ordinal
    prefixes retained from the caller's `name`) so archive-native sort order
    matches reading order in standard comic-viewer tools.
    """
    output_path = Path(output_path)
    if not pages:
        raise ValueError("at least one page is required to create a comic archive")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for i, (name, data) in enumerate(pages):
            if not _is_image(name):
                raise ValueError(f"page {i} name {name!r} does not look like an image file")
            archive.writestr(name, data)
        if metadata:
            root = ET.Element("ComicInfo")
            for key, value in metadata.items():
                child = ET.SubElement(root, str(key))
                child.text = str(value)
            buf = io.BytesIO()
            ET.ElementTree(root).write(buf, encoding="utf-8", xml_declaration=True)
            archive.writestr(_METADATA_NAME, buf.getvalue())

    return inspect_comic_archive(output_path)
