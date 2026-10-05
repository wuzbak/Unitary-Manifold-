# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from src.core.pillar_validation_scope import scoped_pillar_validity


class Proxy:
    def __init__(self, evaluate):
        self.evaluate = evaluate

    @scoped_pillar_validity
    def __bool__(self):
        return bool(self.evaluate())


@pytest.mark.parametrize("value", [False, True])
def test_diamond_deduplicates_both_truth_values_and_refreshes(value):
    calls = []
    leaf = Proxy(lambda: calls.append(value) or value)
    left = Proxy(lambda: bool(leaf))
    right = Proxy(lambda: bool(leaf))
    root = Proxy(lambda: [bool(left), bool(right)] == [True, True])
    assert bool(root) is value
    assert calls == [value]
    leaf.evaluate = lambda: calls.append(not value) or not value
    assert bool(root) is not value
    assert calls == [value, not value]


def test_exception_cleans_scope_and_is_retryable():
    def fail():
        raise ValueError("unavailable evidence")

    leaf = Proxy(fail)
    root = Proxy(lambda: bool(leaf))
    with pytest.raises(ValueError, match="unavailable"):
        bool(root)
    leaf.evaluate = lambda: True
    assert bool(root)


def test_cycle_fails_closed_and_next_call_refreshes():
    root = Proxy(lambda: bool(root))
    assert not root
    root.evaluate = lambda: True
    assert root


def test_real_proxy_retains_fail_closed_and_fresh_report(monkeypatch):
    from src.core import pillar1099_lane2_python_lean_translation_audit as audit

    calls = []
    def unavailable():
        calls.append(False)
        raise ValueError("missing proof")

    monkeypatch.setattr(audit, "lane2_python_lean_translation_audit", unavailable)
    root = Proxy(lambda: [bool(audit.PILLAR_VALID), bool(audit.PILLAR_VALID)] == [True, True])
    assert not root
    assert calls == [False]
    monkeypatch.setattr(audit, "lane2_python_lean_translation_audit", lambda: {"valid": True})
    assert root


def test_independent_threads_do_not_share_results():
    barrier = Barrier(2)
    calls = []
    def leaf_evaluation():
        calls.append(1)
        barrier.wait(timeout=5)
        return True
    leaf = Proxy(leaf_evaluation)
    root = Proxy(lambda: [bool(leaf), bool(leaf)] == [True, True])
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(lambda _: bool(root), range(2))) == [True, True]
    assert len(calls) == 2
