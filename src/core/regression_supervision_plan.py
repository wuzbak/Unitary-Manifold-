# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deterministic supervised regression batching for oversized pytest suites."""

from __future__ import annotations

import shlex
import importlib.util
from pathlib import Path
from typing import Any, Dict, List

_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FAST_BATCH_COUNT = 4
DEFAULT_FULL_CORE_BATCH_COUNT = 8
FAST_MARK_EXPRESSION = "not slow"
SLOW_MARK_EXPRESSION = "slow"
FAST_SUITE_PATH = "tests/"
CLAIMS_SUITE_PATH = "claims/"
RECYCLING_SUITE_PATH = "recycling/"
PENTAD_SUITE_PATH = "5-GOVERNANCE/Unitary Pentad/"
FULL_CORE_SUITE_PATHS = (
    FAST_SUITE_PATH,
    RECYCLING_SUITE_PATH,
    PENTAD_SUITE_PATH,
)
FAST_SUITE_EXCLUDED_FILES = {
    "tests/test_richardson_multitime.py",
}
COMPACTIFIED_PREFLIGHT_FILES = [
    "tests/test_closure_batch1.py",
    "tests/test_closure_batch2.py",
    "tests/test_formal_bridge_schema.py",
    "tests/test_lean_python_bridge_ir.py",
    "tests/test_formal_traceability_spine.py",
    "tests/test_action_to_evolution_contract.py",
]

def discover_fast_suite_files() -> List[str]:
    """Return the deterministic sorted test-file list for the repository-root tests/ suite."""
    test_root = _ROOT / "tests"
    return sorted(
        path.relative_to(_ROOT).as_posix()
        for path in test_root.rglob("test_*.py")
        if path.is_file() and path.relative_to(_ROOT).as_posix() not in FAST_SUITE_EXCLUDED_FILES
    )


def _discover_suite_files(suite_path: str) -> List[str]:
    suite_root = _ROOT / suite_path.rstrip("/")
    if not suite_root.exists():
        return []
    return sorted(
        path.relative_to(_ROOT).as_posix()
        for path in suite_root.rglob("test_*.py")
        if path.is_file()
        and not path.relative_to(_ROOT).as_posix().startswith("5-GOVERNANCE/Unitary Pentad/holon-zero/")
    )


def discover_full_core_suite_files() -> List[str]:
    """Return the deterministic sorted file list for the combined tests/recycling/pentad core."""
    combined: List[str] = []
    for suite_path in FULL_CORE_SUITE_PATHS:
        combined.extend(_discover_suite_files(suite_path))
    return sorted(combined)


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


def pytest_xdist_available() -> bool:
    """Return whether pytest-xdist is importable in the current environment."""
    return importlib.util.find_spec("xdist") is not None


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


def build_full_core_batches(batch_count: int = DEFAULT_FULL_CORE_BATCH_COUNT) -> List[Dict[str, Any]]:
    """Return deterministic supervised file batches for the full tests/recycling/pentad core."""
    files = discover_full_core_suite_files()
    partitions = _partition_evenly(files, batch_count)
    batches: List[Dict[str, Any]] = []
    for index, batch_files in enumerate(partitions):
        batches.append(
            {
                "batch_index": index,
                "batch_count": batch_count,
                "suite_paths": list(FULL_CORE_SUITE_PATHS),
                "test_paths": batch_files,
                "file_count": len(batch_files),
                "first_file": batch_files[0] if batch_files else "",
                "last_file": batch_files[-1] if batch_files else "",
            }
        )
    return batches


def _pytest_argv_from_paths(paths: List[str], marker_expression: str | None = None) -> List[str]:
    if not paths:
        return []
    command = ["python", "-m", "pytest"]
    if pytest_xdist_available():
        command.extend(["-n", "auto"])
    if marker_expression:
        command.extend(["-m", marker_expression])
    command.extend([*paths, "-q"])
    return command


def _fast_batch_command_from_paths(paths: List[str]) -> str:
    return shlex.join(_pytest_argv_from_paths(paths, marker_expression=FAST_MARK_EXPRESSION))


def _full_core_batch_command_from_paths(paths: List[str]) -> str:
    return shlex.join(_pytest_argv_from_paths(paths))


def fast_batch_command(batch_index: int, batch_count: int = DEFAULT_FAST_BATCH_COUNT) -> str:
    """Return the canonical pytest command for one supervised non-slow batch."""
    batches = build_fast_suite_batches(batch_count=batch_count)
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError("batch_index out of range")
    return _fast_batch_command_from_paths(batches[batch_index]["test_paths"])


def fast_batch_argv(batch_index: int, batch_count: int = DEFAULT_FAST_BATCH_COUNT) -> List[str]:
    """Return the canonical pytest argv for one supervised non-slow batch."""
    batches = build_fast_suite_batches(batch_count=batch_count)
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError("batch_index out of range")
    return _pytest_argv_from_paths(
        batches[batch_index]["test_paths"],
        marker_expression=FAST_MARK_EXPRESSION,
    )


def full_core_batch_command(
    batch_index: int,
    batch_count: int = DEFAULT_FULL_CORE_BATCH_COUNT,
) -> str:
    """Return the canonical pytest command for one supervised full-core batch."""
    batches = build_full_core_batches(batch_count=batch_count)
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError("batch_index out of range")
    return _full_core_batch_command_from_paths(batches[batch_index]["test_paths"])


def full_core_batch_argv(
    batch_index: int,
    batch_count: int = DEFAULT_FULL_CORE_BATCH_COUNT,
) -> List[str]:
    """Return the canonical pytest argv for one supervised full-core batch."""
    batches = build_full_core_batches(batch_count=batch_count)
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError("batch_index out of range")
    return _pytest_argv_from_paths(batches[batch_index]["test_paths"])


def compactified_preflight_command() -> str:
    """Return the canonical compactified preflight command."""
    return shlex.join(compactified_preflight_argv())


def compactified_preflight_argv() -> List[str]:
    """Return the canonical compactified preflight argv."""
    return ["python", "-m", "pytest", *COMPACTIFIED_PREFLIGHT_FILES, "-q"]


def build_regression_supervision_plan(batch_count: int = DEFAULT_FAST_BATCH_COUNT) -> Dict[str, Any]:
    """Return the machine-readable supervised regression plan."""
    return build_regression_supervision_plan_with_full_core_count(
        batch_count=batch_count,
        full_core_batch_count=DEFAULT_FULL_CORE_BATCH_COUNT,
    )


def build_regression_supervision_plan_with_full_core_count(
    batch_count: int = DEFAULT_FAST_BATCH_COUNT,
    full_core_batch_count: int = DEFAULT_FULL_CORE_BATCH_COUNT,
) -> Dict[str, Any]:
    """Return the machine-readable supervised regression plan."""
    batches = build_fast_suite_batches(batch_count=batch_count)
    all_files = [path for batch in batches for path in batch["test_paths"]]
    discovered = discover_fast_suite_files()
    unique_files = sorted(set(all_files))
    full_core_batches = build_full_core_batches(batch_count=full_core_batch_count)
    full_core_files = [path for batch in full_core_batches for path in batch["test_paths"]]
    full_core_discovered = discover_full_core_suite_files()
    full_core_unique = sorted(set(full_core_files))
    remaining_canonical_suites: Dict[str, str] = {
        "slow": f'python -m pytest {FAST_SUITE_PATH} -m "{SLOW_MARK_EXPRESSION}" -q',
        "recycling": f"python -m pytest {RECYCLING_SUITE_PATH} -q",
        "pentad": f'python -m pytest "{PENTAD_SUITE_PATH}" -q',
        "full": f'python3 -m pytest {FAST_SUITE_PATH} {RECYCLING_SUITE_PATH} "{PENTAD_SUITE_PATH}" -q',
    }
    if (_ROOT / CLAIMS_SUITE_PATH.rstrip("/")).is_dir():
        remaining_canonical_suites["claims"] = f"python -m pytest {CLAIMS_SUITE_PATH} -q"
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
                _fast_batch_command_from_paths(batch["test_paths"])
                for batch in batches
            ],
        },
        "supervised_full_core_suite": {
            "suite_paths": list(FULL_CORE_SUITE_PATHS),
            "default_batch_count": full_core_batch_count,
            "batches": full_core_batches,
            "batch_commands": [
                _full_core_batch_command_from_paths(batch["test_paths"])
                for batch in full_core_batches
            ],
        },
        "remaining_canonical_suites": remaining_canonical_suites,
        "supervision": {
            "coverage_matches_discovery": all_files == discovered,
            "all_files_unique": len(unique_files) == len(all_files),
            "discovered_file_count": len(discovered),
            "batched_file_count": len(all_files),
            "full_core_coverage_matches_discovery": full_core_files == full_core_discovered,
            "full_core_all_files_unique": len(full_core_unique) == len(full_core_files),
            "full_core_discovered_file_count": len(full_core_discovered),
            "full_core_batched_file_count": len(full_core_files),
        },
    }


__all__ = [
    "COMPACTIFIED_PREFLIGHT_FILES",
    "DEFAULT_FAST_BATCH_COUNT",
    "DEFAULT_FULL_CORE_BATCH_COUNT",
    "FAST_MARK_EXPRESSION",
    "FULL_CORE_SUITE_PATHS",
    "build_fast_suite_batches",
    "build_full_core_batches",
    "build_regression_supervision_plan",
    "build_regression_supervision_plan_with_full_core_count",
    "compactified_preflight_argv",
    "compactified_preflight_command",
    "discover_fast_suite_files",
    "discover_full_core_suite_files",
    "fast_batch_argv",
    "fast_batch_command",
    "full_core_batch_argv",
    "full_core_batch_command",
]
