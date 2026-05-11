# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from src.core.canonical_ledger_consistency import (
    LEDGER_PATHS,
    canonical_ledger_consistency_report,
    canonical_ledger_snapshot,
)


def test_snapshot_contains_all_ledgers():
    snapshot = canonical_ledger_snapshot()
    assert set(snapshot) == set(LEDGER_PATHS)


def test_core_versions_are_present():
    snapshot = canonical_ledger_snapshot()
    assert snapshot["status"]["version"] is not None
    assert snapshot["fallibility"]["version"] is not None
    assert snapshot["derivation_status"]["version"] is not None


def test_consistency_report_passes():
    report = canonical_ledger_consistency_report()
    assert report["version_consistent"] is True
    assert report["regression_consistent"] is True
    assert report["all_pass"] is True
