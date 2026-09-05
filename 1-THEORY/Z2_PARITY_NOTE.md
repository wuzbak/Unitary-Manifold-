# Z₂ Parity and the Missing Photon Zero Mode

**Status: OPEN — the referee's photon objection is valid.**

For the canonical circle ansatz

    ds² = g_μν dx^μ dx^ν + φ²(dy + λB_μ dx^μ)²,

the mixed component is **G_{μ5} = λφ²B_μ** and the connection is
**A_μ = G_{μ5}/G_{55} = λB_μ**, not λφB_μ.

## Reflection and fixed planes

Under the orbifold reflection y → −y, an invariant tensor metric has:

| Field | Parity | Constant zero mode |
|-------|--------|--------------------|
| g_μν | even | allowed |
| G_{55} = φ² | even | allowed |
| positive radius φ | even | allowed; stabilisation may give it mass |
| G_{μ5} | odd | absent |
| B_μ and A_μ = λB_μ | odd | absent |

For a smooth periodic odd field, B_μ(0) = −B_μ(0) = 0 and likewise
B_μ(πR) = 0. Multiplication by any regular even radion factor preserves odd
parity. Its fixed-plane restriction is therefore zero, **not a boundary photon**.
The former argument that a boundary projection rescues the photon was incorrect.

On a circle, the connection produces a Lorentz-type geodesic force. That
conditional geometric result does not establish the observed electromagnetic
sector, and cannot restore the zero mode removed by the orbifold. In particular,
a y-independent odd metric vector must vanish.

## What would be needed

An independently specified even bulk gauge field or boundary gauge sector,
or a different compactification, could change the spectrum. Such an extension
requires an action, boundary conditions, and a demonstrated massless mode;
none is derived here. Likewise, a spacetime reflection does not select an
internal SU(5) gauge bundle or its reflection lift.

## Executable checks

- `src/core/metric.py`: canonical assembly and `z2_parity_clarification()`.
- `tests/test_kk_geometry_invariants.py`: line element, inverse, gauge pullback,
  analytic curvature and one-coordinate derivative convention.
- `tests/test_orbifold_nonuniqueness.py`: odd fixed-plane restrictions and
  inequivalent internal gauge lifts with the same metric reflection.
- `src/core/pillar677_fermion_cl_orbifold_closure.py`: regular finite-interval
  Dirac domain admits every real bulk mass; parity does not select flavor.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
