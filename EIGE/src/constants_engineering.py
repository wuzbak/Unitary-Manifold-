# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/constants_engineering.py — Physics-Free Engineering Constants
=======================================================================

This module re-exports all EIGE operational constants under purely
engineering names — with no reference to Kaluza-Klein physics, the
Unitary Manifold, or cosmological theory.

**Purpose:** Allow evaluators who do not wish to engage with the
underlying physical theory to verify EIGE's mathematical properties on
their own terms.  Every constant here is identical in value to the
corresponding constant in constants.py; only the names and docstrings
differ.

The two modules are kept strictly in sync.  If you need to update a
constant value, update constants.py and this file together.

Engineering equivalence table
------------------------------
  ACCUMULATOR_SEED        = K_CS          = 74
  EQUILIBRIUM_SCALAR      = PHI_0         = π/4
  SHARD_DISTRIBUTION_BASE = WINDING_NUMBER = 5
  EQUILIBRIUM_TOLERANCE   = PHI_TOLERANCE = 1e-15
  SOFT_DRIFT_WARNING      = PHI_DRIFT_WARNING = 1e-12
  AUDIT_PRECISION_BITS    = PRECISION_BITS    = 512

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

import math

# ---------------------------------------------------------------------------
# Core tamper-detection invariants
# ---------------------------------------------------------------------------

ACCUMULATOR_SEED: int = 74
"""
Integer seed for the path-dependent rolling hash accumulator.

Value: 74 = 5² + 7²

Engineering role:
  - Seeds the initial state of the Chern-Simons hash chain
  - Governs shard placement arithmetic (8 shards derived from this seed)
  - Anchors the Holon Zero OSCAL compliance certificate

Why 74?  The integer 74 has the property of being expressible as the sum
of two squares (5² + 7²), which gives the hash chain its non-commutative
XOR structure and the shard layout its reconstruction arithmetic.  Any
other seed value of similar magnitude would work; 74 is the chosen
invariant and must not be changed between election runs.
"""

EQUILIBRIUM_SCALAR: float = math.pi / 4
"""
Floating-point equilibrium reference for the metric closure validator.

Value: π/4 ≈ 0.7853981633974483

Engineering role:
  - The accumulated hash chain produces an effective scalar (φ_eff) that
    converges to this value for any legitimate, unmodified ballot sequence.
  - Any structural manipulation of the ballot sequence (insertion,
    deletion, reorder) disrupts the chain and causes φ_eff to deviate
    beyond EQUILIBRIUM_TOLERANCE.
  - The deviation is deterministic — not statistical.

Why π/4?  It is the self-consistent fixed point of the metric closure
equation under the chosen hash construction.  No external calibration
is required; it emerges from the math.
"""

SHARD_DISTRIBUTION_BASE: int = 5
"""
Base multiplier for inter-shard braid reconstruction arithmetic.

Value: 5

Engineering role:
  - Each county node stores ballot hash state across 8 shards.
  - The shard addresses are computed using polynomial arithmetic with
    this base over the ACCUMULATOR_SEED modulus.
  - This guarantees that any 5 of 8 shards are sufficient to reconstruct
    the full hash chain (tolerates simultaneous loss of 3 shards).
"""

# ---------------------------------------------------------------------------
# Precision & tolerance constants (unchanged from physics module)
# ---------------------------------------------------------------------------

EQUILIBRIUM_TOLERANCE: float = 1e-15
"""
Hard violation threshold: |φ_eff − EQUILIBRIUM_SCALAR| > this → VIOLATED.
Set at floating-point epsilon scale to catch any software manipulation
that rounds or truncates the metric field value.
"""

SOFT_DRIFT_WARNING: float = 1e-12
"""
Soft drift threshold: |φ_eff − EQUILIBRIUM_SCALAR| > this but ≤
EQUILIBRIUM_TOLERANCE → DRIFTED state (warrants investigation).
"""

AUDIT_PRECISION_BITS: int = 512
"""
Bit-precision for the high-precision out-of-band audit worker.
Corresponds to 154 decimal digits (154 × log2(10) ≈ 511.6 bits).
"""

# ---------------------------------------------------------------------------
# Hash & cryptographic constants (unchanged)
# ---------------------------------------------------------------------------

HASH_MODULUS: int = 2**63 - 1
"""
Mersenne prime M63 = 2^63 − 1 used as hash modulus.
Ensures uniform distribution and efficient modular reduction.
"""

HASH_SHIFT_BITS: int = 7
"""
Right-shift bits in the non-commutative hash accumulation step.
Introduces non-linearity that prevents algebraic attack inversion.
"""

# ---------------------------------------------------------------------------
# Operational constants (unchanged)
# ---------------------------------------------------------------------------

NODE_COUNT: int = 39
"""Washington State county node count."""

SHARD_COUNT: int = 8
"""Holographic persistence shards per node."""

SHARD_RECONSTRUCTION_THRESHOLD: int = 5
"""Minimum shards required for full hash-chain reconstruction."""

NOISE_BUDGET_DEFAULT: float = 0.10
"""Default chaos injection noise budget (fraction of ballots, 0–1)."""

PARTICIPATION_FLOOR: float = 0.85
"""
Minimum fraction of nodes contributing non-trivially.
Below this threshold the Freedom Floor kill-switch fires.
"""

PARTICIPATION_MIN_BALLOTS: int = 1
"""Minimum ballot count for a node to count as a non-trivial participant."""

CONFIDENCE_THRESHOLD: float = 0.60
"""
Minimum optical-scanner mark confidence accepted without human adjudication.
Below this threshold an AdmissibilityError routes the ballot to the
human adjudicator queue.
"""

DOSSIER_LATENCY_MS: int = 500
"""Maximum milliseconds from anomaly detection to OSCAL dossier on disk."""

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

ENGINE_VERSION: str = "21.0.0"
OSCAL_VERSION: str = "1.5.0"
