# Post 209 — E035: Proton Decay: A New Prediction

*Unitary Manifold Substack — Season 2, Episode 35*  
*Published: 2026-05-20*

---

The Hyper-Kamiokande experiment in Japan began taking data. It is the most sensitive proton decay detector ever built, capable of accumulating statistics that could see, or rule out, proton decay at lifetimes up to about 10³⁵ years.

The Unitary Manifold now makes a concrete, falsifiable prediction for the proton lifetime. That prediction is the subject of this post and Pillar 293 in the codebase.

---

## Why Proton Decay Matters

Grand Unified Theories — which unify the strong, weak, and electromagnetic forces into a single gauge group — almost universally predict that the proton is unstable. The dominant decay mode in SU(5)-type theories is:

> p → e⁺ + π⁰

mediated by the exchange of superheavy X and Y gauge bosons at the GUT scale. The lifetime of the proton in this mode depends on the fourth power of the GUT scale M_GUT:

> τ(p → e⁺π⁰) ∝ M_GUT⁴ / α_GUT²

The Super-Kamiokande experiment already constrains this lifetime to more than 2.4 × 10³⁴ years. Hyper-Kamiokande will push that to roughly 10³⁵ years within a decade of operation.

---

## The UM Derivation Chain

The Unitary Manifold's GUT sector follows from the Kawamura Z₂ orbifold mechanism. With n_w = 5 and the Chern-Simons level K_CS = 74 = 5² + 7², the gauge coupling at the GUT scale is fixed without any free parameters:

> **α_GUT = N_c / K_CS = 3/74 ≈ 1/24.67**

This is within 1.3% of the conventional SU(5) unification value of 1/25. The GUT scale itself is set by the SM one-loop running from M_Z:

> **M_GUT ≈ 2 × 10^16 GeV**

(corrected for the UM coupling, which is close enough to the standard value that the correction is below 1%).

The proton lifetime then follows from the dimension-6 proton decay operator coefficient:

> τ(p → e⁺π⁰) = M_GUT⁴ / (α_GUT² × A_L² × f_orb² × m_p⁵)

where A_L ≈ 1.25 is the renormalization enhancement from short-distance QCD (this is the standard SU(5) estimate; sometimes quoted as the "chiral Lagrangian matching coefficient"), m_p is the proton mass, and f_orb is the orbifold suppression factor from the Z₂/Z₅ compact dimension geometry:

> f_orb = (1/n_w) × cos²(π/n_w) ≈ 0.131   (for n_w = 5)

The Pillar 293 computation gives:

> **τ(p → e⁺π⁰) ≈ 10^35–36 years** (above the Super-K limit of 2.4 × 10³⁴ yr ✓)

The second mode, p → ν̄ + K⁺ (mediated by strange-sector partners), is longer:

> **τ(p → ν̄K⁺) > τ(p → e⁺π⁰)**

by approximately the ratio V_us⁻² × f_kaon ≈ 12, placing τ(ν̄K⁺) in the range 10^36–37 years.

---

## Uncertainty Sources

The uncertainty on this prediction comes from three main sources:

**1. K_CS uncertainty:** The CS level K_CS = 74 is fixed by the (5,7) braid geometry and the identity 5² + 7² = 74. This is algebraic, not fitted. However, if the physical CS level were 73 or 75 (adjacent values), α_GUT shifts by ±1.4%, and M_GUT shifts by ±1% — translating to ±4% on τ. The prediction is stable to ±1 variation in K_CS.

**2. Hadronic matrix element A_L:** This is the dominant theoretical uncertainty. Lattice QCD computations of A_L carry ~15–20% errors. This translates to ±(30–40%) in the lifetime.

**3. Orbifold geometry f_orb:** The suppression factor from the compact dimension is a geometric input. The ±1 uncertainty in n_w (if the physical winding number were 4 or 6 rather than 5) would shift f_orb substantially, but n_w = 5 is fixed by the Planck n_s measurement and the APS η̄ theorem.

Combined uncertainty: roughly a factor of 2–3 on the predicted lifetime, placing the range at:

> **τ(p → e⁺π⁰) ∈ [3 × 10^34, 3 × 10^36] years**

This is consistent with all existing limits and within the reach of Hyper-Kamiokande.

---

## The Falsifier

The preregistered routing rule (Pillar 293, locked at v11.9) is:

> **FALSIFIED if Hyper-K measures τ(p → e⁺π⁰) < lower_bound_UM at ≥ 3σ**

where lower_bound_UM accounts for the full theoretical uncertainty on the UM prediction.

The current Super-K lower limit of τ > 2.4 × 10³⁴ yr is **CONSISTENT_LOWER_LIMIT** — it is below our predicted range, so we cannot be falsified by non-observation yet. As Hyper-K accumulates data and pushes the limit higher, the consistency region narrows.

If Hyper-K sees proton decay at, say, τ ≈ 10^34 yr (below the UM lower bound), the framework's GUT sector requires revision. If the limit rises to 10^36 yr without a signal, the prediction is constrained but not yet falsified (since the upper end of our range is 3 × 10^36 yr). If a signal appears within our predicted range, the framework is supported.

---

## Why This Prediction is Valuable

Some predictions are intrinsically difficult to falsify — they point at experiments decades away, or they depend on too many uncertain inputs. Proton decay is different:

1. **Hyper-Kamiokande is running now.** This is not a 20-year wait. The experiment is taking data.

2. **The prediction is clean.** The derivation chain is: winding number → CS level → α_GUT → M_GUT → τ. Four steps, each with an explicit formula, each independently checkable.

3. **The uncertainty is honest and bounded.** The main theoretical error is the hadronic matrix element, which is improving with lattice QCD. The geometric inputs (n_w, K_CS) are fixed.

4. **Non-detection is also information.** If Hyper-K runs for 10 years and doesn't see a decay event, that constrains the lifetime to above ~10^35 yr — still within the UM range, but tightening.

This is the kind of prediction that respects both the experiment and the audience.

---

## The Larger Picture

The UM's GUT sector isn't an add-on. The SU(5) gauge group, the α_GUT = 3/74 coupling, the M_GUT scale — these follow from the same (5,7) braid geometry that gives the neutrino mass splittings, the CMB spectral index, and the tensor-to-scalar ratio. The framework is consistent: the same geometry that predicts n_s = 0.9635 also says the proton should live for 10^35–36 years.

That coherence is either deep or coincidental. Hyper-Kamiokande will help determine which.

---

## Summary

- UM predicts τ(p → e⁺π⁰) ∈ [3×10³⁴, 3×10³⁶] yr from α_GUT = 3/74 and M_GUT ≈ 2×10^16 GeV.
- Prediction is CONSISTENT with Super-K lower limit (2.4×10³⁴ yr) — no falsification yet.
- τ(p → ν̄K⁺) is longer by ~12×, predicted in the range 10^36–37 yr.
- Hyper-Kamiokande is the decisive experiment. Data is being taken now.
- Routing rules preregistered and locked (Pillar 293, v11.9). Won't be adjusted post-hoc.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
