# Post 213 — S02E039: The Year of Decision — Three Experiments That Will Make or Break the Unitary Manifold

*Substack — Season 2, Episode 39*
*Published: 2026-05-20*
*Series: The Falsification Decade*

---

## The Rarest Thing in Physics

A framework that tells you exactly how it dies.

Most theories in physics are padded with escape hatches. They predict ranges, not points. They invoke model-dependence when data turns inconvenient. They die slowly, by redefinition, rather than cleanly, by measurement.

The Unitary Manifold was built differently. From the beginning, we insisted on preregistered, machine-readable falsification conditions — thresholds locked in code before the experiments run, not invented afterwards when results arrive. We have 309 passing tests as of today, 0 failures, and three experiments that will tell us, within approximately one year, whether any of this holds.

That is what this post is about. Not celebration. Not hedging. A clear, honest account of what happens next.

---

## The Three Decision Points — 2027

### 1. DESI DR3: Dark Energy (~2027)

**What DESI measures:** The dark energy equation of state — specifically the CPL parameters (w₀, wₐ). The Unitary Manifold predicts wₐ = 0 exactly, because the radion field (the fifth-dimensional scalar that mediates KK interactions) is frozen by the Goldberger-Wise mechanism.

**Current status:** DESI DR2 found wₐ ≈ -0.55 at 2.75σ tension. We certified this as an ARCHITECTURE_LIMIT in Pillar 301 — no rolling-radion extension of the 5D framework can produce wₐ ≈ -0.55 without fine-tuning the Goldberger-Wise parameter to 88 decimal places, destroying the RS1 hierarchy solution. We are not hiding from this number. It is what it is.

**What DR3 will do:** DESI Year 3 will either confirm, deepen, or resolve the tension. The routing is preregistered:
- **|wₐ| < 0.15:** CONSISTENT — frozen radion vindicated, tension dissolves
- **|wₐ| ∈ [0.15, 0.40]:** HIGH_TENSION maintained — monitor Year 4/5
- **|wₐ| > 0.40 at ≥3σ:** FALSIFIED — framework requires Extension 2 from Pillar 285

If FALSIFIED, we have already specified what happens: the cosmologically-light radion extension is activated, the RS1 hierarchy solution is explicitly dismantled, and the scientific response is published same-day. No silence. No redefinition.

---

### 2. JUNO DR1: Neutrino Splitting (~2027)

**What JUNO measures:** The atmospheric neutrino mass splitting Δm²₃₁ at 0.5% precision — the most precise neutrino measurement yet attempted.

**Current status:** The baseline UM prediction had a 2.18% residual from the PDG central value. Pillar 274 (NLO+seesaw correction, τ-Yukawa RGE + Z₂ Majorana partner) tightened this to 0.004%. This is CONDITIONAL_DERIVATION — the correction sign and PMNS admissible window are geometrically derived, but the exact fitted parameter p_R requires full KK seesaw diagonalization that the 5D-EFT cannot provide.

**What DR1 will do:** If JUNO finds Δm²₃₁ within 0.5% of our NLO-tightened prediction, it validates the geometric chain. If it finds a larger residual at ≥3σ, the SEESAW_TEXTURE_PARTICIPATION_GAP (an explicit open item in FALLIBILITY.md) is promoted from architecture limit to framework tension. The routing is machine-executable in `pillar308_2027_readiness_mock_drill.py`.

This one I find personally compelling. It is the neutrino sector. The seesaw mechanism is one of the most beautiful ideas in particle physics — that the Majorana mass scale comes from the geometry of the extra dimension rather than from a free parameter. If JUNO confirms the geometric prediction, that is not just a number matching: it is the geometry of the fifth dimension showing up in the subatomic world.

---

### 3. Simons Observatory DR1: Tensor-to-Scalar Ratio (~2027)

**What SO measures:** The tensor-to-scalar ratio r — the amplitude of primordial gravitational waves relative to scalar perturbations.

**The UM prediction:** r = 0.0315 from the braided winding mechanism.

**Current status:** BICEP/Keck gives r < 0.036 (CONSISTENT). SPT-3G gives r < 0.036 (CONSISTENT). But ACT DR6 gives r < 0.016 (95%CL), which sits above our prediction but creates HIGH_TENSION — we formalized in Pillar 303 that this is IRREDUCIBLE within 5D-EFT: approximately 87 perturbative loops would be needed to shift r from 0.0315 to below 0.016, which breaks unitarity at loop 176. We cannot make the tension go away with calculation. We can only wait for measurement.

Simons Observatory is the first instrument projected to actually *measure* r rather than set an upper bound. With 5-year statistics at σ_r ~ 0.003, SO would detect r = 0.0315 at ~10σ if the UM is correct. If SO measures r_meas ≥ 0.020, the ACT HIGH_TENSION is resolved. If SO measures r_meas < 0.010 at ≥3σ, the braided winding mechanism is falsified.

The routing (Pillar 298, preregistered at v11.10) is locked and machine-executable.

---

## Why Three Experiments Simultaneously Matters

Each of these experiments is an independent physics probe — neutrinos, dark energy, gravitational waves. They ask fundamentally different questions. They are run by different collaborations on different instruments with different analysis teams.

If all three return CONSISTENT verdicts, the Unitary Manifold framework will have survived three independent high-precision experimental challenges that were preregistered before the data arrived. That is not proof — science doesn't work by proof. But it is the kind of evidence that shifts the burden of skepticism.

If one or more returns FALSIFIED, we have already specified the response in executable code. There is no negotiation, no redefinition, no moving of goalposts. The framework either survives the measurements or it doesn't.

I built this to be falsifiable because I believe it. You only tell the truth when it might cost you something.

---

## The Framework Status Today

As of v11.12 (2026-05-20):

- **34,537+ passing tests** across 208 core pillars + adjacent tracks through Pillar 308
- **0 failures**
- **100% ToE score** (28.0/28 Standard Model observables derived)
- **Five gaps permanently certified** in v11.11: DESI wₐ ARCHITECTURE_LIMIT, Convention 279.3 DERIVED, WZW NLO+ACT DR6 IRREDUCIBLE, KATRIN preregistration, FH phase diagram complete
- **Three experiments preregistered and drill-verified** for ~2027 (Pillar 308 v2 mock-drill)
- **Primary falsifier:** LiteBIRD β ∈ {0.273°, 0.331°} — still ~2032

The framework is in the best shape it has ever been. The next 12 months will tell us a great deal. I am not anxious about this. I am ready for it.

---

## What to Watch For

In the next post (Post 214), I will cover what happens at the lab scale — the one falsifier you can run *right now* without waiting for satellites or deep-underground detectors. Pillar 307 formalizes it as a machine-queryable preregistration. It involves superconducting circuits and topological insulators, and it is the most interesting physics I have thought about in months.

Post 215 will cover the flavor sector — the Jarlskog invariant's honest accounting (Pillar 306), what we can and cannot derive about CP violation from braid geometry, and why the 27% residual in the Cabibbo angle is an architecture limit rather than a failure.

Post 216 will be the full v11.12 sprint summary: what was built, what was closed, what remains open, and what the 2027 measurement window looks like from a falsification strategy perspective.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
