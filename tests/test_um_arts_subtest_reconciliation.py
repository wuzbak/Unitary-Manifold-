# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Reconcile repeated pytest subtest call reports without weakening outcomes."""

import pytest

from TOOLS.um_arts.reconcile import check_events


NODE = "tests/test_example.py::test_subtests"


def _phase(when, outcome="passed", *, wasxfail=None):
    return {
        "nodeid": NODE,
        "when": when,
        "outcome": outcome,
        "duration": 0.0,
        "wasxfail": wasxfail,
    }


def _receipt(calls):
    return {
        "version": "1",
        "nonce": "subtest-receipt",
        "collection": [],
        "reports": [_phase("setup"), *calls, _phase("teardown")],
        "internal_errors": [],
        "selected": [NODE],
        "deselected": [],
        "partition_excluded": [],
        "exitstatus": 0,
    }


def _process():
    return {"timed_out": False, "returncode": 0}


def test_repeated_passing_subtest_calls_count_as_one_test():
    result = check_events(
        _receipt([_phase("call"), _phase("call"), _phase("call")]),
        _process(),
        "subtest-receipt",
        [NODE],
    )

    assert result["status"] == "passed"
    assert result["counts"] == {"passed": 1}


@pytest.mark.parametrize(
    ("call", "expected_count"),
    [
        (_phase("call", "failed"), "failed"),
        (_phase("call", wasxfail="unexpected success"), "xpassed"),
    ],
)
def test_repeated_subtest_calls_still_reject_failures_and_unexpected_xpasses(call, expected_count):
    result = check_events(
        _receipt([_phase("call"), call, _phase("call")]),
        _process(),
        "subtest-receipt",
        [NODE],
    )

    assert result["status"] == "blocked"
    assert result["counts"] == {expected_count: 1}
