# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS — Unitary Operating System
================================
A 5-dimensional Kaluza–Klein operating system kernel built on the Unitary
Manifold.  This package provides the **mathematical and simulation layer** of
the UOS architecture: the same geometric invariants that govern field physics
in the UM are reinterpreted as scheduling, memory, security, and storage
primitives.

Sub-modules
-----------
constants      — UOS-specific constants derived from the UM braid triad (5, 7, 74)
hypervisor     — 5D manifold resource manager (the UOS kernel)
scheduler      — geodesic process scheduler (replaces preemptive multitasking)
memory         — unitary addressing memory manager (zero-copy, fold-mapped)
security       — geometric isolation security (3:2-invariant enforcement)
filesystem     — holographic content-addressed filesystem (manifold projection)
driver_wrapper — universal 4D hardware wrapper (5D intent → 4D signal)

Public top-level imports
------------------------
>>> from UOS import UOSHypervisor, GeodesicScheduler, UnitaryMemory
>>> from UOS import GeometricSecurityEngine, HolographicFilesystem, DriverWrapper

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
"""

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

from UOS.hypervisor import UOSHypervisor
from UOS.scheduler import GeodesicScheduler, ProcessGeodesic
from UOS.memory import UnitaryMemory
from UOS.security import GeometricSecurityEngine, SecurityViolation
from UOS.filesystem import HolographicFilesystem
from UOS.driver_wrapper import DriverWrapper

__all__ = [
    "UOSHypervisor",
    "GeodesicScheduler",
    "ProcessGeodesic",
    "UnitaryMemory",
    "GeometricSecurityEngine",
    "SecurityViolation",
    "HolographicFilesystem",
    "DriverWrapper",
]
