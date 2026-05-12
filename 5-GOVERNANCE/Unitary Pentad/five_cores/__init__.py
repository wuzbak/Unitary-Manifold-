# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad / five_cores
============================
The Five Functional Cores of the Unitary Pentad mission architecture.

This package implements the five operational cores that govern a sustained
mission system under AxiomZero HILS oversight:

    1. Strategic Core       — long-horizon goals, doctrine, allocation, escalation
    2. Operational Core     — task routing, workflow execution, cross-domain coordination
    3. Real-Time Safety     — continuous guardrails, trust thresholds, hard-stop/hold
    4. Real-Time Sciences   — live data ingestion, model updates, answer readiness (JAX)
    5. Biological Logics    — crew health/medicine, triage, care pathways

Each core exposes a common ``CoreState`` interface and integrates with the
Unitary Pentad trust field (φ_trust) so that all five cores share the same
(5,7)-braid stability bounds.

Public re-exports
-----------------
StrategicCore, OperationalCore, RealTimeSafetyCore,
RealTimeSciencesCore, BiologicalLogicsCore,
FiveCoresSystem, CoreLabel, SystemHealthReport
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

from five_cores.strategic_core import StrategicCore, StrategicState
from five_cores.operational_core import OperationalCore, OperationalState
from five_cores.realtime_safety_core import RealTimeSafetyCore, SafetyState
from five_cores.realtime_sciences_core import RealTimeSciencesCore, SciencesState
from five_cores.biological_logics_core import BiologicalLogicsCore, BiologicalState
from five_cores.five_cores_system import (
    FiveCoresSystem,
    CoreLabel,
    SystemHealthReport,
    CORE_LABELS,
)

__all__ = [
    "StrategicCore",
    "StrategicState",
    "OperationalCore",
    "OperationalState",
    "RealTimeSafetyCore",
    "SafetyState",
    "RealTimeSciencesCore",
    "SciencesState",
    "BiologicalLogicsCore",
    "BiologicalState",
    "FiveCoresSystem",
    "CoreLabel",
    "SystemHealthReport",
    "CORE_LABELS",
]
