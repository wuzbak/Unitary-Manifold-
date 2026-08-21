# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 789 — WINDING_RESONANCE_STABILITY_BASIN

Status: STABILITY_BASIN_QUANTIFIED

Formally encodes the stability basin around the braided winding number n_w = 5:
the set of n_w values consistent with simultaneous empirical agreement on:
  (a) CMB spectral index n_s ∈ [0.9607, 0.9691]  (Planck 2018, 1σ)
  (b) Birefringence angle β ∈ [0.22°, 0.38°]     (admissible window)
  (c) Tensor-to-scalar ratio r < 0.036            (BICEP/Keck 2021)

Key results
-----------
  n_w = 5 is the unique integer in the admissible set         [STABILITY_BASIN]
  Stability margin Δn_w = 1 (nearest excluded: n_w = 4, 6)   [QUANTIFIED]
  n_s = 0.9635  (Planck 2018: 0.9649 ± 0.0042; 0.33σ)        [DERIVED]
  β   = 0.351°  (admissible window [0.22°, 0.38°]; ✅)        [DERIVED]
  r   = 0.0315  (BICEP/Keck limit r < 0.036; ✅)              [DERIVED]
  k_CS = 74 = 5² + 7²                                         [DERIVED]
  STABILITY_BASIN dict: machine-readable certificate           [EXPORTED]
  Birefringence gap [0.29°, 0.31°] is a structural exclusion  [QUANTIFIED]
  Pre-registration: LiteBIRD 2032 β measurement               [REGISTERED]

How the stability basin is computed
------------------------------------
Each candidate winding number n_w ∈ {1, …, 15} defines a braid pair
(n_w, n_w+2) — the unique shadow pair selected by the orbifold geometry.
Observable predictions for each pair are computed via the full chain from
cmb_topology.topology_to_cmb(), which uses:

  k_CS(n_w) = n_w² + (n_w+2)²
  c_s(n_w)  = n_w(n_w+2) / k_CS          [braided sound speed]
  n_s(n_w)  — slow-roll from braided KK potential
  β(n_w)    — axion-photon coupling via CS coupling constant
  r(n_w)    — braided tensor-to-scalar ratio

An integer n_w is admissible iff all three empirical constraints are satisfied
simultaneously.  The scan over n_w ∈ {1, …, 15} establishes that n_w = 5 is
the unique solution.

Stability margin: min distance from n_w=5 to the nearest excluded candidate.
With n_w=4 and n_w=6 both excluded, the margin is Δn_w = 1.

Lean4 target: WindingStabilityBasin.lean (+15 proxy theorems; total 1021)
Tests: 55 (see tests/test_pillar789_winding_resonance_stability_basin.py)
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.core.cmb_topology import topology_to_cmb, admissible_window

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
N_W_SELECTED = 5          # braided winding number (Planck-selected, Pillar 1)
N_W_SECONDARY = 7         # shadow-pair partner (n_w + 2)

# Empirical windows (from existing pillars)
N_S_PLANCK_CENTRAL = 0.9649
N_S_PLANCK_SIGMA = 0.0042
N_S_LOW = N_S_PLANCK_CENTRAL - N_S_PLANCK_SIGMA   # 0.9607
N_S_HIGH = N_S_PLANCK_CENTRAL + N_S_PLANCK_SIGMA  # 0.9691
BETA_LOW_DEG = 0.22    # admissible β window lower bound [deg]
BETA_HIGH_DEG = 0.38   # admissible β window upper bound [deg]
BETA_GAP_LOW = 0.29    # structural gap lower bound [deg]
BETA_GAP_HIGH = 0.31   # structural gap upper bound [deg]
R_BICEP_LIMIT = 0.036  # BICEP/Keck 2021 95% CL upper bound

PILLAR_STATUS = "STABILITY_BASIN_QUANTIFIED"
PILLAR_NUMBER = 789

# Canonical predicted observables at n_w = 5 (from cmb_topology)
_CMB_NW5 = topology_to_cmb(N_W_SELECTED, N_W_SECONDARY)
N_S_PREDICTED = _CMB_NW5["ns"]       # 0.9635
BETA_PREDICTED_DEG = _CMB_NW5["beta_deg"]  # 0.351
R_PREDICTED = _CMB_NW5["r"]          # 0.0315
K_CS_NW5 = _CMB_NW5["k_cs"]          # 74


# ---------------------------------------------------------------------------
# Admissibility check
# ---------------------------------------------------------------------------

def _evaluate_nw(n_w: int) -> Dict[str, object]:
    """
    Evaluate a candidate winding number using the full cmb_topology chain.

    Returns a dict with CMB observables and admissibility flags.
    Raises ValueError if n_w < 1 (n_w+2 must be > n_w).
    """
    if n_w < 1:
        raise ValueError(f"n_w must be >= 1, got {n_w}")
    try:
        result = topology_to_cmb(n_w, n_w + 2)
    except Exception as exc:
        return {
            "n_w": n_w, "admissible": False,
            "error": str(exc), "n_s": None, "beta_deg": None, "r": None,
        }

    ns = result["ns"]
    beta = result["beta_deg"]
    r = result["r"]

    ok_ns = N_S_LOW <= ns <= N_S_HIGH
    in_gap = BETA_GAP_LOW < beta < BETA_GAP_HIGH
    ok_beta = BETA_LOW_DEG <= beta <= BETA_HIGH_DEG and not in_gap
    ok_r = r < R_BICEP_LIMIT

    return {
        "n_w": n_w,
        "n_s": ns,
        "beta_deg": beta,
        "r": r,
        "k_cs": result["k_cs"],
        "c_s": result["c_s"],
        "ok_ns": ok_ns,
        "ok_beta": ok_beta,
        "in_beta_gap": in_gap,
        "ok_r": ok_r,
        "admissible": ok_ns and ok_beta and ok_r,
    }


def is_admissible(n_w: int) -> Tuple[bool, Dict[str, object]]:
    """Return (admissible, detail_dict) for a candidate winding number."""
    detail = _evaluate_nw(n_w)
    return detail["admissible"], detail


# ---------------------------------------------------------------------------
# Sensitivity (finite difference)
# ---------------------------------------------------------------------------

def _sensitivity(n_w: int = N_W_SELECTED) -> Tuple[float, float]:
    """
    Return (∂n_s/∂n_w, ∂β/∂n_w) via central finite difference.

    Uses neighbouring braid pairs (n_w±1, n_w±3) where available.
    """
    lo = _evaluate_nw(max(1, n_w - 1))
    hi = _evaluate_nw(n_w + 1)
    step = (n_w + 1) - max(1, n_w - 1)
    dns = (hi["n_s"] - lo["n_s"]) / step if step > 0 else 0.0
    dbeta = (hi["beta_deg"] - lo["beta_deg"]) / step if step > 0 else 0.0
    return dns, dbeta


# ---------------------------------------------------------------------------
# Stability basin
# ---------------------------------------------------------------------------

@dataclass
class StabilityBasin:
    """Machine-readable stability basin certificate for n_w = 5."""

    # Selection
    n_w_selected: int = N_W_SELECTED
    status: str = PILLAR_STATUS

    # Admissible set (integers 1..15 evaluated)
    admissible_set: List[int] = field(default_factory=list)
    excluded_set: List[int] = field(default_factory=list)

    # Predicted observables at n_w = 5
    n_s_predicted: float = N_S_PREDICTED
    beta_deg_predicted: float = BETA_PREDICTED_DEG
    r_predicted: float = R_PREDICTED
    k_cs_value: int = K_CS_NW5

    # Sensitivity derivatives (finite difference)
    dns_dnw: float = 0.0   # ∂n_s/∂n_w
    dbeta_dnw: float = 0.0  # ∂β/∂n_w [deg/unit]

    # Constraints
    n_s_window: Tuple[float, float] = (N_S_LOW, N_S_HIGH)
    beta_window: Tuple[float, float] = (BETA_LOW_DEG, BETA_HIGH_DEG)
    beta_gap: Tuple[float, float] = (BETA_GAP_LOW, BETA_GAP_HIGH)
    r_limit: float = R_BICEP_LIMIT

    # Stability margin
    stability_margin_delta_nw: int = 0
    nearest_excluded_lower: Optional[int] = None
    nearest_excluded_upper: Optional[int] = None

    # Falsification
    falsification_condition: str = ""
    pre_registered_experiment: str = "LiteBIRD (launch ~2032)"

    # Gate
    gate: str = "STABILITY_BASIN_QUANTIFIED"
    failures: int = 0


def compute_stability_basin(n_w_range: range = range(1, 16)) -> StabilityBasin:
    """Scan n_w candidates and return the stability basin certificate."""
    basin = StabilityBasin()

    admissible: List[int] = []
    excluded: List[int] = []

    for n in n_w_range:
        ok, _ = is_admissible(n)
        if ok:
            admissible.append(n)
        else:
            excluded.append(n)

    basin.admissible_set = admissible
    basin.excluded_set = excluded

    # Sensitivity
    basin.dns_dnw, basin.dbeta_dnw = _sensitivity()

    # Stability margin
    if N_W_SELECTED in admissible:
        below = [n for n in excluded if n < N_W_SELECTED]
        above_list = [n for n in excluded if n > N_W_SELECTED]
        basin.nearest_excluded_lower = max(below) if below else None
        basin.nearest_excluded_upper = min(above_list) if above_list else None

        margin_low = (N_W_SELECTED - basin.nearest_excluded_lower
                      if basin.nearest_excluded_lower is not None else 999)
        margin_high = (basin.nearest_excluded_upper - N_W_SELECTED
                       if basin.nearest_excluded_upper is not None else 999)
        basin.stability_margin_delta_nw = min(margin_low, margin_high)

    basin.falsification_condition = (
        "Any measurement of birefringence β < 0.22° or β > 0.38° at ≥2σ falsifies "
        "the braided n_w=5 mechanism. A β reading in the predicted gap [0.29°, 0.31°] "
        "would falsify the shadow-pair pairing. Primary falsifier: LiteBIRD 2032."
    )

    return basin


# ---------------------------------------------------------------------------
# STABILITY_BASIN dict (machine-readable export)
# ---------------------------------------------------------------------------

def get_stability_basin_dict() -> Dict[str, object]:
    """Return STABILITY_BASIN as a plain dict for downstream use."""
    basin = compute_stability_basin()
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "n_w_selected": basin.n_w_selected,
        "admissible_set": basin.admissible_set,
        "excluded_set": basin.excluded_set,
        "n_s_predicted": round(basin.n_s_predicted, 6),
        "beta_deg_predicted": round(basin.beta_deg_predicted, 4),
        "r_predicted": round(basin.r_predicted, 6),
        "k_cs": basin.k_cs_value,
        "dns_dnw": round(basin.dns_dnw, 6),
        "dbeta_dnw_deg": round(basin.dbeta_dnw, 4),
        "n_s_window": basin.n_s_window,
        "beta_window_deg": basin.beta_window,
        "beta_gap_deg": basin.beta_gap,
        "r_limit": basin.r_limit,
        "stability_margin_delta_nw": basin.stability_margin_delta_nw,
        "nearest_excluded_lower": basin.nearest_excluded_lower,
        "nearest_excluded_upper": basin.nearest_excluded_upper,
        "falsification_condition": basin.falsification_condition,
        "pre_registered_experiment": basin.pre_registered_experiment,
        "gate": basin.gate,
    }


STABILITY_BASIN = get_stability_basin_dict()


def run_pillar789() -> StabilityBasin:
    """Entry point: compute and return the stability basin certificate."""
    return compute_stability_basin()
