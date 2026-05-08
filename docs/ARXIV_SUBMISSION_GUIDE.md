# arXiv Submission Readiness Guide — Unitary Manifold

*Theory and scientific direction: ThomasCory Walker-Pearson.*  
*Document engineering: GitHub Copilot (AI).*

---

## 1 · Current Submission Readiness (v10.18)

| Item | Status |
|------|--------|
| Theory manuscript | `arxiv/main.tex` exists |
| Abstract | Needs v10.18 ToE score update |
| References | `arxiv/references.bib` |
| ToE score | 15.8/28 = 56% (v10.18) |
| Primary falsifier | LiteBIRD birefringence β ∈ {0.273°, 0.331°} |
| Test suite | 25,500+ tests passing |

## 2 · Pre-Submission Checklist

### 2.1 Manuscript Updates Required
- [ ] Update abstract to reflect v10.18 ToE score (56%)
- [ ] Add v10.18 upgrades: P13 (α), P6 (Higgs VEV) → GEOMETRIC_PREDICTION
- [ ] Add Sections on WS-V, WS-VI, WS-VII roadmap
- [ ] Update Table 1 (parameter table) with v10.18 values
- [ ] Add subsection on CMB-S4, DUNE, Hyper-K falsification timeline
- [ ] Verify all cross-references to source modules are current

### 2.2 FALLIBILITY.md Review
- [ ] Confirm all open problems are documented
- [ ] Confirm P17 (Δm²₃₁) honest 2NLO residual is stated
- [ ] Add DESI wₐ tension as HONEST_OPEN_PROBLEM

### 2.3 arXiv Metadata
- Primary category: `hep-th` (High Energy Physics — Theory)
- Cross-list: `gr-qc`, `astro-ph.CO`
- Title: "The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility"
- Version: v10.18

### 2.4 Figure Checklist
- [ ] Figure 1: 5D metric ansatz and KK tower
- [ ] Figure 2: CMB birefringence prediction with LiteBIRD sensitivity overlay
- [ ] Figure 3: ToE score summary bar chart (56% filled)
- [ ] Figure 4: Falsification timeline (DUNE 2028, Hyper-K/JUNO 2027, CMB-S4 2030, LiteBIRD 2032)

## 3 · Recommended Submission Strategy

### Option A: Two-paper strategy (recommended)
1. **Paper 1** (near-term): Core 5D geometry + algebraic/GEOMETRIC_PREDICTION parameters only  
   - P1, P2 (CMB), P4 (sin²θ_W), P6 (Higgs VEV), P11 (N_gen), P12 (m_p/m_e), P13 (α), P23/P24 (birefringence)
   - ToE subset score: 8 × 0.8 + 1 × 1.0 = 7.4/9 = 82%
   - Clean falsifier: LiteBIRD β measurement (~2034)

2. **Paper 2** (6-12 months later): Full SM parameter coverage, CONSTRAINED and above
   - All 28 parameters, WS-V through WS-VII roadmap
   - Full 56% ToE score

### Option B: Single comprehensive paper
- Submit `arxiv/main.tex` as-is with v10.18 updates
- Risk: reviewers may focus on CONSTRAINED parameters (15-30% residuals)
- Mitigation: FALLIBILITY.md makes all limitations explicit

## 4 · Zenodo Release

When submitting to arXiv, also release on Zenodo:
1. Tag the GitHub repository: `git tag v10.18`
2. Create Zenodo release linked to GitHub
3. Update `CITATION.cff` with new DOI
4. Update `9-INFRASTRUCTURE/schema.jsonld` with new version

Preferred citation format (after release):
```
Walker-Pearson, T. (2026). The Unitary Manifold: A 5D Gauge Geometry of
Emergent Irreversibility (v10.18). Zenodo.
https://doi.org/10.5281/zenodo.19584531
```

## 5 · Community Engagement Prior to Submission

- [ ] Post to `discussions/AI-Automated-Review-Invitation.md` with call for pre-review
- [ ] Share with CMB community (birefringence prediction — most immediate falsifier)
- [ ] Share with neutrino community (δ_CP, Δm²₃₁ predictions)
- [ ] Share with LiteBIRD collaboration contact

---

*Document version: 1.0 — 2026-05-08 (v10.18)*
