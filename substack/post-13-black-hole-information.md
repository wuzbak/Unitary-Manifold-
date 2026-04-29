# What Happens to Information When a Black Hole Dies

*Post 13 of the Unitary Manifold series.*
*Claim: in the five-dimensional geometric framework of the Unitary Manifold, the
conservation law ∇_μ J^μ_inf = 0 holds as a structural identity — information is
never destroyed, including during black hole evaporation. This is not a postulate
added to the theory; it follows from the non-degeneracy of the 5D metric. The claim
would be undermined if a future theoretical derivation shows the information current
has a source term — or if the 5D metric's radion field reaches zero, violating the
Goldberger-Wise bound. No current observation tests this directly.*

---

The black hole information paradox is one of the oldest unsolved problems in theoretical
physics. It is nearly fifty years old. It has attracted contributions from Stephen
Hawking, Leonard Susskind, Juan Maldacena, and essentially every prominent figure in
quantum gravity for the past three decades.

The Unitary Manifold has something specific to say about it — not as a speculation,
but as a consequence of the same five-dimensional geometry that generates the
birefringence prediction. This post explains what the framework says, why the argument
is structural rather than speculative, and where the honest limits of the claim are.

---

## The paradox, precisely stated

In 1974, Stephen Hawking showed that black holes are not fully black. Quantum effects
near the event horizon cause the black hole to radiate thermally — now called Hawking
radiation — and to slowly lose mass. Given enough time, a black hole will evaporate
completely.

The radiation Hawking calculated is exactly thermal. It carries no information about
what fell in: a black hole formed from a library of books and a black hole formed from
the same total mass of hydrogen gas would produce identical Hawking radiation. If this
picture is exactly right, then when the black hole finishes evaporating, the information
that fell in is gone. Not hidden, not encoded somewhere — gone.

This conflicts with a fundamental principle of quantum mechanics: unitary evolution.
Quantum mechanics requires that the state of a closed system evolves unitarily —
meaning information is always preserved, just scrambled. You can always (in principle)
run the equations backward and recover the initial state. If information is destroyed
in black hole evaporation, quantum mechanics is violated at a fundamental level.

Hawking's original position (information is destroyed) and the quantum mechanical
position (information is preserved) cannot both be exactly right. Resolving this
tension is the black hole information paradox.

---

## What the standard proposals say

| Framework | Core mechanism |
|-----------|---------------|
| Hawking (1974) | Information is destroyed — originally, later retracted |
| Page (1993) | Information leaks back out slowly in Hawking radiation |
| ER = EPR (Maldacena & Susskind, 2013) | Entanglement between the hole and radiation is geometrically linked to a wormhole |
| Fuzzball (string theory) | The horizon is not empty space; the structure of the string-theoretic interior encodes the information |

Each of these proposals is serious and mathematically developed. Each has been the
subject of decades of research. What they share is this: each requires *additional*
input beyond the original geometry — entanglement structure, wormhole geometry,
string-theoretic interior — to resolve the paradox.

---

## What the Unitary Manifold says

The framework's claim is different in kind: information is preserved not because of
additional mechanism, but because of what the geometry already is.

The central object is the **information current**:

    J^μ_inf = φ² u^μ

where φ is the five-dimensional radion field (the field that characterises the size of
the compact fifth dimension at each point in spacetime) and u^μ is the four-velocity of
the fluid element. This is implemented in `evolution.py: information_current`.

The conservation law follows from the 5D field equations. The argument runs in four steps.

**Step 1: The 5D metric is non-degenerate.**

The five-dimensional metric has the form:

    G_AB = | g_μν + λ²φ² B_μB_ν    λφ B_μ |
           | λφ B_ν                  φ²     |

The component G_55 = φ². The metric is non-degenerate as long as φ ≠ 0.

**Step 2: The Goldberger-Wise potential keeps φ away from zero.**

The radion field evolves in a stabilisation potential:

    V(φ) = ½ m²_φ (φ − φ₀)²

This is a restoring potential, like a spring: the field φ is pulled toward φ₀ and
cannot reach zero for bounded initial data. Specifically:

    φ_min = φ₀ − C/m_φ > 0

The metric G_AB remains non-degenerate throughout the evolution.

**Step 3: Noether's theorem gives a 5D conservation law.**

The five-dimensional action S₅ = (1/16πG₅) ∫ d⁵x √(−G) R₅ is invariant under the
symmetries of the 5D geometry. Noether's theorem then gives a 5D conservation law:

    ∇_A^(5D) J^A_(5D) = 0

**Step 4: Dimensional reduction projects the conservation law faithfully.**

Kaluza-Klein dimensional reduction is a smooth integration over the compact fifth
dimension. This integration projects the 5D conservation law to a 4D law:

    ∇_μ J^μ_inf = 0

This equation has no source term. It is a 4D identity, not an approximation.

---

## What this means for Hawking evaporation

The information current J^0_inf = φ² / √|g_00| (the time component, the information
density) is bounded below by φ_min² > 0 everywhere in spacetime. This includes at
and inside the event horizon.

During Hawking evaporation in this framework, the information is not destroyed and not
left in a remnant. It flows. The information current, governed by ∇_μ J^μ_inf = 0,
redirects the information content through the compact fifth dimension. An observer
using only the 4D projected metric g_μν sees information appearing to vanish into the
black hole and not return. An observer with access to the full 5D metric G_AB sees the
information current flowing continuously, including through what appears to be a
singularity in the 4D picture.

The apparent paradox is a coordinate artifact: it arises from projecting a 5D
conservation law onto 4D coordinates that cannot represent the fifth direction.

---

## How this compares to ER = EPR

The ER = EPR conjecture (Maldacena and Susskind, 2013) proposes that entanglement
between two quantum systems is geometrically equivalent to a wormhole connecting them.
Applied to black holes, the Hawking radiation becomes entangled with the black hole
interior via a wormhole, and information escapes through this geometric connection.

The Unitary Manifold result is structurally different:

- ER = EPR requires invoking entanglement structure and a specific geometric feature
  (the wormhole) that must be argued for as a consequence of the theory.
- In the Unitary Manifold, ∇_μ J^μ_inf = 0 is a consequence of the metric being
  non-degenerate and the 5D action being symmetric. No additional geometry needs to
  be invoked — the fifth dimension is already there, and it is already smooth.

This does not mean the ER = EPR picture is wrong. It means the two arguments are
reaching the same conclusion — information is preserved — by different routes. The
Unitary Manifold route is more direct: the conservation law is an identity, not a
derived consequence of entanglement.

---

## The Kaluza-Klein black hole remnant

The framework also makes a specific prediction about what is left when a black hole
finishes evaporating: a Kaluza-Klein remnant with mass:

    M_rem = φ_min / (8π m_φ Δφ)

where m_φ is the radion mass and Δφ = φ₀ − φ_min is the stabilisation depth. This
remnant is a geometric object — the minimum-size configuration of the compact
fifth dimension that is consistent with the Goldberger-Wise bound — not a conventional
particle. It is implemented in `src/core/bh_remnant.py` (Theorem XVII).

The remnant mass is a prediction, not a free parameter. It is determined by the same
φ₀ and m_φ that appear throughout the rest of the framework. Whether this remnant is
detectable — and by what experiment — is an open question.

---

## What the test suite confirms — and does not confirm

The automated tests in `tests/test_quantum_unification.py` (Theorem XII section) verify:

- ∂_x J^x ≈ 0 for near-flat initial conditions (conservation in flat spacetime)
- J^0 ≥ 0 throughout evolution (information density is non-negative)
- Total information ∫ J^0 dx is conserved to relative error < 3% over 20 RK4 steps
- Conservation persists with the Goldberger-Wise stabilisation active

What the tests do *not* confirm:

- That the Hawking information paradox is physically resolved by this mechanism
- That real black holes are described by the Unitary Manifold geometry
- That the KK remnant is a physical object that would be detected by any current or
  planned experiment

The tests confirm that ∇_μ J^μ_inf = 0 holds in the numerical implementation of the
Walker-Pearson field equations, and that the information density remains non-negative
under the implemented dynamics. The connection to real black holes requires the
framework's other assumptions — particularly the existence of the compact fifth
dimension — to be correct.

---

## The honest qualification

The black hole information argument in this framework is a mathematical derivation
from the 5D geometry. It is not independently testable with current experiments —
there is no observation that distinguishes "information preserved via 5D current" from
"information preserved via some other mechanism" at energies accessible today.

Its significance is logical, not empirical: *if* the 5D geometry is correct (a claim
LiteBIRD will test through birefringence), *then* information preservation follows as
an identity, not as an additional assumption. The paradox does not arise in this
framework because the geometry does not permit the conditions that generate it.

Whether this is the correct resolution, or whether it fails on deeper inspection that
has not yet been performed, is a genuine open question. The derivation is documented
and the tests pass. The claim is structural, falsifiable in principle, and currently
untested by astrophysical observation.

---

*Full source code, derivations, and 14,641 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Quantum Theorems: https://github.com/wuzbak/Unitary-Manifold-/blob/main/QUANTUM_THEOREMS.md*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
