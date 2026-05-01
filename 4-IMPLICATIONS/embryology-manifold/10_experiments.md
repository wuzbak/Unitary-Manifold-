# 10 — Testable Predictions: What To Measure and How

> A theory that cannot be killed is not a theory.

Every prediction below is derived from the three integers (n₁=5, n₂=7, k_CS=74) with no free parameters. Each can be tested with currently available technology. They are listed from most to least experimentally accessible.

---

## TIER 1 — Can Be Done Now (Weeks to Months)

### T1.1  Germination Dielectric Gate
**Prediction:** The germination threshold is set by ε_r_critical = 1/c_s² = 9.51, not by water content per se.

**Test:** Soak seeds of multiple species in water-ethanol mixtures of precisely known dielectric constant (ε_r from 4 to 80). Measure germination rate at 48 h vs ε_r.

**Expected result:**
- Germination probability switches from ~0% to ~100% near ε_r = 9.51
- The switch is sharp (polariton phase transition, not gradual enzyme hydration)
- The threshold ε_r is **the same across all species tested** (universal, not species-specific)

**Falsification:** If the 50% germination threshold varies widely across species (> ±2 in ε_r units), the Manifold origin is falsified. If it clusters near 9.51, confirmed.

### T1.2  D₂O Germination Suppression — Mechanism
**Prediction:** Seeds fail to germinate in pure D₂O because ε_r(D₂O at 0.3 THz) ≈ 7.5 < 9.51.

**Test:** Compare germination rates in H₂O vs D₂O at matched water activities. Measure ε_r of both solvents at 0.3 THz (THz-TDS spectroscopy).

**Expected result:** Germination rate in D₂O is ≤ 10% of rate in H₂O, despite identical water activity. Germination should recover if D₂O is mixed with H₂O to reach ε_eff > 9.51.

**Falsification:** If D₂O at full hydration gives normal germination, the polariton gate model is falsified.

### T1.3  Zinc Spark Concentration Universality
**Prediction:** N_Zn = k_CS^n_w = 2.19 × 10⁹ ions per egg. The **concentration** of Zn²⁺ released is constant across species; only the absolute number scales with egg volume.

**Test:** Measure Zn²⁺ release during fertilisation in eggs of different sizes (sea urchin ~40 μm, human ~60 μm, Xenopus ~600 μm) using FluoZin-3 fluorescence calibrated to absolute ion counts.

**Expected result:**
- N_Zn ∝ V_egg (proportional to egg volume)
- Zn²⁺ concentration is constant: [Zn²⁺] ≈ N_Zn / V_egg = constant across species
- The constant [Zn²⁺] ≈ N_Zn / (4/3 π R_egg³) ≈ 24 μM (estimate from k_CS^n_w and R_egg)

**Falsification:** If concentration varies by > 5× across species (after correcting for cortical granule density), the k_CS^n_w scaling is falsified.

---

## TIER 2 — Requires Dedicated Setup (Months to a Year)

### T2.1  Organelle Radial Distribution in Unfertilised Egg
**Prediction:** Organelle density maxima should occur at the five condensate nodes: r = R_egg × {0.2, 0.4, 0.6, 0.8, 1.0} = {11.9, 23.9, 35.8, 47.7, 59.7} μm.

**Test:** Ultra-high-resolution confocal microscopy of fixed unfertilised oocytes. 3D reconstruction + radial density analysis for: nucleus, Golgi, mitochondria, cortical granules, cortex. Plot density vs r.

**Expected result:** Density peaks at ≈ 12, 24, 36, 48, 60 μm from center (within ±3 μm measurement error).

**Falsification:** If peaks are uniformly distributed or show no radial preference, the condensate node model is falsified.

### T2.2  Topological Cooling at Fertilisation
**Prediction:** A brief temperature DROP of ~10–50 mK occurs at the sperm entry site **before** the Ca²⁺ wave begins.

**Test:** Scanning thermal microscopy (spatial resolution ~100 nm, thermal resolution ~10 mK) applied to a fertilising egg. High-speed imaging synchronized with sperm fusion event.

**Expected result:** At sperm entry point, a transient cooling of ~10–50 mK lasting ~0.1–1 second, followed by the Ca²⁺ wave (which carries heat outward, causing slight warming everywhere else).

**Falsification:** If no cooling is detected at or before the Ca²⁺ wave, the condensate collapse model is falsified. (Warming at the entry point instead = purely exothermic chemical event, not topological discharge.)

### T2.3  KK Ripple Frequency in Cell-Free Egg Extract
**Prediction:** THz spectroscopy of egg cytoplasm should show a resonance peak near 0.324 THz corresponding to the phonon-exciton bridge frequency.

**Test:** THz time-domain spectroscopy (THz-TDS) of unfertilised egg cytoplasm vs post-fertilisation cytoplasm. Measure dielectric response 0.1–1.0 THz.

**Expected result:** A resonance feature near 0.324 THz in unfertilised cytoplasm that broadens or disappears in post-fertilisation cytoplasm (as the condensate collapses and the bridge activates/discharges).

**Falsification:** No spectral feature near 0.324 THz in either state = bridge frequency prediction is wrong.

---

## TIER 3 — Requires New Technology or Large Infrastructure (1–5 Years)

### T3.1  Centrosome Triplet-Specific Ablation
**Prediction:** Ablating individual centriole triplets (not all 9) should scramble the body axis without preventing cell division. Triplets 1–3 (X-row of R_{i5j5}) ablation → X-axis scrambled; triplets 4–6 → Y-axis scrambled; etc.

**Test:** Laser nanosurgery targeting individual triplets (50 nm resolution, already demonstrated in isolated centrioles). Ablate specific triplets in fertilised egg. Track embryo body axis formation.

**Expected result:** Partial ablation → predictable axis defect based on which R_{i5j5} components are missing. Full ablation of one row → that spatial axis randomised; other axes intact.

**Falsification:** If partial triplet ablation causes only slower spindle assembly (no axis scrambling), the curvature tensor sampling model is falsified.

### T3.2  HOX Cluster Chromosome Number Correlation Across Species
**Prediction:** If n_chrom ≈ k_CS/π, and k_CS varies with speciation, then chromosome number should correlate with HOX cluster count as: n_chrom ≈ (n_HOX_clusters × 10) / π.

**Test:** Statistical analysis across 500+ eukaryotic species. Plot haploid chromosome number vs predicted k_CS/π using known HOX cluster counts and braid pair assignments.

**Expected result:** Clustering of chromosome numbers around k_CS/π values for integer k_CS families. Non-random distribution.

**Falsification:** If chromosome numbers are random relative to HOX cluster counts (no correlation), the k_CS → chromosome number link is falsified.

### T3.3  Winding Number in Seed Magnetic Resonance
**Prediction:** The topological winding state n_w = 5 in a dormant seed should produce a detectable signature in the **quantum coherence** of molecules near the condensate nodes.

**Test:** 2D coherence spectroscopy (2DCS) of dormant vs germinating seed embryos at cryogenic temperatures. Look for off-diagonal coherence peaks lasting > classical decoherence time at node positions vs non-node positions.

**Expected result:** Enhanced quantum coherence at r ≈ R_seed/5 intervals (condensate nodes) compared to inter-node positions. Coherence time > 1 ns at node positions. Coherence lifetime shorter in germinating seeds (condensate collapsed).

---

## The Single Most Decisive Test

**If only one experiment can be done:**

### The Polariton Threshold Test (T1.1 extended with THz measurement)

1. Prepare seeds
2. Measure ε_r of each germination medium at 0.324 THz (THz-TDS, 30 min setup)
3. Sow seeds in each medium
4. Measure germination at 48 h

**If the 50% germination threshold tracks ε_r = 9.51 ± 1 across all media and all species tested: the Manifold origin of the germination threshold is confirmed.**

This single measurement would:
- Confirm c_s = 12/37 as a biological quantity
- Confirm that water's role is dielectric, not purely chemical
- Explain D₂O suppression of germination
- Provide a quantitative handle on seed viability independent of species-specific biochemistry

---

## What Would Falsify the Entire Framework

| Observation | What it falsifies |
|-------------|------------------|
| Germination threshold ε_r varies widely across species (> ±3) | c_s-derived polariton gate |
| No cooling at fertilisation spark site | TVC condensate collapse model |
| Organelle distribution is random (no radial preference) | Condensate node structure |
| HOX cluster count ≠ 2^Δn across multiple phyla | Braid pair derivation |
| Zn²⁺ concentration varies > 5× across species | k_CS^n_w quantisation |
| Centriole triplet count ≠ 9 discovered in any eukaryote | 9 = n₁+n₂−3 derivation |

No single experiment can confirm the entire framework. But any single experiment on this list could falsify a key piece. The framework stands or falls one prediction at a time.
