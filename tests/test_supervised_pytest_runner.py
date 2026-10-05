# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Execution receipts for the supervised pytest entrypoint."""

import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def runner(monkeypatch, tmp_path):
    path = Path(__file__).resolve().parents[1] / "TOOLS/checks/run_supervised_pytest_batch.py"
    spec = importlib.util.spec_from_file_location("supervised_runner", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setattr(module, "ROOT", project)
    module._real_snapshot = module._snapshot
    module._real_environment_fingerprint = module._environment_fingerprint
    monkeypatch.setattr(module, "_snapshot", lambda: {"head": "abc", "worktree_digest": "def"})
    monkeypatch.setattr(module, "_environment_fingerprint", lambda: {
        "python_implementation": "CPython", "python_version": "3.12.14",
        "platform_system": "Linux", "platform_machine": "x86_64",
        "distributions_digest": "a" * 64,
    })
    monkeypatch.setenv("PYTEST_ADDOPTS", "")
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    return module


def configure(monkeypatch, runner, paths, suite="tests-fast"):
    batches = [{"batch_index": i, "test_paths": batch} for i, batch in enumerate(paths)]
    section = {"batches": batches}
    if suite == "tests-fast":
        section["marker_expression"] = "not slow"
    key = "supervised_fast_suite" if suite == "tests-fast" else "supervised_full_core_suite"
    monkeypatch.setattr(runner, "build_regression_supervision_plan_with_full_core_count",
                        lambda **kwargs: {key: section})

    def command(batch_index, batch_count):
        batch = paths[batch_index]
        return [sys.executable, "-m", "pytest", *batch, "-q", "-n", "auto"] if batch else []

    name = "fast_batch_argv" if suite == "tests-fast" else "full_core_batch_argv"
    monkeypatch.setattr(runner, name, command)
    return batches


def invoke(monkeypatch, runner, result, *args, suite="tests-fast"):
    monkeypatch.setattr(sys, "argv", ["runner", "--suite", suite, "--result-dir", str(result),
                                    "--workers", "0", *args])
    return runner.main()


def receipt(result, index=0, suite="tests-fast"):
    return json.loads((result / f"{suite}-{index}.json").read_text())


@pytest.mark.parametrize("suite", ["tests-fast", "full-core"])
def test_real_pytest_cwd_counts_and_aggregate(runner, monkeypatch, tmp_path, suite):
    (runner.ROOT / "test_sample.py").write_text(
        "from pathlib import Path\nimport pytest\n"
        f"def test_cwd(): assert Path.cwd() == Path({str(runner.ROOT)!r})\n"
        "@pytest.mark.skip(reason='explicit skip')\ndef test_skip(): pass\n"
    )
    configure(monkeypatch, runner, [["test_sample.py"], []], suite)
    result = tmp_path / "results"
    assert invoke(monkeypatch, runner, result, "--batch-index", "0", suite=suite) == 0
    data = receipt(result, suite=suite)
    assert data["status"] == "success"
    assert data["exit_code"] == 0
    assert data["counts"] == {"tests": 2, "failures": 0, "errors": 0, "skipped": 1}
    assert len(data["junit_sha256"]) == 64
    assert "-n" not in data["command"]
    assert invoke(monkeypatch, runner, result, "--aggregate", suite=suite) == 1
    assert invoke(monkeypatch, runner, result, "--batch-index", "1", suite=suite) == 0
    assert receipt(result, 1, suite)["status"] == "empty"
    assert invoke(monkeypatch, runner, result, "--aggregate", suite=suite) == 0
    summary = json.loads((result / f"{suite}-aggregate.json").read_text())
    assert summary["counts"] == data["counts"]


def write_junit(path, failure=False, error=False):
    child = "<failure/>" if failure else "<error/>" if error else ""
    path.write_text(f'<testsuites><testsuite tests="1" failures="{int(failure)}" '
                    f'errors="{int(error)}" skipped="0"><testcase>{child}</testcase>'
                    "</testsuite></testsuites>")


def successful_receipt(runner, monkeypatch, tmp_path):
    configure(monkeypatch, runner, [["test_sample.py"]])
    result = tmp_path / "results"

    def run(command, dry_run, timeout):
        write_junit(Path(command[-1].split("=", 1)[1]))
        return 0

    monkeypatch.setattr(runner, "_run", run)
    assert invoke(monkeypatch, runner, result, "--batch-index", "0") == 0
    return result


@pytest.mark.parametrize("status", ["incomplete", "failure", "dry-run", "empty"])
def test_reject_noncompletion(runner, monkeypatch, tmp_path, status):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    data = receipt(result)
    data["status"] = status
    (result / "tests-fast-0.json").write_text(json.dumps(data))
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1


@pytest.mark.parametrize("field", ["snapshot", "plan_digest", "batch_index", "batch_count", "suite",
                                  "exit_code", "counts", "junit_sha256"])
def test_reject_stale_or_corrupt_receipts(runner, monkeypatch, tmp_path, field):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    data = receipt(result)
    data[field] = "corrupt"
    (result / "tests-fast-0.json").write_text(json.dumps(data))
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1


@pytest.mark.parametrize("damage", ["missing", "corrupt", "modified", "receipt-json"])
def test_reject_damaged_artifacts(runner, monkeypatch, tmp_path, damage):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    xml = result / "tests-fast-0.xml"
    if damage == "missing":
        xml.unlink()
    elif damage == "corrupt":
        xml.write_text("not xml")
    elif damage == "modified":
        xml.write_text(xml.read_text() + "\n")
    else:
        (result / "tests-fast-0.json").write_text("{")
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1


def test_current_snapshot_and_plan_required(runner, monkeypatch, tmp_path):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    monkeypatch.setattr(runner, "_snapshot", lambda: {"head": "changed", "worktree_digest": "def"})
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1
    monkeypatch.setattr(runner, "_snapshot", lambda: {"head": "abc", "worktree_digest": "def"})
    configure(monkeypatch, runner, [["other_test.py"]])
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1


@pytest.mark.parametrize("suite", ["tests-fast", "full-core"])
def test_changed_marker_invalidates_receipts(runner, monkeypatch, tmp_path, suite):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    if suite == "full-core":
        configure(monkeypatch, runner, [["test_sample.py"]], suite)
        assert invoke(monkeypatch, runner, result, "--batch-index", "0", suite=suite) == 0
    plan = runner.build_regression_supervision_plan_with_full_core_count()
    key = "supervised_fast_suite" if suite == "tests-fast" else "supervised_full_core_suite"
    plan[key]["marker_expression"] = "slow"
    assert invoke(monkeypatch, runner, result, "--aggregate", suite=suite) == 1


def test_corrupt_selected_marker_digest_rejected(runner, monkeypatch, tmp_path):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    data = receipt(result)
    data["plan_digest"] = runner._digest({
        "batches": [["test_sample.py"]], "marker_expression": "slow",
    })
    (result / "tests-fast-0.json").write_text(json.dumps(data))
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1


def test_environment_distribution_digest_is_sorted_and_version_bound(runner, monkeypatch):
    distributions = [SimpleNamespace(metadata={"Name": "Some_Package"}, version="1.2.3"),
                     SimpleNamespace(metadata={"Name": "another"}, version="4.5.6")]
    monkeypatch.setattr(runner.metadata, "distributions", lambda: distributions)
    first = runner._real_environment_fingerprint()
    assert first["distributions_digest"] == runner._digest(
        [("another", "4.5.6"), ("some-package", "1.2.3")]
    )
    distributions.reverse()
    assert runner._real_environment_fingerprint() == first
    distributions[0].version = "4.5.7"
    assert runner._real_environment_fingerprint() != first


@pytest.mark.parametrize("field", ["python_implementation", "python_version", "platform_system",
                                  "platform_machine", "distributions_digest"])
def test_mixed_nonempty_batch_environments_rejected(runner, monkeypatch, tmp_path, field):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    configure(monkeypatch, runner, [["first.py"], ["second.py"]])
    assert invoke(monkeypatch, runner, result, "--batch-index", "0") == 0
    changed = dict(runner._environment_fingerprint())
    changed[field] = "f" * 64 if field == "distributions_digest" else "different"
    monkeypatch.setattr(runner, "_environment_fingerprint", lambda: changed)
    assert invoke(monkeypatch, runner, result, "--batch-index", "1") == 0
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1
    summary = json.loads((result / "tests-fast-aggregate.json").read_text())
    assert any("mixed batch execution environments" in problem for problem in summary["problems"])


def test_supervisor_environment_is_not_compared(runner, monkeypatch, tmp_path):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    monkeypatch.setattr(runner, "_environment_fingerprint",
                        lambda: pytest.fail("supervisor environment must not be inspected"))
    assert invoke(monkeypatch, runner, result, "--aggregate") == 0


def test_empty_batches_do_not_impose_environment(runner, monkeypatch, tmp_path):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    configure(monkeypatch, runner, [["first.py"], []])
    assert invoke(monkeypatch, runner, result, "--batch-index", "0") == 0
    monkeypatch.setattr(runner, "_environment_fingerprint",
                        lambda: pytest.fail("empty batches must not inspect their environment"))
    assert invoke(monkeypatch, runner, result, "--batch-index", "1") == 0
    assert receipt(result, 1)["environment_fingerprint"] is None
    assert invoke(monkeypatch, runner, result, "--aggregate") == 0


@pytest.mark.parametrize("fingerprint", [None, {}, {"distributions_digest": "wrong"}])
def test_missing_or_corrupt_environment_rejected(runner, monkeypatch, tmp_path, fingerprint):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    data = receipt(result)
    data["environment_fingerprint"] = fingerprint
    (result / "tests-fast-0.json").write_text(json.dumps(data))
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1


@pytest.mark.parametrize("error", [OSError("unreadable source"),
                                 subprocess.CalledProcessError(128, ["git"])])
def test_initial_snapshot_errors_fail_closed(runner, monkeypatch, tmp_path, error):
    def snapshot():
        raise error

    monkeypatch.setattr(runner, "_snapshot", snapshot)
    monkeypatch.setattr(runner, "build_regression_supervision_plan_with_full_core_count",
                        lambda **kwargs: pytest.fail("invalid snapshot must stop before planning"))
    assert invoke(monkeypatch, runner, tmp_path / "results", "--aggregate") == 2


def test_plan_identity_ignores_environment_commands_and_workers(runner, monkeypatch, tmp_path):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    plan = runner.build_regression_supervision_plan_with_full_core_count()
    plan["supervised_fast_suite"]["batch_commands"] = ["different python -m pytest -n auto"]
    monkeypatch.setattr(runner, "fast_batch_argv",
                        lambda **kwargs: pytest.fail("aggregation must not build execution commands"))
    assert invoke(monkeypatch, runner, result, "--aggregate", "--workers", "2") == 0


@pytest.mark.parametrize("suite", ["tests-fast", "full-core"])
def test_real_plan_digest_independent_of_xdist_availability(runner, monkeypatch, tmp_path, suite):
    import src.core.regression_supervision_plan as plans

    monkeypatch.setattr(plans, "_ROOT", runner.ROOT)
    (runner.ROOT / "tests").mkdir()
    (runner.ROOT / "tests/test_sample.py").write_text("def test_sample(): pass\n")
    available = [True]
    monkeypatch.setattr(plans, "pytest_xdist_available", lambda: available[0])
    first = tmp_path / "xdist-results"
    second = tmp_path / "serial-results"
    args = ("--batch-count", "1", "--batch-index", "0", "--dry-run")
    assert invoke(monkeypatch, runner, first, *args, "--workers", "2", suite=suite) == 0
    available[0] = False
    assert invoke(monkeypatch, runner, second, *args, suite=suite) == 0
    xdist = receipt(first, suite=suite)
    serial = receipt(second, suite=suite)
    assert xdist["plan_digest"] == serial["plan_digest"]
    assert xdist["snapshot"] == serial["snapshot"]
    assert xdist["command"][xdist["command"].index("-n") + 1] == "2"
    assert "-n" not in serial["command"]


def test_tracked_change_before_execution_prevents_launch(runner, monkeypatch, tmp_path):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    snapshots = iter([{"head": "abc", "worktree_digest": "def"},
                      {"head": "abc", "worktree_digest": "tracked-change"}])
    monkeypatch.setattr(runner, "_snapshot", lambda: next(snapshots))
    monkeypatch.setattr(runner, "_run", lambda *args: pytest.fail("changed snapshot must not execute"))
    assert invoke(monkeypatch, runner, result, "--batch-index", "0") == 1
    assert receipt(result)["status"] == "incomplete"
    assert receipt(result)["exit_code"] is None


def test_tracked_change_during_aggregation_fails_closed(runner, monkeypatch, tmp_path):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    snapshots = iter([{"head": "abc", "worktree_digest": "def"},
                      {"head": "abc", "worktree_digest": "tracked-change"}])
    monkeypatch.setattr(runner, "_snapshot", lambda: next(snapshots))
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1
    summary = json.loads((result / "tests-fast-aggregate.json").read_text())
    assert "snapshot changed during aggregation" in summary["problems"]


@pytest.mark.parametrize("code,xml,status", [(1, "failure", "failure"), (2, "error", "failure"),
                                           (124, "none", "incomplete"), (0, "none", "incomplete"),
                                           (0, "invalid", "incomplete"), (5, "none", "failure")])
def test_failure_and_incomplete_recorded(runner, monkeypatch, tmp_path, code, xml, status):
    configure(monkeypatch, runner, [["test_sample.py"]])
    result = tmp_path / "results"

    def run(command, dry_run, timeout):
        path = Path(command[-1].split("=", 1)[1])
        if xml in {"failure", "error"}:
            write_junit(path, failure=xml == "failure", error=xml == "error")
        elif xml == "invalid":
            path.write_text("<invalid>")
        return code

    monkeypatch.setattr(runner, "_run", run)
    assert invoke(monkeypatch, runner, result, "--batch-index", "0") != 0
    assert receipt(result)["status"] == status
    assert receipt(result)["exit_code"] == code
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1


def test_dry_run_overwrites_old_success(runner, monkeypatch, tmp_path):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    monkeypatch.setattr(runner, "_run", lambda *args: 0)
    assert invoke(monkeypatch, runner, result, "--batch-index", "0", "--dry-run") == 0
    assert receipt(result)["status"] == "dry-run"
    assert not (result / "tests-fast-0.xml").exists()
    assert invoke(monkeypatch, runner, result, "--aggregate") == 1


def test_snapshot_changed_during_run(runner, monkeypatch, tmp_path):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    snapshots = iter([{"head": "abc", "worktree_digest": "def"},
                      {"head": "abc", "worktree_digest": "def"},
                      {"head": "abc", "worktree_digest": "new"}])
    monkeypatch.setattr(runner, "_snapshot", lambda: next(snapshots))
    assert invoke(monkeypatch, runner, result, "--batch-index", "0") == 1
    assert receipt(result)["status"] == "incomplete"
    assert receipt(result)["exit_code"] == 0


def test_reject_repo_output_and_invalid_options(runner, monkeypatch, tmp_path):
    assert invoke(monkeypatch, runner, runner.ROOT / "results", "--batch-index", "0") == 2
    for args in [("--workers", "-1"), ("--timeout", "0"), ("--timeout", "nan"),
                 ("--aggregate", "--dry-run"), ("--aggregate", "--batch-index", "0")]:
        assert invoke(monkeypatch, runner, tmp_path / "results", *args) == 2


def test_positive_workers_replace_auto(runner, monkeypatch, tmp_path):
    configure(monkeypatch, runner, [["test_sample.py"]])
    result = tmp_path / "results"
    assert invoke(monkeypatch, runner, result, "--batch-index", "0", "--dry-run", "--workers", "3") == 0
    command = receipt(result)["command"]
    assert command[command.index("-n") + 1] == "3"
    assert "auto" not in command


def test_default_execution_cwd(runner, monkeypatch):
    configure(monkeypatch, runner, [["test_sample.py"]])
    calls = []
    monkeypatch.setattr(runner.subprocess, "run",
                        lambda args, **kwargs: calls.append((args, kwargs)) or subprocess.CompletedProcess(args, 0))
    monkeypatch.setattr(sys, "argv", ["runner", "--suite", "tests-fast", "--batch-index", "0"])
    monkeypatch.setenv("PYTEST_ADDOPTS", "-k legacy-filter")
    assert runner.main() == 0
    assert calls[0][1] == {"check": False, "cwd": runner.ROOT}
    assert calls[0][0][-2:] == ["-n", "auto"]


def test_integration_preflight_is_serial_and_uses_run(runner, monkeypatch):
    command = runner.integration_preflight_argv()
    assert "-n" not in command
    assert command[command.index("-m", 3) + 1] == ""
    calls = []
    monkeypatch.setattr(runner, "_run",
                        lambda *args, **kwargs: calls.append((args, kwargs)) or 0)
    monkeypatch.setattr(runner, "build_regression_supervision_plan_with_full_core_count",
                        lambda **kwargs: {})
    monkeypatch.setattr(sys, "argv", ["runner", "--suite", "integration-preflight",
                                    "--dry-run", "--timeout", "12"])
    monkeypatch.setenv("PYTEST_ADDOPTS", "-n auto -k partial")
    assert runner.main() == 0
    assert calls == [((command,), {"dry_run": True, "timeout": 12.0,
                                  "env": {**os.environ, "PYTEST_ADDOPTS": ""}})]


@pytest.mark.parametrize("aggregate", [False, True])
@pytest.mark.parametrize("addopts", ["-k partial", "--ignore=test_sample.py", "-n auto", " "])
@pytest.mark.parametrize("suite", ["tests-fast", "full-core"])
def test_receipts_reject_pytest_addopts(runner, monkeypatch, tmp_path, aggregate, addopts, suite):
    result = successful_receipt(runner, monkeypatch, tmp_path)
    if suite == "full-core":
        configure(monkeypatch, runner, [["test_sample.py"]], suite)
        assert invoke(monkeypatch, runner, result, "--batch-index", "0", suite=suite) == 0
    original = receipt(result, suite=suite)
    monkeypatch.setenv("PYTEST_ADDOPTS", addopts)
    args = ("--aggregate",) if aggregate else ("--batch-index", "0")
    assert invoke(monkeypatch, runner, result, *args, suite=suite) == 2
    assert receipt(result, suite=suite) == original


def test_real_integration_preflight_neutralizes_pytest_addopts(runner, monkeypatch, capfd):
    (runner.ROOT / "test_sample.py").write_text(
        "def test_first(): pass\ndef test_second(): pass\n"
    )
    monkeypatch.setattr(runner, "integration_preflight_argv",
                        lambda: [sys.executable, "-m", "pytest", "test_sample.py", "-m", "", "-q"])
    monkeypatch.setattr(runner, "build_regression_supervision_plan_with_full_core_count",
                        lambda **kwargs: {})
    monkeypatch.setenv("PYTEST_ADDOPTS", "-n auto -k absent")
    monkeypatch.setattr(sys, "argv", ["runner", "--suite", "integration-preflight"])
    assert runner.main() == 0
    assert "2 passed" in capfd.readouterr().out


@pytest.mark.parametrize("suite", ["integration-preflight", "compactified-preflight"])
@pytest.mark.parametrize("aggregate", [False, True])
def test_nonbatched_suites_reject_receipts(runner, monkeypatch, tmp_path, suite, aggregate):
    args = ("--aggregate",) if aggregate else ()
    result = tmp_path / "results"
    assert invoke(monkeypatch, runner, result, *args, suite=suite) == 2
    assert not result.exists()


def test_snapshot_includes_diff_and_untracked_contents(runner, monkeypatch):
    monkeypatch.setattr(runner, "_snapshot", runner._real_snapshot)
    # Mock git, not the hashing logic; do not create commits or change the real repository.
    project = runner.ROOT
    file = project / "new.py"
    file.write_text("first")
    monkeypatch.setattr(runner, "ROOT", project)
    diff = [b"diff"]

    def git(command, **kwargs):
        if command[1] == "diff":
            return diff[0]
        if command[1] == "ls-files":
            return b"new.py\0"
        return b"head\n"

    monkeypatch.setattr(runner.subprocess, "check_output", git)
    original = runner._snapshot()
    file.write_text("second")
    assert runner._snapshot() != original
    diff[0] = b"changed tracked diff"
    assert runner._snapshot() != original


def test_junit_rejects_forged_counts_and_entities(runner, tmp_path):
    xml = tmp_path / "junit.xml"
    xml.write_text('<testsuite tests="2" failures="0" errors="0" skipped="0"><testcase/></testsuite>')
    with pytest.raises(ValueError):
        runner._junit(xml)
    xml.write_text('<!DOCTYPE testsuite [<!ENTITY x "value">]><testsuite/>')
    with pytest.raises(ValueError):
        runner._junit(xml)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux process-group timeout")
def test_timeout_terminates_child_processes(runner):
    pid_file = runner.ROOT / "child.pid"
    script = ("import subprocess, sys, time; "
              "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); "
              f"open({str(pid_file)!r}, 'w').write(str(child.pid)); time.sleep(60)")
    assert runner._run([sys.executable, "-c", script], False, timeout=1) == 124
    pid = int(pid_file.read_text())
    stat = Path(f"/proc/{pid}/stat")
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        try:
            if stat.read_text().split()[2] == "Z":
                return
        except (FileNotFoundError, ProcessLookupError):
            return
        time.sleep(0.01)
    pytest.fail("pytest child survived process-group termination")
