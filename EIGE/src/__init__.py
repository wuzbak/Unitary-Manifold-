# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE v21.0 — Sovereign Elections Integrity Governance Engine
============================================================
Pillar 19-EIGE  |  🔵 ADJACENT TRACK

Theory & scientific direction: ThomasCory Walker-Pearson
Code architecture & implementation: GitHub Copilot (AI)

This package implements the AxiomZero EIGE v21.0 engine: a 3-tier sovereign
election integrity system mapping discrete electoral transactions into the
5-Dimensional Kaluza-Klein geometric framework for tamper-evident, mathematically
verified chain-of-custody across county, state, and federal tiers.

Epistemic note: This is an ADJACENT TRACK governance application. The geometric
constants (k_CS=74, phi_0=pi/4) are used as tamper-detection invariants. This
module makes no claims about the physics of elections; it applies the mathematical
structure of the Unitary Manifold to election integrity verification.
"""

PILLAR = "19-EIGE"
EPISTEMIC_LABEL = "🔵 ADJACENT TRACK"
VERSION = "21.0.0"
JURISDICTION_DEFAULT = "WA-KING-COUNTY"

# Phase 1: Chaos Injection
from .chaos_injection import (
    ChaosInjector,
    FreedomFloorViolation,
    InjectionEvent,
    NoiseMode,
)

# Phase 2: Holographic Screening Layer
from .holographic_screen import (
    HolographicScreen,
    AdmissibilityError,
    NormalisationRecord,
    NormalisationStatus,
    WriteInRegistry,
)

# Phase 3: Public Trust Index
from .public_trust_index import (
    PublicTrustIndexBuilder,
    PublicTrustReport,
)

# Phase 4: Freedom Floor Kill-Switch (in sentinel)
from .sentinel_load_balance import FreedomFloorBreach

__all__ = [
    # Chaos injection
    "ChaosInjector",
    "FreedomFloorViolation",
    "InjectionEvent",
    "NoiseMode",
    # Holographic screen
    "HolographicScreen",
    "AdmissibilityError",
    "NormalisationRecord",
    "NormalisationStatus",
    "WriteInRegistry",
    # Public trust index
    "PublicTrustIndexBuilder",
    "PublicTrustReport",
    # Freedom floor (sentinel)
    "FreedomFloorBreach",
]
