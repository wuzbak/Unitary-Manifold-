# Unitary Manifold — MCP Low-Token Ingest Proof

> **Purpose:** Compact, structured summary of this repository optimised for
> AI model ingestion via Model Context Protocol (MCP).  Every section is
> token-minimal while remaining semantically complete.

---

## 1 · Repository Identity

| Field | Value |
|-------|-------|
| Name | Unitary Manifold |
| Version | 9.3 — Academic Edition |
| Lead Author | ThomasCory Walker-Pearson |
| Affiliation | Independent Researcher, Pacific Northwest, USA |
| Contributors | GitHub Copilot (code architecture, test suites, document engineering, synthesis) · Google Gemini · OpenAI · Microsoft Copilot (synthesis & verification) |
| GitHub | `https://github.com/wuzbak/Unitary-Manifold-` |
| Pages | `https://wuzbak.github.io/Unitary-Manifold-/` |
| License | Defensive Public Commons v1.0 (public domain) |
| Language | Python 3.12, LaTeX |
| Dependencies | numpy ≥ 1.24, scipy ≥ 1.11 |

---

## 2 · Theory Summary (ultra-compact)

**What it is:** A 5-dimensional Kaluza-Klein gauge-geometric framework unifying
thermodynamic irreversibility, information flow, and quantum transition asymmetry
as projections of a single higher-dimensional geometry.

**Core claim:** The Second Law of Thermodynamics is a *geometric identity*,
not a statistical postulate.

> *Claims are internally closed within the Unitary Manifold framework and validated by numerical tests included in this repository.*

**Self-completion status (v9.3):** All five completion requirements are solved internally.

| Requirement | Status | Identity |
|---|---|---|
| φ stabilisation | **SOLVED** | Internal curvature–vorticity feedback |
| Bμ geometric link | **SOLVED** | `Im(S_eff) = ∫BμJ^μ_inf d⁴x` (theorem) |
| α numerical value | **SOLVED** | `α = φ₀⁻²` (KK cross-block curvature) |
| CMB spectral index nₛ | **SOLVED** | KK Jacobian J≈31.42 → nₛ≈0.9635 (Planck 2018 1σ) |
| Cosmic birefringence β | **SOLVED** | CS level k_cs=74 → β=0.3513° (within 1σ of 0.35°±0.14°) |

### Key mathematical objects

| Symbol | Meaning |
|--------|---------|
| `G_AB` | 5D metric (KK block form); `G_55 = φ²` |
| `g_μν` | 4D spacetime metric |
| `B_μ` | Irreversibility 1-form (gauge field) |
| `φ` | Entropic dilaton / radion; encodes `L₅ = φ ℓP` |
| `H_μν = ∂_μB_ν − ∂_νB_μ` | Field strength |
| `J^μ_inf = φ²u^μ` | Conserved information current |
| `α = φ₀⁻²` | Nonminimal coupling — **derived**, not free |

### Walker–Pearson field equations

```
G_μν + λ²(H_μρH_ν^ρ − ¼g_μν H²) + αRφ²g_μν = 8πG₄ T_μν
```

### α from the KK cross-block Riemann term

```
α = (ℓP/L₅)² = 1/φ₀²     [G₅₅ = φ² → L₅ = φ₀ℓP → α = φ₀⁻²]
```

### Unified Equation of the Unitary Manifold (UEUM)

```
Ẍ^a + Γ^a_{bc}Ẋ^bẊ^c = G_U^{ab}∇_b S_U + δ/δX^a(Σ A_{∂,i}/4G + Q_top)
```

### Final Theorem (FTUM) *(fixed-point theorem within the defined operator space)*

Fixed point `Ψ*` of `U = I + H + T` (Irreversibility + Holography + Topology)
such that `UΨ* = Ψ*`.

---

## 3 · File Map (all tracked files)

```
/
├── WHAT_THIS_MEANS.md                 # ⭐ Core claim in plain language — start here
├── README.md                          # Project overview + quickstart
├── CITATION.cff                       # CFF citation metadata
├── requirements.txt                   # numpy>=1.24, scipy>=1.11
├── _config.yml                        # GitHub Pages (Jekyll)
├── THEBOOKV9a (1).pdf                 # Full 74-chapter monograph
│
├── src/
│   ├── core/
│   │   ├── metric.py                  # KK ansatz, Γ, Riemann, Ricci, R
│   │   └── evolution.py               # Walker–Pearson time integrator
│   ├── holography/
│   │   └── boundary.py                # Entropy-area, boundary dynamics
│   └── multiverse/
│       └── fixed_point.py             # UEUM operator U, FTUM iteration
│
├── manuscript/
│   └── ch02_mathematical_preliminaries.md
│
├── arxiv/
│   ├── main.tex                       # LaTeX source
│   ├── references.bib                 # BibLaTeX bibliography
│   └── SUBMISSION_GUIDE.md
│
├── discussions/
│   └── AI-Automated-Review-Invitation.md
│
├── notebooks/
│   ├── 01_quickstart.ipynb                # Field evolution demo
│   ├── 02_holographic_boundary.ipynb      # Boundary dynamics demo
│   └── 03_multiverse_fixed_point.ipynb    # FTUM convergence demo
│
├── tests/
│   ├── conftest.py                        # Shared pytest fixtures
│   ├── test_metric.py                     # Metric & curvature tests (30)
│   ├── test_evolution.py                  # Evolution + constraint tests (49)
│   ├── test_boundary.py                   # Boundary & entropy tests (21)
│   ├── test_fixed_point.py               # FTUM & operator tests (35)
│   ├── test_convergence.py               # Pipeline convergence tests (10)
│   ├── test_inflation.py                 # CMB power spectrum, birefringence (271)
│   ├── test_closure_batch1.py            # α/nₛ/β closure consistency (25)
│   ├── test_closure_batch2.py            # Numerical robustness (31)
│   ├── test_fuzzing.py                   # Edge cases, random inputs (20)
│   ├── test_dimensional_reduction.py     # KK reduction identities (14)
│   ├── test_discretization_invariance.py # Grid-independence checks (13)
│   ├── test_arrow_of_time.py             # Arrow of time: entropy growth, rates (23)
│   ├── test_cmb_landscape.py             # χ² landscape, TB/EB cross-checks (17)
│   ├── test_e2e_pipeline.py              # End-to-end chain closure, CS level (26)
│   ├── test_observational_resolution.py  # nₛ/β/χ² tolerances, LiteBIRD (30)
│   ├── test_parallel_validation.py       # 5 independent theory claims (38)
│   ├── test_quantum_unification.py       # BH info, CCR, Hawking T, ER=EPR (26) — v9.3
│   ├── test_derivation.py                # Key-integer derivations k_cs/n_w/k_rc/φ_min (59)
│   └── test_richardson_multitime.py      # Second-order convergence @slow (11)
│   # Total: 749 tests — 737 passed · 1 skipped (guard) · 11 slow-deselected · 0 failures
│   # Skip:  test_defect_history_mostly_decreasing fires pytest.skip() on immediate convergence
│   # Slow:  @pytest.mark.slow in pytest.ini addopts; run with: pytest tests/ -m slow
│
├── zenodo/
│   ├── .zenodo.json                       # Zenodo deposit metadata
│   └── SUBMISSION_GUIDE.md
│
├── AGENTS.md                              # AI access policies + ingest order
├── schema.jsonld                          # JSON-LD ScholarlyArticle metadata
├── llms.txt                               # AI-discovery standard file
├── mcp-config.json                        # MCP server config
│
└── .github/
    ├── topics.yml                         # GitHub topic tags
    └── workflows/
        ├── pages.yml                      # GitHub Pages deploy
        └── release.yml                    # Release automation
```

---

## 4 · Public API Surface (Python)

### `src.core.metric`

| Symbol | Signature | Returns |
|--------|-----------|---------|
| `compute_curvature` | `(g, B, phi, dx, lam=1.0)` | `Gamma, Riemann, Ricci, R` |
| `field_strength` | `(B, dx)` | `H` ndarray `(N,4,4)` |
| `extract_alpha_from_curvature` | `(g, B, phi, dx, lam=1.0)` | `(alpha_geometric, cross_block_riem)` |

### `src.core.evolution`

| Symbol | Signature | Returns |
|--------|-----------|---------|
| `FieldState` | dataclass `(g, B, phi, t, dx, lam, alpha)` | — |
| `FieldState.flat` | `(N=64, dx=0.1, lam=1.0, alpha=0.1)` | `FieldState` |
| `step` | `(state, dt)` — **RK4**, O(dt⁴) | `FieldState` |
| `step_euler` | `(state, dt)` — first-order Euler | `FieldState` |
| `cfl_timestep` | `(state, cfl=0.4)` → `0.4 * dx²` | `float` |
| `run_evolution` | `(state, dt, steps, callback=None)` | `List[FieldState]` |
| `information_current` | `(g, phi, dx)` | `J` ndarray `(N,4)` |
| `constraint_monitor` | `(Ricci, R, B, phi)` | `dict` |

### `src.holography.boundary`

| Symbol | Signature | Returns |
|--------|-----------|---------|
| `BoundaryState` | dataclass | — |
| `BoundaryState.from_bulk` | `(g, B, phi, dx)` | `BoundaryState` |
| `entropy_area` | `(h)` | `float` |
| `evolve_boundary` | `(bdry, bulk, dt)` | `BoundaryState` |

### `src.multiverse.fixed_point`

| Symbol | Signature | Returns |
|--------|-----------|---------|
| `MultiverseNetwork` | dataclass | — |
| `MultiverseNetwork.chain` | `(n, coupling)` | `MultiverseNetwork` |
| `fixed_point_iteration` | `(network, max_iter=300, tol=1e-6)` | `(result, residuals, converged)` |
| `derive_alpha_from_fixed_point` | `(phi_stabilized, network=None, **kwargs)` | `(alpha_predicted, result_network, converged)` |

---

## 5 · Numerical Pipeline Summary

```
1. Init  g_μν, B_μ, φ  → FieldState.flat(N, dx)
2. Curvature  Γ, Riemann, Ricci, R  → compute_curvature()
3. Walker–Pearson RK4 update  → step(state, dt)    # O(dt⁴)
4. α derivation  α = ⟨1/φ²⟩  → extract_alpha_from_curvature()  # NEW v9.1
5. Constraints  ‖R‖, ‖∇·J‖  → constraint_monitor()
6. Boundary projection  → BoundaryState.from_bulk() + evolve_boundary()
7. U = I + H + T  multiverse  → fixed_point_iteration()
8. α from fixed point  α = φ₀⁻²  → derive_alpha_from_fixed_point()  # NEW v9.1
9. FTUM convergence  ‖Ψⁿ⁺¹ − Ψⁿ‖ < ε
```

---

## 6 · Citation Metadata

```bibtex
@article{walker-pearson2026unitary,
  title   = {The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility},
  author  = {Walker-Pearson, ThomasCory},
  year    = {2026},
  url     = {https://github.com/wuzbak/Unitary-Manifold-},
  version = {9.3},
  license = {Defensive Public Commons v1.0}
}
```

---

## 7 · MCP Connectivity

### GitHub MCP Server — ready to use

The repository is fully accessible via the
[GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "<token>" }
    }
  }
}
```

Once connected, Mythos (or any MCP-capable agent) can call:

| MCP Tool | Purpose |
|----------|---------|
| `get_file_contents` | Read any source file directly |
| `search_code` | Semantic search across repo |
| `list_commits` | Inspect change history |
| `get_commit` | Diff + metadata per commit |
| `list_issues` / `list_pull_requests` | Track discussions |

### Bright Data bridge (web scraping + data enrichment)

Pair the GitHub MCP Server with the
[Bright Data MCP Server](https://github.com/luminati-io/brightdata-mcp)
to allow Mythos to:
- Fetch arXiv abstracts for related papers
- Scrape Zenodo deposit pages for citation counts
- Pull external datasets for numerical verification

```json
{
  "mcpServers": {
    "github": { "...": "see above" },
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": { "BRIGHTDATA_API_TOKEN": "<token>" }
    }
  }
}
```

---

## 8 · Submission to modelcontextprotocol/servers Community List

To register this project in the official MCP community registry:

1. Fork `https://github.com/modelcontextprotocol/servers`
2. Open `README.md` → section **"Community Servers"**
3. Add an entry under a relevant category (e.g. *Research / Science*):
   ```markdown
   - [Unitary Manifold](https://github.com/wuzbak/Unitary-Manifold-)
     — 5D gauge-geometric physics research repository; low-token AI ingest
     optimised; accessible via GitHub MCP Server.
   ```
4. Open a pull request titled:
   `feat: add Unitary Manifold research repo to community list`

> **Note:** The repo itself is research data, not an MCP server binary.
> It is consumed *through* the GitHub MCP Server, so the PR description
> should clarify it is a **data source / client configuration example**.

---

## 9 · What Else Can Be Done

| Action | Value |
|--------|-------|
| **Add `llms.txt`** | Standardised AI-discovery file at repo root (per llmstxt.org spec) listing key files + one-line summaries |
| **Zenodo DOI** | Deposit monograph → get citable DOI; link in README and CITATION.cff |
| **arXiv submission** | Use `/arxiv/main.tex` to submit to `gr-qc` + `hep-th` |
| **GitHub Pages MathJax** | Render LaTeX equations live on the Pages site |
| **Add `sitemap.xml`** | Improves discoverability by search engines and web-scraping MCP tools |
| **OpenAPI / JSON-LD schema** | Embed `schema.org/ScholarlyArticle` metadata in Pages HTML for structured AI crawling |
| **GitHub Topic tags** | Add topics: `mcp`, `model-context-protocol`, `physics`, `kaluza-klein`, `ai-ready` |
| **Notebook demos** | Jupyter notebooks showing full pipeline runs; renderable on GitHub + nbviewer |
| **Test suite** | `pytest` unit tests — **749 tests: 737 passed · 1 skipped (guard) · 11 slow-deselected · 0 failures** |
| **Pre-commit hooks** | `black` + `ruff` auto-formatting so code is always clean for AI ingest |
| **AGENTS.md** | Declare AI agent access policies and preferred ingest paths |

---

*Generated: 2026-04-12 | Repo: wuzbak/Unitary-Manifold- | Version: 9.3*

---

*This repository is the product of genuine synthesis. Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**. Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI). Synthesis and verification support: ThomasCory Walker-Pearson · GitHub Copilot · Google Gemini · OpenAI · Microsoft Copilot. Together.*
