# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/profiler.py
===============
Unitary Operating System — Manifold-Aware Performance Profiler

Classical profilers (cProfile, perf, VTune) sample CPU time and count
function calls.  The UOS ManifoldProfiler tracks performance on the manifold:

  * **φ-time**: time measured in manifold ticks (multiples of BRAIDED_SOUND_SPEED)
    rather than wall-clock microseconds.
  * **Geodesic cost**: the φ-distance a process travels per tick is its
    "computational work".  A long geodesic = heavy computation.
  * **Curvature overhead**: context switches are seen as curvature events
    (sudden changes in geodesic direction) — the profiler counts these and
    charges them as scheduling overhead.
  * **Entropy accounting**: the φ-entropy of a process's output measures
    how much new information it produces (inspired by Pillar 16 recycling).

Profiler Architecture
---------------------
ProfileSample(pid, phi, tick, curvature, entropy)
    A single sample point in the manifold timeline.

ProfileTrace
    A time series of ProfileSamples for one process.

ManifoldProfiler
    The central profiler.  Manages traces for multiple processes.
    Produces reports including hotspot detection (most curvature),
    entropy budget, and geodesic efficiency.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from UOS.constants import (
    K_CS, WINDING_NUMBER, BRAID_PARTNER, PHI_BACKGROUND, BRAIDED_SOUND_SPEED,
    LAMBDA_COUPLING,
)

# Profiler constants
MAX_SAMPLES_PER_TRACE: int = K_CS * WINDING_NUMBER   # = 370 samples
MAX_TRACES: int = K_CS                               # = 74 traces


# ===========================================================================
# ProfileSample
# ===========================================================================

@dataclass(frozen=True)
class ProfileSample:
    """A single profiling sample in manifold time.

    Parameters
    ----------
    pid : int
    phi : float
        Manifold φ-coordinate at the time of sampling.
    tick : int
        Manifold tick (integer multiple of BRAIDED_SOUND_SPEED).
    curvature : float
        Local curvature estimate (|Δφ/Δtick|²).  Large curvature = context switch.
    entropy : float
        Information entropy of the process output at this tick.
    cpu_fraction : float
        Fraction of total CPU used by this process at this tick.
    memory_pages : int
        Memory pages consumed.
    label : str
        Optional label for the sample (function name, system call, etc.).
    """
    pid: int
    phi: float
    tick: int
    curvature: float = 0.0
    entropy: float = 0.0
    cpu_fraction: float = 0.0
    memory_pages: int = 0
    label: str = ""


# ===========================================================================
# ProfileTrace
# ===========================================================================

class ProfileTrace:
    """A time series of ProfileSamples for one process.

    Parameters
    ----------
    pid : int
    name : str
        Process name.
    max_samples : int

    Examples
    --------
    >>> trace = ProfileTrace(pid=42, name="worker")
    >>> trace.add_sample(phi=1.5, tick=0, cpu_fraction=0.3)
    >>> trace.add_sample(phi=1.7, tick=1, cpu_fraction=0.4)
    >>> trace.total_geodesic_length()
    0.2
    """

    def __init__(
        self,
        pid: int,
        name: str = "",
        max_samples: int = MAX_SAMPLES_PER_TRACE,
    ) -> None:
        self.pid = pid
        self.name = name
        self.max_samples = max_samples
        self._samples: List[ProfileSample] = []

    def add_sample(
        self,
        phi: float,
        tick: int,
        curvature: float = 0.0,
        entropy: float = 0.0,
        cpu_fraction: float = 0.0,
        memory_pages: int = 0,
        label: str = "",
    ) -> ProfileSample:
        """Add a sample to the trace.

        Curvature is auto-computed from the last two φ values if not given.

        Returns
        -------
        ProfileSample
        """
        if len(self._samples) >= self.max_samples:
            self._samples.pop(0)   # ring buffer: discard oldest

        if curvature == 0.0 and len(self._samples) >= 1:
            last = self._samples[-1]
            dphi = abs(phi - last.phi)
            dtick = max(tick - last.tick, 1)
            curvature = (dphi / dtick) ** 2

        sample = ProfileSample(
            pid=self.pid,
            phi=phi,
            tick=tick,
            curvature=curvature,
            entropy=entropy,
            cpu_fraction=cpu_fraction,
            memory_pages=memory_pages,
            label=label,
        )
        self._samples.append(sample)
        return sample

    def samples(self) -> List[ProfileSample]:
        """Return all samples (oldest first)."""
        return list(self._samples)

    def total_geodesic_length(self) -> float:
        """Total φ-distance travelled by this process."""
        if len(self._samples) < 2:
            return 0.0
        phis = np.array([s.phi for s in self._samples])
        return float(np.sum(np.abs(np.diff(phis))))

    def mean_curvature(self) -> float:
        """Mean curvature (context-switch overhead indicator)."""
        if not self._samples:
            return 0.0
        return float(np.mean([s.curvature for s in self._samples]))

    def peak_curvature(self) -> float:
        """Peak curvature (worst context switch)."""
        if not self._samples:
            return 0.0
        return float(max(s.curvature for s in self._samples))

    def total_entropy(self) -> float:
        """Total entropy produced by the process."""
        return float(sum(s.entropy for s in self._samples))

    def mean_cpu(self) -> float:
        """Mean CPU fraction used."""
        if not self._samples:
            return 0.0
        return float(np.mean([s.cpu_fraction for s in self._samples]))

    def peak_memory(self) -> int:
        """Peak memory consumption in pages."""
        if not self._samples:
            return 0
        return int(max(s.memory_pages for s in self._samples))

    def hotspots(self, n: int = 3) -> List[ProfileSample]:
        """Return the n samples with the highest curvature (= overhead points)."""
        return sorted(self._samples, key=lambda s: -s.curvature)[:n]

    def geodesic_efficiency(self) -> float:
        """Return the geodesic efficiency in [0, 1].

        Efficiency = mean_cpu / (1 + mean_curvature)
        A perfectly scheduled process has high CPU and low curvature.
        """
        return float(
            np.clip(self.mean_cpu() / (1.0 + self.mean_curvature()), 0.0, 1.0)
        )

    def report(self) -> Dict:
        """Return a full profile report dict."""
        return {
            "pid": self.pid,
            "name": self.name,
            "samples": len(self._samples),
            "geodesic_length": self.total_geodesic_length(),
            "mean_curvature": self.mean_curvature(),
            "peak_curvature": self.peak_curvature(),
            "geodesic_efficiency": self.geodesic_efficiency(),
            "total_entropy": self.total_entropy(),
            "mean_cpu": self.mean_cpu(),
            "peak_memory_pages": self.peak_memory(),
        }


# ===========================================================================
# ManifoldProfiler
# ===========================================================================

class ManifoldProfiler:
    """Central UOS manifold profiler.

    Manages ProfileTraces for multiple processes.  Provides:
      * per-process reports
      * cross-process comparisons
      * hotspot detection
      * entropy budget tracking
      * geodesic efficiency ranking

    Parameters
    ----------
    max_traces : int

    Examples
    --------
    >>> prof = ManifoldProfiler()
    >>> prof.start_trace(pid=1, name="kernel")
    >>> for tick in range(10):
    ...     phi = PHI_BACKGROUND + 0.01 * tick
    ...     prof.sample(pid=1, phi=phi, tick=tick, cpu_fraction=0.8)
    >>> report = prof.report(pid=1)
    >>> report["mean_cpu"]
    0.8
    """

    def __init__(self, max_traces: int = MAX_TRACES) -> None:
        self.max_traces = max_traces
        self._traces: Dict[int, ProfileTrace] = {}
        self._global_tick: int = 0
        self._session_entropy: float = 0.0

    # ------------------------------------------------------------------
    # Trace management
    # ------------------------------------------------------------------

    def start_trace(self, pid: int, name: str = "") -> ProfileTrace:
        """Create and register a new ProfileTrace for a process.

        Parameters
        ----------
        pid : int
        name : str

        Returns
        -------
        ProfileTrace

        Raises
        ------
        OverflowError
            If max_traces is exceeded.
        """
        if pid in self._traces:
            return self._traces[pid]
        if len(self._traces) >= self.max_traces:
            raise OverflowError(
                f"ManifoldProfiler: max_traces ({self.max_traces}) reached."
            )
        trace = ProfileTrace(pid=pid, name=name)
        self._traces[pid] = trace
        return trace

    def stop_trace(self, pid: int) -> None:
        """Remove and discard the trace for a process."""
        self._traces.pop(pid, None)

    def get_trace(self, pid: int) -> Optional[ProfileTrace]:
        """Return the trace for a process, or None."""
        return self._traces.get(pid)

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------

    def sample(
        self,
        pid: int,
        phi: float,
        tick: Optional[int] = None,
        curvature: float = 0.0,
        entropy: float = 0.0,
        cpu_fraction: float = 0.0,
        memory_pages: int = 0,
        label: str = "",
    ) -> Optional[ProfileSample]:
        """Record a sample for a process.

        If no trace exists for ``pid``, one is created automatically.

        Parameters
        ----------
        pid : int
        phi : float
        tick : int, optional
            If None, uses the global tick counter.
        curvature, entropy, cpu_fraction, memory_pages, label : optional

        Returns
        -------
        ProfileSample
        """
        if pid not in self._traces:
            self.start_trace(pid)
        if tick is None:
            tick = self._global_tick
        self._global_tick = max(self._global_tick, tick + 1)
        self._session_entropy += entropy
        return self._traces[pid].add_sample(
            phi=phi, tick=tick, curvature=curvature,
            entropy=entropy, cpu_fraction=cpu_fraction,
            memory_pages=memory_pages, label=label,
        )

    def tick(self) -> int:
        """Advance global tick and return it."""
        self._global_tick += 1
        return self._global_tick

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def report(self, pid: int) -> Dict:
        """Return a full report for one process."""
        trace = self._traces.get(pid)
        if trace is None:
            raise KeyError(f"No trace found for PID {pid}.")
        return trace.report()

    def global_report(self) -> Dict:
        """Return a summary report across all traced processes."""
        if not self._traces:
            return {"traces": 0}
        reports = [t.report() for t in self._traces.values()]
        efficiencies = [r["geodesic_efficiency"] for r in reports]
        return {
            "traces": len(self._traces),
            "global_tick": self._global_tick,
            "session_entropy": self._session_entropy,
            "mean_geodesic_efficiency": float(np.mean(efficiencies)),
            "min_efficiency_pid": min(
                self._traces, key=lambda p: self._traces[p].geodesic_efficiency()
            ),
            "max_efficiency_pid": max(
                self._traces, key=lambda p: self._traces[p].geodesic_efficiency()
            ),
        }

    def efficiency_ranking(self) -> List[Tuple[int, float]]:
        """Return (pid, efficiency) sorted by decreasing efficiency."""
        return sorted(
            [(pid, t.geodesic_efficiency()) for pid, t in self._traces.items()],
            key=lambda x: -x[1],
        )

    def hotspot_pids(self, n: int = 3) -> List[int]:
        """Return PIDs with the highest mean curvature (= most overhead)."""
        return [
            pid for pid, _ in sorted(
                self._traces.items(),
                key=lambda kv: -kv[1].mean_curvature(),
            )[:n]
        ]

    def profile(
        self,
        fn: Callable,
        pid: int,
        n_samples: int = 10,
        name: str = "",
    ) -> Tuple[Any, Dict]:
        """Profile a callable by sampling its φ-trace during execution.

        Parameters
        ----------
        fn : callable
            A zero-argument callable to profile.
        pid : int
        n_samples : int
        name : str

        Returns
        -------
        (result, report) tuple
        """
        trace = self.start_trace(pid=pid, name=name or fn.__name__)
        phi = PHI_BACKGROUND
        for i in range(n_samples):
            # Synthetic φ walk: each sample advances φ by BRAIDED_SOUND_SPEED
            phi = phi - 0.05 * (phi - PHI_BACKGROUND) * BRAIDED_SOUND_SPEED
            self.sample(pid=pid, phi=phi, tick=i, cpu_fraction=0.5, label=f"sample-{i}")
        result = fn()
        # Final sample for return
        self.sample(pid=pid, phi=phi, tick=n_samples, cpu_fraction=0.0, label="return")
        return result, trace.report()

    def stats(self) -> Dict:
        return {
            "active_traces": len(self._traces),
            "global_tick": self._global_tick,
            "session_entropy": self._session_entropy,
            "max_traces": self.max_traces,
        }
