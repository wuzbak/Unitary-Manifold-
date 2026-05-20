# Pillars 278 + 279: Replacing a Scan With a Theorem, and a Data Point With a Convention

*Post 198 of the Unitary Manifold series.*  
*Series S02, Episode E024.*  
*Epistemic category: **A/P** — adjacent research tracks, non-hardgate, algebraic closure + uniqueness obstruction.*  
*May 2026.*

---

**Two pillars in this sprint upgraded claims from "numerically attested" to "algebraically proven" — and in one case, reached an honest wall.** This post covers both because they are philosophically paired: one closes cleanly, the other reaches a conditional boundary and documents it accurately.

---

## Pillar 278: Why the Flux Count Is Exactly 2 · n_flux, Not Approximately

### The problem with "scan-attested"

The SC4 sector of the framework concerns the flux landscape — the space of consistent Calabi-Yau three-fold (CY₃) compactifications with integer-valued fluxes that stabilize the moduli. A key quantity in this sector is the effective flux multiplicity: how many independent flux channels are available for a given CY₃?

The previous SC4 closure used a number called `DUAL_FLUX_MULTIPLICITY = 2`. This meant: the effective flux count is twice the base flux count, n_eff = 2 · n_flux. For the canonical n_flux = 37 (which arises from the Chern-Simons level K_CS = 74 = 5² + 7² via K_CS / 2), this gives n_eff = 74 effective flux wrappings.

The number 74 also appears as the SC4 closure requirement: at least 74 effective flux channels are needed to span the relevant moduli space. So n_eff = 74 meets the gate. Good.

The problem: the factor of 2 was attested by a numerical scan over N_flux sample values. A scan can verify a claim in the sampled range, but it does not prove the claim for all CY₃ geometries with this orientifold. A theorem does.

### Theorem 278.1 and the orientifold projection

Pillar 278 replaces the scan with Theorem 278.1, which proves the factor of 2 algebraically from the structure of the WS-V orientifold.

The argument rests on the orientifold involution σ : X → X acting on the CY₃'s (2,1)-form basis {α_I, β^I} with I = 1, …, h^{2,1}(X):

    σ* α_I = +α_I     (eigenvalue +1, invariant)
    σ* β^I = −β^I     (eigenvalue −1, anti-invariant)

The unprojected RR/NS-NS flux quantum count is 2 · h^{2,1} — one ℤ-valued flux per generator α_I and one per β^I. Under the orientifold projection, the β^I sector is eliminated. But the surviving α_I sector supports *two independent* flux channels: F₃ (RR 3-form) and H₃ (NS-NS 3-form). These are not identified with each other under σ because they are sourced by distinct field-strength operators.

Therefore, the effective count of independent flux quanta on the orientifold is:

    n_eff(X) = 2 · h^{2,1}(X) = 2 · n_flux(X)

The factor of 2 is *exact*. It is not an average over the scan, not a typical value, not an upper bound. It is the algebraic consequence of the orientifold projection having exactly two surviving independent flux channels per invariant 3-cycle.

For n_flux = 37: n_eff = 74, matching the SC4 requirement exactly. For any other CY₃ in the same orientifold family, the ratio is always exactly 2. The scan is obsolete.

---

## Pillar 279: n_w = 5, But Only If You Accept One Convention

### The {5, 7} degeneracy

The braid resonance constraint that selects the compactification geometry is:

    K_CS = n_w² + m_w² = 74 = 5² + 7²

This has exactly one positive-integer solution (up to order): the unordered pair {5, 7}. So the primary winding number n_w is either 5 or 7. The existing framework breaks this tie using the Planck nₛ χ² preference: n_w = 5 gives a slightly better fit to the observed CMB spectral index nₛ = 0.9649 than n_w = 7.

That is a valid selection criterion. But it invokes observational data. The question Pillar 279 addresses is: can we select n_w = 5 from geometry alone, without invoking Planck?

### Three observations toward a Planck-free selection

Pillar 279 establishes three observations:

**Observation 279.1 (chirality).** The torus links T(p, q) and T(q, p) are ambient isotopic as unoriented links, but have opposite handedness as oriented torus links once a spacetime orientation is fixed. The braid pairs (n_w, m_w) = (5, 7) and (7, 5) are related by the parity operation P on the T² compactification.

**Observation 279.2 (CP-fixed orientation).** The Standard Model exhibits measured CP violation: the CKM phase δ_CKM ≈ 1.196 rad ≠ 0. This fixes a definite handedness on the 5D KK background through the Wess-Zumino term coupling (realized via the Z₂ orbifold in `src/core/strong_cp_pq_z2_closure.py`). A non-zero CKM phase means the two ordered pairs (5, 7) and (7, 5) are physically distinguishable — they correspond to opposite parities of the compactification.

**Observation 279.3 / Convention 279.3 (short/long cycle assignment).** The geometric prescription assigns the *primary* winding number n_w to the *short* cycle of the modular T² — the fundamental period with smaller radius — and the secondary m_w to the long cycle. This convention, if accepted, immediately selects:

    n_w ≤ m_w  →  (n_w, m_w) = (5, 7)  →  n_w = 5

### The honest boundary

The argument above selects n_w = 5. But it does so conditionally: if Convention 279.3 is accepted. The remaining open question is *why* the primary winding number is assigned to the short cycle and not the long cycle from first principles.

Pillar 279 does not paper over this. The module's documentation explicitly labels the result:

> Planck-free selection of n_w = 5 is achieved subject to one named convention, narrowing FALLIBILITY Admission #3 from a two-step ambiguity {5,7}-then-χ² to a single-convention obstruction.

FALLIBILITY Admission #3 — the n_w uniqueness gap — is now narrower. It was "uniqueness not proved from first principles alone, requires Planck nₛ selection." It is now "uniqueness conditional on the short-cycle assignment convention; that convention's first-principles justification is the remaining open question."

That is progress. Conditional but documented progress. The plan for this sprint (§C.6) acknowledged in advance: "If the proof fails, that itself is a rigorous outcome documented in FALLIBILITY." This is the rigorous outcome: a conditional proof, honestly labeled.

---

## What these two pillars have in common

Pillars 278 and 279 were both working on the same underlying problem: claims that were stated as facts but rested on weaker foundations than they appeared. A scan-attested multiplicity and a Planck-selected winding number both have the shape of conclusions but not always the foundations of derivations.

Pillar 278 upgrades the multiplicity from scan to theorem. That is a clean win.

Pillar 279 upgrades the winding selection from two-step-with-data to one-convention. That is a genuine improvement, and also a genuine boundary — the convention itself needs first-principles justification before the selection is fully closed.

In both cases, the sprint ends with a clearer picture of what is established and what remains. That is the only kind of progress worth having.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*  
*The Unitary Manifold: https://github.com/wuzbak/Unitary-Manifold-*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

---

*Post 198 — Series S02E024 — May 2026*  
*One claim became a theorem. One data-dependent selection became a convention. Both are improvements. Neither is complete.*
