# TARGETED_OUTREACH_TEMPLATE.md

Repository: https://github.com/wuzbak/Unitary-Manifold-  
DOI: 10.5281/zenodo.19584531

Core technical links:  
- Tier-1 formal entry point: https://github.com/wuzbak/Unitary-Manifold-/blob/main/proof/TIER_1_FORMAL.md  
- One-command observable check: https://github.com/wuzbak/Unitary-Manifold-/blob/main/VERIFY.py

## Version 1 — CMB / cosmic birefringence specialist

**Subject:** A concrete birefringence falsifier from a 5D KK model: $\beta\in\{0.273^\circ,0.331^\circ\}$ with a forbidden gap

Hello,

I’m sending a compact pointer to a 5D Kaluza-Klein construction in the Unitary Manifold repository because it makes a genuinely narrow birefringence claim rather than a generic “nonzero rotation” claim. The core ansatz is a 5D metric with an off-diagonal irreversibility 1-form and a radion, summarized in the Tier-1 document linked above. In the repository’s canonical braided sector, the same topological integer chain that gives $k_{\rm CS}=74$ and $n_s=0.9635$ also gives two admissible birefringence modes: roughly $0.331^\circ$ and $0.273^\circ$.

The most immediate thing to check is not whether the model predicts a nonzero signal, but whether its hard gap is already implausible in your pipeline assumptions: the framework explicitly says that any future result in $\beta\in(0.29^\circ,0.31^\circ)$ is fatal even if the detection is high significance. That is the cleanest single diagnostic.

The corresponding falsification path is also simple: LiteBIRD or comparable data would kill the braided-winding sector if $\beta<0.07^\circ$, $\beta>0.50^\circ$, outside $[0.22^\circ,0.38^\circ]$, or inside the forbidden gap at $3\sigma$. `VERIFY.py` gives the repository’s compact executable chain.

What we are **not** claiming: not that internal consistency proves the cosmology, not that current hints amount to confirmation, and not that this is free of tension. The repository openly records ACT DR6 pressure on $r$ and treats LiteBIRD as the primary external verdict.

Best,
GitHub Copilot

## Version 2 — Kaluza-Klein phenomenologist

**Subject:** A 5D KK proposal with explicit failure conditions, not just a unification narrative

Hello,

I’m reaching out because this repository may be of interest as a falsifiable KK phenomenology package rather than as a broad unification manifesto. The formal core is narrow: a 5D block metric $G_{AB}$ with $g_{\mu\nu}$, an off-diagonal field $B_\mu$, and a radion $\phi$, with the Tier-1 entry point restricted to the executable metric, evolution, algebra, and verification surface.

The most relevant immediate check from a KK perspective is whether the claimed topological chain to $k_{\rm CS}=74=5^2+7^2$ is mathematically defensible on its own terms. If you only inspect one thing, I would suggest the internal logic around the $(5,7)$ sector and the claim that it propagates to $n_s=0.9635$, $r=0.0315$, and the birefringence windows without adding a continuous fit parameter at that stage. `VERIFY.py` is the shortest executable summary.

The falsification route is explicit rather than rhetorical. If CMB-S4 pushes the upper bound below $r=0.0315$ at more than $2\sigma$, or if LiteBIRD lands in the forbidden birefringence interval $0.29^\circ$-$0.31^\circ$, the framework says the canonical braided sector is dead. DESI DR3 is the separate tripwire for the frozen-radion $w_a=0$ claim.

What we are **not** claiming: not that all Standard Model structure is already first-principles derived, not that external mechanisms are absent, and not that architecture limits have vanished. The repository explicitly flags imported breaking steps and open/tension lanes.

Best,
GitHub Copilot

## Version 3 — Quantum gravity / information / irreversibility theorist

**Subject:** A geometric arrow-of-time proposal with executable checks and clear ways to refute it

Hello,

I’m sharing this because the repository’s central move is to treat irreversibility as a geometric degree of freedom in a 5D KK metric, not merely as emergent coarse-graining language. The off-diagonal field $B_\mu$ is interpreted as an irreversibility 1-form, the radion $\phi$ as an entropic dilaton, and the reduced Einstein-gauge-scalar system is treated as the core mathematical object. The narrow formal surface is here: `proof/TIER_1_FORMAL.md`.

The fastest technical check for someone working on quantum gravity or information is whether the proposal cleanly separates theorem, conditional theorem, and conjecture. The repository does try to do this. If you want one executable sanity check before reading deeper, `VERIFY.py` compresses the topological-to-observable chain into a short numerical run.

A concrete prediction you can assess immediately is the claim that a discrete Chern-Simons sector with $k_{\rm CS}=74$ leads not just to qualitative irreversibility language but to specific cosmological observables, especially birefringence and the braided suppression of $r$. A concrete falsification path is correspondingly sharp: a birefringence measurement in the interval $0.29^\circ$-$0.31^\circ$ is counted as a direct failure, not a partial success.

What we are **not** claiming: not a proof that the arrow of time has been solved in general, not a complete non-perturbative quantum-gravity closure, and not a substitute for external empirical discrimination. The repository’s own fallibility ledger keeps those boundaries visible.

Best,
GitHub Copilot
