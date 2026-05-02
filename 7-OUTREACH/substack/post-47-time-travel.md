# Time Travel: What the Framework Permits and What It Forbids

*Post 47 of the Unitary Manifold series.*
*Claim: the five-dimensional Walker-Pearson field equations permit closed timelike
curve (CTC) solutions mathematically — the geometry does not forbid them by fiat.
But the FTUM fixed-point theorem forbids the grandfather paradox: a CTC that
attempts to prevent its own creation would violate the uniqueness of the fixed point
Ψ*, producing a contradiction the geometry resolves by forbidding the paradoxical
trajectory. Time "travel" in the caricature sense is not possible; what is possible
is more subtle and more interesting.*

---

Time travel is the science fiction idea that physics has done the most damage to.
Not because the physics is wrong — but because the way it is usually described
strips out the parts that make it strange and keeps only the parts that make
for good dramatic tension.

The actual physics of time in the Unitary Manifold is not about grandfather paradoxes
or going back to fix your mistakes. It is about the structure of causality in a
five-dimensional geometry — and that structure is genuinely surprising.

---

## What general relativity already allows

General relativity permits closed timelike curves — paths through spacetime that
return to their own starting point in both space and time. The most famous example
is the Gödel metric (1949): a solution to Einstein's equations describing a rotating
universe in which any two events can be connected by a future-directed timelike curve.

This means that in principle, within GR, you can travel to your own past. The physics
allows the worldline.

GR's response to the grandfather paradox is: either such solutions don't correspond
to the actual universe, or the paradox is avoided by some consistency condition
(the Novikov self-consistency principle: only self-consistent histories can occur).

The Unitary Manifold inherits GR in the limit λ → 0, φ → const. But it adds structure
that changes the CTC situation.

---

## What the fixed-point theorem adds

The FTUM fixed-point theorem guarantees that Ψ* is unique. This is the critical
addition.

If you could travel to the past and change something, you would produce a different
trajectory — a trajectory that does not converge to the same Ψ* as the original.
But Ψ* is unique. There is exactly one fixed point of U. A history that produces
a different Ψ* is not a history of the same universe — it is a different winding-state
configuration, a different branch in the multiverse catalog.

The grandfather paradox — going back and killing your grandfather before your parent
is born, thus ensuring you are never born, thus ensuring you never go back — requires
that the *same* fixed point Ψ* be the attractor of two different trajectories.
The uniqueness theorem forbids this: two different histories cannot converge to the
same Ψ* if they are topologically inequivalent.

**The framework's version of Novikov's consistency condition:** any trajectory that
forms a closed timelike curve must be consistent with the same Ψ*. Self-consistent
CTCs are permitted. Paradoxical CTCs violate fixed-point uniqueness and are forbidden.

---

## What is actually possible

What the framework permits, under this constraint:

**Retrocausality in the information current.** The conserved information current
J^μ_inf = φ² u^μ carries information along timelike worldlines — forward and, in
principle, backward along a CTC. A self-consistent CTC would carry information to
the past without contradicting Ψ*. Whether such configurations occur in our universe
is not determined; the framework says they are not geometrically forbidden.

**The compact fifth dimension as a shortcut.** The fifth dimension is compact —
it is a circle. At energies near the compactification scale (far above anything
accessible experimentally), paths through the fifth dimension could in principle
connect spacetime points that appear causally separated in 4D. This is not time travel
in the narrative sense; it is a change in causal order relative to 4D distance.

**Multiverse branches, not timeline branches.** What science fiction calls "alternate
timelines" are, in this framework, different (n₁, n₂) winding configurations —
different fixed points in the multiverse catalog, not branches off the same fixed point.
You cannot "travel" between them, because they are not connected by continuous
deformation — the topological barriers between winding states are real. They are
adjacent in information space, not adjacent in physical space.

---

## What is definitely not possible

- **The grandfather paradox** — violates fixed-point uniqueness.
- **Going back to fix your mistakes** — your past is encoded in the geometry via
  the information conservation law. It cannot be unwritten.
- **Arriving at the same timeline as a duplicate of yourself** — the FTUM fixed point
  determines the dynamics of the manifold; two versions of you at the same spacetime
  event produce a state with doubled information content, which would need to converge
  to the same Ψ* — a constraint that is not generically satisfied.

---

## The honest answer

Can you travel in time? In the dramatic sense — visit the past, change events, return
to find a different present? No. The information conservation law forbids erasing
the past, and the fixed-point uniqueness forbids paradoxical loops.

Are there genuine time-ordering effects beyond ordinary causality in this framework?
Yes: retrocausal correlations through the information current, shortcuts via the
fifth dimension near the compactification scale, and the causal structure of
self-consistent CTCs. None of these produce the science fiction narrative.

The actual physics of time is more interesting than the stories, and less dramatic.

---

*Full source code, derivations, and 15,615 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Fixed-point uniqueness: `src/multiverse/fixed_point.py`*
*Information current: `QUANTUM_THEOREMS.md` (Theorem XII)*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
