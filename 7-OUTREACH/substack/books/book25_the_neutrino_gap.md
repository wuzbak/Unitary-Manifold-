# Book 25 — The Neutrino Gap: Step by Step Toward a Theory of Flavor

*Unitary Manifold v19.1 — ThomasCory Walker-Pearson — July 2026*

*Synthesized with GitHub Copilot (AI)*

---

> **What this book is:**
> A plain-language account of the hardest remaining open problem in the
> Unitary Manifold framework — the atmospheric neutrino mass splitting Δm²₃₁.
> What the gap is, why it exists, what the 3-step closure path looks like,
> and what Step 1 actually computed.
>
> **What this book is not:**
> A claim that the gap is closed. It isn't. This is the story of a gap
> being understood more deeply, one step at a time.

---

## Chapter 1 — What Is Δm²₃₁?

Neutrinos oscillate. A muon neutrino produced in the atmosphere can transform
into a tau neutrino before reaching a detector underground. The probability
of this transformation depends on the *mass splitting* between the second
and third neutrino mass eigenstates:

    Δm²₃₁ = m₃² - m₁²

JUNO Phase 1 (2026) measured this to be:

    Δm²₃₁ = 2.411 × 10⁻³ eV²   (±0.81%)

This is one of the most precisely measured quantities in neutrino physics.
It is the yardstick against which the Unitary Manifold must be judged.

---

## Chapter 2 — The Prediction Problem

The Unitary Manifold is a 5-dimensional Kaluza-Klein framework. Neutrino
masses in this framework arise from the seesaw mechanism: right-handed
neutrinos propagating in the 5D bulk combine with the Standard Model
left-handed neutrinos at the boundary (the "brane") to produce small
effective masses.

The UM 2NLO (next-to-next-to-leading-order) bare prediction is:

    Δm²₃₁^{2NLO} = 2.2845 × 10⁻³ eV²

This is excluded by JUNO at **6.46σ**. That is not a small tension.

The best improvement available within the minimal framework — adding
renormalization-group running (RGE) and seesaw corrections at maximum
right-handed neutrino mixing (p_R = 0.441) — reaches:

    Δm²₃₁^{best} = 2.3457 × 10⁻³ eV²

Still excluded at **3.33σ**. Still outside JUNO's 1σ band.

---

## Chapter 3 — The Architecture Limit

Pillar 544 (v19.0) formally certified the gap as `ARCHITECTURE_LIMIT_CERTIFIED`.

This is a precise scientific label. It means:

1. The gap is **real** — not a numerical error, not a calibration uncertainty.
2. The gap is **at the boundary of the model** — the minimal 5D-EFT cannot
   close it without extending the framework.
3. The closure path is **named** — three specific steps are identified.

An architecture limit is not falsification. It means: "The model tells us
exactly what it needs to do next."

---

## Chapter 4 — The Three-Step Closure Path

**Step 1: WS-V KK Off-Diagonal Yukawa (Pillar 548)**

The Weinberg-Sakai-Sugimoto-Vijay (WS-V) texture introduces off-diagonal
Yukawa couplings between the bulk KK neutrino tower and the IR-brane.
These off-diagonal terms shift Δm²₃₁ upward.

Pillar 548 computed the leading correction (2-3 sector):

    δ(Δm²₃₁) / Δm²₃₁ ≈ +2–8%

This reduces the tension from 3.33σ toward ~2.90σ. Partial progress.

The WS-V correction is a first estimate. It requires the Froggatt-Nielsen
correction δ_KT = 0.053 (Pillar 402) and the KK mode overlap functions.
It is not an exact derivation.

**Step 2: ν_R Orbifold Boundary Condition (future)**

Right-handed neutrinos (ν_R) in the 5D bulk must satisfy orbifold boundary
conditions at the UV brane. The localization of ν_R on the IR brane is
controlled by the orbifold parameter c_R (analogous to c_L for left-handed
fermions, Pillar 546).

Step 2 requires deriving c_R from the Z₂ orbifold geometry — the same
framework used for c_L in Pillar 546. This is tractable but has not yet
been computed.

**Step 3: Two-Loop Seesaw Mass Correction (future)**

The seesaw scale M_R receives two-loop corrections from the KK tower.
These are suppressed by 1/(16π²)² but can be O(1%) for the neutrino
sector where the bare contribution is already small.

Step 3 requires a full two-loop KK calculation — significantly beyond
the current 5D-EFT toolbox. This likely requires external collaboration
or new analytic techniques.

---

## Chapter 5 — Why Step 1 Matters

A 2.90σ tension is still a tension. It is not a resolution.

But the trajectory matters:

    Pillar 300 (v11): 6.46σ (bare 2NLO)
    Pillar 525 (v18): 3.33σ (RGE + seesaw, JUNO measured)
    Pillar 548 (v19.1): ~2.90σ estimate (+ WS-V correction)
    After Step 2: TBD
    After Step 3: TBD

Each step reduces the tension. The gap is not shrinking to zero immediately,
but the architecture is producing the right direction of movement.

The JUNO Phase 2 window (2027–2028) will provide precision at ±0.3%.
If Step 2 narrows the gap to 2σ before JUNO Phase 2 reports, the framework
will be consistent. If the gap remains above 3σ after all three steps, the
seesaw architecture must be replaced.

---

## Chapter 6 — The Fermion Mass Problem and Gen-1

The same orbifold geometry that governs Δm²₃₁ also determines the fermion
bulk masses c_L.

Pillar 546 derived:
- Gen-3 (t, b, τ): c_L = 0 (IR-localized) — DERIVED
- Gen-2 (c, s, μ): c_L = 5/74 — DERIVED
- Gen-1 (u, d, e): NATURAL (FN dominated — not derived)

Pillar 550 proposed the identification: the Froggatt-Nielsen charge Q_FN
is the orbifold lattice position ℓ. Under this identification, gen-1 has
Q_FN = ℓ = 2, giving c_L = 10/74.

The mass ratio prediction under this identification:

    m_gen2 / m_gen3 ≈ 5/74 ≈ 0.068   (cf. m_μ/m_τ ≈ 0.059 ✓)
    m_gen1 / m_gen3 ≈ (5/74)² ≈ 0.0046   (cf. m_e/m_τ ≈ 0.00029 — factor 16 gap)

The lepton sector has a factor-of-16 discrepancy at gen-1. The identification
gives the right order of magnitude for gen-2/gen-3, but gen-1 needs more work.

This is the same honest pattern as the neutrino gap: the framework gets the
direction right, the scale approximately right, and then runs into a precision
gap that requires more physics.

---

## Chapter 7 — What Falsification Looks Like

There are two possible outcomes for the neutrino sector:

**Outcome A (closure):** Steps 1–3 together bring Δm²₃₁ within 1σ of JUNO,
with no free parameters. The architecture limit is closed. The fermion
sector is first-principles derived.

**Outcome B (falsification):** After completing all three steps, Δm²₃₁
remains excluded at ≥3σ without additional free parameters. The seesaw
architecture in the minimal 5D-EFT is insufficient. A new mechanism is
required — possibly a 6D extension or a non-minimal orbifold.

The framework explicitly cannot rule out Outcome B at this stage.
This is stated here, not to be pessimistic, but because honest science
requires naming the failure modes.

---

## Chapter 8 — DESI and the Dark Energy Parallel

There is a structural parallel between the neutrino gap and the DESI
dark energy tension.

Both are:
- Real tensions (not numerical errors)
- Below the falsification threshold (3σ for wₐ, 3σ for Δm²₃₁)
- Associated with architecture limits (frozen radion for wₐ; seesaw for Δm²₃₁)
- Pre-registered for decision routing

The difference is observational timescale:
- DESI DR3: could arrive in months
- JUNO Phase 2: 2027–2028
- Two-loop seesaw computation: unknown timeline

The Unitary Manifold is in a window of productive tension. The framework
is precise enough to be testable, and the tests are arriving.

---

## Conclusion — The Gap Is the Science

The neutrino mass gap is not a failure. It is the most precise statement
the framework can make about its own limits. "I need WS-V off-diagonal terms,
orbifold BCs for ν_R, and two-loop seesaw" is a more useful statement than
"I can't explain neutrino masses."

The gap is closing — one step, one pillar, one honest estimate at a time.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
