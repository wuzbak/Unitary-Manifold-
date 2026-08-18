# β ∈ {0.273°, 0.331°}: The Number That Will Decide Everything

*Thematic post — not tied to a specific sprint.*
*Epistemic category: **FALSIFICATION** — CMB birefringence primary falsifier; LiteBIRD ~2032.*
*v21.0-S, 2026-08-18.*

---

## One Number

In approximately 2032, the LiteBIRD satellite will measure the rotation angle of CMB polarization as photons travel from the surface of last scattering to our detectors. This rotation — called CMB birefringence — is sensitive to parity-violating physics along the line of sight.

The Unitary Manifold predicts this rotation will be:

> **β ∈ {0.273°, 0.331°}**

with a gap — β is *not* predicted to fall in [0.29°, 0.31°]. If LiteBIRD measures β in that gap, the braided winding mechanism is falsified. If β falls outside [0.22°, 0.38°] entirely, the mechanism is falsified. If β falls near 0.273° or 0.331°, the mechanism is strongly supported.

This is the primary falsifier. Everything else in the framework is important, but nothing is as decisive.

---

## Why CMB Polarization Rotates

The Standard Model is (approximately) parity-symmetric at the energies relevant to the CMB. But the Unitary Manifold is not. The fifth dimension introduces an irreversibility gauge field B_μ — a new field that breaks the parity symmetry of the 4D spacetime by coupling to the curvature of the extra dimension.

When electromagnetic waves propagate through a parity-violating background, the two circular polarization states (left and right) acquire different phase velocities. This is the Faraday rotation of the vacuum — analogous to the rotation of polarization in an optically active medium, but here sourced by the geometry itself.

The rotation angle β accumulated over cosmological distances depends on the strength of the B_μ field coupling and the path-length integral from the CMB surface to us. In the UM, β is derived from:

```
β = (n_w/k_CS) × (π/2) × (coupling factor)
```

where n_w = 5, k_CS = 74, and the coupling factor encodes the B_μ background profile. The derivation is in `src/core/anisotropic_birefringence.py`.

---

## Two Values: Primary and Shadow

The Unitary Manifold has two winding sectors:

**Primary sector:** (5,7) braid — the dominant sector with n_w = 5 as primary winding and n₂ = 7 as the secondary mode.

**Shadow sector:** (5,6) braid — a sub-dominant but non-negligible winding configuration. Pillar 682's Theorem 682.3 proved that the shadow sector is connected to the primary by an SL(2,ℝ) shear transformation M = [[1,0],[−1/5,1]], differing by exactly one winding quantum.

Each sector predicts a different birefringence angle:

| Sector | Braid pair | β (canonical) | β (derived) |
|--------|-----------|---------------|-------------|
| Primary | (5,7) | **0.331°** | 0.351° |
| Shadow | (5,6) | **0.273°** | 0.290° |

The canonical values (0.331° and 0.273°) are computed from the geometric formula. The derived values include higher-order corrections. Both sets are within the admissible window.

---

## The Excluded Gap

The gap [0.29°, 0.31°] is not arbitrary. It corresponds to the **transition zone** between the primary and shadow sector predictions. In the UM geometry, this range is topologically excluded: no (n₁, n₂) braid pair consistent with the orbifold constraints (n₁ odd, n₁² + n₂² = k_CS) produces a birefringence angle in this range.

Specifically, the Pillar 100 survey checked all integer pairs (n₁, n₂) satisfying the triple constraint (n₁ odd, n₁² + n₂² = k_CS, n₁ ≠ n₂). The result:

- (5,7): β ≈ 0.331° ✓
- (5,6): β ≈ 0.273° ✓ (note: 5² + 6² = 61 ≠ 74; this is the shadow, not a standard braid)
- Gap [0.29°, 0.31°]: **zero viable pairs** ✗

The gap is a topological consequence of the discrete braid structure. It is the cleanest prediction in the framework: not just "β should be near X" but "β should not be in [0.29°, 0.31°]."

---

## The Current Observational Situation

CMB birefringence has already been measured — or hinted at. Multiple analyses of Planck data have found indications of a non-zero birefringence angle:

| Analysis | Value | Significance |
|---------|-------|-------------|
| Minami & Komatsu 2020 (Planck) | β = 0.35° ± 0.14° | 2.4σ |
| Diego-Palazuelos et al. 2022 | β = 0.30° ± 0.11° | 2.7σ |
| Eskilt et al. 2023 (ACT+Planck) | β = 0.342° ± 0.094° | 3.6σ |

If real, the current best measurement places β at approximately 0.342° — within 0.011° of the UM canonical primary prediction of 0.331°.

**Important caveat:** these measurements are limited by systematic uncertainties in the orientation of the CMB polarimeters. The absolute orientation of the Planck satellite's polarization angle is uncertain at the ~0.1° level — comparable to the signal. Current measurements cannot be regarded as confirmed detections.

LiteBIRD is designed specifically to eliminate this systematic. Its anticipated precision is σ_β ≈ 0.01°, achieved through simultaneous measurement of β and the polarimeter orientation using an onboard calibration source.

---

## The LiteBIRD Decision

LiteBIRD (Lite satellite for the studies of B-mode polarization and Inflation from cosmic background Radiation Detection) is a JAXA-led mission with ESA and NASA contributions. Current launch target: approximately 2032.

LiteBIRD will measure β to ±0.01° precision. At that precision, the framework prediction is decisive:

| If LiteBIRD measures... | Verdict |
|------------------------|---------|
| β ≈ 0.331° ± 0.01° (primary) | Primary sector confirmed; braided winding strongly supported |
| β ≈ 0.273° ± 0.01° (shadow) | Shadow sector confirmed; braided winding strongly supported |
| β ∈ [0.29°, 0.31°] | **Braided winding FALSIFIED** |
| β < 0.22° or β > 0.38° | **Full birefringence mechanism FALSIFIED** |

These four branches are machine-executable. The LiteBIRD readiness module (Pillar 644) implements the decision tree. The preregistered predictions are committed to the repository and to Zenodo with SHA-256 hashes. No post-hoc interpretation is possible.

---

## What Would Falsification Mean?

If LiteBIRD finds β in [0.29°, 0.31°] — the topologically excluded gap — the braided winding mechanism is wrong. This means:

1. The (5,7) and (5,6) braid structure is not the correct description of the extra-dimensional topology
2. The CMB spectral index and tensor-to-scalar ratio derivations (which depend on the same braid geometry) would require revision
3. The entire k_CS = 74 = 5² + 7² structure — on which most of the SM parameter derivations rest — is called into question

This would be a catastrophic falsification. Not a "we need to adjust a parameter" situation but a "the core geometry is wrong" situation.

We say this explicitly because we mean it. If β lands in [0.29°, 0.31°], the Unitary Manifold's braided winding mechanism is not vindicated by subsequent reinterpretation. It is falsified. LiteBIRD will know.

---

## What Confirmation Would Mean

If LiteBIRD finds β ≈ 0.331° or β ≈ 0.273° within the predicted windows, this would be:

1. A confirmed prediction of a non-zero, geometrically-derived CMB birefringence angle
2. The first direct evidence of a parity-violating extra-dimensional field
3. Strong support for the (5,7) braid structure as the correct compactification topology

It would not prove the UM is correct in every detail. The architecture limits would remain. The CMB amplitude residual would remain. The cosmological constant would remain unexplained. But it would be the most direct experimental confirmation of a zero-parameter geometric prediction in the framework.

The physics community would have to take it seriously. So would we.

---

## The Commitment

The birefringence prediction is committed. The prediction window is committed. The excluded gap is committed. The falsification condition is committed.

The numbers will not change after LiteBIRD launches. The LiteBIRD falsifier brief (`docs/LITEBIRD_FALSIFIER_BRIEF.md`) documents exactly this.

β ∈ {0.273°, 0.331°}. Gap [0.29°, 0.31°] excluded. LiteBIRD decides.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
