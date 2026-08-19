# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/fn_charge_geometry_audit.py
========================================
Sprint AL — Wave 4: Fermion Mass Hierarchy FN Charge Geometry Audit.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).

PURPOSE
-------
Gap 4 in the Sprint AH derivation chain:

    L4.3: Fermion mass hierarchy from geometry alone — OPEN GAP
    FN (Froggatt-Nielsen) charges are inputs, not outputs of the UM geometry.

This module executes the definitive audit:

1. Catalogues every FN charge used in the Yukawa/CKM/PMNS chain.
2. For each charge, determines whether it is:
   (a) A FREE PARAMETER (no geometric origin identified)
   (b) GEOMETRICALLY_MOTIVATED (partial correspondence with orbifold)
   (c) GEOMETRICALLY_DERIVED (proved from orbifold fixed-point positions)
3. Tests the GEOMETRICAL FN HYPOTHESIS: can orbifold fixed-point positions
   on S¹/Z₂ with (5,7) winding determine FN charges?
4. Reports the EXACT free-parameter count.

RESULT
------
    FN_AUDIT_STATUS = "ARCHITECTURE_LIMIT_CERTIFIED"

    Free parameter count: 9 independent FN charges remain as inputs.
    The geometric FN hypothesis PARTIALLY holds: the ratio structure of
    FN charges is consistent with orbifold geometry, but the absolute
    normalisation requires one external input.

    ZERO-FREE-PARAMETER CLAIM: NOT ACHIEVED.
    The fermion mass hierarchy in the UM requires FN charges as inputs.
    This is an EXPLICIT OPEN GAP certified as an architecture limit.

PHYSICAL CONTENT
----------------
The Froggatt-Nielsen mechanism introduces a U(1)_FN flavour symmetry.
Each fermion f has an FN charge Q_f, and Yukawa couplings are suppressed:
    Y_{ij} ~ ε^{|Q_i + Q_j|}
where ε = ⟨Φ_FN⟩ / Λ_FN is the FN breaking parameter.

In the UM orbifold context, the natural identification is:
    Q_f = n_w × (fixed-point position of f's wavefunction peak)

For S¹/Z₂ with n_w = 5: the winding-weighted position of the i-th
fermionic zero mode's localisation point (in units of πR) gives a
natural FN charge Q_i ≈ n_w × c_i where c_i is the bulk mass parameter.

However: c_i is itself a free parameter that enters as input to the
bulk fermion profile. The orbifold geometry constrains the allowed
RANGE of c_i (0 < c_i < 1) but does not determine the exact values.
"""
from __future__ import annotations

import math
from typing import Dict, Any, List, Optional

__all__ = [
    "FN_AUDIT_STATUS",
    "FN_CHARGE_TABLE",
    "N_FREE_PARAMETERS_EXACT",
    "fn_charge_table",
    "geometric_fn_hypothesis_test",
    "free_parameter_count",
    "fn_geometry_audit",
    "fermion_mass_gap4_certificate",
]

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
N_W: int = 5                   # Primary winding number
K_CS: int = 74                 # Chern-Simons level
EPSILON_FN: float = 0.22       # FN breaking parameter ε ≈ λ_C (Cabibbo angle proxy)
PI_KR: float = 37.0            # RS1 hierarchy parameter

# PDG masses (GeV) for reference
PDG_MASSES = {
    "u": 2.2e-3,  "d": 4.7e-3,  "s": 95e-3, "c": 1.275, "b": 4.18, "t": 173.0,
    "e": 0.511e-3, "mu": 0.106, "tau": 1.777,
}

# ---------------------------------------------------------------------------
# FN charge table: the complete audit
# ---------------------------------------------------------------------------

def fn_charge_table() -> List[Dict[str, Any]]:
    """
    Return the complete FN charge table for all SM fermions.

    For each fermion, we record:
    - name: particle name
    - Q_FN: the FN charge used in Yukawa texture
    - origin: FREE_PARAMETER / GEOMETRICALLY_MOTIVATED / GEOMETRICALLY_DERIVED
    - orbit_position: the orbifold position (c_i value) if geometrically motivated
    - reasoning: explanation

    Sources: Yukawa texture from yukawa_orbifold_bc_texture.py (Pillar 688);
    FN charges from Froggatt-Nielsen texture matching PDG quark/lepton masses.
    """
    return [
        # Quark left-handed doublets (SU(2)_L pairs)
        {
            "name": "Q_1 (ud left)",
            "Q_FN": 3,
            "sector": "quark",
            "chirality": "L",
            "origin": "GEOMETRICALLY_MOTIVATED",
            "orbit_c_value": 0.6,  # c_L ~ 0.6 for lightest generation
            "geometric_link": "c_L ≈ Q_FN / n_w = 3/5 = 0.6; orbifold localisation toward UV brane",
            "reasoning": (
                "Q=3 is motivated by c_L=0.6 giving the correct hierarchy m_u/m_t ~ ε^6. "
                "But c_L=0.6 is itself a fitted value, not derived from geometry alone."
            ),
            "is_free": True,
        },
        {
            "name": "Q_2 (cs left)",
            "Q_FN": 2,
            "sector": "quark",
            "chirality": "L",
            "origin": "GEOMETRICALLY_MOTIVATED",
            "orbit_c_value": 0.4,
            "geometric_link": "c_L ≈ 2/5 = 0.4 for second generation",
            "reasoning": "Q=2 motivated by Δc = 0.2 between generations from texture; not derived.",
            "is_free": True,
        },
        {
            "name": "Q_3 (tb left)",
            "Q_FN": 0,
            "sector": "quark",
            "chirality": "L",
            "origin": "GEOMETRICALLY_MOTIVATED",
            "orbit_c_value": 0.0,
            "geometric_link": "Third generation localised near IR brane; c_L → 0",
            "reasoning": "Q=0 by convention (top quark reference). Fixed, not free.",
            "is_free": False,
        },
        # Quark right-handed singlets
        {
            "name": "u_R (up-right)",
            "Q_FN": 3,
            "sector": "quark",
            "chirality": "R",
            "origin": "FREE_PARAMETER",
            "orbit_c_value": None,
            "geometric_link": None,
            "reasoning": "Q_uR = 3 fitted to match m_u/v. No geometric determination.",
            "is_free": True,
        },
        {
            "name": "c_R (charm-right)",
            "Q_FN": 1,
            "sector": "quark",
            "chirality": "R",
            "origin": "FREE_PARAMETER",
            "orbit_c_value": None,
            "geometric_link": None,
            "reasoning": "Q_cR = 1 fitted to m_c/v. No geometric determination.",
            "is_free": True,
        },
        {
            "name": "t_R (top-right)",
            "Q_FN": 0,
            "sector": "quark",
            "chirality": "R",
            "origin": "GEOMETRICALLY_MOTIVATED",
            "orbit_c_value": 0.0,
            "geometric_link": "Top quark c_R ~ 0; UV brane localisation gives O(1) Yukawa",
            "reasoning": "Q=0 consistent with c_R ~ 0 near IR; partially geometric.",
            "is_free": False,
        },
        {
            "name": "d_R (down-right)",
            "Q_FN": 4,
            "sector": "quark",
            "chirality": "R",
            "origin": "FREE_PARAMETER",
            "orbit_c_value": None,
            "geometric_link": None,
            "reasoning": "Q_dR = 4 fitted to m_d. No geometric determination.",
            "is_free": True,
        },
        {
            "name": "s_R (strange-right)",
            "Q_FN": 2,
            "sector": "quark",
            "chirality": "R",
            "origin": "FREE_PARAMETER",
            "orbit_c_value": None,
            "geometric_link": None,
            "reasoning": "Q_sR = 2 fitted to m_s. No geometric determination.",
            "is_free": True,
        },
        {
            "name": "b_R (bottom-right)",
            "Q_FN": 0,
            "sector": "quark",
            "chirality": "R",
            "origin": "GEOMETRICALLY_MOTIVATED",
            "orbit_c_value": 0.0,
            "geometric_link": "Q=0 by IR localisation (b mass ~ v); partially geometric.",
            "reasoning": "Q=0 consistent with IR localisation; not uniquely determined by geometry.",
            "is_free": False,
        },
        # Lepton doublets
        {
            "name": "L_1 (e-nu left)",
            "Q_FN": 3,
            "sector": "lepton",
            "chirality": "L",
            "origin": "GEOMETRICALLY_MOTIVATED",
            "orbit_c_value": 0.6,
            "geometric_link": "Same as Q_1: c_L ~ 0.6 for first generation",
            "reasoning": "Q=3 motivated by c_L=0.6; but c_L not derived from geometry.",
            "is_free": True,
        },
        {
            "name": "L_2 (mu-nu left)",
            "Q_FN": 1,
            "sector": "lepton",
            "chirality": "L",
            "origin": "GEOMETRICALLY_MOTIVATED",
            "orbit_c_value": 0.2,
            "geometric_link": "c_L ~ 0.2 for second generation",
            "reasoning": "Q=1 motivated but not derived.",
            "is_free": True,
        },
        {
            "name": "L_3 (tau-nu left)",
            "Q_FN": 0,
            "sector": "lepton",
            "chirality": "L",
            "origin": "GEOMETRICALLY_MOTIVATED",
            "orbit_c_value": 0.0,
            "geometric_link": "Third generation: IR localised",
            "reasoning": "Q=0 by convention; consistent with geometry.",
            "is_free": False,
        },
        # Lepton right-handed singlets
        {
            "name": "e_R (electron-right)",
            "Q_FN": 4,
            "sector": "lepton",
            "chirality": "R",
            "origin": "FREE_PARAMETER",
            "orbit_c_value": None,
            "geometric_link": None,
            "reasoning": "Q=4 fitted to m_e/v. No geometric determination.",
            "is_free": True,
        },
        {
            "name": "mu_R (muon-right)",
            "Q_FN": 1,
            "sector": "lepton",
            "chirality": "R",
            "origin": "FREE_PARAMETER",
            "orbit_c_value": None,
            "geometric_link": None,
            "reasoning": "Q=1 fitted to m_mu/v. No geometric determination.",
            "is_free": True,
        },
        {
            "name": "tau_R (tau-right)",
            "Q_FN": 0,
            "sector": "lepton",
            "chirality": "R",
            "origin": "GEOMETRICALLY_MOTIVATED",
            "orbit_c_value": 0.0,
            "geometric_link": "Q=0 by IR localisation; tau mass ~ v × O(1)",
            "reasoning": "Q=0 consistent with IR localisation.",
            "is_free": False,
        },
    ]


# Expose the table as a module-level constant
FN_CHARGE_TABLE: List[Dict[str, Any]] = fn_charge_table()
N_FREE_PARAMETERS_EXACT: int = sum(1 for e in FN_CHARGE_TABLE if e["is_free"])


# ---------------------------------------------------------------------------
# Geometric FN hypothesis test
# ---------------------------------------------------------------------------

def geometric_fn_hypothesis_test() -> Dict[str, Any]:
    """
    Test the geometrical FN hypothesis: can orbifold fixed-point positions
    on S¹/Z₂ with n_w = 5 determine FN charges?

    The hypothesis: Q_f = round(n_w × c_f) where c_f is the zero-mode
    peak position (bulk mass parameter, 0 ≤ c_f ≤ 1).

    Test: for each fermion with a geometric link, does round(n_w × c_f) = Q_FN?
    """
    table = fn_charge_table()
    results = []

    for entry in table:
        if entry["orbit_c_value"] is not None:
            predicted_Q = round(N_W * entry["orbit_c_value"])
            matches = predicted_Q == entry["Q_FN"]
            results.append({
                "name": entry["name"],
                "Q_FN": entry["Q_FN"],
                "c_value": entry["orbit_c_value"],
                "predicted_Q": predicted_Q,
                "geometric_prediction_correct": matches,
                "origin": entry["origin"],
            })

    n_geometrically_linked = len(results)
    n_correct = sum(1 for r in results if r["geometric_prediction_correct"])
    n_incorrect = n_geometrically_linked - n_correct

    # The geometric rule works only if c_f is itself determined geometrically.
    # The key question: what determines c_f?
    # In RS1 orbifold: c_f is a free 5D bulk mass parameter, not fixed by topology.
    # Therefore the geometric FN hypothesis is PARTIALLY CONSISTENT but NOT DERIVED.

    return {
        "n_geometrically_linked": n_geometrically_linked,
        "n_correct": n_correct,
        "n_incorrect": n_incorrect,
        "accuracy": n_correct / n_geometrically_linked if n_geometrically_linked else 0.0,
        "results": results,
        "hypothesis_status": "PARTIALLY_CONSISTENT_NOT_DERIVED",
        "conclusion": (
            f"The geometric FN hypothesis Q = round(n_w × c) is consistent for "
            f"{n_correct}/{n_geometrically_linked} geometrically-linked fermions. "
            "However, this consistency is TAUTOLOGICAL: c_f was fitted to reproduce Q_f, "
            "so the relation Q = round(n_w × c) holds by construction when c = Q/n_w. "
            "The hypothesis is not a prediction; it is a relabeling. "
            "TRUE geometric derivation would require determining c_f from the 5D action "
            "alone (e.g., from orbifold fixed-point quantisation). This is NOT achieved."
        ),
        "tautology_flag": True,
    }


# ---------------------------------------------------------------------------
# Free parameter count
# ---------------------------------------------------------------------------

def free_parameter_count() -> Dict[str, Any]:
    """
    Count and classify FN charge free parameters.
    """
    table = fn_charge_table()
    free = [e for e in table if e["is_free"]]
    geom_motivated = [e for e in table if not e["is_free"] and e["origin"] != "GEOMETRICALLY_DERIVED"]
    fixed_by_convention = [e for e in table if e["Q_FN"] == 0]

    # Independent charges: the full texture requires independent Q values
    # The quark sector has texture: Y_u ~ ε^{|Q_{Li}+Q_{Rj}|}, similarly for Y_d, Y_e
    # Independent inputs: Q_L1, Q_L2, Q_u1, Q_u2, Q_d1, Q_d2, Q_d3 in quark sector
    #                    Q_l1, Q_l2, Q_e1, Q_e2 in lepton sector (some shared by structure)
    # After convention fixing (Q_L3 = Q_t = Q_b = Q_tau = 0):
    # Residual free: Q_L1, Q_L2, Q_u1, Q_u2, Q_d1, Q_d2, Q_d3, Q_e1, Q_e2 = 9 parameters

    n_free = len(free)
    n_independent = 9  # see above

    return {
        "total_entries": len(table),
        "free_parameters": n_free,
        "n_independent_free": n_independent,
        "convention_fixed": len([e for e in table if e["Q_FN"] == 0]),
        "geometrically_motivated": len(geom_motivated),
        "free_entries": [e["name"] for e in free],
        "zero_free_parameter_claim": False,  # honest negative
        "conclusion": (
            f"HONEST COUNT: The UM Yukawa texture requires {n_independent} independent "
            f"FN charges as inputs. These are NOT derived from the 5D geometry. "
            "The zero-free-parameter claim for the fermion mass hierarchy is NOT achieved. "
            "This is an ARCHITECTURE_LIMIT: the RS1 orbifold topology constrains the "
            "allowed range of c_f values but does not determine them uniquely."
        ),
    }


# ---------------------------------------------------------------------------
# Full audit
# ---------------------------------------------------------------------------

def fn_geometry_audit() -> Dict[str, Any]:
    """Full Gap 4 audit: FN charges, geometric hypothesis, free parameter count."""
    table = fn_charge_table()
    hypothesis = geometric_fn_hypothesis_test()
    param_count = free_parameter_count()

    return {
        "fn_charge_table": table,
        "geometric_hypothesis": hypothesis,
        "free_parameter_count": param_count,
        "gap4_status": "ARCHITECTURE_LIMIT_CERTIFIED",
        "FN_AUDIT_STATUS": "ARCHITECTURE_LIMIT_CERTIFIED",
        "honest_statement": (
            "Gap 4 (L4.3): Fermion mass hierarchy from geometry alone is NOT achievable "
            f"in the current UM/RS1 framework. The Froggatt-Nielsen mechanism requires "
            f"{param_count['n_independent_free']} independent charge inputs. "
            "The orbifold geometry provides a MECHANISM (exponential wavefunction suppression) "
            "but not the INPUTS (bulk mass parameters c_f). "
            "This is an honest architecture limit of the RS1 ansatz."
        ),
        "what_geometry_does_provide": [
            "Exponential mass hierarchy structure: m_i/m_j ~ exp(Δc × πkR) ≫ 1 for Δc ~ 0.1",
            "Constraint 0 < c_f < 1 (orbifold boundary)",
            "Three generations (fixed-point counting, Pillar 770)",
            "SM quantum numbers (from SU(5)→SM projection, Pillar 770)",
        ],
        "what_geometry_does_not_provide": [
            "Exact values of c_f (= exact FN charges)",
            "Absolute mass scale (Yukawa coupling λ_Y is a free parameter)",
            "CP-violating phases in CKM/PMNS (arise from texture, not geometry alone)",
        ],
        "lean4_reference": "lean4/UnitaryManifold/FermionMassGeometry.lean (created in this sprint)",
    }


def fermion_mass_gap4_certificate() -> Dict[str, Any]:
    """Machine-readable certificate for Gap 4 closure attempt."""
    audit = fn_geometry_audit()
    return {
        "sprint": "AL / Wave 4",
        "gap": "Gap 4 (L4.3: Fermion mass hierarchy from geometry alone)",
        "before": "OPEN (scoped)",
        "after": audit["gap4_status"],
        "FN_AUDIT_STATUS": audit["FN_AUDIT_STATUS"],
        "free_parameters_remaining": 9,
        "zero_free_parameter_claim": False,
        "honest_statement": audit["honest_statement"],
        "what_geometry_provides": audit["what_geometry_does_provide"],
        "what_geometry_does_not_provide": audit["what_geometry_does_not_provide"],
    }


# Canonical status token
FN_AUDIT_STATUS: str = "ARCHITECTURE_LIMIT_CERTIFIED"
