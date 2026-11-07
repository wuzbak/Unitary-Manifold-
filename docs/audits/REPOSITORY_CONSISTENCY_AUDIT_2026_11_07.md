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

Expert review completed on the checkpoint branch; these findings are awaiting
correction and independent regression review:

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
- The same tests-only command is running with that environment's interpreter;
  the retained log is `audit-baseline-tests.log` in the session artifact folder.
  It has no final result yet and is not a full repository regression.
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

## Resume procedure

Read this document and the draft PR, inspect the dedicated branch's latest
commit and worktree status, and resume the first incomplete review above.
Do not regenerate status totals, fingerprinted assets, or whole-repository
inventories without first identifying their canonical generators and gates.
Record reviewed scope, commands and outcomes, remaining scope, and blockers
before every pushed checkpoint.
