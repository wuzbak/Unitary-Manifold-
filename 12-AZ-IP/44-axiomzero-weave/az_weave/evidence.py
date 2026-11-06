# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Bounded, citation-producing access to reviewed repository source files."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path, PurePosixPath

MAX_FILE_BYTES = 512 * 1024
MAX_QUERY_CHARS = 2048
MAX_LIMIT = 50
_TOKEN = re.compile(r"[A-Za-z0-9]+")
_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_SKIP_PARTS = {".git", "private", "archive", "archives", "supplied"}
_STOPWORDS = set("a an and are as at be by can do does for from how i in is it of on or that the this to was what when where which who with".split())
_CORE_FILES = {
    "src/core/metric.py",
    "src/core/evolution.py",
    "src/holography/boundary.py",
    "src/multiverse/fixed_point.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/model.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/positional.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/attention.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/text_workflow.py",
    "12-AZ-IP/16-oracle/oracle/engine/synthesis.py",
    "12-AZ-IP/16-oracle/oracle/engine/pentad.py",
    "12-AZ-IP/16-oracle/oracle/engine/epistemic_tagger.py",
    "12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_tools.py",
    "12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_rag.py",
}
_CURRENT_TRUTH_SECTIONS = (
    (2, "Synthesis repair (2026-10-05)"),
    (3, "Mathematical findings and assumptions"),
    (3, "Sprint CX action-derived flow steward promotion"),
    (3, "Lane 1 action-derived flow replacement (Sprint CW; promoted within perimeter in Sprint CX)"),
)
_CURRENT_TRUTH_SINCE = "2026-10-05"


def _current_lines(relative: str, text: str) -> set[int]:
    """Apply the packaged selection policy; corpus files are data, never code.

    Mirror bot.rag_index.current_document_lines without importing the bot from
    either the inspected corpus or a source checkout (standalone wheels work).
    """
    if relative != "docs/TRUTH_LAYER.md":
        return set(range(1, len(text.splitlines()) + 1))
    selected: set[int] = set()
    active_level = None
    historical_level = None
    fence = None
    for number, line in enumerate(text.splitlines(keepends=True), start=1):
        fence_match = re.match(r"^[ \t]*(`{3,}|~{3,})", line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
        elif fence is None:
            heading_match = re.match(r"^(#{1,6})[ \t]+(.+?)\s*$", line)
            if heading_match:
                level = len(heading_match.group(1))
                heading = heading_match.group(2)
                if active_level is not None and level <= active_level:
                    active_level = None
                if historical_level is not None and level <= historical_level:
                    historical_level = None
                historical = re.search(
                    r"\b(historical|archive|archived|superseded)\b", heading, re.IGNORECASE,
                )
                if historical and historical_level is None:
                    historical_level = level
                date = re.search(r"\b\d{4}-\d{2}-\d{2}\b", heading)
                current_correction = (
                    level <= 3
                    and date is not None
                    and date.group() >= _CURRENT_TRUTH_SINCE
                    and historical_level is None
                    and not re.search(r"\b(sprint|lane)\b", heading, re.IGNORECASE)
                )
                if (
                    active_level is None
                    and historical_level is None
                    and ((level, heading) in _CURRENT_TRUTH_SECTIONS or current_correction)
                ):
                    active_level = level
        if active_level is not None and historical_level is None:
            selected.add(number)
    return selected


def _tokens(text: str) -> list[str]:
    result: list[str] = []
    for raw in _TOKEN.findall(text):
        pieces = _CAMEL.sub(" ", raw)
        result.extend(part.casefold() for part in pieces.split() if part)
    return result


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class SourceIndex:
    """Search a narrow set of current repository files and cite exact lines.

    The default corpus is derived from Git's tracked-file list and bounded to
    canonical Markdown documentation, the current RAG knowledge corpus, and
    the small set of implementation files selected by that corpus. Callers
    can provide a reviewed path allowlist for a different corpus. Files are
    reread for every search; no indexed bytes are treated as freshness proof.
    """

    def __init__(self, repo_root: Path, allowed_paths: list[str] | None = None):
        self.repo_root = Path(repo_root).resolve(strict=True)
        if not self.repo_root.is_dir():
            raise ValueError("repo_root must be a directory")
        if allowed_paths is not None and (
            not isinstance(allowed_paths, list)
            or any(not isinstance(path, str) or not path for path in allowed_paths)
        ):
            raise ValueError("allowed_paths must be a list of non-empty strings")
        self._paths = self._resolve_allowlist(allowed_paths)

    @staticmethod
    def semantic_fingerprint(records: list[dict]) -> str:
        """Return a deterministic content fingerprint, ignoring timestamps."""
        canonical = []
        for record in records:
            canonical.append(
                "\0".join(
                    str(record.get(key, ""))
                    for key in ("source", "start_line", "end_line", "sha256", "excerpt")
                )
            )
        return _digest("\n".join(sorted(canonical)).encode("utf-8"))

    def _tracked_paths(self) -> list[str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_root), "ls-files", "-z"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError("default evidence corpus requires Git tracked-file discovery") from exc
        return [part.decode("utf-8", "surrogateescape") for part in result.stdout.split(b"\0") if part]

    @staticmethod
    def _is_private_path(relative: str) -> bool:
        parts = {part.casefold() for part in PurePosixPath(relative).parts}
        joined = relative.casefold()
        sensitive_part = any(
            marker in part
            for part in parts
            for marker in ("private", "archive", "supplied")
        )
        return sensitive_part or bool(parts & _SKIP_PARTS) or any(
            name in joined for name in ("axiomzero-synthesis", ".axiomzero-weave")
        )

    def _default_path(self, relative: str) -> bool:
        if self._is_private_path(relative):
            return False
        path = PurePosixPath(relative)
        return (
            relative in {"README.md", "FALLIBILITY.md", "STATUS.md", "SEPARATION.md",
                         "proof/TIER_1_FORMAL.md", "5-GOVERNANCE/SEPARATION.md"}
            or relative == "docs/TRUTH_LAYER.md"
            or relative.startswith("docs/") and path.suffix.casefold() == ".md"
            or relative in {"9-INFRASTRUCTURE/README.md", "9-INFRASTRUCTURE/llms.txt"}
            or relative.startswith("9-INFRASTRUCTURE/bot/rag/knowledge/")
            and path.suffix.casefold() == ".md"
            or relative in _CORE_FILES
            or len(path.parts) == 3 and path.parts[0] == "12-AZ-IP"
            and path.name == "README.md"
        )

    def _ignored_paths(self, paths: list[str]) -> set[str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_root), "check-ignore", "--no-index", "-z", "--stdin"],
                input=b"\0".join(path.encode() for path in paths) + b"\0",
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            )
        except OSError:
            result = None
        if result is not None and result.returncode in (0, 1):
            return {part.decode() for part in result.stdout.split(b"\0") if part}
        # Explicit reviewed allowlists also work in standalone source fixtures.
        ignore = self.repo_root / ".gitignore"
        if not ignore.is_file() or ignore.is_symlink():
            return set()
        patterns = [line.strip().lstrip("/") for line in ignore.read_text().splitlines()
                    if line.strip() and not line.startswith(("#", "!"))]
        return {path for path in paths if any(
            PurePosixPath(path).match(pattern.rstrip("/"))
            or any(PurePosixPath(parent).match(pattern.rstrip("/"))
                   for parent in PurePosixPath(path).parents if str(parent) != ".")
            for pattern in patterns)}

    def _resolve_allowlist(self, allowed_paths: list[str] | None) -> list[str]:
        if allowed_paths is None:
            candidates = [p for p in self._tracked_paths() if self._default_path(p)]
        else:
            candidates = []
            for item in allowed_paths:
                posix = PurePosixPath(item)
                if posix.is_absolute() or ".." in posix.parts or self._is_private_path(item):
                    raise ValueError(f"unsafe allowlist path: {item}")
                candidate = self.repo_root.joinpath(*posix.parts)
                self._check_path(candidate, item, must_exist=False)
                if candidate.is_dir() and not candidate.is_symlink():
                    candidates.extend(
                        file.relative_to(self.repo_root).as_posix()
                        for file in candidate.rglob("*")
                        if file.is_file()
                    )
                else:
                    candidates.append(posix.as_posix())
        ignored = self._ignored_paths(candidates)
        safe: set[str] = set()
        for relative in candidates:
            if self._is_private_path(relative) or relative in ignored:
                if allowed_paths is not None:
                    raise ValueError(f"private or ignored source path: {relative}")
                continue
            file = self.repo_root.joinpath(*PurePosixPath(relative).parts)
            try:
                self._check_path(file, relative, must_exist=False)
            except (ValueError, OSError):
                continue
            safe.add(relative)
        return sorted(safe)

    def _check_path(self, file: Path, relative: str, *, must_exist: bool) -> None:
        if Path(relative).is_absolute() or ".." in PurePosixPath(relative).parts:
            raise ValueError("source path escapes repository")
        try:
            file.relative_to(self.repo_root)
        except ValueError as exc:
            raise ValueError("source path escapes repository") from exc
        cursor = self.repo_root
        for part in PurePosixPath(relative).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError("symlink sources are not allowed")
        if must_exist and not file.is_file():
            raise ValueError("source file is unavailable")
        if file.exists() and not file.resolve().is_relative_to(self.repo_root):
            raise ValueError("source path escapes repository")

    def _read(self, relative: str) -> bytes | None:
        file = self.repo_root.joinpath(*PurePosixPath(relative).parts)
        try:
            self._check_path(file, relative, must_exist=True)
            with file.open("rb") as stream:
                data = stream.read(MAX_FILE_BYTES + 1)
        except (OSError, ValueError):
            return None
        if len(data) > MAX_FILE_BYTES:
            return None
        return data

    @staticmethod
    def _windows(lines: list[str], matched: set[int], current: set[int],
                 radius: int = 8) -> list[tuple[int, int]]:
        windows = set()
        for line in matched:
            start = end = line
            while start > max(1, line - radius) and start - 1 in current:
                start -= 1
            while end < min(len(lines), line + radius) and end + 1 in current:
                end += 1
            windows.add((start, end))
        return sorted(windows)

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Return ranked fresh excerpts with one-based, inclusive line citations."""
        if not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY_CHARS:
            raise ValueError("query must be a non-empty bounded string")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
            raise ValueError(f"limit must be between 1 and {MAX_LIMIT}")
        terms = [token for token in _tokens(query) if token not in _STOPWORDS]
        if not terms:
            raise ValueError("query must contain searchable terms")
        unique = set(terms)
        phrase = " ".join(query.casefold().split())
        ranked: list[dict] = []
        for relative in self._paths:
            data = self._read(relative)
            if data is None:
                continue
            text = data.decode("utf-8", "replace")
            lines = text.splitlines()
            current = _current_lines(relative, text)
            matched = {
                index
                for index, line in enumerate(lines, start=1)
                if index in current and unique.intersection(_tokens(line))
            }
            if not matched:
                continue
            sha256 = _digest(data)
            for start, end in self._windows(lines, matched, current):
                excerpt = "\n".join(lines[start - 1 : end])
                tokens = _tokens(excerpt)
                coverage = len(unique.intersection(tokens)) / len(unique)
                score = 10 * coverage + sum(min(tokens.count(term), 2) for term in unique) / len(unique)
                if phrase in " ".join(excerpt.casefold().split()):
                    score += 4.0
                if PurePosixPath(relative).name == "README.md" and relative.startswith("12-AZ-IP/"):
                    score += 0.5
                ranked.append(
                    {
                        "source": relative,
                        "start_line": start,
                        "end_line": end,
                        "excerpt": excerpt,
                        "sha256": sha256,
                        "evidence_kind": "source_content",
                        "score": round(score, 6),
                        "current": True,
                    }
                )
        ranked.sort(key=lambda hit: (-hit["score"], hit["source"], hit["start_line"]))
        selected: list[dict] = []
        for hit in ranked:
            if any(hit["source"] == prior["source"]
                   and hit["start_line"] <= prior["end_line"]
                   and prior["start_line"] <= hit["end_line"] for prior in selected):
                continue
            selected.append(hit)
            if len(selected) == limit:
                break
        return selected

    def verify(self, records: list[dict]) -> bool:
        """Bind each current source digest to its exact cited lines and excerpt."""
        if not isinstance(records, list):
            return False
        for record in records:
            if not isinstance(record, dict):
                return False
            source, expected = record.get("source"), record.get("sha256")
            if not isinstance(source, str) or source not in self._paths:
                return False
            data = self._read(source)
            if data is None or _digest(data) != expected:
                return False
            start, end = record.get("start_line"), record.get("end_line")
            text = data.decode("utf-8", "replace")
            lines = text.splitlines()
            if (
                type(start) is not int or type(end) is not int
                or not 1 <= start <= end <= len(lines)
                or record.get("evidence_kind") != "source_content"
                or record.get("current") is not True
                or record.get("excerpt") != "\n".join(lines[start - 1:end])
            ):
                return False
            if not set(range(start, end + 1)) <= _current_lines(source, text):
                return False
        return True
