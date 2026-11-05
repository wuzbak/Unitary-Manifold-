# PART VII — CLOSING THE STANDARD MODEL, SURVIVING THE RED TEAM

*PsiCat Original Work v1 · Series/Season One*
*AxiomZero Technologies & Consulting, SPC commissioned work: Investigated and written by PsiCat Ai.*
*Original-work provenance: authored by PsiCat (Merlin), adapted and corrected from
`7-OUTREACH/pillar-guide/PILLAR_DESCRIPTIONS.md` (v18.5) against current repository status. Not a rewrite of
an externally published source.*
*Part file of Book 56 — reading index: `book-56-the-complete-pillar-guide.md`.*

## Chapter 29 — What "100% Framework Derivation Coverage" Actually Means

Pillars 133 through 167 — developed in a concentrated wave across several point releases — brought the
framework's coverage of the Standard Model's twenty-eight parameters from partial to complete. Before the
inventory, the phrase "100% coverage" needs defining precisely, because it is the single most load-bearing
phrase in this whole arc and the easiest one to misread as "100% derived." It means every one of the
twenty-eight parameters has been addressed with an explicit, honestly labeled status: some are DERIVED (no
free parameters, a clean geometric prediction), some are PARAMETERIZED (consistent with the framework but
requiring per-species inputs not yet derived from first principles), some are CONSTRAINED (derived up to a
named subleading correction or UV-seed input), and one — the cosmological constant — sits at ARCHITECTURE
LIMIT, a label this book explains fully in Chapter 33. The coverage score counts how many parameters have an
honest answer on record. It does not count how accurate, or how first-principles, each answer is.

## Chapter 30 — The Closure Wave (Pillars 133–149)

**Pillar 133** (`src/core/ckm_cp_subleading.py`) closes the CKM CP-phase to 0.99σ accuracy via a braid opening
angle δ_sub = 2·arctan(5/7) ≈ 71.08°, within one standard deviation of the PDG value of 68.5°, with no fitting.
**Pillar 134** (`src/core/higgs_mass_closure.py`) derives the Higgs mass from an FTUM tree-level quartic
coupling plus a one-loop top-Yukawa correction, landing 1.66% below the PDG value — a residual documented as
an open refinement target, not hidden. **Pillar 135** (`src/core/neutrino_mass_splittings.py`) derives the
atmospheric-to-solar neutrino mass-splitting ratio from RS Dirac zero-mode geometry, landing 10.5% above the
PDG central value, a gap later narrowed by Pillar 274's NLO corrections. **Pillar 136**
(`src/core/kk_radion_dark_energy.py`) derives a corrected KK dark-energy equation of state w_KK ≈ −0.9302,
consistent with DESI DR2 but in tension with the Planck+BAO combination — a tension Chapter 33 revisits.
**Pillar 137** (`src/core/sm_parameter_grand_sync.py`) is the authoritative audit ledger for all twenty-eight
parameters at the moment of closure; its one OPEN entry, Λ_QCD at a seven-order-of-magnitude discrepancy, is
resolved in Pillar 162 and Pillar 153, described below. **Pillars 138–142** derive the solar mixing angle, the
Higgs vacuum expectation value (to 0.10% of the PDG value — the tightest single Standard-Model prediction in
this book), a lower bound on the lightest neutrino mass, Newton's constant from Randall-Sundrum self-
consistency, and the CKM Wolfenstein ρ̄ parameter, the last of these landing roughly 25% from the PDG value and
documented as an honest open residual rather than smoothed over.

**Ω₀ Holon Zero** sits structurally in this chapter as well as in Part V: it is the irreducible closure
certificate carrying the full epistemic ledger for the twenty-eight parameters, at the specific moment (eight
DERIVED, nine PARAMETERIZED, four CONSTRAINED, three GEOMETRIC_ESTIMATE, with Λ_QCD then still OPEN) this arc
began.

**Pillars 143–149** form an epistemic-tightening wave: proving a specific neutrino mixing parameter as a
theorem from the orbifold fixed point while honestly diagnosing a remaining order-of-magnitude gap the theorem
alone cannot close; establishing the RS zero-mode RGE bridge for neutrinos; proving that the Jarlskog CP-
violation invariant is non-zero from pure geometry whenever the two winding numbers differ; resolving the
neutrino bulk-mass UV condition and seesaw viability; eliminating the radion as a dark-energy candidate once
fifth-force constraints are applied; deriving the non-Abelian Standard Model gauge group SU(3)×SU(2)×U(1) from
n_w=5 through an SU(5) unification step and a Kawamura Z₂ projection; and quantifying the CMB acoustic-peak
amplitude suppression factor precisely, as an honest open problem rather than a vague caveat.

## Chapter 31 — Two Gap-Closure Arcs (Pillars 150–167)

Pillars 150 through 161 constitute Gap Closure Arc I: a Majorana neutrino-mass derivation via the seesaw
mechanism from the KK UV brane; continued tracking of the dark-energy equation-of-state tension against DESI
and Planck; a baryon-to-photon ratio derived from the KK baryon sector; and, critically, **Pillar 153**
(`src/core/lambda_qcd_gut_rge.py`), which establishes a cross-check path for Λ_QCD via four-loop MS-bar RGE
running, matching the PDG value within experimental uncertainty. The remaining pillars in this stretch address
chiral-fermion derivation from orbifold fixed points, the wₐ=0 frozen-radion dark-energy prediction (with a
DESI tension documented as an open monitoring item rather than resolved), the Randall-Sundrum inflation
amplitude, a Dirac-neutrino branch found viable but disfavored by roughly 1% fine-tuning, a resolution of a
three-orders-of-magnitude neutrino-mass inconsistency via Majorana seesaw, an honest null result on KK axion
quintessence as a mechanism for a non-zero wₐ, and an analysis of the 5D inflaton sector.

Pillars 162 through 167 constitute Gap Closure Arc II. **Pillar 162**
(`src/core/qcd_confinement_geometric.py`) is the geometric AdS/QCD derivation that, combined with Pillar 153,
fully resolves the seven-order-of-magnitude QCD discrepancy that Pillar 137's ledger had flagged OPEN — ρ-meson
mass within 2% of PDG, Λ_QCD derived with zero free parameters. **Pillar 163**
(`src/core/pmns_solar_rge_correction.py`) shows that the relevant one-loop RGE correction is numerically
negligible, leaving a roughly 13% gap in the solar mixing angle as an honest, unresolved open problem — stated
here exactly as the repository states it, without softening. **Pillar 164**
(`src/core/cl_topological_classification.py`) proves a specific bulk-mass parameter as a topological theorem,
within 0.16% of its numerical value. **Pillars 165–166** establish a vacuum-naturalness argument for the scalar
amplitude and compute a negligible one-loop Coleman-Weinberg correction to the dark-energy equation of state.
**Pillar 167** (`src/meta/mas_wave_engine.py`) is the MAS Wave Engine, a meta-pillar that tracks the
repository's documented open gaps and routes closure attempts to the appropriate modules — effectively the
framework's own internal gap-tracking system, a piece of infrastructure this book leaned on directly while
researching Parts V through VII.

## Chapter 32 — The Adversarial Hardening Arc (Pillars 168–217)

This arc may be the most scientifically important fifty pillars in the repository, because each one documents
the framework's response to a specific external or internal critique — from red-team review, from peer-review
responses, from named external adversarial audits — and each either closes the gap honestly or documents
precisely why it remains open. This book treats that willingness to be pressure-tested, and to publish the
results of the pressure-testing even when they are unflattering, as the single strongest piece of evidence
for the project's scientific seriousness, independent of whether any individual physics claim ultimately holds
up under external peer review.

The Red-Team Arc (Pillars 168–181) began when a formal internal audit identified four major weaknesses.
**Pillar 168** documents that the GUT coupling α_GUT is CONSTRAINED rather than silently treated as derived,
with a 1.7% residual named explicitly. **Pillar 171** (`src/core/rs1_laplacian_spectrum.py`) may be the single
most important honest admission in this arc: it documents that the Randall-Sundrum Laplacian has a
*continuous* spectrum, not a discrete KK tower, unless orbifold boundary conditions are carefully imposed —
stated as a geometric fact to be accounted for, not a failure to be minimized. **Pillar 173** documents, and
has never since weakened, that fermion masses are PARAMETERIZED via per-species bulk-mass values, not derived
from first principles. **Pillar 181** (`src/core/symbolic_metric.py`) builds a formal symbolic-metric bridge
using SymPy, enabling algebraic verification of the metric structure independent of any numerical
implementation — closing a formal-rigor gap identified in peer review.

**Pillar 182** is the peer-review arc's capstone: it derives Λ_QCD from the two core integers via two
independent paths with zero Standard-Model RGE input, closing the seven-order-of-magnitude QCD criticism
comprehensively, demoting Goldberger-Wise stabilization from "primary mechanism" to "cross-check," and
auditing the radion stabilization status honestly.

The Audit Response Arc (Pillars 183–188) makes the Z₂-odd Chern-Simons boundary-phase condition executable as
a callable function rather than merely stated (Pillar 183); proves the FTUM fixed point φ₀ is a non-brittle
attractor with a bounded sensitivity parameter (Pillar 184); proves the equivalence principle is screened and
protected at electroweak scale against current fifth-force experiments (Pillar 185); documents an open tension
around a predicted LHC "invisible" KK gauge-boson resonance whose current null result is consistent but whose
positive detection would be decisive (Pillar 186); and documents precisely why the CKM CP phase derives
geometrically while the mixing angles themselves do not — a clear delineation of what the geometric mechanism
explains and does not (Pillar 188).

Pillars 189-A through 189-D implement a two-tier scaffolded registry for the AxiomZero forward chain: RGE
running upward from the GUT coupling, warp-corrected bulk KK eigenvalues, the Goldberger-Wise radion-coupling
stabilizer, and a topological cutoff-action minimizer.

Pillars 190 through 199 address, in sequence, neutrino winding; a complete Sakharov-conditions audit
confirming all three baryogenesis conditions are satisfied with a specific computed baryon asymmetry; a
neutrino-symmetry mapping; a predicted Josephson-style resonance frequency; a resonance audit using Shannon
entropy; an eight-kill-switch safety manifesto for the framework's own claim-making process; a stress-energy
audit at high numerical precision; a B_μ ghost-stability proof; and gravitational-wave polarization
constraints checked against a real detected merger event.

**Pillar 200** is the AxiomZero RGE geometric forward chain, deriving a strong-coupling value from the two
core integers alone and documenting explicitly a roughly ×4 "Warp-Anchor Gap" between this geometric value and
the PDG value — the chain demonstrates the derivation *path* even where the quantitative residual remains
unresolved, and says so without euphemism.

**Pillars 201–208**, the "Near Closure" wave, derive the Higgs VEV geometrically (4.6% from PDG); derive the
proton-to-electron mass ratio from the two core integers to 0.59% accuracy with no lattice-QCD input; audit the
KK QCD renormalization scheme; prove a bulk-mass parameter as a topological theorem; derive exactly three
matter generations from braid quantization; and, in **Pillar 206**, document the cosmological constant as an
ARCHITECTURE LIMIT — RS1-plus-Gauss-Bonnet mechanisms exhaust sixty-four orders of magnitude of suppression,
leaving a fifty-eight-order gap that is named honestly as a limit of the 5D effective theory rather than
papered over with an unexplained fine-tuning. **Pillar 207** rejects a tempting numerological identification
with the Leech lattice (k_CS is exactly 74, not 24 or 196,560, and the identification is geometrically
incompatible). **Pillar 208** establishes braid-lock PMNS predictions for all three neutrino mixing angles,
each within 5% of the PDG value from pure braid geometry — and is, by the repository's own long-standing
convention, the final pillar of the numbered 1–208 hardgate core.

**Pillars 209 through 217** extend this closure into first-principles precision work that followed the formal
208-pillar freeze: a universal Yukawa boundary condition proved with zero free parameters; a tightened
neutrino-splitting constraint; confirmation of the Higgs-mass Architecture Limit; closure of a kinematic gap
in the ADM formalism identified by a prior peer-review response; a braid spectrum including subleading
corrections; a Randall-Sundrum Dirac-neutrino spectrum prediction later verified by Pillar 135; a q-deformed
refinement of the CKM ρ̄ parameter to within 0.03° of the PDG central value; the Higgs Coleman-Weinberg
Architecture Limit; and, in **Pillar 217**, a careful distinction between what the Randall-Sundrum geometry
determines (the KK mass scale, the 5D coupling hierarchy) and what it still does not determine (the absolute
5D Planck mass) — the honest boundary of Newton's constant's derivation.

## Chapter 33 — Architecture Limit: The Framework's Hardest Admission

The ARCHITECTURE_LIMIT label deserves its own short treatment, because it is this repository's most
philosophically serious epistemic category and the one most easily missed by a casual reader. It does not mean
"we have not gotten around to this yet." It means the framework has identified a gap that, as far as its
authors can currently show, cannot be closed by any further refinement within the 5D effective field theory as
constructed — the cosmological constant, where sixty-four orders of magnitude of geometric suppression still
leave a fifty-eight-order residual, is the clearest example, and the Higgs-mass hierarchy carries a related,
if less extreme, version of the same honest ceiling. Naming a limit this way is, in this book's judgment, more
scientifically valuable than a false closure would have been, because it tells a reader exactly where new
physics — beyond this 5D construction — would actually need to enter.

---

*Part VII of Book 56 in the PsiCat Literature.*
*Author: PsiCat (Merlin), AxiomZero Technologies & Consulting, SPC.*
*October 2026.*
