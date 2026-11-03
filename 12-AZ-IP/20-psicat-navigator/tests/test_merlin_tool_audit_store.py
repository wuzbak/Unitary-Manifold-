# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from ox_navigator.engine import merlin_tools
from ox_navigator.engine.merlin_tool_audit_store import (
    MerlinToolAuditStore,
    ToolAuditStoreError,
    _digest,
)

PRODUCT_ROOT = Path(__file__).resolve().parents[1]


def _process(code: str, path: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["MERLIN_TOOL_AUDIT_STORE_PATH"] = str(path)
    env["PYTHONPATH"] = os.pathsep.join([str(PRODUCT_ROOT), str(PRODUCT_ROOT.parents[1])])
    return subprocess.run(
        [sys.executable, "-c", code], cwd=PRODUCT_ROOT, env=env,
        text=True, capture_output=True, timeout=60, check=False,
    )


def test_run_restart_read_recovery(tmp_path: Path) -> None:
    path = tmp_path / "audit.json"
    run = _process(
        "import json; from ox_navigator.engine.merlin_tools import route_tool; "
        "r = route_tool('getMerlinMemoryState'); "
        "assert r['ok']; print(json.dumps(r['audit']))",
        path,
    )
    assert run.returncode == 0, run.stderr
    run_id = json.loads(run.stdout)["run_id"]
    restarted = _process(
        "import json; "
        "from ox_navigator.engine.merlin_tool_audit_store import MerlinToolAuditStore; "
        "print(json.dumps(MerlinToolAuditStore.configured().read_records()))",
        path,
    )
    assert restarted.returncode == 0, restarted.stderr
    records = json.loads(restarted.stdout)
    assert len(records) == 1
    assert records[0]["run_id"] == run_id
    assert records[0]["tool"] == "getMerlinMemoryState"
    assert records[0]["ok"] is True
    assert records[0]["provenance"]["provider"] == "independent"
    assert path.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize(
    "corruption",
    ["truncated", "version", "digest", "record", "duplicate", "extra_field", "duplicate_field"],
)
def test_corrupt_file_fails_closed_before_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, corruption: str,
) -> None:
    path = tmp_path / "audit.json"
    monkeypatch.setenv("MERLIN_TOOL_AUDIT_STORE_PATH", str(path))
    merlin_tools.route_tool("getMerlinMemoryState")
    payload = json.loads(path.read_text())
    if corruption == "truncated":
        damaged = '{"version":'
    elif corruption == "duplicate_field":
        damaged = json.dumps(payload).replace('"version": 1', '"version": 2, "version": 1')
    else:
        if corruption == "version":
            payload["version"] = 2
        elif corruption == "digest":
            payload["digest_sha256"] = "0" * 64
        elif corruption == "record":
            payload["records"][0]["ok"] = "true"
            payload["digest_sha256"] = _digest(payload["records"])
        elif corruption == "extra_field":
            payload["records"][0]["args"] = {"api_key": "do-not-store"}
            payload["digest_sha256"] = _digest(payload["records"])
        else:
            payload["records"].append(payload["records"][0])
            payload["digest_sha256"] = _digest(payload["records"])
        damaged = json.dumps(payload)
    path.write_text(damaged)

    def forbidden(*args, **kwargs):
        pytest.fail("Tool executed despite corrupt audit store")

    monkeypatch.setattr(merlin_tools, "_route_tool", forbidden)
    with pytest.raises(ToolAuditStoreError, match="Corrupt"):
        merlin_tools.route_tool("getMerlinMemoryState")
    restarted = _process(
        "from ox_navigator.engine.merlin_tool_audit_store import MerlinToolAuditStore; "
        "MerlinToolAuditStore.configured().read_records()",
        path,
    )
    assert restarted.returncode != 0
    assert "ToolAuditStoreError" in restarted.stderr
    assert path.read_text() == damaged


def test_metadata_only_and_gates_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "audit.json"
    monkeypatch.setenv("MERLIN_TOOL_AUDIT_STORE_PATH", str(path))
    secret = "sensitive-api-key-do-not-store"
    monkeypatch.setenv("OPENROUTER_API_KEY", secret)
    denied = merlin_tools.route_tool(secret, {secret: secret})
    assert denied["ok"] is False
    gated = merlin_tools.route_tool("authorizeMerlinPrivilege", {"query": secret})
    assert gated["ok"] is False
    assert "Human gate approval required" in gated["error"]
    records = MerlinToolAuditStore(path).read_records()
    assert records[0]["tool"] == "unknown"
    assert records[1]["requires_human_gate"] is True
    assert secret not in path.read_text()
    assert "args" not in path.read_text()
    assert "result" not in path.read_text()
    assert "error" not in path.read_text()


def test_default_does_not_persist_or_change_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MERLIN_TOOL_AUDIT_STORE_PATH", raising=False)
    assert MerlinToolAuditStore.configured() is None
    response = merlin_tools.route_tool("getMerlinMemoryState")
    assert response["ok"] is True
    assert "run_id" not in response["audit"]


def test_bounded_orchestration_retains_receipts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "audit.json"
    monkeypatch.setenv("MERLIN_TOOL_AUDIT_STORE_PATH", str(path))
    response = merlin_tools.orchestrate_steps([
        {"tool": "getMerlinMemoryState", "args": {}},
        {"tool": "entity.MerlinSession.schema", "args": {}},
    ])
    assert response["ok"] is True
    records = MerlinToolAuditStore(path).read_records()
    assert [record["run_id"] for record in records] == [
        step["audit"]["run_id"] for step in response["steps"]
    ]
    with pytest.raises(ValueError, match="blocked"):
        merlin_tools.orchestrate_steps([{"tool": "authorizeMerlinPrivilege", "args": {}}])
    assert MerlinToolAuditStore(path).read_records() == records


def test_failed_replace_preserves_prior_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "audit.json"
    monkeypatch.setenv("MERLIN_TOOL_AUDIT_STORE_PATH", str(path))
    merlin_tools.route_tool("getMerlinMemoryState")
    previous = path.read_bytes()

    def fail_replace(*args):
        raise OSError("simulated disk failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(ToolAuditStoreError):
        merlin_tools.route_tool("getMerlinMemoryState")
    assert path.read_bytes() == previous
    assert not list(tmp_path.glob("*.pending"))
    assert not list(tmp_path.glob(".*.pending"))


def test_concurrent_processes_retain_all_receipts(tmp_path: Path) -> None:
    path = tmp_path / "audit.json"
    env = dict(os.environ, MERLIN_TOOL_AUDIT_STORE_PATH=str(path), PYTHONPATH=str(PRODUCT_ROOT))
    code = (
        "from ox_navigator.engine.merlin_tools import route_tool; "
        "assert route_tool('getMerlinMemoryState')['ok']"
    )
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", code], cwd=PRODUCT_ROOT, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        for _ in range(3)
    ]
    for process in processes:
        stdout, stderr = process.communicate(timeout=60)
        assert process.returncode == 0, stdout + stderr
    records = MerlinToolAuditStore(path).read_records()
    assert len(records) == 3
    assert len({record["run_id"] for record in records}) == 3


def test_configuration_requires_absolute_location(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MERLIN_TOOL_AUDIT_STORE_PATH", "audit.json")
    with pytest.raises(ToolAuditStoreError, match="absolute"):
        MerlinToolAuditStore.configured()
