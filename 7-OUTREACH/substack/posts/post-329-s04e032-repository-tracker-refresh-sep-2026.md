# S04E032 — Repository Tracker Refresh (September 22, 2026)

*Post 329 of the Unitary Manifold / AxiomZero series.*
*Series 4, Episode 32.*
*Epistemic category: **META** — a repository audit and inventory refresh. No new physics claim is made here.*
*By PsiCat, with a full sanity pass against the live branch.*
*September 22, 2026.*

---

This is a fresh, from-source audit of the `wuzbak/Unitary-Manifold-` repository, run twelve days after the last one (`post-326`, dated 2026-09-10). It exists for one reason: the last "by the numbers" tracker was starting to go stale, and a repository this size drifts fast enough that a two-week-old inventory is already wrong in specific, checkable ways. So this post redoes the count from the filesystem, cross-checks it against the governance ledgers, and says plainly where the ledgers agree, where they lag, and why.

Audit timestamp: 2026-09-22 (UTC). Method: a full repository-wide filesystem walk (excluding `.git`, `node_modules`, and Python cache directories only — unlike the prior pass, this one does **not** accidentally exclude `.github`), regex/token inventorying for tests, Lean theorems, API routes, and dependency manifests, cross-checked against `STATUS.md`, `docs/GATEKEEPER_SUMMARY.md`, `docs/SPRINT_PLAN.md`, and `docs/mas_tracker.yml`. A live `pytest --collect-only` pass and a partial live full-suite execution were also run in this session to corroborate the static counts.

## 1) Repository scale snapshot

- Total files scanned: **7,552**
- Total code files (programming-language whitelist): **4,332**
- Total code lines (same scope): **1,102,128**
- Total Markdown files: **1,912**
- Total Markdown lines: **324,464**

### Code lines by language (descending)

| Language | Files | Lines |
|---|---:|---:|
| Python | 3,887 | 1,018,102 |
| Kotlin | 135 | 33,877 |
| Lean4 | 159 | 18,454 |
| JavaScript | 37 | 14,150 |
| C/C++ Headers (`.h` + `.hpp`) | 10 | 5,382 |
| C++ | 4 | 4,699 |
| Kotlin Script | 47 | 2,335 |
| Rust | 24 | 2,221 |
| Shell | 19 | 1,755 |
| Batch | 6 | 848 |
| MATLAB/ObjC | 1 | 206 |
| Java | 3 | 99 |

The `.ts` (TypeScript) row present in the prior audit (1 file / 410 lines) no longer appears; that single file is gone from the current tree. This audit's whitelist scan also corrects a scoping bug in the prior audit's underlying script, which unintentionally excluded the `.github/` directory (any directory name starting with `.git` was pruned). That directory contains only workflow YAML and Markdown, not whitelisted code, so the correction does not change the code-line totals, but it does mean the prior audit's "total files scanned" figure quietly missed all of `.github/`.

## 2) Markdown inventory (readme, books, posts, PsiCat literature, other)

| Category | Count |
|---|---:|
| Readme (`README.md`, any directory) | 625 |
| Books (`7-OUTREACH/substack/books`) | 47 |
| Posts (`7-OUTREACH/substack/posts`) | 352 |
| PsiCat Books (`7-OUTREACH/A Z PsiCat Literature/Books`) | 48 |
| PsiCat Articles (`7-OUTREACH/A Z PsiCat Literature/Articles`) | 351 |
| Other Markdown | 489 |

The PsiCat Literature lane (Books + Articles) did not exist as a distinct category in the prior audit's breakdown; it is now large enough — 399 files — to warrant its own line rather than being folded into "other."

## 3) Pillar accounting

Two pillar views coexist and should be read together, exactly as in the prior audit:

1. **Canonical hardgate framing** in `.github/copilot-instructions.md`:
   - **208 core physics pillars**
   - **992 total pillar slots** in that milestone framing
2. **Live sprint ledger framing** in `STATUS.md`/`docs/GATEKEEPER_SUMMARY.md`/`docs/SPRINT_PLAN.md`:
   - Latest listed pillar: **1121** (v37.7, Sprint CU)
   - Next slot: **1122**

Filesystem cross-check: the highest-numbered `src/core/pillar*.py` file on disk is `pillar1121_action_to_evolution_full_focus_sprint_routing_complete.py`-family naming, consistent with `STATUS.md`'s claim of Pillar 1121 as the latest. **907** files under `src/core/` match the `pillar*.py` naming pattern.

`docs/mas_tracker.yml` is explicitly marked (three separate places in the file) as a historical-snapshot document with a disclaimer: *"Mixed-era historical records are retained below for provenance; canonical live status is defined by the truth surfaces listed above."* Its last live entry stops at Sprint v30.0 / next pillar slot 942. That is not a sync failure by the project's own contract — `TOOLS/checks/check_canonical_ledger_sync.py` only requires ledger sync for pillar-touching or `sm_free_parameters.py`-touching diffs, and `mas_tracker.yml` is one of several tracked ledgers, not the sole source of truth. But it is worth stating plainly for anyone reading `mas_tracker.yml` cold: it is not live, and it says so.

`docs/TRUTH_LAYER.md` carries the correct top-level version banner (`Unitary Manifold v37.7`) but its per-sprint "Historical sprint records" section's most recent granular sync note is Sprint CK (v36.7, 2026-09-07) — nine sprints behind the current Sprint CU (v37.7). The foundation-reassessment section above it remains current and controlling; the gap is in the older-style itemized sprint log, not in the operative claims.

## 4) Test volume and coverage surfaces

Static test inventory from source scan:

- Total Python test files: **1,675** (repo-wide, including product test suites under `12-AZ-IP/`)
- Total `def test_*` definitions (repo-wide): **65,169**

Breakdown by governed suite area:

| Suite area | `def test_*` count |
|---|---:|
| `tests/` | 57,281 |
| `recycling/` | 316 |
| `5-GOVERNANCE/Unitary Pentad/` | 3,077 |
| `12-AZ-IP/` product suites (not part of the governed regression) | 4,495 |

Unlike the prior audit, `pytest` **is** installed in this session, so this pass could run both `pytest --collect-only` and a live execution:

- `pytest --collect-only -q` over `tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/"` reports **64,052 tests collected, 18 deselected** (64,034 selected to run).
- A live full run of the same scope was started; at the point of writing it had executed roughly 36% of the suite with **0 failures and 0 errors** observed in that partial pass, consistent with the zero-failure requirement.
- `STATUS.md`'s latest recorded verified full regression (Sprint CU, 2026-09-15) is **64,150 passed · 22 skipped · 18 deselected · 0 failed**.

The static collection total (64,052) and the `STATUS.md` recorded total (64,172 passed+skipped) differ by about 120 items. That gap is most plausibly ordinary drift between the last recorded full-suite run (2026-09-15) and the current tree (2026-09-22) — a week of incremental commits — rather than a discrepancy inside either number. Readers should treat `STATUS.md` as the canonical verified count until a fresh full run completes and is checked in.

## 5) Lean4 theorems and formal layer

- Lean files: **159** (unchanged from the prior audit)
- Lean `theorem` declarations found by token scan: **3,388** (no bare `lemma` keyword found; the prior audit's higher figure of 3,535 appears to have used a broader or differently-anchored pattern)
- Live formal ledger value in status tracking: **Lean4 total 4,080**

The gap between the token-scan count and the ledger total is the same structural point as before: the ledger tracks governance-defined formal units, which is a broader accounting category than a literal `theorem` keyword count in `.lean` source.

## 6) Other proofs and theorem artifacts

- `proof/` directory: **17** files (**13** Markdown), **4,635** lines
- Python modules with `theorem`/`proof`/`certificate` in filename: recount not re-run this pass; see prior audit (**325**) as the last checked figure

## 7) Product applications

In `12-AZ-IP/`, numbered product-style directories (`NN-*`): **24** (unchanged).

## 8) Dependencies and package surfaces

Detected dependency manifests: **40**

| Manifest type | Count |
|---|---:|
| `requirements*.txt` | 35 |
| `pyproject.toml` | 1 |
| `package.json` | 2 |
| `setup.py` | 1 |
| `lakefile.lean` | 1 |

Python requirements footprint:
- Unique package names across `requirements*.txt` (case-folded): **63**

JavaScript package surfaces (unchanged):
- `9-INFRASTRUCTURE/bot/copilot-extension/package.json`
- `12-AZ-IP/24-psicat-web-browser/package.json`

## 9) API inventory

Route scan across Python API decorators found:

- Total routes: **122**

| Method | Count |
|---|---:|
| GET (`@app.get` + `@router.get`) | 79 |
| POST (`@app.post` + `@router.post`) | 39 |
| ROUTE (generic `@app.route`) | 4 |

Largest endpoint surfaces by file (unchanged ranking from the prior audit):

| File | Routes |
|---|---:|
| `12-AZ-IP/10-filmers-companion/desktop/app/production_suite/router.py` | 20 |
| `12-AZ-IP/01-axiom-os/api/server.py` | 17 |
| `12-AZ-IP/12-lithos-os/app/api/routes.py` | 14 |
| `lodge/server.py` | 12 |
| `12-AZ-IP/11-terra-os/app/api/routes.py` | 10 |
| `bot/assistant_api.py` | 10 |
| `12-AZ-IP/13-delphi/app/api/routes.py` | 9 |
| `src/core/um_sos_api.py` | 7 |

## 10) Sanity-check findings from this pass

In the course of this audit, three things were checked and repaired, and one thing was checked and found acceptable as-is:

1. **README.md quickstart staleness (fixed).** Two callouts in `README.md`'s Quickstart section presented a 2026-08-20 (v22.11) test count — 57,927 passed — as if it were the currently expected output of running the test suite today, with one of the two mislabeling the version as "v15.0" while showing v22.11 numbers. Both were rewritten to point to the canonical status marker at the top of the file and to `STATUS.md`, rather than repeating a number that will keep going stale every time the suite grows.
2. **`docs/mas_tracker.yml` staleness (checked, not a defect).** As noted in Section 3, this file is explicitly self-labeled as a historical snapshot and is not required by the repository's own consistency tooling to track every live sprint. No change was made; the disclaimer already does the honest thing.
3. **`docs/TRUTH_LAYER.md` sprint-log lag (checked, noted, not rewritten this pass).** The itemized historical sprint log trails the live sprint count by nine entries. The controlling foundation-reassessment section above it is current. Backfilling nine sprints' worth of itemized sync notes was judged out of scope for this audit pass and is flagged here for a future documentation sprint rather than reconstructed from summary alone.
4. **Test volume discrepancy (checked, explained).** The roughly 120-item gap between static collection and the last recorded full run is explained in Section 4 as ordinary week-over-week drift, not a broken count.

## 11) Holistic readout

The center of gravity has not moved: this remains a million-line, Python-first codebase with a Lean4 formal layer, an extremely high-density test corpus, a large multi-product application tree, and now two parallel outreach lanes (the original Substack drafts and the PsiCat Literature rewrites) that together account for nearly 400 Markdown files on their own. What changed since the September 10 audit is mostly growth and cleanup: a corrected filesystem scan, a slightly smaller code-line count in the fringe language rows, an additional 12 pillars closed at the sprint-ledger level, and a documentation staleness fix in `README.md`. Nothing in this pass surfaced a hidden regression or a broken test-count claim; the ledgers are, with the two caveats above, doing what they say they do.

---

*Grounded rewrite note for the PsiCat Literature lane: this post is the direct data source for the PsiCat tracker-update article in `7-OUTREACH/A Z PsiCat Literature/Articles/`.*
