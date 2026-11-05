# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import types

import pytest

from ox_navigator.engine import merlin_tool_audit_store, merlin_tools
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
    if os.name == "posix":
        assert path.stat().st_mode & 0o777 == 0o600
    else:
        # Windows ignores POSIX mode bits; privacy relies on the directory ACL (README).
        assert os.access(path, os.R_OK | os.W_OK)


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
    payload = json.loads(path.read_text(encoding="utf-8"))
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
    path.write_text(damaged, encoding="utf-8")

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
    assert path.read_text(encoding="utf-8") == damaged


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
    assert secret not in path.read_text(encoding="utf-8")
    assert "args" not in path.read_text(encoding="utf-8")
    assert "result" not in path.read_text(encoding="utf-8")
    assert "error" not in path.read_text(encoding="utf-8")


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
    env = dict(
        os.environ,
        MERLIN_TOOL_AUDIT_STORE_PATH=str(path),
        PYTHONPATH=os.pathsep.join([str(PRODUCT_ROOT), str(PRODUCT_ROOT.parents[1])]),
    )
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


class _FakeMsvcrt(types.ModuleType):
    LK_NBLCK = 2
    LK_UNLCK = 0

    def __init__(self, failures: list[int]) -> None:
        super().__init__("msvcrt")
        self.failures = list(failures)
        self.calls: list[tuple[int, int, int]] = []

    def locking(self, descriptor: int, mode: int, size: int) -> None:
        assert os.lseek(descriptor, 0, os.SEEK_CUR) == 0
        self.calls.append((descriptor, mode, size))
        if mode == self.LK_NBLCK and self.failures:
            code = self.failures.pop(0)
            raise OSError(code, os.strerror(code))


def _lock_fd(tmp_path: Path) -> int:
    fd = os.open(tmp_path / "audit.json.lock", os.O_CREAT | os.O_RDWR, 0o600)
    os.write(fd, b"x")
    return fd


def test_windows_lock_waits_through_contention_then_unlocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeMsvcrt([errno.EACCES, errno.EDEADLK])
    monkeypatch.setitem(sys.modules, "msvcrt", fake)
    sleeps: list[float] = []
    monkeypatch.setattr(merlin_tool_audit_store.time, "sleep", sleeps.append)
    fd = _lock_fd(tmp_path)
    try:
        merlin_tool_audit_store._acquire_lock(fd, "nt")
        assert [call[1:] for call in fake.calls] == [(2, 1)] * 3
        assert len(sleeps) == 2
        merlin_tool_audit_store._release_lock(fd, "nt")
        assert fake.calls[-1][1:] == (0, 1)
    finally:
        os.close(fd)


def test_windows_lock_propagates_unexpected_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeMsvcrt([errno.EBADF])
    monkeypatch.setitem(sys.modules, "msvcrt", fake)
    monkeypatch.setattr(merlin_tool_audit_store.time, "sleep", lambda _: pytest.fail("retried"))
    fd = _lock_fd(tmp_path)
    try:
        with pytest.raises(OSError) as raised:
            merlin_tool_audit_store._acquire_lock(fd, "nt")
        assert raised.value.errno == errno.EBADF
    finally:
        os.close(fd)


def test_unsupported_platform_fails_closed(tmp_path: Path) -> None:
    fd = _lock_fd(tmp_path)
    try:
        with pytest.raises(ToolAuditStoreError, match="unsupported"):
            merlin_tool_audit_store._acquire_lock(fd, "java")
    finally:
        os.close(fd)


def test_store_uses_windows_lock_and_preserves_primary_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeMsvcrt([])
    monkeypatch.setitem(sys.modules, "msvcrt", fake)
    acquired: list[str] = []
    real_acquire = merlin_tool_audit_store._acquire_lock

    def acquire(descriptor: int, platform: str) -> None:
        acquired.append(platform)
        real_acquire(descriptor, "nt")

    original_release = merlin_tool_audit_store._release_lock

    def release(descriptor: int, platform: str) -> None:
        original_release(descriptor, "nt")
        raise OSError(errno.EIO, "unlock failed")

    monkeypatch.setattr(merlin_tool_audit_store, "_acquire_lock", acquire)
    monkeypatch.setattr(merlin_tool_audit_store, "_release_lock", release)
    store = MerlinToolAuditStore(tmp_path / "audit.json")
    (tmp_path / "audit.json").write_text('{"version":', encoding="utf-8")
    with pytest.raises(ToolAuditStoreError, match="Corrupt"):
        store.read_records()
    assert acquired == [os.name]
    assert [call[1] for call in fake.calls] == [fake.LK_NBLCK, fake.LK_UNLCK]
    with pytest.raises(ToolAuditStoreError, match="persistence failed"):
        with store._locked():
            pass


def test_lock_excludes_concurrent_processes(tmp_path: Path) -> None:
    path = tmp_path / "audit.json"
    marker = tmp_path / "holder-ready"
    env = dict(
        os.environ,
        MERLIN_TOOL_AUDIT_STORE_PATH=str(path),
        PYTHONPATH=os.pathsep.join([str(PRODUCT_ROOT), str(PRODUCT_ROOT.parents[1])]),
    )
    holder = subprocess.Popen(
        [
            sys.executable, "-c",
            "import pathlib, sys; "
            "from ox_navigator.engine.merlin_tool_audit_store import MerlinToolAuditStore as S; "
            "s = S.configured(); cm = s._locked(); cm.__enter__(); "
            f"pathlib.Path({str(marker)!r}).write_text('1'); sys.stdin.readline(); "
            "cm.__exit__(None, None, None)",
        ],
        cwd=PRODUCT_ROOT, env=env, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        for _ in range(600):
            if marker.exists() or holder.poll() is not None:
                break
            time.sleep(0.05)
        assert marker.exists(), holder.stderr.read() if holder.poll() is not None else "holder not ready"
        waiter = subprocess.Popen(
            [
                sys.executable, "-c",
                "from ox_navigator.engine.merlin_tool_audit_store import MerlinToolAuditStore as S; "
                "print(S.configured().read_records())",
            ],
            cwd=PRODUCT_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        with pytest.raises(subprocess.TimeoutExpired):
            waiter.communicate(timeout=1.5)
        holder.stdin.write("\n")
        holder.stdin.flush()
        stdout, stderr = waiter.communicate(timeout=60)
        assert waiter.returncode == 0, stderr
        assert stdout.strip() == "[]"
    finally:
        holder.stdin.close()
        holder.wait(timeout=60)
        for stream in (holder.stdout, holder.stderr):
            stream.close()
    assert holder.returncode == 0
