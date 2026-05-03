# What We Cannot Claim — The Remaining Open Questions at Closure

*Post 89 of the Unitary Manifold series.*
*This post is a systematic accounting of what the Unitary Manifold does not
derive, cannot claim, and has not resolved. An honest framework lists its
failures at least as carefully as its successes.*

---

Every scientific framework has gaps. What distinguishes a trustworthy framework
from an untrustworthy one is not the absence of gaps, but the willingness to
document them precisely and publicly.

The Unitary Manifold has a file called `FALLIBILITY.md`. It documents every
known gap, inconsistency, and approximation in the framework. This post is the
Substack version of that document — the acknowledgment that the framework is
not complete, and the precise statement of where it falls short.

---

## Gap 1: The Absolute Fermion Mass Scale

The most consequential open problem.

The Yukawa geometric closure (Pillar 93) establishes that fermion *mass ratios*
emerge from the five-dimensional geometry. The ratio m_top/m_electron is large
because of the exponential difference in their wavefunction localizations.

But the *scale* — why m_electron = 0.511 MeV rather than 5.11 MeV or 0.0511 MeV —
is not derived. It requires one input: the overall Yukawa scale λ_Y, which sets
the relationship between the 5D coupling and the 4D Fermi scale.

λ_Y is not derived from the metric ansatz. It is not derived from the FTUM
fixed point. It is the one remaining free parameter in the fermion sector.

If λ_Y can be derived from the FTUM fixed point φ₀ via λ_Y = φ₀^{-2} × g_brane,
the scale problem closes. This is a conjecture, not a proof.

> **[Editor's Note — v9.27]** Pillars 97 and 98, added after this post was written,
> substantially close the absolute fermion mass scale problem. The FTUM-fixed-point
> derivation of λ_Y (the conjecture described above) is now implemented and tested.
> The fermion mass scale is no longer the open gap it was at the time of writing.
> See `FALLIBILITY.md` (current edition) for the updated accounting.

---

## Gap 2: The Solar Neutrino Mixing Angle

The PMNS matrix prediction for θ₁₂ (the solar angle):

**Geometric prediction:** sin²θ₁₂ = 4/15 = 0.267
**PDG measured:** sin²θ₁₂ = 0.307 ± 0.012

Discrepancy: **13%** — the largest discrepancy in the mixing sector.

The mechanism is the Tri-Bimaximal Mixing structure modified by Z_{n_w} corrections.
The corrections shift θ₂₃ and θ₁₃ in the right direction with good precision.
They do not shift θ₁₂ correctly.

The resolution may require computing next-order corrections to TBM from the RS
Yukawa potential, or it may require a different starting point for the neutrino
mixing matrix. This is documented as an open problem, not glossed over.

---

## Gap 3: The Strong Coupling Constant

sin²θ_W at the GUT scale is derived from SU(5) geometry: sin²θ_W(M_GUT) = 3/8.
This runs correctly to sin²θ_W(M_Z) ≈ 0.2313 with 0.05% agreement.

The strong coupling α_s has no analogous geometric derivation. It is measured
(α_s(M_Z) ≈ 0.118) and inserted. The framework conjectures that α_s arises from
the E₈ structure of the heterotic string embedding, but this is not derived.

The derivation of all three SM gauge couplings from first principles remains an
open problem.

---

## Gap 4: G₄-Flux Uniqueness in M-Theory

The UV embedding (Pillar 92) shows that the framework is consistent with M-theory
via the Horava-Witten mechanism. Three of four steps are analytically closed:

1. n_w = 5 → SU(5) ⊂ E₈ ✓
2. φ₀ = 1 ↔ M-theory R₁₁ = l_Pl ✓
3. k_CS = 74 consistent with GS-West anomaly cancellation ✓
4. G₄-flux quantization uniquely selecting n_w = 5 **OPEN**

The G₄-flux computation in M-theory requires a specific calculation that involves
the moduli stabilization of the 6 compact dimensions between M-theory (11D) and
the 5D framework. This computation is technical, and doing it correctly in the
presence of the orbifold requires methods from algebraic geometry (Calabi-Yau
cohomology) that are not implemented in the current framework.

---

## Gap 5: The Higgs Mass Precision

The tree-level Higgs mass prediction is 143 GeV (14% off). The top-corrected
prediction is 124 GeV (< 1% off).

The discrepancy between tree-level and corrected suggests that the top Yukawa
correction is large and sensitive to the choice of cutoff scale Λ_KK. The
framework uses Λ_KK ≈ 327 GeV — a value chosen to reproduce m_H. This is a
circular argument at the 1% level: the correction depends on a parameter that
is set by requiring the correction to work.

An independent derivation of Λ_KK from the 5D metric is needed. This requires
the full KK tower spectrum, which requires solving the full 5D equations of
motion numerically. This is technically feasible but not yet done.

---

## Gap 6: CMB Acoustic Peak Positions

The framework derives the primordial spectral index nₛ and amplitude P_s.
The amplitudes of the acoustic peaks in the CMB power spectrum were addressed
by Pillars 57 and 63 (radion amplification + baryon loading). What remains:

The full Boltzmann integration of the acoustic peak *positions* (the ℓ-values
of maxima and minima). The KK correction to peak positions is predicted at
δ_KK ≈ 8 × 10⁻⁴ — below current Planck sensitivity, but potentially accessible
to future CMB surveys (CMB-S4, Simons Observatory).

This is an open prediction that requires a full Boltzmann code integration.

---

## Gap 7: Quantum Gravity Regime

The framework is an effective theory valid below the compactification scale M_KK.
What happens at shorter distances — how the 5D geometry behaves at Planck energies,
whether the KK resonances are resolved or merged into a continuum — is outside
the framework's scope.

Specifically: the framework does not resolve black hole singularities, does not
describe the Planck-scale structure of spacetime, and does not provide a
non-perturbative completion of quantum gravity. The FTUM fixed point S* = A/(4G)
is an attractor in the effective theory; what lies beyond it is unknown.

---

## The Accounting, Honestly

| Category | Status |
|----------|--------|
| Arrow of time | ✅ Derived |
| Three generations | ✅ Derived |
| Fine structure constant | ✅ Derived |
| CMB observables (nₛ, r, β) | ✅ Derived |
| CKM Wolfenstein (λ, A, η̄) | ✅ Derived at 0.6–2.3% |
| PMNS CP phase | ✅ Closed at 0.05σ |
| Fermion mass ratios | ✅ Mechanism derived |
| Higgs mass | ⚠️ Estimate, 1% with correction |
| Solar neutrino angle θ₁₂ | ⚠️ 13% off |
| Absolute fermion masses | ❌ Overall scale open |
| Strong coupling α_s | ❌ Not derived |
| G₄-flux M-theory uniqueness | ❌ Step 4 open |
| CMB peak positions | ❌ Full Boltzmann pending |
| Quantum gravity | ❌ Out of scope |

The ✅ entries are what justifies taking this framework seriously. The ❌ entries
are what prevents calling it a complete Theory of Everything. Both are true
simultaneously, and both are stated without qualification.

---

## The Virtue of Honest Gaps

A framework that claims to explain everything explains nothing. A framework that
claims to explain exactly what it explains — and documents precisely what it
does not — is doing science.

The gaps listed here are not embarrassments. They are the research program.
Every gap is a specific, tractable problem with a clear statement of what would
constitute progress. The absolute mass scale requires deriving λ_Y. The solar
angle requires next-order TBM corrections. The G₄-flux requires M-theory
moduli stabilization.

These are hard problems. They are also exactly the problems that a 5D geometric
framework should be positioned to address.

---

*Full source code, derivations, and 17,438 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Complete gap list: `FALLIBILITY.md`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
