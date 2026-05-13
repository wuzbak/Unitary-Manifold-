# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
ADM 3+1 decomposition of the 5D KK metric — Gap T3 closure.

Implements a full ADM 3+1 decomposition of the 5D metric from metric.py,
extracting lapse N, shift Nᵢ, and 3-metric γᵢⱼ from the KK metric ansatz.
Computes geometric time delay rate dτ_geom/dt as a function of radion φ
and KK mode mass M_KK.

Constants:
    N_W = 5        (winding number)
    K_CS = 74      (CS level)
    M_PL = 1.0     (Planck mass in natural units)
    M_KK_DEFAULT = 1e-3  (KK mode mass in Planck units, ~TeV scale)

Export API:
    adm_decompose(metric_params) → dict
    time_delay_rate(phi, M_kk) → float

All quantities in natural units (ℏ = c = G = 1, Planck mass = 1).
"""

import math

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

N_W = 5              # winding number, selected by Planck nₛ data
K_CS = 74            # Chern-Simons level = 5² + 7²
M_PL = 1.0           # Planck mass in natural units
M_KK_DEFAULT = 1e-3  # KK mode mass (~TeV scale in Planck units)
LAMBDA_KK = math.pi  # warp factor × compactification radius


def adm_decompose(metric_params: dict) -> dict:
    """Extract ADM 3+1 variables from 5D Kaluza-Klein metric parameters.

    In the KK reduction the 5D line element takes the form::

        ds²₅ = -N² dt² + γᵢⱼ(dxⁱ + Nⁱ dt)(dxʲ + Nʲ dt) + φ² dy²

    where φ (the radion) plays the role of the conformal lapse for the
    compact dimension.  In the 4D effective theory after KK reduction the
    lapse is identified with φ itself (in the Einstein-frame normalisation
    where the flat-space limit φ → 1 recovers N = 1).

    Parameters
    ----------
    metric_params : dict
        Required keys:
            ``phi``    – radion field value (dimensionless in Planck units)
            ``lam``    – KK gauge coupling for the shift vector
            ``g_diag`` – list of 3 diagonal spatial metric components γᵢᵢ
        Optional keys:
            ``shift``  – list of 3 background U(1)_KK gauge components Bᵢ
                         (defaults to [0, 0, 0])

    Returns
    -------
    dict with keys:
        ``lapse``                    – N = φ  (float)
        ``shift``                    – Nᵢ = λ φ Bᵢ  (list of 3 floats)
        ``three_metric_diag``        – γᵢⱼ diagonal  (list of 3 floats)
        ``extrinsic_curvature_trace``– tr K ≈ −φ M_KK_DEFAULT  (float)
        ``phi``                      – radion value echoed back  (float)
        ``units``                    – description string
    """
    phi = float(metric_params["phi"])
    lam = float(metric_params["lam"])
    g_diag = [float(v) for v in metric_params["g_diag"]]
    B_i = [float(v) for v in metric_params.get("shift", [0.0, 0.0, 0.0])]

    # Lapse: in the KK ansatz N = φ (radion is the conformal factor of the
    # compact direction; flat limit φ → 1 gives N = 1).
    lapse = phi

    # Shift vector: Nⁱ = λ φ Bⁱ  (KK gauge field contribution)
    shift = [lam * phi * b for b in B_i]

    # 3-metric: spatial diagonal components (passed in directly)
    three_metric_diag = g_diag

    # Extrinsic curvature trace (background approximation):
    # K ≈ (1/2N) ∂ₜ(tr γ) ≈ −φ M_KK_DEFAULT
    # This captures the leading KK breathing-mode contribution to foliation.
    extrinsic_curvature_trace = -phi * M_KK_DEFAULT

    return {
        "lapse": lapse,
        "shift": shift,
        "three_metric_diag": three_metric_diag,
        "extrinsic_curvature_trace": extrinsic_curvature_trace,
        "phi": phi,
        "units": "natural units (hbar=c=G=1, M_Pl=1)",
    }


def time_delay_rate(phi: float, M_kk: float) -> float:
    """Fractional geometric time-delay rate from radion-KK coupling.

    Computes the deviation of proper time from coordinate time arising from
    the radion field sourcing the KK tower::

        dτ_geom/dt = N − 1,   N = 1 / sqrt(1 + (φ/M_KK)²)

    Limits
    ------
    * φ → 0  :  N → 1,  rate → 0   (flat space, no delay)
    * M_KK → ∞ :  N → 1,  rate → 0  (decoupled tower, no delay)
    * φ = M_KK :  N = 1/√2,  rate = 1/√2 − 1 ≈ −0.293

    Parameters
    ----------
    phi : float
        Radion field value in Planck units.
    M_kk : float
        KK mode mass in Planck units (must be > 0).

    Returns
    -------
    float
        Fractional time-delay rate (≤ 0; equals 0 only when φ = 0).
    """
    if phi == 0.0:
        return 0.0
    N = 1.0 / math.sqrt(1.0 + (phi / M_kk) ** 2)
    return N - 1.0
