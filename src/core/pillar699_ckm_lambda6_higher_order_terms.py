# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 699 — CKM Wolfenstein λ⁶ Higher-Order Correction

Extends the CKM Wolfenstein parameterisation to O(λ⁶), computing
the leading higher-order corrections to |Vus|, |Vub|, and the
Jarlskog invariant J (Pillar 693).

At O(λ⁶):
    |Vud| = 1 − λ²/2 − λ⁴/8 − λ⁶(1+4A²)/16
    |Vus| = λ(1 − λ⁴A²/2)
    |Vub| = Aλ³√(ρ²+η²)(1 − λ²/2)

The J correction at O(λ⁶):
    δJ/J ~ A²λ² × (1 − λ²/2) correction factor

This pillar also computes the CKM Cabibbo angle precision: the difference
between the standard O(λ⁴) and O(λ⁶) prediction for sin θ_C = λ_eff
provides a test of perturbativity in the KK FN mechanism.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""

import math

LAMBDA_W = 0.22500
A_W      = 0.826
RHO_BAR  = 0.159
ETA_BAR  = 0.348

def wolfenstein_o_lambda6(
    lam: float = LAMBDA_W,
    A:   float = A_W,
    rho_bar: float = RHO_BAR,
    eta_bar: float = ETA_BAR,
) -> dict:
    """
    CKM matrix elements at O(λ⁶).
    """
    rho = rho_bar / (1 - lam ** 2 / 2)
    eta = eta_bar / (1 - lam ** 2 / 2)

    # |Vud| to O(λ^6)
    Vud = 1 - lam**2/2 - lam**4/8 - lam**6 * (1 + 4*A**2) / 16

    # |Vus| to O(λ^6)
    Vus = lam * (1 - A**2 * lam**4 / 2)

    # |Vub| to O(λ^6) including λ^2 relative correction
    Vub = A * lam**3 * math.sqrt(rho**2 + eta**2) * (1 - lam**2 / 2)

    # Compare to O(λ^4) standard
    Vud_4 = 1 - lam**2/2 - lam**4/8
    Vus_4 = lam
    Vub_4 = A * lam**3 * math.sqrt(rho**2 + eta**2)

    return {
        "pillar":  699,
        "label":   "CKM_LAMBDA6_HIGHER_ORDER",
        "Vud_o6":  Vud,
        "Vus_o6":  Vus,
        "Vub_o6":  Vub,
        "Vud_o4":  Vud_4,
        "Vus_o4":  Vus_4,
        "Vub_o4":  Vub_4,
        "delta_Vud": abs(Vud - Vud_4),
        "delta_Vus": abs(Vus - Vus_4),
        "delta_Vub": abs(Vub - Vub_4),
        "lam_used":  lam,
        "A_used":    A,
    }

def jarlskog_o_lambda6_correction(
    lam: float = LAMBDA_W,
    A:   float = A_W,
    eta_bar: float = ETA_BAR,
) -> dict:
    """
    J = A²λ⁶η at O(λ⁶); relative correction from λ⁸ term.
    """
    eta = eta_bar / (1 - lam**2/2)
    J_o6  = A**2 * lam**6 * eta
    # O(λ^8) correction: δJ/J ~ −λ²(1+4A²)/8
    relative_correction_o8 = -lam**2 * (1 + 4*A**2) / 8
    return {
        "J_o6":                   J_o6,
        "relative_correction_o8": relative_correction_o8,
        "J_o8_estimate":          J_o6 * (1 + relative_correction_o8),
        "perturbativity_ok":      abs(relative_correction_o8) < 0.1,
    }

def cabibbo_angle_precision(lam: float = LAMBDA_W, A: float = A_W) -> dict:
    """
    Effective Cabibbo angle at O(λ⁶):  θ_C ≈ arcsin(|Vus_o6|)
    """
    V = wolfenstein_o_lambda6(lam, A)
    theta_c_o4 = math.asin(V["Vus_o4"])
    theta_c_o6 = math.asin(min(V["Vus_o6"], 1.0))
    return {
        "theta_c_o4_deg": math.degrees(theta_c_o4),
        "theta_c_o6_deg": math.degrees(theta_c_o6),
        "delta_theta_c_deg": abs(math.degrees(theta_c_o4) - math.degrees(theta_c_o6)),
        "relative_shift":    abs(theta_c_o4 - theta_c_o6) / theta_c_o4,
    }

def first_row_unitarity_o6(
    lam: float = LAMBDA_W,
    A:   float = A_W,
    rho_bar: float = RHO_BAR,
    eta_bar: float = ETA_BAR,
) -> dict:
    """First row unitarity at O(λ^6): |Vud|²+|Vus|²+|Vub|² ≈ 1"""
    V = wolfenstein_o_lambda6(lam, A, rho_bar, eta_bar)
    row = V["Vud_o6"]**2 + V["Vus_o6"]**2 + V["Vub_o6"]**2
    return {
        "row1_sum_o6":        row,
        "deviation_from_1":   abs(row - 1),
        "unitarity_satisfied": abs(row - 1) < 5e-4,   # O(λ^6) residual ~ λ^6 ~ 1.5e-4
    }
