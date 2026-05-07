# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 218 — Architecture Limits Registry (Track A, Session 1).

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════
This module is the single authoritative catalog of **Architecture Limits**
in the Unitary Manifold RS1/5D framework.

An ARCHITECTURE_LIMIT is a gap that is:
  1. Quantifiably bounded from within the 5D ansatz.
  2. Provably irreducible to zero *within* RS1/5D.
  3. Formally traceable to a specific higher-dimensional requirement.

This registry distinguishes architecture limits from:
  - SCAFFOLD gaps (parameterized; potentially closable in 5D)
  - OPEN gaps (unexplored; may or may not require higher D)
  - DERIVED quantities (closed — no gap)

DESIGN PHILOSOPHY
-----------------
  - Every limit is labeled with REQUIRES_DIMENSION: the minimum extra
    dimensions needed to close it.
  - Every limit has a REDUCTION_ACHIEVED: how many orders/factors the UM
    already reduces the naive gap.
  - The registry is machine-readable and callable from the completeness
    audit (Pillar 219 / rs1_5d_completeness_audit.py).
  - No limits are hidden. If it is outside the 5D domain, it says so.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

__all__ = [
    # Data structures
    "ARCHITECTURE_LIMIT_REGISTRY",
    # Functions
    "get_limit",
    "list_limits",
    "limits_by_dimension",
    "limits_summary",
    "architecture_limits_report",
    "count_by_status",
]

# ─────────────────────────────────────────────────────────────────────────────
# CORE CONSTANTS (inputs only: no SM seeds)
# ─────────────────────────────────────────────────────────────────────────────

_N_W: int = 5
_K_CS: int = 74
_PI_KR: float = 37.0
_M_PL_GEV: float = 1.22e19
_M_KK_GEV: float = _M_PL_GEV * math.exp(-_PI_KR)

# ─────────────────────────────────────────────────────────────────────────────
# ARCHITECTURE LIMIT REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

#: Machine-readable catalog of all RS1/5D architecture limits.
#: Each entry key is a short identifier; value is a dict with:
#:   - pillar          : Pillar number(s) that established this limit
#:   - module          : src/core/ module file(s)
#:   - gap_description : what the gap is
#:   - naive_gap       : the gap before any UM reduction (order-of-magnitude)
#:   - reduction_achieved : how many orders the UM reduces it
#:   - residual_gap    : remaining gap after UM reductions
#:   - requires_dimension : minimum new dimensions to close residual
#:   - requires_mechanism : specific mechanism or theory needed
#:   - honest_status   : ARCHITECTURE_LIMIT (5D domain exhausted) or
#:                       OPEN (needs more 5D work first)
#:   - falsification   : what experimental result would change this label
ARCHITECTURE_LIMIT_REGISTRY: Dict[str, Dict[str, object]] = {

    # ─── A-1 Cosmological Constant ──────────────────────────────────────────
    "A-1_cosmological_constant": {
        "pillar": 206,
        "module": "src/core/pillar206_cosmological_constant.py",
        "gap_description": (
            "The observed vacuum energy density Λ_obs ≈ 2.9×10⁻¹²² M_Pl⁴ "
            "vs the naive UV estimate M_Pl⁴.  RS1 warp suppression reduces "
            "the estimate to M_KK⁴ ≈ exp(−148) M_Pl⁴ ≈ 10⁻⁶⁴ M_Pl⁴.  "
            "Gauss-Bonnet + Casimir partial cancellation leaves a residual.  "
            "The remaining 58-order gap cannot be closed in 5D RS1."
        ),
        "naive_gap_log10": 122.0,
        "reduction_achieved_log10": 64.0,     # RS1 warp suppression
        "residual_gap_log10": 58.0,           # after all 5D mechanisms
        "requires_dimension": 10,             # string landscape / 10D SUGRA
        "requires_mechanism": (
            "Bousso-Polchinski flux landscape (10D) or Weinberg anthropic "
            "selection.  11D SUGRA has Λ_SUGRA = 0; small positive Λ requires "
            "quantum string vacuum selection from O(10⁵⁰⁰) landscape states."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "A detection of Λ consistent with zero (de Sitter → flat or AdS "
            "transition) would change the observational target but not remove "
            "the need for a higher-dimensional landscape mechanism."
        ),
    },

    # ─── A-2 Strong Force Coupling α_s (warp-anchor gap) ───────────────────
    "A-2_strong_coupling_warp_anchor": {
        "pillar": 200,
        "module": "src/core/pillar200_rge_geometric.py",
        "gap_description": (
            "The pure-geometric AxiomZero forward chain gives "
            "α_s(M_EW_geo) ≈ 0.030 vs PDG α_s(M_Z) = 0.118.  "
            "Factor ~4 gap (the 'warp-anchor gap').  "
            "KK threshold corrections from the tower (Pillar 219) reduce it "
            "toward factor ~2-3 in 5D, but the full perturbative matching "
            "to the 3-flavor QCD β-function requires integrating out 6 "
            "compact CY₃ dimensions at the M_GUT scale."
        ),
        "naive_gap_factor": 4.0,
        "reduction_achieved_factor": 1.5,    # from KK threshold corrections
        "residual_gap_factor": 2.5,
        "requires_dimension": 10,            # CY₃ KK mode sum
        "requires_mechanism": (
            "Full Calabi-Yau threefold KK threshold corrections at M_GUT. "
            "The sum over CY₃ KK modes with Hodge number h₁₁ ≈ 37 (= N_flux) "
            "contributes Δα_s ≈ α_s² × b_1/(2π) × ln(M_GUT/M_KK) per mode, "
            "summing to ≈ factor 2-3 correction.  This requires 10D geometry."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "LHC precision measurement of α_s(M_Z) deviating from 0.118 toward "
            "0.030 would change the residual gap.  A 5D geometric mechanism "
            "that non-perturbatively generates the remaining factor without CY₃ "
            "would remove this limit."
        ),
    },

    # ─── A-3 Fermion Mass Hierarchy (lighter generations) ──────────────────
    "A-3_fermion_mass_hierarchy_light_generations": {
        "pillar": "205, 183",
        "module": (
            "src/core/pillar205_generation_quantization.py, "
            "src/core/fermion_cl_quantization.py"
        ),
        "gap_description": (
            "Integer quantization c_L = m/n_w correctly identifies the "
            "generation STRUCTURE (3 families, O(1) mass ratios for top/bottom) "
            "but fails for lighter generations: m=4 → 25-50× off for muon/strange, "
            "m=5 → 5 orders off for electron.  The c_L spectrum is CONTINUOUS in "
            "RS1/5D (Pillar 174); exact c_L values for the 2nd and 3rd generation "
            "require 6D orbifold geometry to fix the 3 discrete fixed-point "
            "wavefunctions."
        ),
        "naive_gap_factor": 5e5,       # electron mass from naive c_L=1
        "reduction_achieved_factor": 2,  # top/bottom close to within O(1)
        "residual_gap_factor": 5e5,    # for electron specifically
        "requires_dimension": 6,
        "requires_mechanism": (
            "6D T²/Z₃ orbifold: each of the 3 fixed points of Z₃ acting on T² "
            "hosts one fermion generation zero-mode.  The wave function overlap "
            "at each fixed point is discrete (not continuous in c_L), giving exact "
            "mass ratios from the modular forms of T²/Z₃."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "Discovery of a 4th fermion generation would falsify the 3-fixed-point "
            "mechanism entirely.  Precision measurement of c_L ≡ m/n_w exactly "
            "for the muon would confirm the integer quantization and remove this limit."
        ),
    },

    # ─── A-4 CP Violation / Jarlskog Invariant ─────────────────────────────
    "A-4_cp_violation_jarlskog": {
        "pillar": "188, 208",
        "module": (
            "src/core/ckm_cp_subleading.py, "
            "src/core/pillar208_braid_lock_pmns.py"
        ),
        "gap_description": (
            "The braid-lock CKM gives sin²θ₁₂, sin²θ₂₃, sin²θ₁₃ all within 5%, "
            "but the CP-violating phase δ_CP ≈ 1.2 rad (Jarlskog J ≈ 3×10⁻⁵) "
            "requires a non-trivial geometric mechanism.  The leading braid harmonic "
            "gives δ_CP from k_CS/4π correction; the next-order correction (Pillar 220) "
            "closes the gap to ~12%.  Full closure requires discrete torsion in the "
            "6D orbifold H¹(T²/Z₃, U(1)) which cannot be generated in 5D."
        ),
        "naive_gap_fraction": 1.0,       # δ_CP completely undetermined in pure 5D
        "reduction_achieved_fraction": 0.88,  # braid corrections get 88% right
        "residual_gap_fraction": 0.12,   # 12% Jarlskog residual
        "requires_dimension": 6,
        "requires_mechanism": (
            "Discrete torsion in H¹(T²/Z₃, U(1)).  The CP phase arises from the "
            "Aharonov-Bohm phase of fermions transported around the 3 fixed points "
            "of T²/Z₃.  The phase is topologically quantized and gives δ_CP = π/3 "
            "or 2π/3 from first principles (Asaka, Buchmuller, Covi 2001 mechanism)."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "A future precise measurement of δ_CP inconsistent with the braid "
            "prediction would require a different CP mechanism.  If δ_CP → 0 "
            "(CP conservation in quarks) the discrete torsion mechanism is ruled out."
        ),
    },

    # ─── A-5 GW Strain Detection Gap ───────────────────────────────────────
    "A-5_gw_strain_detection": {
        "pillar": "199",
        "module": "src/core/gw_polarization_constraints.py",
        "gap_description": (
            "The UM predicts KK-graviton GW signals from braid oscillations.  "
            "The characteristic strain h_c from the 5D geometry at LIGO band (10-1000 Hz) "
            "is ~22 orders of magnitude below LIGO sensitivity (h < 10⁻²¹).  "
            "This is not a failure — it is the correct physics: the KK mass "
            "m_KK ~ M_Pl × exp(-37) places the signal at energies orders of "
            "magnitude above the LIGO band.  Detecting the UM GW signature "
            "requires a space-based detector operating near the Planck scale, "
            "which is not an architecture of currently conceivable technology."
        ),
        "naive_gap_log10": 22.0,         # orders below LIGO sensitivity
        "reduction_achieved_log10": 0.0,  # no reduction possible in 5D
        "residual_gap_log10": 22.0,
        "requires_dimension": None,       # Not a dimensional issue — technology limit
        "requires_mechanism": (
            "Planck-scale GW detector (not a dimensional extension).  "
            "Alternatively, a cosmological stochastic GW background from "
            "inflationary KK production could be detectable at LISA frequencies "
            "— Pillar 73 (kk_stochastic_gw.py) places this at h² Ω_GW ~ 10⁻¹⁵ "
            "at f ~ 10⁻³ Hz, marginally within LISA reach."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "LISA detection of a stochastic GW background at h² Ω_GW ~ 10⁻¹⁵ "
            "at mHz frequencies would be consistent with UM KK production.  "
            "Non-detection below this level would constrain the KK sector."
        ),
    },

    # ─── A-6 Neutrino Dirac Yukawa y_D ─────────────────────────────────────
    "A-6_neutrino_dirac_yukawa": {
        "pillar": "190, 192",
        "module": (
            "src/core/neutrino_winding.py, "
            "src/core/neutrino_symmetry.py"
        ),
        "gap_description": (
            "The UV-brane localization of RHN (Pillar 190) derives M_R ~ M_Pl "
            "from the inverted (7,5) braid geometry.  The Majorana mass scale is "
            "DERIVED.  The Dirac Yukawa coupling y_D = O(1) is NOT derived — it "
            "is the overlap integral of UV-brane RHN profile with IR-brane "
            "Higgs, which requires knowing the exact fermion zero-mode profile "
            "shape in the 5D bulk.  In RS1, this is c_L-dependent and remains "
            "parameterized until c_L is derived (see A-3)."
        ),
        "naive_gap_factor": float("inf"),  # y_D completely free in 5D
        "reduction_achieved_factor": 1.0,
        "residual_gap_factor": float("inf"),
        "requires_dimension": 6,
        "requires_mechanism": (
            "6D fermion zero-mode profile at T²/Z₃ fixed points.  In 6D, "
            "the overlap integral <f_L|H|f_R> is fixed by the positions of "
            "the fixed points on T², giving y_D from geometry."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "A 5D derivation of y_D from the braid action alone (without c_L as "
            "free parameter) would remove this limit.  Measurement of y_D ≠ O(1) "
            "at the LHC (e.g., leptoquark couplings) would constrain it."
        ),
    },

    # ─── A-7 Gauge Unification Group ───────────────────────────────────────
    "A-7_gauge_unification_group": {
        "pillar": "113",
        "module": "src/core/m_theory_embedding.py",
        "gap_description": (
            "The UM derives the QCD color factor N_c = 3 from n_w = 5 (Pillars 39+67) "
            "and the U(1)_Y coupling from the warp factor.  However, the full "
            "SM gauge group SU(3)×SU(2)×U(1) as a specific subgroup of a GUT "
            "group (SU(5) or E₈) cannot be derived purely from 5D RS1 geometry.  "
            "The identification of the 5D KK gauge fields with the SM gauge bosons "
            "requires embedding in E₈×E₈ (heterotic) or SO(32) (Type I), which "
            "lives in 10D."
        ),
        "naive_gap_factor": None,        # categorical: group theory, not a number
        "reduction_achieved_log10": None,
        "residual_gap_log10": None,
        "requires_dimension": 10,
        "requires_mechanism": (
            "10D heterotic E₈×E₈ compactified on CY₃.  The SM gauge group arises "
            "from the commutant of the holonomy group SU(3) inside E₈.  "
            "The G₄ flux quantization N_flux = 37 (= k_CS/2, Pillar 113) selects "
            "the CY₃ that gives the correct gauge group — this is the connection "
            "already identified in m_theory_embedding.py."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "Discovery of a 4th color charge or a 4th weak isospin partner "
            "would rule out the SU(3)×SU(2) subgroup identification.  "
            "A direct measurement of the GUT group at colliders would determine "
            "whether E₈ or SU(5) is the correct embedding."
        ),
    },

    # ─── A-8 Proton Decay Rate ──────────────────────────────────────────────
    "A-8_proton_decay_rate": {
        "pillar": "55",
        "module": "src/core/proton_decay.py",
        "gap_description": (
            "The UM predicts proton stability from the topological conservation "
            "of the winding number (Pillar 55).  The specific proton decay rate "
            "Γ(p → e⁺π⁰) requires knowing the dimension-6 operator coefficients "
            "from the GUT gauge boson exchange, which requires a 10D action.  "
            "The 5D framework gives M_X ~ M_KK as the GUT boson mass, giving "
            "τ_p ~ M_X⁴/m_p⁵ which is in the right ballpark but not precisely derivable "
            "without the 10D gauge group structure."
        ),
        "naive_gap_factor": 100.0,      # ~100× uncertainty in τ_p
        "reduction_achieved_factor": 10.0,
        "residual_gap_factor": 10.0,
        "requires_dimension": 10,
        "requires_mechanism": (
            "10D GUT gauge group structure to fix the dimension-6 proton decay "
            "operator coefficients.  The specific branching ratios require knowing "
            "the Clebsch-Gordan coefficients of the 10D GUT gauge group."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "Hyper-K or JUNO detection of proton decay.  If τ_p < 10³⁴ years "
            "in p → e⁺π⁰ mode, the UM estimate is in range.  Non-detection "
            "above 10³⁵ years constrains M_X > 10¹⁶ GeV, consistent with UM."
        ),
    },

    # ─── A-9 Supersymmetry / SUSY Breaking ─────────────────────────────────
    "A-9_supersymmetry_breaking": {
        "pillar": None,
        "module": None,
        "gap_description": (
            "The UM has no SUSY sector.  The 5D RS1 ansatz uses a bosonic "
            "action (Einstein-Hilbert + Goldberger-Wise + CS).  Supersymmetry "
            "requires equal numbers of bosonic and fermionic degrees of freedom "
            "at each energy scale, which requires a 10D supergravity embedding.  "
            "The UM's resolution of the hierarchy problem (Higgs VEV from warp "
            "factor) is the RS1 mechanism, not SUSY — but in 10D/11D, RS1 and "
            "SUSY are not independent (Hořava-Witten)."
        ),
        "naive_gap_factor": None,
        "reduction_achieved_log10": None,
        "residual_gap_log10": None,
        "requires_dimension": 11,
        "requires_mechanism": (
            "11D SUGRA (Cremmer-Julia-Scherk 1978).  The Hořava-Witten "
            "compactification on S¹/Z₂ connects 11D SUGRA to the UM's 5D sector.  "
            "N=1 SUSY in 4D emerges automatically from the CY₃ compactification."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "LHC or FCC discovery of superpartners at any mass scale would "
            "require incorporating SUSY into the UM, forcing the 10D/11D extension.  "
            "Non-observation of SUSY at all accessible scales is consistent with "
            "the UM's non-SUSY 5D structure."
        ),
    },

    # ─── A-10 Dark Energy w_a ≠ 0 ──────────────────────────────────────────
    "A-10_dark_energy_wa": {
        "pillar": 160,
        "module": "src/core/kk_axion_quintessence.py",
        "gap_description": (
            "The UM predicts w_a = 0 (frozen EW radion: m_r >> H₀).  "
            "DESI DR2 CPL fit prefers w_a = −0.62 ± 0.30 (2.1σ tension).  "
            "Exhaustive search (Pillar 160) found no viable 5D mechanism for w_a ≠ 0: "
            "all KK modes are too heavy for coherent quintessence.  Explaining "
            "a time-varying w requires a light scalar whose mass is set by H₀, "
            "which is not geometrically natural in 5D RS1 without fine-tuning."
        ),
        "naive_gap_factor": None,
        "reduction_achieved_log10": None,
        "residual_tension_sigma": 2.1,
        "requires_dimension": 6,         # moduli of compact space can be light
        "requires_mechanism": (
            "6D+ moduli fields (Kähler or complex structure moduli of T²/Z₃).  "
            "The Kähler modulus of the compact T² can be naturally light if its "
            "stabilization is delayed, giving w_a ≠ 0 quintessence without "
            "fine-tuning.  This is the 'runaway quintessence' mechanism."
        ),
        "honest_status": "ARCHITECTURE_LIMIT",
        "falsification": (
            "Nancy Grace Roman Space Telescope (~2027) σ(w_a) ≈ 0.10.  "
            "If w_a measured consistent with zero (|w_a| < 0.2), UM prediction "
            "is confirmed and this limit is removed.  If |w_a| > 0.3 at 3σ, "
            "the 5D DE sector is falsified."
        ),
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_limit(key: str) -> Dict[str, object]:
    """Return the registry entry for a given architecture limit key.

    Parameters
    ----------
    key :
        One of the ARCHITECTURE_LIMIT_REGISTRY keys (e.g. 'A-1_cosmological_constant').

    Returns
    -------
    dict
        Registry entry.  Raises KeyError if key not found.
    """
    return ARCHITECTURE_LIMIT_REGISTRY[key]


def list_limits() -> List[str]:
    """Return the list of all architecture limit keys."""
    return list(ARCHITECTURE_LIMIT_REGISTRY.keys())


def limits_by_dimension(dimension: int) -> List[str]:
    """Return architecture limit keys that require the given dimension.

    Parameters
    ----------
    dimension :
        Minimum extra dimension required to close the limit (e.g. 6, 10, 11).

    Returns
    -------
    list of str
        Keys of limits that require exactly ``dimension``.
    """
    return [
        k for k, v in ARCHITECTURE_LIMIT_REGISTRY.items()
        if v.get("requires_dimension") == dimension
    ]


def count_by_status(status: str = "ARCHITECTURE_LIMIT") -> int:
    """Count limits with a given honest_status.

    Parameters
    ----------
    status :
        Status string to filter by (default: 'ARCHITECTURE_LIMIT').
    """
    return sum(
        1 for v in ARCHITECTURE_LIMIT_REGISTRY.values()
        if v.get("honest_status") == status
    )


def limits_summary() -> Dict[str, object]:
    """Return a concise summary of the architecture limits registry.

    Returns
    -------
    dict
        Keys: total, by_dimension, architecture_limit_count, open_count.
    """
    total = len(ARCHITECTURE_LIMIT_REGISTRY)
    arch_count = count_by_status("ARCHITECTURE_LIMIT")
    open_count = count_by_status("OPEN")

    by_dim: Dict[Optional[int], int] = {}
    for v in ARCHITECTURE_LIMIT_REGISTRY.values():
        d = v.get("requires_dimension")
        by_dim[d] = by_dim.get(d, 0) + 1

    return {
        "total_limits": total,
        "architecture_limit_count": arch_count,
        "open_count": open_count,
        "by_dimension": by_dim,
        "limit_keys": list_limits(),
    }


def architecture_limits_report() -> Dict[str, object]:
    """Full machine-readable report for the architecture limits registry.

    Returns
    -------
    dict with keys:
        ``version``, ``framework``, ``registry``, ``summary``,
        ``five_d_domain_statement``.
    """
    return {
        "version": "v10.5",
        "framework": "RS1/5D Kaluza-Klein (Unitary Manifold)",
        "registry": ARCHITECTURE_LIMIT_REGISTRY,
        "summary": limits_summary(),
        "five_d_domain_statement": (
            "The RS1/5D framework exhausts its predictive reach at the following "
            "boundaries.  Every quantity in this registry is either formally bounded "
            "('naive_gap_factor' or 'naive_gap_log10' fields) or categorically "
            "outside the 5D domain ('requires_dimension > 5').  "
            "The framework does NOT attempt to derive these quantities from 5D — "
            "that would be dishonest.  Instead it documents the precise boundary "
            "and the specific higher-dimensional mechanism required."
        ),
        "genuine_5d_achievements": [
            "nₛ ≈ 0.9635 (DERIVED — Planck 0.33σ)",
            "r_braided ≈ 0.0315 (DERIVED — BICEP/Keck ✓)",
            "k_CS = 74 (ALGEBRAICALLY DERIVED from (5,7) braid)",
            "β ≈ 0.331° (DERIVED — awaits LiteBIRD 2032)",
            "Λ_QCD ≈ 198 MeV (DERIVED from AdS/QCD, 5D geometry only)",
            "M_p/M_e ratio (DERIVED — 0.6% residual)",
            "Higgs VEV ≈ 246 GeV (GEOMETRIC PREDICTION — 4.6%)",
            "N_c = 3 (DERIVED from n_w = 5)",
            "n_w = 5 uniqueness (PURE THEOREM — Pillar 70-D)",
            "w_KK ≈ −0.930 (GEOMETRIC PREDICTION — DESI DR2 0.11σ)",
            "sin²θ₁₂, sin²θ₂₃, sin²θ₁₃ (BRAID-LOCK — all <5%)",
        ],
    }
