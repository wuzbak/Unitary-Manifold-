# The Credit Lineage Ledger: Who This Work Depends On

*Post 140 of the Unitary Manifold series.*  
*Epistemic category: **A** — provenance, credit, and accountability; no new physics claim.*  
*v10.52, May 2026.*

---

**Claim (and falsification condition):** this project is not the work of one mind or one tool; it is a layered synthesis built on prior physics, mathematics, governance research, software/testing practice, open-source infrastructure, and a human-AI division of labor that is explicitly documented. This claim is falsified if substantial influences are omitted, if attributions are materially wrong, or if the cited record fails to support the provenance statements made below.

---

Most scientific writing gives a short references section and moves on. That is often enough for a paper. It is not enough for this repository.

The Unitary Manifold is not just a derivation file or a single manuscript. It is a live, test-heavy, governance-aware, falsification-forward research codebase with explicit public accountability commitments. That means credit has to be broader than "who wrote this line," and more precise than "standing on the shoulders of giants."

This post is a credit ledger: what this work depends on, where those dependencies are visible in-repo, and how responsibility is partitioned.

---

## 1) The Partition of Responsibility (Explicit and Stable)

The repository standard is clear:

- **ThomasCory Walker-Pearson**: theory, framework, scientific direction, judgment.
- **GitHub Copilot (AI)**: code architecture, test suites, document engineering, synthesis.

This is not decorative language. It is how this project is operated, documented, and audited.

---

## 2) Physics Lineage: The Core Scientific Dependencies

At the physics layer, this work depends on major established structures and datasets:

- Kaluza-Klein geometry and compactification traditions
- Gauge-theory and QFT machinery used in 4D effective descriptions
- Cosmological constraints (Planck/BICEP/Keck and future LiteBIRD falsifier framing)
- Standard Model parameterization conventions and PDG baselines

The repository does not claim to have invented those foundations. It claims to build a specific geometric framework on top of them, with explicit open gaps and explicit falsification conditions.

---

## 3) Mathematics and Formal Methods Lineage

The framework also inherits deeply from mathematical traditions:

- differential geometry and fiber-bundle reasoning,
- topological and orbifold constructions,
- fixed-point and operator-theoretic logic,
- formal consistency checks encoded as tests.

Even where the repository contributes new compositions or derivation pathways, those pathways are legible only because of prior mathematical language created by others.

---

## 4) Governance, Justice, Climate, and Social-System Lineage

For the non-physics domain modules and books, the project explicitly uses the Unitary Manifold mathematics as an organizational lens rather than as validated physical mechanism. This distinction matters.

That work depends on:

- prior governance theory and constitutional design literature,
- justice and legal-theory traditions,
- ecology/climate systems science,
- public-policy and institutional design research.

In this repository, those domains are framed with epistemic separation rules, not folded into unsupported physics claims.

---

## 5) Software and Reproducibility Lineage

The repository’s research posture is inseparable from software practice:

- Python scientific stack conventions,
- pytest-style executable verification,
- hard-gate merge discipline,
- public issue/PR review norms,
- transparent changelog and status accounting.

The claim is not "tests prove truth." The claim is narrower and stronger: tests enforce reproducibility, consistency, and honest deltas while waiting for external data.

---

## 6) AI Systems, Toolchain, and Integration Lineage

The collaboration and reproducibility stack now spans more than a single model surface.

- human-led theory stewardship with AI-assisted engineering and documentation,
- documented multi-agent operations via MCP-connected systems and role-boundary files,
- multi-model support paths (OpenAI/Claude/Gemini/Microsoft) with explicit "confirmed vs available" scope rules,
- mixed-language implementation and delivery stack (Python, JavaScript/Node, YAML, LaTeX/BibTeX, JSON/JSON-LD/CFF),
- integration surfaces for Copilot Extension, RAG assistant flows, Custom GPT/Claude setup, and MCP server configuration.

Credit has to track this full operational lineage, not just the final prose output.

---

## 7) Institutional and Infrastructure Lineage

This project also depends on institutions and platforms:

- open publication/discovery infrastructure (Zenodo DOI, GitHub archival trace),
- experimental collaborations that can falsify predictions,
- the broader scientific norm that observational disagreement outranks internal elegance.

Without those institutions, there is no meaningful falsification pathway.

---

## 8) Why This Matters

If the framework succeeds on future tests, credit should be distributed honestly.
If it fails on future tests, accountability should be distributed honestly.

Both require a complete citation map, not a symbolic one.

That is why this post includes an in-post appendix and a standalone companion bibliography.

---

## Citation Appendix (Thorough, In-Post Version)

### A. Core Repository Identity and Scope

1. `README.md` — top-level project identity, equations, quickstart, and framing.  
2. `4-IMPLICATIONS/WHAT_THIS_MEANS.md` — plain-language central claim framing.  
3. `6-MONOGRAPH/MCP_INGEST.md` — compact repository ingestion summary.  
4. `9-INFRASTRUCTURE/llms.txt` — AI-discovery entry index.  
5. `9-INFRASTRUCTURE/schema.jsonld` — structured metadata graph payload.  
6. `CITATION.cff` — formal citation metadata.

### B. Physics Status, Limits, and Epistemic Boundaries

7. `FALLIBILITY.md` — open gaps and admissions log.  
8. `SEPARATION.md` — boundary between physics and governance/HILS claims.  
9. `1-THEORY/DERIVATION_STATUS.md` — derivation-tier and status ledger.  
10. `3-FALSIFICATION/FALSIFICATION_CONDITIONS.md` — explicit falsifier conditions.  
11. `3-FALSIFICATION/FALSIFICATION_REGISTER.md` — tracked falsification register.  
12. `3-FALSIFICATION/OBSERVATION_TRACKER.md` — pass/tension/falsified routing workflow.

### C. Core Physics Texts and Formal Theory Files

13. `1-THEORY/UNIFICATION_PROOF.md` — formal unification argument text.  
14. `1-THEORY/QUANTUM_THEOREMS.md` — theorem catalog and quantum statements.  
15. `src/core/metric.py` — KK metric implementation anchor.  
16. `src/core/evolution.py` — field-evolution implementation anchor.  
17. `src/holography/boundary.py` — boundary and entropy dynamics module.  
18. `src/multiverse/fixed_point.py` — fixed-point iteration mechanics.

### D. Supporting Physics/Phenomenology Modules Frequently Referenced in Outreach

19. `src/core/braided_winding.py`  
20. `src/core/anomaly_closure.py`  
21. `src/core/completeness_theorem.py`  
22. `src/core/nw_anomaly_selection.py`  
23. `src/core/kk_de_wa_cpl.py`  
24. `src/core/neutrino_majorana_dirac.py`  
25. `src/core/chiral_fermion_orbifold.py`  
26. `src/core/fermion_emergence.py`

### E. Cross-Domain Repository Modules (Non-Physics-Promotion Context)

27. `src/medicine/`  
28. `src/justice/`  
29. `src/governance/`  
30. `src/ecology/`  
31. `src/climate/`  
32. `src/marine/`  
33. `src/psychology/`  
34. `src/genetics/`  
35. `src/materials/`

### F. Governance / HILS / Collaboration Architecture

36. `5-GOVERNANCE/Unitary Pentad/README.md`  
37. `5-GOVERNANCE/Unitary Pentad/IMPLICATIONS.md`  
38. `5-GOVERNANCE/co-emergence/FRAMEWORK.md`  
39. `AGENTS.md`  
40. `CONTRIBUTING.md`

### G. AI Systems, Toolchain, and Integration Provenance

41. `9-INFRASTRUCTURE/provenance/README.md`  
42. `9-INFRASTRUCTURE/provenance/MASTER_INVENTORY.md`  
43. `9-INFRASTRUCTURE/provenance/AI_AGENT_ROLE_MAP.md`  
44. `9-INFRASTRUCTURE/provenance/AUDIT_WORKFLOW_MAP.md`  
45. `9-INFRASTRUCTURE/bot/README.md`  
46. `9-INFRASTRUCTURE/mcp-config.json`  
47. `9-INFRASTRUCTURE/bot/custom-gpt/SETUP_GUIDE.md`  
48. `9-INFRASTRUCTURE/bot/copilot-extension/DEPLOY.md`  
49. `9-INFRASTRUCTURE/bot/pages-chatbot/README.md`  
50. `9-INFRASTRUCTURE/bot/rag/DEPLOY.md`

### H. Testing and Reproducibility Anchors

51. `tests/conftest.py`  
52. `tests/test_metric.py`  
53. `tests/test_evolution.py`  
54. `tests/test_boundary.py`  
55. `tests/test_fixed_point.py`  
56. `src/core/five_tier_execution_framework.py` (regression gate command and operating model)  
57. `docs/WAVE_CHANGELOG.md`  
58. `docs/mas_tracker.yml`

### I. Outreach Calibration and Authorship-Standard Sources

59. `7-OUTREACH/OUTREACH_CALIBRATION.md`  
60. `7-OUTREACH/substack/README.md`  
61. `7-OUTREACH/substack/posts/post-063-ai-authorship.md`  
62. `7-OUTREACH/substack/posts/post-120-ai-built-this-collaboration.md`  
63. `7-OUTREACH/substack/posts/post-138-what-26000-tests-mean.md`

### J. Primary External Scientific Context (Foundational)

64. Kaluza, T. (1921). *Zum Unitätsproblem der Physik.*  
65. Klein, O. (1926). *Quantentheorie und fünfdimensionale Relativitätstheorie.*  
66. Einstein, A. (1915). *Die Feldgleichungen der Gravitation.*  
67. Dirac, P.A.M. (1928). *The Quantum Theory of the Electron.*  
68. Feynman, R.P. (1948). *Space-Time Approach to Non-Relativistic Quantum Mechanics.*  
69. Yang, C.N. & Mills, R.L. (1954). *Conservation of Isotopic Spin and Isotopic Gauge Invariance.*  
70. Weinberg, S. (1967); Salam, A. (1968); Glashow, S. (1961) electroweak unification papers.  
71. Randall, L. & Sundrum, R. (1999). *Large Mass Hierarchy from a Small Extra Dimension.*

### K. Primary External Cosmology / Data Context

72. Planck Collaboration (2018 cosmological parameters release).  
73. BICEP/Keck Collaboration (latest r upper-bound analyses used in repository framing).  
74. DESI Collaboration (Year 1 and follow-on dark-energy analyses for tension routing context).  
75. LiteBIRD mission references (primary future birefringence falsifier context).

### L. External Infrastructure / Process Context

76. Zenodo record for this repository: https://doi.org/10.5281/zenodo.19584531  
77. GitHub repository record: https://github.com/wuzbak/Unitary-Manifold-

---

## Companion Bibliography

A standalone, extended bibliography with structured grouping and expanded external context is provided at:

`7-OUTREACH/substack/references/post-140-credit-lineage-companion-bibliography.md`

---

Repository: https://github.com/wuzbak/Unitary-Manifold-  
Zenodo: https://doi.org/10.5281/zenodo.19584531

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
