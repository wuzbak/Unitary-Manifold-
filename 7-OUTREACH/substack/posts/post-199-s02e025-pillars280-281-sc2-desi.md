# Pillars 280 + 281: Narrowing the Gravitational Wave Interval and Drilling the DESI Response

*Post 199 of the Unitary Manifold series.*  
*Series S02, Episode E025.*  
*Epistemic category: **A/P** — adjacent research tracks, non-hardgate, interval narrowing + readiness drill.*  
*May 2026.*

---

**Two pillars in this sprint worked on experimental readiness: one narrowed a theoretical interval before the data arrives, and one verified that the same-day response machinery fires correctly for three different DESI DR3 outcomes.** Different problems, same discipline: know your numbers before the experiment reports.

---

## Pillar 280: Narrowing α_GW Without Knowing c_UV

### The interval that needed tightening

The gravitational wave normalization α_GW is the coupling that connects the braided-winding tensor power spectrum to the observed amplitude of CMB scalar modes. It appears in the SC2 lane of the framework and is currently quoted as:

    α_GW ∈ [4.2, 4.8] × 10⁻¹⁰

This interval has a width of 0.6 × 10⁻¹⁰. The 10D bridge benchmark pins the point estimate at 4.49 × 10⁻¹⁰ (Pillars 149 and 165), but the interval spread comes from the uncertainty in the 10D bridge coefficient c_UV — the parameter that encodes how the 10D string embedding normalizes the transfer function.

Deriving c_UV from first principles (from the full CY₃ moduli stabilization) is the SC2 architecture cap: it is open, acknowledged, and named. Pillar 280 does not claim to close it. Instead, it asks a more useful question: can the interval be narrowed *without* knowing c_UV exactly?

### Theorem 280.1: the Mukhanov-Sasaki intersection

The key insight is that the Mukhanov-Sasaki vacuum normalization (Pillar 265, `pillar265_mukhanov_sasaki_as_closure.py`) provides an *independent* constraint on α_GW. At sound-horizon crossing with the braided sound speed c_s = 12/37, the scalar power spectrum amplitude is:

    A_s_MS(H, ε) = H² / (8 π² ε c_s M_Pl²)

The full SC2 chain links α_GW to A_s via the transfer function:

    A_s(α_GW) = A_s_MS · T(α_GW)

The c_UV dependence enters only as a multiplicative correction to the transfer function:

    T(α; c_UV) = T₀(α) · (1 + ε_UV · log10(c_UV / c_UV*))

where c_UV* is the 10D benchmark and ε_UV ≤ 0.05 across the physically-allowed 10D string-embedding window (from Pillar 265).

Theorem 280.1 proves that the intersection of the original α_GW interval with the Mukhanov-Sasaki tolerance band:

    [α_MS · (1 − ε_UV), α_MS · (1 + ε_UV)]

is a sub-interval with width:

    Δα_new = min(α_high − α_low, 2 · α_MS · ε_UV)

For α_MS = 4.49 × 10⁻¹⁰ and ε_UV ≤ 0.05, this gives:

    Δα_new ≤ 0.449 × 10⁻¹⁰  →  width reduction ≥ 25.2%

For the tighter bound ε_UV ≤ 0.04:

    Δα_new ≤ 0.359 × 10⁻¹⁰  →  width reduction ≥ 40.1%

The plan §C.7 acceptance gate required width reduction ≥ 30%. This is met for ε_UV ≤ 0.0445.

### What remains open

The narrowing does not derive c_UV. The exact c_UV from the 10D string embedding — needed for the α_GW point estimate, not just the interval — is still the SC2 architecture cap. Pillar 280 eliminates the interval spread induced by c_UV variation up to O(ε_UV), but the c_UV point value itself is still required for the exact A_s prediction.

This is stated explicitly in the module: "This narrowing does not derive c_UV from first principles (that is the SC2 architecture cap that remains open)."

The path from interval to point will require the full CY₃ moduli/flux/α_s calculation from Pillar 37 (the 10D flux landscape). Until then, α_GW is known to lie in a narrowed interval — narrower by at least 25% — rather than the original [4.2, 4.8] × 10⁻¹⁰.

---

## Pillar 281: Running the DESI DR3 Drill Before the Data Arrives

### Why drill at all?

DESI (the Dark Energy Spectroscopic Instrument) is conducting the most precise large-scale structure survey in history. The DR3 data release — currently expected within the next year or so — will include a high-precision measurement of the dark energy equation of state parameter wₐ (the time-derivative of the equation of state w).

The Unitary Manifold's prediction is clear: the KK frozen-radion mechanism gives wₐ = 0. The radion is stabilized; there is no dark energy evolution. DESI DR2 showed hints of wₐ ≠ 0 at modest significance. DR3 will either confirm this tension or reduce it.

The framework already has a publication-day runbook: `src/core/desi_dr3_publication_day_runbook.py`. This module contains the routing table, the verdict thresholds, and the list of canonical documents to update on publication day. Pillar 281 drills that runbook mechanically — running three synthetic DR3 scenarios through it and checking that the machinery works correctly.

### The three scenarios

The drill operates at three σ levels, selected to cover the main routing branches:

- **σ = 3.2**: wₐ ≠ 0 at 3.2σ → routes to **FALSIFIED**. The KK frozen-radion wₐ = 0 prediction is falsified at this significance level. The runbook must fire the FALSIFIED branch, update the relevant canonical documents, and flag the pillar for reassessment.

- **σ = 2.4**: wₐ ≠ 0 at 2.4σ → routes to **HIGH_TENSION**. Below formal falsification but above the tension threshold. The runbook files the tension, flags for monitoring, and schedules a DR4/Y5 review.

- **σ = 1.8**: wₐ ≠ 0 at 1.8σ → routes to **CONSISTENT** or **TENSION** (below the high-tension threshold). The framework's prediction is consistent with data at this level; the runbook confirms no update to the falsification status.

### What the drill checks

Each scenario runs through the full routing machinery and verifies:

1. **Correct verdict bucket**: the routing table must produce FALSIFIED / HIGH_TENSION / CONSISTENT at the correct σ threshold.
2. **Mandatory-file coverage audit**: the runbook must identify all canonical documents requiring an update (the list is machine-readable in `CANONICAL_DOCS_TO_UPDATE`).
3. **Idempotence check**: re-running the drill on a scenario that has already been applied must produce an empty incremental diff. If applying the routing a second time would change anything, the runbook has a consistency bug.

All three checks pass for all three scenarios. The routing machinery is verified. The document update set is correct. The idempotence property holds.

### What this means for publication day

When DESI DR3 actually publishes — wherever the σ value lands — the framework will have a same-day response that does not require improvisation. The routing decision will be mechanical, transparent, and reproducible by anyone who runs the drill against the real DR3 numbers.

This is the kind of pre-registration behavior that distinguishes a serious falsifiable framework from a post-hoc rationalization engine. The routing rules are committed before the result is known. The update procedure is tested before the data arrives. There is no room for motivated re-interpretation.

---

## The common thread: knowing your position before the measurement

Pillars 280 and 281 are different in their mathematical content — one is an interval narrowing theorem, the other is a routing drill — but they share the same epistemic stance: preparing the framework's position before the experimental data lands.

Pillar 280 ensures that the α_GW interval is as narrow as the current mathematics allows, so that when CMB-S4 provides a precise A_s measurement, the framework's pre-experimental prediction is as tight as possible. Pillar 281 ensures that when DESI DR3 reports, the routing to FALSIFIED / HIGH_TENSION / CONSISTENT happens without delay or ambiguity.

Both are forms of intellectual preparation. Both are required for a framework that takes falsification seriously.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*  
*The Unitary Manifold: https://github.com/wuzbak/Unitary-Manifold-*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

---

*Post 199 — Series S02E025 — May 2026*  
*Narrow the interval before the measurement. Drill the routing before the data. Then let the experiments decide.*
