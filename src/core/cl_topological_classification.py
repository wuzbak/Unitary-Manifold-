# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/cl_topological_classification.py
==========================================
Pillar 164 — c_L Topological Classification for the Unitary Manifold.

CONDITIONAL THEOREM (Left-Chiral Orbifold Fixed-Point Theorem)
--------------------------------------------------------------
The left-chiral bulk-mass parameter c_L is a topological invariant of the
Chern-Simons / S¹/Z₂ structure with level k_CS:

    c_L = (k_CS − N_fp_L) / k_CS

where:
  k_CS   = 74  — Chern-Simons level = 5² + 7² (selected by birefringence data)
  N_fp_L = 3   — number of left-chiral orbifold fixed structures:
                   UV brane (y=0), IR brane (y=πR), chiral midpoint (y=πR/2)

For k_CS = 74, N_fp_L = 3:
    c_L = (74 − 3) / 74 = 71/74 ≈ 0.9595

Comparison with Pillar 144 numerical result c_L^phys = 0.961:
    |71/74 − 0.961| / 0.961 ≈ 0.16%  → CONSISTENT (within 1%)

Why k_CS in the denominator (not n_w² = 25):
  The left-chiral zero mode couples to the Chern-Simons level k_CS = 74,
  not just the winding sector count n_w² = 25, because the chiral midpoint
  structure is tied to the braid group representation at level k_CS.

Why N_fp_L = 3 (not 2 as for right-chiral modes):
  For right-chiral modes the Z₂ orbifold has fixed points only at the two
  branes (UV y=0 and IR y=πR), giving N_fp_R = 2.  For LEFT-chiral modes,
  the chirality-reversal Z₂ (which flips L↔R) has an additional fixed set
  at the bulk midpoint y = πR/2, so N_fp_L = 3.

CONDITIONAL caveat:
  The identification of y = πR/2 as a Z₂ fixed set under the chirality-reversal
  action requires a geometric proof that the chiral Z₂ has a fixed-point locus
  at the orbifold midpoint.  This is the primary open issue for this pillar.

Theory: ThomasCory Walker-Pearson (2026)
Code:   GitHub Copilot (AI)
"""

import math

# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

N_W = 5                            # winding number (Pillar 67)
K_CS = 74                          # Chern-Simons level = 5² + 7²
N_FP_R = 2                         # right-chiral orbifold fixed points (UV + IR brane)
N_FP_L = 3                         # left-chiral fixed structures (UV + IR + chiral midpoint)
C_R_THEOREM = 23 / 25              # = 0.920, Pillar 143 theorem
C_L_TOPOLOGICAL = 71 / 74         # = (K_CS − N_FP_L)/K_CS ≈ 0.9595
C_L_PHYS_NUMERICAL = 0.961        # Pillar 144 numerical result
PILLAR144_NUMERICAL_C_L = 0.961   # alias


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def c_r_theorem_recall(n_w: int = N_W, n_fp_r: int = N_FP_R) -> dict:
    """Recall the Pillar 143 c_R theorem for reference.

    c_R = (n_w² − N_fp_R) / n_w²

    Parameters
    ----------
    n_w:
        Winding number (default 5).
    n_fp_r:
        Number of right-chiral orbifold fixed points (default 2).

    Returns
    -------
    dict with keys 'c_r', 'n_w', 'n_fp_r', 'formula', 'pillar'.
    """
    n_w_sq = n_w ** 2
    c_r = (n_w_sq - n_fp_r) / n_w_sq
    return {
        "c_r": c_r,
        "n_w": n_w,
        "n_fp_r": n_fp_r,
        "formula": f"c_R = (n_w^2 - N_fp_R) / n_w^2 = ({n_w_sq} - {n_fp_r}) / {n_w_sq}",
        "pillar": 143,
    }


def count_left_chiral_fixed_points(n_w: int = N_W) -> dict:
    """Count N_fp_L for left-chiral modes on S¹/Z₂.

    For left-chiral modes the chirality-reversal Z₂ introduces an extra
    fixed structure at the bulk midpoint y = πR/2, in addition to the two
    brane fixed points shared with right-chiral modes.

    Parameters
    ----------
    n_w:
        Winding number (not used in the count, kept for interface consistency).

    Returns
    -------
    dict with keys 'n_fp_l', 'uv_brane_fixed', 'ir_brane_fixed',
    'chiral_midpoint_fixed', 'argument', 'caveat'.
    """
    uv_brane_fixed = 1
    ir_brane_fixed = 1
    chiral_midpoint_fixed = 1
    n_fp_l = uv_brane_fixed + ir_brane_fixed + chiral_midpoint_fixed

    argument = (
        "UV brane (y=0) is a fixed point of the Z2 orbifold for both chiralities. "
        "IR brane (y=piR) is likewise a fixed point for both chiralities. "
        "The chirality-reversal Z2 (L<->R) has an additional fixed set at "
        "the bulk midpoint y=piR/2, contributing one more fixed structure "
        "for LEFT-chiral modes only. Total N_fp_L = 3."
    )
    caveat = (
        "CONDITIONAL: chiral midpoint interpretation requires chirality-reversal "
        "Z2 to have fixed set at piR/2"
    )

    return {
        "n_fp_l": n_fp_l,
        "uv_brane_fixed": uv_brane_fixed,
        "ir_brane_fixed": ir_brane_fixed,
        "chiral_midpoint_fixed": chiral_midpoint_fixed,
        "argument": argument,
        "caveat": caveat,
    }


def c_l_topological_theorem(k_cs: int = K_CS, n_fp_l: int = N_FP_L) -> dict:
    """THE THEOREM: c_L = (k_CS − N_fp_L) / k_CS.

    Parameters
    ----------
    k_cs:
        Chern-Simons level (default 74).
    n_fp_l:
        Number of left-chiral fixed structures (default 3).

    Returns
    -------
    dict with keys 'c_l', 'k_cs', 'n_fp_l', 'formula', 'status'.
    """
    c_l = (k_cs - n_fp_l) / k_cs
    return {
        "c_l": c_l,
        "k_cs": k_cs,
        "n_fp_l": n_fp_l,
        "formula": f"c_L = (k_CS - N_fp_L) / k_CS = ({k_cs} - {n_fp_l}) / {k_cs}",
        "status": "CONDITIONAL_THEOREM",
    }


def compare_c_l_theorem_vs_numerical(
    k_cs: int = K_CS, n_fp_l: int = N_FP_L
) -> dict:
    """Compare c_L topological theorem vs Pillar 144 numerical result.

    Parameters
    ----------
    k_cs:
        Chern-Simons level (default 74).
    n_fp_l:
        Number of left-chiral fixed structures (default 3).

    Returns
    -------
    dict with keys 'c_l_topological', 'c_l_numerical', 'absolute_difference',
    'fractional_difference', 'consistency', 'status'.
    """
    c_l_topological = (k_cs - n_fp_l) / k_cs
    c_l_numerical = PILLAR144_NUMERICAL_C_L
    absolute_difference = abs(c_l_topological - c_l_numerical)
    fractional_difference = absolute_difference / c_l_numerical

    if fractional_difference < 0.01:
        consistency = "CONSISTENT"
    elif fractional_difference < 0.05:
        consistency = "CLOSE"
    else:
        consistency = "INCONSISTENT"

    return {
        "c_l_topological": c_l_topological,
        "c_l_numerical": c_l_numerical,
        "absolute_difference": absolute_difference,
        "fractional_difference": fractional_difference,
        "consistency": consistency,
        "status": "CONDITIONAL_THEOREM",
    }


def c_l_formula_comparison() -> dict:
    """Compare three candidate formulas for c_L.

    Formulas:
      a) Topological via n_w: (n_w² − N_fp_R) / n_w² = 2/25 = 0.08
         (This is c_L^TOPO from Pillar 143 — IR-localized, NOT physical.)
      b) Topological via k_CS: (k_CS − N_fp_L) / k_CS = 71/74 ≈ 0.9595
         (Pillar 164 theorem — UV-localized, consistent with sub-eV masses.)
      c) Numerical (Pillar 144): 0.961

    Returns
    -------
    dict with keys 'c_l_topo_nw', 'c_l_topo_kcs', 'c_l_numerical',
    'preferred_formula', 'agreement_kcs_vs_numerical'.
    """
    c_l_topo_nw = N_FP_R / (N_W ** 2)          # 2/25 = 0.08
    c_l_topo_kcs = (K_CS - N_FP_L) / K_CS      # 71/74 ≈ 0.9595
    c_l_numerical = PILLAR144_NUMERICAL_C_L     # 0.961

    agreement_kcs_vs_numerical = abs(c_l_topo_kcs - c_l_numerical) / c_l_numerical

    return {
        "c_l_topo_nw": c_l_topo_nw,
        "c_l_topo_kcs": c_l_topo_kcs,
        "c_l_numerical": c_l_numerical,
        "preferred_formula": "c_L = (k_CS - N_fp_L) / k_CS = 71/74",
        "agreement_kcs_vs_numerical": agreement_kcs_vs_numerical,
        "note_topo_nw": (
            "c_L = 2/25 = 0.08 is IR-localized (c < 1/2), giving exponentially "
            "LARGE Yukawa coupling — incompatible with sub-eV neutrino masses. "
            "It is a topological label, not the physical bulk-mass parameter."
        ),
    }


def neutrino_mass_consistency_check(c_l: float = C_L_TOPOLOGICAL) -> dict:
    """Check that c_L = 71/74 gives UV-localized zero mode with sub-eV neutrino mass.

    For Randall-Sundrum geometry with πkR ≈ 37:
      f₀(c) ~ exp(-(c - 1/2) × πkR)   for c > 1/2  (UV-localized)

    Parameters
    ----------
    c_l:
        Left-chiral bulk-mass parameter (default 71/74).

    Returns
    -------
    dict with keys 'c_l', 'f0_c_l', 'uv_localized', 'sub_ev_consistent',
    'estimate_gev'.
    """
    pi_k_r = 37.0   # πkR ≈ 37 in RS1 with Planck-to-TeV hierarchy
    uv_localized = c_l > 0.5

    if uv_localized:
        f0_c_l = math.exp(-(c_l - 0.5) * pi_k_r)
    else:
        f0_c_l = math.exp(+(0.5 - c_l) * pi_k_r)

    # Right-chiral profile overlap (Pillar 143)
    c_r = C_R_THEOREM  # 23/25 = 0.920
    f0_c_r = math.exp(-(c_r - 0.5) * pi_k_r)

    v_higgs_gev = 246.0  # GeV
    estimate_gev = v_higgs_gev * f0_c_l * f0_c_r

    # Sub-eV threshold: 1 eV = 1e-9 GeV → sub-eV means < 1e-9 GeV
    sub_ev_consistent = estimate_gev < 1e-9

    return {
        "c_l": c_l,
        "f0_c_l": f0_c_l,
        "uv_localized": uv_localized,
        "sub_ev_consistent": sub_ev_consistent,
        "estimate_gev": estimate_gev,
    }


def cl_topological_classification_report() -> dict:
    """Full summary of the Pillar 164 theorem and its status.

    Returns
    -------
    dict with keys 'pillar', 'theorem', 'c_l_theorem', 'c_l_numerical',
    'agreement_pct', 'epistemic_label', 'open_issues', 'status'.
    """
    c_l_theorem = (K_CS - N_FP_L) / K_CS
    c_l_numerical = PILLAR144_NUMERICAL_C_L
    agreement_pct = abs(c_l_theorem - c_l_numerical) / c_l_numerical * 100.0

    return {
        "pillar": 164,
        "theorem": "c_L = (k_CS - N_fp_L) / k_CS = 71/74",
        "c_l_theorem": c_l_theorem,
        "c_l_numerical": c_l_numerical,
        "agreement_pct": agreement_pct,
        "epistemic_label": "CONDITIONAL_THEOREM",
        "open_issues": [
            "chiral_midpoint_Z2_fixed_set_requires_geometric_proof",
            "k_CS_denominator_vs_n_w_sq_choice",
        ],
        "status": "CONDITIONAL_THEOREM",
    }


def pillar164_summary() -> dict:
    """Concise one-dict summary of Pillar 164.

    Returns
    -------
    dict with keys 'pillar', 'theorem', 'c_l_predicted', 'c_l_numerical',
    'agreement_pct', 'status'.
    """
    return {
        "pillar": 164,
        "theorem": "c_L=(k_CS-3)/k_CS",
        "c_l_predicted": 71 / 74,
        "c_l_numerical": 0.961,
        "agreement_pct": 0.16,
        "status": "CONDITIONAL_THEOREM",
    }
