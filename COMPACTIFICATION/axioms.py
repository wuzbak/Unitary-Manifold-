#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
COMPACTIFICATION/axioms.py
==========================
Machine-readable axiom registry for the Unitary Manifold.

Every axiom that the framework rests on is declared here as a Python
dataclass.  The kernel imports this module; it stands alone as a
complete epistemic map of the foundational layer.

Epistemic labels (per docs/CLAIM_LABEL_STANDARD.md):
    POSTULATED          — assumed, not derived from anything deeper
    DERIVED             — follows from stated axioms by explicit algebra
    PROVED              — formally derived; executable certificate exists
    PROVED_CONDITIONAL  — proved given a named upstream axiom
    CONJECTURAL         — plausible but not formally established
    ARCHITECTURE_LIMIT  — open gap that is a known limit of the 5D ansatz
    FITTED              — calibrated to external data (honest label)

Usage
-----
    from axioms import AXIOM_REGISTRY, AxiomStatus
    for ax in AXIOM_REGISTRY:
        print(ax.name, ax.status.value)

Theory: ThomasCory Walker-Pearson (2026)
Code:   GitHub Copilot (AI)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------------------------
# Epistemic status enum
# ---------------------------------------------------------------------------

class AxiomStatus(Enum):
    POSTULATED          = "POSTULATED"
    DERIVED             = "DERIVED"
    PROVED              = "PROVED"
    PROVED_CONDITIONAL  = "PROVED_CONDITIONAL"
    CONJECTURAL         = "CONJECTURAL"
    ARCHITECTURE_LIMIT  = "ARCHITECTURE_LIMIT"
    FITTED              = "FITTED"


# ---------------------------------------------------------------------------
# Axiom dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Axiom:
    """One foundational assumption or derived result."""
    name: str                        # Short machine-readable tag
    label: str                       # Human display label
    statement: str                   # One-sentence mathematical statement
    status: AxiomStatus              # Epistemic label
    lean4_ref: Optional[str]         # Lean4 file if formally proved
    fallibility_note: str            # Honest gap / caveat
    pillars: List[int] = field(default_factory=list)  # Pillar numbers that depend on this


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

AXIOM_REGISTRY: List[Axiom] = [

    # ------------------------------------------------------------------
    # Layer 0 — Geometric foundation
    # ------------------------------------------------------------------
    Axiom(
        name="A0_MANIFOLD",
        label="5D KK Manifold",
        statement=(
            "Spacetime is a smooth 5D Kaluza–Klein manifold M₄ × S¹/Z₂ "
            "with compact extra dimension of radius R₀."
        ),
        status=AxiomStatus.POSTULATED,
        lean4_ref=None,
        fallibility_note=(
            "The smoothness assumption excludes topology change and string-scale "
            "corrections.  S¹/Z₂ is chosen over other compact spaces by the "
            "uniqueness theorem (Pillar 74), but that theorem is conditional on "
            "this ansatz."
        ),
        pillars=list(range(1, 209)),
    ),

    Axiom(
        name="A1_METRIC",
        label="5D Metric Ansatz",
        statement=(
            "The 5D metric takes the KK block form "
            "G_AB = [[g_μν + λ²φ²B_μB_ν, λφB_μ], [λφB_ν, φ²]] "
            "with G₅₅ = φ², the radion scalar."
        ),
        status=AxiomStatus.DERIVED,
        lean4_ref="lean4/UnitaryManifold/P8FunctionalFull.lean",
        fallibility_note=(
            "Block form is derived from 5D Einstein–Hilbert stationarity + "
            "KK gauge covariance + Z₂ orbifold parity + radion normalization. "
            "Executable certificate: src/core/metric_ansatz_derivation.py. "
            "Conditional on A0_MANIFOLD."
        ),
        pillars=[1, 2, 3],
    ),

    Axiom(
        name="A2_FIELD_EQS",
        label="Walker–Pearson Field Equations",
        statement=(
            "The 4D dynamics of (g_μν, B_μ, φ) are the projection of the 5D "
            "Einstein equations under the A1_METRIC ansatz."
        ),
        status=AxiomStatus.DERIVED,
        lean4_ref=None,
        fallibility_note=(
            "Standard KK reduction; the ADM (lapse/shift) treatment is an open gap. "
            "Flow parameter t and coordinate time x⁰ are related but not formally "
            "synchronized in the current 1D spatial reduction.  "
            "See FALLIBILITY.md §III (ADM gap)."
        ),
        pillars=[2, 5, 6],
    ),

    # ------------------------------------------------------------------
    # Layer 1 — Topological selection
    # ------------------------------------------------------------------
    Axiom(
        name="A3_BRAID_PAIR",
        label="(5,7) Braid Pair",
        statement=(
            "The topological sector of the compact dimension is characterized "
            "by the integer pair (n₁, n₂) = (5, 7), giving "
            "k_CS = n₁² + n₂² = 74."
        ),
        status=AxiomStatus.PROVED,
        lean4_ref="lean4/UnitaryManifold/ShadowPairKCSFormal.lean",
        fallibility_note=(
            "k_CS = 74 is derived from the Chern–Simons level of the 5D action. "
            "The (5,7) pair is the unique minimizer of |β(k) − 0.35°| for "
            "k ∈ [1,100]; this birefringence anchor uses the observational hint "
            "(Minami & Komatsu 2020), which carries ~3σ significance. "
            "LiteBIRD (~2032) is the primary falsifier."
        ),
        pillars=[39, 67, 70, 74],
    ),

    Axiom(
        name="A4_NW5",
        label="Winding Number n_w = 5",
        statement=(
            "The dominant KK winding mode is n_w = 5, selected uniquely over "
            "n_w = 7 by the Z₂ APS boundary condition: "
            "k_CS(5) × η̄(5) = 37 (odd ✓), k_CS(7) × η̄(7) = 0 (even ✗)."
        ),
        status=AxiomStatus.PROVED,
        lean4_ref="lean4/UnitaryManifold/NPW5APS.lean",
        fallibility_note=(
            "Proved from 5D CS action + APS theorem in Pillar 70-D. "
            "Axiom A (Z₂-odd CS boundary phase = −1) is itself DERIVED "
            "from the 5D CS action (not postulated). "
            "Planck nₛ confirms at 0.33σ."
        ),
        pillars=[67, 70],
    ),

    Axiom(
        name="A5_AXIOM_A",
        label="Z₂-Odd CS Boundary Phase",
        statement=(
            "The Chern–Simons boundary phase on the S¹/Z₂ orbifold is "
            "exp(iπ k_CS η̄) = −1 (odd), encoding SM chirality."
        ),
        status=AxiomStatus.DERIVED,
        lean4_ref="lean4/UnitaryManifold/OrbifoldBCUniqueness.lean",
        fallibility_note=(
            "Derived from 5D CS action + Z₂-odd G_{μ5} → APS theorem. "
            "Callable proof: axiom_a_derived_from_cs_action() in "
            "src/core/nw5_pure_theorem.py.  ~15 tests."
        ),
        pillars=[70],
    ),

    Axiom(
        name="A6_SWAMPLAND",
        label="Swampland Axiom SW",
        statement=(
            "The winding number satisfies n_w ≤ 15 (Swampland distance "
            "conjecture applied to compact KK dimension)."
        ),
        status=AxiomStatus.POSTULATED,
        lean4_ref="lean4/UnitaryManifold/SwamplandAxiom.lean",
        fallibility_note=(
            "An IRREDUCIBLE_POSTULATE: cannot be derived from the 5D geometric "
            "axioms alone.  It constrains the search space to {n_w ≤ 15}; "
            "within that space n_w = 5 is uniquely selected by A4_NW5. "
            "24 proxy theorems formalise this in SwamplandAxiom.lean."
        ),
        pillars=[],
    ),

    # ------------------------------------------------------------------
    # Layer 2 — Physical identifications
    # ------------------------------------------------------------------
    Axiom(
        name="A7_PHI_ENTROPY",
        label="φ = Entanglement Capacity",
        statement=(
            "The 5D radion scalar φ is identified with the entanglement "
            "capacity of the compact dimension."
        ),
        status=AxiomStatus.CONJECTURAL,
        lean4_ref=None,
        fallibility_note=(
            "Physical identification only — not derived from QFT first principles. "
            "Supports the arrow-of-time narrative but is not required for the "
            "topological predictions (nₛ, r, β)."
        ),
        pillars=[4, 5, 9],
    ),

    Axiom(
        name="A8_5TH_DIM_IRREV",
        label="5th Dimension = Irreversibility",
        statement=(
            "The compact extra dimension encodes physical irreversibility; "
            "the flow parameter in the field equations is identified with "
            "thermodynamic time."
        ),
        status=AxiomStatus.CONJECTURAL,
        lean4_ref=None,
        fallibility_note=(
            "Conjectural identification.  A full ADM 3+1 treatment with lapse "
            "and shift is required to make this rigorous.  The ADM gap is a "
            "documented open problem (FALLIBILITY.md §III)."
        ),
        pillars=[6, 7, 8],
    ),

    Axiom(
        name="A9_FTUM",
        label="FTUM Operator U = I + H + T",
        statement=(
            "The universe-ensemble dynamics are governed by the operator "
            "U = I (irreversibility) + H (holography) + T (topology), "
            "and a fixed point Ψ* exists with U Ψ* = Ψ*."
        ),
        status=AxiomStatus.POSTULATED,
        lean4_ref=None,
        fallibility_note=(
            "The operator decomposition is postulated; the fixed-point "
            "existence is proved numerically (Banach contraction, "
            "analytic certificate in fixed_point.py) given the decomposition."
        ),
        pillars=[5, 29, 38],
    ),

    Axiom(
        name="A10_HOLOGRAPHY",
        label="Holographic Entropy–Area Relation",
        statement="S = A / 4G at every holographic boundary.",
        status=AxiomStatus.POSTULATED,
        lean4_ref=None,
        fallibility_note=(
            "Assumed standard AdS/CFT; not derived from the 5D metric ansatz. "
            "Used in the H operator of FTUM and in Pillar 4."
        ),
        pillars=[4, 5],
    ),

    # ------------------------------------------------------------------
    # Layer 3 — Derived predictions
    # ------------------------------------------------------------------
    Axiom(
        name="P1_NS",
        label="CMB Spectral Index nₛ",
        statement=(
            "nₛ = 1 − 6ε + 2η ≈ 0.9635, derived from the KK Jacobian "
            "J = n_w · 2π · √φ₀ and the Goldberger–Wise potential."
        ),
        status=AxiomStatus.PROVED_CONDITIONAL,
        lean4_ref=None,
        fallibility_note=(
            "Conditional on A0–A4.  Agrees with Planck 2018 (0.9649 ± 0.0042) "
            "at 0.33σ.  Falsified if future nₛ measurement lands outside "
            "[0.952, 0.977]."
        ),
        pillars=[57, 63],
    ),

    Axiom(
        name="P2_R",
        label="Tensor-to-Scalar Ratio r",
        statement=(
            "r_braided = r_bare × c_s = 16ε × (12/37) ≈ 0.0315; "
            "below BICEP/Keck 95% CL (r < 0.036)."
        ),
        status=AxiomStatus.PROVED_CONDITIONAL,
        lean4_ref=None,
        fallibility_note=(
            "Conditional on A3_BRAID_PAIR.  r = r_bare × c_s is exact for the "
            "(5,7) Pythagorean braid (no truncation).  "
            "Falsified if BICEP/Keck establishes r > 0.036."
        ),
        pillars=[39, 57],
    ),

    Axiom(
        name="P3_BETA",
        label="CMB Birefringence β",
        statement=(
            "β ≈ 0.331° (canonical FTUM primary) or 0.351° (GW-radion variant); "
            "inside the Minami & Komatsu 1σ hint (0.35° ± 0.14°)."
        ),
        status=AxiomStatus.DERIVED,
        lean4_ref=None,
        fallibility_note=(
            "k_CS = 74 was derived independently from β ≈ 0.35° AND from the "
            "braid topology — this independence is essential.  The birefringence "
            "hint carries ~3σ significance.  Primary falsifier: LiteBIRD (~2032). "
            "Any β outside [0.22°, 0.38°] or in the predicted gap [0.29°–0.31°] "
            "falsifies the braided-winding mechanism."
        ),
        pillars=[68],
    ),

    Axiom(
        name="P4_ALPHA_GUT",
        label="GUT Fine-Structure Constant α_GUT",
        statement=(
            "α_GUT = N_c / k_CS = 3/74 ≈ 0.04054, from the SU(N_c) "
            "Chern–Simons Dirac quantization condition."
        ),
        status=AxiomStatus.DERIVED,
        lean4_ref="lean4/UnitaryManifold/AlphaGUTDerivation.lean",
        fallibility_note=(
            "1.7% residual to the SU(5) GUT value; < 0.5% with Casimir correction. "
            "CS quantization is the derivation mechanism; SU(N_c) vs U(1) "
            "normalization factor is N_c²/(2π)."
        ),
        pillars=[153, 173],
    ),

    Axiom(
        name="P5_LAMBDA_QCD",
        label="QCD Scale Λ_QCD (geometric path)",
        statement=(
            "Λ_QCD ≈ 197.7–209 MeV derived from geometry alone: "
            "n_w=5 → N_c=3 → M_KK → AdS/QCD hard-wall → m_ρ → Λ_QCD."
        ),
        status=AxiomStatus.DERIVED,
        lean4_ref=None,
        fallibility_note=(
            "Zero SM RGE input; zero free parameters. "
            "Factor ~1.68 vs PDG MS-bar (332 MeV) is the known soft-wall "
            "AdS/QCD systematic (Erlich et al. 2005).  NLO backreaction moves "
            "result to ~209 MeV (−1.7% from PDG 213 MeV)."
        ),
        pillars=[182],
    ),

    Axiom(
        name="P6_HIGGS",
        label="Higgs Mass (one-loop)",
        statement=(
            "M_H ≈ 126.2 GeV at one-loop, from KK threshold corrections "
            "to the Higgs self-energy."
        ),
        status=AxiomStatus.DERIVED,
        lean4_ref=None,
        fallibility_note=(
            "ONE_LOOP_CONSISTENT (within ~1% of 125.09 GeV PDG).  "
            "A 27.53% irreducible Higgs gap remains at 5D; labeled "
            "ARCHITECTURE_LIMIT at the 5D KK level. "
            "Full naturalness requires 6D/Hosotani mechanism (Pillars 705–709), "
            "which achieves NATURAL but at ARCHITECTURE_LIMIT_CERTIFIED."
        ),
        pillars=[705, 706, 707, 708],
    ),

    Axiom(
        name="P7_YUKAWA",
        label="Yukawa / CKM / PMNS",
        statement=(
            "Fermion mass hierarchies are reproduced by Froggatt–Nielsen "
            "localisation parameters c_L in the orbifold bulk."
        ),
        status=AxiomStatus.FITTED,
        lean4_ref="lean4/UnitaryManifold/YukawaSVDClosure.lean",
        fallibility_note=(
            "The c_L values are solved by root-finding against known experimental "
            "masses — they are NOT derived top-down from (5,7) topology. "
            "Pillar 677 makes progress via orbifold BCs but residual <1.3% still "
            "requires external mass input for calibration.  "
            "'Zero free parameters' applies only to the topological sector. "
            "9→3 irreducible FN parameters remain (Pillar 774)."
        ),
        pillars=[677, 772, 773, 784],
    ),

    Axiom(
        name="P8_DARK_ENERGY",
        label="Dark Energy EoS w_KK",
        statement=(
            "The KK radion predicts w_KK ≈ −0.9302 (w₀ = −1 + (2/3)ε_KK); "
            "w_a = 0 (no time evolution)."
        ),
        status=AxiomStatus.DERIVED,
        lean4_ref=None,
        fallibility_note=(
            "w_KK ≈ −0.9302: DESI DR2 0.1σ [PASS]; Planck+BAO 3.2σ [TENSION]; "
            "DES Y3 1.2σ.  DESI Year 2 tension on w_a ≠ 0 vs KK prediction "
            "w_a = 0 is an open tracked tension.  See docs/CLAIM_MASTER_BOARD.md."
        ),
        pillars=[],
    ),

    # ------------------------------------------------------------------
    # Layer 4 — Known open gaps
    # ------------------------------------------------------------------
    Axiom(
        name="G1_CMB_AMPLITUDE",
        label="CMB Peak Amplitude Gap",
        statement=(
            "The CMB power spectrum amplitude is suppressed ×4–7 at acoustic "
            "peaks relative to Planck data."
        ),
        status=AxiomStatus.ARCHITECTURE_LIMIT,
        lean4_ref=None,
        fallibility_note=(
            "Documented in FALLIBILITY.md Admission 2.  Addressed by Pillars "
            "57+63 (partial decomposition).  A 33.65% irreducible gap remains "
            "at the 5D KK architecture level (DECOMPOSED_V2).  "
            "Not a falsification of the topological predictions (nₛ, r, β) "
            "but is a genuine limitation of the current framework."
        ),
        pillars=[52, 57, 63],
    ),

    Axiom(
        name="G2_ADM",
        label="ADM Time Synchronisation Gap",
        statement=(
            "The flow parameter t and coordinate time x⁰ are not formally "
            "synchronised; a full ADM 3+1 decomposition is absent."
        ),
        status=AxiomStatus.ARCHITECTURE_LIMIT,
        lean4_ref=None,
        fallibility_note=(
            "MECHANISM_IDENTIFIED (Pillar 41 provides first-order correction "
            "Ω(φ) = 1/φ).  Full ADM treatment remains an open problem. "
            "See FALLIBILITY.md §III."
        ),
        pillars=[41],
    ),

    Axiom(
        name="G3_DM21_TENSION",
        label="Δm²₂₁ Neutrino Mass Tension",
        statement=(
            "The solar neutrino mass splitting Δm²₂₁ shows a residual "
            "~1.07σ tension after NLO lattice corrections."
        ),
        status=AxiomStatus.ARCHITECTURE_LIMIT,
        lean4_ref=None,
        fallibility_note=(
            "Three NLO mechanisms (winding + KK threshold + BKT) reduce tension "
            "1.16σ → 1.07σ.  Gate: NLO_INSUFFICIENT_FOR_SUB_1SIGMA. "
            "Classified ARCHITECTURE_LIMIT_CERTIFIED (Pillar 774)."
        ),
        pillars=[772, 773, 774],
    ),
]


# ---------------------------------------------------------------------------
# Convenience accessors
# ---------------------------------------------------------------------------

def axiom_by_name(name: str) -> Optional[Axiom]:
    """Return the axiom with the given name, or None."""
    for ax in AXIOM_REGISTRY:
        if ax.name == name:
            return ax
    return None


def axioms_by_status(status: AxiomStatus) -> List[Axiom]:
    """Return all axioms with the given epistemic status."""
    return [ax for ax in AXIOM_REGISTRY if ax.status == status]


def summary_table() -> str:
    """Return a human-readable summary table of the axiom registry."""
    lines = [
        f"{'Name':<25} {'Status':<22} {'Lean4':<5}",
        "-" * 55,
    ]
    for ax in AXIOM_REGISTRY:
        lean4 = "yes" if ax.lean4_ref else "no"
        lines.append(f"{ax.name:<25} {ax.status.value:<22} {lean4:<5}")
    lines.append(f"\nTotal: {len(AXIOM_REGISTRY)} entries")
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary_table())
    print()
    # Honesty check: count the postulated/conjectural items
    postulated = axioms_by_status(AxiomStatus.POSTULATED)
    conjectural = axioms_by_status(AxiomStatus.CONJECTURAL)
    arch_limits = axioms_by_status(AxiomStatus.ARCHITECTURE_LIMIT)
    print(f"POSTULATED  (assumed, not derived): {len(postulated)}")
    print(f"CONJECTURAL (plausible, not proved): {len(conjectural)}")
    print(f"ARCH LIMITS (open gaps):             {len(arch_limits)}")
