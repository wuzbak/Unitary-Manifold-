# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Local, provider-independent contracts for durable task recovery."""

import asyncio
from contextlib import ExitStack
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from AxiomZero.core.agent_core import AxiomZeroOrchestrator, EpistemicLabel


def _orchestrator(tmp_path):
    root = Path(__file__).resolve().parents[1]
    return AxiomZeroOrchestrator(
        config={"state_db": str(tmp_path / "state.db")},
        repo_root=root,
    )


def test_staged_product_runs_without_symlinks_and_uses_repository_root(tmp_path):
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    source = Path(__file__).resolve().parents[1]
    product = tmp_path / "repo" / "12-AZ-IP" / "01-axiom-os"

    def ignore_links(directory, names):
        return {
            name for name in names
            if (Path(directory) / name).is_symlink() or name in {"tests", "__pycache__"}
        }

    shutil.copytree(source, product, ignore=ignore_links)
    home = tmp_path / "home"
    home.mkdir()
    script = """
from pathlib import Path
import json
from fastapi.testclient import TestClient
from AxiomZero.core.agent_core import AxiomZeroOrchestrator
from AxiomZero.memory.vector_store import VectorStore
from AxiomZero.api.server import create_app

root = Path.cwd().parents[1]
assert AxiomZeroOrchestrator.from_config().repo_root == root
assert VectorStore.from_config().repo_root == root
override = Path.cwd() / 'explicit-config.json'
override.write_text(json.dumps({'repo_root': str(Path.cwd()), 'state_db': str(Path.cwd() / 'state.db')}))
assert AxiomZeroOrchestrator.from_config(override).repo_root == Path.cwd()
assert VectorStore.from_config(override).repo_root == Path.cwd()
with TestClient(create_app()) as client:
    assert client.get('/health').status_code == 200
    status = client.get('/status')
    assert status.status_code == 200
    assert set(status.json()['managers']) == {'m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7'}
"""
    subprocess.run(
        [sys.executable, "-c", script],
        cwd=product,
        env={**os.environ, "PYTHONPATH": str(product), "HOME": str(home), "USERPROFILE": str(home)},
        check=True,
        timeout=60,
    )


def test_interrupted_task_is_restored_and_retried_with_same_id(tmp_path):
    first_process = _orchestrator(tmp_path)
    queued = first_process.queue_task(
        "Check local repository state",
        epistemic_label=EpistemicLabel.GOVERNANCE,
        payload={"scope": "local", "attempt": 1},
        max_cycles=3,
    )

    # Model a process stopping after the durable running transition was written.
    queued.status = "running"
    first_process._persist_task(queued)

    restarted_process = _orchestrator(tmp_path)
    restored = restarted_process.get_task(queued.task_id)
    assert restored is not None
    assert restored.status == "interrupted"
    assert restored.description == queued.description
    assert restored.epistemic_label == EpistemicLabel.GOVERNANCE
    assert restored.payload == {"scope": "local", "attempt": 1}
    assert [task.task_id for task in restarted_process.restartable_tasks()] == [queued.task_id]

    manager_results = {
        "m1": {"status": "ok"},
        "m2": {"status": "ok"},
        "m3": {"verified": None, "status": "adjacent_track_acknowledged"},
        "m4": {"tests_passed": True},
        "m5": {"status": "ok"},
        "m6": {"status": "offline", "papers": []},
        "m7": {"status": "ok"},
    }
    with ExitStack() as patches:
        for key, result in manager_results.items():
            patches.enter_context(
                patch.object(
                    restarted_process.managers[key],
                    "run",
                    new=AsyncMock(return_value=result),
                )
            )
        finished = asyncio.run(
            restarted_process.run_task(
                description=restored.description,
                task_id=queued.task_id,
            )
        )

    assert finished.task_id == queued.task_id
    assert finished.status == "complete"
    assert finished.results["route"] == ["m5", "m1", "m2", "m3", "m4", "m6", "m7"]

    final_process = _orchestrator(tmp_path)
    durable = final_process.get_task(queued.task_id)
    assert durable is not None
    assert durable.status == "complete"
    assert durable.results["route"] == finished.results["route"]
    assert final_process.restartable_tasks() == []


def test_task_id_collision_does_not_overwrite_durable_history(tmp_path, monkeypatch):
    orchestrator = _orchestrator(tmp_path)
    collision_id = uuid.UUID("11111111-1111-4111-8111-111111111111")
    monkeypatch.setattr("AxiomZero.core.agent_core.uuid.uuid4", lambda: collision_id)
    first = orchestrator.queue_task("First durable task", payload={"owner": "first"})
    first_record = orchestrator._state_store.get_task_record(first.task_id)

    with pytest.raises(sqlite3.IntegrityError):
        orchestrator.queue_task("Second task must not replace the first")
    with pytest.raises(sqlite3.IntegrityError):
        asyncio.run(orchestrator.run_task("Direct task must not replace the first"))

    assert first.task_id == collision_id.hex
    assert orchestrator._state_store.get_task_record(first.task_id) == first_record
    assert [task.task_id for task in orchestrator.list_tasks()] == [first.task_id]


def test_hils_approval_survives_restart(tmp_path):
    first_process = _orchestrator(tmp_path)
    task = first_process.queue_task("Review a protected operation")
    task.status = "human_review"
    task.requires_human_approval = True
    first_process._persist_task(task)

    restarted_process = _orchestrator(tmp_path)
    assert [item.task_id for item in restarted_process.pending_approvals()] == [task.task_id]
    approved = asyncio.run(restarted_process.approve_task(task.task_id, approved=True))
    assert approved.status == "complete"

    final_process = _orchestrator(tmp_path)
    restored = final_process.get_task(task.task_id)
    assert restored is not None
    assert restored.status == "complete"
    assert restored.results["human_approved"] is True
    decisions = final_process._state_store.get_hils_decisions(task.task_id)
    assert [item["decision"] for item in decisions] == ["approved"]


def test_api_submission_persists_and_returns_the_executed_task_id(tmp_path):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    orchestrator = _orchestrator(tmp_path)
    manager_results = {
        "m1": {"status": "ok"},
        "m2": {"status": "ok"},
        "m3": {"verified": None, "status": "adjacent_track_acknowledged"},
        "m4": {"tests_passed": True},
        "m5": {"status": "ok"},
        "m6": {"status": "offline", "papers": []},
        "m7": {"status": "ok"},
    }
    with ExitStack() as patches:
        for key, result in manager_results.items():
            patches.enter_context(
                patch.object(
                    orchestrator.managers[key],
                    "run",
                    new=AsyncMock(return_value=result),
                )
            )
        patches.enter_context(
            patch(
                "AxiomZero.api.server.AxiomZeroOrchestrator.from_config",
                return_value=orchestrator,
            )
        )
        from AxiomZero.api.server import create_app

        with TestClient(create_app()) as client:
            response = client.post(
                "/tasks",
                json={
                    "description": "Check local repository state",
                    "epistemic_label": "GOVERNANCE",
                    "payload": {"scope": "local"},
                    "max_cycles": 2,
                },
            )
            assert response.status_code == 202
            task_id = response.json()["task_id"]
            detail = client.get(f"/tasks/{task_id}")
            assert detail.status_code == 200
            assert detail.json()["task_id"] == task_id
            assert detail.json()["status"] == "complete"

    saved = orchestrator._state_store.get_task_record(task_id)
    assert saved is not None
    assert saved["status"] == "complete"
    assert saved["payload"] == {"scope": "local"}


def test_api_startup_retries_interrupted_task(tmp_path):
    crashed_process = _orchestrator(tmp_path)
    interrupted = crashed_process.queue_task(
        "Recover after process restart",
        epistemic_label=EpistemicLabel.GOVERNANCE,
    )
    interrupted.status = "running"
    crashed_process._persist_task(interrupted)

    restarted_process = _orchestrator(tmp_path)
    assert restarted_process.get_task(interrupted.task_id).status == "interrupted"
    manager_results = {
        "m1": {"status": "ok"},
        "m2": {"status": "ok"},
        "m3": {"verified": None, "status": "adjacent_track_acknowledged"},
        "m4": {"tests_passed": True},
        "m5": {"status": "ok"},
        "m6": {"status": "offline", "papers": []},
        "m7": {"status": "ok"},
    }

    with ExitStack() as patches:
        for key, result in manager_results.items():
            patches.enter_context(
                patch.object(
                    restarted_process.managers[key],
                    "run",
                    new=AsyncMock(return_value=result),
                )
            )
        patches.enter_context(
            patch(
                "AxiomZero.api.server.AxiomZeroOrchestrator.from_config",
                return_value=restarted_process,
            )
        )
        from AxiomZero.api.server import create_app
        from fastapi.testclient import TestClient

        with TestClient(create_app()) as client:
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                response = client.get(f"/tasks/{interrupted.task_id}")
                if response.json()["status"] == "complete":
                    break
                time.sleep(0.01)

    assert response.json()["status"] == "complete"
    assert response.json()["task_id"] == interrupted.task_id
