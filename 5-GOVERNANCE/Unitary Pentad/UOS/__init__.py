# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS — Unitary Operating System
================================
A 5-dimensional Kaluza–Klein operating system kernel built on the Unitary
Manifold.  This package provides the **mathematical and simulation layer** of
the UOS architecture: the same geometric invariants that govern field physics
in the UM are reinterpreted as scheduling, memory, security, storage, language
execution, networking, cryptography, and container isolation.

Cross-branch Integration
------------------------
The UOS is aware of and builds upon work across the active development branches:

* **JAX backend** (``src/core/jax_evolution.py``, ``jax_metric.py``) —
  The UOSHypervisor delegates 5D field evolution to the JAX-accelerated
  RK4 integrator when JAX is available, falling back to NumPy otherwise.

* **KK VQE** (``src/core/kk_vqe.py``, ``src/quantum/kk_vqe.py``) —
  The LanguageRegistry includes Qiskit, Cirq, Q#, and Quipper as Tier-0
  quantum lanes.  The scheduler gives quantum artifacts GEODESIC concurrency
  priority.  KK VQE circuits can be submitted directly via the runtime.

* **Fiber Bundle Topology** (``src/core/fiber_bundle.py``) —
  The GeodesicScheduler uses fiber bundle sector labels to assign process
  groups to distinct manifold sectors, preventing sector-crossing overhead.

* **Holon Zero** (``holon_zero/holon_zero_engine.py``) —
  The UOS idle/sleep state maps to Holon Zero: the ground state before any
  process is scheduled.  When the scheduler is empty, the manifold relaxes
  to φ = φ₀ (the HolonZero fixed point).

* **Omega Synthesis** (``omega/omega_synthesis.py``) —
  The UOSHypervisor exposes a ``system_report()`` method that calls into
  OmegaSynthesis to produce a full cross-domain health summary, bridging
  OS metrics with cosmological, biological, and governance indicators.

* **Convergence validation** (stress-test-attractor branch) —
  The UOS profiler tracks geodesic efficiency using the same convergence
  criterion as the attractor validation tests: the manifold field must
  remain within INVARIANT_TOLERANCE of the FTUM fixed point during normal
  operation.

Sub-modules (Phase 1 — Core Kernel)
------------------------------------
constants        — UOS-specific constants derived from the UM braid triad (5, 7, 74)
hypervisor       — 5D manifold resource manager (the UOS kernel)
scheduler        — geodesic process scheduler (replaces preemptive multitasking)
memory           — unitary addressing memory manager (zero-copy, fold-mapped)
security         — geometric isolation security (invariant-enforcement gate)
filesystem       — holographic content-addressed filesystem (manifold projection)
driver_wrapper   — universal 4D hardware wrapper (5D intent → 4D signal)

Sub-modules (Phase 2 — Full System Stack)
------------------------------------------
language_runtime — 74-language native runtime: every language mapped to a manifold lane
ipc              — inter-process communication (channels, queues, shared sections, pipes)
network          — manifold network stack (geodesic routing, sockets, frames)
crypto           — geometric cryptography (φ-hash, manifold keys, cipher, signatures)
shell            — AI-powered intent shell (natural-language OS interface)
bootloader       — 7-phase 5D manifold bootloader
container        — manifold container isolation (winding-sector separation)
profiler         — manifold-aware performance profiler (geodesic efficiency metrics)

Public top-level imports
------------------------
>>> from UOS import UOSHypervisor, GeodesicScheduler, UnitaryMemory
>>> from UOS import GeometricSecurityEngine, HolographicFilesystem, DriverWrapper
>>> from UOS import UniversalRuntime, IPCManager, NetworkStack
>>> from UOS import CryptoEngine, UOSShell, ManifoldBootloader
>>> from UOS import ContainerOrchestrator, ManifoldProfiler

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
"""

from UOS.hypervisor import UOSHypervisor
from UOS.scheduler import GeodesicScheduler, ProcessGeodesic
from UOS.memory import UnitaryMemory
from UOS.security import GeometricSecurityEngine, SecurityViolation
from UOS.filesystem import HolographicFilesystem
from UOS.driver_wrapper import DriverWrapper
from UOS.language_runtime import UniversalRuntime, LanguageRegistry
from UOS.ipc import IPCManager, ManifoldChannel, MessageQueue, SharedManifoldSection, Pipe
from UOS.network import NetworkStack, ManifoldSocket, ManifoldRouter, ManifoldAddress
from UOS.crypto import CryptoEngine, GeometricHash, ManifoldKey, ManifoldCipher
from UOS.shell import UOSShell, IntentParser, IntentAction
from UOS.bootloader import ManifoldBootloader
from UOS.container import ContainerOrchestrator, ManifoldContainer
from UOS.profiler import ManifoldProfiler, ProfileTrace

__all__ = [
    # Phase 1 — Core Kernel
    "UOSHypervisor",
    "GeodesicScheduler",
    "ProcessGeodesic",
    "UnitaryMemory",
    "GeometricSecurityEngine",
    "SecurityViolation",
    "HolographicFilesystem",
    "DriverWrapper",
    # Phase 2 — Full System Stack
    "UniversalRuntime",
    "LanguageRegistry",
    "IPCManager",
    "ManifoldChannel",
    "MessageQueue",
    "SharedManifoldSection",
    "Pipe",
    "NetworkStack",
    "ManifoldSocket",
    "ManifoldRouter",
    "ManifoldAddress",
    "CryptoEngine",
    "GeometricHash",
    "ManifoldKey",
    "ManifoldCipher",
    "UOSShell",
    "IntentParser",
    "IntentAction",
    "ManifoldBootloader",
    "ContainerOrchestrator",
    "ManifoldContainer",
    "ManifoldProfiler",
    "ProfileTrace",
]
