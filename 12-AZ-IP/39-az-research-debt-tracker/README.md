# AZ Research-Debt Tracker — Product 39

**Folder:** `12-AZ-IP/39-az-research-debt-tracker/`
**Version:** 1.1.0
**TRL:** TRL-4 (generic library, now a runnable read-only web dashboard; dogfooded against the project's own real gap list)
**Status:** Active — Phases 1-2 of article-354's "MAS Wave Engine -> generic research-debt tracker" roadmap

## What this is

`src/meta/mas_wave_engine.py`'s `GapItem` / `FrameworkScore` /
`validate_wave_output()` already implement a working gap-tracking and
closure-scoring model, but its vocabulary (pillars, falsifiers,
physics-specific epistemic labels) is Unitary-Manifold-specific. This
product strips that vocabulary and generalizes the same shape:

- `WorkItem` — a tracked unit of debt, with a configurable `status` string.
- `StatusTaxonomy` — the project's own declaration of which status names
  count as "closed" vs "open".
- `ResearchDebtTracker` — add/query items, compute `health_score()`
  (closure fraction, breakdown by status), and `validate_closure()` an
  item against tests-passed/failed + documentation requirements.
- `um_dogfood.load_um_gaps_into_tracker()` — loads the project's own
  real, live 6-item gap list straight out of
  `MASWaveEngine().audit_all_gaps()` into the generic tracker, proving the
  generalization is faithful to at least one real consumer rather than a
  synthetic-only demo.

## Epistemic status

This is a general-purpose library; it does not replace
`src/meta/mas_wave_engine.py`, which remains canonical for UM's own pillar
tracking. The web layer below (Phase 2) serves the project's own live
`um_dogfood` tracker read-only; it is a single-project dashboard, not a
shared multi-project SaaS service — adding items or building a new tracker
still requires Python code via `ResearchDebtTracker` directly.

## Usage

```bash
python 12-AZ-IP/39-az-research-debt-tracker/run.py
```

## Running as a web product

```bash
python 12-AZ-IP/39-az-research-debt-tracker/run.py --serve --port 8139
```

Then visit `http://127.0.0.1:8139/` for the tracker dashboard, or query
the JSON API directly:

- `GET /api/status` — product metadata, dogfood source, total item count
- `GET /api/health-score` — closure fraction, breakdown by status
- `GET /api/open-items` — all open `WorkItem`s
- `GET /api/closed-items` — all closed `WorkItem`s
- `GET /api/item?item_id=` — one item by id

## Committed-source debt inventory (no credentials)

Use a local Git repository's committed TODO/FIXME comments as reproducible
evidence instead of manually constructing every `WorkItem`. Git must be on
`PATH`; no network, API token, third-party Python package or repository
modification is required.

From the Unitary Manifold repository root:

```bash
python 12-AZ-IP/39-az-research-debt-tracker/run.py \
  --git-repo . --revision HEAD \
  --output 12-AZ-IP/39-az-research-debt-tracker/debt-inventory.json
```

`--git-repo` also accepts another local repository. `--revision` accepts a
commit hash, tag or branch and resolves it once to an immutable commit.
Stdout and the optional output file contain the same JSON snapshot: generic
tracker health score and open items, each with exact commit hash, blob hash,
file path, line number, original comment and a triage next action. TODO is
`minor`; FIXME is `significant`; these are triage defaults, not risk analysis.
`owner_ref` is a source locator, **not** an inferred responsible person.

Review significant items first, assign a responsible owner in your existing
issue system, reproduce the concern and verify remediation. The recorded
blob remains inspectable even if the working tree changes:

```bash
git cat-file blob <blob-hash-from-evidence>
```

Add `--fail-on-debt` to use the inventory as an opt-in local/CI gate:
exit **1** means recognized debt exists, **0** means successful inventory
(with no debt when gating), and **2** means an input/Git/output error.
Errors are not treated as healthy empty results and Git/input failures do
not overwrite a prior report. The output parent directory must exist.
Successful writes replace the named file; choose a report path, not source.

Python callers can use
`from az_research_debt_tracker import ingest_git_debt` and
`ingest_git_debt(repo_path, revision="HEAD")` to obtain the same dictionary.

### Scope and limitations

- Reads committed regular source blobs only; ignores staged, dirty and
  untracked files, symlinks and submodules. It never executes source or hooks.
- Recognizes uppercase TODO/FIXME at the start of standalone `#`, `//`,
  `/*`, `*` or `--` comment-shaped lines. Inline comments are not recognized.
  This is a conservative text inventory, not a language parser: comment-shaped
  lines inside multiline strings can match. Review the original evidence.
- Supported extensions: `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.go`, `.rs`,
  `.c`, `.h`, `.cpp`, `.hpp`, `.java`, `.sh`, `.sql`. Binary/non-UTF-8
  source files are skipped and counted in `coverage`; other files are outside
  scope. No markers does **not** mean no research debt.
- IDs derive from path, line number and marker; repeated scans of a commit
  are deterministic, but IDs may change when lines move. Reports are separate
  snapshots, not a persistent lifecycle database. A disappearing comment is
  **not** verified closure and does not generate a closed item.
- The importer does not run tests, verify claims, create issues, infer owners,
  or update the existing UM read-only web dashboard. The existing manual
  closure-validation API and dashboard remain unchanged.
- Reports include local repository paths and source comments; inspect them
  before sharing. Large repositories require one Git blob read per supported
  file; each Git command has a 60-second timeout.

## Tests

```bash
python -m pytest 12-AZ-IP/39-az-research-debt-tracker/tests -q
```

For product-only validation without the repository-wide training hooks/config:

```bash
python -m pytest -c /dev/null -p no:cacheprovider \
  --confcutdir=12-AZ-IP/39-az-research-debt-tracker \
  12-AZ-IP/39-az-research-debt-tracker/tests -q
```

Requires `pytest` and Git. Integration tests create real disposable repositories
inside this product folder and remove them afterward; they do not use external
credentials or network services.

## Sources

- `src/meta/mas_wave_engine.py` — `GapItem`, `FrameworkScore`, `validate_wave_output`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #12

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
