# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 713 — B-mode Polarisation Power Spectrum: KK Prediction

The B-mode CMB polarisation power spectrum C_ℓ^BB provides the primary
observational window on the tensor-to-scalar ratio r.

KK predictions:
    r = R_BRAIDED = 0.0315   (Pillar 660)
    n_T = n_T_KK ≈ −0.0466  (Pillar 712, with c_s = 12/37)

The B-mode power spectrum at recombination peak (ℓ ≈ 80):
    C_80^BB ≈ (r / 0.1) × 0.15 μK²

For r = 0.0315: C_80^BB ≈ 0.315 × 0.15 ≈ 0.047 μK²

Current BICEP/Keck upper limit: r < 0.036 at 95% CL.
The KK prediction r = 0.0315 is within the current 95% CL band
and accessible to CMB-S4, LiteBIRD, and Simons Observatory.

This pillar also computes the angular power spectrum shape
C_ℓ^BB(ℓ) for ℓ = 2–200 using the tensor transfer approximation.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""

import math

# ── CMB constants ─────────────────────────────────────────────────────────────
R_BRAIDED   = 0.0315
N_T_KK      = -0.0466     # from Pillar 712 (braided c_s correction)
A_S         = 2.1e-9      # scalar amplitude (Planck)
A_T         = R_BRAIDED * A_S   # tensor amplitude

# B-mode amplitude normalisation at ℓ=80
C_BB_L80_PER_R = 0.15     # μK² per unit r (empirical calibration)

# ── C_ℓ^BB power spectrum ─────────────────────────────────────────────────────

def c_bb_l(ell: int,
            r: float = R_BRAIDED,
            n_t: float = N_T_KK,
            ell_pivot: int = 80) -> float:
    """
    Approximate C_ℓ^BB in μK²:
        C_ℓ^BB ≈ (r/0.1) × C_BB_L80_PER_R × (ℓ/ℓ_pivot)^(2+n_T)
                 × exp(−ℓ(ℓ+1)/9000)    (reionisation + damping)
    """
    norm = (r / 0.1) * C_BB_L80_PER_R
    tilt = (ell / ell_pivot) ** (2 + n_t)
    damping = math.exp(-ell * (ell + 1) / 9000.0)
    return norm * tilt * damping

def c_bb_peak(r: float = R_BRAIDED) -> float:
    """C_ℓ^BB at the recombination peak (ℓ=80)"""
    return c_bb_l(80, r=r)

def r_within_bicep_keck_limit(r: float = R_BRAIDED,
                                r_limit: float = 0.036) -> bool:
    return r < r_limit

# ── LiteBIRD / CMB-S4 detectability ─────────────────────────────────────────

def litebird_sensitivity_sigma(r: float = R_BRAIDED,
                                sigma_r: float = 0.001) -> float:
    """Detection significance: r / σ_r"""
    return r / sigma_r

def b_mode_summary() -> dict:
    c80 = c_bb_peak()
    det_sig = litebird_sensitivity_sigma()
    return {
        "pillar":           713,
        "label":            "BMODE_POLARISATION_POWER_SPECTRUM",
        "r":                R_BRAIDED,
        "n_t_kk":           N_T_KK,
        "c_bb_l80_muk2":    c80,
        "within_bicep_keck": r_within_bicep_keck_limit(),
        "litebird_sigma":   det_sig,
        "litebird_detectable": det_sig > 10,
        "litebird_timeline": "~2032",
        "cmbs4_timeline":    "~2035",
        "primary_falsifier": True,
    }
