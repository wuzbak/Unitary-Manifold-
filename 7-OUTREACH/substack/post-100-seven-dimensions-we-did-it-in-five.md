# Seven Dimensions? We Did It in Five.

*Post 100 of the Unitary Manifold series.*  
*A response to the 2025 G₂-manifold paper proposing that seven dimensions resolve
Stephen Hawking's black hole information paradox — and a precise account of where
the Unitary Manifold already stands on the same question, with fewer dimensions
and an acknowledged honest gap in the remnant-mass scale.*

---

A news cycle broke recently about a 2025 theoretical result claiming that the black
hole information paradox — one of the most famous unsolved problems in physics —
could be solved if the universe has seven dimensions. The paper proposes that three
extra hidden dimensions, arranged in a shape called G₂ geometry, generate a repulsive
force at Planck densities. Black holes do not fully evaporate. A stable remnant survives.
The information is stored in that remnant. Paradox resolved.

This is a legitimate proposal. The authors are serious physicists. The mechanism is
mathematically developed. If you haven't been following this work, the result is
striking: the same family of ideas that string theorists have developed for decades
turns out to have a specific, checkable consequence for black hole evaporation.

Here is the position of the Unitary Manifold on the same question: we reached the
same qualitative conclusion — black holes do not fully evaporate; a geometric remnant
stores the information — in five dimensions, not seven, through a different mechanism,
and with an honest 30-order-of-magnitude disagreement in the remnant mass scale that
has been documented since the comparison was first made.

This post explains precisely what the framework says, where it agrees with the 7D
proposal, where it differs, and what the disagreement actually means.

---

## The 7D Proposal in Brief

The paper (Pinčák et al., published in *General Relativity and Gravitation*, 2026)
works in a seven-dimensional spacetime: our four familiar dimensions plus three
compact hidden dimensions arranged as a G₂-holonomy manifold. In this geometry,
the spin-torsion contact interaction — a coupling between matter's intrinsic angular
momentum and the curvature of spacetime — generates a repulsive pressure at extreme
densities. Near the Planck scale, this repulsion overpowers gravity. Hawking evaporation
cannot push the black hole below a minimum size.

The predicted remnant mass is:

    M_rem (G₂) ≈ 4.14 × 10⁻³³ M_Planck  ≈  9 × 10⁻⁴¹ kg

The remnant encodes all swallowed information in quasi-normal mode oscillations of the
residual geometry. The G₂ dimensional structure also connects, via torsion, to the
Higgs mechanism at the electroweak scale — a separate prediction that links the
extra-dimensional geometry to particle physics.

---

## What the Unitary Manifold Already Has

The Unitary Manifold is a five-dimensional Kaluza-Klein framework: our four familiar
dimensions plus one compact spatial dimension (a circle) of radius R. The fifth
dimension carries the radion field φ — a scalar that measures the local size of the
compact direction.

Three separate modules address the black hole information paradox. They predate the
Pinčák et al. paper.

### Pillar 28 — The Kaluza-Klein Remnant (bh_remnant.py)

The radion field φ evolves in a Goldberger-Wise stabilisation potential:

    V(φ) = ½ m²_φ (φ − φ₀)²

This potential provides a hard lower bound:

    φ ≥ φ_min > 0

The Hawking temperature in the framework (Theorem XIV of `QUANTUM_THEOREMS.md`) is:

    T_H = |∂_r φ / φ| / (2π)

The maximum achievable gradient is bounded by the GW potential:

    |∂_r φ|_max = m_φ · (φ₀ − φ_min)

So the Hawking temperature cannot exceed:

    T_H_max = m_φ (φ₀ − φ_min) / (2π φ_min)

A black hole cannot evaporate below the mass at which T_H = T_H_max. The remnant
mass is:

    M_rem (5D UM) = φ_min / (8π m_φ (φ₀ − φ_min))

This is implemented in `src/core/bh_remnant.py` (Theorem XVII). The stopping
mechanism is the Goldberger-Wise restoring force — a spring-like potential on
the compact dimension — rather than torsion.

### Pillar 36 — Information Preservation (information_paradox.py)

The information current:

    J^μ_inf = φ² u^μ

has divergence exactly zero:

    ∇_μ J^μ_inf = 0

This is a geometric identity — it follows from the non-degeneracy of the 5D metric
and Noether's theorem applied to the 5D action. It does not require any additional
assumptions. Because φ ≥ φ_min > 0, the information density J^0_inf > 0 everywhere
in spacetime, including at and inside the event horizon, including in the remnant.

### Pillar 48 — The 5D vs. 7D Comparison (torsion_remnant.py)

When the Pinčák et al. result appeared, a dedicated comparison module was built.
It implements both frameworks — the GW mechanism (5D UM) and the torsion-repulsion
mechanism (7D G₂) — and documents their agreement and disagreement precisely.

The module lives in `src/core/torsion_remnant.py` and is covered by 
`tests/test_torsion_remnant.py`.

---

## Where the Two Frameworks Agree

Both frameworks reach the same *qualitative* conclusion:

1. **Black holes do not fully evaporate.** There is a minimum mass below which
   evaporation halts.
2. **Information is preserved.** The remnant stores the information content of
   everything the black hole ever swallowed.
3. **The stopping mechanism is geometric.** In both cases, the halt is not a new
   particle or new force, but a structural feature of the extra dimensions.
4. **The remnant is a topological object**, not a conventional particle.

This agreement across two independent theoretical approaches — one in five dimensions
via stabilisation potential, one in seven dimensions via torsion — provides some
confidence that the qualitative picture is correct. When different geometries reach
the same conclusion by different routes, that conclusion is worth taking seriously.

---

## Where the Two Frameworks Disagree

| Feature | 7D G₂ (Pinčák et al.) | Unitary Manifold (5D) |
|---|---|---|
| Total dimensions | 7 (4D + 3 hidden) | **5 (4D + 1 compact)** |
| Hidden-dimension geometry | G₂-holonomy manifold | Circle S¹ (Kaluza-Klein) |
| Stopping mechanism | Spin-torsion repulsion | **Goldberger-Wise potential** |
| Remnant mass | ~4.1 × 10⁻³³ M_Pl | ~4.4 × 10⁻³ M_Pl |
| Remnant mass ratio | — | **~10³⁰ heavier** (UM) |
| Information encoding | Quasi-normal modes | **5D topological winding** |
| EW scale connection | Via G₂ torsion | Not reproduced (admitted gap) |
| Torsion required? | Yes | **No** |

The most significant disagreement is the remnant mass: the UM predicts a remnant
approximately 10³⁰ times more massive in Planck units than the G₂ result. This is
not a rounding error. It reflects a genuine structural difference between the
Goldberger-Wise stopping mechanism (which depends on the radion mass and vacuum
expectation value in the UM parameter space) and the torsion-density threshold
(which depends on the Planck-scale torsion coupling).

This discrepancy is documented honestly in `FALLIBILITY.md §4.5` and
`src/core/torsion_remnant.py`. The UM does not claim to match the 7D remnant scale.

---

## The Honest Accounting

**What the UM has that the 7D paper also has:**
the qualitative resolution — a geometric stopping mechanism, a stable remnant,
information preservation. The UM had this before the Pinčák et al. paper appeared,
derived from independent assumptions, and with a separate numerical test suite.

**What the UM does not have that the 7D paper claims:**
the correct remnant mass scale, the G₂-torsion mechanism, and the connection to the
electroweak Higgs mechanism via torsion. On those points, the UM either disagrees
by many orders of magnitude or stays silent.

**What neither framework has yet:**
a testable astrophysical prediction. Black hole remnants at either Planck-scale
or GW-scale masses are far beyond current or near-future observational reach.
Both proposals are mathematically coherent but observationally unconstrained.
Neither can currently be falsified by direct observation.

The UM's primary falsifier remains the CMB birefringence prediction
(β ∈ {≈0.273°, ≈0.331°}), which LiteBIRD will test around 2032. That test has
nothing to do with black hole remnants — but if it fails, it falsifies the geometry
that underpins the GW stopping mechanism, and the remnant prediction falls with it.

---

## Why Fewer Dimensions Matter

The 7D proposal requires three hidden dimensions with a specific and intricate
geometry (G₂ holonomy). G₂ manifolds are known objects in differential geometry
and appear naturally in M-theory compactifications, but requiring a specific
seven-dimensional geometry is a strong additional assumption.

The UM resolves the same paradox with one hidden dimension and a stabilisation
potential that is already required by other parts of the framework (specifically,
by the radion stabilisation that generates the winding spectrum, the birefringence
prediction, and the information conservation theorem). The compact fifth dimension
is not added *for* the remnant — the remnant follows automatically from geometry
that was already there.

Occam's razor is not a proof. A five-dimensional solution is not necessarily correct
because it uses fewer dimensions. But if both frameworks make the same qualitative
prediction, the simpler one has a higher prior probability of being right — which
is a statement about theoretical parsimony, not about which framework will survive
experimental test.

---

## The Three-Sentence Summary

The 7D paper proposes that extra dimensions halt black hole evaporation via torsion.
The Unitary Manifold reaches the same qualitative conclusion in 5D via the
Goldberger-Wise potential, with a remnant mass that differs from the 7D prediction
by 30 orders of magnitude — a gap that is documented honestly and not papered over.
Both frameworks agree that information is not lost; they disagree on the scale of
the remnant that stores it.

---

*Full source code, derivations, and 17,438 automated tests:*  
*https://github.com/wuzbak/Unitary-Manifold-*  
*Pillar 28: `src/core/bh_remnant.py` — KK remnant and GW stopping mechanism*  
*Pillar 36: `src/core/information_paradox.py` — information current conservation*  
*Pillar 48: `src/core/torsion_remnant.py` — 5D vs. 7D framework comparison*  
*Quantum Theorems XII, XIV, XVII: `1-THEORY/QUANTUM_THEOREMS.md`*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
