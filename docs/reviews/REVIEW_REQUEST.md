# 🔍 In-House Review Request — Unitary Manifold

> **Badge:** `[REVIEW]` `[HISTORICAL]` `[ARCHIVE]`

**Date raised:** 2026-05-08  
**Raised by:** ThomasCory Walker-Pearson (repository owner)  
**Review type:** Engineering, scientific-claim, and governance review  
**Priority:** Serious — before any broader publication or tooling integration

---

## 1 · What This Repository Is

The **Unitary Manifold** is a 5-dimensional Kaluza-Klein physics framework
that claims to derive Standard Model parameters (quark masses, coupling
constants, mixing angles, CMB observables) from a single 5D metric ansatz.

Key numbers at time of this review request:

| Metric | Value |
|--------|-------|
| Active pillars | 208 core + special modules |
| Test suite size | ~26 300 passing tests (0 failures gated) |
| Claimed ToE score | 19.5 / 28 SM parameters (~70%) |
| Primary falsifier | CMB birefringence β ∈ {0.273°, 0.331°} — LiteBIRD ~2032 |
| Authorship model | Human theory + AI (GitHub Copilot) code/tests |

Supporting frameworks co-located in this repo:

- **Recycling (Pillar 16):** φ-debt entropy accounting system  
- **Unitary Pentad:** Independent HILS governance framework (18 modules)  
- **bot/:** RAG assistant infrastructure and Copilot Extension  

---

## 2 · Why an In-House Review Is Warranted

1. **Scale:** The repo is unusually large for a solo research project — 26 000+ tests, 200+ source modules, governance documents, bot infrastructure, and a LaTeX monograph.
2. **Extraordinary claims:** Deriving all Standard Model parameters from geometry would be a landmark result. The scoring system (ToE score) is self-assessed.
3. **AI authorship:** The codebase is explicitly AI-generated (GitHub Copilot). The test suite was also written by AI. This means passing tests confirm internal self-consistency, not physical correctness.
4. **Tooling and access patterns:** The repo includes MCP server configurations, a RAG bot, and a Copilot Extension — these require careful review of what data they expose and to whom.
5. **Licensing complexity:** Multiple license files exist (`LICENSE`, `LICENSE-AGPL`, `COMMERCIAL_TERMS.md`, `LEGAL.md`, `DUAL_USE_NOTICE.md`). Their interaction needs clarification.

---

## 3 · Recommended Review Areas

### 3.1 Reproducibility
- [ ] Clone repo and run full regression gate independently:
  ```bash
  python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q \
    --ignore=tests/test_symbolic_metric.py \
    --ignore=tests/test_formal_proof_hardening.py \
    --ignore=tests/test_neural_symbolic_drift_check.py
  ```
  Expected: ~26 300 passed, 0 failed
- [ ] Verify tests are testing genuine physical content vs. tautological self-checks
- [ ] Check whether "GEOMETRIC_PREDICTION" status labels are independently verifiable

### 3.2 Scientific Claim Integrity
- [ ] Audit `docs/TOE_SCORE_AUDIT.md` — are parameter residuals computed from PDG values correctly?
- [ ] Audit `FALLIBILITY.md` — are all known gaps honestly documented?
- [ ] Review `3-FALSIFICATION/OBSERVATION_TRACKER.md` — are falsification conditions real and falsifiable?
- [ ] Check for circular reasoning: do tests encode the "predictions" they're claimed to verify?

### 3.3 AI-Authored Code Quality
- [ ] Sample `src/core/`, `src/physics/`, `src/multiverse/` for code correctness
- [ ] Verify that physics equations in Python match stated mathematical derivations in `1-THEORY/`
- [ ] Check `docs/mas_tracker.yml` versioning discipline (v10.27 at review time)

### 3.4 Bot / Tooling Infrastructure
- [ ] Audit `bot/` directory for data handling, access controls, secret exposure
- [ ] Review `mcp-config.json` and `9-INFRASTRUCTURE/` for external service dependencies
- [ ] Check `.github/` workflows for supply-chain risks

### 3.5 Licensing and Compliance
- [ ] Reconcile `LICENSE` (DPCL 1.0), `LICENSE-AGPL`, and `COMMERCIAL_TERMS.md`
- [ ] Review `DUAL_USE_NOTICE.md` — are dual-use controls appropriate?
- [ ] Verify `AGENTS.md` permitted-action declarations are consistent with actual repo behavior

### 3.6 Governance / Authorship
- [ ] Confirm authorship boundary (human theory / AI code) is accurately documented everywhere
- [ ] Review `SEPARATION.md` — is the physics/governance boundary clear and maintained?
- [ ] Assess `5-GOVERNANCE/Unitary Pentad/` independence claim

---

## 4 · Known Open Issues (from `FALLIBILITY.md`)

1. **CMB acoustic peak suppression:** Power spectrum amplitude suppressed ×4–7 at acoustic peaks — documented as Admission 2; partially addressed by Pillars 57+63 but not fully closed.
2. **n_w = 5 uniqueness:** Winding number selection not yet proved from first principles alone; Planck n_s data provides the final selection (Admission 3).
3. **Cosmological constant:** ~10⁵⁸ gap remains; status ARCHITECTURE_LIMIT_CERTIFIED(10D) — honest but unresolved.

---

## 5 · Contacts and Resources

| Resource | Location |
|----------|----------|
| Full monograph | `6-MONOGRAPH/` and `THEBOOKV9a (1).pdf` |
| Quick orientation | `6-MONOGRAPH/MCP_INGEST.md` |
| Test gate command | See §3.1 above |
| Observation tracker | `3-FALSIFICATION/OBSERVATION_TRACKER.md` |
| Roadmap | `docs/mas_tracker.yml` |
| Falsification conditions | `FALLIBILITY.md` |
| GitHub Issues | https://github.com/wuzbak/Unitary-Manifold-/issues |

---

*This review request was raised by the repository owner and drafted with GitHub Copilot (AI) assistance.*  
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
