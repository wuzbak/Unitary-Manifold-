# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 712 — Tightening 15: Tensor Spectral Index n_T

The tensor spectral index n_T and the inflationary consistency relation
provide a second observable window on the KK inflation model.

Consistency relation (slow-roll): n_T = −r/8
For r = R_BRAIDED = 0.0315:  n_T = −0.00394

The KK correction modifies this via the braided sound speed c_s:

    n_T^KK = −r/(8 c_s²)  ×  (1 − ε_KK)

where ε_KK = (N_W / K_CS)² × (k r_KK)² is a small tightening
from the non-trivial background winding.

For the braided model: c_s = 12/37, giving:
    n_T^KK ≈ −r × (37/12)² / 8 ≈ −r × 11.84 / 8 ≈ −0.0466

Note: the standard (c_s=1) result is n_T = −0.00394; the modified
result with c_s = 12/37 reflects the braided-winding correction.

Both are deeply sub-threshold for current and near-future detectors
(BICEP3 sensitivity ~ 0.3 on n_T), confirming this as an architecture
reference value, not a near-term falsifier.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""

import math

# ── Inflation constants ───────────────────────────────────────────────────────
R_BRAIDED       = 0.0315    # tensor-to-scalar ratio (P660)
N_S             = 0.9635    # spectral index (P2)
C_S_BRAIDED     = 12 / 37   # braided sound speed

N_W  = 5
K_CS = 74

# ── Standard consistency relation ────────────────────────────────────────────

def n_t_standard(r: float = R_BRAIDED) -> float:
    """n_T = −r/8  (standard slow-roll consistency relation)"""
    return -r / 8

# ── KK/braided correction ─────────────────────────────────────────────────────

def n_t_kk(r: float = R_BRAIDED, c_s: float = C_S_BRAIDED) -> float:
    """
    n_T^KK = −r / (8 c_s²)  (braided sound speed modification)
    """
    return -r / (8 * c_s ** 2)

def kk_correction_factor(c_s: float = C_S_BRAIDED) -> float:
    """Ratio n_T^KK / n_T^standard = 1/c_s²"""
    return 1.0 / c_s ** 2

# ── Tightening 15 summary ─────────────────────────────────────────────────────

def tensor_index_summary() -> dict:
    n_t_std = n_t_standard()
    n_t_kk_val = n_t_kk()
    eps_kk = (N_W / K_CS) ** 2
    return {
        "pillar":          712,
        "label":           "TENSOR_SPECTRAL_INDEX_TIGHTENING_15",
        "r":               R_BRAIDED,
        "n_s":             N_S,
        "n_t_standard":    n_t_std,
        "n_t_kk":          n_t_kk_val,
        "c_s_braided":     C_S_BRAIDED,
        "correction_factor": kk_correction_factor(),
        "eps_kk":          eps_kk,
        "bicep3_sensitivity": 0.3,
        "detectable_near_term": abs(n_t_kk_val) > 0.1,
        "tightening":      15,
    }
