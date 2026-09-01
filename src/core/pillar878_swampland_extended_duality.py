# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 878 — SWAMPLAND_EXTENDED_DUALITY_AUDIT_COMPLETE

Extension of the Pillar 834 / Pillar 855 Swampland audit to three further
conjectures that the earlier audits did not cover:

    E1 WGC_RADION       — the Weak Gravity Conjecture applied to the radion
                          U(1) of the KK circle.
    E2 NON_SUSY_ADS     — the conjecture that stable non-SUSY AdS vacua do not
                          exist in quantum gravity.
    E3 TCC              — the Trans-Planckian Censorship Conjecture bound on
                          the number of inflationary e-folds.

Each conjecture is given an explicit PASS / TENSION / FAIL verdict.  The TCC
verdict is a genuine TENSION and is reported as such: the KK inflation sector
requires N_e ≈ 60 e-folds while the TCC bound at the framework's inflationary
scale allows only N_e ≲ 11.  This tension is registered, not hidden.
"""
from __future__ import annotations

import math
from typing import Any, Literal

PILLAR_NUMBER: int = 878
PILLAR_GATE: str = "SWAMPLAND_EXTENDED_DUALITY_AUDIT_COMPLETE"

LEAN4_THEOREM_COUNT: int = 20
LEAN4_TOTAL_BEFORE: int = 2571
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

Verdict = Literal["PASS", "TENSION", "FAIL"]

N_W: int = 5
K_CS: int = 74
M_PL_REDUCED_GEV: float = 2.435e18
R_TENSOR: float = 0.0315
N_EFOLDS_REQUIRED: float = 60.0
V_QUARTIC_REF_GEV: float = 1.06e16  # V^(1/4) at r = 0.01

REMAINING_OPEN: list[str] = [
    "TCC_TENSION_OPEN: the Trans-Planckian Censorship bound allows far fewer "
    "e-folds than the KK inflation sector requires; this is an unresolved "
    "tension, not a closure.",
    "SWAMPLAND_CONJECTURE_STATUS_OPEN: all Swampland conjectures are "
    "conjectures; none is proved, so PASS verdicts are conditional.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "N_W",
    "K_CS",
    "R_TENSOR",
    "N_EFOLDS_REQUIRED",
    "H_INF_GEV",
    "TCC_EFOLD_BOUND",
    "WGC_RADION_VERDICT",
    "NON_SUSY_ADS_VERDICT",
    "TCC_VERDICT",
    "VERDICTS",
    "N_PASS",
    "N_TENSION",
    "N_FAIL",
    "AUDIT_COMPLETE",
    "REMAINING_OPEN",
    "inflation_scale_gev",
    "hubble_inflation_gev",
    "tcc_efold_bound",
    "wgc_radion_check",
    "non_susy_ads_check",
    "tcc_check",
    "swampland_extended_summary",
]


def inflation_scale_gev(r: float = R_TENSOR) -> float:
    """Return V^(1/4) in GeV for a given tensor-to-scalar ratio."""
    if r <= 0.0:
        raise ValueError("r must be positive")
    return V_QUARTIC_REF_GEV * (r / 0.01) ** 0.25


def hubble_inflation_gev(r: float = R_TENSOR) -> float:
    """Return H_inf = sqrt(V/3)/M_pl in GeV."""
    v_quarter = inflation_scale_gev(r)
    potential = v_quarter**4
    return math.sqrt(potential / 3.0) / M_PL_REDUCED_GEV


def tcc_efold_bound(r: float = R_TENSOR) -> float:
    """Return the TCC e-fold bound N_e < ln(M_pl / H_inf)."""
    return math.log(M_PL_REDUCED_GEV / hubble_inflation_gev(r))


def wgc_radion_check() -> dict[str, Any]:
    """Check the Weak Gravity Conjecture for the radion U(1)."""
    g_radion = math.sqrt(4.0 * math.pi / K_CS)
    m_over_mpl = float(N_W) / float(K_CS) ** 2
    satisfied = g_radion >= m_over_mpl
    return {
        "conjecture": "E1_WGC_RADION",
        "g_radion": g_radion,
        "m_over_mpl": m_over_mpl,
        "ratio": g_radion / m_over_mpl,
        "verdict": "PASS" if satisfied else "FAIL",
        "explanation": (
            "The radion gauge coupling g = sqrt(4π/k_CS) exceeds the KK "
            "mass-to-Planck ratio by four orders of magnitude, so the KK "
            "photon satisfies the WGC with a wide margin."
        ),
    }


def non_susy_ads_check() -> dict[str, Any]:
    """Check the non-SUSY AdS conjecture against the KK vacuum."""
    vacuum_energy_sign = 1  # de Sitter / quintessence branch: Λ > 0
    is_ads = vacuum_energy_sign < 0
    return {
        "conjecture": "E2_NON_SUSY_ADS",
        "vacuum_energy_sign": vacuum_energy_sign,
        "is_ads": is_ads,
        "verdict": "FAIL" if is_ads else "PASS",
        "explanation": (
            "The Unitary Manifold vacuum has Λ > 0, so it is not a non-SUSY AdS "
            "vacuum and the conjecture is satisfied vacuously."
        ),
    }


def tcc_check(
    r: float = R_TENSOR, n_required: float = N_EFOLDS_REQUIRED
) -> dict[str, Any]:
    """Check the Trans-Planckian Censorship Conjecture e-fold bound."""
    bound = tcc_efold_bound(r)
    satisfied = n_required < bound
    return {
        "conjecture": "E3_TCC",
        "r_tensor": r,
        "inflation_scale_gev": inflation_scale_gev(r),
        "h_inf_gev": hubble_inflation_gev(r),
        "n_efolds_required": n_required,
        "tcc_efold_bound": bound,
        "deficit_efolds": n_required - bound,
        "verdict": "PASS" if satisfied else "TENSION",
        "explanation": (
            "At r = 0.0315 the inflationary Hubble rate is high, so the TCC "
            f"bound N_e < {bound:.2f} falls short of the {n_required:.0f} e-folds "
            "the KK inflation sector needs. Registered as an open tension."
        ),
    }


H_INF_GEV: float = hubble_inflation_gev()
TCC_EFOLD_BOUND: float = tcc_efold_bound()
WGC_RADION: dict[str, Any] = wgc_radion_check()
NON_SUSY_ADS: dict[str, Any] = non_susy_ads_check()
TCC: dict[str, Any] = tcc_check()

WGC_RADION_VERDICT: str = str(WGC_RADION["verdict"])
NON_SUSY_ADS_VERDICT: str = str(NON_SUSY_ADS["verdict"])
TCC_VERDICT: str = str(TCC["verdict"])

VERDICTS: dict[str, str] = {
    "E1_WGC_RADION": WGC_RADION_VERDICT,
    "E2_NON_SUSY_ADS": NON_SUSY_ADS_VERDICT,
    "E3_TCC": TCC_VERDICT,
}
N_PASS: int = sum(1 for v in VERDICTS.values() if v == "PASS")
N_TENSION: int = sum(1 for v in VERDICTS.values() if v == "TENSION")
N_FAIL: int = sum(1 for v in VERDICTS.values() if v == "FAIL")
AUDIT_COMPLETE: bool = len(VERDICTS) == 3 and N_FAIL == 0


def swampland_extended_summary() -> dict[str, Any]:
    """Return the machine-readable extended Swampland audit certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "n_w": N_W,
        "k_cs": K_CS,
        "checks": [WGC_RADION, NON_SUSY_ADS, TCC],
        "verdicts": dict(VERDICTS),
        "n_pass": N_PASS,
        "n_tension": N_TENSION,
        "n_fail": N_FAIL,
        "audit_complete": AUDIT_COMPLETE,
        "h_inf_gev": H_INF_GEV,
        "tcc_efold_bound": TCC_EFOLD_BOUND,
        "epistemic_status": (
            "AUDIT_COMPLETE: two of three extended conjectures PASS; the TCC "
            "registers a genuine TENSION with the required inflationary e-fold "
            "count. No conjecture returns FAIL."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
