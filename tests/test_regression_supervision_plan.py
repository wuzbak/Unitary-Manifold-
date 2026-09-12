# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.regression_supervision_plan import (
    COMPACTIFIED_PREFLIGHT_FILES,
    DEFAULT_FAST_BATCH_COUNT,
    FAST_MARK_EXPRESSION,
    build_fast_suite_batches,
    build_regression_supervision_plan,
    compactified_preflight_command,
    discover_fast_suite_files,
    fast_batch_command,
)


def test_discovery_returns_sorted_files() -> None:
    files = discover_fast_suite_files()
    assert files == sorted(files)
    assert 'tests/test_regression_supervision_plan.py' in files


def test_batches_cover_discovered_fast_suite_without_overlap() -> None:
    batches = build_fast_suite_batches()
    discovered = discover_fast_suite_files()
    flattened = [path for batch in batches for path in batch['test_paths']]
    assert flattened == discovered
    assert len(set(flattened)) == len(flattened)
    assert all(batch['marker_expression'] == FAST_MARK_EXPRESSION for batch in batches)


def test_fast_batch_command_uses_non_slow_marker() -> None:
    command = fast_batch_command(batch_index=0, batch_count=DEFAULT_FAST_BATCH_COUNT)
    assert 'python -m pytest -n auto -m "not slow"' in command
    assert command.endswith(' -q')
    assert 'tests/' in command


def test_compactified_preflight_files_exist_and_command_is_canonical() -> None:
    command = compactified_preflight_command()
    assert command.startswith('python -m pytest ')
    for path in COMPACTIFIED_PREFLIGHT_FILES:
        assert path in command


def test_regression_supervision_plan_reports_consistent_coverage() -> None:
    plan = build_regression_supervision_plan()
    assert plan['supervision']['coverage_matches_discovery'] is True
    assert plan['supervision']['all_files_unique'] is True
    assert len(plan['supervised_fast_suite']['batches']) == DEFAULT_FAST_BATCH_COUNT
    assert plan['remaining_canonical_suites']['slow'] == 'python -m pytest tests/ -m "slow" -q'
