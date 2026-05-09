# Post 140 Companion Bibliography — Credit Lineage Ledger

*Companion to:* `7-OUTREACH/substack/posts/post-140-the-credit-lineage-ledger.md`  
*Purpose:* standalone, expanded citation appendix for provenance, influence mapping, and auditability.  
*v10.31, May 2026.*

---

## 1) How to Read This Companion

This bibliography separates references into four relationship types:

- **Direct source dependence**: used directly for claims made in the post.
- **Repository-context dependence**: files that establish project policy, framing, or accountability.
- **Foundational lineage**: prior scientific/mathematical work this project builds on conceptually.
- **Institutional/measurement context**: external programs and datasets that supply falsification pathways.

Where possible, repository references are path-precise.

---

## 2) Direct Source Dependence (Repository Files)

### 2.1 Identity, framing, and metadata

1. `README.md`  
2. `4-IMPLICATIONS/WHAT_THIS_MEANS.md`  
3. `6-MONOGRAPH/MCP_INGEST.md`  
4. `9-INFRASTRUCTURE/llms.txt`  
5. `9-INFRASTRUCTURE/schema.jsonld`  
6. `CITATION.cff`

### 2.2 Epistemic status, scope, and limits

7. `FALLIBILITY.md`  
8. `SEPARATION.md`  
9. `1-THEORY/DERIVATION_STATUS.md`  
10. `3-FALSIFICATION/FALSIFICATION_CONDITIONS.md`  
11. `3-FALSIFICATION/FALSIFICATION_REGISTER.md`  
12. `3-FALSIFICATION/OBSERVATION_TRACKER.md`

### 2.3 Core theory text + implementation anchors

13. `1-THEORY/UNIFICATION_PROOF.md`  
14. `1-THEORY/QUANTUM_THEOREMS.md`  
15. `src/core/metric.py`  
16. `src/core/evolution.py`  
17. `src/holography/boundary.py`  
18. `src/multiverse/fixed_point.py`

### 2.4 Additional high-frequency physics modules cited in outreach

19. `src/core/braided_winding.py`  
20. `src/core/anomaly_closure.py`  
21. `src/core/completeness_theorem.py`  
22. `src/core/nw_anomaly_selection.py`  
23. `src/core/kk_de_wa_cpl.py`  
24. `src/core/neutrino_majorana_dirac.py`  
25. `src/core/chiral_fermion_orbifold.py`  
26. `src/core/fermion_emergence.py`

### 2.5 Cross-domain modules (explicitly non-physics-promotion context)

27. `src/medicine/`  
28. `src/justice/`  
29. `src/governance/`  
30. `src/ecology/`  
31. `src/climate/`  
32. `src/marine/`  
33. `src/psychology/`  
34. `src/genetics/`  
35. `src/materials/`

---

## 3) Repository-Context Dependence (Policy, Governance, Collaboration)

36. `5-GOVERNANCE/Unitary Pentad/README.md`  
37. `5-GOVERNANCE/Unitary Pentad/IMPLICATIONS.md`  
38. `co-emergence/FRAMEWORK.md`  
39. `AGENTS.md`  
40. `CONTRIBUTING.md`  
41. `7-OUTREACH/OUTREACH_CALIBRATION.md`  
42. `7-OUTREACH/substack/README.md`  
43. `7-OUTREACH/substack/posts/post-063-ai-authorship.md`  
44. `7-OUTREACH/substack/posts/post-120-ai-built-this-collaboration.md`  
45. `7-OUTREACH/substack/posts/post-138-what-26000-tests-mean.md`

---

## 4) Reproducibility and Execution-Lineage References

46. `tests/conftest.py`  
47. `tests/test_metric.py`  
48. `tests/test_evolution.py`  
49. `tests/test_boundary.py`  
50. `tests/test_fixed_point.py`  
51. `src/core/five_tier_execution_framework.py`  
52. `docs/WAVE_CHANGELOG.md`  
53. `docs/mas_tracker.yml`

---

## 5) Foundational Scientific Lineage (External)

### 5.1 Geometry, relativity, and extra-dimension foundations

54. Einstein, A. (1915). *Die Feldgleichungen der Gravitation.* Sitzungsberichte der Königlich Preußischen Akademie der Wissenschaften.  
55. Kaluza, T. (1921). *Zum Unitätsproblem der Physik.* Sitzungsberichte der Preussischen Akademie der Wissenschaften.  
56. Klein, O. (1926). *Quantentheorie und fünfdimensionale Relativitätstheorie.* Zeitschrift für Physik.

### 5.2 Quantum and gauge-theory foundations

57. Dirac, P. A. M. (1928). *The Quantum Theory of the Electron.* Proceedings of the Royal Society A.  
58. Feynman, R. P. (1948). *Space-Time Approach to Non-Relativistic Quantum Mechanics.* Reviews of Modern Physics.  
59. Yang, C. N., & Mills, R. L. (1954). *Conservation of Isotopic Spin and Isotopic Gauge Invariance.* Physical Review.  
60. Glashow, S. L. (1961). *Partial-symmetries of weak interactions.* Nuclear Physics.  
61. Weinberg, S. (1967). *A Model of Leptons.* Physical Review Letters.  
62. Salam, A. (1968). *Weak and Electromagnetic Interactions* (Nobel Symposium contribution).

### 5.3 Extra-dimensional phenomenology context

63. Randall, L., & Sundrum, R. (1999). *A Large Mass Hierarchy from a Small Extra Dimension.* Physical Review Letters, 83, 3370–3373.  
64. Randall, L., & Sundrum, R. (1999). *An Alternative to Compactification.* Physical Review Letters, 83, 4690–4693.

---

## 6) Observational and Falsification Context (External)

65. Planck Collaboration (2018). Cosmological parameter-release papers (A&A Planck 2018 results series).  
66. BICEP/Keck Collaboration (latest combined constraints on tensor-to-scalar ratio r).  
67. DESI Collaboration (Year 1 and successor cosmological analyses relevant to w₀/wₐ tension routing).  
68. LiteBIRD mission and science requirement documents (birefringence falsifier context).

---

## 7) Infrastructure and Archival Context (External)

69. Zenodo archive entry for the Unitary Manifold repository: https://doi.org/10.5281/zenodo.19584531  
70. GitHub repository record: https://github.com/wuzbak/Unitary-Manifold-

---

## 8) Integrity Notes for This Bibliography

- This bibliography is intentionally redundant with the in-post appendix for auditability.
- It separates direct repository dependence from broad scientific lineage to avoid overstating novelty.
- It should be updated when major framework versions change (`docs/WAVE_CHANGELOG.md`, `docs/mas_tracker.yml`).

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
