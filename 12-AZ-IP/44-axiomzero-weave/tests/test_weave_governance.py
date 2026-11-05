# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Before-effect invariants and recovery, without real external effects."""

from concurrent.futures import ThreadPoolExecutor
import errno
import multiprocessing
import os
from pathlib import Path
import subprocess
import sys
import time
import types

import pytest

from az_weave import OBLIGATIONS
from az_weave.governance import AuthorizationError, Journal, _acquire_executor_lock

PASS = {key: "PASS" for key in OBLIGATIONS}


@pytest.fixture
def journal(tmp_path):
    return Journal(tmp_path / "state" / "journal.sqlite")


def approve(journal, **overrides):
    return journal.approve("operator", "effect", {"target": "one"}, obligations=overrides or PASS, sources=[])


@pytest.mark.parametrize("verdict", ["UNKNOWN", "PENDING", "FAIL", True, 1, None])
def test_independent_obligation_veto(journal, verdict):
    obligations = {**PASS, "NO_HARM": verdict}
    with pytest.raises(AuthorizationError):
        approve(journal, **obligations)


def test_no_aggregate_can_substitute(journal):
    with pytest.raises(AuthorizationError):
        journal.approve("operator", "effect", {}, obligations={"omega": 1.0}, sources=[])


@pytest.mark.parametrize("principal,action,args", [
    ("intruder", "effect", {"target": "one"}),
    ("operator", "publish", {"target": "one"}),
    ("operator", "effect", {"target": "other"}),
])
def test_exact_binding(journal, principal, action, args):
    identifier = approve(journal)
    with pytest.raises(AuthorizationError):
        journal.execute(identifier, principal, action, args, lambda: pytest.fail("unauthorized"), lambda _: True)


def test_replay_is_persisted_not_reexecuted(journal):
    identifier = approve(journal)
    calls = []
    def effect():
        calls.append(True)
        return {"actual": 1}
    first = journal.execute(identifier, "operator", "effect", {"target": "one"}, effect, lambda _: True)
    restarted = Journal(journal.path)
    replay = restarted.execute(identifier, "operator", "effect", {"target": "one"}, effect, lambda _: True)
    assert first["replayed"] is False
    assert replay["replayed"] is True
    assert len(calls) == 1
    assert restarted.verify_audit()


def test_concurrent_claim_runs_at_most_once(journal):
    identifier = approve(journal)
    calls = []
    def request():
        try:
            return journal.execute(identifier, "operator", "effect", {"target": "one"},
                                   lambda: calls.append(1) or {"done": True}, lambda _: True)["state"]
        except AuthorizationError:
            return "CLAIMED"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: request(), range(2)))
    assert "SUCCEEDED" in results and len(calls) == 1


def test_exception_after_effect_is_ambiguous(journal):
    identifier = approve(journal)
    def interrupted():
        raise OSError("external effect outcome cannot be established")
    with pytest.raises(OSError):
        journal.execute(identifier, "operator", "effect", {"target": "one"}, interrupted, lambda _: True)
    assert journal.get(identifier, "operator")["state"] == "AMBIGUOUS"
    with pytest.raises(AuthorizationError):
        journal.execute(identifier, "operator", "effect", {"target": "one"},
                        lambda: pytest.fail("automatic retry"), lambda _: True)
    journal.reconcile(identifier, "operator", resolution="CONFIRMED_NO_EFFECT")
    assert journal.get(identifier, "operator")["state"] == "CONFIRMED_NO_EFFECT"


def test_interrupted_process_is_not_implicitly_recovered(journal):
    identifier = approve(journal)
    with journal.connect() as db:
        db.execute("UPDATE decisions SET state='RUNNING' WHERE id=?", (identifier,))
    restarted = Journal(journal.path)
    with pytest.raises(AuthorizationError):
        restarted.execute(identifier, "operator", "effect", {"target": "one"},
                          lambda: pytest.fail("unsafe retry"), lambda _: True)
    restarted.reconcile(identifier, "operator", resolution="CONFIRMED_EFFECT")


@pytest.mark.parametrize("case", ["expired", "revoked", "stale"])
def test_invalid_approval_has_zero_effects(journal, case):
    identifier = approve(journal)
    if case == "expired":
        with journal.connect() as db:
            db.execute("UPDATE decisions SET expires=? WHERE id=?", (time.time() - 1, identifier))
    if case == "revoked":
        journal.revoke(identifier, "operator")
    with pytest.raises(AuthorizationError):
        journal.execute(identifier, "operator", "effect", {"target": "one"},
                        lambda: pytest.fail("invalid approval ran"), lambda _: case != "stale")


def test_audit_corruption_detected(journal):
    approve(journal)
    with journal.connect() as db:
        db.execute("UPDATE events SET state='TAMPERED'")
    assert not journal.verify_audit()


@pytest.mark.parametrize("crash", [False, True])
def test_cross_process_live_executor_blocks_reconciliation_and_other_effects(journal, crash, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parent))
    from weave_process_worker import process_effect

    identifier = approve(journal)
    other = approve(journal)
    context = multiprocessing.get_context("spawn")
    started, finish = context.Event(), context.Event()
    process = context.Process(target=process_effect,
                              args=(journal.path, identifier, started, finish))
    process.start()
    try:
        assert started.wait(10)
        observer = Journal(journal.path)
        with pytest.raises(AuthorizationError, match="still running"):
            observer.reconcile(identifier, "operator", resolution="CONFIRMED_NO_EFFECT")
        with pytest.raises(AuthorizationError, match="still running"):
            observer.execute(other, "operator", "effect", {"target": "one"},
                             lambda: pytest.fail("concurrent effect"), lambda _: True)
        assert observer.get(identifier, "operator")["state"] == "RUNNING"
        if crash:
            process.terminate()
        else:
            finish.set()
        process.join(10)
        assert not process.is_alive()
        if crash:
            assert observer.get(identifier, "operator")["state"] == "RUNNING"
            observer.reconcile(identifier, "operator", resolution="CONFIRMED_EFFECT")
            assert observer.get(identifier, "operator")["state"] == "CONFIRMED_EFFECT"
        else:
            assert process.exitcode == 0
            assert observer.get(identifier, "operator")["state"] == "SUCCEEDED"
            with pytest.raises(AuthorizationError, match="no ambiguous"):
                observer.reconcile(identifier, "operator", resolution="CONFIRMED_NO_EFFECT")
        assert observer.execute(other, "operator", "effect", {"target": "one"},
                                lambda: {"second": True}, lambda _: True)["state"] == "SUCCEEDED"
        assert observer.verify_audit()
    finally:
        if process.is_alive():
            process.terminate()
        process.join(10)


@pytest.mark.parametrize("failure", [False, True])
def test_completion_cannot_overwrite_changed_resolution(journal, failure):
    identifier = approve(journal)

    def handler():
        with journal.connect() as db:
            db.execute("UPDATE decisions SET state='CONFIRMED_EFFECT' WHERE id=?", (identifier,))
        if failure:
            raise OSError("failure after concurrent state change")
        return {"done": True}

    with pytest.raises(AuthorizationError, match="state changed"):
        journal.execute(identifier, "operator", "effect", {"target": "one"}, handler, lambda _: True)
    assert journal.get(identifier, "operator")["state"] == "CONFIRMED_EFFECT"
    with journal.connect() as db:
        assert db.execute("SELECT decision_id FROM active_effect").fetchone()[0] == identifier


def test_windows_executor_uses_nonblocking_byte_zero_lock_without_writes(tmp_path, monkeypatch):
    calls = []
    module = types.SimpleNamespace(LK_NBLCK=17, locking=lambda *args: calls.append(args))
    monkeypatch.setitem(sys.modules, "msvcrt", module)
    path = tmp_path / "executor.lock"
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        os.lseek(descriptor, 12, os.SEEK_SET)
        _acquire_executor_lock(descriptor, "nt")
        assert calls == [(descriptor, module.LK_NBLCK, 1)]
        assert os.lseek(descriptor, 0, os.SEEK_CUR) == 0
        assert path.stat().st_size == 0
    finally:
        os.close(descriptor)


@pytest.mark.parametrize("error_number", [errno.EACCES, errno.EAGAIN, errno.EDEADLK, errno.EIO])
def test_windows_executor_contention_is_distinct_from_lock_failure(tmp_path, monkeypatch, error_number):
    def locking(*_):
        raise OSError(error_number, "native locking error")

    monkeypatch.setitem(sys.modules, "msvcrt", types.SimpleNamespace(LK_NBLCK=2, locking=locking))
    descriptor = os.open(tmp_path / "executor.lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        if error_number == errno.EIO:
            with pytest.raises(OSError) as error:
                _acquire_executor_lock(descriptor, "nt")
            assert error.value.errno == errno.EIO
        else:
            with pytest.raises(AuthorizationError, match="still running"):
                _acquire_executor_lock(descriptor, "nt")
    finally:
        os.close(descriptor)


def test_unsupported_executor_platform_fails_closed():
    with pytest.raises(RuntimeError, match="unsupported"):
        _acquire_executor_lock(-1, "unsupported-platform")


def test_failed_lock_acquisition_closes_descriptor_without_claiming(journal, monkeypatch):
    import az_weave.governance as governance

    descriptors = []

    def denied(descriptor, platform):
        descriptors.append(descriptor)
        raise AuthorizationError("executor is still running")

    monkeypatch.setattr(governance, "_acquire_executor_lock", denied)
    identifier = approve(journal)
    with pytest.raises(AuthorizationError, match="still running"):
        journal.execute(identifier, "operator", "effect", {"target": "one"},
                        lambda: pytest.fail("unlocked effect"), lambda _: True)
    assert len(descriptors) == 1
    with pytest.raises(OSError) as error:
        os.fstat(descriptors[0])
    assert error.value.errno == errno.EBADF
    assert journal.get(identifier, "operator")["state"] == "APPROVED"


def test_readonly_api_imports_without_any_platform_lock_module(tmp_path):
    product = Path(__file__).resolve().parents[1]
    root = product.parents[1]
    code = """
import builtins
import pathlib
import subprocess
import sys
product, root = sys.argv[1:]
sys.path.insert(0, product)
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name in {"fcntl", "msvcrt"}:
        raise ImportError("platform lock module deliberately unavailable")
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
from az_weave.api import capabilities, compute_readonly
assert capabilities(pathlib.Path(root), checkpoints={})["product"] == 44
assert compute_readonly("geometry", {}, repo_root=pathlib.Path(root))["alias_period"] == 74
assert not pathlib.Path(".axiomzero-weave").exists()
"""
    result = subprocess.run([sys.executable, "-c", code, str(product), str(root)],
                            cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
