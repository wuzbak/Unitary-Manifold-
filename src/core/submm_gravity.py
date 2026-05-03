# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/submm_gravity.py
=========================
Pillar 108 — Sub-mm Gravity Tests of the Compact 5th Dimension.

The Unitary Manifold compactifies the 5th dimension on S¹/Z₂ with a
KK mass scale M_KK ≈ 110 meV.  Via ħc / M_KK this corresponds to a
compactification length L_c ≈ 1.79 μm, placing a sharp Yukawa
deviation in Newton's law at the micron scale.

Current Eöt-Wash torsion-balance experiments probe down to ~50 μm.
Next-generation experiments targeting the ~2 μm scale would directly
probe the predicted compactification length.

References
----------
Kapner et al. (2007) PRL 98, 021101 — current sub-mm gravity limits.
Lee et al. (2020) PRL 124, 101101 — improved torsion-balance results.
"""

import math

# ── physical constants ────────────────────────────────────────────────────────
_HC_MEV_M = 197.3269804e-15   # ħc in MeV·m
_M_KK_MEV = 0.110e-6          # M_KK = 110 meV = 0.110 eV = 0.110e-6 MeV

# ── module-level constants ────────────────────────────────────────────────────
WINDING_NUMBER = 5
K_CS = 74

# Compactification length in metres (computed once at import)
_L_C_M: float = _HC_MEV_M / _M_KK_MEV   # ≈ 1.79e-6 m ≈ 1.79 μm


# ── public API ────────────────────────────────────────────────────────────────

def compactification_length_m(m_kk_mev: float = _M_KK_MEV) -> float:
    """Return the compactification length L_c = ħc / M_KK in metres."""
    if m_kk_mev <= 0:
        raise ValueError("m_kk_mev must be positive")
    return _HC_MEV_M / m_kk_mev


def gravity_deviation_yukawa(r_m: float, alpha: float = 1.0,
                             m_kk_mev: float = _M_KK_MEV) -> float:
    """Yukawa fractional deviation δg/g = alpha × exp(-r_m / L_c).

    Parameters
    ----------
    r_m : float
        Separation in metres.
    alpha : float
        Coupling strength (order-1 for lowest KK graviton).
    m_kk_mev : float
        KK mass in MeV (default 110 meV).
    """
    if r_m < 0:
        raise ValueError("r_m must be non-negative")
    l_c = compactification_length_m(m_kk_mev)
    return alpha * math.exp(-r_m / l_c)


def current_experiment_reach_m() -> float:
    """Best current torsion-balance reach: ~50 μm (Eöt-Wash)."""
    return 50e-6


def next_gen_target_m() -> float:
    """Next-generation target separation: ~2 μm."""
    return 2e-6


def experiment_sensitivity_ratio(m_kk_mev: float = _M_KK_MEV) -> float:
    """Ratio of current experiment reach to L_c.

    Values >> 1 mean current experiments cannot yet probe the prediction.
    """
    return current_experiment_reach_m() / compactification_length_m(m_kk_mev)


def submm_gravity_summary(m_kk_mev: float = _M_KK_MEV) -> dict:
    """Return a summary dictionary of sub-mm gravity predictions.

    Keys
    ----
    L_c_microns          : compactification length in microns
    current_reach_microns: Eöt-Wash reach in microns
    next_gen_target_microns: next-gen target in microns
    sensitivity_ratio    : current_reach / L_c
    detectable_next_gen  : True if next_gen_target_m < L_c × 10
    """
    l_c = compactification_length_m(m_kk_mev)
    curr = current_experiment_reach_m()
    nxt = next_gen_target_m()
    return {
        "L_c_microns": l_c * 1e6,
        "current_reach_microns": curr * 1e6,
        "next_gen_target_microns": nxt * 1e6,
        "sensitivity_ratio": curr / l_c,
        "detectable_next_gen": nxt < l_c * 10,
    }
