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
