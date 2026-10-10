# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Feature 6: citation / evidence (`path:line`) verification.

This repository's own memory and documentation culture cites evidence as
`path/to/file.py:123` or `path/to/file.py:96-123,257-265` (see e.g. the
repository memories format used throughout this task). This module lets
PsiCat check whether a claimed citation is real and resolvable -- in
service of the repository's stated epistemic-honesty standard, not as a
new claim-scoring system.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from ._repo import repo_root

#: One citation token: a path ending in a file extension, a colon, then
#: one or more comma-separated line numbers or line ranges.
_CITATION_PATTERN = re.compile(r"([A-Za-z0-9_\-./ ]+?\.[A-Za-z0-9_]+):([0-9]+(?:-[0-9]+)?(?:,[0-9]+(?:-[0-9]+)?)*)")


@dataclass(frozen=True)
class CitationVerification:
    citation: str
    path: str
    file_exists: bool
    line_ranges: Tuple[Tuple[int, int], ...]
    file_line_count: Optional[int]
    invalid_ranges: Tuple[Tuple[int, int], ...] = field(default_factory=tuple)
    verified: bool = False
    reason: str = ""

    def as_dict(self) -> dict:
        return {
            "citation": self.citation,
            "path": self.path,
            "file_exists": self.file_exists,
            "line_ranges": [list(pair) for pair in self.line_ranges],
            "file_line_count": self.file_line_count,
            "invalid_ranges": [list(pair) for pair in self.invalid_ranges],
            "verified": self.verified,
            "reason": self.reason,
        }


def parse_citation_string(text: str) -> List[Tuple[str, str]]:
    """Extract every ``path:spec`` token out of a free-text citation string."""
    return [(match.group(1).strip(), match.group(2)) for match in _CITATION_PATTERN.finditer(text)]


def _parse_ranges(spec: str) -> Tuple[Tuple[int, int], ...]:
    ranges = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if "-" in chunk:
            start_str, end_str = chunk.split("-", 1)
            start, end = int(start_str), int(end_str)
        else:
            start = end = int(chunk)
        ranges.append((min(start, end), max(start, end)))
    return tuple(ranges)


def _verify_one(path_text: str, spec: str) -> CitationVerification:
    citation = f"{path_text}:{spec}"
    root = repo_root().resolve()
    candidate = (root / path_text).resolve()

    try:
        candidate.relative_to(root)
        escapes_root = False
    except ValueError:
        escapes_root = True

    if escapes_root:
        return CitationVerification(
            citation=citation, path=path_text, file_exists=False, line_ranges=(),
            file_line_count=None, reason="path escapes the repository root",
        )

    if not candidate.is_file():
        return CitationVerification(
            citation=citation, path=path_text, file_exists=False, line_ranges=(),
            file_line_count=None, reason="file does not exist in the repository",
        )

    line_ranges = _parse_ranges(spec)
    line_count = len(candidate.read_text(encoding="utf-8", errors="replace").splitlines())
    invalid_ranges = tuple(
        (start, end) for start, end in line_ranges if start < 1 or end > line_count
    )
    verified = not invalid_ranges
    reason = "" if verified else f"line range(s) outside file's {line_count} lines"
    return CitationVerification(
        citation=citation,
        path=path_text,
        file_exists=True,
        line_ranges=line_ranges,
        file_line_count=line_count,
        invalid_ranges=invalid_ranges,
        verified=verified,
        reason=reason,
    )


def verify_citation_string(text: str) -> List[CitationVerification]:
    """Verify every ``path:line`` citation found inside a free-text string."""
    tokens = parse_citation_string(text)
    if not tokens:
        return []
    return [_verify_one(path_text, spec) for path_text, spec in tokens]
