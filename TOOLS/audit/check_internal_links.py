#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Check internal Markdown links for missing repository targets."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((<[^>]+>|[^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "doi"}
SKIP_PREFIXES = ("#", "data:")


def iter_markdown_files(root: Path) -> list[Path]:
    ignored = {".git", ".dvc", "__pycache__"}
    return sorted(
        path
        for path in root.rglob("*.md")
        if not any(part in ignored for part in path.parts)
    )


def normalize_target(raw: str) -> str:
    target = raw.strip()
    if not target or target.startswith(SKIP_PREFIXES):
        return ""
    if " " in target and not target.startswith("<"):
        target = target.split()[0]
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target


def target_exists(source: Path, raw_target: str) -> bool:
    target = normalize_target(raw_target)
    if not target:
        return True
    parsed = urlparse(target)
    if parsed.scheme in SKIP_SCHEMES or parsed.netloc:
        return True
    path_part = unquote(parsed.path)
    if not path_part:
        return True
    candidate = (source.parent / path_part).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return True
    if candidate.exists():
        return True
    if not candidate.suffix and candidate.with_suffix(".md").exists():
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to scan")
    args = parser.parse_args()

    root = args.root.resolve()
    failures: list[tuple[Path, int, str]] = []
    for md_file in iter_markdown_files(root):
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        in_fence = False
        for line_no, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in LINK_RE.finditer(line):
                target = match.group(1)
                if not target_exists(md_file, target):
                    failures.append((md_file.relative_to(root), line_no, target))

    if failures:
        print("Broken internal Markdown links:")
        for path, line_no, target in failures:
            print(f"{path}:{line_no}: {target}")
        return 1

    print(f"Checked {len(iter_markdown_files(root))} Markdown files: all internal file links resolved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
