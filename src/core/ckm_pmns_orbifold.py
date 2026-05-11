# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""
Pillar 104 — CKM + PMNS mixing angles from Randall-Sundrum orbifold overlap integrals.

At leading order (diagonal g5=1), Yukawa matrices have rank 1 → CKM = I exactly.
Wolfenstein-like estimates come from wavefunction ratios.
PMNS large mixing requires see-saw; UV-localized neutrinos give PMNS ≈ I at leading order.
"""

import numpy as np

from src.core.neutrino_p18_route_consolidation import p18_hardgate_certificate
from src.core.wolfenstein_geometry import wolfenstein_lambda_geometric

# ---------- repository constants ----------
N_W = 5
K_CS = 74
PI_KR = 37.0
V_EW = 174.0       # GeV, electroweak VEV
G5_YUKAWA = 1.0    # diagonal 5D Yukawa coupling

# ---------- default c-parameters ----------
C_L_QUARKS = [0.9, 0.8, 0.7]         # LH doublet, gen 1→3
C_R_UP = [0.5, 0.3, 0.1]              # RH up-type: u, c, t
C_R_DOWN = [0.5, 0.4, 0.3]           # RH down-type: d, s, b
C_L_LEPTONS = [0.80, 0.70, 0.60]     # LH lepton doublets: e, μ, τ

# ---------- PDG reference values (degrees) ----------
PDG_CKM_THETA12 = 13.1
PDG_CKM_THETA13 = 0.201
PDG_CKM_THETA23 = 2.38
PDG_PMNS_THETA12 = 33.44
PDG_PMNS_THETA13 = 8.57
PDG_PMNS_THETA23 = 42.1
PDG_WOLFENSTEIN_LAMBDA = 0.22650   # sin(θ_12^CKM)


def _pct_error(value, reference):
    """Return the percent error relative to the comparison reference."""
    if reference == 0:
        raise ValueError("reference must be non-zero")
    return abs(value - reference) / abs(reference) * 100.0


def rs_wavefunction_ir(c, pi_kr=37.0):
    """RS zero-mode wavefunction profile at the IR brane.

    f_IR(c) = sqrt(|1-2c|) × exp((0.5-c)×pi_kr) / sqrt(|exp((1-2c)×pi_kr) - 1|)
    Special case c = 0.5: f_IR = 1/sqrt(2×pi_kr).

    Overflow protection for large |exponent|.

    Parameters
    ----------
    c : float
        Bulk mass parameter.
    pi_kr : float
        π k R (default 37).

    Returns
    -------
    float : wavefunction value (positive)
    """
    if abs(c - 0.5) < 1e-10:
        return 1.0 / np.sqrt(2.0 * pi_kr)

    exponent = (1.0 - 2.0 * c) * pi_kr
    numerator = np.sqrt(abs(1.0 - 2.0 * c)) * np.exp((0.5 - c) * pi_kr)

    if exponent > 500.0:
        # denominator ≈ sqrt(exp(exponent))
        denominator = np.sqrt(np.exp(exponent))
    elif exponent < -500.0:
        # exp(exponent) → 0, so |exp(exponent) - 1| → 1
        denominator = 1.0
    else:
        denominator = np.sqrt(abs(np.exp(exponent) - 1.0))

    if denominator < 1e-300:
        return 0.0
    return float(numerator / denominator)


def yukawa_matrix_up(c_L=None, c_R_u=None, v_higgs_gev=174.0):
    """Build 3×3 up-type Yukawa mass matrix M[i,j] = f_IR(c_L[i]) × f_IR(c_R_u[j]) × V_EW.

    At leading order (diagonal g5=1) the matrix has rank 1 → CKM=I exactly.
    """
    if c_L is None:
        c_L = C_L_QUARKS
    if c_R_u is None:
        c_R_u = C_R_UP
    fL = np.array([rs_wavefunction_ir(c) for c in c_L])
    fR = np.array([rs_wavefunction_ir(c) for c in c_R_u])
    return np.outer(fL, fR) * v_higgs_gev


def yukawa_matrix_down(c_L=None, c_R_d=None, v_higgs_gev=174.0):
    """Build 3×3 down-type Yukawa mass matrix."""
    if c_L is None:
        c_L = C_L_QUARKS
    if c_R_d is None:
        c_R_d = C_R_DOWN
    fL = np.array([rs_wavefunction_ir(c) for c in c_L])
    fR = np.array([rs_wavefunction_ir(c) for c in c_R_d])
    return np.outer(fL, fR) * v_higgs_gev


def _svd_left_unitary(M):
    """Return the left unitary U from SVD: M = U Σ V†."""
    U, _, _ = np.linalg.svd(M)
    return U


def _extract_ckm_angles(V_ckm):
    """Extract CKM angles (degrees) from the CKM matrix."""
    t12 = float(np.degrees(np.arcsin(np.clip(abs(V_ckm[0, 1]), 0.0, 1.0))))
    t13 = float(np.degrees(np.arcsin(np.clip(abs(V_ckm[0, 2]), 0.0, 1.0))))
    cos13 = np.cos(np.radians(t13))
    if cos13 > 1e-10:
        t23 = float(np.degrees(np.arcsin(np.clip(abs(V_ckm[1, 2]) / cos13, 0.0, 1.0))))
    else:
        t23 = 0.0
    return t12, t13, t23


def ckm_from_yukawa(M_u, M_d):
    """Compute CKM matrix and angles from up- and down-type Yukawa matrices.

    At leading order (rank-1 matrices) CKM = I exactly.

    Parameters
    ----------
    M_u, M_d : ndarray, shape (3,3)

    Returns
    -------
    dict with V_ckm, theta_12_deg, theta_13_deg, theta_23_deg, pdg values, note
    """
    U_u = _svd_left_unitary(M_u)
    U_d = _svd_left_unitary(M_d)
    V_ckm = U_u.conj().T @ U_d
    t12, t13, t23 = _extract_ckm_angles(V_ckm)
    return {
        "V_ckm": V_ckm,
        "theta_12_deg": t12,
        "theta_13_deg": t13,
        "theta_23_deg": t23,
        "pdg_theta_12_deg": PDG_CKM_THETA12,
        "pdg_theta_13_deg": PDG_CKM_THETA13,
        "pdg_theta_23_deg": PDG_CKM_THETA23,
        "note": (
            "Rank-1 Yukawa (diagonal g5=1) → CKM=I at leading order. "
            "Off-diagonal mixing requires next-order g5 non-universality."
        ),
    }


def neutrino_c_spectrum(n_w=5):
    """Neutrino bulk mass parameters from the RS orbifold.

    c_ν[n] = 0.5 + n/(2×N_W) for n=1,2,3 → UV-localized (c > 0.5).

    Returns
    -------
    list of 3 floats
    """
    return [0.5 + n / (2.0 * n_w) for n in range(1, 4)]


def pmns_from_orbifold(c_nu_list=None, c_l_list=None, c_R_l=None):
    """Compute PMNS matrix from orbifold overlap integrals.

    UV-localized neutrinos (c_ν > 0.5) give small IR overlaps → PMNS ≈ I.
    Large PMNS mixing requires see-saw mechanism (documented open gap).

    Returns
    -------
    dict with U_pmns, theta_12_deg, theta_13_deg, theta_23_deg, pdg values, note
    """
    if c_nu_list is None:
        c_nu_list = neutrino_c_spectrum(n_w=N_W)
    if c_l_list is None:
        c_l_list = C_L_LEPTONS
    if c_R_l is None:
        c_R_l = [0.5, 0.4, 0.3]

    M_nu = yukawa_matrix_up(c_L=c_nu_list, c_R_u=c_nu_list, v_higgs_gev=V_EW)
    M_l = yukawa_matrix_up(c_L=c_l_list, c_R_u=c_R_l, v_higgs_gev=V_EW)

    U_nu = _svd_left_unitary(M_nu)
    U_l = _svd_left_unitary(M_l)
    U_pmns = U_nu.conj().T @ U_l
    t12, t13, t23 = _extract_ckm_angles(U_pmns)

    return {
        "U_pmns": U_pmns,
        "theta_12_deg": t12,
        "theta_13_deg": t13,
        "theta_23_deg": t23,
        "pdg_theta_12_deg": PDG_PMNS_THETA12,
        "pdg_theta_13_deg": PDG_PMNS_THETA13,
        "pdg_theta_23_deg": PDG_PMNS_THETA23,
        "note": (
            "UV-localized c_ν gives PMNS≈I at leading order. "
            "Large mixing (θ₁₂≈33°, θ₂₃≈42°) requires see-saw mechanism — documented open gap."
        ),
    }


def ckm_wolfenstein_estimate(c_L_list=None):
    """Estimate Wolfenstein parameter λ from wavefunction ratios.

    eps[i] = f_IR(c_L[i])
    lambda_W = eps[0]/eps[1]  (gen1/gen2 ratio)
    Note: lambda_W ≈ 0.029 vs PDG sin(13.1°) ≈ 0.227 — documented open gap.

    Returns
    -------
    dict with lambda_wolfenstein, theta_12_deg, theta_13_deg, theta_23_deg,
          pdg_lambda, note
    """
    if c_L_list is None:
        c_L_list = C_L_QUARKS
    eps = [rs_wavefunction_ir(c) for c in c_L_list]
    lam = eps[0] / eps[1] if eps[1] > 0 else 0.0
    th12 = float(np.degrees(np.arcsin(min(lam, 1.0))))
    th23 = float(np.degrees(np.arcsin(min(eps[1] / eps[2] if eps[2] > 0 else 0.0, 1.0))))
    th13 = float(np.degrees(np.arcsin(min(lam ** 3, 1.0))))
    return {
        "lambda_wolfenstein": lam,
        "theta_12_deg": th12,
        "theta_13_deg": th13,
        "theta_23_deg": th23,
        "pdg_lambda": PDG_WOLFENSTEIN_LAMBDA,
        "note": (
            f"λ_W = eps[0]/eps[1] = {lam:.4f} vs PDG Wolfenstein λ = {PDG_WOLFENSTEIN_LAMBDA:.5f} "
            f"(= sin(13.1°) ≈ 0.22650). "
            "Gap factor ~8× requires next-order c_L non-universality (open gap)."
        ),
    }


def pmns_angle_estimate(c_nu_list=None, c_l_list=None):
    """Parametric PMNS angle estimates from wavefunction ratios.

    eps_nu[i] = f_IR(c_nu[i]), eps_l[i] = f_IR(c_L_leptons[i])
    theta_12_est = arctan(eps_nu[0]/eps_nu[1])
    theta_23_est = arctan(eps_nu[1]/eps_nu[2])

    Returns
    -------
    dict with estimates, note
    """
    if c_nu_list is None:
        c_nu_list = neutrino_c_spectrum(n_w=N_W)
    if c_l_list is None:
        c_l_list = C_L_LEPTONS

    eps_nu = [rs_wavefunction_ir(c) for c in c_nu_list]
    eps_l = [rs_wavefunction_ir(c) for c in c_l_list]

    ratios = [eps_nu[i] / eps_l[i] if eps_l[i] > 0 else 0.0 for i in range(3)]
    th12 = float(np.degrees(np.arctan2(ratios[0], ratios[1]))) if ratios[1] > 0 else 0.0
    th23 = float(np.degrees(np.arctan2(ratios[1], ratios[2]))) if ratios[2] > 0 else 0.0

    return {
        "eps_nu": eps_nu,
        "eps_l": eps_l,
        "ratios": ratios,
        "theta_12_est_deg": th12,
        "theta_23_est_deg": th23,
        "pdg_theta_12_deg": PDG_PMNS_THETA12,
        "pdg_theta_23_deg": PDG_PMNS_THETA23,
        "note": (
            "UV-localized ν wavefunctions nearly degenerate → small ratios. "
            "Large PMNS mixing requires see-saw (documented open gap)."
        ),
    }


def ckm_pmns_orbifold_report():
    """Return a status report for Pillar 104."""
    certificate = ckm_pmns_orbifold_architecture_certificate()
    ckm_w = ckm_wolfenstein_estimate()
    pmns_d = pmns_from_orbifold()
    return {
        "status": certificate["status"],
        "module": "ckm_pmns_orbifold",
        "pillar": 104,
        "ckm_theta12_deg": ckm_w["theta_12_deg"],
        "ckm_pdg_theta12_deg": PDG_CKM_THETA12,
        "ckm_wolfenstein_lambda": ckm_w["lambda_wolfenstein"],
        "ckm_pdg_lambda": PDG_WOLFENSTEIN_LAMBDA,
        "pmns_theta12_deg": pmns_d["theta_12_deg"],
        "pmns_pdg_theta12_deg": PDG_PMNS_THETA12,
        "architecture_limit_scope": certificate["scope"],
        "ckm_overlap_residual_pct": certificate["ckm_overlap_residual_pct"],
        "pmns_overlap_theta12_residual_pct": certificate["pmns_overlap_theta12_residual_pct"],
        "cross_checks": certificate["cross_checks"],
        "residual_unknowns": [
            "CKM off-diagonal mixing requires next-order g5 non-universality.",
            (
                f"Wolfenstein λ_W from leading-order overlaps remains {certificate['ckm_gap_factor_vs_pdg']:.2f}× "
                "below PDG; the mass-ratio route is the usable CKM λ closure surface."
            ),
            "PMNS large mixing requires see-saw / braid-lock closure beyond the diagonal-g5 overlap lane.",
            "Neutrino mass hierarchy and full CKM phase are not predicted by this leading-order module.",
        ],
        "epistemic_label": (
            "ARCHITECTURE_LIMIT_CERTIFIED — this module is the leading-order diagonal-g5 orbifold-overlap lane only; "
            "it honestly certifies where CKM/PMNS closure requires higher-order or alternate geometric routes."
        ),
    }


def ckm_pmns_orbifold_architecture_certificate():
    """Certify the best honest status of the leading-order orbifold overlap lane."""
    ckm_overlap = ckm_wolfenstein_estimate()
    ckm_mass_ratio = wolfenstein_lambda_geometric()
    pmns_overlap = pmns_from_orbifold()
    p18_certificate = p18_hardgate_certificate()

    pmns_route_a_sin2 = float(p18_certificate["report"]["route_a_rge_crosscheck"]["mz_value"])
    pmns_route_a_theta12_deg = float(np.degrees(np.arcsin(np.sqrt(pmns_route_a_sin2))))

    return {
        "status": "ARCHITECTURE_LIMIT_CERTIFIED",
        "scope": "leading-order diagonal-g5 RS orbifold overlap lane",
        "ckm_overlap_lambda": ckm_overlap["lambda_wolfenstein"],
        "ckm_overlap_theta12_deg": ckm_overlap["theta_12_deg"],
        "ckm_overlap_residual_pct": _pct_error(
            ckm_overlap["lambda_wolfenstein"], PDG_WOLFENSTEIN_LAMBDA
        ),
        "ckm_gap_factor_vs_pdg": (
            PDG_WOLFENSTEIN_LAMBDA / ckm_overlap["lambda_wolfenstein"]
            if ckm_overlap["lambda_wolfenstein"] > 0.0 else float("inf")
        ),
        "pmns_overlap_theta12_deg": pmns_overlap["theta_12_deg"],
        "pmns_overlap_theta12_residual_pct": _pct_error(
            pmns_overlap["theta_12_deg"], PDG_PMNS_THETA12
        ),
            "cross_checks": {
                "ckm_mass_ratio_route": {
                    "lambda_geo": ckm_mass_ratio["lambda_geo"],
                    "residual_pct": ckm_mass_ratio["discrepancy_percent"],
                    "status": "usable canonical CKM λ route outside the overlap-only lane",
                },
            "pmns_route_a_rge": {
                "sin2_theta12": pmns_route_a_sin2,
                "theta12_deg": pmns_route_a_theta12_deg,
                "residual_pct": p18_certificate["new_residual_pct"],
                "status": p18_certificate["new_status"],
            },
        },
        "closing_mechanisms": [
            "CKM: off-diagonal g5 non-universality / higher-order overlap structure",
            "PMNS: see-saw or braid-lock route rather than diagonal-g5 overlaps alone",
        ],
        "verdict": (
            "The leading-order orbifold-overlap lane is not the canonical closure route for CKM/PMNS. "
            "It is retained as an honest architecture-limit certificate showing exactly where the "
            "diagonal-g5 approximation fails and which higher-order routes currently carry the closure."
        ),
    }
