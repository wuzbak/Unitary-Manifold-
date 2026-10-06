# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Explicit filesystem snapshots for checks that write into their source tree."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .evidence import EvidenceError, contained, file_hash, fingerprints, write_json


def snapshot(root: Path, output: Path) -> dict:
    """Copy source inputs once; neither run commands nor certify their results."""
    root = root.resolve()
    output = output.absolute()
    if not root.is_dir() or output.exists() or output.is_symlink():
        raise EvidenceError("Snapshot requires an existing root and a new output directory")
    resolved = output.resolve()
    if resolved.is_relative_to(root) or root.is_relative_to(resolved):
        raise EvidenceError("Snapshot output must be outside the source tree")
    # Reject aliases in the destination path before creating anything.
    for parent in [output, *output.parents]:
        if parent.is_symlink():
            raise EvidenceError("Snapshot destination may not traverse symlinks")
    settings = {"operation": "source_snapshot", "version": 1}
    before = fingerprints(root, output, settings)
    output.mkdir(parents=True, exist_ok=False)
    source = output / "source"
    source.mkdir()
    try:
        for relative in before["source_directories"]:
            contained(source, relative, must_exist=False).mkdir(parents=True, exist_ok=True)
        for relative, expected in before["source_files"].items():
            original = contained(root, relative)
            destination = contained(source, relative, must_exist=False)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, destination)
            if file_hash(destination) != expected:
                raise EvidenceError(f"Source changed while copying: {relative}")
        for relative, metadata in before["source_links"].items():
            destination = contained(source, relative, must_exist=False)
            destination.parent.mkdir(parents=True, exist_ok=True)
            target = source / metadata["resolved"]
            is_directory = (root / metadata["resolved"]).is_dir()
            if is_directory:
                target.mkdir(parents=True, exist_ok=True)
            # Absolute source links must not escape back to the original working tree.
            destination.symlink_to(os.path.relpath(target, destination.parent),
                                   target_is_directory=is_directory)
        after = fingerprints(root, output, settings)
        if after["compatibility"] != before["compatibility"]:
            raise EvidenceError("Source/environment changed while creating snapshot")
        result = {
            "status": "snapshot_ready", "source_root": str(root),
            "snapshot_root": str(source), "original_fingerprints": before,
            "snapshot_fingerprints": fingerprints(source, output / "evidence", settings),
            "proof_claim": False, "test_gate": False,
            "boundary": "Filesystem copy only, not execution or certification. "
                        "Checks may mutate this isolated copy; such runs remain source-unstable "
                        "and cannot satisfy a frozen-source gate.",
        }
        write_json(output / "snapshot.json", result)
        return result
    except BaseException:
        shutil.rmtree(output)
        raise
