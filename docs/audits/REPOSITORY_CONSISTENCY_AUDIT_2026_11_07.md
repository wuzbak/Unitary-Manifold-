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

### Slow-inclusive frozen core regression

A later, frozen run used
`TOOLS/checks/run_supervised_pytest_batch.py --suite full-core`, with an exact
source/environment plan bound to audit checkpoint
`177f81116b90136c831b5d07a40ea5944a6d8699`. The plan covered 1,611 unique
core/governance test paths in 12 chunks, plus six shared-process integration
paths; it used two workers and marker expression `""` to include slow tests.
The source worktree digest was empty and remained unchanged through aggregate.

Exact aggregate receipt: **66,176 tests, 0 failures, 0 errors, 67 skipped**;
status `success`, `problems: []`, Python 3.12.3, Linux x86_64. Plan digest:
`78d148878382ab3da5f431081e762ea76377a618b19ee67741945badde85b1f7`.
Plan, chunk JUnit/JSON receipts and logs are retained in the session artifact
directory (`full-core-plan.json`, `full-core-results/`, `full-core-run.log`).
This is stronger evidence for its exact full-core selection, not all products,
claims, deploy targets, external integrations or scientific validity. It is
not the repository's historical 64,150 count and does not replace that receipt.

## Second-tranche findings — baseline `177f811`

These are reviewed, high-confidence status/provenance defects, not independent
physical verification. They are the next correction tranche:

| ID | Evidence | Finding and safe boundary |
|----|----------|---------------------------|
| S6 | `public-site/status/index.html:205-224`; `public-site/portal/library/index.html:287-309`; `hf-spaces/space_core/live_status.py:80-103`; `bot/assistant_api.py:268-279` | Pages and the HF adapter collapse explicit unavailable/null counts into historic values or zero failures. Preserve `null` as unknown and disclose the source/date; zero is a measured count, not missing evidence. |
| S7 | `.github/workflows/deploy-hf-spaces.yml:47-68`; `hf-spaces/axiom-apps/app.py:51-70` and other space imports | Isolated per-app deployment uploads omit the shared `space_core` package used by multiple apps, causing imports to fall through to `vunknown`/zero. Reproduce package layout before changing the deploy contract. |
| S8 | `public-site/status/index.html:95,124,162-164`; `public-site/apps/verification-dashboard.html:124-138`; `public-site/js/physics-engine.js:284`; `hf-spaces/unitary-manifold-showcase/app.py:109`; `hf-spaces/axiomzero-portal/app.py:78` | Current-facing prose still asserts blanket internal consistency, P8 functional closure, or a universal CMB suppression floor, despite `docs/TRUTH_LAYER.md:39-55,851-856` and the qualified API contract. Keep historical catalog facts but withdraw current all-clear wording. |
| S9 | `public-site/js/physics-engine.js:239-265,294,299`; `public-site/apps/desi-tracker.html:115-134`; `hf-spaces/az-tools/app.py:526-532,566-588`; `um_live_status.json:275-316` | DESI falsification thresholds differ by consumer; old engine/HF paths still make operative tensor/graviton/dark-matter assertions inconsistent with current canonical records. Do not invent new thresholds; keep dated observations labeled by dataset and use canonical statuses. |
| S10 | `firebase.json:3,39-40`; `public-site/status/index.html:205-206`; `public-site/portal/library/index.html:305-308`; `DEPLOY.md:172-174` | Firebase is a static SPA with no `/api/status` rewrite, while pages call same-origin `/api/status` then silently use checked-in snapshots. Confirm the deployment contract before adding a backend rewrite; otherwise show a dated snapshot explicitly. Hosted behavior was not probed. |
| F1 | `src/core/pillar793_graviton_mass_bound_kk.py:20-23,41-49,112-125`; P790 source; `docs/TRUTH_LAYER.md:245-247` | P793 presents 1 TeV as from P790, although P790's calculated first mode is 24.622 GeV and 1 TeV is a separate supplied benchmark; P793's own formula on 1 TeV returns ≈0.403 TeV. Source/input/arithmetic inconsistency, not a physical mass determination. |
| F2 | `src/core/pillar793_graviton_mass_bound_kk.py:13-23,64-75,153-167`; `tests/test_pillar793_graviton_mass_bound_kk.py:198-212`; `docs/CLAIM_MASTER_BOARD.md:477,483` | P793's <4 TeV exclusion, 0.8 TeV threshold verdict helper, and explicit-input PASS tests disagree; the default computed value routes FALSIFIED. P430/Admission 10 is a separate channel-specific tension/≥5 TeV bound. No common model/coupling/channel premise is established. Do not infer physical falsification or choose a spectrum to reconcile them. |
| F3 | `docs/TRUTH_LAYER.md:973-985`; `STATUS.md:3-16`; P1135 source | “Open and untouched” obscures P1135's certified restricted subcase while the general physical-time residual remains open. Clarify subcase versus framework-level obligation; do not broaden P1135's certificate. |
| R4 | `bot/assistant_api.py:147-166,364-375` | `retrieve_context()` always appends static PREDICTIONS/FALLIBILITY text with DESI Y1, the older r bound, and stale Higgs labels despite the new boundary and current status feed. Local RAG queries reproduce stale text. Replace with dynamic qualified status or a pointer-only summary and assert retrieved output. |
| I1 | `12-AZ-IP/README.md:18-63,65-82`; `12-AZ-IP/PORTFOLIO_LICENSE_SCHEDULE.md:17-18,42-43`; `12-AZ-IP/IP_REGISTRY.json:3718-4167`; `12-AZ-IP/FINGERPRINT_MANIFEST.md:6-12,81-89,1049` | README/license schedule declare 46 canonical products/surfaces; JSON has 44 entries. Products 24 and 25 are absent (08–15 are not catalog rows). Product 24 has 26 fingerprinted assets but no product metadata; Product 25 has neither a product record nor asset fingerprints/history. This is a real catalog sync defect, but the manifest describes steward-governed registration, not automatic directory inclusion. Do not autonomously choose Product 25's fingerprint set or add registry entries without steward approval. |
| I2 | `src/core/pillar536_axiomzero_ip_registry.py:232-266`; `tests/test_pillar536_axiomzero_ip_registry.py:378-382`; registry asset entries | Verifier reported `all_verified=True` for 8 of 10 `IP_ASSET_CLASSES` paths; two were not in the JSON assets map, which contains 194 entries. It also did not disclose that this was not registry-wide coverage. Corrected below: scope and unregistered count are explicit, and `all_verified` now requires every scoped path to be registered and verified. |

Inventory expert checks passed for `COMPACTIFICATION/build_maps.py --check`,
Product 45 catalog `--check` (46 products), and Product 46 copy `--check`.
Fingerprint manifests were not regenerated; historical snapshot differences
were not presumed stale.

### Second-tranche corrections and validation

- **S6-S10:** Public status pages now use explicitly dated bundled snapshots
  rather than a nonexistent Firebase `/api/status`; null/invalid values display
  as unavailable while zero remains a real count. The HF loader preserves
  source/date and null counts; each Space and shared package are staged and
  uploaded together as one revision. Current DESI/physics summaries no longer
  apply a single-scalar falsification threshold or stale closure labels.
- **F1-F2:** P793 now calls the 1 TeV input a separately supplied benchmark,
  reports the calculation's ≈0.403 TeV output as illustrative, and retires the
  mass-only detector verdict. The verdict API returns
  `MODEL_DEPENDENT_UNESTABLISHED` for all mass inputs. No physical spectrum,
  coupling, or detector-channel contract was inferred.
- **F3:** Truth Layer wording distinguishes P1135's restricted certificate
  from the still-open broader obligation.
- **R4:** Assistant retrieval renders dated generator-backed prediction rows;
  if unavailable it emits only a canonical pointer, not stale hard-coded
  DESI-Y1, tensor-bound, or Higgs labels.
- **I2:** Pillar 536 now states its 10-path scope, counts paths missing from
  the registry, and reports `all_verified` only when all scoped paths are
  registered and match. Current result: 8 verified, 2 not registered,
  0 missing, 0 tampered, `all_verified: false`. This is not a check of all 194
  JSON registry assets.

Combined focused command, using the session-isolated interpreter:

```bash
/root/.copilot/session-state/776568fa3fb942f2bc5d5ee3af49a04d/files/audit-venv/bin/python -m pytest -p no:cacheprovider tests/test_pillar536_axiomzero_ip_registry.py tests/test_status_consumer_audit.py tests/test_pillar793_graviton_mass_bound_kk.py tests/test_bot_assistant_api.py tests/test_hf_spaces_canary.py -q
```

Result: **177 passed, 0 failed**, one existing Starlette/httpx deprecation
warning, under 2 seconds. This includes HF canary YAML and mocked-transport
checks; it does not probe hosted Spaces. This is targeted validation after
the second-tranche source changes; the earlier slow-inclusive full-core
receipt predates these edits and does not certify them. The independent diff
review found no significant issues; that reviewer's environment lacked pytest.

HF live deployment behavior was not probed. Product 24/25 registry metadata
remains unresolved; no product records or asset fingerprints were added. The
audit has not certified external behavior or registry-wide fingerprint
completeness.

### Formal action-to-evolution slice — P1130-P1135

The bounded review found no current status contradiction within this chain:

- P1130 promotes the Euler-Lagrange field-equation deliverable only within its
  stated static perimeter; its t-relaxation law and framework-level
  physical-time evolution remain open.
- P1131 closes the exact non-diagonal reduction identity. It removes that
  obligation from the current contract while preserving P1130's historical
  three-item record.
- P1132 explicitly withdraws its earlier hyperbolic/physical propagation
  interpretation. Its current source and regression test limit the result to
  off-shell acceleration and static identities; the current Truth Layer and
  planar technical note identify the supersession.
- P1135 certifies a separate restricted massless, zero-vector, transversely
  isotropic coordinate-time sector through the existing symbolic/numerical
  acceptance report. It leaves both broader P1130 obligations open and
  disclaims global well-posedness and empirical confirmation.
- No P1130-P1135 Lean source was found in the bounded Lean path search. Their
  source/docs identify the evidence as executable Python/SymPy/numerical
  checks, not a Lean proof; no formal-verification claim was inferred.

Slow-inclusive focused command:

```bash
/root/.copilot/session-state/776568fa3fb942f2bc5d5ee3af49a04d/files/audit-venv/bin/python -m pytest -p no:cacheprovider tests/test_pillar1130_action_derived_flow_steward_promotion.py tests/test_pillar1131_offdiagonal_exact_reduction_closure.py tests/test_pillar1132_adm_homogeneous_hyperbolic_evolution.py tests/test_pillar1133_superfluid_effective_theory.py tests/test_pillar1134_rare_decay_probes.py tests/test_pillar1135_planar_radion_physical_time_certification.py tests/test_action_to_evolution_contract.py tests/test_planar_radion_acceptance.py -q -m ""
```

Result: **113 passed, 0 failed** in 53.43 seconds. This validates the
repository's scoped executable contracts, not the underlying physics or any
Lean proof. No source correction was justified in this bounded slice.

## Merge-blocker repair checkpoint

The checks at `b846a8a86cec7ab97d0cfc73eb6e4b5353f78e4b`
are **not merge-ready**. Failed job logs establish three distinct causes:

- CI run `42422494650` and the Tests compactified preflight stop on
  `Stale maps: monorepo_map.json`. The canonical map omitted the newly tracked
  public status helper and status-consumer regression test.
- Tests run `42422494820` fails the explicit UM-ARTS inventory coverage
  assertion because `tests/test_status_consumer_audit.py` is not selected in
  the repository execution config. Coverage reports **1 failed, 66,241
  passed, 36 skipped**; fast shard 3 reports **1 failed, 14,615 passed,
  33 skipped, 20 deselected**. The supervisors correctly reject the incomplete
  validation; they must not be bypassed.
- Windows CPU-backend run `42422494759` cancels the streamed model read
  exactly 15 minutes after fetching begins. This is download cancellation,
  not evidence that the model passed or failed qualification.

The map was regenerated with `python COMPACTIFICATION/build_maps.py`.
The UM-ARTS config was synchronized surgically with discovery, preserving
existing reviewed selections rather than replacing them with a new inventory.
The Windows downloader now has one shared 30-minute budget inside a 35-minute
fetch step, 60-second header/read idle cancellation, and at most three
transient-only attempts. Retries restart from the pinned publisher and remove
only their own incomplete destination. Redirects retain the approved HTTPS
host checks and additionally reject nonstandard ports and user information.
Byte caps, LFS SHA-256, provenance, and mandatory acceptance remain unchanged.
The workflow runs the new `.github/tests/` contract/runtime fixture explicitly;
it is not inserted into the unrelated Python core execution suite.

Local validation used the preserved audit environment:

- Inventory/map/status-consumer focused tests: **34 passed**.
- `python TOOLS/checks/check_licensing_policy.py`: structural evidence checks
  passed; explicitly not legal certification.
- `python COMPACTIFICATION/build_maps.py --check`: passed.
- The exact platform-smoke pytest selection from `.github/workflows/ci.yml`
  (licensing, metric, file-size, HF failure aggregation, integer claim, and
  selected Navigator compatibility/training tests): **135 passed** in 86.84s.
  This is local Linux evidence, not hosted macOS or Windows certification.
- `python TOOLS/checks/run_supervised_pytest_batch.py --suite compactified-preflight`:
  **89 passed** in 32.65s.
- `python TOOLS/checks/run_supervised_pytest_batch.py --suite integration-preflight`:
  **318 passed** in 40.39s.
- `python -m pytest recycling/ "5-GOVERNANCE/Unitary Pentad/" -q`:
  **3,404 passed, 3 skipped** in 7.99s.
- `PWSH_EXE=<session PowerShell>/pwsh python -m unittest discover -s .github/tests -p test_embedded_model_download_contract.py -q`:
  **5 tests passed**, including 17 extracted PowerShell transport scenarios,
  in 13.807s. The first local attempt failed explicitly because PowerShell was
  absent. The rerun used session-only PowerShell 7.5.4, downloaded from its
  official release and SHA-256 checked against the publisher's manifest.
  Fixtures exercise progress, transient retries, idle/shared deadlines,
  redirect guards, sizes, and cleanup without external network requests.
- `python -m unittest discover -s 12-AZ-IP/43-az-geometric-tori-transformer/tests -p test_candidate_engine.py -q`:
  **70 tests passed**. Intentional negative-fixture FAIL output is not a
  production candidate evaluation.
- `node --test 12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs`:
  **87 passed, 0 failed**.

These receipts address the identified blockers locally. They do not replace
latest-head CI, coverage, mutation, or slow-inclusive full-core gates.
Extracted Linux PowerShell fixtures do not establish hosted Windows networking,
multi-GB throughput, or actual model qualification.
The PR remains draft until required checks pass at the repaired commit.

## Remaining scope

1. Obtain steward direction for Product 24/25 catalog reconciliation and define
   the Product 25 fingerprint set before changing registry metadata/assets.
2. Audit additional frontend/HF/product status paths and verify deploy-time
   behavior with repository tests; hosted deployment is not verified.
3. Review formal theorem axiom dependencies and action-to-observable contracts
   outside the reviewed P1130-P1135 slice.
4. Expand product/governance/editorial/archive provenance and registered-asset
   checks in bounded batches.
5. The slow-inclusive supervised result above covers the specified core suite,
   not a complete all-products, `claims/`, deployment, hosted-service, or
   independent scientific certification.

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
