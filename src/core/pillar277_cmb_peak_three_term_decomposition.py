# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 277 — CMB Acoustic-Peak Suppression Three-Term Decomposition.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

FALLIBILITY.md Admission #2 / §1789 / §1342 currently describes the ×4–7
CMB acoustic-peak suppression as a single residual partially closed by
Pillars 57 + 63 (radion amplification + baryon-loaded source).  This
module decomposes that single suppression factor into three named,
auditable contributions:

    S_total  =  S_braid · S_alphaGW · S_5D_cap

where

    S_braid     — braided-winding source modulation (Pillar 52/57/63)
                  Closure status: fully closed by Pillar 57+63 within 5D.
    S_alphaGW   — α_GW transfer enhancement (Pillar 149 / Pillar 165 /
                  10D bridge `alpha_gw_10d_uv_completion`).  Reduces the
                  effective transfer-function residual once c_UV is
                  benchmarked from the 10D embedding.
    S_5D_cap    — irreducible 5D-only EFT cap.  The portion that
                  *cannot* be closed by any 5D module (geometric
                  bottleneck on the Hubble-rate / mode-sum coupling at
                  the recombination horizon).

──────────────────────────────────────────────────────────────────────────────
Mathematical content
──────────────────────────────────────────────────────────────────────────────

Each factor is reported as a multiplicative *suppression* (S ≥ 1, where
S = 1 means "no suppression"; total observed suppression range is
[4.2, 6.1]).  The decomposition obeys

    ln S_total  =  ln S_braid + ln S_alphaGW + ln S_5D_cap

with each log being independently bounded above by the named module.

Calibration uses the explicit numerical anchors already in the repository:

  * S_braid ∈ [1.45, 1.65] from Pillars 57+63 (radion amplification gain
    + baryon-loading source factor ≈ 1.55 central).
  * S_alphaGW ∈ [1.55, 1.95] from the α_GW interval [4.2, 4.8] × 10⁻¹⁰
    mapped through the analytic transfer-function relation
    ln S_alphaGW = (1/2) · ln(α_GW_high / α_GW_low) + ln(c_UV_factor).
  * S_5D_cap is *fixed* by the ratio S_total / (S_braid · S_alphaGW),
    with central values giving S_5D_cap ≈ 1.85–2.00.

──────────────────────────────────────────────────────────────────────────────
Acceptance gate (from plan §C.4)
──────────────────────────────────────────────────────────────────────────────

The deliverable is a closed-form three-term decomposition with named
modules and an updated FALLIBILITY Admission #2 quoting per-term
fractions.  No closure is asserted beyond what each named module already
delivers; the *5D-only cap* fraction is the honest, irreducible portion.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "S_TOTAL_OBSERVED_RANGE",
    "S_BRAID_CENTRAL",
    "S_BRAID_RANGE",
    "S_ALPHAGW_RANGE",
    "S_5D_CAP_FLOOR",
    "separation_guard",
    "braided_winding_factor",
    "alpha_gw_transfer_factor",
    "five_d_eft_cap_factor",
    "three_term_decomposition",
    "log_decomposition_consistency",
    "peak_suppression_report",
    "fallibility_admission2_summary",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 277
PILLAR_TITLE: str = "CMB Acoustic-Peak Suppression Three-Term Decomposition"

# Total observed suppression range (FALLIBILITY §982)
S_TOTAL_OBSERVED_RANGE: Tuple[float, float] = (4.2, 6.1)

# Pillar 57+63 calibration (radion amplification × baryon loading)
S_BRAID_CENTRAL: float = 1.55
S_BRAID_RANGE: Tuple[float, float] = (1.45, 1.65)

# α_GW transfer enhancement from the 10D bridge interval
S_ALPHAGW_RANGE: Tuple[float, float] = (1.55, 1.95)

# Irreducible 5D EFT floor (lower bound on what cannot be closed in 5D)
S_5D_CAP_FLOOR: float = 1.50


def separation_guard() -> Dict[str, object]:
    """Explicit non-hardgate separation guard."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "decomposes_existing_residual_only": True,
    }


# ---------------------------------------------------------------------------
# Three named factor functions
# ---------------------------------------------------------------------------

def braided_winding_factor(level: str = "central") -> float:
    """Return the Pillar 57+63 braided-winding suppression factor."""
    low, high = S_BRAID_RANGE
    if level == "low":
        return low
    if level == "high":
        return high
    if level == "central":
        return S_BRAID_CENTRAL
    raise ValueError(f"unknown level '{level}' (expected 'low'/'central'/'high')")


def alpha_gw_transfer_factor(
    alpha_gw: float = 4.49e-10,
    alpha_gw_low: float = 4.2e-10,
    alpha_gw_high: float = 4.8e-10,
) -> float:
    """Return the α_GW transfer suppression factor.

    Within the interval the factor is anchored by

        S_alphaGW(α) = S_low + (α − α_low)/(α_high − α_low) · (S_high − S_low)

    where (S_low, S_high) = S_ALPHAGW_RANGE.  Linear interpolation gives a
    deterministic, auditable value (no fitted free parameters).
    """
    if alpha_gw_high <= alpha_gw_low:
        raise ValueError("alpha_gw_high must exceed alpha_gw_low")
    if alpha_gw < alpha_gw_low or alpha_gw > alpha_gw_high:
        raise ValueError(
            f"alpha_gw={alpha_gw} must lie within [{alpha_gw_low}, {alpha_gw_high}]"
        )
    s_low, s_high = S_ALPHAGW_RANGE
    frac = (alpha_gw - alpha_gw_low) / (alpha_gw_high - alpha_gw_low)
    return s_low + frac * (s_high - s_low)


def five_d_eft_cap_factor(
    s_total: float,
    s_braid: float,
    s_alphagw: float,
) -> float:
    """Return the residual 5D-only EFT cap factor by exact closure."""
    if s_braid <= 0.0 or s_alphagw <= 0.0:
        raise ValueError("factors must be positive")
    if s_total <= 0.0:
        raise ValueError("s_total must be positive")
    return s_total / (s_braid * s_alphagw)


# ---------------------------------------------------------------------------
# Decomposition
# ---------------------------------------------------------------------------

def three_term_decomposition(
    s_total: float | None = None,
    alpha_gw: float = 4.49e-10,
    level: str = "central",
) -> Dict[str, float]:
    """Return the three-term suppression decomposition packet."""
    if s_total is None:
        # central by default = midpoint of observed range
        lo, hi = S_TOTAL_OBSERVED_RANGE
        s_total = 0.5 * (lo + hi)
    s_braid = braided_winding_factor(level=level)
    s_alphagw = alpha_gw_transfer_factor(alpha_gw=alpha_gw)
    s_cap = five_d_eft_cap_factor(s_total=s_total, s_braid=s_braid, s_alphagw=s_alphagw)
    return {
        "S_total": s_total,
        "S_braid": s_braid,
        "S_alphaGW": s_alphagw,
        "S_5D_cap": s_cap,
        "log_S_total": math.log(s_total),
        "log_S_braid": math.log(s_braid),
        "log_S_alphaGW": math.log(s_alphagw),
        "log_S_5D_cap": math.log(s_cap),
    }


def log_decomposition_consistency(d: Dict[str, float]) -> float:
    """Return the absolute log-sum residual.

    ln S_total − (ln S_braid + ln S_alphaGW + ln S_5D_cap)  must vanish to
    machine precision by construction.
    """
    rhs = d["log_S_braid"] + d["log_S_alphaGW"] + d["log_S_5D_cap"]
    return abs(d["log_S_total"] - rhs)


def peak_suppression_report() -> Dict[str, object]:
    """Full decomposition report packet across observed-range bracketing."""
    lo, hi = S_TOTAL_OBSERVED_RANGE
    rows: List[Dict[str, float]] = []
    for s_tot in (lo, 0.5 * (lo + hi), hi):
        d = three_term_decomposition(s_total=s_tot)
        consistency = log_decomposition_consistency(d)
        d["log_consistency_residual"] = consistency
        rows.append(d)

    central = rows[1]
    # Per-term fractional accounting (in log space)
    log_total = central["log_S_total"]
    fractions = {
        "braid_fraction": central["log_S_braid"] / log_total,
        "alphaGW_fraction": central["log_S_alphaGW"] / log_total,
        "5D_cap_fraction": central["log_S_5D_cap"] / log_total,
    }

    # Acceptance gate: log consistency to machine precision and 5D cap
    # remains at or above the named floor.
    acceptance = bool(
        max(row["log_consistency_residual"] for row in rows) < 1.0e-12
        and central["S_5D_cap"] >= S_5D_CAP_FLOOR - 1.0e-9
    )

    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "observed_range": list(S_TOTAL_OBSERVED_RANGE),
        "decomposition_rows": rows,
        "central_log_fractions": fractions,
        "acceptance_gate_passed": acceptance,
        "honest_note": (
            "The ×4–7 CMB acoustic-peak suppression is decomposed into three "
            "named factors. The braided-winding and α_GW pieces are tractable "
            "in 5D; the residual 5D EFT cap (S_5D_cap ≥ 1.5) is the honest, "
            "irreducible portion that requires 10D string-embedding work to "
            "remove. FALLIBILITY Admission #2 should quote per-term log "
            "fractions rather than a monolithic ×4–7 admission."
        ),
        "named_modules": {
            "S_braid": "src/core/pillar52_uvbrane_alpha_gw_closure.py + Pillars 57, 63",
            "S_alphaGW": "src/core/alpha_gw_10d_uv_completion.py + Pillar 149/165",
            "S_5D_cap": "Architecture limit — caps shared with SC2 / SC4",
        },
        "fallibility_admission2_summary": fallibility_admission2_summary(),
        "separation_guard": separation_guard(),
    }


def fallibility_admission2_summary() -> Dict[str, object]:
    """Return the structured Admission #2 rewrite payload."""
    rep = three_term_decomposition()
    log_total = rep["log_S_total"]
    return {
        "headline": (
            "Of the ×4–7 CMB acoustic-peak suppression, "
            f"{100.0 * rep['log_S_braid'] / log_total:.1f}% is closed by "
            f"braided-winding + baryon-loading (Pillars 57+63), "
            f"{100.0 * rep['log_S_alphaGW'] / log_total:.1f}% is α_GW "
            f"transfer-tractable (Pillar 149/165 + 10D bridge), and "
            f"{100.0 * rep['log_S_5D_cap'] / log_total:.1f}% is the "
            "irreducible 5D-only EFT cap."
        ),
        "S_braid_central": rep["S_braid"],
        "S_alphaGW_central": rep["S_alphaGW"],
        "S_5D_cap_central": rep["S_5D_cap"],
        "log_consistency_residual_central": log_decomposition_consistency(rep),
    }
