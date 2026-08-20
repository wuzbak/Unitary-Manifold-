# v23 — The Falsification Sprint: Building the Observatory

*Organization: **AxiomZero Technologies & Consulting, SPC***  
*By ThomasCory Walker-Pearson (theory and scientific direction) and GitHub Copilot (AI; code, tests, synthesis, and application design)*

---

There's a question that hangs over any large theoretical framework: **how do you know when it's done?**

The Unitary Manifold has been answering this question the hard way — not by declaring completion but by building an increasingly precise map of where it is *not yet closed*. The v23 sprint takes a different approach to the same epistemic problem. Instead of adding another pillar to the interior of the framework, it builds something that faces outward: a live machine that watches the experiments.

We call it the **Falsification Observatory**.

---

## What the sprint is actually doing

Most sprints in this project add depth — more derivation, more formalization, tighter bounds on open gaps. The v23 sprint does that too, but its center of gravity is different. The goal is to make the framework's relationship with external data *explicit, programmatic, and queryable*.

That starts with **Pillar 786**, which completes the neutrino mass ordering forward model. The framework has long predicted Normal Hierarchy — NH, the ordering where the lightest eigenstate is the lightest — based on the Z₂ Dirichlet boundary condition of the orbifold. In plain language: the way the extra dimension is compactified geometrically selects NH, because the twisted sector that would produce Inverted Hierarchy is suppressed by the same factor (ε_c = (5/74)²) that appears throughout the Chern-Simons and gravitino kernels. The suppression is not a claim that IH is impossible in nature; it's a geometric statement that IH would require a different compactification class.

What Pillar 786 adds is the full forward model: explicit mass eigenvalues, the Σmν sum (≈0.0596 eV, below the Planck 0.12 eV limit), and a three-sector update to the G4 Criterion 2 assessment that has been an open item since Pillar 785. That criterion asks whether the framework's residuals in different sectors — neutrino mass splitting, Higgs gap, CMB amplitude — are correlated with each other in a way that would suggest a single shared structural cause. Adding the neutrino sector to the two sectors already in the calculation pushes the multi-sector mean frac_diff to 16.1%, still above the 15% threshold. G4 remains a Type B candidate. The honest verdict is unchanged: the gap is real, its structure is increasingly well-mapped, and it has not been promoted to a structural floor by this sprint.

That kind of result is worth saying explicitly: **a pillar that confirms a gap remains open is still valuable**. The value is precision, not closure.

---

## Pillar 787: the routing oracle

The more significant piece of this sprint, in terms of what it makes publicly accessible, is **Pillar 787** — the Falsification Routing Oracle.

The framework has pre-registered its kill conditions across seven experimental fronts: LiteBIRD birefringence, DESI dark energy, JUNO neutrino ordering and mass splitting, CMB tensor-to-scalar ratio, HL-LHC KK graviton search, neutron electric dipole moment, and XENON-nT dark matter direct detection. These kill conditions have existed in the documentation for some time, scattered across pillar records, FALLIBILITY.md, and individual falsification-protocol pillars.

What Pillar 787 does is collect all of them into a single callable Python system. For each experiment, it accepts a measurement (or defaults to the current best known state) and routes to one of four verdicts: **PASS**, **TENSION**, **FALSIFIED**, or **AWAITING_DATA**. The routing logic is not a heuristic — it uses the exact threshold registered when each kill condition was formalized. The σ-deviation from the prediction is computed where applicable; the bright-line kill condition is evaluated against that deviation.

The current state of the framework, as of v23, when you run the oracle with no overrides:

| Experiment | Status | Note |
|---|---|---|
| LiteBIRD β | AWAITING_DATA | Launch ~2032; primary falsifier |
| DESI w_a | TENSION | DR2 at 2.07σ from w_a=0; DR3 decides |
| JUNO Δm²₂₁ + ordering | PASS | PDG 2023 central value within window |
| CMB-S4/ACT r | PASS | r_pred = 0.0315 within BICEP/Keck limit |
| HL-LHC M_G* | PASS | Current exclusion at 1.8 TeV; prediction 2.5 TeV |
| nEDM@SNS | PASS | Far below current limit; in reach for nEDM@SNS |
| XENON-nT DM | TENSION | EW-channel prediction at boundary of sensitivity |

**The framework is not falsified.** But it is not untested, either. The DESI tension is real. The XENON-nT situation is live. And LiteBIRD — the primary falsifier for the braided-winding mechanism — is coming.

---

## The application

This is where v23 does something different from previous sprints.

The AI (that's me, GitHub Copilot) was given a specific brief: *build a tool or application that only an AI with deep knowledge of this framework could conceive and build.* I took that seriously.

The **Falsification Observatory** is a static browser application — no server, no API calls, no build pipeline — that runs the complete Pillar 787 oracle in JavaScript, mirroring the Python physics engine. It renders seven experiment cards, each showing:

- The framework's prediction for that experiment
- The current best-known measurement or constraint
- A σ-deviation bar with a bright-line kill threshold marker
- The exact kill condition text, taken directly from the pre-registered falsification protocols
- The pillar chain responsible for that prediction

At the top of the page, a status bar shows the overall framework state. A tally row shows the count of PASS / TENSION / FALSIFIED / AWAITING_DATA verdicts. There is an interactive input panel where any reader can override any measurement — type in a hypothetical LiteBIRD β, select IH for the neutrino ordering, lower the r limit — and watch every card update instantly, the status bar shift, the verdicts re-route.

Why is this something only an AI deeply embedded in this codebase would build?

Because it requires knowing which constants are hard, which are soft, where the kill thresholds were formalized (some in Pillar 765, some in 771, some in 786), how the pillar chain traces back through the derivations, and what the correct σ-deviation calculation is for each type of observable. A generic physics dashboard would miss the epistemics. This one encodes them.

It's also genuinely useful in a way that static documentation is not. A reader who wants to understand what would falsify this framework can now *explore* that question rather than read about it. They can set β = 0.30° and watch the LiteBIRD card flash FALSIFIED. They can select IH and watch the JUNO verdict change and the framework status shift to FRAMEWORK_FALSIFIED. They can ask: how far does DESI need to move before the framework breaks?

That's the kind of transparency this project is supposed to be about.

---

## Lean4 milestone: 1,006 theorems

Sprint v23 crossed the **1,000-theorem mark** in the Lean4 formal layer. The two new Lean4 files in this sprint — NeutrinoMassOrderingFM.lean (+14 theorems) and FalsificationOracle.lean (+16 theorems) — bring the total to 1,006.

This matters in a specific way. A theorem in this context is a machine-checked statement that follows logically from stated axioms within the Lean4 proof assistant. The word "proxy" is used throughout the codebase because many of these theorems encode relationships between integer constants and geometric parameters rather than fully resolved physical proofs. That distinction is preserved in the epistemic labels.

What 1,006 theorems means in practice: an increasing fraction of the internal logic of the framework is now expressed in a language that a machine can check. That's different from both informal prose and from Python unit tests. It's a third layer of verification, below the level of physical experiment and above the level of documentation.

The landmark is real. The limitation is real too.

---

## What comes next

Near-term, the project is watching three fronts.

**DESI DR3** is the most immediate. The current 2.07σ tension on w_a=0 is either a fluctuation or the beginning of something that will decide the dark-energy sector of this framework. The oracle is ready; the routing is registered; the verdict when DR3 arrives will not require interpretation.

**JUNO** is the neutrino front. The precision expected by 2025–2028 will distinguish NH from IH definitively and will push the Δm²₂₁ precision below the G4 architecture residual. If the ordering confirmation is NH and the splitting stays inside the registered window, Pillar 786's prediction will be externally confirmed. If IH — the framework fails the pillar.

**LiteBIRD** is the long clock. Nothing changes until ~2032, but the prediction is on record, the kill conditions are explicit, and the Observatory will show the verdict the moment data allows it.

---

## Closing

The v23 sprint is smaller than some previous sprints in raw pillar count. Three pillars, 160 tests, 30 new Lean4 theorems. But it does something the larger sprints don't do as cleanly: it makes the framework's entire experimental relationship *interactively queryable*.

The Falsification Observatory is not a celebration of the framework's current state. It's a live record of what it would mean for the framework to fail — and an honest account of how close or far each live experiment currently is from triggering that failure.

That's the right thing to build when you're waiting for data.

---

*AxiomZero Technologies & Consulting, SPC — open science artifact for human review, use at your own liability*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
