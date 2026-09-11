# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from __future__ import annotations

from src.core.canonical_ledger_consistency import (
    LEDGER_PATHS,
    LEDGER_SYNC_REQUIRED_PATHS,
    ONBOARDING_PATHS,
    canonical_ledger_consistency_report,
    canonical_ledger_sync_requirement,
    canonical_status_token_report,
    canonical_ledger_snapshot,
    closure_gate_label_discipline_report,
    historical_snapshot_disclaimer_report,
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
    assert report["version_consistent"] is True, (
        "Core ledger versions drifted: "
        f"{report['core_versions']}. Keep STATUS.md, FALLIBILITY.md, and "
        "1-THEORY/DERIVATION_STATUS.md on the same version."
    )
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


class TestCanonicalStatusTokenSync:
    def test_canonical_status_tokens_exist_in_all_ledgers(self):
        report = canonical_status_token_report()
        assert report["all_pass"] is True, (
            f"Missing canonical status tokens: {report['missing']}"
        )


class TestClosureGateLabelDiscipline:
    def test_no_premature_fully_closed_labels(self):
        report = closure_gate_label_discipline_report()
        assert report["all_pass"] is True, (
            f"Forbidden FULLY_CLOSED labels detected: {report['violations']}"
        )


class TestHistoricalSnapshotDisclaimers:
    def test_archived_ledgers_are_explicitly_marked_non_canonical(self):
        report = historical_snapshot_disclaimer_report()
        assert report["all_pass"] is True, (
            "Historical ledger disclaimer markers missing: "
            f"{report['missing']}"
        )


class TestCanonicalLedgerSyncRequirement:
    def test_existing_pillar_maintenance_edit_does_not_require_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=[
                "src/core/pillar1087_sprint_cm_full_physics_parallel_execution.py",
                "tests/test_pillar1087_sprint_cm_full_physics_parallel_execution.py",
            ],
            name_status_lines=[
                "M\tsrc/core/pillar1087_sprint_cm_full_physics_parallel_execution.py",
                "M\ttests/test_pillar1087_sprint_cm_full_physics_parallel_execution.py",
            ],
            patch_by_path={
                "src/core/pillar1087_sprint_cm_full_physics_parallel_execution.py": (
                    "@@ -195,0 +196,4 @@\n"
                    "+    head_sha = _run_git([\"rev-parse\", \"HEAD\"])\n"
                )
            },
        )
        assert report["requires_sync"] is False
        assert report["matched_paths"] == []

    def test_new_pillar_file_requires_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/pillar1121_new_thing.py"],
            name_status_lines=["A\tsrc/core/pillar1121_new_thing.py"],
        )
        assert report["requires_sync"] is True
        assert report["all_required_paths_changed"] is False
        assert report["missing_required_paths"] == list(LEDGER_SYNC_REQUIRED_PATHS)

    def test_status_bearing_metadata_edit_requires_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/pillar1087_sprint_cm_full_physics_parallel_execution.py"],
            name_status_lines=["M\tsrc/core/pillar1087_sprint_cm_full_physics_parallel_execution.py"],
            patch_by_path={
                "src/core/pillar1087_sprint_cm_full_physics_parallel_execution.py": (
                    "@@ -29,2 +29,2 @@\n"
                    '-PILLAR_STATUS: str = "OLD"\n'
                    '+PILLAR_STATUS: str = "NEW"\n'
                )
            },
        )
        assert report["requires_sync"] is True
        assert report["reasons"] == [
            "status-bearing pillar metadata changed in src/core/pillar1087_sprint_cm_full_physics_parallel_execution.py"
        ]

    def test_sm_free_parameters_always_requires_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/sm_free_parameters.py"],
            name_status_lines=["M\tsrc/core/sm_free_parameters.py"],
        )
        assert report["requires_sync"] is True

    def test_renamed_pillar_file_with_new_identity_requires_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/pillar1121_new_name.py"],
            name_status_lines=["R100\tsrc/core/pillar1087_old_name.py\tsrc/core/pillar1121_new_name.py"],
        )
        assert report["requires_sync"] is True
        assert report["matched_paths"] == ["src/core/pillar1121_new_name.py"]
        assert report["reasons"] == ["renamed pillar file with new identity src/core/pillar1121_new_name.py"]

    def test_same_identity_rename_without_metadata_change_does_not_require_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/pillar1087_history_variant.py"],
            name_status_lines=["R100\tsrc/core/pillar1087_sprint_cm_full_physics_parallel_execution.py\tsrc/core/pillar1087_history_variant.py"],
            patch_by_path={
                "src/core/pillar1087_history_variant.py": "@@ -1 +1 @@\n+helper = 1\n",
            },
        )
        assert report["requires_sync"] is False

    def test_rename_from_pillar_to_nonpillar_path_requires_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/history_variant.py"],
            name_status_lines=["R100\tsrc/core/pillar1087_sprint_cm_full_physics_parallel_execution.py\tsrc/core/history_variant.py"],
        )
        assert report["requires_sync"] is True
        assert report["reasons"] == ["renamed pillar file with new identity src/core/history_variant.py"]

    def test_copied_pillar_file_requires_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/pillar1121_copy.py"],
            name_status_lines=["C100\tsrc/core/pillar1087_sprint_cm_full_physics_parallel_execution.py\tsrc/core/pillar1121_copy.py"],
        )
        assert report["requires_sync"] is True
        assert report["matched_paths"] == ["src/core/pillar1121_copy.py"]
        assert report["reasons"] == ["copied pillar file with new identity src/core/pillar1121_copy.py"]

    def test_same_identity_copy_without_metadata_change_does_not_require_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/pillar1087_copy_variant.py"],
            name_status_lines=["C100\tsrc/core/pillar1087_sprint_cm_full_physics_parallel_execution.py\tsrc/core/pillar1087_copy_variant.py"],
            patch_by_path={
                "src/core/pillar1087_copy_variant.py": "@@ -1 +1 @@\n+helper = 1\n",
            },
        )
        assert report["requires_sync"] is False

    def test_copy_from_pillar_to_nonpillar_path_requires_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/history_variant.py"],
            name_status_lines=["C100\tsrc/core/pillar1087_sprint_cm_full_physics_parallel_execution.py\tsrc/core/history_variant.py"],
        )
        assert report["requires_sync"] is True
        assert report["reasons"] == ["copied pillar file with new identity src/core/history_variant.py"]

    def test_deleted_pillar_file_requires_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/pillar1121_copy.py"],
            name_status_lines=["D\tsrc/core/pillar1121_copy.py"],
            patch_by_path={
                "src/core/pillar1121_copy.py": (
                    "@@ -1 +0,0 @@\n"
                    '-PILLAR_STATUS: str = "PROMOTED"\n'
                )
            },
        )
        assert report["requires_sync"] is True
        assert report["reasons"] == ["deleted pillar file src/core/pillar1121_copy.py"]

    def test_deleted_same_identity_variant_without_metadata_change_does_not_require_sync(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/pillar1087_history_variant.py"],
            name_status_lines=["D\tsrc/core/pillar1087_history_variant.py"],
            patch_by_path={
                "src/core/pillar1087_history_variant.py": "@@ -1 +0,0 @@\n-helper = 1\n",
            },
        )
        assert report["requires_sync"] is False

    def test_duplicate_name_status_entries_do_not_duplicate_reasons(self):
        report = canonical_ledger_sync_requirement(
            changed_files=["src/core/pillar1121_copy.py"],
            name_status_lines=[
                "D\tsrc/core/pillar1121_copy.py",
                "D\tsrc/core/pillar1121_copy.py",
            ],
            patch_by_path={
                "src/core/pillar1121_copy.py": (
                    "@@ -1 +0,0 @@\n"
                    '-PILLAR_STATUS: str = "PROMOTED"\n'
                )
            },
        )
        assert report["matched_paths"] == ["src/core/pillar1121_copy.py"]
        assert report["reasons"] == ["deleted pillar file src/core/pillar1121_copy.py"]
