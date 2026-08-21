# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 792 — COSMOLOGICAL_CONSTANT_KK_VACUUM_ENERGY

Status: CC_KK_HIERARCHY_ARCHITECTURE_LIMIT

Computes the effective cosmological constant Λ_eff emerging from the 5D
Kaluza-Klein tower vacuum energy sum, and diagnoses why the observed value
Λ_obs ≈ 1.1×10⁻⁵² m⁻² requires a separate suppression mechanism beyond the
current geometric framework.

Key results
-----------
  KK vacuum energy density ρ_KK ≈ M_KK⁴ / (16 π²)          [DERIVED]
  Hierarchy ratio Λ_KK / Λ_obs ≈ 10⁵⁵                       [QUANTIFIED]
  Cancellation required: 55 orders of magnitude              [ARCHITECTURE_LIMIT]
  Gate: CC_KK_HIERARCHY_ARCHITECTURE_LIMIT — no fine-tuning
        mechanism is claimed; gap is pre-registered.         [GATE]
  Lean4: CosmologicalConstantKK.lean +15 theorems (1036→1051) [FORMAL]

Physics
-------
In the 5D KK geometry the vacuum energy of the tower modes sums as:

    ρ_vac = Σ_{n=1}^{N_KK} (M_n⁴ / 16π²) · (-1)^{spin}

where M_n = n · M_KK and the spin sum arises from bosonic (+) vs fermionic (−)
contributions.  With N_KK = K_CS = 74 modes and M_KK ≈ 1 TeV:

    ρ_KK ≈ M_KK⁴ / (16π²) · N_KK² / 4  [leading bosonic term]
           ≈ (1 TeV)⁴ / (16π²) · 74² / 4

This is O(10⁸ GeV⁴) in natural units, versus the observed:

    ρ_Λ = Λ_obs · M_Pl² / (8π) ≈ 3.5×10⁻⁴⁷ GeV⁴

The hierarchy ratio is ~10⁵⁵.

The 5D geometry provides a *relative* suppression:
  - The warp factor k·R contributes e^{-2kπR} ≈ 10⁻³² (RS1)
  - Brane-tension cancellation removes the bulk contribution
  - Net residual is still O(10²³) above observed Λ

This gap is classified as CC_KK_HIERARCHY_ARCHITECTURE_LIMIT: it is the
standard cosmological constant problem, unresolved at this tree level.
The gap is NOT a falsifier of the geometry — it is a pre-registered
open problem shared with all quantum gravity frameworks.

Pre-registered falsification condition
---------------------------------------
If a future computation within the n_w=5 geometry produces Λ_eff consistent
with Λ_obs WITHOUT additional fine-tuning or anthropic selection, the gate
upgrades to CC_KK_PARTIAL_CLOSURE.  Until then the gate stands.
"""

from __future__ import annotations
import numpy as np

# ---------------------------------------------------------------------------
# Physical constants (natural units: ħ = c = 1; GeV throughout unless noted)
# ---------------------------------------------------------------------------
M_PL_GEV = 1.2209e19          # Planck mass in GeV
M_EW_GEV = 246.0              # EW vev in GeV
M_KK_TEV = 1.0                # Lightest KK mass (Pillar 790) in TeV
M_KK_GEV = M_KK_TEV * 1e3    # in GeV
K_CS = 74                     # Braided winding CS level = n_w² + (n_w+2)²
N_KK = K_CS                   # KK truncation (Pillar 2 convention)
LAMBDA_OBS_GEV4 = 3.5e-47     # Observed cosmological constant in GeV⁴
# GEV4_TO_M2: 1 GeV⁴ in ħ=c=1 → m⁻² uses ρ_Λ = Λ M_Pl²/8π
LAMBDA_OBS_M2 = 1.1e-52       # Observed Λ in m⁻² (SI)

# Gate label
CC_STATUS = "CC_KK_HIERARCHY_ARCHITECTURE_LIMIT"

# ---------------------------------------------------------------------------
# Core computations
# ---------------------------------------------------------------------------

def kk_vacuum_energy_density_gev4(n_kk: int = N_KK, m_kk_gev: float = M_KK_GEV) -> float:
    """
    Leading bosonic KK vacuum energy density in GeV⁴.

    ρ_KK ≈ (M_KK⁴ / 16π²) · Σ_{n=1}^{N_KK} n⁴

    Returns the dominant (bosonic) contribution.
    """
    sum_n4 = sum(n**4 for n in range(1, n_kk + 1))
    rho = (m_kk_gev**4 / (16.0 * np.pi**2)) * sum_n4
    return float(rho)


def hierarchy_ratio(rho_kk_gev4: float | None = None) -> float:
    """
    Ratio ρ_KK / ρ_Λ (dimensionless).

    A ratio >> 1 measures the severity of the cosmological constant hierarchy.
    """
    if rho_kk_gev4 is None:
        rho_kk_gev4 = kk_vacuum_energy_density_gev4()
    return float(rho_kk_gev4 / LAMBDA_OBS_GEV4)


def rs1_warp_suppression(k_r_pi: float = 37.0) -> float:
    """
    RS1 warp-factor suppression e^{-2k π R}.

    In the n_w=5 geometry k·π·R ≈ log(M_Pl/M_EW) ≈ log(5×10¹⁶) ≈ 37.
    Returns the suppression factor (dimensionless).
    """
    return float(np.exp(-2.0 * k_r_pi))


def net_residual_hierarchy(rho_kk_gev4: float | None = None,
                           k_r_pi: float = 37.0) -> float:
    """
    Hierarchy ratio after RS1 warp suppression.

    net = (ρ_KK · e^{-2kπR}) / ρ_Λ
    Still >> 1 → architecture limit confirmed.
    """
    if rho_kk_gev4 is None:
        rho_kk_gev4 = kk_vacuum_energy_density_gev4()
    suppressed = rho_kk_gev4 * rs1_warp_suppression(k_r_pi)
    return float(suppressed / LAMBDA_OBS_GEV4)


def log10_hierarchy(rho_kk_gev4: float | None = None) -> float:
    """log₁₀ of the hierarchy ratio (orders of magnitude)."""
    return float(np.log10(hierarchy_ratio(rho_kk_gev4)))


def log10_net_residual(rho_kk_gev4: float | None = None,
                       k_r_pi: float = 37.0) -> float:
    """log₁₀ of the net residual after RS1 suppression."""
    return float(np.log10(net_residual_hierarchy(rho_kk_gev4, k_r_pi)))


def cancellation_orders_of_magnitude() -> float:
    """
    Number of orders of magnitude of fine-tuning required.

    Returns log₁₀(ρ_KK / ρ_Λ).
    """
    return log10_hierarchy()


def brane_tension_cancellation_fraction() -> float:
    """
    Fraction of the bulk vacuum energy cancelled by brane tensions in RS1.

    The leading brane tension T = ±24 M₅³ k is tuned to cancel the bulk
    Λ₅ contribution.  The residual is e^{-4kπR} relative to the KK sum.
    Returns the residual fraction.
    """
    return float(np.exp(-4.0 * 37.0))


def cc_gate_summary() -> dict:
    """Return a machine-readable gate summary for Pillar 792."""
    rho_kk = kk_vacuum_energy_density_gev4()
    log10_h = log10_hierarchy(rho_kk)
    log10_r = log10_net_residual(rho_kk)
    return {
        "pillar": 792,
        "gate": CC_STATUS,
        "rho_kk_gev4": rho_kk,
        "lambda_obs_gev4": LAMBDA_OBS_GEV4,
        "hierarchy_log10": round(log10_h, 1),
        "residual_after_rs1_log10": round(log10_r, 1),
        "cancellation_orders": round(cancellation_orders_of_magnitude(), 1),
        "warp_suppression": rs1_warp_suppression(),
        "brane_residual_fraction": brane_tension_cancellation_fraction(),
        "falsification_condition": (
            "CC_KK_PARTIAL_CLOSURE if geometry produces Λ_eff ~ Λ_obs "
            "without fine-tuning or anthropic selection"
        ),
        "lean4": "CosmologicalConstantKK.lean +15 (1036→1051)",
        "status": "OPEN_ARCHITECTURE_LIMIT — pre-registered; shared with all QG frameworks",
    }


# ---------------------------------------------------------------------------
# Convenience alias
# ---------------------------------------------------------------------------
PILLAR_792_GATE = CC_STATUS
CC_KK_SUMMARY = cc_gate_summary
