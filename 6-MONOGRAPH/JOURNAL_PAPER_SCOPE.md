# JOURNAL_PAPER_SCOPE.md — Physics Paper Pre-Submission Definition

**Version:** v9.29 (101 pillars + sub-pillars CLOSED, 2026-05-02)  
**Status:** Pre-submission planning document  
**Theory:** ThomasCory Walker-Pearson  
**Documentation:** GitHub Copilot (AI)

---

## 1 · Submission Target

| Preference | Journal | Why |
|------------|---------|-----|
| First choice | *Physical Review D* (PRD) | Standard venue for KK/inflation phenomenology; broad readership in theoretical and observational cosmology |
| Second choice | *JCAP* (Journal of Cosmology and Astroparticle Physics) | Actively publishes CMB prediction papers; receptive to birefringence predictions |

**Submission section:** Theory and Models of Inflation / CMB Phenomenology

---

## 2 · Paper Scope — What Is Included

The journal paper covers **only the physics core**:

1. The 5D KK metric ansatz and its dimensional reduction
2. Derivation of n_w ∈ {5, 7} from Z₂ orbifold + CS anomaly gap (Pillars 39, 67)
3. Derivation of n_w = 5 from metric Z₂-parity and APS index theorem (Pillars 70-C, 70-C-bis)
4. The explicit FTUM → φ₀_bare = 1 → φ₀_eff chain (Pillar 56-B)
5. Inflationary observables: nₛ ≈ 0.9635, r_braided ≈ 0.0315 (Pillars 1–5, 97-B)
6. Birefringence prediction: β ≈ 0.331° [(5,7) canonical sector], β ≈ 0.273° [(5,6) sector] (Pillar 95)
7. The birefringence gap β_gap = 0.058° = 2.9σ_LiteBIRD as the primary discriminating observable
8. Competitor comparison: Starobinsky (R²), hilltop quartic, UM (5D KK)

---

## 3 · Paper Scope — Explicit Exclusions

The following aspects of the Unitary Manifold repository are **explicitly excluded**
from the journal paper scope:

- All phenomenological extensions: medicine, justice, consciousness, ecology, psychology,
  genetics, materials science, education, politics (Pillars 17–26 and extensions)
- The Unitary Pentad governance framework (5-GOVERNANCE/)
- AxiomZero / Substack outreach books (7-OUTREACH/substack/)
- The omega/ and recycling/ modules
- Dark energy w_KK prediction (separate paper)
- Muon g-2 KK graviton contribution (separate paper or note)
- Neutrino mass RS Yukawa mechanism (separate paper)

---

## 4 · Abstract Strategy

**Lead sentence:** A 5D Kaluza-Klein framework compactified on S¹/Z₂ with winding
number n_w = 5 (forced by Z₂ topology and the APS index theorem) predicts three
independent CMB observables — nₛ = 0.9635, r = 0.0315, β ≈ 0.331° — from integer
arithmetic alone.

**Key selling point:** The birefringence prediction β ≈ 0.331° [(5,7) sector] vs.
β ≈ 0.273° [(5,6) sector], with a predicted gap of 0.058° = 2.9 × σ_LiteBIRD,
allows *direct discrimination* from Starobinsky R² inflation (which predicts zero
birefringence) at LiteBIRD precision (~2032).

**Address the nₛ–r degeneracy directly:** While nₛ ≈ 0.964 is shared by Starobinsky
and the UM, the combination (r ≈ 0.032) + (β ≈ 0.331°) is unique to UM.  Starobinsky
predicts r ≈ 0.004 and β = 0°.  The two-dimensional (r, β) observable space
discriminates the models independently of nₛ.

---

## 5 · Known Gaps to Address in Paper

These gaps must be explicitly acknowledged in the paper's "Outstanding gaps" subsection:

| Gap | Current status | Where documented |
|-----|---------------|-----------------|
| φ₀_bare = 1 normalization | Normalization convention (Steps 1–3 derived; Step 4 is ℓ_Pl = 1 choice) | Pillar 56-B; DERIVATION_STATUS.md Part VI |
| ADM time parameterization | Ricci-flow parameter ≠ coordinate time; Pillar 41 partial correction only | FALLIBILITY.md §III; DERIVATION_STATUS.md Part I |
| n_w = 5 uniqueness residual | η-class requirement MOTIVATED but not proved as theorem | NW_UNIQUENESS_STATUS.md; DERIVATION_STATUS.md Part II |
| SU(2) × SU(3) | Not produced by 5D KK; Witten (1981) | DERIVATION_STATUS.md Part V |
| CMB peak amplitude (acoustic) | Shape residual open; requires full Boltzmann integration | FALLIBILITY.md §V |
| ~15/28 SM parameters | Lepton/quark Yukawa hierarchies fitted | DERIVATION_STATUS.md Part V; sm_free_parameters.py |

---

## 6 · Competitor Model Comparison Table

| Model | nₛ | r | β (birefringence) | Discriminating? |
|-------|-----|---|--------------------|----------------|
| Starobinsky R² | 0.965 | 0.004 | 0° (none) | r ≪ UM; β = 0° ≠ UM |
| Hilltop quartic | 0.960–0.967 | 0.001–0.010 | 0° (none) | r ≪ UM; β = 0° ≠ UM |
| **UM (5,7) [PRIMARY]** | **0.9635** | **0.0315** | **0.331°** | Unique (r, β) pair |
| UM (5,6) [SECONDARY] | 0.9635 | 0.0315 | 0.273° | Same nₛ, r; different β |
| Natural inflation | 0.945–0.970 | 0.03–0.10 | 0° (none) | r overlaps; β = 0° |

**Primary discriminator:** The combination (r ≈ 0.032, β ≈ 0.331°) is unique to the
UM (5,7) canonical sector and will be testable by LiteBIRD + CMB-S4 simultaneously.

---

## 7 · Cover Letter Language (AI Involvement Disclosure)

> This paper was developed through a human-AI collaboration under the HILS (Human-
> in-the-Loop Systems) framework documented in the companion repository.  The scientific
> direction, theoretical framework, and physical interpretation are the work of
> T. C. Walker-Pearson (human author).  The code architecture, numerical verification,
> test suites, and document synthesis were performed by GitHub Copilot (AI).
> The AI-generated code and tests are available at [repository URL] and constitute
> a complete verification of all numerical claims in this paper.  The authors
> declare that no AI-generated text appears in the manuscript proper.

*Note on peer review: Per the review recommendation, the use of AI in code
development and testing should be disclosed in the cover letter even if journals
do not yet have explicit policies.*

---

## 8 · Pre-Submission Checklist

Before journal submission, all of the following must be completed:

- [ ] All items in TRACK A (A1–A7) implemented and tested
- [ ] `DERIVATION_STATUS.md` reviewed by the author for any status changes
- [ ] `FALLIBILITY.md` up to date
- [ ] Human expert preprint review in mathematical physics / inflationary cosmology
- [ ] LaTeX manuscript (`6-MONOGRAPH/arxiv/main.tex`) updated with:
  - φ₀_bare = 1 bridge derivation (Pillar 56-B)
  - Z₂ parity clarification for B_μ
  - Honest SM parameter count (9/28)
  - Competitor model comparison table (above)
  - Outstanding gaps subsection
- [ ] arXiv submission (gr-qc or hep-ph or astro-ph.CO cross-listed)
- [ ] Zenodo DOI updated to reflect submission version

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
