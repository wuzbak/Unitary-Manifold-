# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/constants.py — System-Wide Physical and Operational Constants
======================================================================
All constants for the EIGE v21.0 engine live here.

Physical origin of the key constants
--------------------------------------
K_CS = 74 = 5² + 7² — the Chern-Simons topological winding invariant
    derived from the (5,7) braid resonance in the Unitary Manifold.
    In EIGE, this integer seeds all shard placement arithmetic and the
    path-dependent rolling hash, ensuring that any external tampering
    with ballot sequences produces an immediate, machine-verifiable
    deviation from the expected geometric state.

PHI_0 = π/4 — the radion scalar equilibrium value (φ₀) at which the
    5D metric is self-consistent.  EIGE uses this as the "metric health"
    reference: if the accumulated field state deviates from π/4 by more
    than PHI_TOLERANCE, the closure validator flags a VIOLATED state.

WINDING_NUMBER = 5 — n_w; the fundamental compactification winding number.
    Used as the base multiplier in braid reconstruction arithmetic.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

import math

# ---------------------------------------------------------------------------
# Core 5D geometric invariants  (hardgate constants — do not modify)
# ---------------------------------------------------------------------------

K_CS: int = 74
"""Chern-Simons topological invariant: 5² + 7² = 74."""

PHI_0: float = math.pi / 4
"""Radion scalar equilibrium value φ₀ = π/4 ≈ 0.7853981633974483."""

WINDING_NUMBER: int = 5
"""KK compactification winding number n_w = 5."""

XI_C: float = 35 / 74
"""Consciousness coupling constant Ξ_c = 35/74 (used by Pentad layer)."""

# ---------------------------------------------------------------------------
# System operational constants
# ---------------------------------------------------------------------------

COUNTY_COUNT: int = 39
"""Number of Washington State counties."""

SHARD_COUNT: int = 8
"""
Number of holographic persistence shards per county node.
Derived from k_CS = 74 (5² + 7²): the 8-shard architecture encodes
the (5,7) braid topology in its data distribution geometry, guaranteeing
that ≥5 shards suffice to reconstruct any 3 lost shards.
"""

SHARD_RECONSTRUCTION_THRESHOLD: int = 5
"""Minimum shards required for full topological reconstruction (8 − 3 = 5)."""

# ---------------------------------------------------------------------------
# Precision & tolerance constants
# ---------------------------------------------------------------------------

PHI_TOLERANCE: float = 1e-15
"""
Maximum allowed deviation |φ_eff − φ₀| before closure is VIOLATED.
Set at floating-point epsilon scale to catch any software manipulation
that rounds or truncates the metric field value.
"""

PHI_DRIFT_WARNING: float = 1e-12
"""
Softer tolerance: deviation above this but below PHI_TOLERANCE → DRIFTED.
Signals hardware or numerical drift that warrants investigation but does
not immediately constitute a tamper event.
"""

PRECISION_BITS: int = 512
"""Target precision for the high-precision audit worker."""

MPMATH_DPS: int = 154
"""
mpmath decimal places ≈ 512 bits of precision.
154 decimal digits × log2(10) ≈ 511.6 bits.
"""

# ---------------------------------------------------------------------------
# Hash & cryptographic constants
# ---------------------------------------------------------------------------

HASH_MODULUS: int = 2**63 - 1
"""
Mersenne prime M63 used as hash modulus in the Chern-Simons rolling hash.
Chosen for efficient modular reduction and distribution uniformity.
"""

HASH_SHIFT_BITS: int = 7
"""Right-shift bits in the non-commutative hash accumulation step."""

# ---------------------------------------------------------------------------
# Network & deployment constants
# ---------------------------------------------------------------------------

COUNTY_API_PORT: int = 8080
"""Default port for county ingestion API endpoints."""

STATE_MESH_PORT: int = 9090
"""Default port for state aggregation mesh sync endpoint."""

DOSSIER_EMIT_DEADLINE_MS: int = 500
"""
Maximum latency (ms) for OSCAL dossier emission after anomaly detection.
Derived from NIST SP-800-53 AU-12 audit generation requirements.
"""

BACKUP_CRON_HOURS: int = 1
"""Cold storage snapshot interval (hours)."""

# ---------------------------------------------------------------------------
# Chaos Injection & Freedom Floor constants
# ---------------------------------------------------------------------------

CHAOS_NOISE_BUDGET_DEFAULT: float = 0.10
"""
Default noise budget ε for the ChaosInjector: fraction of ballots that may
be perturbed during a chaos injection run.  Values in [0, 1].
"""

FREEDOM_FLOOR: float = 0.85
"""
Minimum fraction of county nodes that must contribute non-trivially
(ballot_count ≥ FREEDOM_FLOOR_MIN_BALLOTS) before the Freedom Floor
Guardian fires a FreedomFloorBreach event.

Rationale: if fewer than 85% of counties are participating meaningfully,
the system may be "stabilising" φ_eff by silently suppressing low-turnout
counties — which is mathematically convenient but democratically destructive.
"""

FREEDOM_FLOOR_MIN_BALLOTS: int = 1
"""
Minimum ballot count a county node must have to be considered a
"non-trivial participant" for freedom-floor monitoring purposes.
"""

HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE: float = 0.60
"""
Minimum mark_confidence value (0–1) that the HolographicScreen will accept
without routing to the human adjudicator queue.  Below this threshold an
AdmissibilityError is raised.
"""

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

ENGINE_VERSION: str = "21.0.0"
OSCAL_VERSION: str = "1.5.0"
NIST_SP_VERSION: str = "SP-800-53-R5"
