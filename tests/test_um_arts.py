# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Adversarial evidence reconciliation and configuration boundaries."""

import json
import shutil
import uuid
from copy import deepcopy
from pathlib import Path

import pytest

from TOOLS.um_arts.adapters import load_config, selection_policy
from TOOLS.um_arts.engine import balanced_jobs
from TOOLS.um_arts.evidence import (
    EvidenceError,
    contained,
    read_json,
    seal,
    verify_seal,
    write_json,
)
from TOOLS.um_arts.formal import capture, coverage, evaluate_build
from TOOLS.um_arts.reconcile import check_events
from TOOLS.um_arts.reporting import dashboard


@pytest.fixture
def arts_workspace():
    # Keep all test artifacts inside the repository, never in system temp paths.
    directory = Path.cwd() / ".um-arts-test-work" / uuid.uuid4().hex
    directory.mkdir(parents=True)
    yield directory
    for current in directory.rglob("*"):
        if not current.is_symlink():
            current.chmod(0o755 if current.is_dir() else 0o644)
    directory.chmod(0o755)
    shutil.rmtree(directory)


def events():
    node = "tests/test_example.py::test_ok"
    return {
        "version": "1", "nonce": "nonce", "selected": [node], "deselected": [],
        "partition_excluded": [], "collection": [], "internal_errors": [], "exitstatus": 0,
        "reports": [{"nodeid": node, "when": phase, "outcome": "passed", "duration": 0.1,
                     "wasxfail": None} for phase in ["setup", "call", "teardown"]],
    }


def process():
    return {"returncode": 0, "error": None, "timed_out": False}


def test_exact_evidence_green():
    evidence = events()
    result = check_events(evidence, process(), "nonce", evidence["selected"])
    assert result["status"] == "passed"
    assert result["counts"] == {"passed": 1}


@pytest.mark.parametrize("outcome,expected", [("passed", "xpassed"), ("skipped", "xfailed")])
def test_reasonless_xfail_metadata_is_not_treated_as_absent(outcome, expected):
    receipt = events()
    receipt["reports"][1].update(outcome=outcome, wasxfail="")
    result = check_events(receipt, process(), "nonce", receipt["selected"])
    assert result["counts"] == {expected: 1}
    assert result["status"] == ("blocked" if outcome == "passed" else "passed")


@pytest.mark.parametrize("mutation", [
    "missing_node", "extra_node", "duplicate_node", "missing_phase", "duplicate_phase",
    "wrong_nonce", "wrong_version", "nonzero_exit", "mismatched_exit", "timeout",
    "internal_error", "collection_error", "setup_failure", "teardown_failure",
    "call_failure", "empty", "unknown_phase", "unknown_outcome", "negative_duration",
    "nan_duration", "deselection_overlap", "duplicate_deselection", "unexpected_xpass",
    "setup_skip_with_call", "teardown_skip", "successful_setup_without_call",
])
def test_false_greens_fail_closed(mutation):
    receipt, proc = events(), process()
    expected = list(receipt["selected"])
    if mutation == "missing_node":
        receipt["reports"] = []
    elif mutation == "extra_node":
        receipt["reports"].append({**receipt["reports"][1], "nodeid": "evil::extra"})
    elif mutation == "duplicate_node":
        receipt["selected"] *= 2
    elif mutation == "missing_phase":
        receipt["reports"].pop()
    elif mutation == "duplicate_phase":
        receipt["reports"].append(dict(receipt["reports"][-1]))
    elif mutation == "wrong_nonce":
        receipt["nonce"] = "different"
    elif mutation == "wrong_version":
        receipt["version"] = "0"
    elif mutation == "nonzero_exit":
        proc["returncode"] = receipt["exitstatus"] = 1
    elif mutation == "mismatched_exit":
        proc["returncode"] = 1
    elif mutation == "timeout":
        proc["timed_out"] = True
    elif mutation == "internal_error":
        receipt["internal_errors"] = ["internal exception"]
    elif mutation == "collection_error":
        receipt["collection"] = [{"nodeid": "broken.py", "outcome": "failed"}]
    elif mutation in {"setup_failure", "call_failure", "teardown_failure"}:
        slot = {"setup_failure": 0, "call_failure": 1, "teardown_failure": 2}[mutation]
        receipt["reports"][slot]["outcome"] = "failed"
    elif mutation == "empty":
        receipt["selected"] = receipt["reports"] = []
        expected = []
    elif mutation == "unknown_phase":
        receipt["reports"][1]["when"] = "unexpected"
    elif mutation == "unknown_outcome":
        receipt["reports"][1]["outcome"] = "unknown"
    elif mutation == "negative_duration":
        receipt["reports"][1]["duration"] = -1
    elif mutation == "nan_duration":
        receipt["reports"][1]["duration"] = float("nan")
    elif mutation == "deselection_overlap":
        receipt["deselected"] = expected
    elif mutation == "duplicate_deselection":
        receipt["deselected"] = ["other"] * 2
    elif mutation == "unexpected_xpass":
        receipt["reports"][1]["wasxfail"] = "expected fail"
    elif mutation == "setup_skip_with_call":
        receipt["reports"][0]["outcome"] = "skipped"
    elif mutation == "teardown_skip":
        receipt["reports"][2]["outcome"] = "skipped"
    elif mutation == "successful_setup_without_call":
        receipt["reports"].pop(1)
    result = check_events(receipt, proc, "nonce", expected)
    assert result["status"] == "blocked", mutation
    assert result["errors"]


@pytest.mark.parametrize("phase,xfail", [("setup", False), ("setup", True),
                                       ("call", False), ("call", True)])
def test_skip_and_xfail_accounting(phase, xfail):
    receipt = events()
    slot = 0 if phase == "setup" else 1
    receipt["reports"][slot]["outcome"] = "skipped"
    receipt["reports"][slot]["wasxfail"] = "expected" if xfail else None
    if phase == "setup":
        receipt["reports"].pop(1)
    result = check_events(receipt, process(), "nonce", receipt["selected"])
    assert result["status"] == "passed"
    assert result["counts"] == {"xfailed" if xfail else "skipped": 1}


def test_collection_only_receipt_with_execution_is_not_green():
    receipt = events()
    assert check_events(receipt, process(), "nonce", receipt["selected"],
                        collection=True)["status"] == "blocked"


def test_conservative_changed_mode():
    assert selection_policy("changed")["effective_mode"] == "full"
    assert selection_policy("changed")["fallback_reason"]


def test_default_um_adapter_targets_all_three_existing_lanes():
    config = load_config(Path(__file__).resolve().parents[1])
    assert [suite["name"] for suite in config["suites"]] == ["physics", "recycling", "pentad"]
    assert config["suites"][-1]["paths"] == ["5-GOVERNANCE/Unitary Pentad"]
    assert config["suites"][-1]["serial"]
    assert config["suites"][-1]["requires"] == ["recycling"]


def test_duration_balancing_and_fixture_locality():
    suites = [{"name": "s", "serial": False,
               "nodes": ["a.py::x", "a.py::y", "b.py::x", "c.py::x"]}]
    jobs = balanced_jobs(suites, 2, {"a.py::x": 6, "a.py::y": 4, "b.py::x": 9, "c.py::x": 1})
    assert [job["estimated_seconds"] for job in jobs] == [10, 10]
    assert any(set(job["nodes"]) == {"a.py::x", "a.py::y"} for job in jobs)
    suites[0]["serial"] = True
    assert len(balanced_jobs(suites, 32, {})) == 1


@pytest.mark.parametrize("relative", ["../secret", "/absolute", "x/../../secret", r"x\secret"])
def test_artifact_traversal_rejected(arts_workspace, relative):
    with pytest.raises(EvidenceError):
        contained(arts_workspace, relative, must_exist=False)


def test_symlinks_and_manifest_tamper_rejected(arts_workspace):
    target = arts_workspace / "safe.json"
    write_json(target, {"value": 1})
    seal(arts_workspace)
    assert verify_seal(arts_workspace)["files"]
    target.write_text('{"value":2}')
    with pytest.raises(EvidenceError, match="hash mismatch"):
        verify_seal(arts_workspace)
    target.write_text(json.dumps({"value": 1}, separators=(",", ":")))
    link = arts_workspace / "link"
    link.symlink_to(target)
    with pytest.raises(EvidenceError, match="Symlink"):
        contained(arts_workspace, "link")
    with pytest.raises(EvidenceError):
        verify_seal(arts_workspace)


def test_manifest_missing_and_unlisted_files_rejected(arts_workspace):
    write_json(arts_workspace / "safe.json", {"value": 1})
    seal(arts_workspace)
    (arts_workspace / "extra").write_text("unlisted")
    with pytest.raises(EvidenceError, match="unexpected"):
        verify_seal(arts_workspace)
    (arts_workspace / "extra").unlink()
    (arts_workspace / "safe.json").unlink()
    with pytest.raises(EvidenceError, match="Missing"):
        verify_seal(arts_workspace)


@pytest.mark.parametrize("payload", ['{"duplicate":1,"duplicate":2}', '{"duration":NaN}'])
def test_ambiguous_json_receipts_rejected(arts_workspace, payload):
    path = arts_workspace / "ambiguous.json"
    path.write_text(payload)
    with pytest.raises(EvidenceError):
        read_json(path)


@pytest.mark.parametrize("override", [
    {"workers": 0}, {"workers": 33}, {"workers": True}, {"timeout_seconds": -1},
    {"timeout_seconds": float("inf")}, {"pytest_args": ["-n", "auto"]},
    {"pytest_args": ["--numprocesses=2"]}, {"pytest_args": ["-p", "xdist"]},
    {"pytest_args": ["-o", "addopts=-n auto"]},
    {"pytest_args": ["--rootdir=/outside"]}, {"unknown_setting": True},
    {"suites": [{"name": "bad/name", "paths": ["tests"]}]},
    {"suites": [{"name": "s", "paths": ["../outside"]}]},
    {"suites": [{"name": "s", "paths": ["tests"], "requires": ["unknown"]}]},
    {"suites": [{"name": "s", "paths": ["tests"], "requires": ["s"]}]},
])
def test_invalid_or_unbounded_config_rejected(arts_workspace, override):
    (arts_workspace / "tests").mkdir()
    config = {"adapter": "generic", "suites": [{"name": "s", "paths": ["tests"]}], **override}
    path = arts_workspace / "config.json"
    # allow_nan here exercises the strict finite validation of an imported JSON value.
    path.write_text(json.dumps(config))
    with pytest.raises(EvidenceError):
        load_config(arts_workspace, path, "generic")


def test_formal_build_receipt_is_never_a_correspondence_proof():
    snapshot = {"status": "captured", "units": [
        {"unit_id": "u", "proof_class": "LEAN_CONDITIONAL_WITH_NAMED_AXIOMS",
         "lean": {"build_target": "UnitaryManifold.A"},
         "python": {"tests": ["tests/test_a.py"]},
         "translation_contract": {"normalization_contract": {"domains": ["real"]},
                                  "certificate_contract": {
                                      "required_certificate_types": ["RESIDUAL"]}}}]}
    build = {"status": "built", "scope": "scoped", "targets": ["UnitaryManifold.A"]}
    result = coverage(snapshot, build, ["tests/test_a.py::test_p"])
    assert result["units"][0]["lean_build_covered"]
    assert result["units"][0]["declared_proof_class"] == "LEAN_CONDITIONAL_WITH_NAMED_AXIOMS"
    assert result["units"][0]["correspondence"] == "UNRESOLVED"
    assert result["units"][0]["certificate_requirements"] == ["RESIDUAL"]
    assert result["units"][0]["normalization_contract"] == {"domains": ["real"]}
    assert result["proof_claim"] is False
    build["targets"] = ["Other.Module"]
    assert not coverage(snapshot, build, [])["units"][0]["lean_build_covered"]


def test_fake_keyword_build_success_cannot_certify(arts_workspace):
    lean = {"scope": "full", "targets": [], "project": "lean4"}
    write_json(arts_workspace / "request.json", lean)
    write_json(arts_workspace / "build.json", {
        "status": "built", "scope": "full", "targets": [], "proof_claim": False})
    (arts_workspace / "output.log").write_text("theorem proof success QED")
    result = evaluate_build(arts_workspace, lean)
    assert result["status"] == "blocked"
    assert result["proof_claim"] is False


def test_existing_um_registry_and_schema_are_snapshotted(arts_workspace):
    result = capture(Path(__file__).resolve().parents[1], arts_workspace,
                     {"adapter": "um", "timeout_seconds": 30})
    assert result["status"] == "captured"
    assert result["units"]
    assert result["rows"]
    assert result["schema"]["float_policy"]["raw_floats_do_not_promote"]
    assert result["correspondence"] == "UNRESOLVED"


def test_dashboard_html_is_escaped_and_contains_same_evaluation():
    data = {"status": "blocked", "attempt_id": "<script>alert(1)</script>",
            "suites": {"<img onerror='evil()'>": "blocked"}, "errors": ["&unsafe"]}
    rendered = dashboard(deepcopy(data))
    assert "<script>" not in rendered
    assert "<img " not in rendered
    assert "&lt;script&gt;" in rendered
    assert "default-src 'none'" in rendered
    assert "&amp;unsafe" in rendered
