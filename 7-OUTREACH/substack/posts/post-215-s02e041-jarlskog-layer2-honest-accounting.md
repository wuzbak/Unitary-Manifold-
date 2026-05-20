# Post 215 — S02E041: The 27% Gap — Honest Accounting of Jarlskog Layer 2

*Substack — Season 2, Episode 41*
*Published: 2026-05-20*
*Series: The Falsification Decade*

---

## On Honest Gaps

One of the commitments this framework makes — in FALLIBILITY.md, in the OBSERVATION_TRACKER, in every sprint summary — is that honest gaps are documented clearly, permanently, and without minimisation. Not as footnotes. Not as caveats buried in appendices. As explicit, machine-readable admission records.

This post is about one of those gaps. It is one I find intellectually satisfying to explain, even though — or perhaps because — we cannot close it.

---

## The Jarlskog Invariant: A Two-Layer Problem

The Jarlskog invariant J is the single number that encodes the amount of CP violation in the Standard Model quark sector. PDG value: J ≈ 3.08 × 10⁻⁵. It appears in every calculation involving CP-violating processes — kaon decay, B-meson oscillations, and ultimately (via the matter-antimatter asymmetry) why the universe exists at all.

The Unitary Manifold addresses J in two layers.

**Layer 1 — closed (Pillar 145):** CP violation is geometrically required. The braid pair (n₁, n₂) = (5, 7) has n₁ ≠ n₂. This asymmetry means the up-type and down-type quark wavefunctions receive *different* braid phases: φ_u = arctan(5/7) ≈ 35.54° for up-type, φ_d = arctan(7/5) ≈ 54.46° for down-type. Their difference is δ = 18.93° — locked by the winding ratio, not a free parameter. J ≠ 0 if and only if n₁ ≠ n₂. This is a theorem about the geometry of the vacuum, derived in full, with tests. **CLOSED.**

**Layer 2 — open (Pillar 306, this sprint):** The full PDG Jarlskog is J = J_angle × J_mass, where J_mass encodes the quark mass hierarchy. Our geometric construction gives J_angle ≈ 0.024 — the mixing-angle sector, from braid geometry alone. J_mass = J_PDG / J_angle ≈ 1.28 × 10⁻³. The question: can the UM geometry constrain J_mass independently?

The answer, honestly: not within 5D-EFT.

---

## The Cabibbo Angle and the 27% Residual

Pillar 306 attempts the best geometric constraint available. The braid opening angle predicts the dominant off-diagonal CKM element — the Cabibbo angle:

    sin(θ_C)_geometric = 1 - n₁/n₂ = 1 - 5/7 = 2/7 ≈ 0.286

The PDG value is sin(θ_C)_PDG ≈ 0.2253.

Residual: |0.286 - 0.2253| / 0.2253 ≈ 27%.

That 27% is the Layer 2 gap. It is not small. But it is not a failure, either — here is why.

The geometric construction captures the *topology* of quark mixing — the fact that 5/7 is the ratio of the winding numbers, and that ratio is what breaks the Cabibbo universality. The 27% residual is the piece that requires precise Yukawa texture diagonalization: knowing exactly how the quark wavefunctions overlap in the bulk, which modes dominate, how the KK tower mixes the generations.

That calculation — full KK seesaw diagonalization with texture matrices — requires string-theory-level Yukawa textures, not 5D-EFT. It is an architecture limit. The same architecture limit that causes the SEESAW_TEXTURE_FULL_DIAGONALIZATION gap for neutrinos.

This is documented honestly in FALLIBILITY.md Admission 7: "Jarlskog Invariant Absolute Value: OPEN — not hidden." The status in Pillar 306 is: CONSTRAINT_WITH_ARCHITECTURE_LIMIT_ACKNOWLEDGED.

---

## What "Constraint" Actually Means Here

Let me be precise about what the geometric calculation does and does not achieve.

**What it achieves:**
- Proves CP violation is geometrically required (J ≠ 0 from n₁ ≠ n₂) — Layer 1, CLOSED
- Derives the order of magnitude of quark mixing: sin(θ_C) ~ 2/7 (27% from PDG)
- Predicts the braid geometry signature of CP violation: J_geo ≈ 0.024 (the mixing-angle factor)
- Provides a structural prediction for the ratio of CKM off-diagonal elements

**What it does not achieve:**
- Independently predicting sin(θ_C) = 0.2253 from geometry alone, without Yukawa input
- Closing the 27% residual to < 5% inside 5D-EFT
- Providing the full texture matrix that gives J_mass = 1.28 × 10⁻³

The difference between these two lists is the architecture limit. It is not a failure of the framework — it is an honest statement of what 5D-EFT can and cannot do without string-theory-level inputs.

---

## The n_w χ² Tracker

Pillar 306 also formalises the second open item from the flavor sector: the winding-number uniqueness question. After hard geometric cuts (Z₂ parity, three-generation stability), only n_w ∈ {5, 7} survive. The APS η̄ discriminator (Pillar 302) selects n_w = 5 as the APS-non-trivial primary cycle. Pillar 306 adds the Planck n_s χ² quantitative preference:

    n_w = 5: χ²(n_s) = 0.111 — CONSISTENT
    n_w = 7: χ²(n_s) = 4.183 — DISFAVOURED at 2.04σ
    
    Likelihood ratio: P(n_w=5) / P(n_w=7) ≈ 7.6 from Planck n_s alone

So n_w = 5 is preferred over n_w = 7 by a factor of ~7.6 from CMB data, combined with the APS structural discriminator. But the remaining open item — a fully action-level uniqueness proof excluding n_w = 7 without any observational input — is explicitly retained as an open problem in FALLIBILITY.md Admission 3.

We document this as: NW_CHI2_TRACKER_STATUS = "QUANTIFIED_PLANCK_PREFERENCE_TABULATED".

The quantitative preference is real, derived, and tabulated. The gap is also real, acknowledged, and not closed by the quantification. Both things are true simultaneously.

---

## Why This Matters

The reason I write these posts about honest gaps is not self-flagellation. It is strategy.

A framework that hides its gaps does not survive contact with serious scrutiny — it gets destroyed the first time a physicist asks the question the framework cannot answer. A framework that documents its gaps openly, precisely, and in machine-readable form does something more valuable: it tells you exactly where to look for the next advance.

The Layer 2 Jarlskog gap tells you: if you want to close this framework on the flavor sector, you need a geometric derivation of the Yukawa texture matrices from the orbifold fixed-point structure — at the string-theory level. That is a well-posed research question. It is not hopeless. It is just not achievable within the current architecture.

That is the honest state of affairs. I would rather write that clearly than pretend the 27% is an artifact of the calculation.

---

*Next post: v11.12 sprint summary — everything we built, everything we closed, and what the 2027 measurement window looks like.*

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
