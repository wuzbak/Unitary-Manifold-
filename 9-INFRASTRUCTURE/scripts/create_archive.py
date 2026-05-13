#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
create_archive.py — Package the Unitary Manifold project for local download.

Usage
-----
Run from repository root:
    python 9-INFRASTRUCTURE/scripts/create_archive.py                  # → unitary-manifold-omega-v10.52_<timestamp>.zip
    python 9-INFRASTRUCTURE/scripts/create_archive.py --out my_copy    # → my_copy_<timestamp>.zip

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
# Keep `.github` in full-download archives for reproducibility of CI/workflows.
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "wandb",  # W&B local run cache; integration module is in src/core/wandb_logger.py
}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}
EXCLUDE_EXTENSIONS = {".pyc", ".pyo"}

# ── Human-readable notes printed in the zip comment ──────────────────────────
SECTION_NOTES = """\
Unitary Manifold — full repository archive
==========================================
This zip contains all tracked source files and workflows at packaging time
(excluding .git history, local caches, and build artifacts).

Included highlights:
  README.md                      Project overview and current quick start
  STATUS.md                      Canonical status ledger
  CITATION.cff                   Citation metadata
  src/                           Core and adjacent-track implementation modules
  tests/                         Primary validation suite
  recycling/                     Pillar 16 entropy accounting suite
  5-GOVERNANCE/Unitary Pentad/   Independent HILS governance framework
  9-INFRASTRUCTURE/              Provenance and infrastructure metadata
  .github/workflows/             CI and release automation definitions

Quick start:
  pip install -r requirements.txt
  python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q

Validation expectation:
  Suite should complete with 0 failed tests.
  For canonical latest pass/skip totals, see STATUS.md in this archive.
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
    parser.add_argument("--out", default="unitary-manifold-omega-v10.52",
                        help="Base name for the output zip (no extension). "
                             "A timestamp is appended automatically.")
    args = parser.parse_args()

    # Locate repo root: this script is at <repo_root>/9-INFRASTRUCTURE/scripts/create_archive.py
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    required_markers = ("README.md", "CITATION.cff")
    missing_markers = [name for name in required_markers if not (repo_root / name).exists()]
    if missing_markers:
        raise FileNotFoundError(
            "Could not resolve repository root from script location. "
            f"Missing marker files at {repo_root}: {', '.join(missing_markers)}"
        )

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
