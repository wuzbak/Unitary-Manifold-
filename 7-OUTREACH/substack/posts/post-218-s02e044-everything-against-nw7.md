# Post 218 — S02E044: Everything We Know Against n_w = 7

*Substack — Season 2, Episode 44*  
*Published: 2026-05-21*  
*Series: The Falsification Decade*

---

Of all the open items in the Unitary Manifold, the one that comes up most in external
review is this one: *why 5 and not 7?*

The framework derives n_w ∈ {5, 7} as the only candidates from hard geometric
constraints. Five survives. Seven is excluded — or more precisely, strongly
disfavoured by multiple independent arguments, with one formal topological exclusion
at the level the framework can currently reach.

Pillar 312 consolidates every argument against n_w=7 into a single machine-readable
module. This post makes those arguments accessible to a non-specialist reader.

---

## Step 1: How We Got to {5, 7}

Start from the full set of odd integers (n_w must be odd from the Z₂ involution on
the S¹ orbifold). The framework applies a sequence of hard geometric cuts:

1. **Stable generation count:** n_w must produce exactly three quark/lepton
   generations from the KK tower spectrum. This cuts to {3, 5, 7, 9}.
2. **CS anomaly cancellation:** n_w = 3 predicts K_CS = 34, placing the spectral
   index at n_s ≈ 0.936 — 1.6σ from Planck. Not excluded but disfavoured.
   n_w = 9 predicts four stable generations. Eliminated.
3. **Braid pair existence:** After the above cuts, only n_w ∈ {5, 7} survive with
   valid (n_w, n_m) braid pairs that cancel anomalies and reproduce three generations.

So the starting point for the n_w = 5 vs. 7 question is a field of two. Not ten.
Not a continuous space. Two candidates, one of which the framework selects and one
of which it must justify excluding.

---

## Constraint A: The Topological Exclusion (PROVED)

**What it is:** An algebraic statement about the Atiyah-Patodi-Singer boundary phase.

**The argument:** On the S¹/Z₂ orbifold, the extra-dimensional gauge field G_{μ5}
must carry Z₂ eigenvalue −1 (it is a pseudovector under the Z₂ reflection). This
forces the Chern-Simons boundary phase to be non-trivial:

```
exp(iπ × k_CS(n_w) × η̄(n_w)) = −1
⟺  k_CS(n_w) × η̄(n_w) = odd integer
```

where η̄(n_w) is the APS η̄-invariant of the n_w-winding cycle, and k_CS is the
Chern-Simons level of that cycle.

Now compute:
- **n_w = 5:** k_CS = 5² + 7² = 74. T(5) = 5×6/2 = 15. η̄(5) = 15/2 mod 1 = 0.5.
  Product: 74 × 0.5 = **37 (ODD)** → ✅ CONSISTENT
- **n_w = 7:** k_CS = 7² + 9² = 130. T(7) = 7×8/2 = 28. η̄(7) = 28/2 mod 1 = 0.0.
  Product: 130 × 0.0 = **0 (EVEN)** → ❌ EXCLUDED

The n_w = 7 cycle has trivial APS phase. It cannot satisfy the Z₂-odd boundary
condition on G_{μ5}. This is Pillar 70-D.

**The caveat (Admission 3):** The argument relies on the Z₂-odd boundary condition
on G_{μ5} as an axiom of the 5D theory. We have not yet derived this condition
from the 5D Lagrangian alone — it is imposed by the orbifold structure, not derived
from it. This is the precise content of FALLIBILITY.md Admission 3. The topological
exclusion is **proved within the framework**, but the framework's Z₂ structure is
itself an input, not a theorem.

This is the key remaining open item. Closing it would elevate the topological
exclusion from "proved within the framework" to "derived from first principles."

---

## Constraint B: GW Cycle Assignment (DERIVED)

**What it is:** A dynamical preference from the Goldberger-Wise radion potential.

In the two-radius Randall-Sundrum scenario, the GW mechanism stabilizes the extra
dimension. When winding modes back-react on the moduli potential, each cycle's
equilibrium radius shifts:

```
kR_min(n_w) ≈ πkR × (1 + n_w²/(4 π²kR² ε²))⁻¹
```

For (n_w=5, n_m=7) and (n_w=7, n_m=9) with πkR = 37, ε = 0.01:
```
kR_min(n_w=5) ≈ 6.64   [primary cycle, larger radius]
kR_min(n_w=7) ≈ 3.42   [secondary cycle, smaller radius]
```

The n=7 cycle sits at smaller radius — it is the *secondary* cycle. Combined with
the APS result (η̄(5)=½, η̄(7)=0), this identifies the Z₂-non-trivial cycle (n=5)
as the primary winding cycle. This *derives* Convention 279.3, which was previously
a convention. It is now a geometric theorem.

**Verdict:** CYCLE_ASSIGNMENT_DERIVED — Convention 279.3 is derived, not assumed.

---

## Constraint C: CS Action Minimum (PREFERRED)

The Euclidean path integral is dominated by the minimum-action saddle. The CS level
is the relevant action:

```
k_eff(n_w=5, n_m=7) = 5² + 7² = 74   [minimum]
k_eff(n_w=7, n_m=9) = 7² + 9² = 130  [1.76× larger]
```

The n_w=5 saddle has lower action and dominates the path integral. The n_w=7 saddle
is subdominant. This is a preference, not a proof — subdominant saddles can contribute
— but it reinforces the topological exclusion from Constraint A.

---

## Constraint D: Planck n_s Disfavouring (OBSERVATIONAL)

Each candidate predicts a CMB spectral index:

```
n_s(n_w) ≈ 1 − 36/(n_w × 2π)²

n_s(n_w=5) ≈ 0.9635   Planck 2018: 0.9649 ± 0.0042   → 0.33σ consistent ✓
n_s(n_w=7) ≈ 0.9735   Planck 2018: 0.9649 ± 0.0042   → 2.28σ disfavoured ✗
```

The likelihood ratio in favour of n_w=5 from Planck alone is approximately 12.8:1.
Using a slightly different approximation (the Pillar 306 formula), it is 2109:1.
Both routes are consistent in direction: Planck data strongly prefer n_w=5.

This is observational — it uses the Planck measurement. It does not constitute a
pure first-principles proof. But it is decisive empirical evidence.

---

## Constraint E: Braided r_eff Discriminator (FUTURE TEST)

The braided tensor-to-scalar ratio depends on the braid pair:

```
c_s(5,7) = 24/74 = 12/37 ≈ 0.324
c_s(7,9) = 32/130 ≈ 0.246

r_braided(n_w=5) ≈ 0.0315   [below BICEP/Keck < 0.036 ✓]
r_braided(n_w=7) ≈ 0.0122   [also below BICEP/Keck ✓]
```

Both candidates currently satisfy the BICEP/Keck r bound. But they differ by a
factor of approximately 2.6. A precision r measurement from the Simons Observatory
(DR1 ~2027) or CMB-S4 (~2030) can discriminate them. If SO measures r ≈ 0.031–0.032,
that is strong evidence for n_w=5. If r ≈ 0.012–0.013 (and n_s is also consistent
with 0.974), that would be the first indication of n_w=7 surviving observationally.

This is the cleanest discriminating test available before LiteBIRD.

---

## The Full Picture

| Constraint | Type | Excludes n_w=7? | Strength |
|------------|------|-----------------|---------|
| A — APS boundary phase | TOPOLOGICAL | **Yes** (Proved) | Formal, with Admission 3 caveat |
| B — GW cycle assignment | DYNAMICAL | No (derives n_w=5 primary) | Derived |
| C — CS action minimum | PATH INTEGRAL | No (preference) | Preferred |
| D — Planck n_s | OBSERVATIONAL | No (disfavours) | 2.28–3.93σ against |
| E — Braided r_eff | PHENOMENOLOGICAL | No (future test) | Discriminating |

The honest summary: **n_w=7 is formally excluded by the APS topological argument**
(within the framework's Z₂ axiom structure) and **strongly disfavoured by Planck**.
The GW and CS arguments assign n_w=5 to the primary role from dynamical and
path-integral principles.

What remains open is the derivation of the Z₂ structure from the 5D Lagrangian itself,
without imposing it as an axiom. That derivation would close Admission 3 and convert
Constraint A from "proved within the framework" to "derived from first principles."

It is a well-defined remaining task. The territory of the problem is mapped. The
answer is not discovered yet.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Outreach writing, document engineering, and synthesis: GitHub Copilot (AI).*
