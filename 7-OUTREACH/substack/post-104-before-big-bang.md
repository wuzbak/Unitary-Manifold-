# Before the Big Bang: What Geometry Remembers

*Post 104 of the Unitary Manifold series.*  
*Pillars 110–113 — Non-Equilibrium Attractors, Pre-Big Bang Geometry, Dimension Uniqueness, M-Theory Embedding.*  
*Epistemic category: **P** (Pillars 112–113 are geometric theorems) / **A** (Pillars 110–111 are exploratory derivations).*  
*v9.32, May 2026.*

---

There is a question that physicists are usually not allowed to ask at conferences.
Not because it is rude, but because it is unanswerable in most frameworks.
The question is: *what was happening before the Big Bang?*

In standard cosmology the question has no answer, because "before" requires time,
and time, according to general relativity, begins at the singularity.
Ask what came before and the equations hand you infinity, which is the universe's
polite way of saying: *wrong question*.

The Unitary Manifold doesn't dissolve the question. It reshapes it.

If the universe is a five-dimensional geometry — if the compact fifth dimension
is physically real — then what we call the Big Bang is not the beginning of
*everything*. It is the beginning of a specific phase. Before it, the geometry
was doing something different. The question is not unanswerable; it is a question
about phase transitions.

This post covers four pillars that probe that earlier phase: the FTUM non-equilibrium
attractors (Pillar 110), the pre-big-bang geometry (Pillar 111), the uniqueness
theorem for why the compact dimension must be exactly five-dimensional (Pillar 112),
and where the framework sits inside M-theory (Pillar 113).

---

## Pillar 110 — When the FTUM Doesn't Rest *[A]*

The FTUM (Fixed-point Topology of the Unitary Manifold) operator is the
convergence engine at the heart of the framework. Apply it repeatedly and
the system settles to a fixed point — the same φ₀ = 1 that anchors
the radion field and seeds the inflationary predictions.

But fixed points are not the only attractors.

Pillar 110 (`src/core/nonequilibrium_attractors.py`) shows that the FTUM operator
also admits *periodic attractors* — Floquet orbits in which the system oscillates
rather than settling. The Floquet eigenvalue for a periodic orbit of period τ is:

$$\lambda_F = \exp\!\left(\frac{2\pi i\, \phi_0^2}{k_{\text{cs}} \cdot \tau}\right)$$

Note that |λ_F| = 1: the orbit is marginally stable, neither growing nor decaying.
The natural period of the periodic attractor — the "time-crystal period" — is:

$$T_{\text{tc}} = \frac{2\pi\, k_{\text{cs}}}{n_w^2\, \phi_0^2}
= \frac{2\pi \times 74}{25} \approx 18.59 \text{ Planck units}$$

The attractor dimension of these orbits is $d_a = n_w - 1 = 4$ — a codimension-1
attractor inside the full five-dimensional phase space. The Lyapunov exponent is:

$$\lambda_L = \frac{\phi_0^2}{k_{\text{cs}}} (1 - \phi_0)$$

This is negative for φ₀ > 1 (stable), zero at φ₀ = 1 (marginal, the fixed point),
and positive for φ₀ < 1 (unstable). The FTUM fixed point at φ₀ = 1 is the
*boundary* between stability and instability.

The honest characterisation here is **analogy**: the mathematics is rigorous,
but whether these Floquet orbits correspond to actual physical states before
the Big Bang, or are mathematical structures without physical realisation, is
not settled. The framework opens the door; it does not walk through it.

---

## Pillar 111 — The Geometry Before t = 0 *[A]*

Pillar 111 (`src/core/prebigbang.py`) models the 5D geometry *before* the
Chern-Simons locking event that we identify with the Big Bang.

The central idea is that the (5,7) braid resonance — the event in which the
winding modes lock at k_cs = 74 — is a *geometric phase transition*. Before the
locking, the compact radius was dynamically active. After the locking, it is
frozen. The universe as we know it begins with the freeze.

The 5D metric signature is unchanged across the transition: (+,−,−,−,+) before
and after. The extra dimension stays spacelike. What changes is the compactification
radius φ₀, which transitions from a dynamical degree of freedom to a fixed parameter.

The CS locking temperature — the energy scale at which the transition occurs — is:

$$T_{\text{lock}} = \frac{k_{\text{cs}}}{n_w^2 \cdot 2\pi}
= \frac{74}{25 \times 2\pi} \approx 0.236 \text{ Planck units}$$

The width of the phase transition (the relative temperature range over which
locking happens) is:

$$\frac{\delta T}{T} = \frac{1}{\sqrt{k_{\text{cs}}}} = \frac{1}{\sqrt{74}} \approx 0.116$$

A transition with δT/T ≈ 12% is sharp but not instantaneous — it is more like
a first-order electroweak phase transition than a knife-edge discontinuity.

Before locking, the pre-Big Bang geometry accumulated e-folds of expansion:

$$N_{\text{pre}} = \frac{\phi_0^2 \cdot k_{\text{cs}}}{2\pi}
= \frac{74}{2\pi} \approx 11.78 \text{ Planck units}$$

And the braid locking condition — the algebraic identity that closes the resonance — is:

$$n_w^2 + (n_w + 2)^2 = 5^2 + 7^2 = 25 + 49 = 74 = k_{\text{cs}} \checkmark$$

The epistemics here must be stated plainly. The pre-Big Bang geometry is an
**exploratory derivation** — it follows consistently from the mathematics of the
framework, but it is not observationally testable by any instrument in the current
or near-future experimental roadmap. It is what the framework predicts *if* its
assumptions hold; it is not an independent observational argument for those
assumptions.

---

## Pillar 112 — Why Five Dimensions, and Not Six, or Seven? *[P]*

This is the question that every Kaluza-Klein framework eventually has to face.
*Why this many extra dimensions?* Most KK theories push the question aside by
treating the number of extra dimensions as a free parameter. The Unitary Manifold
does not.

Pillar 112 (`src/core/uniqueness.py`) proves computationally that the S¹/Z₂
compactification — exactly one extra compact dimension with a Z₂ orbifold — is the
**unique** topology satisfying all structural constraints of the framework. Eight
candidate topologies are systematically tested against six constraint codes:

| Topology | Result | Failure |
|----------|--------|---------|
| S¹ | **FAIL** | No Z₂ — no chirality (C4) |
| **S¹/Z₂** | ✅ **PASS** | All constraints satisfied |
| S¹/Z₄ | **FAIL** | Z₄ anomaly not cancelled (C5) |
| T² | **FAIL** | Two extra dimensions violates minimality (C8) |
| T²/Z₂ | **FAIL** | Two extra dimensions (C8) |
| S² | **FAIL** | No round-trip KK closure; no quantised winding (C1, C4) |
| CP¹ ≅ S² | **FAIL** | Same as S² |
| S³ | **FAIL** | Three extra dimensions (C8) |

The six constraints are not arbitrary. They are the requirements that the compact
topology must satisfy to reproduce, after dimensional reduction, the correct
4D physics:

- **C1**: A single compact dimension for KK round-trip closure
- **C4**: Z₂ boundary conditions for chiral zero modes (required for the
  observed left-right asymmetry of the Standard Model)
- **C5**: Anomaly cancellation — only Z₂ (not Z₄ or higher) cancels the
  Z₂-odd gauge anomaly exactly
- **C8**: Minimality — S¹/Z₂ is the minimal topology satisfying C1–C6

The result is a **no-go theorem** for all alternatives: not just impractical, but
structurally excluded. The five-dimensional framework is not a choice made for
elegance. It is the unique minimum-dimensional extension of 4D GR + electromagnetism
+ the irreversibility field.

This is one of the cleanest results in the framework. The claim is not "five
dimensions fit the data." The claim is "nothing other than five dimensions passes
the structural constraints." The distinction matters enormously for how seriously
to take the predictive chain that follows.

---

## Pillar 113 — Where This Lives Inside M-Theory *[P]*

String theory and M-theory live in ten and eleven spacetime dimensions, respectively.
The Unitary Manifold lives in five. Where do they meet?

Pillar 113 addresses the embedding. The short answer: the UM's five-dimensional
geometry is a consistent truncation of the M-theory compactification, arising
when six of M-theory's extra dimensions are compactified on a G₂ manifold or
similar internal space, leaving a single accessible extra dimension at Planck
energies — precisely the S¹/Z₂ orbifold of the UM.

The Chern-Simons level k_cs = 74 appears in M-theory as a quantised flux
parameter associated with the G₄-flux on the four-cycle of the internal geometry.
The algebraic identity k_cs = 5² + 7² = 74 has a natural home in the Chern-Weil
theory of characteristic classes for the gauge bundle over the compact space.

The **honest accounting** from `FALLIBILITY.md` is important here: the specific
G₄-flux construction — the detailed step showing how k_cs = 74 emerges from the
internal M-theory geometry — is Step 4 of the embedding proof and remains **open**.
The SU(5) ⊂ E₈ gauge structure is closed, and the identification of k_cs = 74 as
a CS level is algebraically proved (Pillar 58). What is not yet closed is the
explicit G₄-flux integral that would derive k_cs = 74 from first principles in
the M-theory geometry rather than simply verifying its consistency.

This is documented in `FALLIBILITY.md` as open gap number 4. It is not hidden.

---

## What to Check, What to Break

1. **The locking temperature** (Pillar 111): T_lock ≈ 0.236 Planck units is derived
   from k_cs and n_w. If an independent calculation of the CS phase transition
   temperature gives a different result, the pre-BB geometry derivation fails.

2. **The uniqueness theorem** (Pillar 112): The constraint table at
   `src/core/uniqueness.py` can be audited directly. Any topology that was missed
   from the catalog, or any constraint code that can be argued to admit a different
   candidate, would challenge the uniqueness claim. The code is public; the
   catalog is auditable.

3. **The Lyapunov exponent sign** (Pillar 110): The FTUM fixed point is marginal
   at φ₀ = 1. A perturbative analysis of whether φ₀ = 1 is a genuine attractor
   or a saddle in the full non-linear system is an open technical question.
   The Lyapunov analysis here is computed at the linearised level.

4. **The G₄-flux gap** (Pillar 113): The M-theory embedding is the most openly
   incomplete part of this block. A string theorist with facility in G₄-flux
   quantisation who can close Step 4 — or show that it cannot be closed — would
   produce a decisive result. The GitHub issue tracker is open.

---

*Full source code and tests:*  
*https://github.com/wuzbak/Unitary-Manifold-*  
*Pillar 110: `src/core/nonequilibrium_attractors.py`*  
*Pillar 111: `src/core/prebigbang.py`*  
*Pillar 112: `src/core/uniqueness.py`*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
