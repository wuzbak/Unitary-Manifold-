# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Independent CPU callable profiling evidence."""

from dataclasses import FrozenInstanceError
import json
import math
import weakref

import pytest

from src.infrastructure import performance_profile as profiler


def test_deterministic_per_invocation_clocks_and_nearest_rank(monkeypatch):
    wall = iter([10, 14, 20, 21, 30, 35, 40, 42])
    cpu = iter([10, 12, 20, 20.5, 30, 33, 40, 41])
    monkeypatch.setattr(profiler.time, "perf_counter", lambda: next(wall))
    monkeypatch.setattr(profiler.time, "process_time", lambda: next(cpu))
    calls = []
    result = profiler.profile_callable(
        lambda: calls.append(1), subject="algorithm", owner_scope="test",
        warmups=2, repetitions=4,
    )
    assert len(calls) == 6
    assert result.wall_time.samples_seconds == (4, 1, 5, 2)
    assert result.wall_time.p50_seconds == 2
    assert result.wall_time.p95_seconds == 5
    assert result.process_cpu_time.samples_seconds == (2, .5, 3, 1)
    assert result.process_cpu_time.p50_seconds == 1
    assert result.process_cpu_time.p95_seconds == 3
    assert len(result.python_peak_bytes) == 4
    assert not profiler.tracemalloc.is_tracing()


def test_nearest_rank_p95_is_not_always_maximum(monkeypatch):
    wall = iter(value for duration in range(1, 21) for value in (0, duration))
    cpu = iter(value for duration in range(1, 21) for value in (0, duration / 2))
    monkeypatch.setattr(profiler.time, "perf_counter", lambda: next(wall))
    monkeypatch.setattr(profiler.time, "process_time", lambda: next(cpu))
    result = profiler.profile_callable(
        lambda: None, subject="x", owner_scope="y", warmups=0, repetitions=20,
    )
    assert result.wall_time.p50_seconds == 10
    assert result.wall_time.p95_seconds == 19
    assert result.process_cpu_time.p50_seconds == 5
    assert result.process_cpu_time.p95_seconds == 9.5


def test_actual_callable_smoke_json_receipt_and_immutability():
    result = profiler.profile_callable(
        lambda: bytearray(32_768), subject="allocation", owner_scope="tests",
    )
    data = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    assert data["status"] == "measured"
    assert len(data["wall_time"]["samples_seconds"]) == 5
    assert all(v >= 0 for v in result.process_cpu_time.samples_seconds)
    assert min(result.python_peak_bytes) >= 32_768
    assert data["hardware"]["gpu_counters"] == {"status": "unmeasured"}
    assert data["hardware"]["architecture"]
    receipt = result.receipt()
    assert receipt.status == "measured"
    assert receipt.promotion == {"eligible": False, "automatic_promotion": False}
    json.dumps(receipt.to_dict(), allow_nan=False)
    with pytest.raises(FrozenInstanceError):
        result.config.warmups = 2
    with pytest.raises(FrozenInstanceError):
        result.hardware.system = "different"
    with pytest.raises(FrozenInstanceError):
        result.python_peak_bytes = ()
    data["memory"]["python_peak_bytes"].append(-1)
    assert -1 not in result.python_peak_bytes


@pytest.mark.parametrize("warmups,fail_at", [(0, 1), (2, 1), (2, 4)])
def test_callable_exception_propagates_and_cleans_up(warmups, fail_at, monkeypatch):
    error = LookupError("original failure")
    calls = 0
    receipts = []
    monkeypatch.setattr(profiler, "PerformanceProfile", lambda *a: receipts.append(a))

    def fail():
        nonlocal calls
        calls += 1
        if calls == fail_at:
            raise error

    with pytest.raises(LookupError) as caught:
        profiler.profile_callable(fail, subject="fail", owner_scope="tests", warmups=warmups)
    assert caught.value is error
    assert calls == fail_at
    assert not profiler.tracemalloc.is_tracing()
    assert receipts == []


def test_existing_trace_rejected_and_left_active():
    calls = []
    profiler.tracemalloc.start(7)
    try:
        with pytest.raises(RuntimeError, match="already active"):
            profiler.profile_callable(lambda: calls.append(1), subject="x", owner_scope="y")
        assert profiler.tracemalloc.is_tracing()
        assert profiler.tracemalloc.get_traceback_limit() == 7
        assert calls == []
    finally:
        profiler.tracemalloc.stop()


def test_callable_disabling_tracing_is_not_success():
    with pytest.raises(RuntimeError, match="disabled"):
        profiler.profile_callable(
            profiler.tracemalloc.stop, subject="trace-interference",
            owner_scope="tests", warmups=0,
        )
    assert not profiler.tracemalloc.is_tracing()


def test_maximum_config_boundary():
    config = profiler.ProfileConfig("x", "y", warmups=0, repetitions=10_000)
    assert config.repetitions == profiler.MAX_INVOCATIONS


@pytest.mark.parametrize("kwargs", [
    {"warmups": True}, {"warmups": False}, {"repetitions": True},
    {"repetitions": False}, {"warmups": -1}, {"repetitions": 0},
    {"warmups": 1.0}, {"repetitions": "2"}, {"warmups": None},
    {"repetitions": math.inf}, {"repetitions": 10_001},
    {"warmups": 10_000, "repetitions": 1},
    {"subject": ""}, {"subject": " \n"}, {"subject": 1},
    {"owner_scope": ""}, {"owner_scope": False}, {"owner_scope": None},
])
def test_validation_precedes_calls(kwargs):
    calls = []
    options = {"subject": "x", "owner_scope": "y", **kwargs}
    with pytest.raises(ValueError):
        profiler.profile_callable(lambda: calls.append(1), **options)
    assert calls == []
    assert not profiler.tracemalloc.is_tracing()


@pytest.mark.parametrize("fn", [None, False, 2, "callable"])
def test_noncallable_rejected(fn):
    with pytest.raises(ValueError, match="callable"):
        profiler.profile_callable(fn, subject="x", owner_scope="y")


def test_unknown_cpu_inventory_and_gpu_not_guessed(monkeypatch):
    monkeypatch.setattr(profiler.os, "cpu_count", lambda: None)
    monkeypatch.delattr(profiler.os, "sched_getaffinity", raising=False)
    result = profiler.profile_callable(lambda: None, subject="x", owner_scope="y", warmups=0)
    inventory = result.to_dict()["hardware"]
    assert inventory["logical_cpu_count"] is None
    assert inventory["logical_cpu_status"] == "unknown"
    assert inventory["affinity_cpu_count"] is None
    assert inventory["affinity_cpu_status"] == "unknown"
    assert inventory["gpu_counters"] == {"status": "unmeasured"}


def test_cpu_inventory_observed_and_unsupported(monkeypatch):
    monkeypatch.setattr(profiler.os, "cpu_count", lambda: 8)
    monkeypatch.setattr(profiler.os, "sched_getaffinity", lambda _: {2, 4}, raising=False)
    inventory = profiler._hardware_inventory()
    assert inventory.logical_cpu_count == 8
    assert inventory.affinity_cpu_count == 2

    def unsupported(*args):
        raise OSError("unsupported")

    monkeypatch.setattr(profiler.os, "cpu_count", unsupported)
    monkeypatch.setattr(profiler.os, "sched_getaffinity", unsupported)
    assert profiler._hardware_inventory().logical_cpu_count is None
    assert profiler._hardware_inventory().affinity_cpu_count is None


def test_callable_and_outputs_not_retained():
    outputs = []

    class Output:
        pass

    class Callable:
        def __call__(self):
            output = Output()
            outputs.append(weakref.ref(output))
            return output

    fn = Callable()
    reference = weakref.ref(fn)
    result = profiler.profile_callable(fn, subject="private-free", owner_scope="tests")
    del fn
    assert reference() is None
    assert len(outputs) == 6
    assert all(output() is None for output in outputs)
    assert "Output" not in json.dumps(result.to_dict())


@pytest.mark.parametrize("invalid", [math.nan, math.inf, -1.0])
def test_bad_clock_data_fails_without_receipt(monkeypatch, invalid):
    values = iter([0.0, invalid])
    monkeypatch.setattr(profiler.time, "perf_counter", lambda: next(values))
    with pytest.raises(ValueError, match="finite and nonnegative"):
        profiler.profile_callable(
            lambda: None, subject="x", owner_scope="y", warmups=0, repetitions=1,
        )
    assert not profiler.tracemalloc.is_tracing()
