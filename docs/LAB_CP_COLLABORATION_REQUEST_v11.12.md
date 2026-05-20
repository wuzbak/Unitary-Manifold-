# LAB_CP_COLLABORATION_REQUEST_v11.12.md
# Unitary Manifold — Lab-Scale CP Falsifier Collaboration Request
# Generated from: `src/core/pillar307_lab_cp_falsifier_preregistration.draft_collaboration_request()`
# Version: v11.12 | Pillar: P307 | Status: PREREGISTERED_v11.12
# Operationalised in: v11.13 Tightening Sprint

---

## Collaboration Request — Lab-Scale CP Falsifier Campaign
### Preregistration: PREREGISTERED_v11.12
### Date: 2026-05-20 | Reference: P307 / OBSERVATION_TRACKER P8

Dear [EXPERIMENTAL CONTACT NAME] ([EXPERIMENTAL INSTITUTION]),

We are writing to invite your group to participate in a near-term experimental
campaign to test a specific, quantitative prediction of the Unitary Manifold (UM)
theoretical framework.

### The Prediction (Preregistered P8)

The UM (5,7) braid geometry predicts a laboratory-measurable CP asymmetry:

```
A_CP^lab = (Γ+ − Γ−) / (Γ+ + Γ−) ~ O(2×10⁻⁵)
```

in condensed-matter platforms with (5,7)-equivalent topological winding geometry
(Josephson-junction/SQUID arrays or topological-insulator winding devices).

**This prediction is FALSIFIABLE NOW — no satellite or accelerator is required.**

### Required Measurement Precision

```
σ(A_CP) ≤ 1×10⁻⁵
```

at ≥ 3σ significance, in a topology-certified device.

### Decision-Grade Checklist (F-LAB-CP-1 through F-LAB-CP-5)

Before a verdict (CONSISTENT or P8_TENSION) can be issued, all five items
must be CONFIRMED:

| Item | Description | Requirement |
|------|-------------|-------------|
| F-LAB-CP-1 | Topology certification | Device operates with (5,7)-equivalent topological winding. Control: different winding ratio gives null A_CP. |
| F-LAB-CP-2 | Blinded analysis protocol | Analysis code finalised and registered BEFORE data collection. Unblinding only after full dataset is recorded. |
| F-LAB-CP-3 | σ(A_CP) ≤ 1×10⁻⁵ | Measurement 1σ uncertainty must be at or below the target signal amplitude. |
| F-LAB-CP-4 | Control conditions passed | (a) Topology swap (different winding ratio): A_CP ≈ 0. (b) Time-reversal break (sign reversal): A_CP flips sign. Both controls required. |
| F-LAB-CP-5 | Independent replication | At least one independent laboratory replication at decision-grade σ. |

### Experimental Platforms

**Track A — Josephson-junction / SQUID arrays**

JJ arrays can be engineered with (5,7)-winding-equivalent topological boundary
conditions. The CP asymmetry enters via the braid phase difference in the
tunnelling Hamiltonian. Modern dilution-refrigerator JJ platforms achieve
σ(A_CP) ~ 10⁻⁵–10⁻⁶ with lock-in detection and repeated switching.

**Track B — Topological-insulator (TI) winding devices**

TI surface states with (5,7)-winding number support topological CP breaking via
the axion coupling. A_CP is measurable as a Hall asymmetry at low temperature.
TI Hall measurements at mK temperatures achieve σ(A_CP) ~ few × 10⁻⁵;
improvements toward 10⁻⁵ are feasible with extended averaging.

### Routing Protocol

Results are routed deterministically via
`pillar307_lab_cp_falsifier_preregistration.route_lab_cp_result()`.

| Verdict | Condition |
|---------|-----------|
| CONSISTENT | \|A_CP\| ≥ 1×10⁻⁵ at ≥3σ, topology certified → Update P8 to CONSISTENT |
| P8_TENSION | \|A_CP\| < 1×10⁻⁶ at ≥3σ, topology certified → P8 TENSION (full framework falsification also requires LiteBIRD) |
| BELOW_SENSITIVITY | \|A_CP\| between 1×10⁻⁶ and 1×10⁻⁵ → improve precision |
| INCONCLUSIVE | Topology NOT certified → re-certify before reporting |

A null result at topology-certified σ ≤ 10⁻⁶ would create a P8-TENSION signal;
**full framework falsification requires BOTH lab tension AND LiteBIRD β ∉ [0.22°, 0.38°].**

### Technical Appendix — Geometry Derivation

The A_CP^lab prediction derives from the (5,7) braid geometry:

| Quantity | Value | Formula |
|----------|-------|---------|
| Braid pair | (n₁, n₂) = (5, 7) | Proved from 5D geometry, Pillar 70-D |
| K_CS | 74 | = n₁² + n₂² = 5² + 7², algebraic identity |
| Braid angle θ | 35.54° | atan(n₁/n₂) |
| Asymmetry δ | 18.93° | \|atan(n₁/n₂) − atan(n₂/n₁)\| |
| J_geo (Layer 1) | ≈ 0.024 | ¼ sin²(δ) sin²(2θ) |
| η_T (raw) | ≈ 5/74 ≈ 0.0676 | n₁/K_CS |
| A_CP (before dilution) | ≈ 1.6×10⁻³ | J_geo × η_T |
| Orientation dilution | ÷100 | Lab-frame averaging |
| **A_CP^lab** | **≈ 2×10⁻⁵** | **Target measurement** |

### Preregistration Reference

```
Framework:     Unitary Manifold v11.12
Preregistered: 2026-05-20
Status:        PREREGISTERED_v11.12
DOI:           https://doi.org/10.5281/zenodo.19584531
Repository:    https://github.com/wuzbak/Unitary-Manifold-
Pillar:        P307 (src/core/pillar307_lab_cp_falsifier_preregistration.py)
```

We welcome discussion of platform design, topology certification protocol,
and blinding strategy. Please contact us via the GitHub repository:
https://github.com/wuzbak/Unitary-Manifold-/issues

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
