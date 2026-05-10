# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/constants.py
================
Unitary Operating System — constants derived from the Unitary Manifold braid
triad (n_w=5, n_b=7, k_cs=74=5²+7²).

All UOS resource limits, scheduling quanta, and security thresholds are
expressed in units of these geometric invariants so that the OS obeys the
same conservation laws as the underlying 5D physics.

Constants
---------
WINDING_NUMBER       n_w = 5      (braid winding; primary spatial period)
BRAID_PARTNER        n_b = 7      (braid partner; secondary resonance)
K_CS                 k_cs = 74    (= 5² + 7² = 25 + 49; Chern–Simons level)
BRAIDED_SOUND_SPEED  c_s = 12/37  (from (5,7) resonance; speed-of-light proxy)
PHI_BACKGROUND       φ₀ = 1.0     (radion attractor; normalised Planck units)
LAMBDA_COUPLING      λ = 0.1      (KK coupling; default from evolution.py)
ALPHA_COUPLING       α = 0.05     (non-minimal coupling; default)

UOS resource constants (dimensionless, in manifold units)
----------------------------------------------------------
UOS_PROCESS_SLOTS    = K_CS       (74 simultaneous geodesic lanes)
UOS_MEMORY_PAGES     = K_CS ** 2  (74² = 5476 unitary address pages)
UOS_SECURITY_LEVELS  = WINDING_NUMBER  (5 geometric isolation tiers)
UOS_FS_SHARDS        = BRAID_PARTNER   (7 holographic shard dimensions)
UOS_DRIVER_CHANNELS  = K_CS       (74 4D hardware translation channels)
UOS_CLOCK_QUANTUM    = c_s        (≈ 0.3243 manifold time units per tick)
INVARIANT_RATIO      = WINDING_NUMBER / BRAID_PARTNER   (= 5/7 ≈ 0.7143)
INVARIANT_TOLERANCE  = 1e-6       (max allowed deviation from 3:2 / 5:7 ratio)
"""

# ---------------------------------------------------------------------------
# Braid triad (mirror of src/core constants; do NOT import from src to keep
# the UOS self-contained enough for early bootstrap)
# ---------------------------------------------------------------------------
WINDING_NUMBER: int = 5          # n_w
BRAID_PARTNER: int = 7           # n_b
K_CS: int = 74                   # = 5² + 7² = k_cs
BRAIDED_SOUND_SPEED: float = 12 / 37   # c_s  ≈ 0.3243
PHI_BACKGROUND: float = 1.0      # φ₀  (normalised radion attractor)
LAMBDA_COUPLING: float = 0.1     # λ   (KK coupling)
ALPHA_COUPLING: float = 0.05     # α   (non-minimal coupling)

# ---------------------------------------------------------------------------
# UOS resource limits
# ---------------------------------------------------------------------------
UOS_PROCESS_SLOTS: int = K_CS              # 74 geodesic lanes
UOS_MEMORY_PAGES: int = K_CS ** 2         # 5 476 unitary address pages
UOS_SECURITY_LEVELS: int = WINDING_NUMBER  # 5 isolation tiers
UOS_FS_SHARDS: int = BRAID_PARTNER         # 7 holographic shards
UOS_DRIVER_CHANNELS: int = K_CS            # 74 hardware channels
UOS_CLOCK_QUANTUM: float = BRAIDED_SOUND_SPEED   # ≈ 0.3243 time units / tick

# ---------------------------------------------------------------------------
# Geometric invariant gate
# ---------------------------------------------------------------------------
INVARIANT_RATIO: float = WINDING_NUMBER / BRAID_PARTNER   # 5/7 ≈ 0.7143
INVARIANT_TOLERANCE: float = 1e-6
