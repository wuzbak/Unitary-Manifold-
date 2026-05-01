# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/braid_uniqueness.py
================================
Pillar 95-B — Quantitative Braid Uniqueness Bounds for (5, 7).

Physical context
----------------
The Unitary Manifold selects the (5, 7) braided winding sector from among all
possible integer pairs (n1, n2) through the simultaneous intersection of three
independent constraints:

    1. Planck CMB spectral index:  |nₛ(n1) − 0.9649| ≤ 2σ_ns  ← 0.33σ for n1=5
    2. BICEP/Keck tensor ratio:    r_eff(n1,n2) < 0.036         ← 0.0315 for (5,7)
    3. CMB birefringence window:   β(k_cs) ∈ [0.22°, 0.38°]    ← 0.331° for k=74

Within the scan n_max=10 this leaves exactly TWO viable sectors:

    (5, 6)  k_cs=61, c_s≈0.180, r≈0.018, β≈0.273°  [shadow sector]
    (5, 7)  k_cs=74, c_s≈0.324, r≈0.032, β≈0.331°  [primary sector]

This module provides QUANTITATIVE BOUNDS on the uniqueness of the (5,7)
selection within this two-sector landscape:

  minimum_step_pairs:
      Among all viable pairs, (5,7) is the only one with n2 − n1 = 2
      (minimum step for adjacent odd-integer winding modes in the Z₂ orbifold).
      (5,6) has n2 − n1 = 1 (adjacent integers, not adjacent odds).

  cs_gap_between_viable_pairs:
      The sound-speed gap Δc_s = c_s(5,7) − c_s(5,6) ≈ 0.144 between the two
      viable sectors.  No other viable pair falls between them.

  birefringence_exclusivity:
      For β_measured ≈ 0.35° (Minami-Komatsu 2020), how many viable pairs
      land within n_sigma?  (5,7) at 0.331° is within 0.14°/σ of the
      measurement; (5,6) at 0.273° is 0.55σ away.

  triple_constraint_centrality:
      A combined metric M = ns_sigma × (r/r_limit) scores each pair.
      Lower M → more central.  Augmented with birefringence proximity.

  braid_uniqueness_audit:
      Complete quantitative summary of all four bounds.

Honest status
-------------
A field-theoretic proof that (5,7) is the unique stable braid pair from first
principles — without appeal to CMB observations — remains open.  See
FALLIBILITY.md §3.1 Admission 3.  The current module quantifies WHY (5,7) is
the preferred pair within the two-sector landscape, providing quantitative
bounds on the separation.

Public API
----------
minimum_step_pairs(n_max, ns_sigma_max, r_limit)
    Find viable pairs and classify by step size n2 − n1.

cs_gap_between_viable_pairs(n_max, ns_sigma_max, r_limit)
    Compute the c_s gap and separation statistics for viable sectors.

birefringence_exclusivity(beta_measured_deg, sigma_deg, n_max, ns_sigma_max, r_limit)
    Score each viable pair by proximity to a birefringence measurement.

triple_constraint_centrality(n_max, ns_sigma_max, r_limit)
    Combined (nₛ, r) centrality metric for each viable pair.

braid_uniqueness_audit(n_max)
    Complete quantitative audit of (5, 7) uniqueness bounds.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

import math
from typing import Dict, List, Optional

from src.core.braided_winding import (
    braided_ns_r,
    resonance_scan,
    BraidedPrediction,
)

# ---------------------------------------------------------------------------
# Framework constants
# ---------------------------------------------------------------------------

N_W: int = 5
N2_CANONICAL: int = 7
K_CS: int = 74           # = 5² + 7²
C_S_CANONICAL: float = 12.0 / 37.0   # ≈ 0.3243

PLANCK_NS: float = 0.9649
PLANCK_NS_SIGMA: float = 0.0042
R_BICEP_KECK: float = 0.036

#: Canonical birefringence predictions (degrees)
BETA_57_DEG: float = 0.331
BETA_56_DEG: float = 0.273

#: Minami-Komatsu 2020 birefringence hint
BETA_MK2020_DEG: float = 0.35
BETA_MK2020_SIGMA_DEG: float = 0.14

#: Birefringence formula: β ∝ k_cs (linear in the CS level at fixed geometry)
#: Calibrated to (5,7): β(74) = 0.331°
_BETA_SLOPE: float = BETA_57_DEG / K_CS


def _beta_from_k(k_cs: int) -> float:
    """Approximate birefringence angle [degrees] from CS level.

    Linear proportionality calibrated to (5,7): β(74) = 0.331°.
    This is the leading-order approximation; the full formula is in
    birefringence_scenario_scan() in braided_winding.py.
    """
    return _BETA_SLOPE * k_cs


# ---------------------------------------------------------------------------
# 1. Minimum-step pairs
# ---------------------------------------------------------------------------

def minimum_step_pairs(
    n_max: int = 10,
    ns_sigma_max: float = 2.0,
    r_limit: float = R_BICEP_KECK,
) -> Dict[str, object]:
    """Find viable pairs and classify by Z₂-orbifold parity and step size.

    In the S¹/Z₂ orbifold compactification, Z₂-parity-odd winding modes have
    both n1 and n2 odd (the Z₂ action sends φ → −φ, selecting odd-integer
    winding numbers).  Even-n2 pairs like (5,6) arise in the Z₂-even sector
    which is subdominant in the vacuum.

    Among ALL viable pairs (Planck nₛ + BICEP/Keck r), we classify:
      - z2_odd_pairs: both n1, n2 odd (genuine Z₂-orbifold modes)
      - z2_mixed_pairs: n2 even (Z₂-even sector)

    The minimum step in the Z₂-odd sector is n2 − n1 = 2 (adjacent odd
    integers).  (5, 7) is the only viable pair in this sector:
      - (5, 9) fails r < 0.036 (r≈0.051)
      - all smaller pairs fail the Planck nₛ constraint

    Parameters
    ----------
    n_max : int  Maximum winding number.
    ns_sigma_max : float  Planck nₛ acceptance window in σ.
    r_limit : float  BICEP/Keck r upper limit.

    Returns
    -------
    dict with keys:
        viable_pairs, z2_odd_pairs, z2_mixed_pairs,
        unique_z2_odd, z2_odd_pair, n_viable_total.
    """
    viable: List[BraidedPrediction] = resonance_scan(n_max, ns_sigma_max=ns_sigma_max, r_limit=r_limit)
    z2_odd = [p for p in viable if p.n1 % 2 == 1 and p.n2 % 2 == 1]
    z2_mixed = [p for p in viable if not (p.n1 % 2 == 1 and p.n2 % 2 == 1)]

    return {
        "viable_pairs": [(p.n1, p.n2) for p in viable],
        "z2_odd_pairs": [(p.n1, p.n2) for p in z2_odd],
        "z2_mixed_pairs": [(p.n1, p.n2) for p in z2_mixed],
        "unique_z2_odd": len(z2_odd) == 1,
        "z2_odd_pair": (z2_odd[0].n1, z2_odd[0].n2) if len(z2_odd) == 1 else None,
        "step_sizes_z2_odd": [p.n2 - p.n1 for p in z2_odd],
        "n_viable_total": len(viable),
        "n_z2_odd": len(z2_odd),
    }


# ---------------------------------------------------------------------------
# 2. c_s gap between viable pairs
# ---------------------------------------------------------------------------

def cs_gap_between_viable_pairs(
    n_max: int = 10,
    ns_sigma_max: float = 2.0,
    r_limit: float = R_BICEP_KECK,
) -> Dict[str, object]:
    """Compute the c_s gap and separation statistics for viable sectors.

    Two viable sectors exist at canonical constraints:
      (5, 6): c_s ≈ 0.180 (shadow)
      (5, 7): c_s ≈ 0.324 (primary)

    The gap Δc_s ≈ 0.144 means no viable sector sits between them.
    This quantifies how separated the two sectors are in sound-speed space.

    Parameters
    ----------
    n_max, ns_sigma_max, r_limit : scan parameters.

    Returns
    -------
    dict with keys:
        viable_pairs_sorted_by_cs, c_s_values, gaps,
        max_gap, total_range, n_viable.
    """
    viable: List[BraidedPrediction] = resonance_scan(n_max, ns_sigma_max=ns_sigma_max, r_limit=r_limit)
    viable.sort(key=lambda p: p.c_s)
    c_s_vals = [p.c_s for p in viable]
    gaps = [c_s_vals[i + 1] - c_s_vals[i] for i in range(len(c_s_vals) - 1)]

    return {
        "viable_pairs_sorted_by_cs": [(p.n1, p.n2) for p in viable],
        "c_s_values": c_s_vals,
        "gaps": gaps,
        "max_gap": max(gaps) if gaps else 0.0,
        "total_range": (max(c_s_vals) - min(c_s_vals)) if len(c_s_vals) >= 2 else 0.0,
        "n_viable": len(viable),
    }


# ---------------------------------------------------------------------------
# 3. Birefringence exclusivity
# ---------------------------------------------------------------------------

def birefringence_exclusivity(
    beta_measured_deg: float = BETA_MK2020_DEG,
    sigma_deg: float = BETA_MK2020_SIGMA_DEG,
    n_sigma: float = 1.0,
    n_max: int = 10,
    ns_sigma_max: float = 2.0,
    r_limit: float = R_BICEP_KECK,
) -> Dict[str, object]:
    """Score each viable pair by proximity to a birefringence measurement.

    For each viable (n1,n2) pair, compute its predicted β ≈ β_slope × k_cs
    and measure the distance |β_pred − β_measured| in units of sigma.

    Parameters
    ----------
    beta_measured_deg : float  Central birefringence measurement [degrees].
    sigma_deg : float  1σ uncertainty [degrees].
    n_sigma : float  Window size in σ.
    n_max, ns_sigma_max, r_limit : scan parameters.

    Returns
    -------
    dict with keys:
        beta_measured_deg, sigma_deg, window_lo, window_hi,
        pairs_with_beta, pairs_in_window, n_in_window,
        best_match_pair, best_match_distance_sigma.
    """
    window_lo = beta_measured_deg - n_sigma * sigma_deg
    window_hi = beta_measured_deg + n_sigma * sigma_deg

    viable: List[BraidedPrediction] = resonance_scan(n_max, ns_sigma_max=ns_sigma_max, r_limit=r_limit)

    pairs_with_beta = []
    in_window = []
    best_dist = float("inf")
    best_pair = None

    for p in viable:
        beta_pred = _beta_from_k(p.k_cs)
        dist_sigma = abs(beta_pred - beta_measured_deg) / sigma_deg
        entry = {
            "n1": p.n1, "n2": p.n2, "k_cs": p.k_cs,
            "c_s": p.c_s, "r_eff": p.r_eff,
            "beta_pred_deg": beta_pred,
            "distance_sigma": dist_sigma,
            "in_window": bool(window_lo <= beta_pred <= window_hi),
        }
        pairs_with_beta.append(entry)
        if entry["in_window"]:
            in_window.append(entry)
        if dist_sigma < best_dist:
            best_dist = dist_sigma
            best_pair = (p.n1, p.n2)

    return {
        "beta_measured_deg": beta_measured_deg,
        "sigma_deg": sigma_deg,
        "n_sigma": n_sigma,
        "window_lo": window_lo,
        "window_hi": window_hi,
        "pairs_with_beta": pairs_with_beta,
        "pairs_in_window": in_window,
        "n_in_window": len(in_window),
        "exclusive": len(in_window) <= 1,
        "best_match_pair": best_pair,
        "best_match_distance_sigma": best_dist,
    }


# ---------------------------------------------------------------------------
# 4. Triple-constraint centrality
# ---------------------------------------------------------------------------

def triple_constraint_centrality(
    n_max: int = 10,
    ns_sigma_max: float = 2.0,
    r_limit: float = R_BICEP_KECK,
    beta_ref_deg: float = BETA_MK2020_DEG,
    sigma_beta_deg: float = BETA_MK2020_SIGMA_DEG,
) -> Dict[str, object]:
    """Combined (nₛ, r, β) centrality metric for each viable pair.

    The centrality metric combines all three constraint dimensions:

        M(n1,n2) = ns_sigma(n1) × (r_eff / r_limit) × (|β_pred − β_ref| / σ_β)

    Lower M → more central in the 3D constraint cube.
    The pair with smallest M is most empirically preferred.

    For (5,7): ns_sigma=0.33, r=0.031/0.036=0.875, |0.331-0.35|/0.14=0.136 → M≈0.039
    For (5,6): ns_sigma=0.33, r=0.018/0.036=0.486, |0.273-0.35|/0.14=0.550 → M≈0.088

    (5,7) has the smaller M, making it more central in all three dimensions
    simultaneously.

    Parameters
    ----------
    n_max, ns_sigma_max, r_limit : scan parameters.
    beta_ref_deg, sigma_beta_deg : birefringence reference.

    Returns
    -------
    dict with keys:
        viable_pairs, centrality_scores, most_central_pair,
        most_central_n1, most_central_n2, minimum_M.
    """
    viable: List[BraidedPrediction] = resonance_scan(n_max, ns_sigma_max=ns_sigma_max, r_limit=r_limit)

    scored = []
    for p in viable:
        beta_pred = _beta_from_k(p.k_cs)
        beta_dist = abs(beta_pred - beta_ref_deg) / sigma_beta_deg
        M = p.ns_sigma * (p.r_eff / r_limit) * (beta_dist + 0.01)  # +0.01 avoids M=0 artificially
        scored.append({
            "n1": p.n1, "n2": p.n2, "k_cs": p.k_cs,
            "ns_sigma": p.ns_sigma, "r_eff": p.r_eff, "c_s": p.c_s,
            "beta_pred_deg": beta_pred,
            "beta_distance_sigma": beta_dist,
            "centrality_M": M,
        })
    scored.sort(key=lambda s: s["centrality_M"])

    return {
        "viable_pairs": [(s["n1"], s["n2"]) for s in scored],
        "centrality_scores": scored,
        "most_central_pair": (scored[0]["n1"], scored[0]["n2"]) if scored else None,
        "most_central_n1": scored[0]["n1"] if scored else None,
        "most_central_n2": scored[0]["n2"] if scored else None,
        "minimum_M": scored[0]["centrality_M"] if scored else None,
        "n_viable": len(scored),
    }


# ---------------------------------------------------------------------------
# 5. Braid uniqueness audit
# ---------------------------------------------------------------------------

def braid_uniqueness_audit(n_max: int = 10) -> Dict[str, object]:
    """Complete quantitative audit of (5, 7) braid uniqueness bounds.

    Combines all four analyses and summarises the key bounds that
    justify the empirical preference for (5, 7) within the two-sector
    landscape.

    Parameters
    ----------
    n_max : int  Maximum winding number for all scans.

    Returns
    -------
    dict
    """
    msp = minimum_step_pairs(n_max)
    csg = cs_gap_between_viable_pairs(n_max)
    bex = birefringence_exclusivity(n_max=n_max)
    tcc = triple_constraint_centrality(n_max)

    return {
        "title": "Braid Uniqueness Audit — Pillar 95-B",
        "status": "QUANTITATIVE BOUNDS ESTABLISHED — field-theoretic proof partially open",
        "canonical_pair": {"n1": N_W, "n2": N2_CANONICAL, "k_cs": K_CS, "c_s": C_S_CANONICAL},
        "viable_sectors": {
            "n_viable": msp["n_viable_total"],
            "pairs": msp["viable_pairs"],
        },
        "minimum_step_analysis": {
            "n_z2_odd_pairs": msp["n_z2_odd"],
            "unique_z2_odd_pair": msp["unique_z2_odd"],
            "z2_odd_pair": msp["z2_odd_pair"],
            "all_viable_pairs": msp["viable_pairs"],
        },
        "sound_speed_gap": {
            "c_s_values": csg["c_s_values"],
            "gaps": csg["gaps"],
            "max_gap": csg["max_gap"],
            "total_range": csg["total_range"],
        },
        "birefringence_exclusivity": {
            "beta_measured_deg": bex["beta_measured_deg"],
            "best_match_pair": bex["best_match_pair"],
            "best_match_distance_sigma": bex["best_match_distance_sigma"],
            "n_pairs_in_1sigma": bex["n_in_window"],
        },
        "triple_constraint": {
            "most_central_pair": tcc["most_central_pair"],
            "minimum_M": tcc["minimum_M"],
        },
        "open_gap": (
            "A field-theoretic proof that (5,7) is the unique stable braid pair "
            "from first principles — without appeal to CMB observations — remains open. "
            "The minimum-step and centrality arguments establish empirical uniqueness "
            "within the scan range.  See FALLIBILITY.md §3.1 Admission 3."
        ),
        "pillar": "95-B (extends Pillar 95 / Pillar 74 Completeness Theorem)",
        "closes": "Braid uniqueness bounds gap documented in FALLIBILITY.md §3.1",
    }
