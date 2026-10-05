# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Owned adapter receipt/schema tests, not tests of the Lean exporter implementation."""

import copy
import json
import sys

import pytest

from tests.test_um_arts import arts_workspace as _arts_workspace
from TOOLS.um_arts import formal, lean_adapter
from TOOLS.um_arts.adapters import load_config
from TOOLS.um_arts.evidence import EvidenceError, write_json
from TOOLS.um_arts.process import execute

arts_workspace = _arts_workspace

REQUEST = {"modules": ["Fixture.Module"], "declarations": ["Fixture.clean", "Fixture.conditional"]}


def document():
    return {
        "schema_version": 1, "lean_version": "4.22.0-rc2", "modules": ["Fixture.Module"],
        "declarations": [
            {"name": "Fixture.clean", "statement": "True", "kind": "theorem", "axioms": [],
             "dependencies": ["True", "True.intro"], "checked": True},
            {"name": "Fixture.conditional", "statement": "True", "kind": "theorem",
             "axioms": ["Fixture.assumption"], "dependencies": ["Fixture.assumption"], "checked": True},
        ],
    }


def test_checked_metadata_retains_axioms_and_unresolved_correspondence():
    result = lean_adapter.decode(document(), REQUEST, "4.22.0-rc2")
    assert result["status"] == "inspected"
    assert result["all_requested_theorems_checked"]
    assert result["proof_claim"] is False
    assert result["correspondence"] == "UNRESOLVED"
    assert result["declarations"][0]["classification"] == "CHECKED_THEOREM_NO_AXIOMS_REPORTED"
    conditional = result["declarations"][1]
    assert conditional["classification"] == "CHECKED_THEOREM_WITH_REPORTED_AXIOMS"
    assert conditional["axioms"] == ["Fixture.assumption"]
    assert conditional["proof_claim"] is False


@pytest.mark.parametrize("mutation", [
    "schema", "schema_bool", "version", "modules_missing", "modules_extra",
    "declaration_missing", "declaration_extra", "declaration_duplicate",
    "declaration_order", "statement_missing", "checked_string", "axiom_checked",
    "sorry_checked", "dependency_sorry_checked", "axioms_duplicate", "dependencies_malformed",
])
def test_exporter_false_green_metadata_rejected(mutation):
    data = document()
    if mutation == "schema":
        data["schema_version"] = 2
    elif mutation == "schema_bool":
        data["schema_version"] = True
    elif mutation == "version":
        data["lean_version"] = "unrelated-version"
    elif mutation == "modules_missing":
        data["modules"] = []
    elif mutation == "modules_extra":
        data["modules"] += ["Unrelated.Module"]
    elif mutation == "declaration_missing":
        data["declarations"].pop()
    elif mutation == "declaration_extra":
        data["declarations"].append({**data["declarations"][-1], "name": "Unrelated.theorem"})
    elif mutation == "declaration_duplicate":
        data["declarations"].append(dict(data["declarations"][-1]))
    elif mutation == "declaration_order":
        data["declarations"].reverse()
    elif mutation == "statement_missing":
        data["declarations"][0]["statement"] = ""
    elif mutation == "checked_string":
        data["declarations"][0]["checked"] = "true"
    elif mutation == "axiom_checked":
        data["declarations"][0]["kind"] = "axiom"
    elif mutation == "sorry_checked":
        data["declarations"][0]["axioms"] = ["sorryAx"]
    elif mutation == "dependency_sorry_checked":
        data["declarations"][0]["dependencies"] = ["sorryAx"]
    elif mutation == "axioms_duplicate":
        data["declarations"][1]["axioms"] *= 2
    elif mutation == "dependencies_malformed":
        data["declarations"][0]["dependencies"] = "keyword proof success"
    with pytest.raises(EvidenceError):
        lean_adapter.decode(data, REQUEST, "4.22.0-rc2")


def test_sorry_and_non_theorem_declarations_are_not_promoted():
    data = document()
    data["declarations"][0]["axioms"] = ["sorryAx"]
    data["declarations"][0]["checked"] = False
    data["declarations"][1]["kind"] = "axiom"
    data["declarations"][1]["checked"] = False
    result = lean_adapter.decode(data, REQUEST)
    assert not result["all_requested_theorems_checked"]
    assert result["declarations"][0]["classification"] == "UNCHECKED_SORRY_DEPENDENCY"
    assert result["declarations"][1]["classification"] == "AXIOM_DECLARATION"
    assert result["proof_claim"] is False


@pytest.mark.parametrize("inspection", [
    {"modules": [], "declarations": ["Fixture.clean"]},
    {"modules": ["Fixture.Module"], "declarations": []},
    {"modules": ["Other.Module"], "declarations": ["Fixture.clean"]},
    {"modules": ["Fixture.Module"], "declarations": ["--unsafe"]},
    {"modules": ["Fixture.Module"], "declarations": ["Fixture.clean", "Fixture.clean"]},
    {"modules": ["Fixture.Module"], "declarations": ["Fixture.clean"], "hidden_option": True},
])
def test_inspection_config_requires_explicit_exact_scoped_requests(arts_workspace, inspection):
    (arts_workspace / "tests").mkdir()
    (arts_workspace / "lean4").mkdir()
    config = arts_workspace / "config.json"
    config.write_text(json.dumps({
        "adapter": "generic", "suites": [{"name": "unit", "paths": ["tests"]}],
        "lean": {"project": "lean4", "scope": "scoped", "targets": ["Fixture.Module"],
                 "inspection": inspection},
    }))
    with pytest.raises(EvidenceError):
        load_config(arts_workspace, config, "generic")


def test_unavailable_tools_block_inspection_without_commands(arts_workspace, monkeypatch):
    (arts_workspace / "lean4").mkdir()
    config = {"timeout_seconds": 1,
              "lean": {"scope": "scoped", "project": "lean4", "targets": ["Fixture.Module"],
                       "inspection": copy.deepcopy(REQUEST)}}
    monkeypatch.setattr(formal.shutil, "which", lambda name: None)
    monkeypatch.setattr(lean_adapter, "execute", lambda *args, **kwargs: pytest.fail("tools unavailable"))
    formal.build(arts_workspace, arts_workspace / "receipt", config)
    result = formal.evaluate_build(arts_workspace / "receipt", config["lean"], str(arts_workspace))
    assert result["status"] == "blocked"
    assert result["inspection"]["status"] == "blocked"
    assert result["inspection"]["declarations"] == []
    assert result["proof_claim"] is False


def test_mocked_typed_inspection_flow_and_offline_revalidation(arts_workspace, monkeypatch):
    # Protocol fixtures exercise our adapter only; no exporter/compiler is invoked.
    project = arts_workspace / "fixture-project"
    binary = project / ".lake/build/bin/um_arts_export"
    binary.parent.mkdir(parents=True)
    binary.write_text("owned adapter protocol fixture")
    binary.chmod(0o755)
    (project / "lean-toolchain").write_text("leanprover/lean4:v4.22.0-rc2\n")
    directory = arts_workspace / "receipt"
    calls = []

    def mock_execute(command, cwd, destination, timeout, **kwargs):
        calls.append(command)
        destination.mkdir(parents=True)
        process = {"command": command, "cwd": str(cwd), "returncode": 0,
                   "timed_out": False, "error": None, "seconds": 0.01}
        write_json(destination / "process.json", process)
        (destination / "output.log").write_text(
            json.dumps(document()) if destination.name == "export" else "build-only receipt")
        if kwargs.get("separate_stderr"):
            (destination / "stderr.log").write_text("")
        return process

    monkeypatch.setattr(lean_adapter, "execute", mock_execute)
    lean_adapter.inspect(project, directory, REQUEST, "/fixture/bin/lake", 1)
    assert len(calls) == 2
    assert calls[0] == ["/fixture/bin/lake", "build", "um_arts_export"]
    assert calls[1] == ["/fixture/bin/lake", "env", str(binary), "--module", "Fixture.Module",
                        "--decl", "Fixture.clean", "--decl", "Fixture.conditional"]
    monkeypatch.setattr(lean_adapter, "execute", lambda *args, **kwargs: pytest.fail("offline evaluation executed"))
    result = lean_adapter.evaluate(directory, REQUEST, str(project))
    assert result["status"] == "inspected"
    assert result["declarations"][1]["axioms"] == ["Fixture.assumption"]
    assert result["proof_claim"] is False
    data = document()
    data["declarations"].pop()
    (directory / "export/output.log").write_text(json.dumps(data))
    assert lean_adapter.evaluate(directory, REQUEST, str(project))["status"] == "blocked"


def test_keyword_output_cannot_replace_exported_json_receipt(arts_workspace):
    request = copy.deepcopy(REQUEST)
    lean_adapter.blocked(arts_workspace, request, "missing checked JSON")
    (arts_workspace / "output.log").write_text("theorem proof checked success")
    result = lean_adapter.evaluate(arts_workspace, request)
    assert result["status"] == "blocked"
    assert result["proof_claim"] is False


def test_build_success_remains_distinct_from_blocked_inspection(arts_workspace):
    lean = {"scope": "scoped", "project": "lean4", "targets": ["Fixture.Module"],
            "inspection": copy.deepcopy(REQUEST)}
    directory = arts_workspace / "receipt"
    write_json(directory / "request.json", lean)
    write_json(directory / "build.json", {
        "status": "built", "scope": "scoped", "targets": ["Fixture.Module"], "proof_claim": False})
    write_json(directory / "process.json", {
        "command": ["/fixture/bin/lake", "build", "Fixture.Module"],
        "cwd": str(arts_workspace / "lean4"), "returncode": 0, "timed_out": False, "error": None})
    lean_adapter.blocked(directory / "inspection", REQUEST, "exporter unavailable")
    result = formal.evaluate_build(directory, lean, str(arts_workspace))
    assert result["status"] == "built"
    assert result["inspection"]["status"] == "blocked"
    assert result["proof_claim"] is False


def test_json_stdout_is_not_contaminated_by_stderr(arts_workspace):
    receipt = execute(
        [sys.executable, "-c", "import sys;print('{\"schema_version\":1}');print('diagnostic',file=sys.stderr)"],
        arts_workspace, arts_workspace / "streams", 5, stream=False, separate_stderr=True)
    assert receipt["returncode"] == 0
    assert json.loads((arts_workspace / "streams/output.log").read_text()) == {"schema_version": 1}
    assert (arts_workspace / "streams/stderr.log").read_text().strip() == "diagnostic"
