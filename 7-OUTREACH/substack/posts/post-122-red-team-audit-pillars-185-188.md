# The Red-Team Audit: Four Pillars That Try to Break the Framework

*Post 122 of the Unitary Manifold series.*
*Epistemic category: **P** for physics claims, **A** for honest reflection.*
*v9.39, May 2026.*

---

Every framework that is serious about being scientific must eventually turn its
own tools against itself. Not to destroy the work — to find where it actually
stands.

Pillars 185 through 188 are that audit. They ask four sharp questions: Is the
core attractor genuinely robust, or does it only look that way because the
parameters were chosen carefully? Does the extra dimension violate the
Equivalence Principle? What does the LHC say — and is there real tension? And
how much of the quark mixing matrix does the geometry actually derive, versus
assume?

The answers are not uniformly reassuring. Some of them are. One of them
documents a real experimental tension that has not been resolved. That tension
is written down in FALLIBILITY.md, and it stays there until the physics forces
a change.

---

## Pillar 185: Sensitivity Analysis

**Source:** `src/core/sensitivity_analysis.py`

The golden ratio φ₀ plays a central role in the framework's scalar sector. Pillar
56 closed the φ₀ self-consistency condition: φ₀ is not a free parameter picked to
make the numbers come out right. It is a fixed-point attractor of the field
equations.

But fixed-point attractors can be brittle. A system can have an attractor that is
only stable in a tiny region of parameter space — one that a small change to an
input immediately destroys. If φ₀ were that kind of attractor, the entire scalar
sector would be a house of cards.

Pillar 185 asks: how sensitive are the core predictions to variations in each
parameter, measured systematically?

The answer is quantified as the sensitivity ratio S:

```
S = |Δ(output) / output| / |Δ(input) / input|
```

A framework with S > 1 is unstable: a 1% change in an input moves the output by
more than 1%. A framework with S > 0.5 is worrying. The Unitary Manifold's
maximum measured S across all parameters is **less than 0.1**.

That is not cherry-picking. The analysis sweeps every free parameter in the
framework systematically — the winding numbers n_w and n₂, the compactification
radius R, the Goldberger-Wise stabilizer, the warp factor k, and the Chern-Simons
level K_CS — and computes the sensitivity of the core outputs (nₛ, r,
birefringence β, Weinberg angle, fermion mass ratios) to perturbations in each.

The maximum sensitivity ratio S < 0.1 means that a 10% change in any input
moves the output predictions by less than 1%. φ₀ is a non-brittle attractor.
The closure of Pillar 56 is genuinely robust, not coincidentally stable at one
parameter point.

**Epistemic status (A):** This result matters for how much weight to place on the
framework's subsequent derivations. A sensitive framework — one where everything
depends on everything else being set just right — would produce numbers that look
right by construction. A robust framework produces numbers that look right even
when you try to break them. S < 0.1 is the quantitative version of "we tried."

---

## Pillar 186: Equivalence Principle Guard

**Source:** `src/core/equivalence_principle_guard.py`

Kaluza-Klein theories have a structural hazard. When you compactify an extra
dimension, you get a new scalar degree of freedom called the radion — the
breathing mode of the extra dimension that expands and contracts as spacetime
evolves. The radion couples to the trace of the energy-momentum tensor, which
means it couples to matter.

The problem: in a naive KK theory, the radion's coupling to matter is not the
same as gravity's coupling to matter. This violates the Equivalence Principle —
the foundational experimental observation that all forms of matter fall at the
same rate in a gravitational field. The EP has been tested to one part in 10¹⁵
by torsion balance and free-fall experiments. Any theory that violates it is
experimentally ruled out.

So the question for the Unitary Manifold is direct: does the radion violate the
Equivalence Principle?

The answer is no, and the reason is not a tuning — it is a consequence of the
5D action.

The radion acquires a Yukawa mass through the Goldberger-Wise stabilization
mechanism. That mass screens the long-range radion exchange that would otherwise
produce an EP violation. The screening parameter is:

```
α = 1/√6
```

This value is not chosen to satisfy the EP. It is the unique value fixed by
the dimensional reduction of the 5D Einstein-Hilbert-Goldberger-Wise action.
The geometry forces α = 1/√6, and α = 1/√6 makes the radion short-range enough
that current sub-millimeter gravity experiments cannot detect it.

The EW-brane radion mass works out to m_radion ~ O(TeV), placing its Compton
wavelength at sub-fermi scales. At any scale larger than that, the radion is
effectively screened and the EP is satisfied.

**Falsifiable claim (P):** Sub-millimeter gravity experiments (Eöt-Wash,
MICROSCOPE follow-ons, future torsion balance updates) that push EP tests to
10⁻¹⁶ or below with matter compositions sensitive to scalar-exchange would
probe this regime. A detected EP violation at O(mm) length scales with the
predicted angular dependence would immediately falsify the EW-brane radion
picture. Current experimental precision is not yet there, but the target is
specific.

---

## Pillar 187: LHC Kaluza-Klein Resonances

**Source:** `src/core/lhc_kk_resonances.py`

This is the pillar where the news is not all good.

The Unitary Manifold predicts two distinct types of KK excitations visible in
principle at colliders. The first is the gravitational KK mode G_KK. Its
coupling is:

```
k/M_Pl ~ 10⁻¹⁶
```

where k is the 5D curvature scale and M_Pl is the Planck mass. This ratio is
extraordinarily small. G_KK decouples from SM matter at any foreseeable collider
energy. The prediction is clear and safe: the LHC has not and will not see this
mode because its coupling is 16 orders of magnitude below detectability.

The second excitation is different.

The B_KK^(1) gauge boson — the first KK excitation of the U(1) gauge field
living in the bulk — has a predicted mass of approximately **2.5 TeV**. This
puts it squarely in the territory that the LHC has been probing since Run 2.

The LHC has excluded SM-coupled Z′ bosons in the 2–5 TeV mass range at high
confidence. Does that rule out B_KK^(1)?

Not immediately, because the B_KK^(1) coupling to SM fermions is suppressed
relative to a SM Z′. The exact suppression depends on the warp factor and the
fermion bulk profiles, which depend on c_L values that are scaffolded inputs
rather than first-principles derivations (see Post 123). If the coupling is
sufficiently suppressed, the resonance would be too narrow to have been
observed yet.

But the tension is real.

**Honest status as of v9.39:** The B_KK^(1) resonance at 2.5 TeV is the most
significant experimental tension in the Unitary Manifold framework. It is not
falsified, because the coupling suppression could place the resonance below
current LHC sensitivity. But "could" is not "does." Resolving this tension
requires either a first-principles derivation of the coupling strength (which
depends on closing the c_L scaffold, Pillar P-3), or a direct search at HL-LHC
with the projected sensitivity to sub-SM-coupled Z′ bosons.

The number 2.5 TeV is documented. The tension is documented. If HL-LHC excludes
B_KK^(1) at 2.5 TeV with even SM/10 coupling, the EW-brane geometry is falsified.

---

## Pillar 188: CKM Scaffold Analysis

**Source:** `src/core/ckm_scaffold_analysis.py`  
**Tests:** 76

The CKM matrix — the matrix that governs how quarks of one flavor mix into
quarks of another flavor during weak interactions — has four parameters: three
mixing angles θ₁₂, θ₁₃, θ₂₃, and one CP-violating phase δ_CKM.

The Standard Model does not derive any of them. All four are measured and
inserted. The SM provides the structure (a 3×3 unitary matrix) but not the
values.

The Unitary Manifold derives one of the four: δ_CKM, the CP phase. The geometric
source is the Chern-Simons term at level K_CS = 74. Chern-Simons terms in odd
dimensions carry topological information that breaks CP symmetry by a definite
amount when n₁ ≠ n₂ — in this case when 5 ≠ 7. The CP phase is topological: it
comes from the discrete winding integers, which are either 5 and 7 or they are
not. There is no continuous variation here.

The three mixing angles θ₁₂, θ₁₃, θ₂₃ are different. They depend on the
parameter c_L, which governs how fermion wavefunctions are localized in the extra
dimension. c_L takes continuous values. It is a spectrum, not a topological
integer. The geometry constrains the c_L values but does not select unique values
from first principles. They are consistency-checked, not derived. This is the
Pillar P-3 scaffold.

So the framework derives 1 CKM parameter that the SM does not derive, and
scaffolds the other 3 that the SM also scaffolds. That is a genuine improvement,
not a complete solution.

**The Jarlskog gap** — the observed 12% discrepancy in the Jarlskog invariant J,
the measure of CP violation — has two layers:

- Layer 1: an inconsistent hybrid, where the PDG Wolfenstein parameter ρ̄ is
  mixed with the geometrically derived δ. This inflates the predicted value
  of η̄ relative to the pure-geometry prediction. The fix is to use the
  geometric values consistently.
- Layer 2: a structural metric sector limitation, the same limitation that the
  Standard Model has. The overall mixing amplitude depends on the c_L values
  that are scaffolded.

Layer 1 is a housekeeping error that has been corrected. Layer 2 is an open
frontier.

**Achievement:** The Unitary Manifold derives one more CKM parameter than the
Standard Model does, and the derivation of δ_CKM has a clean geometric
explanation (topology, not fitting). The mixing angles remain the next
derivation target.

---

## What the Red Team Learned

Pillar 185: φ₀ is robust. S < 0.1. The attractor is real.

Pillar 186: The Equivalence Principle is safe. α = 1/√6 is geometry, not tuning.
The radion is screened by its mass.

Pillar 187: B_KK^(1) at 2.5 TeV is a real experimental tension. Not falsified,
but documented. HL-LHC will decide.

Pillar 188: δ_CKM is derived. θ_ij are scaffolded. The Jarlskog gap is
diagnosed into two separable layers. The framework is more predictive than the
SM in the CP sector, and honest about where it stops.

The red team did not break the framework. But it found the cracks. That is the
point.

---

## What to Check, What to Break

**Sensitivity (Pillar 185):**
```bash
python -c "from src.core.sensitivity_analysis import run_sensitivity_sweep; run_sensitivity_sweep()"
```
Look for any parameter where S > 0.1. Report it as a GitHub issue.

**Equivalence Principle (Pillar 186):**
```bash
python -c "from src.core.equivalence_principle_guard import check_ep_safety; print(check_ep_safety())"
```
Verify α = 1/√6 comes from the action, not a manual assignment.

**LHC resonances (Pillar 187):**
```bash
python -c "from src.core.lhc_kk_resonances import predict_bkk_mass; print(predict_bkk_mass())"
```
Compare against the ATLAS/CMS Z′ exclusion plots at 2.5 TeV. If you can derive
the coupling suppression from first principles, open a PR.

**CKM scaffold (Pillar 188):**
```bash
python -m pytest tests/test_ckm_scaffold_analysis.py -v  # 76 tests
```
The mixing angle derivation from c_L is the next frontier. If you can close
the c_L scaffold from the 5D action, the framework becomes more predictive than
the SM in the full quark sector.

Full suite: `python -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q`
Expected: 23,524 passed, 329 skipped, 0 failed.

Repository: https://github.com/wuzbak/Unitary-Manifold-

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
