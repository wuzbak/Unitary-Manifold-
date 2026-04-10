#!/usr/bin/env python3
"""
create_archive.py — Package the Unitary Manifold project for local download.

Usage
-----
    python scripts/create_archive.py                  # → unitary-manifold.zip
    python scripts/create_archive.py --out my_copy    # → my_copy.zip

Run this from the repository root (the folder that contains README.md).
The resulting zip contains every project file in a well-organized layout;
Python cache folders and other generated artifacts are excluded.
"""

import argparse
import os
import zipfile
from datetime import datetime
from pathlib import Path

# ── Files / directories to exclude ──────────────────────────────────────────
EXCLUDE_DIRS = {".git", "__pycache__", ".github", "node_modules", ".mypy_cache"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}
EXCLUDE_EXTENSIONS = {".pyc", ".pyo"}

# ── Human-readable section labels printed inside the zip comment ─────────────
SECTION_NOTES = """\
Unitary Manifold — project archive
===================================
Contents
--------
  THEBOOKV9a (1).pdf        Full monograph (PDF)
  README.md                 Project overview and quick-start
  CITATION.cff              Machine-readable citation metadata
  requirements.txt          Python dependencies  (pip install -r requirements.txt)

  arxiv/
    main.tex                LaTeX source for the arXiv submission
    references.bib          BibTeX reference list
    SUBMISSION_GUIDE.md     Step-by-step arXiv upload guide

  manuscript/
    ch02_mathematical_preliminaries.md   Chapter 2 draft

  src/
    core/
      metric.py             Unitary metric tensor implementation
      evolution.py          Quantum / geometric evolution utilities
    holography/
      boundary.py           AdS/CFT boundary-state tools
    multiverse/
      fixed_point.py        Fixed-point / attractor analysis

  discussions/
    AI-Automated-Review-Invitation.md    Peer-review discussion notes

  zenodo/
    .zenodo.json            Zenodo metadata
    SUBMISSION_GUIDE.md     Step-by-step Zenodo deposit guide

  scripts/
    create_archive.py       This packaging script (re-run any time)

Getting started
---------------
  pip install -r requirements.txt
  python -c "from src.core import metric, evolution; print('OK')"
"""


def should_exclude(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    if path.name in EXCLUDE_FILES:
        return True
    if path.suffix in EXCLUDE_EXTENSIONS:
        return True
    return False


def build_archive(repo_root: Path, output_stem: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"{output_stem}_{timestamp}.zip"
    archive_path = repo_root / archive_name

    prefix = output_stem + "/"

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.comment = SECTION_NOTES.encode()

        # Walk every file under repo_root
        for file_path in sorted(repo_root.rglob("*")):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(repo_root)
            if should_exclude(rel):
                continue
            # Don't include a previous archive of ourselves
            if file_path.suffix == ".zip" and file_path.parent == repo_root:
                continue
            arcname = prefix + str(rel)
            zf.write(file_path, arcname)
            print(f"  + {arcname}")

    return archive_path


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default="unitary-manifold",
                        help="Base name for the output zip (no extension). "
                             "A timestamp is appended automatically.")
    args = parser.parse_args()

    # Locate repo root: the directory that contains this script's parent
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    print(f"Packaging: {repo_root}")
    archive = build_archive(repo_root, args.out)
    size_mb = archive.stat().st_size / (1024 * 1024)
    print(f"\n✓ Archive created: {archive.name}  ({size_mb:.2f} MB)")
    print(f"  Full path: {archive}")
    print("\nExtract with:")
    print(f"  unzip {archive.name}          # Linux / macOS")
    print(f"  Expand-Archive {archive.name} # Windows PowerShell")


if __name__ == "__main__":
    main()
