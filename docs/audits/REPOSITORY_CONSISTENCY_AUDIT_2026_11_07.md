# Repository consistency audit — 2026-11-07

## Checkpoint and isolation

- Baseline: `b47cf02` (full hash is recorded in the draft PR).
- Dedicated branch: `copilot/repository-consistency-audit-20261107`.
- All edits occur in a separate Git worktree. Do not switch, reset, merge into,
  or clean the original worktree or another contributor's branch.
- This is an ongoing audit, not a repository-wide certification. No physics
  result, observational confirmation, score, or regression total is asserted
  by creating this checkpoint.

## Review plan

1. Review current claim/status ledgers against the isolated formal gate and
   documented open obligations; distinguish current claims from history.
2. Review AI discovery and RAG ingestion for stale canonical pointers,
   unsupported summaries, and loss of epistemic boundaries.
3. Review machine-readable status and consistency checks against their
   authoritative inputs and executable contracts.
4. Correct only reproduced, evidence-backed defects. Preserve unresolved
   findings with exact source locations and reasons for deferral.
5. Triple-check each correction: source evidence, relevant executable
   validation, and independent final-diff review.

## Findings

### Machine-readable status review

Expert review completed on the checkpoint branch. The first correction tranche
addresses the presentation defects below; the underlying physical obligations
are not closed:

| ID | Evidence at baseline | Finding | Disposition |
|----|----------------------|---------|-------------|
| S1 | `9-INFRASTRUCTURE/generate_live_status.py:138-144`; `docs/TRUTH_LAYER.md:241-260` | EXP-7 publishes an unsupported detector comparison as PASS. The reassessment leaves physical cross-section and detector-limit fields unset. | Correct the live summary; do not invent a replacement amplitude. |
| S2 | `9-INFRASTRUCTURE/generate_live_status.py:65,120-125`; `FALLIBILITY.md:2820-2854`; `docs/CLAIM_MASTER_BOARD.md:477-483` | EXP-5 conflates the approximately 1 TeV KK scale with the first approximately 3.98 TeV graviton mode and labels an unresolved channel comparison PASS. | Preserve channel dependence and explicit tension; no new universal exclusion claim. |
| S3 | `bot/assistant_api.py:292-315`; `docs/TRUTH_LAYER.md:96-102`; `docs/mas_tracker.yml:44` | API compatibility text claims repository-wide mathematical self-consistency and omits historical regression provenance. | Qualify compatibility fields without changing historical counts. |
| S4 | `bot/assistant_api.py:260-270,292-315` | Unavailable sources produce zero failures and a success-shaped epistemic assertion. | Return explicit unknown counts and unavailable status, with logging and fallback regressions. |
| S5 | `9-INFRASTRUCTURE/generate_live_status.py:417-429`; `.github/workflows/status-drift-gate.yml:19-20` | Generator `--check` does not compare the checked-in artifact; the drift workflow does not invoke that comparison. | Add artifact drift detection and negative tests; do not present substring scans as scientific validation. |

The expert ran the existing generator and drift checks successfully and found
the baseline JSON equal to generated output. That equality does not make the
embedded predictions correct. Targeted pytest was unavailable in the default
interpreter (`No module named pytest`).

### Coverage boundary

The status expert reviewed the named pipeline, tracker provenance, relevant
truth passages, drift workflow, and targeted tests. It did not certify all
detector calculations, all frontend consumers, or repository-wide correctness.
### Canonical-claim review

| ID | Evidence at baseline | Finding | Disposition |
|----|----------------------|---------|-------------|
| C1 | `README.md:73`; `docs/TRUTH_LAYER.md:2118`; `docs/CLAIM_MASTER_BOARD.md:39-53` | Current prose asserts all derivation chains are internally self-consistent despite withdrawn or open foundation obligations. | Replace blanket all-clear with scoped software evidence and the reassessment. |
| C2 | `docs/TRUTH_LAYER.md:2,971-973`; `STATUS.md:3,80` | Truth Layer header says v38.2 although the current record and included P1135 section are v38.6. | Synchronize the current document header, not historical sprint entries. |
| C3 | `docs/GATEKEEPER_SUMMARY.md:40-42`; `STATUS.md:80` | “Verified full regression in the current branch” blurs the Sprint CU receipt with current Sprint DB validation. | State historical provenance explicitly; retain the receipt unchanged. |

This expert reviewed the eight assigned canonical documents and navigation.
It did not independently establish the mathematical counterexamples, evaluate
every derivation, or run source-level physics tests.

### AI-discovery and RAG review

| ID | Evidence at baseline | Finding | Disposition |
|----|----------------------|---------|-------------|
| R1 | `.github/copilot-instructions.md:3,37-39`; `6-MONOGRAPH/MCP_INGEST.md:3,39`; `docs/TRUTH_LAYER.md:987-989` | AI entry points present undated regression markers and snapshot counts as current expectations. | Label historical receipts and direct current status to canonical evidence; do not guess totals or runtimes. |
| R2 | `6-MONOGRAPH/MCP_INGEST.md:34-48`; `docs/TRUTH_LAYER.md:840-845` | The ingest summary calls claims internally closed and the curvature alpha diagnostic SOLVED/derived. | Preserve the old summary as history, explicitly supersede its closure language, and distinguish the diagnostic from an action-derived coupling. |
| R3 | `9-INFRASTRUCTURE/llms.txt:26`; `AGENTS.md:103-104`; `bot/assistant_api.py:101-107`; `proof/TIER_1_FORMAL.md:24-26,44-48,70-80` | Discovery descriptions and assistant gate definitions upgrade repository arguments/labels to formal physical closure. | State conditions and Tier-1 proof rules explicitly; registry labels do not discharge foundation obligations. |

The RAG expert executed `bot.rag_index.RAGIndex.build` and `search` locally
with `include_psicat_literature=False` and `UM_PSICAT_EDITORIAL_CORPUS=0`.
The deterministic corpus contained **2,022 chunks**. A query for current full
regression/historical pass counts retrieved Truth Layer passages qualifying
recorded metadata rather than green execution. No external indexing, hosted
expert session, model inference, or credentials were used.

Reproduction from the dedicated worktree:

```bash
UM_PSICAT_EDITORIAL_CORPUS=0 python -c 'from pathlib import Path; from bot.rag_index import RAGIndex; i=RAGIndex.build(repo_root=Path.cwd(), include_psicat_literature=False); r=[(s,c.source," ".join(c.text.split())[:180]) for s,c in i.search("current full regression historical pass count not a current all clear",top_k=20) if c.source in {"docs/TRUTH_LAYER.md","6-MONOGRAPH/MCP_INGEST.md",".github/copilot-instructions.md"}][:5]; print(f"chunks={len(i.chunks)} editorial=off; results={r}")'
```

The expert reviewed the assigned discovery documents and RAG manifest/prompt
surfaces. `schema.jsonld` is explicitly versioned and dated, so it was treated
as historical metadata, not relabeled as current. Outreach, external CI, and
the entire corpus remain outside this bounded review.

## Validation

- Initialization contained documentation only; no fresh regression was claimed.
- The required initial `python -m pytest tests/ -q` failed because the default
  interpreter lacks pytest. Missing test dependencies were restored in a
  session-isolated virtual environment, not in the shared system environment.
- Pre-correction `python -m pytest tests/ -q` with the isolated interpreter:
  **62,305 passed, 57 skipped, 66 deselected, 0 failed**, three warnings,
  850.80 seconds. This is tests-only, excludes slow tests, and is not a full
  repository regression. The retained log is `audit-baseline-tests.log`.
- Pre-correction `python -m pytest recycling/ "5-GOVERNANCE/Unitary Pentad/" -q`:
  **3,404 passed, 3 skipped, 0 failed** in 9.86 seconds. Log:
  `audit-governance-before.log`.
- `python COMPACTIFICATION/build_maps.py --check` initially reported stale
  `monorepo_map.json` because this audit added an indexed path. Regeneration
  with the existing builder restored equality; no inventory logic was changed.
- `python -m pytest COMPACTIFICATION/test_maps.py -q` in the isolated environment:
  **6 passed**.
- Pre-correction `python -m pytest tests/test_base44_live_status.py
  tests/test_status_drift_gate.py tests/test_bot_rag_index.py -q` in the isolated
  environment: **139 passed**, one dependency deprecation warning.
- `python TOOLS/audit/check_internal_links.py --root docs/audits`: **1 Markdown
  file checked; all internal file links resolved**.

Existing regression markers are historical evidence, not a fresh run.

## Corrections and independent checks

- C1-C3: narrowed blanket all-chain consistency prose, synchronized the current
  Truth Layer header with STATUS, and identified the Gatekeeper count as the
  historical Sprint CU receipt.
- R1-R3: labeled mixed-era inventories and regression expectations historical;
  corrected the alpha diagnostic's claimed derivation; prioritized Tier-1 and
  reassessment pointers; qualified assistant registry labels and legacy
  retrieval summaries. Historical formulas and receipts remain traceable.
- S1: live EXP-7 is `UNSUPPORTED`; physical cross-section/limit-ratio fields are
  unset and its old threshold is explicitly non-operative without a physical
  detector contract.
- S2: live EXP-5 and its mass field are unestablished, rather than selecting
  a spectrum or a new physical exclusion. A direct pre-correction execution of
  `src.core.pillar793_graviton_mass_bound_kk.kk_graviton_mass_tev(1)` returned
  **0.40304222059897743 TeV**, and `hllhc_verdict()` returned **FALSIFIED**,
  contradicting the module's supplied 1 TeV/PASS headline. This is a toy
  implementation contradiction, not evidence of physical falsification.
- S3-S4: compatibility text exposes historical scope; unavailable or missing
  regression counts remain JSON null, not zero failures. All-source failure
  logs an error. Known integer/string legacy counts retain numeric compatibility.
- S5: `--check` compares the actual artifact and rejects missing, malformed,
  or stale output. The existing drift workflow runs this check. Generator
  regressions no longer skip wholesale when FastAPI is absent.

An independent final-diff reviewer found two additional directly coupled
consumer defects. Both were corrected: the dashboard now preserves null/zero
counts and never substitutes hardcoded historic totals; the observatory
withdraws unsupported EXP-5/EXP-7 physical comparisons and calls its remaining
P787 routes historical simulations, not framework certificates.

A narrower frontend review verified nullable behavior and unsupported verdict
rendering, then caught a cross-origin/main-branch fallback introduced during
the repair. The dashboard retains its existing same-origin historical snapshot
fallback instead, with explicit provenance, failure logging, and tests asserting
the exact API/local URL sequence. The multi-underscore verdict badge was also
corrected. No external status service was introduced.

Triple checks comprise original-source comparison, executed regressions
(including real JavaScript, not merely a Python mirror), and independent
diff/consumer review. They are not independent scientific reproduction.

Post-correction focused command (isolated interpreter):

```bash
python -m pytest tests/test_base44_live_status.py tests/test_status_drift_gate.py tests/test_bot_rag_index.py tests/test_falsification_observatory.py COMPACTIFICATION/test_maps.py -q
```

Result: **201 passed, 0 failed**, one dependency deprecation warning, 6.13
seconds. Actual Node execution covers null/missing/zero counts, API failure with
successful local fallback, both sources failing, exact fallback URLs, and
unestablished mass/detector verdicts for multiple inputs.

Standalone checks:

- `python 9-INFRASTRUCTURE/generate_live_status.py --check`: **passed**, artifact
  matches generated status; historical counts unchanged.
- `python 9-INFRASTRUCTURE/check_status_drift.py`: **passed**.
- `python COMPACTIFICATION/build_maps.py --check`: **passed**.
- `node --check public-site/js/17-falsification-observatory.js`: **passed**.
- `python TOOLS/audit/check_internal_links.py --root docs`: **90 files checked,
  all internal file links resolved**.
- `python TOOLS/audit/check_internal_links.py --root 6-MONOGRAPH`: **13 files
  checked, all internal file links resolved**.
- `git diff --check`: **passed**.

Combined post-correction command, executed on frozen correction commit
`aa610235d4840440afc204d09ad56047ed36a257` with unchanged source/dependencies:

```bash
python -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q
```

Result: **65,732 passed, 60 skipped, 66 deselected, 0 failed**, three warnings,
797.27 seconds. Log: `audit-combined-after.log`. Warnings concern an existing
dataclass collection name, FastAPI's dependency deprecation, and an existing
test returning a dictionary. Optional integrations were skipped and default
slow deselections retained; product suites outside this command were not run.
This receipt does not replace the canonical historical regression marker or
certify all repository assets.

`python TOOLS/checks/check_canonical_ledger_sync.py --base-sha b47cf02 --head-sha aa610235d4840440afc204d09ad56047ed36a257`
also passed: canonical wave/pillar synchronization is not required for this
diff. The correction commit and evidence checkpoints are pushed to the draft
PR. Only this audit record is updated after the frozen regression; no tested
implementation is changed by recording the outcome.

## Remaining scope and next audit tranche

1. Reconcile P793's supplied headline, computed spectrum, physical inputs and
   exclusion function with the older Admission 10/P430 channel assumptions.
   Do not change toy constants or claim physical falsification to make labels
   agree. The live presentation is corrected; source physics remains open.
2. Trace remaining current-facing status consumers, including static flashcards,
   `physics-engine.js` historical datasets, HF spaces and deployment artifacts.
   Do not convert dated snapshots into live status or silently rewrite history.
3. Review formal theorem axiom dependencies and action-to-observable contracts
   with specialist evidence; this tranche did not certify every derivation.
4. Expand beyond assigned entrypoints to product/governance/editorial/archive
   provenance and registered-asset consistency, in bounded batches.
5. A true whole-repository, slow-inclusive certification requires its documented
   suite inventory, complete dependencies, frozen source/environment provenance,
   and complete supervised receipts. The combined pytest command below is not
   that certification.

## Resume procedure

Read this document and the draft PR, inspect the dedicated branch's latest
commit and worktree status, and resume the first incomplete review above.
Do not regenerate status totals, fingerprinted assets, or whole-repository
inventories without first identifying their canonical generators and gates.
Record reviewed scope, commands and outcomes, remaining scope, and blockers
before every pushed checkpoint.

Use the session artifact directory's `audit-venv/bin/python` for this
environment's exact test commands; it is not a repository dependency or a
portable environment guarantee. Artifacts and SQLite audit/task state are
session-persistent; this document and commits are the durable cross-session
record. `audit-environment.txt` records installed distributions. The combined
post-correction run is complete; resume the remaining scope above rather than
relabeling this first tranche a whole-repository all-clear.
