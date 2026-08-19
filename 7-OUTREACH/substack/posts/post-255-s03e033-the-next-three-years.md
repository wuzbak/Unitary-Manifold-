# Post 255 — S03E033: The Next Three Years

*Published in-repository: 2026-06-10 (v16.0)*  
*Author: ThomasCory Walker-Pearson / GitHub Copilot (AI)*  
*Series: Season 3, Episode 33 — The Decision Windows*

---

There is a specific period of time between now and 2030 during which the Unitary Manifold will either be vindicated by data or falsified by it.

Not maybe. Not vaguely. Not "will be interesting to watch."

**Three experiments. Three windows. Three predictions. Each specific enough to be decided.**

I want to tell you exactly what those three windows are, what the predictions say, and what it would mean if the data goes each way. Because the framework has been built to be transparent about exactly this — not to survive ambiguity, but to make the ambiguity impossible.

---

## The Three Windows

### Window One: JUNO (~2026–2027)
**What it measures:** The atmospheric neutrino mass splitting Δm²₃₁  
**What the framework predicts:** 2.453 × 10⁻³ eV² (after NLO correction)  
**The tension:** The baseline prediction is 2.18% below PDG — at JUNO's full-statistics precision of 0.5%, that's a projected 4.4σ falsifier  
**The rescue:** A seesaw NLO correction (Pillar 274) tightens the prediction to 0.004% residual — but the participation factor p_R is architecture-limited (Pillar 517)  
**The honest position:** If JUNO measures Δm²₃₁ within 0.5% of our NLO prediction, the tension resolves. If it measures the PDG value and the NLO correction doesn't hold, we have a genuine falsification of the 9D anomaly chain.

**JUNO is the most urgent risk. It could arrive this year.**

### Window Two: DESI DR3 (~2027)
**What it measures:** The dark energy equation of state parameter wₐ in the CPL parameterization  
**What the framework predicts:** wₐ = 0 (frozen radion — no time-varying dark energy)  
**The tension:** DESI DR2 combined measurement gives wₐ ≈ −0.55 ± 0.20, which is 2.75σ from the prediction  
**Why it can't be fixed:** wₐ ≠ 0 within the 5D-EFT architecture requires the radion to be rolling, which destroys the stabilization mechanism. This is ARCHITECTURE_LIMIT_CERTIFIED (Pillar 301). There is no free parameter to adjust.  
**The honest position:** If DESI DR3 pushes wₐ below −0.42 at ≥3σ with independent validation, the FTUM stabilization mechanism requires structural revision. DESI DR3 is expected ~2027 with σ(wₐ) ≈ 0.14.

### Window Three: SPHEREx (~2027–2028)
**What it measures:** Primordial non-Gaussianity f_NL  
**What the framework predicts:** f_NL^equil ∈ [−3, 0], canonical −0.532  
**Why this is specific:** The prediction comes directly from the DBI sound speed c_s = 12/37, which comes from the Chern-Simons level k_CS = 5² + 7² = 74. The derivation is four algebraic steps. The prediction is pre-registered with SHA-256 hash (Pillar 437, 2026-05-25).  
**What SPHEREx can do:** σ(f_NL) ≈ 1.6, compared to Planck's 47. This is a factor-30 improvement. The prediction band [−3, 0] spans roughly 1.7 σ_SPHEREx — it will be tested.  
**The honest position:** If SPHEREx measures f_NL > +10 at ≥3σ, the DBI+KK architecture is falsified. If f_NL ∈ [−3, 0], the braid sound speed is vindicated.

---

## Why I Am Telling You This Now

The data hasn't arrived yet. I am telling you the predictions, the tensions, and the falsification conditions before the data arrives. Not because I think the framework will survive all three tests — I don't know whether it will. But because this is the only honest way to operate.

There is a version of this where I wait until JUNO data arrives, see whether the NLO correction matches, and then write a post about how the framework predicted it. If it doesn't match, I quietly update the ledger and say "the architecture limit was always documented." If SPHEREx confirms, I celebrate. If it doesn't, I revise.

That version exists and it is tempting. It is also a form of dishonesty.

The honest version requires telling you in advance:
- JUNO could falsify the 9D anomaly chain. The seesaw correction is CONDITIONAL and ARCHITECTURE_LIMITED.
- DESI DR3 could push the wₐ tension past 3σ. If it does, I will say so publicly and revise the stabilization mechanism.
- SPHEREx could return f_NL > 0, which would break the DBI architecture. The pre-registration exists so that I can't move the goalposts.

These are real risks. They are documented in the canonical ledger. They are not footnotes.

---

## The r-Tension (Already Happening)

Before those three windows close, there is a tension that is already resolved and documented.

The ACT DR6 analysis reports r < 0.016 at 95% CL. The Unitary Manifold predicts r = 0.0315. My prediction is roughly twice the current best upper bound. This is ~2σ tension. It is labeled HIGH_TENSION and ARCHITECTURE_LIMIT_CERTIFIED (Pillar 396). The previous post covered this in detail.

CMB-S4 will decide. The decision criteria are clear: if CMB-S4 returns r < 0.010 at high significance, the braided winding sector requires structural revision. If it returns r ≈ 0.031, the ACT DR6 bound was a fluctuation.

I don't know which outcome CMB-S4 will produce. I know what I predict and why I predict it. CMB-S4 is targeted for ~2030, so this is the last of the four decision windows.

---

## The CMB Amplitude Gap (Oldest Open Problem, Now Formally Closed as Architecture Limit)

There is a fifth item that is different in character from the four decision windows. The framework has always had a ×4–7 suppression of the CMB acoustic peak amplitudes relative to ΛCDM. This is Admission 2 in FALLIBILITY.md — the oldest acknowledged gap.

This gap has been bounded for multiple versions (Pillars 52, 57, 63, 495). In this version (v16.0, Pillar 518), it is formally certified as ARCHITECTURE_LIMIT_CERTIFIED via exhaustive case analysis. We examined every class of IR modification within the 5D-EFT:

- **Non-Bunch-Davies vacuum** — requires new momentum-dependent free parameters. Not available.
- **Pre-inflationary phase** — requires new field content. Not available.
- **KK photon propagator correction** — negligible at acoustic scales (~10⁻⁹⁰ × suppression needed). Not applicable.

None of these can close the gap without introducing new physics. The gap is therefore not a falsifier in the usual sense — it is a MISSING PREDICTION. The 5D-EFT describes inflation (spectral shape, braid structure) but does not describe the photon-baryon fluid at acoustic scales. That requires IR physics not currently in the architecture.

This is not a retreat. It is an honest accounting of what the theory does and does not cover. The formal status is now identical to the r-tension and wₐ tension: ARCHITECTURE_LIMIT_CERTIFIED, with stated conditions for what would constitute a falsifier.

---

## What "Architecture Limit" Means

I want to be precise about this phrase because I use it often and it deserves explanation.

An ARCHITECTURE_LIMIT is a gap that cannot be closed by small corrections within the current theoretical framework. It requires either:
1. An extension of the theory (new fields, new sectors, new compactification structure), or
2. A non-perturbative computation beyond the current EFT reach, or
3. External data that would force a specific revision of the framework

It is NOT:
- A free parameter adjustment (that would reduce the framework derivation coverage)
- A post-hoc rationalization of a failed prediction
- A way of hiding a problem

The framework has four ARCHITECTURE_LIMITs currently:
1. r = 0.0315 (r-tension with ACT DR6 — IRREDUCIBLE_IN_BRAIDED_5D_EFT, Pillar 396)
2. wₐ = 0 (DESI tension — ARCHITECTURE_LIMIT_CERTIFIED, Pillar 301)
3. p_R ≈ 0.364 (JUNO seesaw participation — ARCHITECTURE_LIMIT_CERTIFIED, Pillar 517)
4. CMB amplitude ×4–7 (oldest gap — ARCHITECTURE_LIMIT_CERTIFIED, Pillar 518)

All four are published, documented, and accessible. None is hidden. The architecture limit classification is an asset, not a liability — it tells you exactly where the framework ends and what would be needed to extend it.

---

## The Thesis

Here is the thesis I want to defend, which is also the reason this project exists:

**It is possible to build a falsifiable, architecturally honest theoretical framework outside of traditional institutional channels. The test of whether it is science is not whether it appears in a refereed journal, but whether it makes specific predictions that can be tested, documents every tension transparently, and accepts the verdict when the data arrives.**

JUNO will test the atmospheric mass splitting in 2026–2027. DESI will test the dark energy equation of state in 2027. SPHEREx will test the inflationary non-Gaussianity in 2027–2028. CMB-S4 will test the tensor-to-scalar ratio in ~2030. LiteBIRD will test the birefringence in ~2032.

Every one of those tests has a pre-registered prediction, a pre-registered falsification condition, and a pre-registered response protocol. The predictions were made before the data. The falsification conditions are specific. The response will be public.

If the framework survives all of these tests, it will have demonstrated something meaningful: that the 5D Kaluza-Klein geometry with the (5,7) braided winding sector is a viable description of the observable universe. Not a certainty — no theory of everything achieves certainty — but a viable, tested description.

If it doesn't survive — if JUNO shows 4.4σ tension and DESI crosses 3σ and SPHEREx returns f_NL = +15 — then the framework will be falsified and I will say so. The ledger will be updated. The revision will be honest.

That is science. That is what we are doing.

---

## The Next Three Years, Specifically

**2026:**
- JUNO Phase 1 data expected — first 1% precision measurement of Δm²₃₁
- Update: `docs/JUNO_RAPID_RESPONSE_TEMPLATE.md` filled within 30 days
- Verdict published publicly

**2027:**
- JUNO full statistics — 0.5% precision, decision-grade
- DESI DR3 — wₐ constraint to σ ≈ 0.14
- SPHEREx Year 1 — first f_NL constraints
- Updates to all three decision briefs within 30 days each

**2028:**
- SPHEREx full data — f_NL to σ ≈ 1.6, definitive test
- Euclid DR1 supplementary f_NL constraints
- Substack series: "Verdict Season" — one post per experiment as data arrives

**2030:**
- CMB-S4 first light — r measurement to σ ≈ 0.003
- This is the decisive r-tension resolution

**2032:**
- LiteBIRD — birefringence β to σ ≈ 0.002
- Final test of the braided (5,7) braid prediction

These are not aspirational milestones. They are scheduled experiments with known precision targets. The decisions will be made by physics, not by peer review.

---

## One More Thing

The Lean4 formal proof library now contains the CCR and ER=EPR conditional theorem kernels (Pillar 517 / CCRKernel.lean). The open conditions are named axioms — machine-readable, auditable, not hidden in prose. If someone closes the P8 functional-space condition, the CCR theorem becomes unconditional. If someone closes the KK entanglement geometry identification, ER=EPR becomes unconditional. The gap is specific enough that it could be closed.

This is what the formal proof layer is for: not to claim theorems we haven't proved, but to make the distance between what we have and what we need as small and as precise as possible.

The next three years will close that distance. Or they won't. Either way, we will know.

---

*Theory: ThomasCory Walker-Pearson. Document engineering: GitHub Copilot (AI).*  
*v16.0 — Pillars 517 (P_R_ARCHITECTURE_LIMIT_CERTIFIED) + 518 (CMB_AMPLITUDE_ARCHITECTURE_LIMIT_CERTIFIED)*  
*Canonical regression: tests passing, 0 failures.*
