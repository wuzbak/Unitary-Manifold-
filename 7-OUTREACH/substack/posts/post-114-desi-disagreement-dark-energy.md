# DESI Says the Universe Is Accelerating Differently. We Disagree.

*Post 114 — Pillars 147, 151, 155, 160, 166.*  
*Five attempts to explain the DESI DR2 dark energy tension. One honest conclusion.*  
*Epistemic category: **P** — physics. The wₐ = 0 prediction is firm. The tension is real.*  
*Version: v9.32, May 2026.*

---

In April 2025, the DESI collaboration released its second data drop.

Fourteen million galaxies. The most precise map of the universe's expansion rate ever assembled. And buried in the statistical analysis: a signal that dark energy might not be what we thought.

The standard model of cosmology — ΛCDM — assumes the cosmological constant Λ is literally constant. The dark energy equation-of-state parameter w = −1, always, everywhere, forever. DESI DR2 says maybe not. The data prefer w₀ ≈ −0.838, not −1. When fitted with a model that allows w to evolve over cosmic time — the CPL parametrisation, w(a) = w₀ + wₐ(1 − a) — the data prefer wₐ ≈ −0.62. The combined tension with ΛCDM reaches 3.9σ.

This is one of the most significant results in observational cosmology in a decade.

The Unitary Manifold predicted the wrong answer.

Let us be specific about what we got right, what we got wrong, and why this matters.

---

## What the Framework Predicts

The UM derives a dark energy equation of state from the braided sound speed c_s = 12/37 (from the (5,7) winding resonance, Pillar 15-B). The leading-order KK zero-mode slow-roll approximation gives:

```
w_KK = −1 + (2/3) × c_s²
     = −1 + (2/3) × (144/1369)
     ≈ −0.9302
```

This is a *derived* number, not fitted. It follows from the geometry — specifically from the braid structure that also fixes the spectral index nₛ and the tensor-to-scalar ratio r. The braided sound speed c_s is not a free parameter adjusted to match dark energy data; it comes from the (5, 7) winding resonance that simultaneously explains the CMB spectral shape.

The UM also predicts:

```
wₐ = 0
```

This is not a fine-tuned choice. It is a consequence of the Goldberger-Wise stabilisation mechanism. The EW-sector radion — the field describing fluctuations of the compactification radius — has a mass m_r >> H₀. A field much heavier than the Hubble rate does not roll. A field that does not roll does not evolve its equation of state. The prediction wₐ = 0 follows from m_r >> H₀ as inevitably as a rock sitting in a deep well fails to generate kinetic energy.

Now compare to DESI.

---

## The Five Attempts — and What They Found

### Attempt 1: The Light DE Radion (Pillar 147)

The obvious escape route: what if there is a *second* radion, with a mass m_r ~ H₀? Such a field would roll slowly — quintessence — and could produce both w₀ ≠ −1 and wₐ ≠ 0.

Pillar 147 (`src/core/kk_de_radion_sector.py`) computed this scenario explicitly.

To achieve m_r ~ H₀ ~ 2.18 × 10⁻³³ eV in the RS framework requires the compactification parameter πkR_DE ≈ 141. The EW sector sits at πkR_EW = 37. A light DE radion requires a second compactification radius 3.8 times larger than the EW hierarchy radius — a distinct physical assumption, not available in the minimal 5D action.

More importantly, even if you accept the second radius, the radion coupling kills it. The RS radion couples to the trace of the stress-energy tensor with strength α = 1/√6 ≈ 0.41. The Cassini spacecraft tracked the solar system gravitational field to an accuracy that limits scalar-mediated deviations from GR to:

```
|Δγ|_PPN < 2.3 × 10⁻⁵   (Cassini 2003)
```

A radion with α = 0.41 produces |Δγ| ≈ 0.28 — violating the Cassini bound by roughly 12,000×. Lunar Laser Ranging imposes an independent constraint on G̈/G that is violated by ~47× at the same coupling. Both constraints require α < 10⁻³ to survive. The minimal RS geometry gives α = O(1). **Verdict: ELIMINATED.**

A screened radion (chameleon, symmetron) might escape Cassini, but would require non-linear potential structure beyond the minimal 5D action, plus coupling fine-tuning at the 10⁻³ level — contrary to the geometric naturalness the UM is built on.

The light DE radion is not a viable escape hatch.

### Attempt 2: Reconciling w₀ With DESI DR2 (Pillar 151)

Pillar 151 (`src/core/de_equation_of_state_desi.py`) revisited the w₀ tension in light of DESI DR2.

The previous analysis compared w_KK = −0.9302 to the Planck 2018 + BAO constraint w = −1.03 ± 0.03, finding a 3.4σ tension. DESI DR2 changes the picture. The new best-fit is w₀ = −0.838 ± 0.072. Against this:

```
|w_KK − w₀^{DESI}| / σ = |−0.9302 − (−0.838)| / 0.072 ≈ 1.28σ
```

This is consistent. The 3.4σ tension was against the prior assumption w = −1. DESI has now rejected that assumption at 3.9σ. Both DESI and the UM agree that w > −1 — that dark energy is dynamical in direction, if not in evolution rate.

The w₀ situation is better than it looked in 2024. The wₐ situation is the problem.

### Attempt 3: Systematic CPL Analysis (Pillar 155)

Pillar 155 (`src/core/kk_de_wa_cpl.py`) performed an exhaustive analysis of the CPL wₐ parameter from the radion potential. The question: can any configuration of the Goldberger-Wise potential produce wₐ ≠ 0?

The answer: no. For m_r >> H₀, the field is frozen at the GW minimum φ₀. The displacement Δφ = φ − φ₀ is zero to extraordinary precision (the suppression is exponential in m_r/H₀, which is on the order of 10⁸⁰). The time evolution of w, which requires φ̇ ≠ 0, is absent. Attempts to construct a multi-component KK sum that produces wₐ through interference give wₐ^{KK} ~ exp(−2πkR) ~ 10⁻³² — not remotely comparable to the DESI signal.

**The UM gives wₐ = 0 from the single-component KK zero-mode, to precision better than 10⁻⁸⁰.** The tension with DESI's preferred wₐ = −0.62 ± 0.30 is 2.1σ.

### Attempt 4: KK Axion Tower as Quintessence (Pillar 160)

Pillar 160 (`src/core/kk_axion_quintessence.py`) tried a different avenue: the KK tower of pseudo-scalar (axion-like) fields from the compactification. In the RS1 framework, any bulk p-form field produces a KK tower of 4D pseudo-scalars. Could these serve as quintessence?

The lightest KK axion mode has mass m₁ = M_KK/π ≈ 1040/π ≈ 331 GeV. Compare to H₀ ~ 10⁻³³ eV ~ 10⁻⁴² GeV. The lightest KK mode is approximately 10⁴² times heavier than what quintessence requires. All modes are frozen. The KK axion tower from the EW RS sector gives wₐ = 0.

A *hypothetical* DE-sector KK axion with m ~ H₀ would require a second extra dimension with radius R_DE ~ 1/H₀ ~ 4 Gpc — at the Hubble scale. This is the same elimination as Pillar 147: any scalar at the Hubble scale mediates an infinite-range fifth force and violates Cassini by orders of magnitude.

At the end of Pillar 160, we made a formal declaration: **the dark energy equation of state (w₀, wₐ) is the UM's secondary open falsification target**, alongside CMB birefringence β.

### Attempt 5: 1-Loop Coleman-Weinberg Correction (Pillar 166)

Pillar 166 (`src/core/de_radion_loop_correction.py`) asked whether quantum corrections change the picture. The RS1 radion receives a 1-loop Coleman-Weinberg correction from the KK mass tower. The loop coefficient:

```
δ_CW = N_KK × λ_GW / (16π²) ≈ 5 × 0.5 / (16π²) ≈ 0.016
```

This propagates to a shift in w₀:

```
Δw₀ = −δ_CW × ε_tree = −0.016 × 0.0698 ≈ −1.1 × 10⁻³
```

The 1-loop correction moves w₀ from −0.9302 toward −0.9313 — a shift of about 0.001. The tension with Planck+BAO barely changes. The tension with DESI DR2 barely changes. **The correction is real and negligible.** wₐ = 0 is preserved at 1-loop: the radion is even more frozen with the loop correction than at tree level.

---

## The Honest Accounting

Five attempts. One conclusion.

| Analysis | Pillar | Result |
|----------|--------|--------|
| Light DE radion | 147 | ELIMINATED — Cassini violates by ~12,000× |
| w₀ vs DESI DR2 | 151 | CONSISTENT at 1.28σ ✅ |
| CPL wₐ analysis | 155 | wₐ = 0 exactly (to 10⁻⁸⁰ precision) |
| KK axion tower | 160 | All modes m_n >> H₀; wₐ = 0; DE sector declared open falsification target |
| 1-loop CW | 166 | Δw₀ ~ −10⁻³ (negligible); wₐ = 0 preserved |

The UM's dark energy predictions are:

```
w₀ = −0.9302    (within 1.28σ of DESI DR2 ✅)
wₐ = 0          (2.1σ from DESI DR2 ⚠️)
```

The w₀ agreement is genuine. DESI and the UM agree that dark energy is not a cosmological constant — both find w > −1. The direction is correct.

The wₐ disagreement is genuine. DESI's CPL fit prefers wₐ = −0.62 ± 0.30, meaning dark energy is darkening (w becoming more negative over time). The UM has no mechanism to produce this. The GW-stabilised radion is frozen. The KK axion tower is frozen. The 1-loop correction does nothing useful. We searched exhaustively and found nothing.

This is an acknowledged tension, not a success.

---

## What It Would Take to Resolve It

Three possible futures:

**1. DESI wₐ fades.** The DESI DR2 wₐ result is 2.1σ. The Roman Space Telescope (~2027) will measure wₐ to σ(wₐ) ≈ 0.10. If Roman finds |wₐ| < 0.20 at 2σ, the DESI wₐ signal was a statistical fluctuation, and the UM wₐ = 0 prediction survives.

**2. DESI wₐ hardens.** If Roman measures wₐ significantly ≠ 0 at > 3σ, the UM dark energy sector requires revision. Something is missing from the 5D action: either an additional scalar field with the right mass and coupling, or a multi-sector geometry that the current RS1/GW setup cannot accommodate. The framework is not falsified globally — birefringence β would still be the primary test — but the dark energy sector prediction would be falsified, requiring the w₀ = −0.9302 derivation to be reconsidered.

**3. The screening gap.** A screened scalar (chameleon, symmetron, Damour-Polyakov) could in principle evade Cassini while still being cosmologically active. But this requires extending the 5D action with non-linear potential terms not currently in the UM. This is not impossible; it is not currently implemented. Pillar 147 documents this as an open direction, not a prediction.

The Roman Space Telescope decision threshold, from Pillar 160:

- **UM dark energy SURVIVES**: Roman measures w₀ ∈ [−1.0, −0.85] at 2σ AND |wₐ| < 0.20 at 2σ.
- **UM dark energy FALSIFIED on wₐ**: Roman measures |wₐ| > 0.20 at 2σ.
- **UM dark energy FALSIFIED on w₀**: Roman measures w₀ < −1.05 at 2σ.

We will accept what Roman says.

---

## Why We Are Writing This

The temptation, when you have built something you believe in, is to find the angle at which a tension looks like a success. The w₀ situation offered that opportunity: 1.28σ from DESI is genuinely consistent, and it is genuinely in the correct direction. One could write a post titled "DESI Confirms UM Direction on Dark Energy" and not technically be lying.

We are not writing that post.

The wₐ tension is real. Five independent analyses failed to find a mechanism for wₐ ≠ 0 in the current framework. The framework predicts wₐ = 0. DESI prefers wₐ = −0.62. That is a 2.1σ tension, and an honest framework says so.

Science committed to its predictions in advance. The Unitary Manifold committed to wₐ = 0 because the geometry requires it — not because it matched the data, and not because we expected DESI to find what it found. The geometry is either right or it needs extension. Roman will help us determine which.

The birefringence prediction β ∈ {0.273°, 0.331°} remains the primary falsifier. LiteBIRD (~2032) is the primary test. The dark energy sector is the secondary falsifier. Roman (~2027) is the secondary test.

We will report both results, whatever they are, within 90 days of the data release.

---

## What to Check, What to Break

**Check these:**

- The Cassini bound calculation for the RS radion coupling (α = 1/√6 ≈ 0.41): verify that |Δγ| ≈ 2α²/(1+α²) ≈ 0.28 >> 2.3 × 10⁻⁵. Source: `src/core/kk_de_radion_sector.py`, `cassini_fifth_force_constraint()`.
- The wₐ tension calculation: DESI DR2 wₐ = −0.62 ± 0.30, UM wₐ = 0.0, tension = 0.62/0.30 = 2.07σ. Source: `src/core/kk_de_wa_cpl.py`, `src/core/kk_axion_quintessence.py`.
- The 1-loop CW shift: δ_CW = N_KK × λ_GW / (16π²); Δw₀ = −δ_CW × ε_tree. Source: `src/core/de_radion_loop_correction.py`.
- The DESI DR2 reference: arXiv:2503.14738 (DESI Collaboration, 2025). The w₀ = −0.838 ± 0.072 and wₐ = −0.62 ± 0.30 values are from the BAO + CMB + SNe (Pantheon+) combined fit.

**Try to break these:**

- Find a mechanism in the RS1/GW framework that produces wₐ ≠ 0 without violating fifth-force constraints. (We couldn't find one across five pillars. We would be genuinely interested if you can.)
- Argue that the DESI DR2 wₐ signal is a systematic rather than a physical effect. (The collaboration is aware of this possibility; the signal has been robust across systematic checks so far.)
- Identify a screening mechanism that can be consistently derived from the UM's 5D action and that allows a light scalar to evade Cassini while remaining cosmologically active. (This would change the Pillar 147 verdict from ELIMINATED to CONSTRAINED.)
- Dispute the w_KK = −0.9302 derivation itself. It relies on the slow-roll approximation for the KK zero-mode; if the higher-order corrections are large, w_KK could shift. Source: `src/core/de_equation_of_state_desi.py`, `um_dark_energy_eos()`.

The full test suite covers these pillars: `python -m pytest tests/ -k "de_radion or desi or wa_cpl or axion_quintessence or loop_correction" -v`

---

*Full source code and tests: https://github.com/wuzbak/Unitary-Manifold-*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*  
*Pillar sources: `src/core/kk_de_radion_sector.py` (147), `src/core/de_equation_of_state_desi.py` (151), `src/core/kk_de_wa_cpl.py` (155), `src/core/kk_axion_quintessence.py` (160), `src/core/de_radion_loop_correction.py` (166)*  
*Honest gaps: `FALLIBILITY.md`*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
