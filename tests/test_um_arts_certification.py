# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Certification never silently combines unrelated or collection-only receipts."""

import json
import sys
from copy import deepcopy

import pytest
from TOOLS.um_arts.capture import capture_command
from TOOLS.um_arts.certification import certify
from TOOLS.um_arts.evidence import EvidenceError


def receipt(node="test.py::test_ok", **changes):
    result = {
        "status": "passed", "test_gate": True,
        "evidence_class": "STRUCTURED_PYTEST_EXECUTION",
        "command": ["python", "-m", "pytest", "tests"],
        "compatibility": dict.fromkeys(["source", "environment", "engine", "git"], "hash"),
        "provenance": {"root": "/repository"},
        "jobs": {"captured": {"selected": [node]}}, "counts": {"passed": 1},
        "deselected": 0, "collection_skips": [], "attempt_id": node,
    }
    result.update(changes)
    return result


def manifest(tmp_path, monkeypatch, receipts):
    checks = []
    for index, row in enumerate(receipts):
        name = f"check-{index}"
        checks.append({"id": name, "artifact": name, "command": row["command"],
                       "kind": "pytest", "scope": f"suite {index}"})
    path = tmp_path / "required.json"
    path.write_text(json.dumps({"label": "declared scope", "checks": checks}))
    monkeypatch.setattr("TOOLS.um_arts.certification.evaluate_capture",
                        lambda artifact: deepcopy(receipts[int(artifact.name.split("-")[1])]))
    return path


def test_compatible_disjoint_receipts_aggregate_without_execution(tmp_path, monkeypatch):
    path = manifest(tmp_path, monkeypatch, [receipt(), receipt("other.py::test_ok")])
    result = certify(path)
    assert result["status"] == "passed"
    assert result["counts"] == {"passed": 2}
    assert result["unique_test_identities"] == 2
    assert result["proof_claim"] is False
    assert "Only checks explicitly" in result["coverage_scope"]


@pytest.mark.parametrize("change", ["source", "environment", "engine", "git", "root",
                                  "collection", "failed", "command", "overlap"])
def test_incompatible_or_nonexecuted_checks_block_certification(tmp_path, monkeypatch, change):
    second = receipt("other.py::test_ok")
    if change in {"source", "environment", "engine", "git"}:
        second["compatibility"][change] = "different"
    elif change == "root":
        second["provenance"]["root"] = "/other"
    elif change == "collection":
        second.update(status="collection_passed", test_gate=False,
                      evidence_class="STRUCTURED_PYTEST_COLLECTION")
    elif change == "failed":
        second.update(status="blocked", test_gate=False)
    elif change == "overlap":
        second["jobs"]["captured"]["selected"] = ["test.py::test_ok"]
    path = manifest(tmp_path, monkeypatch, [receipt(), second])
    if change == "command":
        data = json.loads(path.read_text())
        data["checks"][1]["command"] = ["different"]
        path.write_text(json.dumps(data))
    result = certify(path)
    assert result["status"] == "blocked"
    assert result["errors"]


def test_missing_required_artifact_is_blocked(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({
        "label": "missing", "checks": [
            {"id": "required", "artifact": "missing", "command": ["python", "VERIFY.py"],
             "kind": "command", "scope": "isolated verification"}]}))
    assert certify(path)["status"] == "blocked"


def test_artifact_path_escape_is_rejected(tmp_path, monkeypatch):
    path = manifest(tmp_path, monkeypatch, [receipt()])
    data = json.loads(path.read_text())
    data["checks"][0]["artifact"] = "../outside"
    path.write_text(json.dumps(data))
    with pytest.raises(EvidenceError, match="Unsafe"):
        certify(path)


def test_actual_captured_checks_produce_a_declared_scope_certificate(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "test_first.py").write_text("def test_first(): assert True\n")
    (root / "test_second.py").write_text("def test_second(): assert True\n")
    checks = []
    for filename in ["test_first.py", "test_second.py"]:
        command = [sys.executable, "-m", "pytest", filename, "-q"]
        artifact = tmp_path / filename
        result = capture_command(command, artifact, root)
        assert result["status"] == "passed", result["errors"]
        checks.append({"id": filename, "artifact": filename, "command": command,
                       "kind": "pytest", "scope": filename})
    command = [sys.executable, "-c", "assert 2 + 2 == 4"]
    result = capture_command(command, tmp_path / "arithmetic", root)
    assert result["status"] == "command_passed", result
    checks.append({"id": "arithmetic", "artifact": "arithmetic", "command": command,
                   "kind": "command", "scope": "declared executable assertion, not formal proof"})
    path = tmp_path / "certificate.json"
    path.write_text(json.dumps({"label": "fixture declared checks", "checks": checks}))
    result = certify(path)
    assert result["status"] == "passed", result
    assert result["counts"] == {"passed": 2}
    assert result["unique_test_identities"] == 2
    assert len(result["checks"]) == 3
