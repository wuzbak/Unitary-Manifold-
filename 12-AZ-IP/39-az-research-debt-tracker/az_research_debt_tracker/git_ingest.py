# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Read committed source comments as provenance-bearing research debt."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
from pathlib import Path
import re
import subprocess

from .tracker import ResearchDebtTracker, WorkItem

SOURCE_SUFFIXES = frozenset({
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".c", ".h",
    ".cpp", ".hpp", ".java", ".sh", ".sql",
})
MARKER = re.compile(r"^\s*(?:#|//|/\*|\*|--)\s*(TODO|FIXME)\b[: \t]*(.*)")


def _git(repo: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, check=True, timeout=60,
        )
    except FileNotFoundError as exc:
        raise ValueError("Git executable is required") from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Git command timed out") from exc
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"Git failed: {exc.stderr.decode('utf-8', errors='replace').strip()}") from exc
    return result.stdout


def ingest_git_debt(repo: str | Path, revision: str = "HEAD") -> dict:
    """Scan one immutable commit, never the index or working tree.

    Only standalone TODO/FIXME comment lines in supported UTF-8 source
    files are recognized. Results are an inventory, not closure evidence.
    """
    repo = Path(repo).resolve()
    root = _git(repo, "rev-parse", "--show-toplevel").decode().strip()
    commit = _git(
        repo, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}",
    ).decode().strip()
    tree = _git(repo, "ls-tree", "-r", "-z", commit)
    tracker = ResearchDebtTracker()
    evidence = {}
    scanned = 0
    skipped = 0
    for entry in tree.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, blob = metadata.decode("ascii").split()
        path = raw_path.decode("utf-8", errors="surrogateescape")
        if kind != "blob" or mode not in {"100644", "100755"}:
            continue
        if Path(path).suffix.lower() not in SOURCE_SUFFIXES:
            continue
        content = _git(repo, "cat-file", "blob", blob)
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            skipped += 1
            continue
        if "\0" in text:
            skipped += 1
            continue
        scanned += 1
        for line_number, line in enumerate(text.splitlines(), 1):
            match = MARKER.match(line)
            if match is None:
                continue
            marker, description = match.groups()
            description = description.removesuffix("*/").strip() or f"{marker} needs triage"
            identity = f"{path}\0{line_number}\0{marker}".encode("utf-8", errors="surrogateescape")
            item_id = "git-" + hashlib.sha256(identity).hexdigest()
            tracker.add_item(WorkItem(
                item_id, description, "OPEN",
                "significant" if marker == "FIXME" else "minor",
                f"{path}:{line_number}",
            ))
            evidence[item_id] = {
                "source": "git", "commit": commit, "blob": blob,
                "path": path, "line": line_number, "marker": marker,
                "source_line": line,
                "next_action": "Triage this committed comment; assign an owner and verify remediation.",
            }
    return {
        "schema_version": 1,
        "source": {"kind": "local_git", "repository": root, "commit": commit},
        "coverage": {"source_files_scanned": scanned, "binary_or_non_utf8_skipped": skipped},
        "health_score": asdict(tracker.health_score()),
        "items": [
            {**asdict(item), "evidence": evidence[item.item_id]}
            for item in tracker.all_items()
        ],
    }
