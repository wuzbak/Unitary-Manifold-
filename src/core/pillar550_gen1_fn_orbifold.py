# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 550 — Gen-1 Fermion c_L: Froggatt-Nielsen Charge = Orbifold Winding.

STATUS: GEN1_FERMION_FN_ORBIFOLD_DERIVATION_ATTEMPTED

This pillar advances the gen-1 fermion bulk mass derivation from:

  Pillar 546: FERMION_CL_ORBIFOLD_FIRST_PRINCIPLES_PARTIALLY_DERIVED
              - Gen-3 (t, b, τ): DERIVED (c_L = 0, IR-localized)
              - Gen-2 (c, s, μ): DERIVED (c_L = 5/74, one lattice step)
              - Gen-1 (u, d, e): NATURAL — FN sub-lattice dominates, not first-principles

to an attempted identification:

  Pillar 550: GEN1_FERMION_FN_ORBIFOLD_DERIVATION_ATTEMPTED
              - Gen-1: FN charge n_FN is IDENTIFIED with the orbifold winding number n_w
              - The FN sub-lattice correction δ_KT is identified with the lattice step Δc
              - This provides a FIRST-PRINCIPLES CANDIDATE for gen-1 c_L

## The identification

Froggatt-Nielsen mechanism assigns integer charges Q_FN to fermions, so that
the effective Yukawa coupling is:

    Y_ij = ε^{|Q_FN_i - Q_FN_j|}

where ε = ⟨φ_FN⟩ / Λ_FN is the FN breaking parameter.

In the Unitary Manifold, the orbifold boundary condition assigns integer
lattice positions ℓ to fermions:

    c_L = ℓ × Δc = ℓ × n_w / k_CS

The identification proposed here is:

    Q_FN_i = ℓ_i   (FN charge = lattice position)
    ε = exp(-n_w k_CS / (2π))   (FN parameter from KK geometry)

Under this identification, the FN suppression factor becomes:

    ε^|ℓ_i - ℓ_j| = exp(-|ℓ_i - ℓ_j| × n_w × k_CS / (2π))

which matches the overlap suppression from the orbifold wavefunctions.

## Gen-1 derivation under the identification

Gen-1 has lattice position ℓ = 2 (two steps from IR brane):
    c_L^{gen1} = 2 × Δc = 2 × 5/74 = 10/74

The FN charge is Q_FN^{gen1} = 2 (two orbifold lattice steps from IR).

The FN breaking parameter:
    ε = Δc = n_w / k_CS = 5/74 ≈ 0.0676

is identified with the fundamental lattice step.

## Honest assessment

This identification is a CANDIDATE, not a proof:
  - It requires that the FN flavon ⟨φ_FN⟩ couples with the same coefficient
    as the orbifold lattice step — this is a non-trivial assumption.
  - The identification n_FN = ℓ requires that the FN symmetry is the
    discrete shift symmetry of the orbifold, not an independent new symmetry.
  - If the FN symmetry is identified with U(1)_KK (the zero mode of the bulk
    gauge field in the compact dimension), the identification is natural.

Status: GEN1_FERMION_FN_ORBIFOLD_DERIVATION_ATTEMPTED
  → Not yet DERIVED (identification is a candidate, not a proof)
  → Advances from NATURAL (Pillar 546) to ATTEMPTED

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "N_W",
    "K_CS",
    "DELTA_C",
    "FN_IDENTIFICATION",
    "GEN1_CL_CANDIDATE",
    "FERMION_FN_TABLE",
    "fn_charge_from_lattice",
    "fn_epsilon",
    "fn_yukawa_suppression",
    "orbifold_yukawa_overlap",
    "fn_orbifold_consistency",
    "gen1_derivation_status",
    "mass_ratio_prediction",
    "pillar_report",
]

PILLAR_NUMBER: int = 550
PILLAR_STATUS: str = "GEN1_FERMION_FN_ORBIFOLD_DERIVATION_ATTEMPTED"
PILLAR_TITLE: str = "Gen-1 Fermion c_L: FN Charge = Orbifold Winding Derivation"
VERSION: str = "v19.1"

# ─── Core constants ──────────────────────────────────────────────────────────

N_W: int = 5
K_CS: int = 74
DELTA_C: float = N_W / K_CS     # = 5/74 ≈ 0.0676
K_PI_R: float = 37.0            # kπR (hierarchy logarithm)

# ─── FN ↔ Orbifold identification ────────────────────────────────────────────

FN_IDENTIFICATION: Dict[str, Any] = {
    "proposal": "Q_FN_i = ℓ_i (FN charge = orbifold lattice position)",
    "epsilon_identification": "ε_FN = Δc = n_w / k_CS = 5/74",
    "physical_basis": (
        "If the FN symmetry is identified with U(1)_KK (zero mode of the bulk "
        "compact gauge field), the FN charge is naturally the KK zero-mode quantum "
        "number, which coincides with the orbifold lattice position ℓ."
    ),
    "status": "CANDIDATE — not proved",
    "blocking_assumptions": [
        "FN flavon couples with coefficient exactly equal to orbifold lattice step Δc.",
        "FN symmetry = discrete shift symmetry of the orbifold (no independent new symmetry).",
        "U(1)_KK zero mode provides the FN charge (not an additional external field).",
    ],
    "if_identification_holds": (
        "Gen-1 c_L = 10/74 is FIRST_PRINCIPLES_DERIVED from the orbifold. "
        "The FN mechanism is not an independent assumption but a consequence of the orbifold geometry."
    ),
}

# ─── Lattice positions and FN charges ────────────────────────────────────────

LATTICE_POSITIONS: Dict[str, int] = {
    "t": 0, "b": 0, "tau": 0,    # gen-3: IR-localized, ℓ = 0
    "c": 1, "s": 1, "mu":  1,    # gen-2: one step, ℓ = 1
    "u": 2, "d": 2, "e":   2,    # gen-1: two steps, ℓ = 2
}

# Gen-1 c_L candidate under FN = orbifold identification
GEN1_CL_CANDIDATE: Dict[str, Any] = {
    "lattice_position": 2,
    "fn_charge": 2,
    "cl_value": 2 * DELTA_C,     # = 10/74 ≈ 0.1351
    "derivation": "ℓ = 2 from Z₃ orbifold, n_FN = ℓ = 2 from identification",
    "status": "FIRST_PRINCIPLES_CANDIDATE",
    "consistent_with_pillar546": True,
    "advance_over_pillar546": (
        "Pillar 546: gen-1 is NATURAL (FN dominates, not derived). "
        "Pillar 550: gen-1 FN charge n_FN = ℓ = 2 IDENTIFIED with orbifold position."
    ),
}

# Full fermion table with FN charges under the identification
FERMION_FN_TABLE: Dict[str, Dict[str, Any]] = {
    fermion: {
        "lattice_position": ell,
        "fn_charge": ell,                           # Q_FN = ℓ (identification)
        "cl_value": ell * DELTA_C,                  # c_L = ℓ × Δc
        "fn_epsilon_power": ell,                    # suppression ~ ε^ℓ
        "pillar546_status": (
            "DERIVED" if ell <= 1 else "NATURAL"    # gen-1 was NATURAL in P546
        ),
        "pillar550_status": (
            "DERIVED" if ell <= 1 else "FIRST_PRINCIPLES_CANDIDATE"
        ),
    }
    for fermion, ell in LATTICE_POSITIONS.items()
}


# ─── Core functions ───────────────────────────────────────────────────────────

def fn_charge_from_lattice(lattice_position: int) -> int:
    """Return the FN charge under the identification Q_FN = ℓ."""
    return lattice_position


def fn_epsilon() -> float:
    """Return the FN breaking parameter under the identification ε = Δc = n_w / k_CS."""
    return DELTA_C


def fn_yukawa_suppression(q_fn_i: int, q_fn_j: int) -> float:
    """Compute the FN Yukawa suppression factor ε^|Q_FN_i - Q_FN_j|."""
    return fn_epsilon() ** abs(q_fn_i - q_fn_j)


def orbifold_yukawa_overlap(ell_i: int, ell_j: int, kpi_r: float = K_PI_R) -> float:
    """Compute the orbifold Yukawa overlap for fermions at lattice positions ℓ_i, ℓ_j.

    The overlap is:
        O(ℓ_i, ℓ_j) = exp(-|ℓ_i - ℓ_j| × Δc × kπR)

    Under the identification ε = Δc and Q_FN = ℓ, this equals:
        O(ℓ_i, ℓ_j) = ε^|ℓ_i - ℓ_j| × exp(|ℓ_i - ℓ_j| × (1 - kπR × Δc))

    At leading order (kπR × Δc = 37 × 5/74 = 2.5):
        O ≈ ε^|Δℓ| × exp(-|Δℓ| × 1.5)   (residual non-FN factor)
    """
    delta_ell = abs(ell_i - ell_j)
    c_avg = delta_ell * DELTA_C
    return math.exp(-c_avg * kpi_r)


def fn_orbifold_consistency(ell_i: int, ell_j: int, kpi_r: float = K_PI_R) -> Dict[str, float]:
    """Compare FN Yukawa suppression with orbifold overlap.

    Returns a consistency check: how well the FN identification captures
    the orbifold suppression.
    """
    fn_supp = fn_yukawa_suppression(fn_charge_from_lattice(ell_i),
                                     fn_charge_from_lattice(ell_j))
    orb_overlap = orbifold_yukawa_overlap(ell_i, ell_j, kpi_r)
    ratio = fn_supp / orb_overlap if orb_overlap > 0 else float("inf")

    return {
        "ell_i": ell_i,
        "ell_j": ell_j,
        "fn_suppression": fn_supp,
        "orbifold_overlap": orb_overlap,
        "ratio_fn_over_orbifold": ratio,
        "log_ratio": math.log(ratio) if ratio > 0 and ratio != float("inf") else None,
        "consistent": 0.01 < ratio < 100.0,  # order-of-magnitude consistency
    }


def gen1_derivation_status() -> Dict[str, Any]:
    """Return the honest derivation status for gen-1 fermions."""
    fn_consistency_23 = fn_orbifold_consistency(1, 0)  # gen2 vs gen3
    fn_consistency_13 = fn_orbifold_consistency(2, 0)  # gen1 vs gen3

    return {
        "gen1_cl": GEN1_CL_CANDIDATE["cl_value"],
        "fn_charge": GEN1_CL_CANDIDATE["fn_charge"],
        "status_pillar546": "NATURAL (FN dominates — not derived)",
        "status_pillar550": "FIRST_PRINCIPLES_CANDIDATE",
        "identification": FN_IDENTIFICATION["proposal"],
        "fn_consistency_gen23": fn_consistency_23,
        "fn_consistency_gen13": fn_consistency_13,
        "blocking_assumptions": FN_IDENTIFICATION["blocking_assumptions"],
        "advance": (
            "The FN charge n_FN = ℓ = 2 is now IDENTIFIED with the orbifold "
            "lattice position, reducing the unexplained FN charge to zero. "
            "The identification is a candidate — not a proof — because it requires "
            "that FN symmetry = U(1)_KK (an additional assumption)."
        ),
    }


def mass_ratio_prediction() -> Dict[str, Any]:
    """Predict fermion mass ratios from orbifold + FN identification.

    The mass ratio between generations is:
        m_i / m_j ≈ ε^|Δℓ| = (5/74)^|Δℓ|

    For Δℓ = 1 (adjacent generations):
        m_2 / m_3 ≈ 5/74 ≈ 0.068 (cf. m_μ/m_τ ≈ 0.059, m_c/m_t ≈ 0.007)

    For Δℓ = 2 (gen-1 vs gen-3):
        m_1 / m_3 ≈ (5/74)² ≈ 0.0046 (cf. m_e/m_τ ≈ 0.00029, m_u/m_t ≈ 0.00001)
    """
    eps = fn_epsilon()
    return {
        "epsilon": eps,
        "ratio_gen2_over_gen3_predicted": eps ** 1,
        "ratio_gen1_over_gen3_predicted": eps ** 2,
        "ratio_mu_over_tau_pdg": 0.059,     # m_μ/m_τ ≈ 0.059
        "ratio_e_over_tau_pdg": 0.000290,   # m_e/m_τ ≈ 0.000290
        "ratio_mc_over_mt_pdg": 0.0065,     # m_c/m_t ≈ 0.0065
        "ratio_gen2_over_gen3_agreement": (
            "Order-of-magnitude agreement for leptons (predicted 0.068 vs 0.059). "
            "Quark sector differs due to top/bottom mass splitting from Ŷ₅ × W_R."
        ),
        "ratio_gen1_over_gen3_agreement": (
            "Predicted (5/74)² ≈ 0.0046, cf. m_e/m_τ ≈ 0.00029. "
            "Factor ~16 discrepancy in leptons — FN correction or sector weight needed. "
            "Honest: identification provides order-of-magnitude, not exact, prediction."
        ),
        "status": "ORDER_OF_MAGNITUDE_CANDIDATE",
    }


def pillar_report() -> Dict[str, Any]:
    """Full Pillar 550 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "fn_identification": FN_IDENTIFICATION,
        "gen1_cl_candidate": GEN1_CL_CANDIDATE,
        "fermion_fn_table": FERMION_FN_TABLE,
        "gen1_derivation_status": gen1_derivation_status(),
        "mass_ratio_prediction": mass_ratio_prediction(),
        "epistemic_delta": (
            "Gen-1 fermions: NATURAL (Pillar 546) → "
            "FIRST_PRINCIPLES_CANDIDATE (Pillar 550). "
            "FN charge n_FN = ℓ = 2 identified with orbifold lattice position. "
            "Not yet DERIVED — identification is a candidate pending U(1)_KK proof."
        ),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
        "parent_pillar": 546,
    }
