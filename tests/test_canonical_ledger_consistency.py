# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from src.core.canonical_ledger_consistency import (
    LEDGER_PATHS,
    ONBOARDING_PATHS,
    canonical_ledger_consistency_report,
    canonical_ledger_snapshot,
    onboarding_docs_consistency_report,
)


# ──────────────────────────────────────────────────────────────────────────────
# Core ledger tests (unchanged behaviour)
# ──────────────────────────────────────────────────────────────────────────────

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
    assert report["public_version_consistent"] is True
    assert report["public_regression_consistent"] is True
    assert report["all_pass"] is True


# ──────────────────────────────────────────────────────────────────────────────
# Onboarding docs tests (new)
# ──────────────────────────────────────────────────────────────────────────────

class TestOnboardingDocsConsistency:
    """Every user-facing onboarding document must contain the canonical passed count."""

    def test_onboarding_paths_are_defined(self):
        assert len(ONBOARDING_PATHS) >= 6, "Expected at least 6 onboarding doc paths"

    def test_onboarding_report_has_canonical_count(self):
        report = onboarding_docs_consistency_report()
        assert report["canonical"] is not None, "STATUS.md must export a regression count"
        assert report["canonical"]["passed"] > 0

    def test_all_onboarding_docs_exist(self):
        report = onboarding_docs_consistency_report()
        missing = [
            key for key, res in report["results"].items() if not res["exists"]
        ]
        assert missing == [], f"Onboarding doc files not found on disk: {missing}"

    def test_all_onboarding_docs_contain_canonical_count(self):
        report = onboarding_docs_consistency_report()
        drifted = report["drifted_docs"]
        canonical = report["canonical"]
        assert drifted == [], (
            f"These onboarding docs do not contain the canonical passed count "
            f"({canonical['passed']} passed): {drifted}. "
            f"Update them to match STATUS.md."
        )

    def test_onboarding_all_pass(self):
        report = onboarding_docs_consistency_report()
        assert report["all_pass"] is True, (
            f"Onboarding consistency check failed. Drifted docs: {report['drifted_docs']}"
        )
