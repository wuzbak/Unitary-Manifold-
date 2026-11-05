# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Bounded in-process CPU callable measurements, not hardware qualification.

Hardware inventory does not qualify a machine or certify algorithm correctness.
Wall and process CPU timings include profiler overhead and the in-process
baseline (including other threads); they are not GPU or server latency metrics.
Tracemalloc peaks cover Python-traced allocations only, including profiler and
other-thread allocations, not native/device memory or process RSS. Each measured
invocation uses a fresh process-local tracing session; warmups are untraced.
Use exclusively: tracemalloc is process-global and must not be manipulated by
the callable or concurrent code. No outputs, callable references, or arguments
are retained. Subject and owner are caller assertions, not verified provenance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import os
import platform
import time
import tracemalloc
from typing import Callable

from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance

MAX_INVOCATIONS = 10_000


@dataclass(frozen=True)
class ProfileConfig:
    """Bounds invocation count, not runtime: callables must terminate themselves."""

    subject: str
    owner_scope: str
    warmups: int = 1
    repetitions: int = 5

    def __post_init__(self) -> None:
        for name in ("subject", "owner_scope"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be nonempty text")
        for name, minimum in (("warmups", 0), ("repetitions", 1)):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise ValueError(f"{name} must be an integer >= {minimum}")
        if self.warmups + self.repetitions > MAX_INVOCATIONS:
            raise ValueError(f"total invocations must be <= {MAX_INVOCATIONS}")


@dataclass(frozen=True)
class HardwareInventory:
    system: str
    release: str
    architecture: str
    python_version: str
    python_implementation: str
    logical_cpu_count: int | None
    affinity_cpu_count: int | None

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["logical_cpu_status"] = (
            "unknown" if self.logical_cpu_count is None else "observed"
        )
        data["affinity_cpu_status"] = (
            "unknown" if self.affinity_cpu_count is None else "observed"
        )
        data["gpu_counters"] = {"status": "unmeasured"}
        data["scope"] = "inventory only; not hardware qualification"
        return data


def _hardware_inventory() -> HardwareInventory:
    try:
        logical = os.cpu_count()
    except (OSError, NotImplementedError):
        logical = None
    affinity = None
    get_affinity = getattr(os, "sched_getaffinity", None)
    if get_affinity is not None:
        try:
            affinity = len(get_affinity(0))
        except (OSError, NotImplementedError):
            pass
    return HardwareInventory(
        platform.system() or "unknown", platform.release() or "unknown",
        platform.machine() or "unknown", platform.python_version() or "unknown",
        platform.python_implementation() or "unknown", logical, affinity,
    )


@dataclass(frozen=True)
class TimingSummary:
    """Seconds; p(q) is sorted(samples)[ceil(q * n) - 1], no interpolation."""

    samples_seconds: tuple[float, ...]

    def __post_init__(self) -> None:
        values = tuple(self.samples_seconds)
        if not values or any(
            isinstance(v, bool) or not isinstance(v, (int, float))
            or not math.isfinite(v) or v < 0 for v in values
        ):
            raise ValueError("timing samples must be nonempty, finite and nonnegative")
        object.__setattr__(self, "samples_seconds", values)

    @property
    def p50_seconds(self) -> float:
        return sorted(self.samples_seconds)[math.ceil(0.50 * len(self.samples_seconds)) - 1]

    @property
    def p95_seconds(self) -> float:
        return sorted(self.samples_seconds)[math.ceil(0.95 * len(self.samples_seconds)) - 1]

    def to_dict(self) -> dict[str, object]:
        return {
            "samples_seconds": list(self.samples_seconds),
            "p50_seconds": self.p50_seconds,
            "p95_seconds": self.p95_seconds,
            "percentile_definition": "nearest rank: sorted[ceil(q*n)-1]",
        }


@dataclass(frozen=True)
class PerformanceProfile:
    config: ProfileConfig
    hardware: HardwareInventory
    wall_time: TimingSummary
    process_cpu_time: TimingSummary
    python_peak_bytes: tuple[int, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "measured",
            "config": asdict(self.config),
            "hardware": self.hardware.to_dict(),
            "wall_time": self.wall_time.to_dict(),
            "process_cpu_time": self.process_cpu_time.to_dict(),
            "memory": {
                "python_peak_bytes": list(self.python_peak_bytes),
                "max_python_peak_bytes": max(self.python_peak_bytes),
                "scope": "process-local Python-traced allocations only; not RSS or native/GPU memory",
            },
            "measurement_scope": (
                "in-process CPU callable baseline including profiler overhead; "
                "not GPU/server latency, correctness, or hardware qualification"
            ),
            "provenance": "subject and owner_scope are caller assertions; code identity unverified",
        }

    def receipt(self) -> ExecutionSpineRecord:
        return ExecutionSpineRecord(
            surface_id="az-ml-performance-profile", surface_kind="cpu-callable-profile",
            lane="adjacent", status="measured",
            summary="Local CPU callable measurements only; no qualification or promotion.",
            compatibility=self.to_dict(),
            governance=build_fail_closed_governance(
                epistemic_label="measured local CPU baseline",
                promotion_rule="Human review required; timings never authorize promotion.",
                residual_blockers=[
                    "No correctness, production latency, GPU, or hardware qualification.",
                    "Subject and ownership are caller assertions; code identity unverified.",
                ],
            ),
            promotion={"eligible": False, "automatic_promotion": False},
        )


def profile_callable(
    fn: Callable[[], object], *, subject: str, owner_scope: str,
    warmups: int = 1, repetitions: int = 5,
) -> PerformanceProfile:
    """Invoke a zero-argument CPU callable; exceptions propagate without a receipt.

    A closure may supply private inputs, but neither it nor its outputs is stored.
    Existing tracemalloc sessions are rejected without modification. No shell,
    network, credential probing, device probes, or privileged counters are used.
    """
    config = ProfileConfig(subject, owner_scope, warmups, repetitions)
    if not callable(fn):
        raise ValueError("fn must be callable")
    if tracemalloc.is_tracing():
        raise RuntimeError("tracemalloc is already active; exclusive tracing required")
    hardware = _hardware_inventory()
    for _ in range(config.warmups):
        fn()
    wall_samples: list[float] = []
    cpu_samples: list[float] = []
    peaks: list[int] = []
    for _ in range(config.repetitions):
        if tracemalloc.is_tracing():
            raise RuntimeError("tracemalloc is already active; exclusive tracing required")
        tracemalloc.start()
        try:
            wall_start = time.perf_counter()
            cpu_start = time.process_time()
            fn()
            cpu_elapsed = time.process_time() - cpu_start
            wall_elapsed = time.perf_counter() - wall_start
            if not tracemalloc.is_tracing():
                raise RuntimeError("callable disabled required tracemalloc measurement")
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        wall_samples.append(wall_elapsed)
        cpu_samples.append(cpu_elapsed)
        peaks.append(peak)
    return PerformanceProfile(
        config, hardware, TimingSummary(tuple(wall_samples)),
        TimingSummary(tuple(cpu_samples)), tuple(peaks),
    )
