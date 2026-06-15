# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
pillar525_juno_2026_falsification_response.py — Pillar 525: JUNO First Physics
Results (Nature, June 10 2026) — rigorous falsification response.

═══════════════════════════════════════════════════════════════════════════
PILLAR 525 — JUNO_2026_FALSIFICATION_RESPONSE
═══════════════════════════════════════════════════════════════════════════

Event: JUNO Collaboration publishes first physics results in *Nature*,
June 10 2026.  59 days of reactor antineutrino data yield:

    Δm²₃₁ = (2.411 ± 0.020) × 10⁻³ eV²   (σ_frac ≈ 0.81%)

This is the first sub-1% precision measurement of the atmospheric
mass-squared splitting, superseding the PDG 2023 baseline (1.3%).

─────────────────────────────────────────────────────────────────────────
VERDICT ON UM 2NLO ESTIMATE
─────────────────────────────────────────────────────────────────────────
The Pillar 17 2NLO prediction from `src/sixd/neutrino_dm31_2nlo.py`:

    Δm²₃₁(2NLO) = 2.453 × 10⁻³ × (1 − 0.0687) ≈ 2.2845 × 10⁻³ eV²

compared to JUNO 2.411 × 10⁻³ eV² yields a tension of **6.46σ** —
formally EXCLUDED at current JUNO precision.  This is documented
honestly as HONEST_OPEN_PROBLEM in FALLIBILITY.md §XV.

─────────────────────────────────────────────────────────────────────────
BEST-ATTEMPT PROJECTION: CHAIN OF ALL KNOWN CORRECTIONS
─────────────────────────────────────────────────────────────────────────
This module applies every correction already named in the repository
chain, starting from the 2NLO baseline:

  Step 1 — 2NLO T²/Z₃ baseline:
       Δm²₃₁(2NLO) ≈ 2.2845 × 10⁻³ eV²   (6.87% below PDG)

  Step 2 — τ-Yukawa RGE running from M_KK (1 TeV) to m_atm (≈49.5 meV):
       δ_RGE = (y_τ²/8π²) × ln(M_KK / m_atm) ≈ 4.04 × 10⁻⁵
       This is the leading RGE back-reaction on the τ-lepton channel.
       Sign: positive (Δm²₃₁ runs upward toward lower μ). [Pillar 274]

  Step 3 — Kaluza-Klein Majorana seesaw partner, Z₂-symmetric, at p_R:
       δ_seesaw = p_R × (v/M_R)² = p_R × (246.22/1000)² ≈ p_R × 0.06062
       Upper bound from PMNS rotation geometry:
           p_R^max = sin²θ₂₃ × cos²θ₁₃ ≈ 0.4411   [Pillar 274]
       Max seesaw contribution: δ_seesaw^max ≈ 2.674%
       Sign: positive (partner integrated out adds to effective splitting).
       Named gap: SEESAW_TEXTURE_PARTICIPATION_GAP — exact p_R requires
       full KK Yukawa texture diagonalization (Pillar 274 §PMNS-bound).

  Combined projection at p_R = p_R^max (maximally aggressive):
       Δm²₃₁(proj) = 2.2845e-3 × (1 + δ_RGE + δ_seesaw^max)
                    ≈ 2.3457 × 10⁻³ eV²

  Tension of projection vs JUNO 2026:
       |2.411 − 2.346| / σ_JUNO = 0.065e-3 / 0.0196e-3 ≈ **3.33σ**
       Level: EXCLUDED (> 3σ even with maximally aggressive corrections)

  Remaining gap: 2.71%  — outside JUNO 0.81% measurement window.

─────────────────────────────────────────────────────────────────────────
WHAT THIS MEANS
─────────────────────────────────────────────────────────────────────────
The KK tower correction is negligible at TeV scale:

    ε_KK = Δm²₃₁ / M²_KK ≈ 2.3e-3 / (1e12)² ~ 10⁻²¹

so "extra-dimensional sequestration" cannot rescue the 2NLO value by an
amount measurable at current precision.  The gap is structural:

  - The 2NLO T²/Z₃ overlap integrals are ~6.87% below PDG/JUNO.
  - RGE running adds only 0.004% — negligible.
  - Seesaw at PMNS maximum adds 2.67% — reduces tension to 3.33σ.
  - Full closure to < 1% requires WS-V: exact p_R from KK Yukawa
    texture diagonalization, which remains the named open workstream.

Status: HONEST_OPEN_PROBLEM
Machine-readable callable: `juno_2026_falsification_verdict()`

─────────────────────────────────────────────────────────────────────────
IMPORTANT: What is NOT being done here
─────────────────────────────────────────────────────────────────────────
This module does NOT:
  - Introduce any free parameter to make the prediction agree with JUNO
  - Soften the falsification window [2.2, 2.7] × 10⁻³ eV²
  - Promote the projected value to a hardgate claim
  - Invent "extra-dimensional sequestration" as a rescue mechanism

The projected value at PMNS maximum is the honest upper bound on what
the existing corrections can contribute.  Every correction term used
here is derived from named geometric parameters (no fit to JUNO data).

═══════════════════════════════════════════════════════════════════════════

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    # Data anchor
    "JUNO_2026_RELEASE",
    # Constants for the projection chain
    "DM2_31_PDG_EV2",
    "DM2_31_2NLO_EV2",
    "DM2_31_2NLO_RESIDUAL_PCT",
    "M_KK_GEV",
    "Y_TAU",
    "V_HIGGS_GEV",
    "M_R_GEV",
    "THETA_23_DEG",
    "THETA_13_DEG",
    "P_R_PMNS_MAX",
    # Computed projection outputs
    "DELTA_RGE",
    "SEESAW_BASE",
    "DELTA_SEESAW_MAX",
    "DM2_31_PROJECTED_EV2",
    "DM2_31_PROJECTED_RESIDUAL_PCT",
    "JUNO_TENSION_2NLO_SIGMA",
    "JUNO_TENSION_PROJECTED_SIGMA",
    "PILLAR_STATUS",
    "ADMISSION_TAG",
    # Functions
    "rge_running_correction",
    "seesaw_correction_at_p_r",
    "kk_tower_correction_negligible",
    "project_dm31_from_2nlo",
    "juno_2026_falsification_verdict",
    "juno_2026_full_report",
]

# ─────────────────────────────────────────────────────────────────────────
# JUNO 2026 Nature data anchor
# ─────────────────────────────────────────────────────────────────────────

#: JUNO first physics results — Nature, June 10 2026.
#: 59 days of baseline reactor antineutrino data. Normal ordering assumed.
JUNO_2026_RELEASE: Dict = {
    "release": "JUNO First Physics Results (Nature 2026)",
    "year": 2026,
    "reference": (
        "JUNO Collaboration, 'First measurement of Δm²₃₁ with reactor "
        "antineutrinos by JUNO,' Nature (June 10, 2026)"
    ),
    "dm2_31_central_eV2": 2.411e-3,
    "dm2_31_sigma_frac": 0.008125,           # 0.81% fractional 1σ
    "dm2_31_sigma_abs_eV2": 2.411e-3 * 0.008125,  # ≈ 1.959e-5 eV²
    "exposure_days": 59,
    "status": "ACTIVE_TRACKING",
    "note": (
        "Derived from 59 days of baseline reactor antineutrino data. "
        "First sub-1% precision measurement; supersedes PDG 2023 (1.3%) "
        "as the primary experimental anchor for Δm²₃₁ monitoring."
    ),
    "verdicts": {
        "um_2nlo_bare": "EXCLUDED_6.46_SIGMA",
        "um_best_attempt_projection": "EXCLUDED_3.33_SIGMA",
        "overall_pillar17_status": "HONEST_OPEN_PROBLEM",
    },
}

# ─────────────────────────────────────────────────────────────────────────
# Physical constants for the correction chain
# ─────────────────────────────────────────────────────────────────────────

DM2_31_PDG_EV2: float = 2.453e-3
"""PDG 2023 Δm²₃₁ central value [eV²]. Superseded by JUNO 2026 for monitoring."""

DM2_31_2NLO_EV2: float = DM2_31_PDG_EV2 * (1.0 - 0.0687)
"""Pillar 17 2NLO T²/Z₃ prediction [eV²]. ≈ 2.2845 × 10⁻³ eV²."""

DM2_31_2NLO_RESIDUAL_PCT: float = (
    (JUNO_2026_RELEASE["dm2_31_central_eV2"] - DM2_31_2NLO_EV2)
    / JUNO_2026_RELEASE["dm2_31_central_eV2"] * 100.0
)
"""Residual of 2NLO vs JUNO 2026 as percentage of JUNO value. ≈ +5.22%."""

M_KK_GEV: float = 1000.0
"""KK/seesaw scale [GeV]. 1 TeV canonical; from Pillar 274."""

Y_TAU: float = 0.0102
"""τ-lepton Yukawa coupling at M_KK ≈ 1 TeV. Running value from SM RGE."""

V_HIGGS_GEV: float = 246.22
"""Higgs VEV [GeV]."""

M_R_GEV: float = M_KK_GEV
"""Z₂-symmetric Majorana seesaw partner mass [GeV]. Canonical: at KK scale."""

THETA_23_DEG: float = 42.2
"""Atmospheric mixing angle θ₂₃ [degrees]. PDG 2023 NH best fit."""

THETA_13_DEG: float = 8.6
"""Reactor mixing angle θ₁₃ [degrees]. PDG 2023."""

P_R_PMNS_MAX: float = (
    math.sin(math.radians(THETA_23_DEG)) ** 2
    * math.cos(math.radians(THETA_13_DEG)) ** 2
)
"""
PMNS geometric upper bound on seesaw participation factor p_R.

Derived from: p_R^max = sin²θ₂₃ × cos²θ₁₃ ≈ 0.4411.

This bound comes from requiring the rotated seesaw matrix remain within
the PMNS admissible mixing volume. Exact p_R requires Yukawa texture
diagonalization (SEESAW_TEXTURE_PARTICIPATION_GAP, Pillar 274).
"""

# ─────────────────────────────────────────────────────────────────────────
# Pre-computed correction outputs
# ─────────────────────────────────────────────────────────────────────────

def rge_running_correction(
    y_tau: float = Y_TAU,
    m_kk_gev: float = M_KK_GEV,
    dm2_31_ev2: float = DM2_31_2NLO_EV2,
) -> float:
    """
    τ-Yukawa RGE running correction from M_KK down to the atmospheric scale.

    Formula (NLO τ-Yukawa back-reaction):
        δ_RGE = (y_τ² / 8π²) × ln(M_KK × 10⁹ eV / m_atm)

    where m_atm = √Δm²₃₁ is the atmospheric neutrino mass scale [eV].

    The logarithm ratio spans from M_KK ≈ 10¹² eV down to
    m_atm ≈ 4.95 × 10⁻² eV, giving ln ≈ 24.8.

    Sign: positive — Δm²₃₁ runs upward as μ decreases, bringing the
    2NLO estimate slightly closer to the observed value.

    Parameters
    ----------
    y_tau : float
        τ-Yukawa coupling at the KK scale.
    m_kk_gev : float
        KK mass scale [GeV].
    dm2_31_ev2 : float
        Starting Δm²₃₁ value [eV²] (used to extract m_atm).

    Returns
    -------
    float
        Dimensionless correction δ_RGE (multiply by Δm²₃₁ baseline to get eV²).
    """
    m_atm_ev = math.sqrt(dm2_31_ev2)              # eV; depends on dm2_31_ev2 argument
    m_kk_ev = m_kk_gev * 1.0e9                    # GeV → eV
    log_ratio = math.log(m_kk_ev / m_atm_ev)      # ln(M_KK/m_atm) ≈ 25.2
    return (y_tau ** 2) / (8.0 * math.pi ** 2) * log_ratio


def seesaw_correction_at_p_r(
    p_r: float,
    v_gev: float = V_HIGGS_GEV,
    m_r_gev: float = M_R_GEV,
) -> float:
    """
    Kaluza-Klein Majorana seesaw partner correction at participation p_R.

    Formula (leading-order Z₂-symmetric seesaw integrated out near M_KK):
        δ_seesaw(p_R) = p_R × (v / M_R)²

    Physical derivation: A Z₂-symmetric Majorana partner at M_R = M_KK
    contributes to the effective Δm²₃₁ through the seesaw mechanism. The
    full correction magnitude is (v/M_R)² ≈ 6.06%. The participation
    factor p_R ∈ [0, p_R^max] encodes what fraction of the 3×3 Yukawa
    texture actually participates in the atmospheric channel — this is
    the SEESAW_TEXTURE_PARTICIPATION_GAP (exact value requires Yukawa
    texture diagonalization, Pillar 274).

    Sign: positive — partner integrated out adds to the effective
    4D mass splitting in the NH direction.

    Parameters
    ----------
    p_r : float
        Seesaw participation factor. Physical range: [0, P_R_PMNS_MAX].
    v_gev : float
        Higgs VEV [GeV].
    m_r_gev : float
        Majorana partner mass [GeV].

    Returns
    -------
    float
        Dimensionless correction δ_seesaw (multiply by Δm²₃₁ baseline).
    """
    return p_r * (v_gev / m_r_gev) ** 2


def kk_tower_correction_negligible(
    dm2_31_ev2: float = DM2_31_2NLO_EV2,
    m_kk_gev: float = M_KK_GEV,
    n_modes: int = 10,
) -> Dict:
    """
    Demonstrate that the KK tower mixing correction is negligible at TeV scale.

    For a bulk neutrino on T²/Z₃, the off-diagonal KK mixing in the mass
    matrix generates a correction to the effective 4D Δm²₃₁:

        δΔm²₃₁ / Δm²₃₁ ≈ Σ_{n≥1} |c_n|² × (Δm²₃₁ / M²_KK(n))

    where M_KK(n) = n × M_KK and |c_n|² ≤ 1 are wavefunction overlaps.
    For M_KK = 1 TeV and Δm²₃₁ ≈ 2.3 × 10⁻³ eV²:

        ε_KK ≡ Δm²₃₁ / M²_KK = 2.3e-3 / (1e12)² ≈ 2.3 × 10⁻²¹

    The sum is bounded by ε_KK × π²/6 < 4 × 10⁻²¹ — physically
    undetectable. "Extra-dimensional sequestration" cannot rescue the
    2NLO value by any measurable amount at current experimental precision.

    Parameters
    ----------
    dm2_31_ev2 : float
        Δm²₃₁ value [eV²].
    m_kk_gev : float
        First KK mass [GeV].
    n_modes : int
        Number of KK modes to sum (convergence check).

    Returns
    -------
    dict
        Analysis showing the correction magnitude and its ratio to JUNO σ.
    """
    m_kk_ev2 = (m_kk_gev * 1.0e9) ** 2  # M²_KK in eV²
    eps_kk = dm2_31_ev2 / m_kk_ev2      # ε_KK ≈ 2.3e-21

    # Upper-bound sum: assume |c_n|² = 1 for all n (overestimate)
    tower_sum = sum(1.0 / n ** 2 for n in range(1, n_modes + 1))
    correction_upper_bound = eps_kk * tower_sum  # < 4e-21

    juno_sigma_abs = JUNO_2026_RELEASE["dm2_31_sigma_abs_eV2"]
    correction_in_juno_sigma = (correction_upper_bound * dm2_31_ev2) / juno_sigma_abs

    return {
        "epsilon_kk": eps_kk,
        "tower_sum_n_modes": tower_sum,
        "correction_relative_upper_bound": correction_upper_bound,
        "correction_absolute_eV2": correction_upper_bound * dm2_31_ev2,
        "correction_in_juno_sigma": correction_in_juno_sigma,
        "verdict": "NEGLIGIBLE",
        "interpretation": (
            f"KK tower mixing correction ≤ {correction_upper_bound:.2e} "
            f"({correction_in_juno_sigma:.2e} × JUNO σ). "
            "Extra-dimensional sequestration cannot rescue the 2NLO value "
            "at any precision achievable in the next century."
        ),
    }


def project_dm31_from_2nlo(
    p_r: float = P_R_PMNS_MAX,
    include_rge: bool = True,
) -> Dict:
    """
    Apply all known corrections from the 2NLO baseline → best-attempt projection.

    This is the rigorous upper bound on what the existing UM correction
    chain can predict, using p_R at its PMNS geometric maximum and
    including the τ-Yukawa RGE running.  No free parameters are fitted
    to the JUNO data.

    Parameters
    ----------
    p_r : float
        Seesaw participation factor. Default: P_R_PMNS_MAX (maximally
        aggressive, gives the upper bound on the projection).
    include_rge : bool
        Whether to include the τ-Yukawa RGE correction.

    Returns
    -------
    dict
        Full correction chain with intermediate and final values.
    """
    if p_r < 0.0 or p_r > P_R_PMNS_MAX + 1e-10:
        raise ValueError(
            f"p_r={p_r:.4f} outside physical range [0, {P_R_PMNS_MAX:.4f}]"
        )

    delta_rge = rge_running_correction() if include_rge else 0.0
    delta_seesaw = seesaw_correction_at_p_r(p_r)
    total_correction = delta_rge + delta_seesaw

    dm31_proj = DM2_31_2NLO_EV2 * (1.0 + total_correction)

    # Tensions
    juno_central = JUNO_2026_RELEASE["dm2_31_central_eV2"]
    juno_sigma = JUNO_2026_RELEASE["dm2_31_sigma_abs_eV2"]
    tension_proj = abs(dm31_proj - juno_central) / juno_sigma
    residual_pct = (juno_central - dm31_proj) / juno_central * 100.0

    return {
        "dm31_2nlo_baseline_eV2": DM2_31_2NLO_EV2,
        "delta_rge": delta_rge,
        "delta_seesaw": delta_seesaw,
        "p_r_used": p_r,
        "p_r_pmns_max": P_R_PMNS_MAX,
        "total_correction": total_correction,
        "dm31_projected_eV2": dm31_proj,
        "juno_central_eV2": juno_central,
        "residual_pct": residual_pct,
        "tension_sigma": tension_proj,
        "in_falsification_window": 2.2e-3 <= dm31_proj <= 2.7e-3,
        "status": (
            "EXCLUDED" if tension_proj > 3.0 else
            "MARGINAL" if tension_proj > 2.0 else
            "CONSISTENT"
        ),
        "note": (
            f"Best-attempt projection at p_R={p_r:.4f} (PMNS max). "
            f"Residual gap {residual_pct:.2f}% from JUNO. "
            f"Tension {tension_proj:.2f}σ. "
            "Exact p_R requires WS-V KK Yukawa texture diagonalization."
        ),
    }


def juno_2026_falsification_verdict() -> Dict:
    """
    Machine-readable falsification verdict for Pillar 17 vs JUNO 2026.

    Computes:
      1. Tension of bare 2NLO value vs JUNO 2026.
      2. Tension of best-attempt projection vs JUNO 2026.
      3. KK tower correction magnitude (shown to be negligible).
      4. Overall status and named open-workstream closure path.

    Returns
    -------
    dict
        Structured falsification verdict with all intermediate computations.
    """
    juno_central = JUNO_2026_RELEASE["dm2_31_central_eV2"]
    juno_sigma = JUNO_2026_RELEASE["dm2_31_sigma_abs_eV2"]

    # Tension of bare 2NLO vs JUNO
    tension_bare = abs(DM2_31_2NLO_EV2 - juno_central) / juno_sigma

    # Best-attempt projection
    proj = project_dm31_from_2nlo(p_r=P_R_PMNS_MAX)

    # KK tower (negligible)
    kk_tower = kk_tower_correction_negligible()

    # Overall status
    overall_status = "HONEST_OPEN_PROBLEM"
    closure_path = (
        "WS-V: full KK Yukawa texture diagonalization to derive exact p_R "
        "from first principles. If p_R > P_R_PMNS_MAX is required, the "
        "seesaw architecture is disfavored and a deeper geometric closure "
        "path (full 6D+ orbifold treatment) is the next step."
    )

    return {
        "pillar": 525,
        "title": "JUNO_2026_FALSIFICATION_RESPONSE",
        "juno_data": JUNO_2026_RELEASE,
        "um_2nlo_bare": {
            "dm31_eV2": DM2_31_2NLO_EV2,
            "tension_sigma": tension_bare,
            "level": "EXCLUDED",
            "verdict": f"EXCLUDED at {tension_bare:.2f}σ — bare 2NLO value",
        },
        "um_best_attempt_projection": proj,
        "kk_tower_analysis": kk_tower,
        "overall_status": overall_status,
        "admission_tag": "JUNO_2026_P17_EXCLUDED",
        "closure_path": closure_path,
        "fallibility_section": "§XV (FALLIBILITY.md)",
        "machine_readable": {
            "bare_tension_sigma": tension_bare,
            "projected_tension_sigma": proj["tension_sigma"],
            "residual_gap_pct": proj["residual_pct"],
            "in_falsification_window_bare": 2.2e-3 <= DM2_31_2NLO_EV2 <= 2.7e-3,
            "in_falsification_window_proj": proj["in_falsification_window"],
            "status": overall_status,
        },
    }


def juno_2026_full_report() -> Dict:
    """
    Complete human-readable + machine-readable report for JUNO 2026 event.

    Returns
    -------
    dict
        Full structured report with narrative summary and all numerics.
    """
    verdict = juno_2026_falsification_verdict()
    bare_tension = verdict["um_2nlo_bare"]["tension_sigma"]
    proj_tension = verdict["um_best_attempt_projection"]["tension_sigma"]
    proj_dm31 = verdict["um_best_attempt_projection"]["dm31_projected_eV2"]
    residual = verdict["um_best_attempt_projection"]["residual_pct"]

    narrative = (
        f"JUNO First Physics Results (Nature, June 10 2026) measure "
        f"Δm²₃₁ = {JUNO_2026_RELEASE['dm2_31_central_eV2']:.4e} eV² "
        f"(σ = {JUNO_2026_RELEASE['dm2_31_sigma_frac']*100:.2f}%) "
        f"from {JUNO_2026_RELEASE['exposure_days']} days of data.\n\n"
        f"UM Pillar 17 2NLO bare prediction: {DM2_31_2NLO_EV2:.4e} eV². "
        f"Tension: {bare_tension:.2f}σ. Level: EXCLUDED.\n\n"
        f"Best-attempt projection (RGE + seesaw at p_R={P_R_PMNS_MAX:.4f} PMNS max): "
        f"{proj_dm31:.4e} eV². "
        f"Tension: {proj_tension:.2f}σ. Level: EXCLUDED. "
        f"Residual gap: {residual:.2f}%.\n\n"
        f"KK tower correction: NEGLIGIBLE (ε_KK ≈ 2.3 × 10⁻²¹ at 1 TeV).\n\n"
        f"Status: HONEST_OPEN_PROBLEM. Closure path: WS-V full Yukawa texture "
        f"diagonalization to derive exact p_R from KK geometry."
    )

    return {
        "version": "v17.1",
        "pillar": 525,
        "event_date": "2026-06-10",
        "narrative_summary": narrative,
        "verdict": verdict,
        "corrections_applied": {
            "rge_tau_yukawa": rge_running_correction(),
            "seesaw_at_pmns_max": seesaw_correction_at_p_r(P_R_PMNS_MAX),
            "kk_tower": "NEGLIGIBLE (< 10⁻²⁰)",
        },
        "open_workstream": "WS-V: KK Yukawa texture diagonalization",
        "fallibility_ref": "FALLIBILITY.md §XV",
    }


# ─────────────────────────────────────────────────────────────────────────
# Module-level pre-computed values (used in __all__ exports)
# ─────────────────────────────────────────────────────────────────────────

DELTA_RGE: float = rge_running_correction()
"""τ-Yukawa RGE correction δ_RGE ≈ 4.04 × 10⁻⁵."""

SEESAW_BASE: float = (V_HIGGS_GEV / M_R_GEV) ** 2
"""Bare seesaw correction (v/M_R)² ≈ 0.0606 = 6.06%."""

DELTA_SEESAW_MAX: float = seesaw_correction_at_p_r(P_R_PMNS_MAX)
"""Max seesaw correction at PMNS bound ≈ 0.02674 = 2.674%."""

DM2_31_PROJECTED_EV2: float = DM2_31_2NLO_EV2 * (1.0 + DELTA_RGE + DELTA_SEESAW_MAX)
"""Best-attempt projected Δm²₃₁ [eV²] ≈ 2.3457 × 10⁻³ eV²."""

DM2_31_PROJECTED_RESIDUAL_PCT: float = (
    (JUNO_2026_RELEASE["dm2_31_central_eV2"] - DM2_31_PROJECTED_EV2)
    / JUNO_2026_RELEASE["dm2_31_central_eV2"] * 100.0
)
"""Residual gap of projected value vs JUNO 2026 [%]. ≈ 2.71%."""

JUNO_TENSION_2NLO_SIGMA: float = (
    abs(DM2_31_2NLO_EV2 - JUNO_2026_RELEASE["dm2_31_central_eV2"])
    / JUNO_2026_RELEASE["dm2_31_sigma_abs_eV2"]
)
"""Tension of bare 2NLO vs JUNO 2026 [σ]. ≈ 6.46σ."""

JUNO_TENSION_PROJECTED_SIGMA: float = (
    abs(DM2_31_PROJECTED_EV2 - JUNO_2026_RELEASE["dm2_31_central_eV2"])
    / JUNO_2026_RELEASE["dm2_31_sigma_abs_eV2"]
)
"""Tension of best-attempt projection vs JUNO 2026 [σ]. ≈ 3.33σ."""

PILLAR_STATUS: str = "HONEST_OPEN_PROBLEM"
"""Machine-readable overall Pillar 525 status."""

ADMISSION_TAG: str = "JUNO_2026_P17_EXCLUDED"
"""Admission tag for FALLIBILITY.md §XV cross-reference."""
