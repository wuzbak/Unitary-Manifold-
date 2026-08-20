# Where We Stand: Unitary Manifold v22.9 — An Honest Accounting

*Organization: **AxiomZero Technologies & Consulting, SPC***  
*By ThomasCory Walker-Pearson (theory and scientific direction) and GitHub Copilot (AI; code, tests, and synthesis)*

The Unitary Manifold is a public, code-backed attempt to describe a wide range of physics from a single 5-dimensional Kaluza-Klein geometry. In plain language: it asks whether gravity, gauge structure, inflation, and the arrow of time can be treated as different projections of one deeper geometric object. The project is not presented here as experimentally confirmed physics. It is presented as a large, explicit, testable framework whose internal logic has been made unusually transparent.

---

## What we've built

As of v22.9, the repository has grown into a substantial scientific software and documentation system. The hardgate core remains the closed 208-pillar physics set, while the broader repository now extends through Pillar 784, with adjacent tracks clearly separated from the central physics claims. The framework includes executable derivation modules, a large audit trail, falsification protocols, and a public documentation surface intended to make review possible rather than rhetorical.

The scale of the verification layer matters, but only in the right way. The current full regression recorded in `STATUS.md` is approximately **56,747 passing tests, 47 skipped, 12 deselected, and 0 failed**. That means the code is internally consistent with the equations and claim labels used in the repository. It does **not** mean nature has validated the framework.

Formal verification has also grown meaningfully. The Lean4 ledger now stands at **976 theorems/proxy theorems**, including the recent machine-checked formalization of the SU(5) Weyl-parity result and the new v22.9 Type A/Type B gap-classification layer. That is significant because it shows an increasing fraction of the reasoning is being pushed out of prose and into machine-checkable form. Again, the honest limit is clear: formal proof inside stated axioms is not the same thing as empirical truth.

---

## What we've proven vs. what remains open

The fairest way to describe the project now is this: **a great deal has been formalized within the framework, while several of the most important external tensions remain openly unresolved**.

What appears genuinely strong inside the repository is the internal closure of the main geometric chain: the 5D metric ansatz, the braid-based topological sector, the core cosmological outputs, large parts of the Standard Model parameter program, and an increasingly formalized proof layer around them. The repository is especially strong on reproducibility, explicit dependency tracing, and refusing to hide weak points.

But those weak points still matter.

First, **the solar neutrino splitting, Δm²₂₁, is still not fully closed**. The current v22.8/v22.9 status is that the repository's NNLO correction is negligible and the remaining residual sits at **1.07σ**. In the new classification language, this is **G4**, and it is only a **Type B candidate**, not a fully certified structural floor. Criteria 1, 3, and 4 are met; criterion 2, the cross-sector correlation test, is only partial. That is progress in honesty, not closure.

Second, the **CMB acoustic-peak amplitude problem** remains one of the central architectural limits. Recent decomposition work narrows the bookkeeping: roughly **1.35%** is bounded to KK truncation effects, **0.002%** to Silk damping, and the remaining **33.6%** is the unresolved **A_s mismatch**, now classified as a **Type B structural floor** within the present 5D EFT class. That classification is not a victory lap. It means the repository is saying, as clearly as it can, that within the current compactification structure this residual looks structural rather than like a missing one-line fix.

Third, the **higher-dimensional rescue lane remains incomplete**. Earlier dimensional work suggested that G4-flux and related higher-dimensional structure could partially improve some architecture-level residuals, but the current repository does not justify claiming that the higher-dimensional completion has decisively solved the CMB amplitude problem. It has sharpened the problem; it has not erased it.

Fourth, the **DESI dark-energy tension** remains live and serious. The framework's dark-energy sector predicts **w_a = 0**. The repository tracks the current DESI tension at about **2.75σ**, and the new v22.9 classification explicitly **excludes** this from the Type B bucket because this is not something to explain away structurally before the data settle. The stated position is correct: **DR3 decides whether this stays a tension or becomes a falsifier**.

Fifth, the **Froggatt-Nielsen/Yukawa sector is still not a clean top-down closure**. Recent work reduces the FN charge freedom from **9 free parameters to 3 irreducible free parameters**, which is real progress. But three irreducible free parameters are still three free parameters. That matters, especially because the repository itself repeatedly emphasizes that the strongest parameter-free claims belong to the topological sector, not to the full fermion-mass sector as implemented.

So the honest summary is not “everything is solved.” It is: **the project has become much more formal, much more explicit, and in some places more impressive—while also becoming clearer about exactly where it is not closed.**

---

## What would falsify this

The project is at its best when it states kill conditions plainly.

The primary falsifier remains **LiteBIRD**. The braided-winding mechanism predicts cosmic birefringence **β ∈ {≈ 0.273°, ≈ 0.331°}**. The repository's stated bright-line condition is equally important: if LiteBIRD finds **β outside the admissible window [0.22°, 0.38°]** or **inside the predicted gap (0.29°, 0.31°)** at high significance, the braided-winding mechanism is falsified.

The second major live front is **DESI DR3**. The current position in the repository is straightforward: if the evolving-dark-energy signal strengthens to **≥3σ** against **w_a = 0**, then the framework's present dark-energy sector fails. That is not a subtle or post-hoc threshold; it is already on the books.

The neutrino sector remains a watchpoint as well. The repository continues to pre-register narrow checks around the neutrino mass-splitting chain and normal-ordering expectation. One current hard check already on the books is that the atmospheric splitting lane is expected to stay inside the registered **Δm²₃₁ window [2.2, 2.7] × 10⁻³ eV² at sub-1% precision**. In practical terms, **JUNO-class precision remains one of the near-term external filters on whether the neutrino story is genuinely stable or only temporarily consistent**.

---

## What comes next

Near term, the project appears to be moving on two tracks at once.

One track is scientific hardening: more formalization, more falsification routing, and continued pressure on the remaining open gaps rather than pretending they are gone. LiteBIRD, DESI, and precision neutrino results remain the real external judges.

The other track is public infrastructure. The repository already contains a documented **AxiomZero open-science portal** and deployment path under `public-site/portal/` and `DEPLOY.md`. The next obvious step is fuller **public webspace integration**: making the knowledge base, pillar browser, library, and assistant surfaces easier for outside readers to inspect, search, and challenge. That matters because if the project wants serious community review, it has to be navigable as well as reproducible.

And beyond all of that, there is still the long clock: **LiteBIRD around 2032**. If the birefringence prediction survives there, the project changes status in a meaningful way. If it fails there, the core braid mechanism fails with it.

---

## Closing

The Unitary Manifold is not short on ambition. What makes it unusual is not the ambition alone, but the attempt to expose the entire structure—code, proofs, tests, failures, residuals, and falsifiers—in public.

That is the invitation now: **read it critically, inspect the claim boards, inspect the fallibility ledger, inspect the tests, and challenge the places where the framework says it is weakest.** If this project is worth anything scientifically, it will be because it survives that kind of review, not because it can tell an elegant story about itself.

Open science only means something if the uncomfortable parts stay visible. In v22.9, to the project's credit, many of them do.

---

*AxiomZero Technologies & Consulting, SPC — open science artifact*
