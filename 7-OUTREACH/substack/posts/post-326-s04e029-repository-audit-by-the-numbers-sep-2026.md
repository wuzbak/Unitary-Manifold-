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
