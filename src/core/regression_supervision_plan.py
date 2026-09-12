# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deterministic supervised regression batching for oversized pytest suites."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FAST_BATCH_COUNT = 4
FAST_MARK_EXPRESSION = "not slow"
SLOW_MARK_EXPRESSION = "slow"
FAST_SUITE_PATH = "tests/"
CLAIMS_SUITE_PATH = "claims/"
RECYCLING_SUITE_PATH = "recycling/"
PENTAD_SUITE_PATH = "5-GOVERNANCE/Unitary Pentad/"
COMPACTIFIED_PREFLIGHT_FILES = [
    "tests/test_closure_batch1.py",
    "tests/test_closure_batch2.py",
    "tests/test_formal_bridge_schema.py",
    "tests/test_lean_python_bridge_ir.py",
    "tests/test_formal_traceability_spine.py",
    "tests/test_action_to_evolution_contract.py",
]


def discover_fast_suite_files() -> List[str]:
    """Return the deterministic sorted test-file list for the non-slow tests/ suite."""
    test_root = _ROOT / "tests"
    return sorted(
        path.relative_to(_ROOT).as_posix()
        for path in test_root.rglob("test_*.py")
        if path.is_file()
    )


def _partition_evenly(items: List[str], batch_count: int) -> List[List[str]]:
    if batch_count <= 0:
        raise ValueError("batch_count must be positive")
    if not items:
        return [[] for _ in range(batch_count)]
    base = len(items) // batch_count
    remainder = len(items) % batch_count
    partitions: List[List[str]] = []
    start = 0
    for index in range(batch_count):
        size = base + (1 if index < remainder else 0)
        stop = start + size
        partitions.append(items[start:stop])
        start = stop
    return partitions


def build_fast_suite_batches(batch_count: int = DEFAULT_FAST_BATCH_COUNT) -> List[Dict[str, Any]]:
    """Return deterministic supervised file batches for the non-slow tests/ suite."""
    files = discover_fast_suite_files()
    partitions = _partition_evenly(files, batch_count)
    batches: List[Dict[str, Any]] = []
    for index, batch_files in enumerate(partitions):
        batches.append(
            {
                "batch_index": index,
                "batch_count": batch_count,
                "marker_expression": FAST_MARK_EXPRESSION,
                "test_paths": batch_files,
                "file_count": len(batch_files),
                "first_file": batch_files[0] if batch_files else "",
                "last_file": batch_files[-1] if batch_files else "",
            }
        )
    return batches


def fast_batch_command(batch_index: int, batch_count: int = DEFAULT_FAST_BATCH_COUNT) -> str:
    """Return the canonical pytest command for one supervised non-slow batch."""
    batches = build_fast_suite_batches(batch_count=batch_count)
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError("batch_index out of range")
    batch = batches[batch_index]
    if not batch["test_paths"]:
        raise ValueError("selected batch is empty")
    paths = " ".join(batch["test_paths"])
    return f'python -m pytest -n auto -m "{FAST_MARK_EXPRESSION}" {paths} -q'


def compactified_preflight_command() -> str:
    """Return the canonical compactified preflight command."""
    files = " ".join(COMPACTIFIED_PREFLIGHT_FILES)
    return f"python -m pytest {files} -q"


def build_regression_supervision_plan(batch_count: int = DEFAULT_FAST_BATCH_COUNT) -> Dict[str, Any]:
    """Return the machine-readable supervised regression plan."""
    batches = build_fast_suite_batches(batch_count=batch_count)
    all_files = [path for batch in batches for path in batch["test_paths"]]
    discovered = discover_fast_suite_files()
    unique_files = sorted(set(all_files))
    return {
        "default_fast_batch_count": batch_count,
        "compactified_preflight": {
            "test_paths": list(COMPACTIFIED_PREFLIGHT_FILES),
            "command": compactified_preflight_command(),
        },
        "supervised_fast_suite": {
            "suite_path": FAST_SUITE_PATH,
            "marker_expression": FAST_MARK_EXPRESSION,
            "batches": batches,
            "batch_commands": [
                fast_batch_command(batch_index=index, batch_count=batch_count)
                for index in range(batch_count)
            ],
        },
        "remaining_canonical_suites": {
            "slow": f'python -m pytest {FAST_SUITE_PATH} -m "{SLOW_MARK_EXPRESSION}" -q',
            "claims": f"python -m pytest {CLAIMS_SUITE_PATH} -q",
            "recycling": f"python -m pytest {RECYCLING_SUITE_PATH} -q",
            "pentad": f'python -m pytest "{PENTAD_SUITE_PATH}" -q',
            "full": f'python3 -m pytest {FAST_SUITE_PATH} {RECYCLING_SUITE_PATH} "{PENTAD_SUITE_PATH}" -q',
        },
        "supervision": {
            "coverage_matches_discovery": all_files == discovered,
            "all_files_unique": len(unique_files) == len(all_files),
            "discovered_file_count": len(discovered),
            "batched_file_count": len(all_files),
        },
    }


__all__ = [
    "COMPACTIFIED_PREFLIGHT_FILES",
    "DEFAULT_FAST_BATCH_COUNT",
    "FAST_MARK_EXPRESSION",
    "build_fast_suite_batches",
    "build_regression_supervision_plan",
    "compactified_preflight_command",
    "discover_fast_suite_files",
    "fast_batch_command",
]
