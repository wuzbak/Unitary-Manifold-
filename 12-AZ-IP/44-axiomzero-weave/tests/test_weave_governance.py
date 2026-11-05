# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Before-effect invariants and recovery, without real external effects."""

from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import time

import pytest

from az_weave import OBLIGATIONS
from az_weave.governance import AuthorizationError, Journal

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


def _process_effect(path, identifier, started, finish):
    journal = Journal(path)

    def handler():
        started.set()
        if not finish.wait(15):
            raise RuntimeError("test handler timeout")
        return {"actual": 1}

    journal.execute(identifier, "operator", "effect", {"target": "one"}, handler, lambda _: True)


@pytest.mark.parametrize("crash", [False, True])
def test_cross_process_live_executor_blocks_reconciliation_and_other_effects(journal, crash):
    identifier = approve(journal)
    other = approve(journal)
    context = multiprocessing.get_context("spawn")
    started, finish = context.Event(), context.Event()
    process = context.Process(target=_process_effect,
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
