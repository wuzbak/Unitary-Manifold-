# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Adversarial scanner coverage and real optional-tool integration."""

import json
import os
from pathlib import Path

import pytest
from TOOLS.um_arts.evidence import EvidenceError, write_json
from TOOLS.um_arts.scanning import inspect_scan, scan

from tests.test_um_arts import arts_workspace as _arts_workspace

arts_workspace = _arts_workspace


@pytest.fixture
def scan_workspace(arts_workspace):
    root = arts_workspace / "source"
    root.mkdir()
    (root / "a.py").write_text("x = 1\n")
    (root / "b.py").write_text("x = 2\n")
    binary = arts_workspace / "scanner"
    binary.write_text("#!/bin/sh\nexit 0\n")
    binary.chmod(0o755)
    rules = arts_workspace / "rules.yml"
    rules.write_text("rules: []\n")
    return root, binary, rules


def fake_execute(monkeypatch, *, omission=False, errors=None, findings=False, drift=False,
                 returncode=0, skipped_rules=None):
    invocations = []

    def execute(command, cwd, directory, timeout, environment, **kwargs):
        files = command[command.index("--") + 1:]
        invocations.append(files)
        assert "--disable-version-check" in command
        assert "--no-git-ignore" in command
        assert environment["SEMGREP_SEND_METRICS"] == "off"
        write_json(directory / "process.json", {
            "returncode": returncode, "timed_out": False, "error": None, "command": command,
        })
        results = [{"path": files[0], "check_id": "review", "start": {"line": 1}}] \
            if findings else []
        write_json(directory / "output.log", {
            "results": results, "errors": errors or [],
            "paths": {"scanned": files[:-1] if omission else files},
            "version": "test-scanner", "skipped_rules": skipped_rules or [],
        })
        if drift:
            (cwd / "a.py").write_text("x = 3\n")

    monkeypatch.setattr("TOOLS.um_arts.scanning.execute", execute)
    return invocations


def test_shards_exact_coverage_and_verified_report(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    calls = fake_execute(monkeypatch)
    result = scan(root, root.parent / "evidence", binary, rules, files_per_shard=1)
    assert calls == [["a.py"], ["b.py"]]
    assert result["status"] == "checked"
    assert result["selected"] == result["scanned"] == 2
    assert result["security_certified"] is False
    assert inspect_scan(Path(result["artifact"])) == result


@pytest.mark.parametrize("options", [
    {"omission": True}, {"errors": [{"type": "ParseError"}]}, {"returncode": 2},
    {"skipped_rules": ["unsupported"]},
])
def test_zero_findings_cannot_hide_missing_coverage(scan_workspace, monkeypatch, options):
    root, binary, rules = scan_workspace
    fake_execute(monkeypatch, **options)
    result = scan(root, root.parent / "evidence", binary, rules)
    assert result["status"] == "blocked"
    assert result["errors"]


def test_findings_are_review_candidates_not_vulnerability_claims(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    fake_execute(monkeypatch, findings=True)
    result = scan(root, root.parent / "evidence", binary, rules)
    assert result["status"] == "findings"
    assert result["findings"][0]["review_required"] is True
    assert not result["security_certified"]


def test_only_unchanged_shards_reused_after_file_change(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    calls = fake_execute(monkeypatch)
    old = root.parent / "old"
    scan(root, old, binary, rules, files_per_shard=1)
    (root / "b.py").write_text("x = 4\n")
    calls.clear()
    result = scan(root, root.parent / "new", binary, rules, files_per_shard=1, previous=old)
    assert calls == [["b.py"]]
    assert [s["reused"] for s in result["shards"]] == [True, False]
    assert result["status"] == "checked"


def test_source_unstable_shards_are_not_reused(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    fake_execute(monkeypatch, drift=True)
    old = root.parent / "old"
    assert scan(root, old, binary, rules)["status"] == "blocked"
    calls = fake_execute(monkeypatch)
    result = scan(root, root.parent / "new", binary, rules, previous=old)
    assert calls
    assert not any(s["reused"] for s in result["shards"])


def test_rule_changes_invalidate_all_prior_shards(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    calls = fake_execute(monkeypatch)
    old = root.parent / "old"
    scan(root, old, binary, rules, files_per_shard=1)
    rules.write_text("rules: []\n# changed\n")
    calls.clear()
    result = scan(root, root.parent / "new", binary, rules, files_per_shard=1, previous=old)
    assert calls == [["a.py"], ["b.py"]]
    assert not any(s["reused"] for s in result["shards"])


def test_empty_scope_is_not_a_clean_security_result(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    (root / "a.py").unlink()
    (root / "b.py").unlink()
    fake_execute(monkeypatch)
    result = scan(root, root.parent / "evidence", binary, rules)
    assert result["status"] == "blocked"
    assert result["selected"] == result["scanned"] == 0


def test_oversize_missing_binary_and_unsafe_paths_fail_closed(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    fake_execute(monkeypatch)
    result = scan(root, root.parent / "oversize", binary, rules, max_file_bytes=1)
    assert result["status"] == "blocked"
    assert result["oversized"] == ["a.py", "b.py"]
    for options in ({"paths": ["../source"]}, {"files_per_shard": True},
                    {"timeout_seconds": float("nan")}, {"paths": ["missing"]}):
        with pytest.raises(EvidenceError):
            scan(root, root.parent / "other", binary, rules, **options)
    with pytest.raises(EvidenceError):
        scan(root, root / "inside", binary, rules)


def test_modified_artifact_is_rejected(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    fake_execute(monkeypatch)
    output = root.parent / "evidence"
    scan(root, output, binary, rules)
    (output / "scan.json").write_text("{}")
    with pytest.raises(EvidenceError):
        inspect_scan(output)


def test_nested_reuse_output_cannot_mutate_previous_evidence(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    fake_execute(monkeypatch)
    old = root.parent / "old"
    scan(root, old, binary, rules)
    with pytest.raises(EvidenceError, match="prior evidence"):
        scan(root, old / "next", binary, rules, previous=old)
    assert not (old / "next").exists()
    assert inspect_scan(old)["status"] == "checked"


def test_unreadable_source_directory_cannot_disappear_from_coverage(scan_workspace, monkeypatch):
    root, binary, rules = scan_workspace
    fake_execute(monkeypatch)
    directory = root / "inaccessible"
    directory.mkdir()
    (directory / "secret.py").write_text("x = 1\n")
    directory.chmod(0)
    try:
        if os.access(directory, os.R_OK):
            pytest.skip("Permissions cannot restrict this test process")
        with pytest.raises(EvidenceError, match="traversal"):
            scan(root, root.parent / "evidence", binary, rules)
        assert not (root.parent / "evidence").exists()
    finally:
        directory.chmod(0o755)


def test_real_optional_opengrep_capture(arts_workspace):
    tool = os.environ.get("UM_ARTS_OPENGREP")
    if not tool:
        pytest.skip("Set UM_ARTS_OPENGREP to an installed optional scanner")
    root = arts_workspace / "source"
    root.mkdir()
    (root / "example.py").write_text("import subprocess\nsubprocess.run('echo x', shell=True)\n")
    rules = Path(__file__).resolve().parents[1] / (
        "12-AZ-IP/26-um-arts/um_arts/examples/python-review.yml")
    result = scan(root, arts_workspace / "scan", Path(tool), rules)
    assert result["status"] == "findings", json.dumps(result)
    assert result["selected"] == result["scanned"] == 1
    assert result["source_stable"]
    assert result["findings"][0]["line"] == 2
