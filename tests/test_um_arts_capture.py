# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Capture existing CI test invocations without overlapping execution."""

import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from TOOLS.um_arts.capture import _serial_pytest_arguments, evaluate_report
from TOOLS.um_arts.capture import capture_command as capture_existing_command
from TOOLS.um_arts.engine import import_artifact, resume
from TOOLS.um_arts.evidence import EvidenceError
from TOOLS.um_arts.reporting import report

from tests.test_um_arts import arts_workspace as _arts_workspace
from tests.test_um_arts import events
from TOOLS.um_arts import pytest_plugin as plugin

arts_workspace = _arts_workspace


def capture_command(workspace, *extra):
    root = workspace / "capture-repository"
    root.mkdir()
    (root / "pytest.ini").write_text("[pytest]\n")
    (root / "test_capture.py").write_text(
        "import pytest\n"
        "@pytest.mark.parametrize('n', [1,2])\n"
        "def test_pass(n): assert n > 0\n"
        "@pytest.mark.skip(reason='honest skip')\n"
        "def test_skip(): pass\n"
        "@pytest.mark.xfail(reason='honest xfail')\n"
        "def test_xfail(): assert False\n")
    destination = workspace / "external.json"
    env = dict(os.environ)
    env.pop("UM_ARTS_RECEIPT", None)
    env.pop("UM_ARTS_SELECTION", None)
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("PYTEST_PLUGINS", None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["UM_ARTS_PYTEST_REPORT"] = str(destination)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    command = [sys.executable, "-m", "pytest", "-p", "TOOLS.um_arts.pytest_plugin",
               "--rootdir", str(root), "--confcutdir", str(root),
               "--basetemp", str(workspace / "scratch"), "-q", *extra]
    return command, env, root, destination


def test_external_existing_pytest_invocation_emits_and_evaluates_receipt(arts_workspace, monkeypatch):
    command, env, root, path = capture_command(arts_workspace)
    completed = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True,
                               check=False, timeout=30)
    assert completed.returncode == 0, completed.stderr
    receipt = json.loads(path.read_text())
    assert receipt["selected"] == [
        "test_capture.py::test_pass[1]", "test_capture.py::test_pass[2]",
        "test_capture.py::test_skip", "test_capture.py::test_xfail"]
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: pytest.fail("capture executed a command"))
    result = evaluate_report(path, returncode=completed.returncode)
    assert result["status"] == "passed"
    assert result["counts"] == {"passed": 2, "skipped": 1, "xfailed": 1}
    assert result["executed_commands"] is False
    assert result["evidence_class"] == "RAW_STRUCTURED_PYTEST_RECEIPT"
    assert result["sealed"] is False
    assert result["proof_claim"] is False
    assert evaluate_report(path, returncode=1)["status"] == "blocked"
    assert evaluate_report(path, returncode=0, timed_out=True)["status"] == "blocked"
    assert evaluate_report(path, returncode=0, expected_nodeids=["missing"])["status"] == "blocked"


def test_external_collection_only_receipt(arts_workspace):
    command, env, root, path = capture_command(arts_workspace, "--collect-only")
    completed = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True,
                               check=False, timeout=30)
    assert completed.returncode == 0
    result = evaluate_report(path, returncode=0, collection_only=True)
    assert result["status"] == "passed"
    assert result["counts"] == {}
    assert evaluate_report(path, returncode=0, collection_only=False)["status"] == "blocked"


def test_capture_missing_file_is_not_a_green_zero_exit(arts_workspace):
    result = evaluate_report(arts_workspace / "missing.json", returncode=0)
    assert result["status"] == "blocked"


def test_capture_cli_evaluates_existing_receipt(arts_workspace):
    command, env, root, path = capture_command(arts_workspace)
    completed = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True,
                               check=False, timeout=30)
    assert completed.returncode == 0
    evaluated = subprocess.run(
        [sys.executable, "-m", "TOOLS.um_arts", "capture", "--report", str(path), "--returncode", "0"],
        capture_output=True, text=True, check=False, timeout=30)
    assert evaluated.returncode == 0, evaluated.stderr
    assert json.loads(evaluated.stdout)["counts"]["passed"] == 2


def xdist_events():
    data = events()
    data["root"] = "/repository"
    data["collection_only"] = False
    worker = {key: copy.deepcopy(data[key]) for key in [
        "version", "nonce", "root", "selected", "deselected", "partition_excluded",
        "collection", "internal_errors"]}
    data["xdist"] = {
        "enabled": True, "numprocesses": 2, "distribution": "load",
        "worker_collections": {"gw0": list(data["selected"]), "gw1": list(data["selected"])},
        "worker_receipts": {"gw0": copy.deepcopy(worker), "gw1": copy.deepcopy(worker)},
        "worker_errors": [],
    }
    return data


@pytest.mark.parametrize("mutation", [
    None, "missing_worker_receipt", "worker_mismatch", "duplicate_identity", "crash",
    "worker_nonce", "deselected_mismatch", "collection_skip_mismatch", "duplicate_phase", "missing_phase",
])
def test_xdist_evidence_reconciliation_without_installed_xdist(arts_workspace, mutation):
    data = xdist_events()
    if mutation == "missing_worker_receipt":
        del data["xdist"]["worker_receipts"]["gw1"]
    elif mutation == "worker_mismatch":
        data["xdist"]["worker_collections"]["gw1"] = ["other"]
    elif mutation == "duplicate_identity":
        data["xdist"]["worker_collections"]["gw0"] *= 2
    elif mutation == "crash":
        data["xdist"]["worker_errors"] = [{"worker": "gw0", "error": "crashed"}]
    elif mutation == "worker_nonce":
        data["xdist"]["worker_receipts"]["gw1"]["nonce"] = "other"
    elif mutation == "deselected_mismatch":
        data["xdist"]["worker_receipts"]["gw1"]["deselected"] = ["extra"]
    elif mutation == "collection_skip_mismatch":
        data["xdist"]["worker_receipts"]["gw1"]["collection"] = [
            {"nodeid": "optional.py", "outcome": "skipped", "detail": "worker-specific skip"}]
    elif mutation == "duplicate_phase":
        data["reports"] += list(data["reports"])
    elif mutation == "missing_phase":
        data["reports"].pop()
    path = arts_workspace / "workers.json"
    path.write_text(json.dumps(data))
    result = evaluate_report(path, returncode=0)
    assert result["status"] == ("passed" if mutation is None else "blocked")


def test_xdist_hooks_transport_collection_and_never_write_worker_report(arts_workspace, monkeypatch):
    master = xdist_events()
    master["xdist"]["worker_collections"] = {}
    master["xdist"]["worker_receipts"] = {}
    monkeypatch.setattr(plugin, "_data", master)
    node = SimpleNamespace(workerinput={"workerid": "gw0"}, workeroutput={})
    plugin.pytest_configure_node(node)
    assert node.workerinput["um_arts_nonce"] == master["nonce"]
    plugin.pytest_xdist_node_collection_finished(node, master["selected"])
    worker_config = SimpleNamespace(workerinput=node.workerinput, workeroutput={})
    plugin.pytest_sessionfinish(SimpleNamespace(config=worker_config), 0)
    assert worker_config.workeroutput["um_arts_collection"]["selected"] == master["selected"]
    node.workeroutput = worker_config.workeroutput
    plugin.pytest_testnodedown(node, None)
    assert "gw0" in master["xdist"]["worker_receipts"]
    path = arts_workspace / "master.json"
    monkeypatch.setenv("UM_ARTS_PYTEST_REPORT", str(path))
    monkeypatch.delenv("UM_ARTS_RECEIPT", raising=False)
    plugin.pytest_sessionfinish(SimpleNamespace(config=SimpleNamespace()), 0)
    assert evaluate_report(path, returncode=0)["status"] == "passed"


def test_external_xdist_configuration_allowed_managed_nested_xdist_forbidden(arts_workspace, monkeypatch):
    monkeypatch.setattr(plugin, "_data", events())
    monkeypatch.setenv("UM_ARTS_PYTEST_REPORT", str(arts_workspace / "output.json"))
    monkeypatch.delenv("UM_ARTS_RECEIPT", raising=False)
    config = SimpleNamespace(rootpath=arts_workspace,
                             option=SimpleNamespace(collectonly=False, numprocesses=2, dist="load"))
    plugin.pytest_configure(config)
    assert plugin._data["xdist"]["enabled"]
    monkeypatch.setenv("UM_ARTS_RECEIPT", str(arts_workspace / "managed.json"))
    with pytest.raises(pytest.UsageError, match="nested"):
        plugin.pytest_configure(config)


def test_real_external_xdist_if_already_installed(arts_workspace):
    pytest.importorskip("xdist", reason="xdist is optional; no dependency installation for capture")
    command, env, root, path = capture_command(arts_workspace, "-p", "xdist.plugin", "-n", "2")
    completed = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True,
                               check=False, timeout=60)
    assert completed.returncode == 0, completed.stderr
    result = evaluate_report(path, returncode=0)
    assert result["status"] == "passed", result
    assert result["xdist"]["workers"] == ["gw0", "gw1"]
    assert result["counts"] == {"passed": 2, "skipped": 1, "xfailed": 1}


def test_wrapper_runs_existing_pytest_once_and_seals_portable_evidence(arts_workspace, monkeypatch):
    _, _, root, _ = capture_command(arts_workspace)
    counter = arts_workspace / "invocation-count"
    with (root / "test_capture.py").open("a") as stream:
        stream.write(
            f"\nfrom pathlib import Path\np=Path({str(counter)!r})\n"
            "p.write_text(str(int(p.read_text())+1) if p.exists() else '1')\n")
    artifact = arts_workspace / "wrapped"
    result = capture_existing_command([sys.executable, "-m", "pytest", "-q"], artifact, root)
    assert result["status"] == "passed", result
    assert result["test_gate"] is True
    assert result["evidence_class"] == "STRUCTURED_PYTEST_EXECUTION"
    assert result["sealed"] is True
    assert result["proof_claim"] is False
    assert counter.read_text() == "1"
    assert result["counts"] == {"passed": 2, "skipped": 1, "xfailed": 1}
    assert result["provenance"]["source_stable"]
    assert result["provenance"]["environment_stable"]
    assert "test_capture.py" in result["provenance"]["source_files"]
    assert result["provenance"]["environment"]["python"]
    assert result["provenance"]["command"] == [sys.executable, "-m", "pytest", "-q"]
    assert result["provenance"]["settings"]["xdist_policy"] == "serial_in_explicit_capture_wrapper"
    assert (artifact / "manifest.json").is_file()
    assert (artifact / "output.log").is_file()
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: pytest.fail("report executed a command"))
    assert report(artifact)["status"] == "passed"
    imported = import_artifact(artifact, arts_workspace / "imported-store")
    assert imported["status"] == "passed"
    assert report(Path(imported["attempt_path"]))["counts"] == result["counts"]
    with pytest.raises(EvidenceError, match="no resumable plan"):
        resume(artifact)


def test_wrapper_cli_existing_suite_without_extra_run(arts_workspace):
    _, _, root, _ = capture_command(arts_workspace)
    output = arts_workspace / "cli-wrapped"
    completed = subprocess.run(
        [sys.executable, "-m", "TOOLS.um_arts", "capture", "--root", str(root),
         "--output", str(output), "--timeout-seconds", "30", "--",
         sys.executable, "-m", "pytest", "-q"],
        capture_output=True, text=True, check=False, timeout=60)
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "passed"
    assert result["returncode"] == 0
    assert result["counts"]["passed"] == 2


def test_wrapper_other_commands_do_not_claim_test_gate(arts_workspace):
    root = arts_workspace / "command-root"
    root.mkdir()
    result = capture_existing_command([sys.executable, "-c", "print('command log')"],
                                     arts_workspace / "command-artifact", root)
    assert result["status"] == "command_passed"
    assert result["test_gate"] is False
    assert result["pytest_status"] == "not_observed"
    assert result["evidence_class"] == "COMMAND_EXECUTION_ONLY"
    assert result["counts"] == {}
    failed = capture_existing_command([sys.executable, "-c", "raise SystemExit(1)"],
                                     arts_workspace / "failed-artifact", root)
    assert failed["status"] == "blocked"
    assert failed["returncode"] == 1


def test_wrapper_collection_only_does_not_claim_execution_gate(arts_workspace):
    _, _, root, _ = capture_command(arts_workspace)
    result = capture_existing_command(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        arts_workspace / "collection-artifact", root)
    assert result["status"] == "collection_passed"
    assert result["test_gate"] is False
    assert result["evidence_class"] == "STRUCTURED_PYTEST_COLLECTION"
    assert result["counts"] == {}
    assert result["reconciled"] == 0
    assert result["selected"] > 0


def test_wrapper_timeout_and_changed_sources_are_blocked(arts_workspace):
    root = arts_workspace / "command-root"
    root.mkdir()
    timed_out = capture_existing_command(
        [sys.executable, "-c", "import time;time.sleep(60)"],
        arts_workspace / "timeout-artifact", root, timeout_seconds=0.2)
    assert timed_out["status"] == "blocked"
    changed = capture_existing_command(
        [sys.executable, "-c", "from pathlib import Path;Path('input.bin').write_bytes(b'changed')"],
        arts_workspace / "changed-artifact", root)
    assert changed["status"] == "blocked"
    assert any("changed during captured" in error for error in changed["errors"])


@pytest.mark.parametrize("arguments", [
    ["-n", "auto", "--dist", "load", "-k", "test_pass"],
    ["-nauto", "--dist=load", "-k", "test_pass"],
    ["--numprocesses=8", "--max-worker-restart", "2", "-k", "test_pass"],
])
def test_worker_options_are_normalized_only_inside_explicit_capture(arguments):
    kept, removed = _serial_pytest_arguments(arguments)
    assert kept == ["-k", "test_pass"]
    assert removed


def test_serial_normalization_preserves_option_values_and_positional_delimiter():
    arguments = ["--ignore-glob", "-nfoo", "-k", "--numprocesses=4", "--", "-nauto"]
    assert _serial_pytest_arguments(arguments) == (arguments, [])


def test_ci_wrapper_strips_n_auto_and_preserves_frozen_command_provenance(arts_workspace, monkeypatch):
    _, _, root, _ = capture_command(arts_workspace)
    monkeypatch.setenv("PYTEST_ADDOPTS", "-n auto --dist=load -k test_pass")
    original = [sys.executable, "-m", "pytest", "-n", "auto", "--dist", "load", "-q"]
    result = capture_existing_command(original, arts_workspace / "ci-serial", root)
    assert result["status"] == "passed", result
    assert result["counts"] == {"passed": 2}
    assert result["provenance"]["command"] == original
    assert "-n" not in result["provenance"]["effective_command"]
    assert "--dist" not in result["provenance"]["effective_command"]
    assert result["provenance"]["settings"]["removed_worker_options"] == ["-n", "auto", "--dist", "load"]
    assert result["provenance"]["settings"]["removed_environment_worker_options"] == ["-n", "auto", "--dist=load"]
    assert result["jobs"]["captured"]["xdist"]["enabled"] is False
    artifact = Path(result["attempt_path"])
    assert (artifact / "manifest.json").is_file()
    assert report(artifact)["provenance"] == result["provenance"]


def test_capture_serial_flag_prevents_xdist_workers_before_session_start(arts_workspace, monkeypatch):
    monkeypatch.setattr(plugin, "_data", events())
    monkeypatch.setenv("UM_ARTS_PYTEST_REPORT", str(arts_workspace / "serial.json"))
    monkeypatch.setenv("UM_ARTS_CAPTURE_SERIAL", "1")
    monkeypatch.delenv("UM_ARTS_RECEIPT", raising=False)
    config = SimpleNamespace(rootpath=arts_workspace,
                             option=SimpleNamespace(collectonly=False, numprocesses="auto", dist="load"))
    plugin.pytest_configure(config)
    assert config.option.numprocesses == 0
    assert config.option.dist == "no"
    assert plugin._data["xdist"]["enabled"] is False
