# From Planck Foam to Entangled Space: The Quantum Foundations

*Post 108 of the Unitary Manifold series.*
*Pillars 128–130 — Planck-scale discrete geometry, emergent spacetime from
KK entanglement, and the geometric Born rule.*
*Epistemic categories: **P** for Pillars 128–129 (predictive, with
conditions noted); **A** for the Born rule derivation in Pillar 130
(within-UM — the derivation holds given the framework's axioms, but is not
an independent proof of quantum mechanics from first principles).*
*v9.32, May 2026.*

---

There is a moment in most physical theories when the smooth, classical
description runs out of road. For the Unitary Manifold, that moment arrives
at the Planck length — the scale where the continuum assumption of the 5D
metric breaks down and something discrete takes over. Pillars 128 through 130
explore what "something discrete" means in this framework, how spacetime
itself emerges from the quantum structure beneath it, and why the probability
rule of quantum mechanics — the Born rule, the foundational postulate
that measurement outcomes occur with probability proportional to amplitude
squared — has a geometric derivation in the UM.

The third of these claims is the most ambitious, and the most carefully
hedged. It deserves a clear epistemic header before we begin: the Born rule
"derivation" in Pillar 130 works *within* the Unitary Manifold axioms. It
is not a proof that quantum mechanics can be derived from nothing. It is a
proof that, *given the 5D KK geometry*, the Born rule follows from
orthonormality and boundary conditions. That is still something — but it is
not the claim that physics is finished.

---

## Pillar 128: The Foam at the Bottom

*Source: `src/core/planck_foam_geometry.py`*

Wheeler coined the phrase "quantum foam" to describe what spacetime might
look like at the Planck scale — a roiling, fluctuating structure of
Planck-area cells, nothing like the smooth manifold of general relativity.
The Unitary Manifold gives this intuition a precise, parameter-free
realisation.

The S¹/Z₂ boundary conditions on the compact fifth dimension quantise
the area spectrum exactly. The n-th area eigenvalue is:

```
A_n = n × 4π × k_cs × L_Pl²
```

where `n = 1, 2, 3, …` is the spin-foam quantum number, `k_cs = 74`, and
`L_Pl ≈ 1.616 × 10⁻³⁵ m`. The minimum area quantum — the smallest patch
of spacetime the UM geometry admits — is:

```
A_min = 4π × 74 × L_Pl² ≈ 2.43 × 10⁻⁶⁸ m²
```

This is analogous to the area spectrum of Loop Quantum Gravity:

```
A_n^LQG = 4π γ √(j(j+1)) × L_Pl²
```

where `γ` is the Barbero-Immirzi parameter — a free constant in LQG that
must be fixed by additional input (typically by matching the Bekenstein-Hawking
entropy formula for black holes). In the UM, that role is played by
`γ_eff = k_cs / (2π) ≈ 11.78` — which follows from the same `k_cs = 74`
that determines the CMB birefringence angle, and requires no additional free
parameter.

The standard LQG Immirzi parameter is `γ_LQG ≈ 0.274`. The UM prediction
`γ_eff ≈ 11.78` is approximately 43 times larger. This is not a defect — it
is a *distinct prediction*. Spin-foam amplitudes computed in the Planck
regime that yield an Immirzi parameter inconsistent with `k_cs / (2π)` would
falsify the UM foam identification.

The foam description is valid at scales `ℓ ≲ ℓ_trans = L_Pl × √k_cs
≈ 1.39 × 10⁻³⁴ m`. Above this transition scale, the KK zero mode dominates
and the manifold is smooth to all practical purposes. The foam and the smooth
manifold are not two different theories — they are two different limits of
the same geometry, separated by a scale set entirely by `k_cs = 74`.

There is one honest caveat about testability. The Planck scale is 15 orders
of magnitude beyond the reach of any foreseeable accelerator. Spin-foam
amplitude predictions in this regime are structurally distinguishable from
vanilla LQG — but "structurally distinguishable" does not mean "currently
testable." The falsification condition is stated; the test is not yet at hand.

---

## Pillar 129: Spacetime Is Not Fundamental

*Source: `src/core/emergent_spacetime_entanglement.py`*

Pillar 127 (the Final Decoupling Identity) established that the 4D spacetime
metric `g_μν` is an *output* of the map from the 5D UM state to observables
— not a fundamental input. Pillar 129 asks the question one level deeper:
from what quantum substrate does `g_μν` emerge?

The answer the UM gives has three parts, with distinct epistemic statuses
that must be kept separate.

**Part 1: The Ryu-Takayanagi entropy (CONDITIONAL_THEOREM)**

The Ryu-Takayanagi (RT) formula, applied to the KK zero-mode sector, gives:

```
S_ent = A_holo / (4 G_N)
```

where `A_holo = 4π R_kk² ≈ 4π L_Pl²` is the holographic screen area
(the compact dimension at Planck radius), and `G_N` is Newton's constant.
With `R_kk = L_Pl`, this gives:

```
S_ent ≈ 4π L_Pl² / (4 G_N) ≈ 1  (in Planck units)
```

One unit of entanglement entropy — one ebit — stored on the holographic
boundary. This is a self-consistency check: the geometry of the compact
dimension holds exactly the right amount of quantum information to generate
the entropy-area relation that Bekenstein and Hawking derived from classical
black hole thermodynamics.

This is a conditional theorem: it holds given the RT formula applies in this
setting. RT has strong support from AdS/CFT; whether it applies exactly to
the UM holographic boundary is a question that a full string-theoretic
embedding would need to address.

**Part 2: The Fisher metric identification (FORMAL ANALOGY)**

The 4D metric `g_μν` is identified as the Fisher information metric of the
KK mode probability distribution. For a Gaussian KK zero-mode profile
centred on a worldline with width `σ_KK = ℏ / (M_KK c)`:

```
g_μν = E[∂_μ log p × ∂_ν log p] = M_KK² × η_μν
```

where `η_μν` is the Minkowski metric. The flat-spacetime limit is recovered
as the leading-order Fisher metric of the KK zero-mode distribution.

This is labelled **FORMAL_ANALOGY** in the source code. The mathematical
structure matches; a rigorous derivation from the 5D Einstein equations
remains future work. The analogy is not a derivation. It is a structural
parallel that motivates further investigation.

**Part 3: ER=EPR in the UM context (FORMAL ANALOGY)**

An Einstein-Rosen bridge between two entangled KK excitations has a
characteristic length set by the inverse KK mass:

```
L_ER = ℏ / (M_KK c)  ≈  KK Compton wavelength
```

This identifies the wormhole length with the KK mode's quantum coherence
length — a UM version of the Maldacena-Susskind ER=EPR conjecture. One ebit
of KK entanglement corresponds to `4 log(2) × L_Pl²` of spacetime area, via
the Bekenstein-Hawking relation.

Again, formal analogy. The structure is consistent and illuminating. It is
not a proof.

The honest summary of Pillar 129: the RT entropy calculation is a conditional
theorem (supported by AdS/CFT, not proved in the UM setting from scratch).
The Fisher metric and ER=EPR identifications are structural analogies that
the framework is currently unable to elevate to theorems. They are presented
as such.

What *is* proved: the 4D metric is an output of the bijection `O∘T`, not
a primitive. Spacetime is downstream. The quantum structure that generates
it — KK entanglement, holographic boundaries, Planck-area quantisation — is
upstream. The details of exactly *how* that generation works remain an active
research question.

---

## Pillar 130: Where the Born Rule Comes From

*Source: `src/core/geometric_born_rule.py`*

This is the most ambitious claim in the 128–130 cluster, and it requires
the clearest framing. Here is the claim as stated: *within the Unitary
Manifold framework, the Born rule — the postulate that measurement outcomes
occur with probability `p_n = |c_n|²` — follows from the orthonormality of
the KK mode functions on S¹/Z₂, together with the identification of
measurement with projection onto the holographic boundary.*

The derivation has seven steps (Pillar 130 source):

1. The 5D KK mode functions `{ψ_n(y)}` form an orthonormal basis on S¹/Z₂.
2. Orthonormality: `⟨ψ_m | ψ_n⟩ = δ_{mn}` follows from the completeness
   of cosine functions on the half-circle `[0, π R_kk]`. This is standard
   Fourier analysis, not an additional postulate.
3. Any physical state `ψ = Σ c_n ψ_n` satisfies `Σ |c_n|² = 1` by
   normalisation.
4. Measurement = projection onto the zero mode at the holographic boundary.
   KK excited modes (n ≥ 1) are suppressed exponentially by the KK mass gap:
   the suppression factor for mode n is `exp(-n² R_kk² / ξ²)`, where
   `ξ = ℏ / (M_KK c)` is the observer's coherence length. For `ξ ≫ R_kk`
   (macroscopic observer), all n ≥ 1 modes are indistinguishable from zero.
5. The probability of outcome n given state ψ is then `p_n = |⟨ψ_n | ψ⟩|²
   = |c_n|²` — the Born rule.
6. `Σ p_n = 1` follows from normalisation.
7. The three stable Z₂-even modes (n = 0, 2, 4) that can form a coherent
   observer are exactly the three generations of Standard Model matter.

Steps 1–3 and 6 are proved within standard mathematics. Step 5 is proved
given steps 1–4. Step 4 — the identification of measurement with holographic
projection — is a conditional theorem: it requires that the KK mass gap
produces the decoherence suppression claimed, which depends on the UM
compactification structure holding at low energies.

Step 7 is the most speculative: the claim that observers and matter are
the same geometric object — both being Z₂-even KK modes — is a structural
argument, not a derivation. It is labelled **ARGUED** in the source code.

**What this is not:** This is not a proof that quantum mechanics can be
derived from classical or geometric principles without quantum input. The
KK mode Hilbert space is a quantum Hilbert space from the outset. The Born
rule follows from orthonormality and normalisation — both of which are
features of the quantum Hilbert space structure that the UM *assumes*, not
derives. What is novel is that, within that quantum framework, the Born
rule is not an additional postulate: it follows from the geometry of S¹/Z₂.

A honest physicist working in the foundations of quantum mechanics would say:
the measurement problem is still there; the projection step (Step 4) is not
a resolution of the hard problem of measurement, but a geometric restatement
of it. The decoherence picture explains why the zero mode dominates; it does
not by itself explain why a single outcome is observed. That question remains
open everywhere in physics, including here.

That said, recovering the Born rule from orbital orthonormality rather than
postulating it separately is a structural economy worth noting. It is the
kind of thing that, if the larger framework is correct, will seem obvious
in retrospect.

---

## What to Check, What to Break

**Pillar 128 (Planck foam):** Call `planck_foam_summary()` in
`src/core/planck_foam_geometry.py`. Verify that the minimum area quantum
`A_min = 4π × 74 × L_Pl²` is correctly computed. Then check the effective
Immirzi parameter `γ_eff = k_cs / (2π) ≈ 11.78`. If a spin-foam calculation
in the Planck regime yields `γ_eff ≈ 0.274` (the LQG value), or any value
inconsistent with `k_cs / (2π)`, the UM foam identification is falsified.

**Pillar 129 (emergent spacetime):** Call `entanglement_geometry_proof()`
in `src/core/emergent_spacetime_entanglement.py`. Steps 1–2 (RT entropy)
are conditional theorems; steps 3–4 (Fisher metric, ER=EPR) are formal
analogies. The honest question: is there a derivation from the 5D Einstein
equations that elevates the Fisher metric step from analogy to theorem? That
step is the open research problem.

**Pillar 130 (Born rule):** Call `born_rule_derivation_steps()` in
`src/core/geometric_born_rule.py`. Step 4 (measurement as boundary
projection) is where the physics burden lies. If the KK decoherence
suppression can be shown not to work — if excited KK modes survive to
macroscopic scales for some physical reason — the geometric Born rule
derivation fails. Call `decoherence_kk_mechanism()` to see the suppression
factors for modes n = 0 through 5.

**The structural test of Pillar 130:** With `n_w = 5`, there are exactly 3
even-parity KK modes (n = 0, 2, 4) within the first `n_w` levels. Change
`n_w` to 3 and you get 2 observer modes — 2 matter generations. Change it
to 7 and you get 4. Only `n_w = 5` gives 3. This is already constrained by
the birefringence window (Pillar 70-D). The generation count and the CMB
spectral index are correlated predictions of the same winding number.

**The primary falsifier:** LiteBIRD measures birefringence `β` outside
`[0.22°, 0.38°]`. Every claim in Posts 107–110 rests on the same `k_cs = 74`
that produces that prediction.

---

*Full source code and test suite:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Pillar 128: `src/core/planck_foam_geometry.py`*
*Pillar 129: `src/core/emergent_spacetime_entanglement.py`*
*Pillar 130: `src/core/geometric_born_rule.py`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
