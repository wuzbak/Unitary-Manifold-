# The One Thing That Still Needs to Be Proved

*Post 23 of the Unitary Manifold series.*
*Claim: the final open mathematical problem in the Unitary Manifold framework is the
Atiyah-Patodi-Singer η-invariant conjecture — the formal proof that n_w = 5 is
uniquely selected by the 5D geometry, not just observationally preferred. The framework
is honest about this gap: it documents it as Pillar 70, a conjecture, not a theorem.
This post explains what the problem is, why it is hard, and what solving it would mean.*

---

This is a post about an unsolved mathematical problem. Not a physics problem — a pure
mathematics problem. The framework has a gap, it knows it has a gap, and this post
explains the gap without hiding it or minimising it.

Post 0 of this series promised that every genuine open problem would be stated plainly.
This is the most important one.

---

## The question

The Unitary Manifold framework depends on a single integer: n_w = 5, the winding number
of the scalar field around the compact fifth dimension. Every quantitative prediction —
the spectral index nₛ, the tensor-to-scalar ratio r, the birefringence angle β, the
dark energy equation of state w — flows downstream from this integer.

The framework has two good arguments that n_w = 5 is the right value:

**Argument 1 (observational):** Among all odd winding numbers, n_w = 5 is the only one
consistent with the Planck spectral index nₛ = 0.9649 ± 0.0042. The table from the
winding number derivation:

| n_w | nₛ | Deviation from Planck |
|-----|-----|----------------------|
| 1 | 0.088 | ~208σ — eliminated |
| 3 | 0.899 | ~15.8σ — eliminated |
| **5** | **0.964** | **0.33σ — consistent** |
| 7 | 0.981 | 3.9σ — eliminated |
| 9 | 0.989 | 7.1σ — eliminated |

Only n_w = 5 survives the Planck constraint. This is a strong observational selection.

**Argument 2 (anomaly cancellation):** The orbifold Z₂ symmetry restricts n_w to
odd values. The three-generation constraint (the Standard Model has exactly three
generations of matter) restricts the allowed set further to {5, 7}. The action dominance
calculation (`src/core/nw_anomaly_selection.py`) shows that the effective Chern-Simons
action at n_w = 5 (k_eff = 74) is lower than at n_w = 7 (k_eff = 130), making n_w = 5
the dominant saddle point of the path integral.

Both arguments are strong. Neither is a proof.

---

## What is missing: the APS η-invariant

The mathematical gap is in the η-invariant of the Dirac operator on the orbifold
S¹/Z₂.

The Atiyah-Patodi-Singer (APS) η-invariant is a spectral invariant of the Dirac operator
on a manifold with boundary. For the orbifold S¹/Z₂, the APS index theorem relates
the η-invariant to the Chern-Simons level through:

    η(0, D) = T(n_w) / 2 mod 1

where D is the Dirac operator and T(n_w) is the topological charge of the winding
configuration.

The conjecture (Pillar 70, `src/core/aps_spin_structure.py`) is:

> *The zero-mode Z₂ parity condition — the condition that the standard model chirality
> (matter-antimatter asymmetry) is accommodated — requires η̄ = 1/2, and this condition
> is satisfied only by n_w = 5 in the allowed set {5, 7}.*

For n_w = 5: η̄(5) = 0.5 (the conjecture says this is the chirality-compatible value).
For n_w = 7: η̄(7) = 0 (the conjecture says this is chirality-incompatible).

If the conjecture is correct, n_w = 5 is not merely observationally preferred — it is
mathematically required by the condition that the standard model's matter-antimatter
asymmetry is compatible with the orbifold structure.

---

## Why the conjecture is hard

The APS η-invariant is a non-local spectral quantity. Computing it requires knowledge
of the full spectrum of the Dirac operator, not just its zero modes. For compact
manifolds without boundary, the index theorem gives a topological formula. For
manifolds with boundary (and orbifolds can be treated as manifolds with conical boundary
conditions), the η-invariant appears as a correction term that depends on the detailed
spectral flow of the Dirac operator across the boundary.

The computational difficulty: the orbifold S¹/Z₂ has two fixed points (y = 0 and
y = πR), and the spectral flow of the Dirac operator at each fixed point depends on
the local orbifold action. Computing η̄(n_w) analytically requires:

1. The full eigenspectrum of the Dirac operator on the orbifold
2. The boundary condition at each fixed point (which depends on the Z₂ action on spinors)
3. The modular properties of the spectral zeta function

This is a genuine hard analysis problem. The framework's implementation in
`src/core/aps_spin_structure.py` implements the Hurwitz ζ-function representation of
the η-invariant and derives η̄ from the CS inflow relation — but the derivation of
η̄(5) = 0.5 uses the physical argument (SM chirality requires it) rather than a direct
analytical computation. That is what makes it a conjecture rather than a proof.

---

## What the 256 tests cover

`tests/test_aps_spin_structure.py` (256 tests) confirms:

- The Hurwitz ζ function η(0, α) = 1 − 2α (proved analytically from the ζ-function definition)
- The CS inflow relation η̄ = T(n_w)/2 mod 1 (derived from the CS inflow formula)
- The numerical value η̄(5) = 0.5 when the chirality boundary condition is applied
- The numerical value η̄(7) = 0 under the same conditions
- The zero-mode Z₂ parity eigenvalue for each winding number

What the tests do not confirm:

- That the chirality boundary condition (η̄ = 1/2 required by SM matter-antimatter asymmetry)
  is the mathematically unique choice. The physical argument says it must be; the
  mathematical proof of uniqueness has not been completed.
- That the orbifold fixed-point contributions are correctly summed. The implementation
  uses a model that is consistent with known results for S¹/Z₂, but a full computation
  from the APS boundary data would require additional mathematical work.
- That the result generalises correctly to the full 5D geometry (the implementation
  works in the compact dimension alone; the full 5D APS theorem is more complex).

---

## Why this matters

The distinction between "observationally preferred" and "mathematically required"
is the difference between a fit and a derivation.

If n_w = 5 is merely observationally preferred, the framework has:
- A parameter (n_w) fixed by external data
- Predictions that follow from that parameter
- A theory that works because it was calibrated to work

If n_w = 5 is mathematically required, the framework has:
- A parameter that cannot be different without violating internal consistency
- Predictions that follow from first principles
- A theory that works because the geometry forces it

These are very different epistemic situations. The first is a model. The second is a
derivation. The framework claims to be the second; Pillar 70 is honest that the claim
is not yet fully proved.

---

## The state of the art on APS

The Atiyah-Patodi-Singer index theorem was proved in 1975 for compact manifolds with
boundary. Its generalisation to orbifolds — spaces with conical singularities at fixed
points — is an active area of mathematics. Several partial results are available:

- The APS theorem for orbifold S¹/Z₂ with simple discrete group actions has been
  computed in specific cases (Donnelly, 1976; Gilkey, 1984).
- The η-invariant for circle bundles with Z₂ action has been partially computed
  (Cheeger, 1987; Kirk & Leichtnam, 2000).
- The case relevant to the Unitary Manifold — the Dirac operator on S¹/Z₂ with
  Chern-Simons inflow at the fixed points — has not been computed in the specific
  form required.

The framework's conjecture is not in conflict with any known result. It is simply
unproved. The calculation is well-posed and could, in principle, be completed by
a mathematician with the right background in spectral geometry. The repository's
open invitation for mathematical collaboration (in `discussions/AI-Automated-Review-Invitation.md`)
is particularly relevant here.

---

## The two paths forward

**Path 1: Direct APS computation.** A mathematician computes η̄(n_w) directly from
the APS boundary data for the Dirac operator on S¹/Z₂ with Chern-Simons inflow.
If the result is η̄(5) = 1/2 and η̄(7) = 0, the conjecture is proved. If the result
is different, the conjecture fails and the physical argument for n_w = 5 must be
rebuilt on different foundations.

**Path 2: LiteBIRD bypasses the need.** If LiteBIRD measures β ≈ 0.331° or β ≈ 0.273°
(the predicted values for n_w = 5), and simultaneously rules out n_w = 7 via the
different birefringence prediction for that winding number, the observational case for
n_w = 5 becomes so strong that the mathematical uniqueness proof matters less. The
theory would be observationally confirmed even if the last mathematical gap remained
a conjecture.

The framework prefers Path 1. Physics without mathematical rigour is philosophy. But
if LiteBIRD arrives first, Path 2 is a meaningful result.

---

## What this series has been about

Twenty-three posts. One claim: the arrow of time is a geometric fact, not a statistical
accident. The claim rests on a single integer (k_CS = 74) derived from a single
braid vector ((5, 7)) derived from a single winding number (n_w = 5) whose uniqueness
is observationally established and mathematically conjectured but not yet fully proved.

The most important honest acknowledgment of this series is not in any one post —
it is in the structure of the series. Physics advances by stating claims, deriving
predictions, submitting to experimental test, and being honest when gaps remain.
The gap here is Pillar 70. It is documented. It is open. It is the right kind of
open problem: precisely stated, bounded, and accessible to mathematical attack.

LiteBIRD will provide the observational answer. The APS computation will provide
the mathematical one. The series continues until one or both arrives.

---

*Full source code, derivations, and 14,183 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*APS spin structure: `src/core/aps_spin_structure.py` — 256 tests in `tests/test_aps_spin_structure.py`*
*Anomaly selection: `src/core/nw_anomaly_selection.py` — 156 tests*
*Winding number derivation: `WINDING_NUMBER_DERIVATION.md`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
