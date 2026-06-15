# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Pillar 394 — Postulate Minimality Audit
Epistemological Deep Audit — v12.9

Provides a machine-readable inventory of every postulate, named Admission, and
free parameter on which the Unitary Manifold rests.  Three outputs:

1. CANONICAL POSTULATE REGISTRY — structured records for all P1–P8 core
   postulates, Admissions 1–13, and all free parameters.  Each record carries:
   name, status, breaks_if_fails, and citation.

2. COMPLETENESS CHECK — verifies that every claim labelled DERIVED in the
   canonical claim set has at least one documented postulate dependency in the
   registry.  A DERIVED claim with no known postulate chain is a documentation
   gap, not a real derivation.

3. MINIMALITY CHECK — flags any postulate that does not appear in the
   dependency chain of any DERIVED result.  A postulate that no result depends
   on is either redundant or mislabelled.

Epistemic status: EPISTEMOLOGICAL_INFRASTRUCTURE — this module does not make
physics claims; it audits whether existing claims have properly documented
postulate dependencies.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


# ──────────────────────────────────────────────────────────────────────────────
# Status taxonomy
# ──────────────────────────────────────────────────────────────────────────────

class PostulateStatus(str, Enum):
    POSTULATED      = "POSTULATED"        # Core axiom; not derivable from below.
    DERIVED         = "DERIVED"           # Follows from other postulates via proof.
    ARCHITECTURE_LIMIT = "ARCHITECTURE_LIMIT"  # Framework boundary; closed by design.
    CONVENTION      = "CONVENTION"        # Normalisation or labelling choice.
    OPEN_GAP        = "OPEN_GAP"          # Acknowledged gap; not yet resolved.


class PostulateKind(str, Enum):
    CORE_POSTULATE  = "CORE_POSTULATE"    # P1–P8 foundational axioms.
    ADMISSION       = "ADMISSION"         # Named honest admission.
    FREE_PARAMETER  = "FREE_PARAMETER"    # Numerical input not derived from axioms.


# ──────────────────────────────────────────────────────────────────────────────
# Registry record
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PostulateRecord:
    """A single entry in the canonical postulate registry."""
    name: str
    kind: PostulateKind
    status: PostulateStatus
    description: str
    breaks_if_fails: str           # What collapses if this is wrong.
    citation: str                  # Canonical source: pillar / module / document.
    used_by: List[str] = field(default_factory=list)   # DERIVED results that depend on this.
    closed_by: Optional[str] = None   # Pillar that closed or narrowed the gap.

    @property
    def label(self) -> str:
        return self.name

    @property
    def is_open(self) -> bool:
        return self.status == PostulateStatus.OPEN_GAP


# ──────────────────────────────────────────────────────────────────────────────
# Canonical registry — Core Postulates P1–P8
# ──────────────────────────────────────────────────────────────────────────────

CORE_POSTULATES: List[PostulateRecord] = [
    PostulateRecord(
        name="P1: Z₂ orbifold structure (S¹/Z₂)",
        kind=PostulateKind.CORE_POSTULATE,
        status=PostulateStatus.POSTULATED,
        description=(
            "The compact fifth dimension is the orbifold S¹/Z₂.  This involution "
            "y→−y selects the Z₂-even zero-mode spectrum, imposes Neumann BCs on "
            "even fields, and forces Dirichlet BCs on Z₂-odd fields.  It is the "
            "starting-point topological assumption."
        ),
        breaks_if_fails="All KK mode selection, Z₂-parity arguments, and Pillars 39/67/70-B/70-C/70-D.",
        citation="src/core/solitonic_charge.py (Pillar 39); 1-THEORY/DERIVATION_STATUS.md Part II",
        used_by=[
            "n_w ∈ {5,7}", "η̄(5)=½", "n_w=5 pure theorem", "N_gen=3",
            "SU(3)×SU(2)×U(1)", "k_CS=74", "c_s=12/37",
        ],
    ),
    PostulateRecord(
        name="P2: 5D KK metric block ansatz",
        kind=PostulateKind.CORE_POSTULATE,
        status=PostulateStatus.DERIVED,
        description=(
            "The 5D metric takes the Kaluza-Klein block form G_AB with off-diagonal "
            "G_{μ5}=λφB_μ and G_{55}=φ².  Now DERIVED_CONDITIONAL via Pillar 344: "
            "RS1 + CSS uniqueness theorem + diffeomorphism invariance fix the lowest-"
            "order local block form; remaining input is Λ₅<0 from AdS₅ bulk."
        ),
        breaks_if_fails="All field equations, KK reduction, B_μ interpretation, arrow of time.",
        citation=(
            "src/core/metric.py; src/core/metric_ansatz_derivation.py; "
            "Pillar 344 / src/core/pillar344_metric_ansatz_conditional_derivation.py; "
            "Pillar 384 / src/core/pillar384_metric_ansatz_uniqueness.py"
        ),
        closed_by="Pillar 344 (CONDITIONAL_DERIVATION); Pillar 384 (DERIVED_UNIQUE at NLO < 0.74%)",
        used_by=[
            "Walker-Pearson field equations", "Arrow of time", "α_NM",
            "B_μ gauge invariance", "All CMB/inflation predictions",
        ],
    ),
    PostulateRecord(
        name="P3: B_μ as irreversibility 1-form",
        kind=PostulateKind.CORE_POSTULATE,
        status=PostulateStatus.POSTULATED,
        description=(
            "The off-diagonal KK gauge field B_μ is physically identified with the "
            "geometric source of irreversibility.  H_μν=∂_μB_ν−∂_νB_μ drives "
            "entropy production.  This is a physical interpretation of the "
            "mathematical structure, not derived from a deeper principle."
        ),
        breaks_if_fails="Arrow-of-time claim; interpretation of entropy production as geometric.",
        citation="src/core/evolution.py; 1-THEORY/DERIVATION_STATUS.md Part I",
        used_by=["Arrow of time (DERIVED conditional on P3)", "Entropy production σ≥0"],
    ),
    PostulateRecord(
        name="P4: Goldberger-Wise double-well potential",
        kind=PostulateKind.CORE_POSTULATE,
        status=PostulateStatus.POSTULATED,
        description=(
            "The radion stabilisation potential takes the GW form V_GW=λ_GW(φ²−φ₀²)². "
            "This is a motivated choice from RS1 literature; other potentials (CW, KKLT) "
            "are not excluded.  The stabilisation mechanism is geometric; λ_GW is a "
            "free parameter (see Admission 6)."
        ),
        breaks_if_fails="Radion stabilisation; inflaton potential shape; nₛ/r predictions.",
        citation="src/core/evolution.py (FieldState); src/core/goldberger_wise.py (Pillar 68)",
        used_by=["φ₀ stabilisation", "Inflation plateau", "Chirality derivation (Pillar 70-C)"],
    ),
    PostulateRecord(
        name="P5: FTUM fixed-point operator U = I+H+T",
        kind=PostulateKind.CORE_POSTULATE,
        status=PostulateStatus.POSTULATED,
        description=(
            "The holographic fixed-point operator U maps network states via "
            "U=I+H+T and has a unique fixed point Ψ* satisfying S=A/(4G).  "
            "The analogy with imaginary-time Schrödinger evolution e^{−Hτ/ℏ} "
            "is physical motivation, not a theorem."
        ),
        breaks_if_fails="FTUM convergence; φ₀ self-consistency; dark energy cosmological constant.",
        citation="src/multiverse/fixed_point.py; Pillar 309",
        used_by=[
            "φ₀_bare=1 (FTUM → φ₀ bridge, Pillar 56-B)",
            "Holographic S=A/4G (Pillar 379, DERIVED_CONDITIONAL)",
            "FTUM basin contraction (Pillar 309, physical regime)",
        ],
    ),
    PostulateRecord(
        name="P6: Holographic entropy S=A/4G at FTUM fixed point",
        kind=PostulateKind.CORE_POSTULATE,
        status=PostulateStatus.DERIVED,
        description=(
            "The Bekenstein-Hawking relation S*=A/(4G_N^{4D}) holds at the FTUM "
            "fixed point.  Now DERIVED_CONDITIONAL via Pillar 379: the FTUM S* "
            "equals A/(4G) exactly at the fixed point, derived from the 5D "
            "Gauss-Bonnet reduction.  Assumption: standard AdS/CFT bulk geometry."
        ),
        breaks_if_fails=(
            "Holographic bound; KK back-reaction closure; neutrino-radion identity; "
            "dark energy via braid-suppressed vacuum energy."
        ),
        citation="src/holography/boundary.py; Pillar 379 / src/core/pillar379_holographic_entropy_derivation.py",
        closed_by="Pillar 379 (DERIVED_CONDITIONAL; ASSUMED → DERIVED in v12.6)",
        used_by=["FTUM S*=A/4G", "KK back-reaction (Pillar 72)", "Neutrino-radion identity"],
    ),
    PostulateRecord(
        name="P7: Minimum-step braid assignment n₁=n_w, n₂=n_w+2",
        kind=PostulateKind.CORE_POSTULATE,
        status=PostulateStatus.DERIVED,
        description=(
            "The braid partner n₂ = n₁ + 2 = 7 follows from the minimum-step "
            "Dirichlet BC quantization on S¹/Z₂.  Now DERIVED_STRUCTURAL via "
            "Pillar 377: Δn=2 from Dirichlet quantization + δ²S_E>0 stability. "
            "P8 postulate status upgraded: POSTULATED → DERIVED."
        ),
        breaks_if_fails="k_CS=74; c_s=12/37; r_braided=0.0315; all braid-derived predictions.",
        citation="Pillar 377 / src/core/pillar377_p8_braid_stability_proof.py",
        closed_by="Pillar 377 (DERIVED_STRUCTURAL)",
        used_by=["k_CS=74", "c_s=12/37", "r_braided=0.0315", "β∈{0.273°,0.331°}"],
    ),
    PostulateRecord(
        name="P8: Minimum-step braid stability",
        kind=PostulateKind.CORE_POSTULATE,
        status=PostulateStatus.DERIVED,
        description=(
            "The (5,7) braid pair is the energetically stable minimum-step "
            "configuration.  Derived in Pillar 377 via Euclidean action second "
            "variation δ²S_E>0 confirming stability of the (n_w, n_w+2) saddle."
        ),
        breaks_if_fails="Same as P7: all braid-derived predictions.",
        citation="Pillar 377 / src/core/pillar377_p8_braid_stability_proof.py",
        closed_by="Pillar 377 (POSTULATED → DERIVED_STRUCTURAL in v12.6)",
        used_by=["(5,7) uniqueness", "k_CS=74 algebraic", "c_s=12/37"],
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Admissions 1–6 (from §3.2 of FALLIBILITY.md) + 11–13 (v12.9 formal additions)
# ──────────────────────────────────────────────────────────────────────────────

ADMISSIONS: List[PostulateRecord] = [
    PostulateRecord(
        name="Admission 1: n_w=5 observationally selected within constrained set",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.OPEN_GAP,
        description=(
            "The topological argument (Pillars 39, 67, 70-B, 70-D) narrows n_w to "
            "{5,7}; Planck nₛ=0.9649 then selects n_w=5 at 0.33σ vs n_w=7 at 3.9σ.  "
            "The APS Z₂-odd CS phase (Pillar 70-D) independently selects n_w=5 "
            "from pure geometry without Planck data.  The geometric selection is "
            "DERIVED; the Planck confirmation is OBSERVATIONALLY_SELECTED.  Both "
            "are documented; neither is hidden."
        ),
        breaks_if_fails="All predictions built on n_w=5.",
        citation="FALLIBILITY.md §3.2 Admission 1; src/core/nw5_pure_theorem.py (Pillar 70-D)",
        closed_by="Pillar 70-D (geometric selection; n_w=5 now PURE_THEOREM from Z₂-odd CS boundary phase)",
        used_by=["All n_w=5 derived results"],
    ),
    PostulateRecord(
        name="Admission 2: k_CS=74 algebraically derived from braid pair",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.DERIVED,
        description=(
            "k_eff = n₁²+n₂² is an algebraic identity (Pillar 58). "
            "For (n₁,n₂)=(5,7): k_CS=25+49=74 with zero free parameters. "
            "Status: DERIVED from 5D CS action integral (Pillar 99-B). "
            "Previously ASSERTED."
        ),
        breaks_if_fails="k_CS=74; all birefringence/CMB predictions.",
        citation="FALLIBILITY.md §3.2 Admission 2; src/core/anomaly_closure.py (Pillars 58, 99-B)",
        closed_by="Pillar 99-B (DERIVED from CS integral)",
        used_by=["k_CS=74", "β∈{0.273°,0.331°}", "c_s=12/37"],
    ),
    PostulateRecord(
        name="Admission 3: r=0.097 (bare) tension resolved via braiding",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.DERIVED,
        description=(
            "Bare r=96/φ₀_eff²≈0.097 exceeded BICEP/Keck bound r<0.036. "
            "Resolved by (5,7) braiding: r_braided=r_bare×c_s≈0.0315. "
            "G_{μ5} Z₂-odd derivation (Pillar 387) FORMALLY CLOSES Admission 3: "
            "n_w=5 chain COMPLETE at classical level from 5D EH action."
        ),
        breaks_if_fails="r prediction; BICEP/Keck compliance.",
        citation="FALLIBILITY.md §3.2 Admission 3; src/core/pillar387_z2_odd_gmu5_derivation.py (P387)",
        closed_by="Pillar 387 (ADMISSION_3_FORMALLY_CLOSED; CONVENTION → DERIVED_FROM_5D_LAGRANGIAN)",
        used_by=["r_braided=0.0315", "BICEP/Keck consistency"],
    ),
    PostulateRecord(
        name="Admission 4: φ₀ self-consistency closed analytically",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.DERIVED,
        description=(
            "Three candidate φ₀ values previously differed by ~5%.  Pillar 56 "
            "proves they collapse to a single fixed point under the c_s-corrected "
            "slow-roll formula.  Status: CLOSED analytically."
        ),
        breaks_if_fails="φ₀ self-consistency; all slow-roll predictions.",
        citation="FALLIBILITY.md §3.2 Admission 4; src/core/phi0_closure.py (Pillar 56)",
        closed_by="Pillar 56 (CLOSED analytically)",
        used_by=["φ₀=1 Planck unit", "nₛ=0.9635", "r_braided=0.0315"],
    ),
    PostulateRecord(
        name="Admission 5: r_braided=r_bare×c_s now derived (Pillar 97-B)",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.DERIVED,
        description=(
            "The tensor suppression factor c_s is now DERIVED from 5D CS→4D WZW "
            "kinetic rotation (Pillar 97-B).  Residual: tree-level WZW; loop "
            "corrections O(ρ/4π)²≈2% — sub-leading."
        ),
        breaks_if_fails="r_braided value; BICEP/Keck consistency.",
        citation="FALLIBILITY.md §3.2 Admission 5; src/core/braided_winding.py::braided_r_full_derivation()",
        closed_by="Pillar 97-B (DERIVED via WZW reduction)",
        used_by=["r_braided=0.0315"],
    ),
    PostulateRecord(
        name="Admission 6: λ_GW (Goldberger-Wise coupling) is a free parameter",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.DERIVED,
        description=(
            "Pillar 404 (v13.1) CLOSES Admission 6: ν_GW = n_w/K_CS = 5/74 from the "
            "braid quantization condition uniquely identifies the GW bulk mass parameter.  "
            "This gives α_φ = √(8ν) ≈ 0.735 and m_φ = α_φ M_KK ≈ 765 GeV.  "
            "λ_GW = α_φ² M_KK²/(8φ₀²) is now derived, not fitted.  "
            "DEPENDENCY NOTE (v13.0): Admission 11 chains back to Admission 6 "
            "through T_RH: the reheating temperature depends on the KK decay rate "
            "which involves λ_GW.  Once λ_GW is fixed (naturally by m_φ ~ M_KK), "
            "T_RH is determined and N_e closes (Pillar 404 derives T_RH ≈ 3.7×10⁸ GeV "
            "→ N_e ≈ 66 within Planck-consistent range).  Admission 11 cascades CLOSED."
        ),
        breaks_if_fails=(
            "Radion mass scale (m_φ~M_KK qualitative result remains; exact mass undefined). "
            "Does NOT break n_w selection or CMB predictions."
        ),
        citation=(
            "FALLIBILITY.md §3.2 (referenced 'see Admission 6 below') and §4.6; "
            "src/core/pillar404_lambda_gw_derivation.py (Pillar 404); "
            "src/core/goldberger_wise.py (Pillar 68); "
            "DERIVATION_STATUS.md Part II (n_w=5 from APS spin structure)"
        ),
        closed_by="Pillar 404 (DERIVED_FROM_GW_NORMALIZATION; ν_GW=n_w/K_CS braid identification)",
        used_by=[
            "Radion mass scale (qualitative)",
            "GW chirality argument (any λ_GW≠0)",
            "Admission 11 (N_e conditional on λ_GW via T_RH)",
        ],
    ),
    # ── v12.9 additions — Admissions 11, 12, 13 ──
    # ── v13.0 additions — Admissions 7, 10 (formally named) ──
    PostulateRecord(
        name="Admission 7: Jarlskog invariant absolute value (ARCHITECTURE_LIMIT_MAPPED)",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.ARCHITECTURE_LIMIT,
        description=(
            "Pillar 402 (v13.1) maps the architecture limit precisely.  "
            "The Jarlskog invariant J = Im(V_us V_cb V_ub* V_cs*) requires "
            "non-integer c_L bulk-mass parameters.  Pillar 398 (integer lattice scan) "
            "confirmed: minimum residual > 15% for all integer assignments.  "
            "Pillar 402 (continuous scan) finds the exact non-integer target: "
            "(Δℓ₁₂ ≈ 1.390, Δℓ₂₃ ≈ 0.665) reproduces J_PDG within 0.02%.  "
            "Required LKT correction δ_KT ≈ 0.053 (NATURAL, < 10%).  "
            "FN charge identification: n_FN = Δℓ.  "
            "Status: ARCHITECTURE_LIMIT_MAPPED — the exact target is now quantified; "
            "the closing mechanism (localized kinetic term correction) is specified."
        ),
        breaks_if_fails="Absolute Jarlskog invariant value J_PDG ≈ 3.08e-5.",
        citation=(
            "FALLIBILITY.md §XIII Admission 7; "
            "Pillar 398 / src/core/pillar398_jarlskog_lattice_scan.py (integer scan); "
            "Pillar 402 / src/core/pillar402_jarlskog_continuous_scan.py (continuous map)"
        ),
        closed_by="Pillar 402 (ARCHITECTURE_LIMIT_MAPPED — target quantified; δ_KT≈0.053 specified)",
        used_by=["CKM Jarlskog invariant J", "CP violation in kaon/B sector"],
    ),
    PostulateRecord(
        name="Admission 10: LHC KK resonance constraints (CONSTRAINED_BOUNDED)",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.ARCHITECTURE_LIMIT,
        description=(
            "Pillar 403 (v13.1) derives the B_μ gauge mixing suppression.  "
            "The UM metric ansatz g_μν + φ² B_μ B_ν introduces mixed graviton-gauge "
            "kinetic term at leading order in φ².  Suppression factor for gluon→G_KK: "
            "(1 + φ₀² k²/M_KK²)⁻¹ ≈ 0.998.  The corrected σ_gluon/σ_benchmark "
            "ratio is precisely bounded: ratio ≥ 0.61 (conservative).  "
            "KK mass lower bound from LHC di-jet limits: m_G_KK ≥ 1.8 TeV at 95% CL.  "
            "Fermion channels remain SAFE (c₁_eff ≈ 8×10⁻⁴ << 0.1).  "
            "Status: CONSTRAINED_BOUNDED — exact suppression factor derived; "
            "exact exclusion limit stated.  Gluon channel remains in tension."
        ),
        breaks_if_fails=(
            "If m_G_KK < 1.8 TeV were observed (no resonance seen above this), "
            "the UM KK spectrum would be excluded."
        ),
        citation=(
            "FALLIBILITY.md §XIII Admission 10; "
            "Pillar 399 / src/core/pillar399_lhc_kkgraviton_crosssection.py (CONSTRAINED_QUANTIFIED); "
            "Pillar 403 / src/core/pillar403_bmu_gauge_correction.py (CONSTRAINED_BOUNDED)"
        ),
        closed_by="Pillar 403 (CONSTRAINED_BOUNDED — B_μ suppression derived; m_G_KK ≥ 1.8 TeV lower bound)",
        used_by=["LHC KK graviton di-jet/di-lepton predictions", "KK mass spectrum"],
    ),

    PostulateRecord(
        name="Admission 11: 60 e-folds is a standard assumption, not derived",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.DERIVED,
        description=(
            "Pillar 404 (v13.1) CLOSES Admission 11: λ_GW is now derived "
            "(Admission 6 closed) → m_φ ≈ 765 GeV → T_RH ≈ 3.7×10⁸ GeV → "
            "N_e ≈ 66 within the Planck-consistent range [47, 72].  "
            "The N_e chain is now fully derived from geometry.  "
            "Prior status (v13.0): CONDITIONALLY_CLOSED given Adm. 6 "
            "(Pillar 400: N_e ∈ [55,65] observationally benign at <1σ Planck)."
        ),
        breaks_if_fails=(
            "CMB predictions nₛ=0.9635 and r=0.0315 would shift if N_e differs. "
            "A 10% change in N_e shifts nₛ by ~0.002 — within Planck 1σ but "
            "resolvable by CMB-S4 (Δnₛ~0.002 precision)."
        ),
        citation=(
            "FALLIBILITY.md §4.3 (prose gap, now formally named); "
            "Pillar 346 / src/core/pillar346_ne_kk_thermalization.py (partial closure); "
            "Pillar 400 / src/core/pillar400_ne_sensitivity_closure.py (sensitivity + conditional closure); "
            "Pillar 404 / src/core/pillar404_lambda_gw_derivation.py (CLOSES via λ_GW derivation)"
        ),
        closed_by="Pillar 404 (CLOSED: λ_GW derived → T_RH → N_e chain complete)",
        used_by=["nₛ=0.9635", "r_braided=0.0315", "All CMB slow-roll predictions"],
    ),
    PostulateRecord(
        name="Admission 12: FTUM basin completeness — analytic proof open",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.DERIVED,
        description=(
            "Pillar 405 (v13.1) CLOSES Admission 12: the FTUM contraction mapping "
            "is extended from L² (minisuperspace) to the Sobolev space H¹(Ω) by "
            "adding gradient energy E_grad = ∫|∇φ|² dy to the norm.  The Sobolev "
            "embedding theorem proves ||T(φ+δφ)−T(φ)||_{H¹} ≤ L||δφ||_{H¹} with "
            "L < 1 for bounded-gradient perturbations.  KK graviton energy cross-check "
            "confirms δE_G_KK << E_basin (Pillar 399 coupling).  The minisuperspace "
            "caveat is resolved.  "
            "Prior status (v13.0): CONTRACTIVE_IN_ORBIFOLD_BASIN (Pillar 401)."
        ),
        breaks_if_fails=(
            "If a physically accessible initial state does not converge to Ψ*, "
            "the FTUM uniqueness claim is invalid for that initial state.  "
            "The existing 192-sample numerical evidence would remain valid; "
            "only the universal claim would be weakened."
        ),
        citation=(
            "FALLIBILITY.md §4.3 (prose, 'Convergence for all physically reasonable "
            "initial conditions has not been proven analytically'); "
            "Pillar 309 / src/core/pillar309_ftum_contractive_regime_cert.py; "
            "Pillar 401 / src/core/pillar401_ftum_basin_geometric_bound.py (orbifold basin); "
            "Pillar 405 / src/core/pillar405_sobolev_ftum_extension.py (H¹ closure)"
        ),
        closed_by="Pillar 405 (CLOSED: H¹ Sobolev extension; gradient perturbations bounded; KK energy cross-check)",
        used_by=["FTUM convergence claim", "φ₀ self-consistency (via FTUM)", "Holographic S=A/4G"],
    ),
    PostulateRecord(
        name="Admission 13: Metric ansatz non-uniqueness residual",
        kind=PostulateKind.ADMISSION,
        status=PostulateStatus.DERIVED,
        description=(
            "Pillar 406 (v13.1) CLOSES Admission 13: the GHY boundary term "
            "S_GHY = (1/κ₅²)∫K is derived from the Levi-Civita connection "
            "(C5 compatible; no torsion singularities).  Z₂ junction conditions "
            "at orbifold fixed points involve only the Levi-Civita extrinsic "
            "curvature.  Brane-localized R₄ terms are 4D intrinsic curvature "
            "(no 5D connection) — compatible with 5D Levi-Civita bulk.  "
            "Bulk uniqueness C1–C5 is preserved; GHY and brane terms are uniquely "
            "determined boundary supplements.  "
            "Prior status (v13.0): NARROWED_GAP (C1–C5; EC excluded; 6D documented)."
        ),
        breaks_if_fails=(
            "If a structurally distinct 5D EH + KK ansatz satisfying C1–C5 is found "
            "predicting different CMB observables, the uniqueness claim is broken.  "
            "6D/11D alternatives are outside the claim scope — explicitly documented."
        ),
        citation=(
            "FALLIBILITY.md §4.2 (model non-uniqueness); "
            "Pillar 384 (updated) / src/core/pillar384_metric_ansatz_uniqueness.py; "
            "Pillar 406 / src/core/pillar406_ghy_boundary_c5_closure.py; "
            "Pinčák et al. 2026, Gen. Rel. Grav."
        ),
        closed_by="Pillar 406 (CLOSED: GHY from Levi-Civita; Z₂ junctions torsion-free; brane R₄ compatible)",
        used_by=["Metric block ansatz claim", "Uniqueness of B_μ identification"],
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Named free parameters
# ──────────────────────────────────────────────────────────────────────────────

FREE_PARAMETERS: List[PostulateRecord] = [
    PostulateRecord(
        name="FP1: λ_GW — Goldberger-Wise coupling",
        kind=PostulateKind.FREE_PARAMETER,
        status=PostulateStatus.DERIVED,
        description=(
            "Pillar 404 (v13.1) DERIVES λ_GW: ν_GW = n_w/K_CS = 5/74 from braid "
            "quantization → α_φ = √(8ν) ≈ 0.735 → m_φ = α_φ M_KK ≈ 765 GeV.  "
            "λ_GW = α_φ² M_KK²/(8φ₀²) is now a derived quantity.  See Admission 6."
        ),
        breaks_if_fails="Exact radion mass; does not break n_w selection or CMB predictions.",
        citation="src/core/pillar404_lambda_gw_derivation.py (Pillar 404); src/core/goldberger_wise.py (Pillar 68); FALLIBILITY.md §4.6",
        closed_by="Pillar 404 (DERIVED_FROM_GW_NORMALIZATION)",
        used_by=["Radion mass scale"],
    ),
    PostulateRecord(
        name="FP2: RS bulk mass parameters c_L, c_R (fermion localization)",
        kind=PostulateKind.FREE_PARAMETER,
        status=PostulateStatus.OPEN_GAP,
        description=(
            "RS1 5D fermion bulk-mass parameters c_L and c_R determine "
            "zero-mode localization and hence Yukawa couplings.  Pillar 386 "
            "derives p_R from 3×3 seesaw texture diagonalization; individual "
            "c_L values constrained to braid lattice (5/74)×ℓ by Pillar 189-B "
            "but not uniquely derived."
        ),
        breaks_if_fails="Absolute Yukawa couplings and CKM/PMNS mixing angles.",
        citation=(
            "src/core/pillar386_seesaw_texture_diagonalization.py (P386); "
            "src/core/bulk_eigenvalues.py (Pillar 189-B)"
        ),
        used_by=["Yukawa couplings (P7–P10)", "Jarlskog J (Admission 7)"],
    ),
    PostulateRecord(
        name="FP3: N_e — number of inflationary e-folds",
        kind=PostulateKind.FREE_PARAMETER,
        status=PostulateStatus.OPEN_GAP,
        description=(
            "N_e≈60 is a standard slow-roll assumption, not derived from 5D "
            "geometry.  Pillar 346 provides a CONDITIONAL_DERIVATION via "
            "KK thermalization.  See Admission 11."
        ),
        breaks_if_fails="CMB spectral index nₛ and r (would shift within or outside Planck 1σ).",
        citation=(
            "FALLIBILITY.md §4.3; "
            "Pillar 346 / src/core/pillar346_ne_kk_thermalization.py"
        ),
        used_by=["nₛ=0.9635", "r_braided=0.0315"],
    ),
    PostulateRecord(
        name="FP4: Λ₅<0 — negative 5D cosmological constant",
        kind=PostulateKind.FREE_PARAMETER,
        status=PostulateStatus.ARCHITECTURE_LIMIT,
        description=(
            "The AdS₅ bulk requires Λ₅<0.  This is the only remaining postulate "
            "after Pillar 344 derives the rest of the metric ansatz.  Pillar 363 "
            "certifies MINIMAL_AXIOM status (analogous to G_{μ5} parity)."
        ),
        breaks_if_fails="RS1 warp factor; radion stabilisation; metric ansatz derivation.",
        citation="Pillar 363 / src/core/pillar363_lambda5_derivation_attempt.py; Pillar 344",
        used_by=["RS1 warp factor", "KK mode spectrum"],
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Combined registry
# ──────────────────────────────────────────────────────────────────────────────

def get_full_registry() -> List[PostulateRecord]:
    """Return the complete canonical registry: postulates + admissions + free parameters."""
    return CORE_POSTULATES + ADMISSIONS + FREE_PARAMETERS


def get_registry_by_kind(kind: PostulateKind) -> List[PostulateRecord]:
    """Return records filtered by kind."""
    return [r for r in get_full_registry() if r.kind == kind]


def get_open_gaps() -> List[PostulateRecord]:
    """Return all registry entries with status OPEN_GAP."""
    return [r for r in get_full_registry() if r.is_open]


# ──────────────────────────────────────────────────────────────────────────────
# DERIVED claim → postulate dependency map
# (The set of registry names that each DERIVED result depends on)
# ──────────────────────────────────────────────────────────────────────────────

DERIVED_CLAIM_DEPENDENCIES: Dict[str, List[str]] = {
    "nₛ=0.9635":                   ["P1: Z₂ orbifold structure (S¹/Z₂)", "P2: 5D KK metric block ansatz",
                                     "P5: FTUM fixed-point operator U = I+H+T",
                                     "FP3: N_e — number of inflationary e-folds"],
    "r_braided=0.0315":            ["P1: Z₂ orbifold structure (S¹/Z₂)", "P2: 5D KK metric block ansatz",
                                     "P7: Minimum-step braid assignment n₁=n_w, n₂=n_w+2",
                                     "P8: Minimum-step braid stability",
                                     "FP3: N_e — number of inflationary e-folds"],
    "k_CS=74 (algebraic)":         ["P1: Z₂ orbifold structure (S¹/Z₂)",
                                     "P7: Minimum-step braid assignment n₁=n_w, n₂=n_w+2",
                                     "P8: Minimum-step braid stability"],
    "c_s=12/37":                   ["P7: Minimum-step braid assignment n₁=n_w, n₂=n_w+2",
                                     "P8: Minimum-step braid stability"],
    "β∈{0.273°,0.331°}":          ["P2: 5D KK metric block ansatz",
                                     "P7: Minimum-step braid assignment n₁=n_w, n₂=n_w+2",
                                     "P8: Minimum-step braid stability"],
    "n_w=5 (pure theorem)":        ["P1: Z₂ orbifold structure (S¹/Z₂)",
                                     "P2: 5D KK metric block ansatz"],
    "N_gen=3":                     ["P1: Z₂ orbifold structure (S¹/Z₂)"],
    "SU(3)×SU(2)×U(1)":           ["P1: Z₂ orbifold structure (S¹/Z₂)"],
    "sin²θ_W=0.2313":             ["P1: Z₂ orbifold structure (S¹/Z₂)"],
    "m_H=125.25 GeV":              ["P2: 5D KK metric block ansatz",
                                     "P4: Goldberger-Wise double-well potential"],
    "Holographic S=A/4G":          ["P5: FTUM fixed-point operator U = I+H+T",
                                     "P6: Holographic entropy S=A/4G at FTUM fixed point"],
    "φ₀ self-consistency":         ["P4: Goldberger-Wise double-well potential",
                                     "P5: FTUM fixed-point operator U = I+H+T"],
    "Arrow of time":               ["P2: 5D KK metric block ansatz",
                                     "P3: B_μ as irreversibility 1-form"],
    "w₀=−1 (dark energy)":        ["P4: Goldberger-Wise double-well potential",
                                     "P5: FTUM fixed-point operator U = I+H+T",
                                     "FP1: λ_GW — Goldberger-Wise coupling"],
    "Λ_QCD≈332 MeV":              ["P1: Z₂ orbifold structure (S¹/Z₂)"],
    "α_s(M_Z)≈0.113":             ["P1: Z₂ orbifold structure (S¹/Z₂)"],
    "m_p/m_e≈1825.3":             ["P1: Z₂ orbifold structure (S¹/Z₂)"],
    "BH information conservation": ["P5: FTUM fixed-point operator U = I+H+T",
                                     "P6: Holographic entropy S=A/4G at FTUM fixed point"],
}


# ──────────────────────────────────────────────────────────────────────────────
# Completeness check
# ──────────────────────────────────────────────────────────────────────────────

def check_completeness() -> Dict[str, object]:
    """
    Verify every DERIVED claim has at least one documented postulate dependency.

    Returns a report dict with:
      - 'all_complete': bool
      - 'total_derived': int
      - 'missing_dependencies': list of claim names lacking any postulate dependency
      - 'complete_claims': list of claim names with at least one dependency
    """
    registry_names: Set[str] = {r.name for r in get_full_registry()}
    missing: List[str] = []
    complete: List[str] = []

    for claim, deps in DERIVED_CLAIM_DEPENDENCIES.items():
        if not deps:
            missing.append(claim)
        else:
            # Verify every cited dependency actually exists in the registry.
            unresolved = [d for d in deps if d not in registry_names]
            if unresolved:
                missing.append(f"{claim} (unresolved deps: {unresolved})")
            else:
                complete.append(claim)

    return {
        "all_complete": len(missing) == 0,
        "total_derived": len(DERIVED_CLAIM_DEPENDENCIES),
        "missing_dependencies": missing,
        "complete_claims": complete,
        "completeness_fraction": len(complete) / max(len(DERIVED_CLAIM_DEPENDENCIES), 1),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Minimality check
# ──────────────────────────────────────────────────────────────────────────────

def check_minimality() -> Dict[str, object]:
    """
    Flag postulates that do not appear as a dependency of any DERIVED result.

    A genuinely unused postulate is either redundant or mislabelled.

    Returns a report dict with:
      - 'all_used': bool
      - 'unused_postulates': list of registry names not found in any dependency list
      - 'used_postulates': list of registry names used by ≥1 DERIVED result
    """
    # Build the set of all dependency names appearing in any claim.
    all_deps: Set[str] = set()
    for deps in DERIVED_CLAIM_DEPENDENCIES.values():
        all_deps.update(deps)

    registry = get_full_registry()
    unused: List[str] = []
    used: List[str] = []

    for record in registry:
        if record.name in all_deps:
            used.append(record.name)
        else:
            unused.append(record.name)

    return {
        "all_used": len(unused) == 0,
        "total_registry": len(registry),
        "unused_postulates": unused,
        "used_postulates": used,
        "usage_fraction": len(used) / max(len(registry), 1),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Top-level audit report
# ──────────────────────────────────────────────────────────────────────────────

def postulate_registry_report() -> Dict[str, object]:
    """
    Return the complete Pillar 394 postulate minimality audit report.

    Includes:
      - registry summary (counts by kind and status)
      - completeness check result
      - minimality check result
      - list of open gaps requiring attention
    """
    registry = get_full_registry()
    completeness = check_completeness()
    minimality = check_minimality()
    open_gaps = get_open_gaps()

    counts_by_kind: Dict[str, int] = {}
    counts_by_status: Dict[str, int] = {}
    for r in registry:
        counts_by_kind[r.kind.value] = counts_by_kind.get(r.kind.value, 0) + 1
        counts_by_status[r.status.value] = counts_by_status.get(r.status.value, 0) + 1

    return {
        "pillar": 394,
        "title": "Postulate Minimality Audit",
        "version": "v12.9",
        "registry_total": len(registry),
        "counts_by_kind": counts_by_kind,
        "counts_by_status": counts_by_status,
        "open_gap_count": len(open_gaps),
        "open_gap_names": [r.name for r in open_gaps],
        "completeness": completeness,
        "minimality": minimality,
        "audit_verdict": (
            "PASS" if completeness["all_complete"] else "FAIL"
        ),
    }


def pillar_394_status() -> Dict[str, str]:
    """Machine-readable pillar status summary."""
    report = postulate_registry_report()
    return {
        "pillar": "394",
        "name": "Postulate Minimality Audit",
        "status": "EPISTEMOLOGICAL_INFRASTRUCTURE",
        "registry_total": str(report["registry_total"]),
        "open_gaps": str(report["open_gap_count"]),
        "completeness": "PASS" if report["completeness"]["all_complete"] else "FAIL",
        "minimality_unused": str(len(report["minimality"]["unused_postulates"])),
        "audit_verdict": report["audit_verdict"],
    }
