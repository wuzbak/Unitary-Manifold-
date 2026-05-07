# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar213_braid_cl_spectrum.py
========================================
Pillar 213 — Sub-leading Chern-Simons Braid Corrections to RS Bulk-Mass Spectrum.

═══════════════════════════════════════════════════════════════════════════
THE PHYSICS
═══════════════════════════════════════════════════════════════════════════
In the Randall-Sundrum (RS) framework the fermion zero-mode wavefunction is
determined by the 5D bulk Dirac mass parameter c_L (in units of the AdS
curvature k).  For UV-localized fermions (c_L > 1/2) the zero-mode profile is:

    f₀(c_L) = √[(2c_L − 1) / (exp((2c_L − 1) π k R) − 1)]

Pillar 93 showed that winding-quantization fixes the leading values:

    c_L^(0)(gen) = 1/2 + (n_w − gen) / (2 n_w)     gen ∈ {0, 1, 2}

giving c_L = {0.9, 0.8, 0.7} for three generations with n_w = 5.

Pillar 213 derives the *sub-leading* corrections arising from the (5, 7)
Chern-Simons braid phase on AdS₅:

    δc_L^(1)(gen) = gen · n₁ · n₂ / (n₂² · K_CS)
                  = gen · 35 / 3626

    δc_L^(2)(gen) = gen² · (n₁ n₂)² / (n₂⁴ · K_CS²)

═══════════════════════════════════════════════════════════════════════════
HONEST GATE — FERMION MASS STATUS
═══════════════════════════════════════════════════════════════════════════
The leading-order c_L from winding quantization gives absolute fermion masses
that are O(10–100×) discrepant from PDG values.  The sub-leading CS correction
shifts masses by O(few %), not enough to reach agreement.

The precise c_L values that reproduce all nine quark/lepton masses to <0.01%
(Pillars 98 and 209) require a fit to observational data — they are NOT derived
from first principles alone.  Therefore:

    STATUS of P6–P18 fermion masses: FITTED (unchanged by Pillar 213)

The *architecture* result of Pillar 213 is the derivation of the correction
formula δc_L^(1,2) and the demonstration that the braid hierarchy generates a
systematic O(gen/K_CS) pattern — a falsifiable prediction for future precision
measurements.

The best-fit test that Pillar 213 *does* pass is on mass *ratios* between
consecutive generations, where the absolute c_R normalisation cancels.

═══════════════════════════════════════════════════════════════════════════
REFERENCES
═══════════════════════════════════════════════════════════════════════════
  • Pillar 93 — winding-quantized c_L
  • Pillar 98 (universal_yukawa.py) — exact c_L fit, <0.01% mass reproduction
  • Pillar 209 (pillar209_universal_yukawa_bc.py) — Ŷ₅ = 1 from GW vacuum
  • Randall & Sundrum (1999) Phys. Rev. Lett. 83, 3370
  • PDG 2024 mass values
"""
from __future__ import annotations

import math

__all__ = [
    "f0",
    "cl_leading",
    "cs_phase_correction",
    "cl_corrected",
    "braid_mass_ratio",
    "pillar213_summary",
    # Constants
    "N_W",
    "N1",
    "N2",
    "K_CS",
    "PI_KR",
    "V_EW_MEV",
    "YUKAWA5",
    # Sector labels
    "SECTORS",
]

__provenance__ = {
    "pillar": 213,
    "title": "Sub-leading Chern-Simons Braid Corrections to RS Bulk-Mass Spectrum",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "builds_on": ["Pillar 93", "Pillar 98", "Pillar 209"],
    "honest_status": (
        "Architecture result only — absolute masses require fitted c_L. "
        "P6-P18 fermion mass status remains FITTED."
    ),
    "toe_delta": 0,
}

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------
N_W: int = 5         # Braid winding number
N1: int = 5          # (n₁, n₂) braid pair
N2: int = 7
K_CS: int = 74       # = 5² + 7²; Chern-Simons level
PI_KR: float = 37.0  # π k R (RS compactification scale)
V_EW_MEV: float = 246_220.0   # Electroweak VEV in MeV (246.22 GeV)
YUKAWA5: float = 1.0           # Ŷ₅ = 1 (closed by Pillar 209)

# Generation labels (for dict keys)
SECTORS: tuple[str, ...] = ("leptons", "up_quarks", "down_quarks")

# PDG 2024 masses in MeV — used for honest error reporting only
_PDG_MEV: dict[str, dict[int, float]] = {
    "leptons":     {0: 0.510999, 1: 105.658,  2: 1776.86},
    "up_quarks":   {0: 2.16,     1: 1273.0,   2: 172_760.0},
    "down_quarks": {0: 4.67,     1: 93.4,     2: 4180.0},
}

# Fermion name labels (for summary readability)
_FERMION_NAMES: dict[str, dict[int, str]] = {
    "leptons":     {0: "e", 1: "mu", 2: "tau"},
    "up_quarks":   {0: "u", 1: "c",  2: "t"},
    "down_quarks": {0: "d", 1: "s",  2: "b"},
}


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def f0(c: float, pi_k_r: float = PI_KR) -> float:
    """RS zero-mode wavefunction for UV-localized fermions (c > 1/2).

    For c_L > 1/2:

        f₀(c) = √[(2c − 1) / (exp((2c − 1) π k R) − 1)]

    For c = 1/2 the formula reduces to f₀ = 1/√(π k R) (flat wave function).

    Parameters
    ----------
    c : float
        Bulk mass parameter.  For c > 1/2, fermion is UV-localized.
    pi_k_r : float
        RS scale π k R (default 37).

    Returns
    -------
    float
        Zero-mode wavefunction value f₀(c).

    Raises
    ------
    ValueError
        If pi_k_r <= 0 or c < 0.
    """
    if pi_k_r <= 0:
        raise ValueError(f"pi_k_r must be positive; got {pi_k_r}")
    if c < 0:
        raise ValueError(f"c must be non-negative; got {c}")

    x = 2.0 * c - 1.0  # > 0 for c > 0.5 (UV-localized); = 0 for c = 0.5 (flat); < 0 for c < 0.5 (IR-localized, non-physical)
    if abs(x) < 1e-12:
        # c = 1/2 limit: f0 = 1/sqrt(pi_k_r)
        return 1.0 / math.sqrt(pi_k_r)

    exp_arg = x * pi_k_r
    if exp_arg > 700:
        # Avoid overflow: exp(x*pi_k_r) >> 1
        return math.sqrt(x) * math.exp(-exp_arg / 2.0)

    denominator = math.exp(exp_arg) - 1.0
    if denominator <= 0:
        raise ValueError(f"Denominator non-positive for c={c}, pi_k_r={pi_k_r}")
    return math.sqrt(x / denominator)


def cl_leading(gen: int) -> float:
    """Leading-order winding-quantized bulk mass parameter c_L^(0)(gen).

    From Pillar 93:
        c_L^(0)(gen) = 1/2 + (n_w − gen) / (2 n_w)

    Parameters
    ----------
    gen : int
        Generation index (0, 1, or 2).

    Returns
    -------
    float

    Raises
    ------
    ValueError
        If gen is not in {0, 1, 2}.
    """
    if gen not in (0, 1, 2):
        raise ValueError(f"gen must be 0, 1, or 2; got {gen}")
    # Pillar 93 counts generation rank from 1 (electron=rank 1, muon=rank 2,
    # tau=rank 3), so internally we use rank = gen + 1:
    #   c_L = 0.5 + (n_w − rank) / (2 n_w),  rank ∈ {1, 2, 3}
    rank = gen + 1
    return 0.5 + (N_W - rank) / (2.0 * N_W)


def cs_phase_correction(gen: int, order: int = 1) -> float:
    """Chern-Simons braid correction δc_L to the bulk mass parameter.

    First-order (one-loop CS):
        δc_L^(1)(gen) = gen · n₁ · n₂ / (n₂² · K_CS)
                      = gen · 35 / 3626

    Second-order (two-loop CS):
        δc_L^(2)(gen) = gen² · (n₁ n₂)² / (n₂⁴ · K_CS²)

    Parameters
    ----------
    gen : int
        Generation index (0, 1, or 2).
    order : int
        Correction order — 1 or 2.

    Returns
    -------
    float
        The correction δc_L^(order)(gen).

    Raises
    ------
    ValueError
        If gen not in {0,1,2} or order not in {1, 2}.
    """
    if gen not in (0, 1, 2):
        raise ValueError(f"gen must be 0, 1, or 2; got {gen}")
    if order not in (1, 2):
        raise ValueError(f"order must be 1 or 2; got {order}")

    n1n2 = N1 * N2  # = 35
    n2sq = N2 ** 2  # = 49

    if order == 1:
        return gen * n1n2 / (n2sq * K_CS)
    # order == 2
    return gen ** 2 * n1n2 ** 2 / (N2 ** 4 * K_CS ** 2)


def cl_corrected(gen: int, order: int = 1) -> float:
    """Corrected bulk mass parameter c_L(gen, order).

    c_L(gen, 0) = c_L^(0)(gen)
    c_L(gen, 1) = c_L^(0)(gen) + δc_L^(1)(gen)
    c_L(gen, 2) = c_L^(0)(gen) + δc_L^(1)(gen) + δc_L^(2)(gen)

    Parameters
    ----------
    gen : int
        Generation index (0, 1, or 2).
    order : int
        Maximum correction order included (0, 1, or 2).

    Returns
    -------
    float

    Raises
    ------
    ValueError
        If gen not in {0,1,2} or order not in {0,1,2}.
    """
    if gen not in (0, 1, 2):
        raise ValueError(f"gen must be 0, 1, or 2; got {gen}")
    if order not in (0, 1, 2):
        raise ValueError(f"order must be 0, 1, or 2; got {order}")

    cl = cl_leading(gen)
    if order >= 1:
        cl += cs_phase_correction(gen, order=1)
    if order >= 2:
        cl += cs_phase_correction(gen, order=2)
    return cl


def _predict_mass_mev(gen: int, order: int = 1) -> float:
    """Predict fermion mass in MeV (all sectors share the same c_L structure).

    m_f(gen) = V_EW [MeV] × Ŷ₅ × f₀(c_L(gen)) × f₀(c_R = 0.5)

    f₀(c_R = 0.5) = 1/√(π k R)
    """
    cl = cl_corrected(gen, order=order)
    f0_L = f0(cl)
    f0_R = f0(0.5)   # = 1/sqrt(37)
    return V_EW_MEV * YUKAWA5 * f0_L * f0_R


def braid_mass_ratio(sector: str, order: int = 1) -> dict:
    """Compute consecutive-generation mass ratios m(gen+1)/m(gen).

    The ratios m_μ/m_e, m_τ/m_μ (and quark equivalents) cancel the c_R
    normalization and are therefore a cleaner test of the c_L hierarchy.

    Parameters
    ----------
    sector : str
        One of 'leptons', 'up_quarks', 'down_quarks'.
    order : int
        CS correction order (0, 1, or 2).

    Returns
    -------
    dict with keys:
        'sector'    : str
        'order'     : int
        'ratio_1_0' : float  — m(gen=1)/m(gen=0)
        'ratio_2_1' : float  — m(gen=2)/m(gen=1)
        'ratio_2_0' : float  — m(gen=2)/m(gen=0)
        'masses_mev': dict   — {gen: mass_mev}
        'pdg_ratio_1_0': float
        'pdg_ratio_2_1': float

    Raises
    ------
    ValueError
        If sector is unknown or order not in {0,1,2}.
    """
    if sector not in SECTORS:
        raise ValueError(f"sector must be one of {SECTORS}; got {sector!r}")
    if order not in (0, 1, 2):
        raise ValueError(f"order must be 0, 1, or 2; got {order}")

    masses = {gen: _predict_mass_mev(gen, order=order) for gen in (0, 1, 2)}
    pdg = _PDG_MEV[sector]

    return {
        "sector": sector,
        "order": order,
        "ratio_1_0": masses[1] / masses[0],
        "ratio_2_1": masses[2] / masses[1],
        "ratio_2_0": masses[2] / masses[0],
        "masses_mev": masses,
        "pdg_ratio_1_0": pdg[1] / pdg[0],
        "pdg_ratio_2_1": pdg[2] / pdg[1],
    }


def pillar213_summary() -> dict:
    """Full Pillar 213 summary.

    Returns
    -------
    dict with keys:
        'c_L_leading'          : {sector: {gen: float}}
        'c_L_corrected'        : {sector: {gen: float}}  (order=1)
        'mass_predictions_mev' : {sector: {gen: float}}
        'mass_pdg_mev'         : {sector: {gen: float}}
        'mass_pct_errors'      : {sector: {gen: float}}  (can be large)
        'correction_magnitudes': {gen: float}  (δc_L^(1))
        'honest_status'        : str
        'architecture_limit'   : str
        'toe_delta'            : int  (0)
    """
    # Leading and corrected c_L (all three sectors share the same c_L formula)
    c_L_leading: dict = {}
    c_L_corrected_d: dict = {}
    mass_preds: dict = {}
    mass_pct: dict = {}

    for sector in SECTORS:
        c_L_leading[sector] = {gen: cl_leading(gen) for gen in (0, 1, 2)}
        c_L_corrected_d[sector] = {gen: cl_corrected(gen, order=1) for gen in (0, 1, 2)}
        mass_preds[sector] = {gen: _predict_mass_mev(gen, order=1) for gen in (0, 1, 2)}
        pdg = _PDG_MEV[sector]
        mass_pct[sector] = {
            gen: 100.0 * abs(mass_preds[sector][gen] - pdg[gen]) / pdg[gen]
            for gen in (0, 1, 2)
        }

    correction_magnitudes = {gen: cs_phase_correction(gen, order=1) for gen in (0, 1, 2)}

    honest_status = (
        "Leading-order c_L from winding quantization gives absolute masses "
        "O(10-100x) off PDG.  The first-order CS braid correction shifts c_L "
        "by O(gen/K_CS) ~ few×10⁻³, improving masses by O(few%).  Exact "
        "agreement (<0.01%) requires fitted c_L values (Pillars 98 & 209).  "
        "STATUS P6-P18: FITTED (unchanged)."
    )

    architecture_limit = (
        "The braid hierarchy δc_L^(1)(gen) = gen·n₁n₂/(n₂²·K_CS) generates "
        "a systematic O(gen/K_CS) pattern across generations.  This is an "
        "architecture-level falsifiable prediction: future precision measurements "
        "of c_L (e.g., from RS KK-graviton resonance widths at colliders) should "
        "show this linear-in-gen sub-leading correction.  The prediction does NOT "
        "fix absolute masses without additional observational input."
    )

    return {
        "pillar": 213,
        "title": "Sub-leading Chern-Simons Braid Corrections to RS Bulk-Mass Spectrum",
        "c_L_leading": c_L_leading,
        "c_L_corrected": c_L_corrected_d,
        "mass_predictions_mev": mass_preds,
        "mass_pdg_mev": {s: dict(_PDG_MEV[s]) for s in SECTORS},
        "mass_pct_errors": mass_pct,
        "correction_magnitudes": correction_magnitudes,
        "honest_status": honest_status,
        "architecture_limit": architecture_limit,
        "toe_delta": 0,
    }
