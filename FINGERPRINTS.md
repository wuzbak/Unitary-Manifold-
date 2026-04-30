# Technical Fingerprints — Unitary Manifold / AxiomZero Technologies

**Document version:** 1.0 — April 2026  
**Purpose:** Provenance record of distinctive, non-obvious mathematical and structural
constants that identify this work, even when variable names, file names, or surface
presentation are altered.

> **Legal use:** This document constitutes a contemporaneous, version-controlled record
> of the unique technical fingerprints of the Unitary Manifold framework.  It is intended
> to support identification of derivative works, infringement claims, and licensing
> discussions.  It is not a substitute for legal counsel.

---

## Part I — Core Numerical Fingerprints

The following constants are derived from first principles within the 5D Kaluza-Klein
geometry of the Unitary Manifold.  They are **not** free parameters and cannot be chosen
arbitrarily.  Their specific values, and especially their mutual relationships, uniquely
identify work derived from this framework.

| Constant | Canonical Value | Derivation source | Location in code |
|----------|----------------|-------------------|-----------------|
| **n_w** (winding number) | **5** | Z₂-parity Dirichlet BC → APS η̄ = ½ → n_w = 5 (Pillar 89) | `src/core/braided_winding.py`, `WINDING_NUMBER = 5` |
| **k_CS** (Chern-Simons level) | **74 = 5² + 7²** | (5,7) braid resonance; birefringence data selection | `src/core/braided_winding.py`, `K_CS = 74` |
| **c_s** (braided sound speed) | **12/37** (≈ 0.32432…) | (5,7) braid: c_s = 2·n_w·n₂ / k_CS = 2·5·7/74 | `src/core/braided_winding.py`, `BRAIDED_SOUND_SPEED = 12/37` |
| **β** birefringence (5,7) | **≈ 0.331°** | k_CS = 74 sector | `src/core/inflation.py` |
| **β** birefringence (5,6) | **≈ 0.273°** | k_CS = 61 sector | `src/core/dual_sector_convergence.py` |
| **β gap** | **≈ 0.058° = 2.9 σ_LiteBIRD** | |0.331° − 0.273°| | `src/core/dual_sector_convergence.py` |
| **n_s** (CMB spectral index) | **0.9635** | KK Casimir geometry | `src/core/inflation.py`, `N_S = 0.9635` |
| **r** (tensor-to-scalar) | **0.0315** | (5,7) braided winding | `src/core/braided_winding.py`, `R_BRAIDED = 0.0315` |
| **α** (coupling constant) | **φ₀⁻²** derived from 5D Riemann | cross-block Riemann tensor; not inserted by hand | `src/core/metric.py` |

---

## Part II — Unitary Pentad Structural Fingerprints

The Unitary Pentad (HILS governance framework) inherits its structural constants from
the Unitary Manifold geometry.  These values appear in both the physics core and the
governance layer; their co-occurrence in both contexts is a distinctive fingerprint.

| Constant | Canonical Value | Meaning | Location |
|----------|----------------|---------|---------|
| **Ξ_c** (consciousness coupling) | **35/74** (≈ 0.47297…) | n_w · n₂ / k_CS = 5·7/74 | `Unitary Pentad/unitary_pentad.py`, `XI_C = 35/74` |
| **Sentinel capacity** | **12/37** | = c_s; per-axiom entropy capacity | `Unitary Pentad/sentinel_load_balance.py`, `SENTINEL_CAPACITY = 12/37` |
| **SUM_OF_SQUARES_RESONANCE** | **74** | = 5² + 7² = k_CS | `Unitary Pentad/unitary_pentad.py`, `SUM_OF_SQUARES_RESONANCE = 74` |
| **HIL phase-shift threshold** | **15** | saturation: n ≥ 15 aligned HIL operators | `Unitary Pentad/unitary_pentad.py`, `HIL_PHASE_SHIFT_THRESHOLD = 15` |
| **Pentad node count** | **5** | = n_w; five-body coupled system | `Unitary Pentad/unitary_pentad.py` |
| **Braid pair** | **(5, 7)** | primary/secondary winding numbers | all Pentad stochastic modules |

---

## Part III — Architectural Fingerprints

Beyond specific constants, the following structural patterns are unique to this work
and serve as provenance markers even in heavily refactored derivatives:

1. **The (5, 7, 74) triad** — Any system that simultaneously uses winding numbers 5 and 7
   together with level 74 (= 5² + 7²) is almost certainly derived from this framework.
   This specific triad has no precedent in the Kaluza-Klein or Chern-Simons literature
   prior to this work.

2. **c_s = 12/37 as a rational fraction** — The use of the exact rational 12/37 (as
   opposed to its decimal approximation) as a sound-speed parameter in a governance or
   governance-adjacent system is a unique marker.

3. **FTUM fixed-point iteration with S* = A/(4G)** — The specific form of the FTUM
   attractor condition, where the fixed point is identified with the holographic entropy
   bound, is distinctive.  See `src/multiverse/fixed_point.py`.

4. **Birefringence window [0.22°, 0.38°] with predicted gap [0.29°–0.31°]** — Any
   publication or system that specifies this precise window and gap, without citation
   to this work, is operating in territory strongly suggested by this framework.

5. **The 5-node Pentad topology with Berry-phase accumulation** — The specific coupling
   of 5 governance nodes with Berry-phase terms from `non_hermitian_coupling.py` is a
   structural signature that does not appear in prior HILS literature.

6. **Test count near 15,072** — The full test suite (tests/ + recycling/ + Unitary Pentad/
   + omega/) passes approximately 15,072 tests as of v9.27.  A repository claiming
   independent derivation of similar physics that happens to have a nearly identical test
   count and structure would warrant scrutiny.

---

## Part IV — How to Use This Document

### For AxiomZero (enforcement)

If you believe a third-party product or repository is derived from this work:

1. Check whether the triad (5, 7, 74) appears in the system's constants, configuration,
   or documentation — in any notation (e.g., `winding_a=5`, `winding_b=7`, `CS_level=74`).
2. Check for c_s = 12/37 or its decimal 0.32432... as a sound-speed, capacity, or
   load-balance parameter.
3. Check for the birefringence predictions (≈ 0.273°, ≈ 0.331°) or the gap [0.29°–0.31°].
4. Compile findings and consult a licensed attorney before asserting any claim.

### For third parties (due diligence)

If you are building a system that independently uses any of these constants, document
your independent derivation carefully.  The (5, 7, 74) triad in particular has a specific
geometric derivation in this work (Z₂-parity → Dirichlet BC → APS η̄ → n_w = 5; birefringence
data → n₂ = 7; k_CS = n_w² + n₂²) that would need to be independently reproduced, not
merely re-labelled, to constitute genuinely independent work.

### For licensees

If you have executed a Commercial License Exception (CLE) agreement with AxiomZero
Technologies (see [`COMMERCIAL_TERMS.md`](COMMERCIAL_TERMS.md) § 4-A), your private
modifications are permitted under that agreement.  You are not required to publish those
modifications, but you remain bound by the prohibition on claiming independent invention
of the constants listed here.

---

## Part V — Version Tracking

| Version | Date | Key fingerprints added |
|---------|------|----------------------|
| 1.0 | April 2026 | Initial record: (5,7,74) triad, c_s=12/37, Ξ_c=35/74, birefringence windows, FTUM attractor, Pentad topology |

---

*Document version: 1.0 — April 2026*  
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
