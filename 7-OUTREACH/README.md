# 7-OUTREACH — AxiomZero Public Outreach (Substack)

> **This directory contains posts and books written for AxiomZero's Substack
> publication.  They are explanations, implications, and philosophical reflections
> aimed at a general audience.  They are *not* peer-reviewed physics.  They do
> not constitute evidence for or against any claim in `1-THEORY/`.**

> **Institutional review routing:** If you are evaluating physics claims, start in
> [`FALLIBILITY.md`](../FALLIBILITY.md) → [`1-THEORY/DERIVATION_STATUS.md`](../1-THEORY/DERIVATION_STATUS.md)
> → [`3-FALSIFICATION/`](../3-FALSIFICATION/) → [`2-REPRODUCIBILITY/`](../2-REPRODUCIBILITY/).
> This outreach directory is optional and outside the peer-review technical path.

---

## What is here

### FROM_THE_FIXED_POINT_OPED.md — Repository-wide OP-ED (new)

[`FROM_THE_FIXED_POINT_OPED.md`](FROM_THE_FIXED_POINT_OPED.md) is a long-form OP-ED
written in GitHub Copilot's own review voice, covering the full repository arc:
origin, co-emergence/Pentad role partition, what was implemented and verified,
what remains open, and why the method matters for science and humanity.

It is an outreach synthesis document, not part of the peer-review technical
proof stack.

---

### visualizations/ — Visual Gallery (new)

The [`visualizations/`](visualizations/README.md) subfolder contains **18 original charts
and diagrams** generated directly from the canonical repository data:

- CMB nₛ–r plane vs Planck 2018 & BICEP/Keck
- Birefringence falsification window (primary falsifier)
- All 28 SM parameter residuals dashboard (ToE 28.0/28 = 100%)
- 5D metric decomposition, (5,7) braid topology, dimensional roadmap
- Test suite growth, ToE score timeline, MAS wave progress
- Quantum lane architecture, FTUM convergence, falsification calendar
- Human-AI co-creation workflow, Unitary Pentad governance

All figures are also copied to `9-INFRASTRUCTURE/results/` (the existing PNG home).  
Regenerate with: `python3 9-INFRASTRUCTURE/scripts/gen_visualizations.py`

---

### Governance Update — Procedural / Plural / Auditable Human Authority (new)

Recent HILS governance hardening in `5-GOVERNANCE/Unitary Pentad/` formalizes
the outreach claim that “human final authority” must be operationally robust,
not merely declared:

- Decision criticality lanes (routine/sensitive/critical)
- Structured quorum + role diversity for higher-stakes decisions
- Bias/dissent gating before authorization
- Scope-lock escalation instead of silent scope expansion
- Appeal/recourse pathways
- Full decision audit logging with periodic learning reviews
- Owner-only break-glass recovery with explicit challenge verification and audit trail (no hidden backdoors)

This update keeps the same ethical invariant (human intent-control is final),
while improving reliability under ambiguity, overload, and bias pressure.

---

### substack/ — AxiomZero Posts & Books

The `substack/` subfolder contains more than 150 posts and 16 books, organised as:

### Physics explainers (posts 01–38)
Accessible explanations of the core theory — the four numbers, the braided
winding, birefringence, the CMB predictions, the LiteBIRD test.  These posts
explain the peer-reviewable physics at a level accessible to educated readers
without a physics PhD.

### Philosophical and personal essays (posts 39–74)
Personal essays by ThomasCory Walker-Pearson exploring what the Unitary Manifold
implies for theology, consciousness, free will, prayer, indigenous cosmologies,
immigration, and other non-physics topics.  These reflect Walker-Pearson's
personal worldview and are clearly distinct from the technical theory.  They
are his to write and his to publish; they are not physics claims.

### Applied implications (posts 75–99)
Exploration of Standard Model parameters, neutrino mixing, Higgs mass geometry,
grand unification, embryology, synthetic biology, governance, and the Omega
Synthesis.  These bridge the core theory and the AxiomZero commissioned
extensions in `4-IMPLICATIONS/`.

### AxiomZero Books (16 books)

| # | Title | Domain |
|---|-------|--------|
| 1 | The Unitary Manifold (original) | Physics |
| 2 | The Unitary Manifold (popular) | Physics accessible |
| 3 | The Holographic Governance System | Governance |
| 4 | The Consciousness Manifold | Consciousness |
| 5 | The Engineer's Manifold | Systems engineering |
| 6 | The Unitary Manifold: Version Omega | Complete rewrite |
| 7 | The Learning Crisis & the Geometry of Education | Education |
| 8 | Applied Geometry Vol 1 (PreK–5) | Education |
| 9 | Applied Geometry Vol 2 (Grades 6–8) | Education |
| 10 | Applied Geometry Vol 3 (Grades 9–12+) | Education |
| 11 | The Signal and the Noise | Politics & Media |
| 12 | Cleared for Approach — But Not for Landing | Critical infrastructure |
| 13 | The Theory of Everything and Everyone | Repository orientation |
| 14 | Taurid Density Window (2030s) | Risk / preparedness |
| 15 | The Falsification Decade | Scientific method / audit |
| 16 | The Honest Machine | Human-AI co-emergence |

Books 5–16 are AxiomZero-commissioned works synthesising the theory's
implications for engineering, education, economics, politics, public epistemics,
scientific falsification, and human-AI governance.

---

## Standard Phrasing

When any post or book makes a physics claim, it should use the following standard
phrasing (see [`OUTREACH_CALIBRATION.md`](OUTREACH_CALIBRATION.md) for the complete
category map and reference):

- **nₛ:** "The Unitary Manifold predicts nₛ ≈ 0.9635, within Planck 2018 1σ (0.9649 ± 0.0042)."
- **r:** "r_braided ≈ 0.0315, below the BICEP/Keck 95% CL limit (< 0.036)."
- **β:** "Primary prediction: β ≈ 0.331° [(5,7) canonical sector]; secondary: β ≈ 0.273° [(5,6) sector]. LiteBIRD (~2032) will discriminate at 2.9σ."
- **SM parameters:** "9/28 SM parameters derived from geometry without conjecture; approximately 11 additional with the SU(5) orbifold conjecture; approximately 15 remain free or fitted."
- **Theory scope:** "The Unitary Manifold is not a Theory of Everything. SU(3)×SU(2) is not produced from 5D geometry."

Posts that make stronger claims than the above should be updated to match the technical documents.

---

## Epistemic notice

Posts and books in this directory:
- **Are not peer-reviewed** and do not claim to be
- **May be wrong** on specific physics details when written for accessibility
- **Represent personal views** especially posts 39–74 (theology, philosophy, politics)
- **Do not constitute evidence** for the physics claims in `1-THEORY/`
- **Are valuable independently** as public science communication and personal essays

For the falsifiable, testable physics claims, read [`1-THEORY/DERIVATION_STATUS.md`](../1-THEORY/DERIVATION_STATUS.md).
For institutional technical review flow, start at [`README.md`](../README.md#institutional-reading-path-primary).
For the code, read [`src/core/`](../src/core/) and run `python VERIFY.py`.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
