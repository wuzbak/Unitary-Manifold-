# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Regression coverage using real local Git repositories."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT))

from az_research_debt_tracker import ingest_git_debt
from az_research_debt_tracker import git_ingest


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True,
    ).stdout.decode().strip()


@pytest.fixture
def repo():
    path = PRODUCT_ROOT / (".git-ingest-test-" + uuid.uuid4().hex)
    path.mkdir()
    try:
        git(path, "init", "-q")
        git(path, "config", "user.name", "Regression Test")
        git(path, "config", "user.email", "test@example.invalid")
        git(path, "config", "commit.gpgsign", "false")
        (path / "logic.py").write_text(
            "# TODO: verify uncertainty budget\n"
            "# FIXME: preserve missing measurements\n"
            "message = 'TODO not a comment'\n",
        )
        git(path, "add", ".")
        git(path, "commit", "-qm", "record real source debt")
        yield path
    finally:
        shutil.rmtree(path)


def test_real_commit_provenance_and_actionable_items(repo):
    report = ingest_git_debt(repo)
    assert report["health_score"]["n_open"] == 2
    assert report["health_score"]["n_closed"] == 0
    assert report["coverage"]["source_files_scanned"] == 1
    first, second = report["items"]
    assert first["description"] == "verify uncertainty budget"
    assert first["owner_ref"] == "logic.py:1"
    assert second["severity"] == "significant"
    evidence = first["evidence"]
    assert evidence["commit"] == git(repo, "rev-parse", "HEAD")
    assert evidence["blob"] == git(repo, "rev-parse", "HEAD:logic.py")
    assert evidence["source_line"] == "# TODO: verify uncertainty budget"
    assert evidence["next_action"]
    assert report == ingest_git_debt(repo)


def test_ignores_dirty_staged_and_untracked_source(repo):
    expected = ingest_git_debt(repo)
    (repo / "logic.py").write_text("# FIXME: staged but not committed\n")
    git(repo, "add", "logic.py")
    (repo / "new.py").write_text("# TODO: untracked\n")
    assert ingest_git_debt(repo) == expected


def test_revision_is_pinned_and_removal_is_not_claimed_closure(repo):
    initial = git(repo, "rev-parse", "HEAD")
    (repo / "logic.py").write_text("value = 1\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "remove comments")
    assert len(ingest_git_debt(repo, initial)["items"]) == 2
    current = ingest_git_debt(repo)
    assert current["items"] == []
    assert current["health_score"]["n_closed"] == 0


def test_special_paths_binary_symlinks_and_unsupported_files(repo):
    name = "source:odd\nname.ts"
    (repo / name).write_text(" // TODO: triage owner\n /* FIXME: data loss */\n")
    (repo / "binary.py").write_bytes(b"# TODO hidden\0\n")
    (repo / "latin.py").write_bytes(b"# TODO: \xff\n")
    (repo / "notes.md").write_text("# TODO: not source\n")
    (repo / "link.py").symlink_to("logic.py")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "add edge cases")
    report = ingest_git_debt(repo)
    assert report["coverage"] == {
        "source_files_scanned": 2, "binary_or_non_utf8_skipped": 2,
    }
    items = [item for item in report["items"] if item["evidence"]["path"] == name]
    assert [item["description"] for item in items] == ["triage owner", "data loss"]
    assert items[0]["item_id"] == "git-" + hashlib.sha256(
        f"{name}\0{1}\0TODO".encode(),
    ).hexdigest()
    assert json.loads(json.dumps(report)) == report


@pytest.mark.parametrize("revision", ["missing-ref", "--help", "HEAD:logic.py"])
def test_invalid_revision_is_error_not_empty_health(repo, revision):
    with pytest.raises(ValueError, match="Git failed"):
        ingest_git_debt(repo, revision)


def test_non_repository_rejected():
    with pytest.raises(ValueError, match="Git failed"):
        ingest_git_debt("/dev/null")


@pytest.mark.parametrize("error, message", [
    (FileNotFoundError("git"), "Git executable is required"),
    (subprocess.TimeoutExpired("git", 60), "Git command timed out"),
])
def test_tooling_failures_are_explicit(monkeypatch, error, message):
    def fail(*args, **kwargs):
        raise error
    monkeypatch.setattr(git_ingest.subprocess, "run", fail)
    with pytest.raises(ValueError, match=message):
        ingest_git_debt(PRODUCT_ROOT)


def test_marker_boundaries_and_empty_description(repo):
    (repo / "logic.py").write_text(
        "# TODO\n# TODOUBLE: not a marker\nx = 1 # FIXME: inline\n# todo: lowercase\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "marker grammar")
    items = ingest_git_debt(repo)["items"]
    assert len(items) == 1
    assert items[0]["description"] == "TODO needs triage"


def cli(*args):
    return subprocess.run(
        [sys.executable, str(PRODUCT_ROOT / "run.py"), *map(str, args)],
        capture_output=True, text=True,
    )


def test_cli_persists_report_and_debt_gate(repo):
    output = repo / "inventory.json"
    result = cli("--git-repo", repo, "--output", output, "--fail-on-debt")
    assert result.returncode == 1
    report = json.loads(output.read_text())
    assert report == json.loads(result.stdout)
    assert len(report["items"]) == 2
    assert cli("--git-repo", repo).returncode == 0


def test_cli_empty_inventory_passes_gate(repo):
    (repo / "logic.py").write_text("value = 1\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "no markers")
    result = cli("--git-repo", repo, "--fail-on-debt")
    assert result.returncode == 0
    assert json.loads(result.stdout)["items"] == []


def test_cli_error_preserves_previous_report(repo):
    output = repo / "inventory.json"
    output.write_text("previous report")
    result = cli("--git-repo", repo, "--revision", "invalid", "--output", output)
    assert result.returncode == 2
    assert "Git failed" in result.stderr
    assert not result.stdout
    assert output.read_text() == "previous report"


def test_cli_reports_output_errors(repo):
    result = cli("--git-repo", repo, "--output", repo / "missing" / "report.json")
    assert result.returncode == 2
    assert "research-debt tracker:" in result.stderr
    assert not result.stdout


@pytest.mark.parametrize("args", [
    ("--fail-on-debt",),
    ("--revision", "HEAD~1"),
    ("--serve", "--git-repo", "."),
])
def test_cli_rejects_incompatible_options(args):
    assert cli(*args).returncode == 2
