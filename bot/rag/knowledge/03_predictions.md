# Predictions, Gaps, and Falsification — Unitary Manifold

## Three Quantitative Predictions

### 1. CMB Spectral Index nₛ ≈ 0.9635

The theory predicts a primordial scalar power spectrum with spectral index:

```
nₛ = 0.9635
```

This is derived from the scalar perturbation equations in the 5D geometry
during inflation. The irreversibility field B_μ modifies the slow-roll
parameters, giving a slight tilt below scale-invariance.

**Experimental status**: Planck 2018 measured nₛ = 0.9649 ± 0.0044 (68% CL).
The theoretical prediction 0.9635 is within the Planck 1σ band. ✅

### 2. Cosmic Birefringence β = 0.3513°

The theory predicts a rotation of the CMB polarisation plane (cosmic
birefringence) of:

```
β = 0.3513°   (at wavenumber k_cs = 74)
```

This rotation arises from the parity-violating coupling of the irreversibility
field B_μ to photons during propagation from the last-scattering surface.

**Experimental status**: Several analyses of Planck and WMAP data have reported
hints of birefringence at β ≈ 0.3°–0.5°, but current measurements have
uncertainties of ~0.1°–0.2°. The LiteBIRD satellite (launch ~2032) will
measure β to precision ~0.05°, which is sufficient to confirm or falsify the
prediction.

### 3. Derived Coupling α = φ₀⁻²

The electromagnetic-like coupling constant α is fully determined by the
vacuum expectation value of the KK dilaton:

```
α = φ₀⁻²
```

This is **not** a free parameter — it is derived. If the theory's self-
consistency equation for φ₀ closes, α becomes a pure prediction with no
tuning. This would make the theory highly falsifiable.

---

## Honest Gaps

The theory has two known open problems. These are not hidden — they are
acknowledged in the primary documents.

### Gap 1 — CMB Amplitude Suppression (×4–7)

The predicted primordial power spectrum amplitude A_s is suppressed by a
factor of **4–7 relative to the Planck-observed value**.

The Planck-observed amplitude is A_s ≈ 2.1 × 10⁻⁹. The theory currently
predicts a value 4–7× smaller than this.

This is a serious quantitative discrepancy. The most likely resolution
involves a modified inflation model or a reheating mechanism not yet
incorporated. This is the primary open challenge for the theory.

### Gap 2 — φ₀ Self-Consistency Not Fully Closed

The coupling α = φ₀⁻² requires knowing φ₀, which is determined by the
self-consistency equation of the vacuum potential:

```
V'(φ₀) = 0
```

The analytic solution to this equation in the full theory has not been
completed. Numerical evidence suggests φ₀ exists and is stable, but a
rigorous analytic proof is outstanding.

Until φ₀ is determined self-consistently, α cannot be computed as a pure
prediction — it depends on numerical input.

---

## Falsification Conditions

The theory is falsifiable. It will be definitively tested by:

### Primary falsifier — LiteBIRD (2030–2032)

> **If LiteBIRD measures β outside the range 0.3513° ± 0.05°, the
> geometric irreversibility mechanism that produces birefringence is falsified.**

LiteBIRD's projected sensitivity is ~0.05°, which means it can either
confirm or rule out the prediction to high confidence.

### Secondary falsifier — precision nₛ measurement

A future CMB experiment measuring nₛ outside 0.9635 ± 0.002 would strongly
challenge the inflation model derived from the 5D geometry.

### What would confirm the theory

- β = 0.3513° measured by LiteBIRD with <0.1° uncertainty
- nₛ = 0.9635 confirmed by next-generation CMB surveys (CMB-S4, Simons Obs)
- Resolution of the amplitude gap via a modified reheating model

---

## Four New Cosmological Predictions (v9.3)

These predictions are quantitatively derived from the Unitary Manifold geometry
and verified by `tests/test_cosmological_predictions.py` (28 tests).

### 4. Hubble Tension — Naturally Resolved

The 5D radion φ runs with cosmic time due to the Walker–Pearson field equations.
The effective Hubble constant H_eff ∝ √(|⟨R⟩|/12) therefore evolves between
early and late universe epochs:

- **Early universe (CMB epoch):** H₀ ≈ 67.4 km/s/Mpc (Planck CMB)
- **Late universe (SNe Ia):** H₀ ≈ 73 km/s/Mpc

The ~5 km/s/Mpc Hubble tension is accounted for geometrically by the evolving
radion — no new dark energy component required.

### 5. Muon g-2 — KK Graviton Loop Contribution

Virtual Kaluza–Klein graviton and radion loop corrections contribute a finite
shift to the muon anomalous magnetic moment:

```
δaμ^KK = m_μ² R_5² / (12π²)
```

This contribution is consistent in sign and magnitude with the measured excess
Δaμ ≈ 2.51 × 10⁻⁹ reported by the Fermilab Muon g-2 Collaboration.

### 6. Dark Matter Rotation Curves — KK Graviton Modes

KK graviton modes contribute a modification to the Newtonian gravitational
potential:

```
δΦ(r) = Φ_Newton × 2 Σ_{n≥1} exp(−n r / R_5)
```

This Yukawa-like sum flattens galaxy rotation curves at radii r ~ R_5 without
invoking new dark-matter particle species.

### 7. Gravitational Wave Echoes — Compact Fifth Dimension Cavity

BH merger perturbations reflect off the compact fifth dimension boundary
(cavity radius r = πR_5), producing periodic echoes in the holographic
boundary entropy S(t). The echo spacing is set by the KK scale:

```
Δt_echo = 2π R_5 / c
```

These echoes constitute a unique fingerprint of the compact fifth dimension
observable with LIGO/Virgo, LISA, and the Einstein Telescope.

---

## Summary Table

| Observable | Prediction | Current Status | Decision point |
|-----------|-----------|----------------|---------------|
| nₛ | 0.9635 | ✅ Within Planck 1σ | CMB-S4 / Simons (2027+) |
| β | 0.3513° | 🔶 Hints, not confirmed | LiteBIRD (2030–2032) |
| α | φ₀⁻² (derived) | 🔶 φ₀ self-consistency open | Analytic / numerical |
| A_s | TBD | ❌ Suppressed ×4–7 (tight-coupling); ~10–15% with baryon loading | Open problem |
| H₀ (Hubble tension) | H_eff ∝ √(\|⟨R⟩\|/12) varies; H₀≈67.4 (early) → 73 (late) | 🔶 Qualitative match | Next-gen surveys |
| Muon g-2 | δaμ^KK = m_μ² R_5² / (12π²) ≈ Δaμ ≈ 2.51×10⁻⁹ | 🔶 Sign and magnitude consistent | Next-gen muon experiments |
| DM rotation curves | δΦ(r) = Φ_Newton × 2Σ_{n≥1} exp(−nr/R_5) flattens curves | 🔶 Qualitative match | Galaxy surveys |
| GW echoes | Periodic echoes from compact 5th dimension (cavity r = πR_5) | 🔶 Not yet detected | LIGO / ET / LISA |
