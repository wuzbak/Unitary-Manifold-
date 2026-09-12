# Appendix A — Repository Credit Map and Attribution Matrix
## Companion to Book 33

This appendix maps major in-repository credit surfaces so attribution claims can be checked quickly.

All file references below are **repository-root-relative paths** in `wuzbak/Unitary-Manifold-`.

---

## A.1 Identity, Scope, and Citation Anchors

1. `README.md`  
2. `CITATION.cff`  
3. `PROVENANCE.md`  
4. `AGENTS.md`  
5. `SEPARATION.md`  
6. `FALLIBILITY.md`

---

## A.2 Core Physics and Formal Structure Anchors

1. `1-THEORY/UNIFICATION_PROOF.md`  
2. `1-THEORY/QUANTUM_THEOREMS.md`  
3. `proof/TIER_1_FORMAL.md`  
4. `src/core/metric.py`  
5. `src/core/evolution.py`  
6. `src/holography/boundary.py`  
7. `src/multiverse/fixed_point.py`

---

## A.3 Falsification and Epistemic-Honesty Anchors

1. `3-FALSIFICATION/FALSIFICATION_CONDITIONS.md`  
2. `3-FALSIFICATION/FALSIFICATION_REGISTER.md`  
3. `3-FALSIFICATION/OBSERVATION_TRACKER.md`  
4. `docs/CLAIM_MASTER_BOARD.md`  
5. `docs/TRUTH_LAYER.md`

---

## A.4 Governance and Co-Emergence Anchors

1. `5-GOVERNANCE/Unitary Pentad/README.md`  
2. `5-GOVERNANCE/co-emergence/FRAMEWORK.md`  
3. `CONTRIBUTING.md`  
4. `SECURITY.md`

---

## A.5 Toolchain and Provenance Infrastructure Anchors

1. `9-INFRASTRUCTURE/llms.txt`  
2. `9-INFRASTRUCTURE/schema.jsonld`  
3. `9-INFRASTRUCTURE/mcp-config.json`  
4. `9-INFRASTRUCTURE/provenance/README.md`  
5. `9-INFRASTRUCTURE/provenance/MASTER_INVENTORY.md`  
6. `9-INFRASTRUCTURE/provenance/AI_AGENT_ROLE_MAP.md`

---

## A.6 Testing and Reproducibility Anchors

1. `tests/conftest.py`  
2. `tests/test_metric.py`  
3. `tests/test_evolution.py`  
4. `tests/test_boundary.py`  
5. `tests/test_fixed_point.py`  
6. `docs/WAVE_CHANGELOG.md`  
7. `docs/mas_tracker.yml`  
8. `STATUS.md`

---

## A.7 Responsibility Matrix (Operational)

| Layer | Primary responsibility | Typical artifacts |
|---|---|---|
| Theory direction and scientific judgment | ThomasCory Walker-Pearson | theory framing, claim boundaries, acceptance/rejection decisions |
| Code architecture and implementation synthesis | GitHub Copilot (AI) under human direction | Python modules, integration logic, infrastructure glue |
| Regression and executable verification | GitHub Copilot (AI) with human oversight | tests, CI-facing updates, stability checks |
| Public-document engineering and outreach synthesis | GitHub Copilot (AI) with human editorial direction | books, posts, summaries, status narrative |
| Final stewardship and release judgment | ThomasCory Walker-Pearson | merge/promotion decisions, publication direction |

---

## A.8 Maintenance Notes

- When adjacent branches merge, update this appendix by appending new anchors rather than rewriting prior entries.  
- Keep references repository-relative and stable.  
- If attribution boundaries change, update both this appendix and Book 33 together.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
