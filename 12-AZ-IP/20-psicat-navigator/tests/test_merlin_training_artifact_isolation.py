# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import conftest as root_config
from ox_navigator.engine import merlin_training_execution as training


def test_production_paths_remain_unchanged_without_override(tmp_path, monkeypatch):
    monkeypatch.delenv(training.TRAINING_RUNTIME_ENV)
    paths = training._training_artifact_paths(tmp_path / "defaults")
    assert paths == tuple(
        tmp_path / "defaults" / path.name
        for path in (
            training.EXECUTION_ARTIFACT_PATH,
            training.LANE_E_PROFILE_ARTIFACT_PATH,
            training.PERFORMANCE_GATE_HISTORY_PATH,
        )
    )
    assert not paths[0].parent.exists()


def test_runtime_copies_preserve_baseline_reads_and_isolate_real_writes(tmp_path, monkeypatch):
    defaults = PRODUCT_ROOT / "training" / "training_execution"
    originals = {path: path.read_bytes() for path in defaults.glob("*.json")}
    runtime_dir = tmp_path / "runtime"
    monkeypatch.setenv(training.TRAINING_RUNTIME_ENV, str(runtime_dir))
    execution, profile, history = training._training_artifact_paths(defaults)
    for path in (execution, profile, history):
        assert path.read_bytes() == originals[defaults / path.name]

    monkeypatch.setattr(training, "EXECUTION_ARTIFACT_PATH", execution)
    monkeypatch.setattr(training, "LANE_E_PROFILE_ARTIFACT_PATH", profile)
    monkeypatch.setattr(training, "PERFORMANCE_GATE_HISTORY_PATH", history)
    monkeypatch.setattr(training, "_LANE_E_RUNTIME_PROFILE_CACHE", None)
    baseline_entries = json.loads(originals[defaults / history.name])["entries"]
    assert training._load_performance_gate_history() == baseline_entries

    def no_benchmark(*args, **kwargs):
        raise AssertionError("baseline profiles must be reused without benchmarks")

    monkeypatch.setattr(training, "run_stage_b_head_to_head_receipts_sync", no_benchmark)
    monkeypatch.setattr(training, "run_stage_c_head_to_head_receipts_sync", no_benchmark)
    baseline_profiles = json.loads(originals[defaults / profile.name])["profiles"]
    readback = training.get_merlin_lane_e_runtime_profiles()
    assert readback["runtime_profiles"]["profiles"] == baseline_profiles
    assert readback["runtime_profiles"]["evidence"]["source"] == "persisted_lane_e_runtime_profiles"
    assert readback["runtime_profiles"]["evidence"]["artifact_path"] == str(profile)
    assert readback["artifact_path"] == str(profile)
    assert readback["artifact_exists"] is True

    recorded = training._record_performance_gate_history(
        performance_gate={"ok": True, "gate_verdict": "pass", "baseline_source": "test"},
        include_ast_context=False,
        ast_file_limit=None,
        processed_count=0,
        dataset_summary=None,
    )
    assert recorded["artifact_path"] == str(history)
    assert recorded["latest"]["cycle_id"] == max(
        (int(entry.get("cycle_id", 0)) for entry in baseline_entries), default=0
    ) + 1
    assert json.loads(history.read_text())["entries"][-1] == recorded["latest"]
    training._write_json(profile, {"profiles": baseline_profiles, "evidence": {"artifact_path": str(profile)}})
    training._write_json(execution, {"artifact_path": str(execution), "test_write": True})
    assert json.loads(execution.read_text())["test_write"] is True
    assert json.loads(profile.read_text())["evidence"]["artifact_path"] == str(profile)
    assert all(path.read_bytes() == original for path, original in originals.items())

    modified = {path: path.read_bytes() for path in (execution, profile, history)}
    assert training._training_artifact_paths(defaults) == (execution, profile, history)
    assert all(path.read_bytes() == original for path, original in modified.items())


def test_missing_baseline_is_not_fabricated(tmp_path, monkeypatch):
    monkeypatch.setenv(training.TRAINING_RUNTIME_ENV, str(tmp_path / "runtime"))
    paths = training._training_artifact_paths(tmp_path / "absent")
    assert all(not path.exists() for path in paths)


def test_empty_runtime_override_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv(training.TRAINING_RUNTIME_ENV, "")
    with pytest.raises(ValueError, match="must not be empty"):
        training._training_artifact_paths(tmp_path)


def test_pytest_runtime_is_active_before_collection():
    directory = Path(os.environ[training.TRAINING_RUNTIME_ENV]).resolve()
    assert directory.is_dir()
    assert not directory.is_relative_to(training.REPO_ROOT)
    for path in (
        training.EXECUTION_ARTIFACT_PATH,
        training.LANE_E_PROFILE_ARTIFACT_PATH,
        training.PERFORMANCE_GATE_HISTORY_PATH,
    ):
        assert path.parent == directory


def test_pytest_owned_runtime_is_cleaned_and_environment_restored(monkeypatch):
    monkeypatch.delenv(training.TRAINING_RUNTIME_ENV)
    cleanups = []
    config = SimpleNamespace(add_cleanup=cleanups.append)
    root_config._start_training_runtime(config)
    directory = Path(os.environ[training.TRAINING_RUNTIME_ENV])
    assert directory.is_dir()
    assert not directory.is_relative_to(training.REPO_ROOT)
    root_config._finish_training_runtime(config)
    assert not directory.exists()
    assert training.TRAINING_RUNTIME_ENV not in os.environ
    cleanups[0]()


def test_pytest_respects_caller_owned_external_runtime(tmp_path, monkeypatch):
    directory = tmp_path / "caller-runtime"
    directory.mkdir()
    retained = directory / "retained.json"
    retained.write_text('{"retained": true}')
    original = str(directory) + "/"
    monkeypatch.setenv(training.TRAINING_RUNTIME_ENV, original)
    config = SimpleNamespace()
    root_config._start_training_runtime(config)
    root_config._finish_training_runtime(config)
    assert os.environ[training.TRAINING_RUNTIME_ENV] == original
    assert json.loads(retained.read_text()) == {"retained": True}


@pytest.mark.parametrize("relative", ["", "training/runtime"])
def test_pytest_rejects_repository_runtime_paths(relative, monkeypatch):
    monkeypatch.setenv(training.TRAINING_RUNTIME_ENV, str(training.REPO_ROOT / relative))
    with pytest.raises(pytest.UsageError, match="outside the repository"):
        root_config._start_training_runtime(SimpleNamespace())


def test_pytest_rejects_symlink_into_repository(tmp_path, monkeypatch):
    link = tmp_path / "repo-link"
    link.symlink_to(training.REPO_ROOT, target_is_directory=True)
    monkeypatch.setenv(training.TRAINING_RUNTIME_ENV, str(link / "runtime"))
    with pytest.raises(pytest.UsageError, match="outside the repository"):
        root_config._start_training_runtime(SimpleNamespace())


def test_pytest_rejects_empty_runtime_override(monkeypatch):
    monkeypatch.setenv(training.TRAINING_RUNTIME_ENV, "")
    with pytest.raises(pytest.UsageError, match="must not be empty"):
        root_config._start_training_runtime(SimpleNamespace())


def test_xdist_controller_leaves_runtime_for_workers(monkeypatch):
    monkeypatch.delenv(training.TRAINING_RUNTIME_ENV)
    config = SimpleNamespace(option=SimpleNamespace(numprocesses=2))
    root_config._start_training_runtime(config)
    assert training.TRAINING_RUNTIME_ENV not in os.environ
    assert not hasattr(config, "_merlin_training_runtime")
    root_config._finish_training_runtime(config)


def test_xdist_workers_have_distinct_seeded_state(tmp_path, monkeypatch):
    caller = tmp_path / "caller"
    caller.mkdir()
    defaults = PRODUCT_ROOT / "training" / "training_execution"
    originals = {path: path.read_bytes() for path in defaults.glob("*.json")}
    caller_originals = {}
    for name in (
        "three_lane_execution_bundle.json",
        "lane_e_runtime_profiles.json",
        "performance_gate_history.json",
    ):
        source = caller / name
        source.write_bytes(originals[defaults / name])
        caller_originals[source] = source.read_bytes()
    inherited = str(caller) + "/"
    monkeypatch.setenv(training.TRAINING_RUNTIME_ENV, inherited)
    workers = []
    directories = []
    try:
        for worker_id in ("gw0", "gw1"):
            # Fake each process receiving the controller's unchanged environment.
            monkeypatch.setenv(training.TRAINING_RUNTIME_ENV, inherited)
            config = SimpleNamespace(
                workerinput={"workerid": worker_id},
                option=SimpleNamespace(numprocesses=2),
                add_cleanup=lambda callback: None,
            )
            root_config._start_training_runtime(config)
            workers.append(config)
            directory = Path(os.environ[training.TRAINING_RUNTIME_ENV])
            directories.append(directory)
            assert directory != caller
            assert not directory.is_relative_to(training.REPO_ROOT)
            for source, original in caller_originals.items():
                assert (directory / source.name).read_bytes() == original
            paths = training._training_artifact_paths(defaults)
            assert all(path.parent == directory for path in paths)
        assert directories[0] != directories[1]
        history_name = training.PERFORMANCE_GATE_HISTORY_PATH.name
        for index, directory in enumerate(directories):
            monkeypatch.setattr(training, "PERFORMANCE_GATE_HISTORY_PATH", directory / history_name)
            snapshot = training._record_performance_gate_history(
                performance_gate={"ok": True, "gate_verdict": "pass", "baseline_source": f"worker-{index}"},
                include_ast_context=False,
                ast_file_limit=None,
                processed_count=0,
                dataset_summary=None,
            )
            assert snapshot["artifact_path"] == str(directory / history_name)
            assert snapshot["latest"]["baseline_source"] == f"worker-{index}"
        for index, directory in enumerate(directories):
            persisted = json.loads((directory / history_name).read_text())
            assert persisted["entries"][-1]["baseline_source"] == f"worker-{index}"
    finally:
        for config in workers:
            root_config._finish_training_runtime(config)
    assert all(not directory.exists() for directory in directories)
    assert os.environ[training.TRAINING_RUNTIME_ENV] == inherited
    assert all(source.read_bytes() == original for source, original in caller_originals.items())
    assert all(path.read_bytes() == original for path, original in originals.items())


def test_xdist_worker_without_override_owns_runtime(monkeypatch):
    monkeypatch.delenv(training.TRAINING_RUNTIME_ENV)
    config = SimpleNamespace(
        workerinput={"workerid": "gw0"}, add_cleanup=lambda callback: None
    )
    root_config._start_training_runtime(config)
    directory = Path(os.environ[training.TRAINING_RUNTIME_ENV])
    assert directory.exists()
    root_config._finish_training_runtime(config)
    assert not directory.exists()
    assert training.TRAINING_RUNTIME_ENV not in os.environ


def test_subprocess_inherited_directory_remains_caller_owned(tmp_path, monkeypatch):
    # A serial nested pytest treats the inherited override as caller-owned.
    monkeypatch.delenv(training.TRAINING_RUNTIME_ENV)
    parent = SimpleNamespace(add_cleanup=lambda callback: None)
    root_config._start_training_runtime(parent)
    directory = Path(os.environ[training.TRAINING_RUNTIME_ENV])
    retained = directory / "performance_gate_history.json"
    retained.write_text('{"entries": []}')
    try:
        child = SimpleNamespace(option=SimpleNamespace(numprocesses=0))
        root_config._start_training_runtime(child)
        root_config._finish_training_runtime(child)
        assert directory.exists()
        assert retained.read_text() == '{"entries": []}'
        assert os.environ[training.TRAINING_RUNTIME_ENV] == str(directory)
    finally:
        root_config._finish_training_runtime(parent)
    assert not directory.exists()
