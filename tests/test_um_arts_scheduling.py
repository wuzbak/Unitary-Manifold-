# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Historical timing hints must not imply historical test evidence reuse."""

import json
from pathlib import Path

import pytest
from TOOLS.um_arts.adapters import load_config
from TOOLS.um_arts.engine import balanced_jobs
from TOOLS.um_arts.evidence import EvidenceError, Index

from TOOLS.um_arts import engine


def record(index, tmp_path, status="passed"):
    compatibility = dict.fromkeys(["source", "git", "environment", "settings", "engine"], "first")
    attempt = tmp_path / "attempt"
    attempt.mkdir()
    (attempt / "attempt.json").write_text(json.dumps({
        "id": "one", "compatibility": compatibility}))
    index.record(attempt, {"status": status, "durations": {"tests/test_a.py::test_ok": 12.0}})
    return compatibility


def test_timing_hints_survive_revision_changes_only(tmp_path):
    index = Index(tmp_path / "store")
    compatibility = record(index, tmp_path)
    next_revision = {**compatibility, "source": "new bytes", "git": "new revision"}
    assert index.durations(next_revision) == {"tests/test_a.py::test_ok": 12.0}
    # Run identities in the index retain exact provenance.
    import sqlite3

    with sqlite3.connect(index.path) as db:
        assert db.execute("SELECT count(*) FROM attempts").fetchone()[0] == 1


@pytest.mark.parametrize("field", ["environment", "settings", "engine"])
def test_timing_profile_does_not_cross_execution_contexts(tmp_path, field):
    index = Index(tmp_path / "store")
    compatibility = record(index, tmp_path)
    assert index.durations({**compatibility, field: "changed"}) == {}


def test_blocked_runs_do_not_publish_successful_duration_profiles(tmp_path):
    index = Index(tmp_path / "store")
    compatibility = record(index, tmp_path, status="blocked")
    assert index.durations(compatibility) == {}


def test_large_suites_have_fine_grained_bounded_checkpoints():
    nodes = [f"test_{index}.py::test_ok" for index in range(100)]
    suite = {"name": "unit", "nodes": nodes, "serial": False}
    jobs = balanced_jobs([suite], 2, {nodes[0]: 10000}, files_per_job=8)
    assert len(jobs) > 2
    assert sorted(node for job in jobs for node in job["nodes"]) == sorted(nodes)
    assert all(len({node.split("::")[0] for node in job["nodes"]}) <= 8 for job in jobs)
    suite["serial"] = True
    assert len(balanced_jobs([suite], 2, {}, files_per_job=8)) == 1


@pytest.mark.parametrize("value", [True, 0, -1, 1025, 1.5, "32"])
def test_invalid_checkpoint_granularity_is_rejected(tmp_path, value):
    (tmp_path / "tests").mkdir()
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "adapter": "generic", "suites": [{"name": "unit", "paths": ["tests"]}],
        "files_per_job": value}))
    with pytest.raises(EvidenceError, match="files_per_job"):
        load_config(tmp_path, config, "generic")


@pytest.mark.parametrize("value", [True, None, 0, -1, 86401, float("inf"), "600"])
def test_invalid_collection_timeout_is_rejected(tmp_path, value):
    (tmp_path / "tests").mkdir()
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "adapter": "generic", "suites": [{"name": "unit", "paths": ["tests"]}],
        "collection_timeout_seconds": value}))
    with pytest.raises(EvidenceError):
        load_config(tmp_path, config, "generic")


def test_collection_timeout_is_optional_and_explicit_budget_changes_settings(tmp_path):
    (tmp_path / "tests").mkdir()
    path = tmp_path / "config.json"
    raw = {"adapter": "generic", "timeout_seconds": 10,
           "suites": [{"name": "unit", "paths": ["tests"]}]}
    path.write_text(json.dumps(raw))
    old = load_config(tmp_path, path, "generic")
    assert "collection_timeout_seconds" not in old
    path.write_text(json.dumps({**raw, "collection_timeout_seconds": 600}))
    new = load_config(tmp_path, path, "generic")
    assert new["collection_timeout_seconds"] == 600
    assert {k: v for k, v in new.items() if k != "collection_timeout_seconds"} == old


@pytest.mark.parametrize("collect,explicit,expected", [
    (True, False, 10), (False, False, 10), (True, True, 600), (False, True, 10),
])
def test_collection_and_execution_use_independent_timeouts(tmp_path, monkeypatch, collect, explicit, expected):
    root = tmp_path / "root"
    root.mkdir()
    (root / "tests").mkdir()
    (root / "tests" / "test_one.py").write_text("def test_one(): pass\n")
    (root / "pytest.ini").write_text("[pytest]\n")
    suite = {"name": "unit", "paths": ["tests"], "serial": False}
    config = {"pytest_args": [], "timeout_seconds": 10}
    if explicit:
        config["collection_timeout_seconds"] = 600
    timeouts = []
    monkeypatch.setattr(engine, "execute",
                        lambda command, cwd, directory, timeout, environment: timeouts.append(timeout))
    engine._pytest(root, tmp_path / "job", suite, config,
                   None if collect else ["tests/test_one.py::test_one"])
    assert timeouts == [expected]


@pytest.mark.parametrize("serial", [False, True])
def test_independent_execution_does_not_recollect_whole_large_suite(tmp_path, monkeypatch, serial):
    root = tmp_path / "root"
    root.mkdir()
    (root / "tests").mkdir()
    (root / "tests" / "test_one.py").write_text("def test_one(): pass\n")
    (root / "pytest.ini").write_text("[pytest]\n")
    suite = {"name": "unit", "paths": ["tests"], "serial": serial}
    directory = tmp_path / "job"
    commands = []
    monkeypatch.setattr(engine, "execute", lambda command, *args, **kwargs: commands.append(command))
    engine._pytest(root, directory, suite, {"pytest_args": [], "timeout_seconds": 10},
                   ["tests/test_one.py::test_one"])
    request = json.loads((directory / "request.json").read_text())
    assert request["collection_scope"] == ("suite" if serial else "assigned_files")
    assert ("tests" in commands[0]) is serial
    assert ("tests/test_one.py" in commands[0]) is not serial


def test_real_fine_grained_run_reconciles_all_files_and_declared_skips(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "tests").mkdir()
    for index in range(4):
        (root / "tests" / f"test_{index}.py").write_text(f"def test_{index}(): assert True\n")
    (root / "tests" / "test_optional.py").write_text(
        "import pytest\npytest.skip('optional module', allow_module_level=True)\n")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "adapter": "generic", "workers": 2, "files_per_job": 1,
        "suites": [{"name": "unit", "paths": ["tests"]}]}))
    planned = engine.plan(root, tmp_path / "store", config, adapter="generic")
    assert planned["status"] == "ready", planned
    result = engine.run(Path(planned["plan_path"]))
    assert result["status"] == "passed", result
    report = engine.evaluate(Path(result["attempt_path"]))
    assert len(report["jobs"]) == 4
    assert report["counts"] == {"passed": 4}
    assert report["selected"] == report["reconciled"] == 4
    assert report["collection_skips"] == {"unit": ["tests/test_optional.py"]}


@pytest.mark.parametrize("value", [True, 0, -1, 1.5, "2"])
def test_invalid_invocation_budget_is_rejected_before_reading_plan(tmp_path, value):
    with pytest.raises(EvidenceError, match="max_jobs"):
        engine.run(tmp_path / "missing" / "plan.json", max_jobs=value)


def test_scheduling_history_is_published_only_after_complete_write(tmp_path, monkeypatch):
    path = tmp_path / "dispatch" / "suite.json"

    def interrupted(destination, value):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("{")
        raise KeyboardInterrupt

    monkeypatch.setattr(engine, "write_json", interrupted)
    with pytest.raises(KeyboardInterrupt):
        engine._write_scheduling_receipt(path, {"attempted_jobs": ["unit-000"]})
    assert not path.exists()
    assert path.with_name("suite.json.pending").read_text() == "{"


def test_budgeted_slices_reuse_successes_and_preserve_dependency_order(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "tests").mkdir()
    for index in range(3):
        (root / "tests" / f"test_{index}.py").write_text(f"def test_{index}(): assert True\n")
    (root / "integration").mkdir()
    (root / "integration" / "test_final.py").write_text("def test_final(): assert True\n")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "adapter": "generic", "workers": 2, "files_per_job": 1,
        "suites": [{"name": "unit", "paths": ["tests"]},
                   {"name": "integration", "paths": ["integration"],
                    "requires": ["unit"], "serial": True}]}))
    planned = engine.plan(root, tmp_path / "store", config, adapter="generic")
    assert planned["status"] == "ready"
    calls = []
    original = engine._checkpoint_job

    def record(*args, **kwargs):
        destination = args[2]
        attempt = destination.parent.parent
        assert (attempt / "scheduling_history.json").is_file()
        dispatched = json.loads((attempt / "dispatch" / f"{args[3]['name']}.json").read_text())
        assert destination.name in dispatched["attempted_jobs"]
        calls.append(args[2].name)
        return original(*args, **kwargs)

    monkeypatch.setattr(engine, "_checkpoint_job", record)
    first = engine.run(Path(planned["plan_path"]), max_jobs=1)
    first_path = Path(first["attempt_path"])
    first_manifest = (first_path / "manifest.json").read_bytes()
    assert first["status"] == "blocked"
    assert first["counts"] == {"passed": 1}
    assert first["executed_jobs"] == 1
    assert first["deferred_jobs"] == 2
    assert not (first_path / "jobs" / "integration-000").exists()
    assert any("budget exhausted" in error for error in first["errors"])
    second = engine.resume(first_path, max_jobs=2)
    assert second["status"] == "blocked"
    assert second["counts"] == {"passed": 3}
    assert second["executed_jobs"] == 2
    assert second["deferred_jobs"] == 1
    second_path = Path(second["attempt_path"])
    assert not (second_path / "jobs" / "integration-000").exists()
    third = engine.resume(second_path, max_jobs=1)
    assert third["status"] == "passed", third
    assert third["counts"] == {"passed": 4}
    assert third["executed_jobs"] == 1
    assert third["deferred_jobs"] == 0
    assert len(calls) == len(set(calls)) == 4
    assert calls[-1] == "integration-000"
    assert (first_path / "manifest.json").read_bytes() == first_manifest
    third_path = Path(third["attempt_path"])
    verified = engine.evaluate(third_path)
    assert verified["reconciled"] == verified["selected"] == 4
    assert verified["compatibility"] == engine.evaluate(first_path)["compatibility"]
    completed = engine.resume(third_path, max_jobs=1)
    assert completed["status"] == "passed"
    assert completed["executed_jobs"] == 0
    assert len(calls) == 4


def test_budgeted_failure_does_not_starve_never_executed_jobs(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "tests").mkdir()
    for name in ["a", "b"]:
        (root / "tests" / f"test_{name}.py").write_text(
            f"def test_{name}(): assert False\n")
    (root / "independent").mkdir()
    (root / "independent" / "test_c.py").write_text("def test_c(): assert True\n")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "adapter": "generic", "workers": 1, "files_per_job": 1,
        "suites": [{"name": "unit", "paths": ["tests"]},
                   {"name": "independent", "paths": ["independent"]}]}))
    planned = engine.plan(root, tmp_path / "store", config, adapter="generic")
    first = engine.run(Path(planned["plan_path"]), max_jobs=1)
    second = engine.resume(Path(first["attempt_path"]), max_jobs=1)
    inherited = json.loads((Path(second["attempt_path"]) / "scheduling_history.json").read_text())
    assert inherited["attempted_jobs"] == ["unit-000"]
    third = engine.resume(Path(second["attempt_path"]), max_jobs=1)
    assert third["status"] == "blocked"
    assert third["counts"] == {"passed": 1}
    budget = json.loads((Path(third["attempt_path"]) / "execution_budget.json").read_text())
    assert budget["attempted_jobs"] == ["independent-000", "unit-000", "unit-001"]
    assert third["deferred_jobs"] == 2
