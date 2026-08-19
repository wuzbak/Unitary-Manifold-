# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
oracle/engine/constants.py
==========================
The five seed constants of the Unitary Manifold and all quantities derived from them.

Every number in this file flows from exactly five inputs:
    N_W  = 5      (primary winding number — selected by Planck CMB nₛ)
    N_2  = 7      (braid partner — selected by BICEP/Keck r constraint)
    K_CS = 74     (Chern-Simons level = N_W² + N_2²)
    C_S  = 12/37  (braided sound speed — braid kinematics)
    XI_C = 35/74  (consciousness coupling — brain-universe fixed point)

No other free parameters are admitted.

Theory: ThomasCory Walker-Pearson.
Code:   GitHub Copilot (AI).
"""

from fractions import Fraction
import math

# ── Five Seed Constants ──────────────────────────────────────────────────────

N_W: int = 5          # primary winding number
N_2: int = 7          # braid partner
K_CS: int = 74        # Chern-Simons level  =  N_W² + N_2²  =  25 + 49
C_S: Fraction = Fraction(12, 37)   # braided sound speed  ≈ 0.32432
XI_C: Fraction = Fraction(35, 74)  # consciousness coupling  ≈ 0.47297

# ── Verification of the resonance identity ───────────────────────────────────

assert N_W**2 + N_2**2 == K_CS, "Chern-Simons resonance identity violated"

# ── Derived quantities (float) ────────────────────────────────────────────────

C_S_F: float = float(C_S)       # ≈ 0.324324…
XI_C_F: float = float(XI_C)     # ≈ 0.472972…

# Spectral index  nₛ = 1 − 2/k_CS
N_S: float = 1.0 - 2.0 / K_CS                     # ≈ 0.9730 …
# Tensor-to-scalar ratio  r = 12/k_CS²
R_BRAIDED: float = 12.0 / (K_CS ** 2)              # ≈ 0.00220 … (braided suppression)
# Birefringence angles (canonical and shadow)
BETA_57_DEG: float = math.degrees(math.atan(C_S_F / N_W))   # ≈ 3.71°
BETA_56_DEG: float = math.degrees(math.atan(C_S_F / N_2))   # ≈ 2.65°

# HILS stability threshold
HIL_PHASE_SHIFT_THRESHOLD: int = 15    # n_hil ≥ 15 → stability = 1.0
SENTINEL_CAPACITY: float = C_S_F       # per-axiom entropy capacity
PHI_TRUST_CRISIS: float = C_S_F        # phi_trust < C_S → authenticity crisis

# Omega score grade boundaries
OMEGA_GRADE_BOUNDS: dict[str, tuple[float, str, str]] = {
    "Ω": (0.90, "Unified",    "All bodies resonant — ground state achieved."),
    "A": (0.75, "Strong",     "Most bodies solid; minor gaps present."),
    "B": (0.60, "Functional", "Working well; some open work remains."),
    "C": (0.40, "Fragmented", "Several bodies need attention."),
    "D": (0.24, "Unstable",   "Significant open bodies; rebuild needed."),
    "F": (0.00, "Crisis",     "Low coherence; urgent intervention required."),
}

# Epistemic status weights (mirrors holon_zero.py)
STATUS_WEIGHTS: dict[str, float] = {
    "SOLID":       1.00,
    "CONSTRAINED": 0.75,
    "ESTIMATED":   0.40,
    "OPEN":        0.00,
}

# Impact multipliers for the decision-resonance oracle
IMPACT_MULTIPLIERS: dict[tuple[str, str], float] = {
    ("OPEN",        "improve"): +2.0,
    ("ESTIMATED",   "improve"): +1.5,
    ("CONSTRAINED", "improve"): +1.0,
    ("SOLID",       "improve"): +0.5,
    ("SOLID",       "harm"):    -2.0,
    ("CONSTRAINED", "harm"):    -1.5,
    ("ESTIMATED",   "harm"):    -0.5,
    ("OPEN",        "harm"):    -0.2,
}

# Governance audit thresholds (EIGE-aligned)
GOV_INTEGRITY_THRESHOLD: float = 0.70   # below → governance concern
GOV_TRANSPARENCY_IDEAL: float  = 0.85   # target for fully accountable system
GOV_FREEDOM_FLOOR: float       = C_S_F  # participation must exceed braided CS

# Human-readable category labels for 5-body Pentad mapping
DEFAULT_PENTAD_BODIES: list[str] = [
    "Ψ₁ — Foundation & Infrastructure",
    "Ψ₂ — People & Stakeholders",
    "Ψ₃ — Process & Intelligence",
    "Ψ₄ — Trust & Accountability",
    "Ψ₅ — Purpose & Horizon",
]


def stability_floor(n_aligned: int) -> float:
    """
    HILS stability formula from omega_synthesis.py:
        stability_floor(n) = min(1.0, C_S + n × C_S / N_2)

    Returns the minimum achievable stability for a system with n_aligned
    SOLID-or-CONSTRAINED bodies.
    """
    return min(1.0, C_S_F + n_aligned * C_S_F / N_2)


def phi_trust_status(phi_trust: float) -> str:
    """Classify phi_trust (authenticity / integrity score)."""
    if phi_trust >= 0.85:
        return "AUTHENTIC"
    if phi_trust >= C_S_F:
        return "COHERENT"
    if phi_trust >= 0.15:
        return "STRAINED"
    return "CRISIS"


def omega_grade(omega_score: float) -> tuple[str, str, str]:
    """Return (letter_grade, label, description) for an omega_score."""
    for letter, (threshold, label, desc) in OMEGA_GRADE_BOUNDS.items():
        if omega_score >= threshold:
            return letter, label, desc
    return "F", "Crisis", OMEGA_GRADE_BOUNDS["F"][2]
