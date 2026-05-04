# Why Matter Won: Baryogenesis from the Chern-Simons Field

*Post 102 of the Unitary Manifold series.*  
*Pillars 105–106 — Baryogenesis from B_μ, dark matter as KK graviton modes.*  
*v9.32, May 2026.*

**Epistemic categories:** P (baryogenesis mechanism, CS level derivation), A (dark matter KK mode counting is exploratory; the hot-relic formula is a framework estimate, not a precision calculation).

---

## The Universe Cheated, and We Are Here Because of It

At the moment of the Big Bang — or rather, in the first microseconds after it — the universe produced equal numbers of particles and antiparticles. We think this because every process in the Standard Model that creates a particle also creates an antiparticle. Matter and antimatter are mirror images. The laws of physics, at the level we understand them, do not obviously distinguish between them.

And yet you are reading this. The chair beneath you is matter. The air in the room is matter. The galaxy containing you is matter, and so is every galaxy we have ever observed. The antimatter is gone. Every positron we detect was created freshly from some energetic collision; there is no *ambient* antimatter reservoir.

Something broke the symmetry. The universe cheated, and everything that exists — every atom, every cell, every mountain and ocean and star — is the residue of that cheat.

The fraction of the cheat is measurable. For every 10 billion antiprotons created in the first second, approximately 10 billion and one protons were created. The surviving one-in-ten-billion is the entire material content of the observable universe. In the language of cosmology, this is expressed as the baryon-to-photon ratio:

    η_B ≡ n_B / n_γ ≈ 6 × 10⁻¹⁰

Measured by Planck 2018 through the CMB acoustic peak heights. Measured independently by Big Bang nucleosynthesis through the helium and deuterium abundances. The two measurements agree. The number is real, it is tiny, and the Standard Model cannot explain it.

---

## What the Standard Model Says (and Why It Fails)

The conditions for baryogenesis were laid out by Andrei Sakharov in 1967: you need baryon number violation, C and CP violation, and departure from thermal equilibrium. The Standard Model has all three ingredients in principle. In practice, the CP violation in the CKM matrix — the observed mismatch between quarks and antiquarks — is many orders of magnitude too small to produce η_B ≈ 6 × 10⁻¹⁰. The electroweak phase transition in the SM is not strongly first-order at the measured Higgs mass, so the departure from equilibrium is insufficient. The Standard Model fails baryogenesis by approximately ten orders of magnitude in the CP-violation alone.

This is one of the most concrete failures of an otherwise spectacularly successful theory. Something beyond the Standard Model is required.

---

## Pillar 105: The Chern-Simons Answer

The Unitary Manifold's answer begins with the Chern-Simons level k_CS = 74.

This number — derived algebraically from the braid pair (5,7) as k_CS = 5² + 7² = 74, confirmed by seven independent physical constraints — enters the baryogenesis calculation through a specific channel: the CP-violation amplitude of the irreversibility field B_μ.

In the framework, B_μ is not the Standard Model Higgs field or any Standard Model field. It is the five-dimensional gauge potential whose compactification encodes the direction of irreversibility — the geometric origin of the arrow of time. When this field interacts with the electroweak sector during the EW phase transition, it breaks CP symmetry through its Chern-Simons coupling at level k_CS = 74.

The CP-violation amplitude derived from this coupling is (`src/core/baryogenesis.py`, Pillar 105):

    ε_CP = k_CS / (k_CS² + 4π²)
          = 74 / (5476 + 39.48)
          ≈ 0.01342

This is not a fitted parameter. The formula follows from the Chern-Simons path integral with level k_CS — a standard construction in topological field theory, applied here to the KK irreversibility sector.

---

## The Sphaleron Bridge

To convert a CP asymmetry into an actual baryon number excess, you need *sphaleron transitions* — non-perturbative electroweak processes that violate baryon number by converting three quarks into three leptons (or vice versa), mediated by the topology of the electroweak gauge field. Sphalerons are suppressed at low temperatures by a factor ∼ e^{−E_sph/T}, but at T ≳ 100 GeV they operate rapidly.

The sphaleron transition rate per unit volume at the electroweak scale is:

    Γ_sph = α_w⁴ × T_EW

with α_w = 1/30 the weak coupling at the EW scale and T_EW = 246 GeV. The baryon-to-photon ratio generated during the EW phase transition, in the standard freeze-out approximation, is:

    η_B = ε_CP × α_w⁴ × (45 / 2π² g*)

where g* = 106.75 is the effective number of relativistic degrees of freedom in the SM at T_EW.

Computing numerically from `baryogenesis_summary()`:

| Quantity | Value | Observed |
|----------|-------|----------|
| ε_CP (CS level 74) | 0.01342 | — |
| η_B (predicted) | 3.54 × 10⁻¹⁰ | 6 × 10⁻¹⁰ |
| Order-of-magnitude match | ✅ | — |

The prediction is 3.54 × 10⁻¹⁰ against an observed 6.0 × 10⁻¹⁰ — a factor of 1.7 discrepancy. The order-of-magnitude match is genuine. The factor-of-two gap is honest.

What does the factor of 1.7 mean? Three possibilities:

1. The sphaleron rate formula used here (Γ_sph = α_w⁴ × T_EW) is the leading-order estimate; higher-order corrections to the sphaleron rate are known to be O(1) and could bridge the gap.
2. The EW phase transition in the UM may be slightly more strongly first-order than in the pure SM, because B_μ contributes to the effective potential. A more first-order transition means a larger departure from equilibrium and a larger η_B.
3. The factor-of-two gap may survive and require a modification of the CP-violation formula.

The code (`src/core/baryogenesis.py`) tracks this honestly. The `order_of_magnitude_match` flag is True (|log₁₀(η_B/6×10⁻¹⁰)| < 2); the `cp_amplitude` and `eta_B` values are returned numerically so future improvements can track the residual.

The key point is the *mechanism*, not just the number: the CP violation in the Unitary Manifold is *geometrically* sourced from the Chern-Simons level of the compactification, not from an explicit free phase in the Standard Model Lagrangian. If k_CS = 74 is the correct level — which is an algebraic consequence of the braid pair (5,7) and the winding number n_w = 5 — then the baryon asymmetry is not an unexplained accident. It is the geometric residue of the same structure that selects the winding number.

---

## Pillar 106: Dark Matter as KK Graviton Modes

*Epistemic category for this section: A. The KK graviton dark matter candidate is a framework exploration, not a precision prediction.*

In a theory with a compact extra dimension, every four-dimensional field acquires a tower of *Kaluza-Klein excitations* — heavier copies at masses M_n = n × M_KK, where M_KK is the compactification scale. For the Unitary Manifold, the lightest KK graviton mass is given by (`src/core/dark_matter_kk.py`, Pillar 106):

    M_KK = φ₀ × (n_w² + √k_CS) × 10⁻³  [eV]
          = 1.0 × (25 + 8.602) × 10⁻³
          ≈ 33.6 meV

This is in the milli-electronvolt range — ultralight. The corresponding relic density, computed in the hot-relic approximation:

    Ω_KK h² = (M_KK / 94 eV) × (g_KK / g*_s)
             = (0.0336 / 94) × (2 / 3.91)
             ≈ 1.83 × 10⁻⁴

This is well below the Planck 2018 dark matter bound Ω_DM h² ≈ 0.12 — meaning the lightest KK graviton mode, if it exists, is *not* the dominant dark matter component. It contributes less than 0.2% of the required dark matter energy density.

Is this a problem? Not necessarily. The KK tower contains multiple modes, and the mass formula M_n = n × M_KK gives higher modes at 67 meV, 101 meV, 134 meV, and so on. These are still ultralight. For the KK tower to account for the full dark matter abundance, either the mass scale needs to be higher (of order eV to keV, depending on the mechanism) or there are additional KK fields with different spin content.

The honest summary of Pillar 106: the lightest KK graviton is a viable but subdominant dark matter component. The framework is consistent with dark matter observations in the sense that it does not *overproduce* KK relics (which would rule out the compactification). Whether the KK tower explains dark matter, or whether dark matter is explained by another sector of the theory entirely, is an open question that requires UV-completing the coupling of the KK modes to the Standard Model bath.

The `dark_matter_kk_summary()` function returns `n_viable_modes: 5`, meaning five KK modes satisfy the Planck relic density bound individually. The combined contribution is small.

---

## Why the Geometry, Not the Phase

There is a conceptual point worth pausing on, because it distinguishes the Unitary Manifold's approach to baryogenesis from the Standard Model's.

In the SM, CP violation enters through the CKM matrix — a 3×3 unitary matrix with one irreducible complex phase δ_CKM. This phase is a free parameter. We measure it to be δ_CKM ≈ 68°. But there is no reason it couldn't be 0°, in which case no CP violation and no baryogenesis. The value is what it is; the SM provides no explanation.

In the Unitary Manifold, the CP violation that drives baryogenesis comes from k_CS = 74, which is not a free parameter — it is an algebraic consequence of the braid pair (5,7). And the braid pair is constrained (though not yet uniquely determined from first principles alone) by the requirement that the birefringence angle β fall in the observed window and that n_w = 5 produces the correct CMB spectral index. The CP violation is woven into the same geometric structure that gives us the arrow of time, the fermion generations, and the inflation observables.

This is either a remarkable unification or a remarkable coincidence. LiteBIRD and DUNE will help discriminate. If β ≈ 0.331° and δ_CP^PMNS ≈ −108° are confirmed simultaneously — two predictions from the same k_CS = 74 — the coincidence becomes harder to maintain.

---

## What to Check, What to Break

**Check:** Run `from src.core.baryogenesis import baryogenesis_summary; print(baryogenesis_summary())`. Verify that η_B ≈ 3.54 × 10⁻¹⁰ and that `order_of_magnitude_match` is True.

**Check:** Verify the dark matter relic density is subdominant: `from src.core.dark_matter_kk import dark_matter_kk_summary; print(dark_matter_kk_summary())`. Confirm Ω_KK h² ≈ 1.83 × 10⁻⁴ ≪ 0.12.

**Break:** The CP-violation formula ε_CP = k_CS / (k_CS² + 4π²) derives from the Chern-Simons path integral. Show that this formula overcounts or undercounts the actual CP asymmetry generated in the EW plasma — i.e., find the correct finite-temperature correction to the CS effective action that changes ε_CP by a factor of 1.7 upward. That would close the gap; a correction in the opposite direction would deepen it.

**Break:** The hot-relic formula for Ω_KK h² assumes the KK graviton decoupled from the SM plasma when g*_s ≈ 3.91 (today's value). If the KK mode decoupled during radiation domination at high temperature, use g*_s ≈ 106.75 at decoupling — this changes the relic density by a factor of (106.75/3.91) ≈ 27, which would make the lightest KK mode even more subdominant. Verify which value is physically correct for a mode with M_KK ≈ 34 meV.

**Break the mechanism:** The Sakharov conditions require departure from thermal equilibrium. The UM sphaleron calculation uses a freeze-out approximation that assumes the EW transition is instantaneous. Construct the B_μ-corrected effective potential at T = T_EW and compute the bubble nucleation rate. If the transition is a smooth crossover (not first-order), sphalerons equilibrate and wash out any asymmetry — the baryogenesis mechanism fails regardless of ε_CP. This calculation is open.

---

*Full source code, derivations, and 20,249 automated tests:*  
*https://github.com/wuzbak/Unitary-Manifold-*  
*Baryogenesis: `src/core/baryogenesis.py` (Pillar 105)*  
*Dark matter KK modes: `src/core/dark_matter_kk.py` (Pillar 106)*  
*Honest gaps: `FALLIBILITY.md`*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
