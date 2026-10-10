# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Feature 1 + 2: live product-registry awareness and a capability router.

Reads the canonical `12-AZ-IP/README.md` product table directly (rather
than duplicating it into a static, driftable copy), so PsiCat's awareness
of its own sibling products never goes stale as new products are added.

A holistic audit of `merlin_tools.py` found zero of PsiCat's ~200 tool
functions referenced any of the monorepo's other products -- this module
is the fix.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ._repo import repo_root

_README_RELATIVE = Path("12-AZ-IP") / "README.md"

#: Matches one canonical product table row, e.g.
#: | 01 | Axiom OS Core Suite | 1.0.0 | TRL-5 | http://localhost:8000 | 162 | ... | [01-axiom-os/](01-axiom-os/) |
_ROW_PATTERN = re.compile(
    r"^\|\s*(\d{1,3})\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*\[.*?\]\((.+?)\)\s*\|\s*$"
)


@dataclass(frozen=True)
class ProductRecord:
    """One row of the canonical `12-AZ-IP/README.md` product registry."""

    number: int
    name: str
    version: str
    trl: str
    port: str
    tests: str
    description: str
    folder: str

    def as_dict(self) -> dict:
        return {
            "number": self.number,
            "name": self.name,
            "version": self.version,
            "trl": self.trl,
            "port": self.port,
            "tests": self.tests,
            "description": self.description,
            "folder": self.folder,
        }


def _readme_path() -> Path:
    return repo_root() / _README_RELATIVE


def load_product_registry(readme_path: Optional[Path] = None) -> List[ProductRecord]:
    """Parse the canonical product table out of `12-AZ-IP/README.md`.

    This is a read-only, text-only parse of a Markdown table -- it does
    not execute or import any product code, and so carries no more risk
    than reading any other repository document.
    """
    path = readme_path or _readme_path()
    text = path.read_text(encoding="utf-8")
    records: List[ProductRecord] = []
    for line in text.splitlines():
        match = _ROW_PATTERN.match(line.strip())
        if not match:
            continue
        number_str, name, version, trl, port, tests, description, folder = match.groups()
        records.append(
            ProductRecord(
                number=int(number_str),
                name=name,
                version=version,
                trl=trl,
                port=port,
                tests=tests,
                description=description,
                folder=folder,
            )
        )
    records.sort(key=lambda record: record.number)
    return records


def get_product(identifier, readme_path: Optional[Path] = None) -> Optional[ProductRecord]:
    """Look up one product by number (int/str) or case-insensitive name/folder substring."""
    records = load_product_registry(readme_path)
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.strip().isdigit()):
        number = int(identifier)
        for record in records:
            if record.number == number:
                return record
        return None
    needle = str(identifier).strip().lower()
    for record in records:
        haystack = f"{record.name} {record.folder}".lower()
        if needle in haystack:
            return record
    words = [word for word in needle.split() if word]
    if words:
        for record in records:
            haystack = f"{record.name} {record.folder}".lower()
            if all(word in haystack for word in words):
                return record
    return None


def _haystack(record: ProductRecord) -> str:
    return " ".join([record.name, record.description, record.folder, record.trl]).lower()


def route_capability_request(
    intent: str,
    limit: int = 5,
    readme_path: Optional[Path] = None,
) -> List[dict]:
    """Rank sibling products against a free-text intent string.

    Uses the same term-overlap scoring idea as `interrogator.search_kb`
    (name-match terms score higher than description-only matches), kept
    intentionally simple and fully explainable -- every suggestion can be
    traced back to which terms matched which field.
    """
    terms = [term for term in re.split(r"\W+", str(intent).lower()) if term]
    records = load_product_registry(readme_path)
    if not terms:
        return [
            {"product": record.as_dict(), "score": 0, "matched_terms": []}
            for record in records[: max(limit, 0)]
        ]
    ranked = []
    for record in records:
        name_lower = record.name.lower()
        haystack = _haystack(record)
        matched_terms = [term for term in terms if term in haystack]
        if not matched_terms:
            continue
        score = sum(3 if term in name_lower else 1 for term in matched_terms)
        ranked.append((score, record, matched_terms))
    ranked.sort(key=lambda item: (-item[0], item[1].number))
    return [
        {"product": record.as_dict(), "score": score, "matched_terms": matched_terms}
        for score, record, matched_terms in ranked[: max(limit, 0)]
    ]
