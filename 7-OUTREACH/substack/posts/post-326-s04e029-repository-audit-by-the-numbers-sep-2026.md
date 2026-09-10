# Repository Audit (By the Numbers) — September 2026

This is a fresh quantitative audit of the full `wuzbak/Unitary-Manifold-` repository, prepared for Substack and scoped to code, documents, tests, pillars, formal work, products, dependencies, and API surfaces.

Audit timestamp: 2026-09-10 (UTC).  
Method: repository-wide filesystem scan plus regex-based inventorying for tests, routes, and theorem/proof assets, cross-checked against `STATUS.md`, `docs/mas_tracker.yml`, and `.github/copilot-instructions.md` for live/declared governance totals.

## 1) Repository scale snapshot

- Total files scanned: **6,332**
- Total code files (programming-language whitelist): **4,277**
- Total code lines (same scope): **1,085,939**

### Code lines by language (descending)

| Language | Files | Lines |
|---|---:|---:|
| Python | 3,831 | 1,001,503 |
| Kotlin | 135 | 33,877 |
| Lean4 | 159 | 18,454 |
| JavaScript | 37 | 14,150 |
| C++ | 4 | 4,699 |
| C/C++ Headers (`.h` + `.hpp`) | 10 | 5,382 |
| Kotlin Script | 47 | 2,335 |
| Rust | 24 | 2,221 |
| Shell | 19 | 1,755 |
| Batch | 6 | 848 |
| TypeScript | 1 | 410 |
| MATLAB/ObjC | 1 | 206 |
| Java | 3 | 99 |

## 2) Markdown inventory (readme, books, posts, other)

Total Markdown files: **1,505**

| Category | Count |
|---|---:|
| Readme | 625 |
| Books (`7-OUTREACH/substack/books`) | 44 |
| Posts (`7-OUTREACH/substack/posts`) | 349 |
| Other Markdown | 487 |

## 3) Pillar accounting

Two pillar views coexist and should be read together:

1. **Canonical hardgate framing** in `.github/copilot-instructions.md`:
   - **208 core physics pillars**
   - **992 total pillar slots** in that milestone framing
2. **Live sprint ledger framing** in `STATUS.md`/`docs/mas_tracker.yml`:
   - Latest listed pillar: **1120**
   - Next slot: **1121**

Current branch headline in `STATUS.md` records the latest verified full regression as:
**64,150 passed · 22 skipped · 18 deselected · 0 failed**.

## 4) Test volume and coverage surfaces

Static test inventory from source scan:

- Total Python test files: **1,530**
- Total `def test_*` definitions: **60,395**

Breakdown:

| Suite area | Test files | `def test_*` count |
|---|---:|---:|
| `tests/` | 1,479 | 57,002 |
| `recycling/` | 2 | 316 |
| `5-GOVERNANCE/Unitary Pentad/` | 49 | 3,077 |

Runtime collection (`pytest --collect-only`) could not be re-run in this sandbox because `pytest` is not installed in the active Python runtime, so this audit reports:
- static inventory above, and
- the latest verified runtime regression totals from `STATUS.md`.

## 5) Lean4 theorems and formal layer

- Lean files: **159**
- Lean `theorem` declarations found by token scan: **3,535**
- Live formal ledger value in status tracking: **Lean4 total 4,080**

The difference reflects that ledger totals are governance-tracked formal units, while token scanning counts literal `theorem` declarations in `.lean` files.

## 6) Other proofs and theorem artifacts

- `proof/` directory files: **17** total (**13** Markdown), **4,538** lines
- Markdown files with `proof`/`theorem` in path/name: **33**
- Markdown theorem mentions: **2,182**
- Markdown proof mentions: **1,543**
- Python modules with `theorem`/`proof`/`certificate` in filename: **325**
- LaTeX files: **2**

## 7) Product applications

In `12-AZ-IP/`, numbered product-style directories (`NN-*`): **24**.

## 8) Dependencies and package surfaces

Detected dependency manifests: **40**

| Manifest type | Count |
|---|---:|
| `requirements*.txt` | 34 |
| `pyproject.toml` | 1 |
| `package.json` | 2 |
| `setup.py` | 1 |
| Other (`environment*`, `lakefile.lean`) | 2 |

Python requirements footprint:
- Unique package names across `requirements*.txt`: **59**

Top-level packaging (`pyproject.toml`) declares core runtime deps including NumPy, SciPy, mpmath, DuckDB, Polars, PyArrow, Zarr, with optional groups for symbolic, API, AI, observability, notebooks, and dev toolchains.

JavaScript package surfaces:
- `9-INFRASTRUCTURE/bot/copilot-extension/package.json`
- `12-AZ-IP/24-psicat-web-browser/package.json`

## 9) API inventory

Route scan across Python API decorators found:

- Total routes: **121**
- Unique route paths: **108**
- Files declaring routes: **14**

Method split:

| Method | Count |
|---|---:|
| GET | 78 |
| POST | 39 |
| ROUTE (generic `@app.route`) | 4 |

Largest endpoint surfaces by file:

| File | Routes |
|---|---:|
| `12-AZ-IP/10-filmers-companion/desktop/app/production_suite/router.py` | 20 |
| `12-AZ-IP/01-axiom-os/api/server.py` | 17 |
| `12-AZ-IP/12-lithos-os/app/api/routes.py` | 14 |
| `lodge/server.py` | 12 |
| `12-AZ-IP/11-terra-os/app/api/routes.py` | 10 |
| `bot/assistant_api.py` | 9 |
| `12-AZ-IP/13-delphi/app/api/routes.py` | 9 |
| `src/core/um_sos_api.py` | 7 |

## 10) Holistic readout

By volume, this repository is now a large mixed system: a million-line Python-first codebase with formal Lean infrastructure, high-density testing, a substantial documentation and publication layer, and a multi-product application tree with nontrivial API surface area. The center of gravity remains Python + tests + formal/governance registries, while Substack books/posts and product applications have grown into major parallel structures rather than side notes.

## 11) Scenario replacement estimates (time + labor)

The following estimates assume replacement from scratch of equivalent breadth and operational posture (codebase scale, test depth, formal layer, multi-product registry, and documentation/publication footprint), using contemporary engineering best practices (CI, code review, test discipline, security posture, release governance). They are order-of-magnitude planning bands, not a bid quote.

| Scenario | Team shape | Labor estimate (hours) | Time estimate |
|---|---|---:|---:|
| A) Small team + AI | 8–12 cross-functional builders with strong AI acceleration | **140,000–230,000** | **~1.8–3.4 years** |
| B) Enterprise + domain experts | 30–45 staff across physics, formal methods, platform, QA/SRE, product, compliance | **260,000–420,000** | **~2.3–3.7 years** |
| C) Solo human (no AI) | 1 full-time senior generalist, no AI co-development | **520,000–900,000** | **~250–430 years** |

Interpretation: scenario A minimizes coordination cost and gets the strongest productivity multiplier from AI-assisted implementation; scenario B is faster in parallel throughput but pays substantial overhead in coordination, governance, and handoff boundaries; scenario C is mathematically dominated by labor volume and therefore not practical on a normal program horizon.

## 12) Scenario replacement cost estimates (best-practice execution)

Costs below use blended fully loaded rates (salary + overhead + tooling + infra + management burden) by scenario.

| Scenario | Assumed blended rate | Replacement cost band |
|---|---:|---:|
| A) Small team + AI | $140–$220 / hour | **$19.6M–$50.6M** |
| B) Enterprise + experts | $190–$320 / hour | **$49.4M–$134.4M** |
| C) Solo human (no AI) | $90–$160 / hour | **$46.8M–$144.0M** |

The apparent overlap between B and C is expected: enterprise spends more per hour but can parallelize; solo spends less per hour but requires drastically more hours and carries extreme continuity risk.

## 13) Asset-level financial value bands (replacement-value framing)

These are conservative replacement-value bands for major asset classes already present in this monorepo, based on observed scale (LOC/tests/formal assets/product count/API depth) rather than speculative revenue multiples.

| Asset class | Observable anchor in-repo | Estimated value band |
|---|---|---:|
| Individual apps (product layer) | 24 canonical products in `12-AZ-IP/` | **$12M–$32M** |
| Physics stack (hardgate + adjacent physics implementation) | `src/core/`, dimensional lanes, test corpus, falsification surfaces | **$20M–$60M** |
| Engines | registered engine catalog and runtime engine surfaces (`12-AZ-IP/engines/`) | **$6M–$18M** |
| OS layers | AZ-OS, AZ-KERNEL, UM-SOS, full-stack OS surfaces (`12-AZ-IP/os/`) | **$4M–$12M** |
| IP corpus (docs/books/posts/governance/formal narrative layer) | large structured publication and governance corpus | **$8M–$25M** |

## 14) Monorepo aligned-system value estimate

If these components are valued as one integrated system (shared provenance, shared tests, shared governance lane, shared APIs, and cross-layer interoperability), the system-level value should include an integration premium over category-level estimates. Because apps, engines, OS layers, and IP corpus overlap materially, the prior table is **non-additive** and should be read as indicative category bands, not strict sum-of-parts arithmetic.

- Non-additive category-level replacement-value envelope: **~$50M–$147M** (illustrative only)
- Integrated aligned-system monorepo estimate (best-practice replacement framing): **$75M–$220M**

Reason for premium: the operational value is not only the parts, but the fact that physics claims, formal artifacts, software products, governance rails, and public documentation are already synchronized in one continuously testable and auditable repository.
