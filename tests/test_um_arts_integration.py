# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Real generic-repository CLI execution, immutable resume, and false-green tests."""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest
from TOOLS.um_arts.evidence import EvidenceError, fingerprints, read_json, seal
from TOOLS.um_arts.reporting import report

from tests.test_um_arts import arts_workspace as _arts_workspace
from TOOLS.um_arts import engine

arts_workspace = _arts_workspace


def make_repository(workspace, source=None, *, workers=2, timeout=30, pytest_args=None):
    root = workspace / "second-repository"
    root.mkdir()
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_a.py").write_text(source or (
        "import pytest\n"
        "@pytest.mark.parametrize('value', [1, 2])\n"
        "def test_parameter(value): assert value > 0\n"
        "@pytest.mark.skip(reason='explicit skip')\n"
        "def test_skip(): pass\n"
        "@pytest.mark.xfail(reason='honest expected failure')\n"
        "def test_xfail(): assert False\n"
    ))
    if source is None:
        (tests / "test_b.py").write_text("def test_other(): assert True\n")
    config = workspace / "adapter.json"
    config.write_text(json.dumps({
        "adapter": "generic", "workers": workers, "timeout_seconds": timeout,
        "pytest_args": pytest_args or [],
        "suites": [{"name": "unit", "paths": ["tests"]}],
    }))
    return root, workspace / "store", config


def collect(root, store, config, *, mode="full"):
    result = engine.plan(root, store, config, adapter="generic", mode=mode)
    assert result["status"] == "ready", result
    return Path(result["plan_path"])


def test_second_repository_run_resume_report_import_without_execution(arts_workspace, monkeypatch):
    root, store, config = make_repository(arts_workspace)
    plan = collect(root, store, config, mode="changed")
    result = engine.run(plan)
    assert result["status"] == "passed", result
    assert result["counts"] == {"passed": 3, "skipped": 1, "xfailed": 1}
    attempt = Path(result["attempt_path"])
    original_manifest = (attempt / "manifest.json").read_bytes()
    initial = report(attempt)
    assert len(initial["jobs"]) == 2
    assert initial["formal"]["registry_status"] == "not_applicable"
    assert initial["selection"]["effective_mode"] == "full"

    def unexpected_execution(*args, **kwargs):
        raise AssertionError("No completed shard or imported artifact should execute")

    monkeypatch.setattr(engine, "_pytest", unexpected_execution)
    resumed = engine.resume(attempt)
    assert resumed["status"] == "passed", resumed
    assert Path(resumed["attempt_path"]) != attempt
    assert (attempt / "manifest.json").read_bytes() == original_manifest
    comparison = report(Path(resumed["attempt_path"]), attempt)
    assert comparison["comparison"]["compatible"]
    assert comparison["comparison"]["duration_delta_seconds"] == 0
    monkeypatch.setattr(subprocess, "Popen", unexpected_execution)
    imported = engine.import_artifact(attempt, arts_workspace / "import-store")
    assert imported["status"] == "passed"
    assert imported["executed_commands"] is False
    assert report(Path(imported["attempt_path"]))["counts"] == initial["counts"]
    # Imported/report evidence is portable and never imports code from its old root.
    root.rename(arts_workspace / "moved-repository")
    assert report(Path(imported["attempt_path"]))["status"] == "passed"


def test_resume_failed_shard_only_and_dependency_order(arts_workspace, monkeypatch):
    state = arts_workspace / ".first-execution"
    source = (
        "from pathlib import Path\n"
        "def test_flaky():\n"
        f" p = Path({str(state)!r})\n"
        " if not p.exists():\n"
        "  p.write_text('executed')\n"
        "  assert False\n"
    )
    root, store, config = make_repository(arts_workspace, source)
    (root / "tests/test_good.py").write_text("def test_good(): assert True\n")
    integration = root / "integration"
    integration.mkdir()
    (integration / "test_dependency.py").write_text(
        "from pathlib import Path\n"
        f"def test_dependency(): assert Path({str(state)!r}).exists()\n")
    data = json.loads(config.read_text())
    data["suites"].append({"name": "integration", "paths": ["integration"],
                           "requires": ["unit"], "serial": True})
    config.write_text(json.dumps(data))
    plan = collect(root, store, config)
    initial = engine.run(plan)
    assert initial["status"] == "blocked"
    attempt = Path(initial["attempt_path"])
    initial_report = report(attempt)
    successful = {job for job, result in initial_report["jobs"].items()
                  if result["status"] == "passed"}
    assert len(successful) == 1
    assert not (attempt / "jobs/integration-000").exists()
    calls = []
    original = engine._pytest

    def record(*args, **kwargs):
        calls.append(args[1].name)
        return original(*args, **kwargs)

    monkeypatch.setattr(engine, "_pytest", record)
    resumed = engine.resume(attempt)
    assert resumed["status"] == "passed", resumed
    assert not successful.intersection(calls)
    assert "integration-000" in calls
    assert len(calls) == 2


@pytest.mark.parametrize("source", [
    "def test_failure(): assert False\n",
    ("import pytest\n@pytest.fixture\ndef broken(): raise RuntimeError('setup')\n"
     "def test_setup(broken): pass\n"),
    ("import pytest\n@pytest.fixture\ndef broken():\n yield\n raise RuntimeError('teardown')\n"
     "def test_teardown(broken): pass\n"),
    ("import pytest\n@pytest.mark.xfail(reason='unexpected pass')\n"
     "def test_xpass(): pass\n"),
    "import pytest\n@pytest.mark.xfail\ndef test_reasonless_xpass(): pass\n",
])
def test_real_phase_failures_are_blocked(arts_workspace, source):
    root, store, config = make_repository(arts_workspace, source)
    result = engine.run(collect(root, store, config))
    assert result["status"] == "blocked"
    assert result["errors"]


@pytest.mark.parametrize("source", [
    "this is not valid python !!!\n",
    "raise RuntimeError('collection failure')\n",
    "def not_a_test(): pass\n",
    "import pytest\npytest.skip('whole module skipped', allow_module_level=True)\n",
])
def test_real_collection_errors_empty_and_all_skipped_are_blocked(arts_workspace, source):
    root, store, config = make_repository(arts_workspace, source)
    result = engine.plan(root, store, config, adapter="generic")
    assert result["status"] == "blocked"
    with pytest.raises(EvidenceError):
        engine.run(Path(result["plan_path"]))


def test_deselected_identity_and_collection_skip_accounting(arts_workspace):
    root, store, config = make_repository(arts_workspace, pytest_args=["-k", "parameter"])
    (root / "tests/test_optional.py").write_text(
        "import pytest\npytest.skip('optional integration', allow_module_level=True)\n")
    result = engine.run(collect(root, store, config))
    assert result["status"] == "passed", result
    data = report(Path(result["attempt_path"]))
    assert data["counts"] == {"passed": 2}
    assert data["deselected"] == 3
    assert data["collection_skips"] == {"unit": ["tests/test_optional.py"]}


def test_plan_source_changes_and_resume_config_changes_rejected(arts_workspace, monkeypatch):
    root, store, config = make_repository(arts_workspace)
    plan = collect(root, store, config)
    result = engine.run(plan)
    (root / "tests/test_b.py").write_text("def test_other(): assert False\n")
    with pytest.raises(EvidenceError, match="compatible"):
        engine.run(plan)
    with pytest.raises(EvidenceError, match="compatible"):
        engine.resume(Path(result["attempt_path"]))


def test_external_execution_config_change_blocks_resume(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    executed = engine.run(collect(root, store, config))
    data = json.loads(config.read_text())
    data["workers"] = 1
    config.write_text(json.dumps(data))
    with pytest.raises(EvidenceError, match="config changed"):
        engine.resume(Path(executed["attempt_path"]))


def test_runtime_source_mutation_is_not_green(arts_workspace):
    root, store, config = make_repository(arts_workspace,
        "from pathlib import Path\n"
        "def test_changes_source(): Path('new_source.py').write_text('# changed\\n')\n")
    result = engine.run(collect(root, store, config))
    assert result["status"] == "blocked"
    assert any("changed during execution" in error for error in result["errors"])


def test_restoring_source_does_not_make_unstable_attempt_reusable(arts_workspace):
    root, store, config = make_repository(arts_workspace,
        "from pathlib import Path\n"
        "def test_changes_source(): Path('new_source.py').write_text('# changed\\n')\n")
    result = engine.run(collect(root, store, config))
    assert result["status"] == "blocked"
    (root / "new_source.py").unlink()
    with pytest.raises(EvidenceError, match="changed during prior execution"):
        engine.resume(Path(result["attempt_path"]))


def test_dataset_and_environment_changes_invalidate_source_plan(arts_workspace, monkeypatch):
    root, store, config = make_repository(arts_workspace)
    data = root / "fixture.bin"
    data.write_bytes(b"\x00\x01")
    plan = collect(root, store, config)
    data.write_bytes(b"\x00\x02")
    with pytest.raises(EvidenceError, match="compatible"):
        engine.run(plan)
    data.write_bytes(b"\x00\x01")
    monkeypatch.setenv("UM_TEST_MACHINE_PROFILE", "changed")
    with pytest.raises(EvidenceError, match="compatible"):
        engine.run(plan)


def test_parallel_tracker_scratch_is_not_a_source_change(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    (root / ".gitignore").write_text(".um-arts-test-work/\n")
    subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
    settings = engine.load_config(root, config, "generic")
    initial = fingerprints(root, store, settings)
    scratch = root / ".um-arts-test-work"
    scratch.mkdir()
    (scratch / "receipt.json").write_text('{"temporary":true}')
    current = fingerprints(root, store, settings)
    assert current["compatibility"] == initial["compatibility"]
    assert ".um-arts-test-work" in current["source_policy"]["excluded_directories"]
    (root / "fixture.bin").write_bytes(b"real test input")
    assert fingerprints(root, store, settings)["compatibility"] != initial["compatibility"]


def test_internal_source_aliases_track_targets_and_content_without_cycles(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    settings = engine.load_config(root, config, "generic")
    inputs = root / "inputs"
    inputs.mkdir()
    (inputs / "first.bin").write_bytes(b"same data")
    (inputs / "second.bin").write_bytes(b"same data")
    (root / "directory_alias").symlink_to("inputs", target_is_directory=True)
    file_alias = root / "file_alias"
    file_alias.symlink_to("inputs/first.bin")
    (root / "root_alias").symlink_to(".", target_is_directory=True)
    first = fingerprints(root, store, settings)
    assert first["source_links"]["directory_alias"]["resolved"] == "inputs"
    assert first["source_links"]["root_alias"]["resolved"] == "."
    assert first["source_links"]["file_alias"]["target"] == "inputs/first.bin"
    assert not any(name.startswith("directory_alias/") for name in first["source_files"])
    file_alias.unlink()
    file_alias.symlink_to("inputs/second.bin")
    second = fingerprints(root, store, settings)
    assert second["compatibility"]["source"] != first["compatibility"]["source"]
    (inputs / "second.bin").write_bytes(b"modified input")
    third = fingerprints(root, store, settings)
    assert third["compatibility"]["source"] != second["compatibility"]["source"]


@pytest.mark.parametrize("target", ["external", "missing", "excluded", "cyclic", "store"])
def test_unsafe_source_aliases_are_rejected(arts_workspace, target):
    root, store, config = make_repository(arts_workspace)
    settings = engine.load_config(root, config, "generic")
    if target == "external":
        destination = arts_workspace / "outside.bin"
        destination.write_bytes(b"not in repository")
    elif target == "excluded":
        destination = root / ".lake"
        destination.mkdir()
    elif target == "store":
        destination = store
        destination.mkdir()
    else:
        destination = root / ("alias" if target == "cyclic" else "missing.bin")
    (root / "alias").symlink_to(destination)
    with pytest.raises(EvidenceError, match="source symlink|Source symlink"):
        fingerprints(root, store, settings)


def test_pytest_scratch_is_inside_store_and_not_imported_as_evidence(arts_workspace):
    root, store, config = make_repository(arts_workspace,
        "from pathlib import Path\n"
        "def test_scratch(tmp_path):\n"
        " assert '.um-arts-test-work' in str(tmp_path)\n"
        " (tmp_path / 'file').write_text('artifact')\n"
        " (tmp_path / 'symlink').symlink_to(tmp_path / 'file')\n")
    result = engine.run(collect(root, store, config))
    assert result["status"] == "passed", result
    attempt = Path(result["attempt_path"])
    assert not list((attempt / "jobs").glob("*/scratch"))


def test_completed_receipts_must_validate_before_resume(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    result = engine.run(collect(root, store, config))
    attempt = Path(result["attempt_path"])
    events = next((attempt / "jobs").glob("*/events.json"))
    events.chmod(0o644)
    data = read_json(events)
    data["reports"] = []
    events.write_text(json.dumps(data))
    with pytest.raises(EvidenceError, match="hash mismatch"):
        engine.resume(attempt)
    with pytest.raises(EvidenceError):
        engine.import_artifact(attempt, arts_workspace / "bad-import")


def test_resealed_missing_phase_receipts_still_fail_semantic_gate(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    executed = engine.run(collect(root, store, config))
    attempt = Path(executed["attempt_path"])
    receipt = next((attempt / "jobs").glob("*/events.json"))
    receipt.chmod(0o644)
    data = read_json(receipt)
    data["reports"] = []
    receipt.write_text(json.dumps(data))
    attempt.chmod(0o755)
    receipt.parent.chmod(0o755)
    (receipt.parent / "manifest.json").unlink()
    (receipt.parent / "seal.json").unlink()
    seal(receipt.parent)
    (attempt / "manifest.json").unlink()
    (attempt / "seal.json").unlink()
    seal(attempt)
    evaluated = report(attempt)
    assert evaluated["status"] == "blocked"
    assert any("Missing or extra executed" in error for error in evaluated["errors"])


def test_import_destination_symlink_cannot_escape_store(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    result = engine.run(collect(root, store, config))
    destination_store = arts_workspace / "unsafe-import-store"
    destination_store.mkdir()
    outside = arts_workspace / "outside"
    outside.mkdir()
    (destination_store / "imports").symlink_to(outside, target_is_directory=True)
    with pytest.raises(EvidenceError, match="Symlink|escapes"):
        engine.import_artifact(Path(result["attempt_path"]), destination_store)
    assert not list(outside.iterdir())


def test_baseline_comparison_requires_matching_fingerprints(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    first = engine.run(collect(root, store, config))
    (root / "tests/test_b.py").write_text("def test_other(): assert 1 == 1\n")
    second = engine.run(collect(root, store, config))
    result = report(Path(second["attempt_path"]), Path(first["attempt_path"]))
    assert not result["comparison"]["compatible"]
    assert "duration_delta_seconds" not in result["comparison"]


def test_missing_lean_tools_block_requested_build_not_certify(arts_workspace, monkeypatch):
    root, store, config = make_repository(arts_workspace)
    (root / "lean4").mkdir()
    data = json.loads(config.read_text())
    data["lean"] = {"scope": "scoped", "project": "lean4", "targets": ["Example.Module"]}
    config.write_text(json.dumps(data))
    plan = collect(root, store, config)
    monkeypatch.setattr(engine.formal.shutil, "which", lambda name: None)
    result = engine.run(plan)
    assert result["status"] == "blocked"
    evaluated = report(Path(result["attempt_path"]))
    assert evaluated["formal"]["lean_build"]["status"] == "blocked"
    assert evaluated["formal"]["proof_claim"] is False


def test_bounded_timeout_cleans_descendant_process_group(arts_workspace):
    state = arts_workspace / ".child-pid"
    root, store, config = make_repository(arts_workspace,
        "import subprocess, sys, time\nfrom pathlib import Path\n"
        "def test_hangs():\n"
        " child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        f" Path({str(state)!r}).write_text(str(child.pid))\n"
        " time.sleep(60)\n", timeout=5)
    start = time.monotonic()
    result = engine.run(collect(root, store, config))
    assert result["status"] == "blocked"
    assert time.monotonic() - start < 20
    pid = int(state.read_text())
    proc = Path(f"/proc/{pid}/stat")
    if proc.exists():
        assert proc.read_text().split()[2] == "Z"


def cli(*args):
    command = [sys.executable, "-m", "TOOLS.um_arts", *map(str, args)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_real_cli_plan_run_resume_verify_dashboard_and_import(arts_workspace):
    root, store, config = make_repository(arts_workspace, "def test_pass(): pass\n")
    planned = cli("plan", "--root", root, "--store", store, "--adapter", "generic",
                  "--config", config)
    executed = cli("run", "--plan", planned["plan_path"])
    attempt = executed["attempt_path"]
    resumed = cli("resume", "--attempt", attempt)
    assert resumed["attempt_path"] != attempt
    assert cli("verify", "--attempt", attempt)["status"] == "passed"
    output = arts_workspace / "dashboard.html"
    evaluated = cli("dashboard", "--attempt", attempt, "--output", output)
    assert evaluated["counts"] == {"passed": 1}
    assert output.is_file()
    assert cli("import", "--artifact", attempt, "--store",
               arts_workspace / "cli-import")["executed_commands"] is False


def unseal_attempt(attempt):
    attempt.chmod(0o755)
    for name in ["manifest.json", "seal.json", "end_fingerprints.json",
                "execution_errors.json"]:
        (attempt / name).unlink()


def test_unsealed_attempt_is_never_green_and_reuses_checked_jobs(arts_workspace, monkeypatch):
    root, store, config = make_repository(arts_workspace)
    executed = engine.run(collect(root, store, config))
    attempt = Path(executed["attempt_path"])
    unseal_attempt(attempt)
    incomplete = report(attempt)
    assert incomplete["status"] == "incomplete"
    assert all(job["status"] == "passed" for job in incomplete["jobs"].values())
    with pytest.raises(EvidenceError, match="Unsealed"):
        engine.import_artifact(attempt, arts_workspace / "incomplete-import")

    def unexpected(*args, **kwargs):
        raise AssertionError("Validated checkpoints should not rerun")

    monkeypatch.setattr(engine, "_pytest", unexpected)
    result = engine.resume(attempt)
    assert result["status"] == "passed", result
    assert report(attempt)["status"] == "incomplete"


@pytest.mark.parametrize("damage", ["missing_seal", "corrupt_receipt", "wrong_identity",
                                  "changed_environment"])
def test_unsealed_invalid_checkpoints_rerun_only_affected_job(arts_workspace, monkeypatch, damage):
    root, store, config = make_repository(arts_workspace)
    attempt = Path(engine.run(collect(root, store, config))["attempt_path"])
    unseal_attempt(attempt)
    job = next((attempt / "jobs").iterdir())
    job.chmod(0o755)
    if damage == "missing_seal":
        (job / "seal.json").unlink()
    elif damage == "corrupt_receipt":
        path = job / "events.json"
        path.chmod(0o644)
        path.write_text("{}")
    else:
        path = job / "checkpoint.json"
        path.chmod(0o644)
        data = read_json(path)
        if damage == "wrong_identity":
            data["job_digest"] = "different"
        else:
            data["after"]["environment"] = "different"
        path.write_text(json.dumps(data))
        (job / "manifest.json").unlink()
        (job / "seal.json").unlink()
        seal(job)
    incomplete = report(attempt)
    assert incomplete["jobs"][job.name]["status"] == "incomplete"
    calls = []
    original = engine._pytest

    def record(*args, **kwargs):
        calls.append(args[1].name)
        return original(*args, **kwargs)

    monkeypatch.setattr(engine, "_pytest", record)
    resumed = engine.resume(attempt)
    assert resumed["status"] == "passed", resumed
    assert calls == [job.name]


def test_partial_final_seal_is_not_treated_as_recoverable_checkpoint_state(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    attempt = Path(engine.run(collect(root, store, config))["attempt_path"])
    attempt.chmod(0o755)
    (attempt / "seal.json").unlink()
    with pytest.raises(EvidenceError, match="Missing regular"):
        engine.resume(attempt)


def test_runner_lock_blocks_concurrent_recovery(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    attempt = Path(engine.run(collect(root, store, config))["attempt_path"])
    unseal_attempt(attempt)
    with engine._attempt_lock(attempt), pytest.raises(EvidenceError, match="still running"):
        engine.resume(attempt)


def test_sealed_attempt_cannot_silently_drop_required_checkpoint(arts_workspace):
    root, store, config = make_repository(arts_workspace)
    attempt = Path(engine.run(collect(root, store, config))["attempt_path"])
    checkpoint = next((attempt / "jobs").glob("*/checkpoint.json"))
    checkpoint.parent.chmod(0o755)
    checkpoint.unlink()
    (checkpoint.parent / "manifest.json").unlink()
    (checkpoint.parent / "seal.json").unlink()
    seal(checkpoint.parent)
    attempt.chmod(0o755)
    (attempt / "manifest.json").unlink()
    (attempt / "seal.json").unlink()
    seal(attempt)
    result = report(attempt)
    assert result["status"] == "blocked"
    assert any("Required job checkpoint" in error for error in result["errors"])


def test_hard_killed_cli_recovers_completed_checkpoint_without_reexecuting(arts_workspace):
    calls = arts_workspace / "successful-calls"
    child_pid = arts_workspace / "unfinished-child"
    root, store, config = make_repository(arts_workspace,
        "from pathlib import Path\n"
        f"def test_pass(): Path({str(calls)!r}).write_text('once')\n")
    (root / "tests/test_b.py").write_text(
        "import os, time\nfrom pathlib import Path\n"
        "def test_interrupted():\n"
        f" p = Path({str(child_pid)!r})\n"
        " if not p.exists():\n"
        "  p.write_text(str(os.getpid()))\n"
        "  time.sleep(60)\n")
    planned = cli("plan", "--root", root, "--store", store, "--adapter", "generic",
                  "--config", config)
    plan = Path(planned["plan_path"])
    runner = subprocess.Popen(
        [sys.executable, "-m", "TOOLS.um_arts", "run", "--plan", str(plan)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 20
        attempt = None
        while time.monotonic() < deadline:
            attempts = list((store / "attempts").glob("*")) if (store / "attempts").exists() else []
            if attempts:
               attempt = attempts[0]
               if list((attempt / "jobs").glob("*/seal.json")) and child_pid.exists():
                   break
            if runner.poll() is not None:
                pytest.fail("Runner exited before checkpoint capture: " +
                            runner.stderr.read().decode())
            time.sleep(0.05)
        else:
            pytest.fail("Runner did not finish a checkpoint before timeout")
        runner.kill()
        runner.wait(timeout=10)
        # Hard-killing the coordinator cannot clean up its independent process groups.
        os.killpg(int(child_pid.read_text()), signal.SIGKILL)
        initial = report(attempt)
        assert initial["status"] == "incomplete"
        assert sum(job["status"] == "passed" for job in initial["jobs"].values()) == 1
        calls.write_text("must not rerun")
        resumed = cli("resume", "--attempt", attempt)
        assert resumed["status"] == "passed", resumed
        assert calls.read_text() == "must not rerun"
    finally:
        if runner.poll() is None:
            runner.kill()
            runner.wait(timeout=10)
        if child_pid.exists():
            try:
               os.killpg(int(child_pid.read_text()), signal.SIGKILL)
            except ProcessLookupError:
               pass
        runner.stdout.close()
        runner.stderr.close()
