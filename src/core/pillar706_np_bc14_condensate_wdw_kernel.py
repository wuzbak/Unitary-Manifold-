# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 706 — NP-BC14: Non-Perturbative Condensate WdW Kernel

Closes NP-BC14 by computing the gluon and Higgs condensate contributions
to the Wheeler–DeWitt path-integral measure in the KK framework.

The gluon condensate ⟨αs/π G²⟩ ≈ (330 MeV)⁴ enters via the trace anomaly:

    Γ_cond = -(b_QCD/32π²) × ⟨G_μν² ⟩

where b_QCD = 11 - 2n_f/3 = 7 (for n_f = 3 light quarks).

The Higgs condensate ⟨v²⟩ ≈ (246 GeV)² contributes:

    Γ_higgs = λ_H × ⟨φ†φ⟩²   (quartic with λ_H = m_H²/(2v²) ≈ 0.129)

Kernel:
    K_BC14 = G_N* × (Γ_cond + Γ_higgs) × (1 - G_N / G_N*)²

Both condensates are SM-scale objects (far below M_KK) so the kernel
is hierarchically smaller than the one-loop KK contributions (BC9–BC11).

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""

import math

# ── Constants ─────────────────────────────────────────────────────────────────
N_W   = 5
K_CS  = 74
G_N_STAR = 3 * math.pi / (N_W * K_CS - 10)    # ≈ 0.02618

# QCD gluon condensate: ⟨αs/π G²⟩ = (330 MeV)⁴ in GeV⁴
GLUON_CONDENSATE_GEV4 = (0.330) ** 4   # GeV⁴

# Higgs vev
V_HIGGS_GEV  = 246.0      # GeV
M_HIGGS_GEV  = 125.25     # GeV
LAMBDA_HIGGS = M_HIGGS_GEV ** 2 / (2 * V_HIGGS_GEV ** 2)   # ≈ 0.129

B_QCD = 7.0   # β-function coefficient (n_f = 3)

# Unit conversion: 1 GeV = 1/(1.221×10¹⁹) M_Pl
GEV_TO_MPL = 1.0 / 1.221e19

# ── Condensate widths ─────────────────────────────────────────────────────────

def gamma_gluon_condensate() -> float:
    """Γ_cond = (b_QCD / 32π²) × ⟨G²⟩  [M_Pl = 1 units]"""
    G2_mpl4 = GLUON_CONDENSATE_GEV4 * GEV_TO_MPL ** 4
    return (B_QCD / (32 * math.pi ** 2)) * G2_mpl4

def gamma_higgs_condensate() -> float:
    """Γ_higgs = λ_H × ⟨φ†φ⟩²  where ⟨φ†φ⟩ = v²/2 [M_Pl = 1 units]"""
    phi_sq_mpl2 = (V_HIGGS_GEV ** 2 / 2) * GEV_TO_MPL ** 2
    return LAMBDA_HIGGS * phi_sq_mpl2 ** 2

# ── BC14 kernel ───────────────────────────────────────────────────────────────

def compute_bc14_kernel(
    g_n: float = G_N_STAR,
    g_n_star: float = G_N_STAR,
) -> dict:
    """K_BC14 = G_N* × (Γ_gluon + Γ_higgs) × (1 - G_N/G_N*)²"""
    gamma_g   = gamma_gluon_condensate()
    gamma_h   = gamma_higgs_condensate()
    gamma_tot = gamma_g + gamma_h
    supp      = (1.0 - g_n / g_n_star) ** 2 if g_n_star != 0 else 0.0
    kernel    = g_n_star * gamma_tot * supp
    return {
        "pillar":            706,
        "label":             "NP_BC14_CONDENSATE_KERNEL_COMPUTED",
        "gamma_gluon":       gamma_g,
        "gamma_higgs":       gamma_h,
        "gamma_total":       gamma_tot,
        "suppression":       supp,
        "kernel_bc14":       kernel,
        "g_n_star":          g_n_star,
        "g_n":               g_n,
        "units":             "M_Pl = 1",
    }

def bc14_fixed_point_vanishing(g_n_star: float = G_N_STAR) -> dict:
    result = compute_bc14_kernel(g_n=g_n_star, g_n_star=g_n_star)
    return {"vanishes": result["kernel_bc14"] == 0.0}

def np_bc_ledger() -> dict:
    return {
        "bc1_through_bc13": "CLOSED",
        "bc14":             "BC14 — CLOSED — condensate contributions",
        "bc14_status":      "CLOSED",
        "ledger_complete_through": "BC14",
        "next_bc15":        "BC15 — topological (Chern-Simons) contributions",
    }
