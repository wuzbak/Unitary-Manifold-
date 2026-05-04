# The Open Problems We Are Proud Of

*Post 118 — Epistemic category: **P** (physics gaps, documented honestly)*  
*Unitary Manifold v9.32, May 2026*

*Good science doesn't hide its failures. It names them, quantifies them, and invites people to work on them. This is an honest inventory of the five most important things the Unitary Manifold cannot currently explain.*

---

There is a category of scientific paper that makes no predictions you could test next Tuesday. It lists results, carefully avoids committing to numbers, and presents uncertainty as nuance rather than as a deficit. Reviewers call it "balanced." Readers call it "thorough." Nobody calls it falsifiable.

This is not that kind of article.

The Unitary Manifold makes specific, numbered, testable claims. It also has specific, numbered, documented failures. The failures are listed in `FALLIBILITY.md`, which is tracked in the public repository alongside the passing tests. If the framework is eventually falsified — and it could be — the failure will not be a surprise. It will be the third line of `FALLIBILITY.md`, already written, already waiting.

This article walks through the five most important open problems. Not as apologies. As markers of honest work.

---

## 1. CMB Acoustic Peak Amplitude Suppression

The Unitary Manifold derives the *shape* of the CMB power spectrum — the spectral index nₛ ≈ 0.9635, the tensor-to-scalar ratio r_braided ≈ 0.0315 — from the geometry of the braided winding state (Pillars 27–52, `src/core/braided_winding.py`). Shape: derived.

The *amplitude* is a different story.

When the framework computes the acoustic peak heights — the actual Cₗ values at ℓ ≈ 220, 540, 810 — it predicts amplitudes that are **×4.2–6.1 too small** compared to Planck 2018 observations. Pillar 149 (`src/core/cmb_peak_amplitude.py`) quantifies this suppression explicitly. Pillar 165 (`src/core/casimir_natural_bound.py`) shows that the gravitational wave warp parameter α_GW is *naturally* of order 10⁻¹⁰ from Casimir energy considerations — bounded, not unconstrained — but it doesn't fix the precise value.

The spectral shape is derived. The normalization requires one UV-brane parameter, α_GW ≈ 4×10⁻¹⁰, that the framework cannot yet fix from first principles. Until it can, the acoustic peaks are predicted in the wrong place vertically.

This is Admission 2 in `FALLIBILITY.md`, unresolved and clearly stated. A framework that suppresses acoustic peak amplitudes by a factor of five is not in agreement with the CMB data on amplitude, whatever else it gets right.

---

## 2. The A_s Normalization Problem

The amplitude suppression problem has a precise algebraic form: the primordial power spectrum normalization A_s ≈ 2.1×10⁻⁹ (Planck 2018) requires a gravitational wave warp factor α_GW ≈ 4×10⁻¹⁰ at the UV brane.

Pillar 161 (`src/core/as_normalization.py`) shows that this value is not derivable from the three central parameters of the framework — n_w = 5, k_CS = 74, πkR — alone. It is a UV-brane initial condition: something set at the beginning, not predicted by the geometry. Pillar 165 constrains α_GW to be *naturally* O(10⁻¹⁰) via Casimir energy at the GUT scale — a reassuring bound — but naturally bounded is not the same as precisely derived.

The spectral *shape* (nₛ, r) is derived with zero free parameters. The spectral *amplitude* (A_s) requires one parameter that the framework currently accepts rather than explains. This is an honest gap. It does not make the shape predictions wrong. It does mean the framework is incomplete at the level of absolute normalization.

---

## 3. DESI wₐ Tension at 2.1σ

The Unitary Manifold predicts wₐ = 0. This follows from the physics of the radion field: in the UM geometry, the compact dimension stabilizes at a fixed radius determined by the Goldberger-Wise potential, and a frozen radion gives a cosmological constant that doesn't evolve. Dark energy is a cosmological constant. wₐ = 0, exactly.

DESI Data Release 2 (2025) prefers wₐ ≠ 0 at 2.1σ. The tension is not yet a falsification — 2.1σ is below the standard 3σ threshold — but no mechanism within the Unitary Manifold produces wₐ ≠ 0. Pillar 160 (`src/core/dark_energy_eos.py`) searches for one and does not find it.

This is declared, in `FALLIBILITY.md` and `3-FALSIFICATION/OBSERVATION_TRACKER.md`, as the **secondary falsification target**. If DESI DR3 or DR4 push the wₐ tension above 3σ, that would be a strong signal that the radion is not frozen — which would require a mechanism the framework does not currently contain.

The primary falsifier remains LiteBIRD's β measurement. But the DESI wₐ result is the canary that could sing before 2032.

---

## 4. Dirac Branch C Fine-Tuning at ~1%

The Unitary Manifold generates neutrino masses through a KK Dirac mechanism. There are multiple viable branches depending on how the bulk fermion profiles are arranged. Branch C produces neutrino masses in the observed range — but it requires the right-chiral bulk mass parameter c_R to be tuned to approximately 1% precision.

Pillar 157 (`src/core/neutrino_mass_spectrum.py`) documents this: Branch C is viable, the neutrino masses are in the right ballpark, but the fine-tuning required to achieve them is ~1%, which is disfavoured by standard naturalness arguments (though not ruled out — nature has demonstrated its willingness to fine-tune in other contexts, most conspicuously in the cosmological constant problem).

The framework does not claim Branch C is the correct branch. It identifies it as viable but disfavoured. Branches A and B are less fine-tuned; Branch C is kept on the list because "less natural" and "wrong" are different claims, and it would be dishonest to discard it.

---

## 5. The Lightest Neutrino Mass

The Randall-Sundrum Dirac mechanism, taken naively with the UM geometry, predicts a lightest neutrino mass of approximately 1.086 eV. The cosmological bound (Planck 2018 + BAO) constrains the sum of neutrino masses Σmν < 0.12 eV, which — assuming near-degenerate masses — limits any individual mass to roughly 0.04 eV.

The discrepancy is a factor of ~25.

Pillar 159 (`src/core/neutrino_majorana_seesaw.py`) resolves this via a Majorana seesaw: the RS Dirac states mix with a heavy Majorana sector, driving the lightest physical mass down to below the cosmological bound. This resolution works. But it does not predict the *precise* value of the lightest neutrino mass — it establishes an upper bound but not a lower bound, leaving the precise value unconstrained within a wide window.

This means the framework is consistent with neutrino mass data but does not yet make a specific prediction about the lightest mass. A theory that predicts m₁ ∈ [0, 0.04] eV is weaker than a theory that predicts m₁ = 0.0073 eV. Documenting the gap honestly is the prerequisite for eventually closing it.

---

## Why We Are Proud of These Failures

A theory that lists its failures is more trustworthy than one that doesn't.

The five problems above are real. None of them is hidden. Each one has a pillar number, a source file, and a line in `FALLIBILITY.md` that says exactly what is wrong and what would fix it. The CMB amplitude suppression has a path to resolution (geometrically fixing α_GW). The DESI tension has a falsification threshold (3σ wₐ). The neutrino mass has a mechanism that partially works but needs to be tightened.

This is what open science looks like — not as a gesture, but as a structure. The repository is public. The tests run in minutes. The problems are named.

If you can fix one of these, the framework will be stronger. If the fixes are not possible — if the gaps prove unclosable — the framework will be wrong. Either outcome is better than not knowing.

---

## What to Check, What to Break

- **Pillar 149** (`src/core/cmb_peak_amplitude.py`): Run the acoustic peak suppression audit. Verify the ×4.2–6.1 factors. Propose a geometric mechanism to fix α_GW.
- **Pillar 161** (`src/core/as_normalization.py`): Try to derive α_GW ≈ 4×10⁻¹⁰ from n_w, k_CS, and πkR alone. If you can, the normalization problem closes.
- **Pillar 160** (`src/core/dark_energy_eos.py`): Find a UM mechanism that allows wₐ ≠ 0 without requiring a radion that is not frozen. If you can't, document why.
- **DESI data** (~2027): If DR3 pushes wₐ tension to 3σ, the framework needs to be updated or declared falsified on the secondary criterion.
- **Pillar 157** (`src/core/neutrino_mass_spectrum.py`): Check whether Branch C fine-tuning can be reduced by a bulk mass symmetry. If not, assess whether to demote Branch C further.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson. Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
