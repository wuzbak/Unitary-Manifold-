# TOOLS — Calculators, Verification Entrypoints, and Maintenance Utilities

This folder is the navigation hub for executable tools, calculators, notebooks, and repository-maintenance utilities.

Some stable entrypoints intentionally remain at the repository root for compatibility with existing docs, badges, notebooks, and external users. They are indexed here so humans and AI agents can find them quickly without breaking established commands.

## Fast verification

| Tool | Path | Use |
|------|------|-----|
| Formal verification script | [`../VERIFY.py`](../VERIFY.py) | Fast observable consistency check used by the README quick start. |
| Isolated proof verifier | [`../proof/VERIFY.py`](../proof/VERIFY.py) | Minimal proof-surface copy for formal review. |
| Algebra proof test/script | [`../ALGEBRA_PROOF.py`](../ALGEBRA_PROOF.py) | Root compatibility entrypoint included by pytest discovery. |
| Proof-surface algebra script | [`../proof/ALGEBRA_PROOF.py`](../proof/ALGEBRA_PROOF.py) | Isolated proof-surface algebra checks. |

## Audit and maintenance tools

| Tool | Path | Use |
|------|------|-----|
| Audit tools | [`../AUDIT_TOOLS.py`](../AUDIT_TOOLS.py) | Repository audit helper retained at root for compatibility. |
| Link checker | [`audit/check_internal_links.py`](audit/check_internal_links.py) | Checks Markdown file links for missing internal targets. |
| Large-directory guard | [`checks/check_large_directories.py`](checks/check_large_directories.py) | Enforces per-directory tracked-entry limits to prevent GitHub 1,000-entry UI truncation risk from growing. |
| Number updater | [`../9-INFRASTRUCTURE/update_numbers.sh`](../9-INFRASTRUCTURE/update_numbers.sh) | Version/count update utility. |
| Archive creator | [`../9-INFRASTRUCTURE/scripts/create_archive.py`](../9-INFRASTRUCTURE/scripts/create_archive.py) | Archive helper script. |

## Calculators and pillar tools

| Tool area | Path | Use |
|-----------|------|-----|
| PCCRE calculator | [`../src/core/pillar242_planetary_coherence_cascade_resilience_engine.py`](../src/core/pillar242_planetary_coherence_cascade_resilience_engine.py) | Pillar 242 executable physics module (calculator docs integrated in module). |
| USIVF calculator | [`../src/core/pillar243_unified_scientific_interoperability_validation_fabric.py`](../src/core/pillar243_unified_scientific_interoperability_validation_fabric.py) | Pillar 243 executable physics module (calculator docs integrated in module). |
| Core Python calculators | [`../src/core/`](../src/core/) | Main executable physics/audit modules. |
| Omega synthesis | [`../5-GOVERNANCE/Unitary Pentad/omega/omega_synthesis.py`](../5-GOVERNANCE/Unitary%20Pentad/omega/omega_synthesis.py) | Governance/summary calculator surface. |

## Notebooks and demos

| Tool | Path | Use |
|------|------|-----|
| Root demo notebook | [`../demo.ipynb`](../demo.ipynb) | Fast interactive repository demonstration. |
| Infrastructure notebooks | [`../9-INFRASTRUCTURE/notebooks/`](../9-INFRASTRUCTURE/notebooks/) | Quickstart, holographic boundary, and FTUM notebooks. |

## Rule

If a tool is a public or tested entrypoint, keep a compatibility path or wrapper when moving it. Do not move root verification scripts without updating README, AGENTS, tests, notebooks, and external-facing docs in the same PR.

## UM-ARTS — regression evidence application

UM-ARTS is canonical AZ-IP **Product 26**, living in
[`../12-AZ-IP/26-um-arts/`](../12-AZ-IP/26-um-arts/), outside the physics implementation.
`TOOLS.um_arts` is a thin compatibility namespace; existing CLI and pytest-plugin
imports remain supported. The canonical launcher is
`python 12-AZ-IP/26-um-arts/run.py --help` from the repository root. It
orchestrates existing checks and preserves their evidence; it does not generate
new physics certificates, decide merges, or promote scientific claims. Its
repository adapter uses the existing supervised suite planner and formal
traceability contracts rather than a second pillar or theorem registry.

### Canonical product installation and operational application

Technology readiness has **not been assessed**. Python 3.12+ on Linux or macOS is
required: execution/recovery uses Unix `fcntl` locking and POSIX process groups
for bounded cleanup; native Windows is not supported. The application uses the standard
library; executing Python suites requires the existing pytest installation, and
Lean capture requires the existing Lean/lake toolchain. No extra runtime
dependencies are introduced.

The product release is **1.0.0** in packaging and the registry. The preserved
`VERSION = "1"` constant identifies evidence schema compatibility; the legacy
CLI `--version` displays that schema version, not a newer product release.

From the repository root:

```bash
python 12-AZ-IP/26-um-arts/run.py --help
python 12-AZ-IP/26-um-arts/run.py serve \
  --root "$PWD" --store "$PWD/.um-arts" --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`. The server only accepts loopback hosts; it is not
a remotely hosted service. `--config`, `--adapter`, and `--mode` select the same
trusted execution settings as the planner. Keep the ignored `.um-arts/` store.
The operational API exposes health/preflight inspection and supervised plan,
run, and resume tasks. Run/resume requests use server-issued identifiers, not
arbitrary paths. Mutations require a per-session token and same-site
Host/Origin/fetch checks. Local browser access is not permission to execute
unreviewed repository code; use only trusted source and execution configuration.
API clients obtain the session token from `/api/session` and send it in
`X-UM-ARTS-Token` for mutations.

Task loading, state persistence, execution, and log writes share one guarded
lifecycle. Transient I/O failures block the affected task without stranding
later tasks. If a terminal task result cannot be persisted, new submissions are
disabled and preflight reports the queue error; the failed task remains visible
in memory until the server stops. Restart never upgrades interrupted tasks to
passes.

From the product directory, `python -m um_arts --help` is equivalent. For an
editable installation using standard pip/setuptools:

```bash
python -m pip install --no-deps -e 12-AZ-IP/26-um-arts
um-arts --help
```

The distribution contains only the product package and its bundled assets, not
the physics repository. The legacy `TOOLS` namespace is available in repository
checkouts; installed distributions use `um_arts` and `um_arts.pytest_plugin`.
Plugin loading is explicit (`pytest -p um_arts.pytest_plugin`), never automatic.
Trusted adapter examples are bundled under
[`../12-AZ-IP/26-um-arts/um_arts/examples/`](../12-AZ-IP/26-um-arts/um_arts/examples/).
The bundled `repository.json` is a compact **review-required** starting
configuration, not a complete coverage certificate. Review current inventory
exclusions, unclassified/uncovered files, and local optional dependencies before
execution; missing dependencies may skip or block their affected checks.

### Capturing existing checks

Run from the repository root with Python 3.12 or newer on a POSIX runner
(the executor uses process groups for bounded cleanup):

```bash
python -m TOOLS.um_arts --help
python -m TOOLS.um_arts plan --root "$PWD" --store "$PWD/.um-arts" --mode full
python TOOLS/checks/run_supervised_pytest_batch.py \
  --suite compactified-preflight --evidence-dir "$PWD/.um-arts/preflight"
python TOOLS/checks/run_supervised_pytest_batch.py \
  --suite full-core --batch-count 8 --batch-index 0 \
  --evidence-dir "$PWD/.um-arts/core-0"
python -m TOOLS.um_arts capture --repo "$PWD" \
  --output "$PWD/.um-arts/verify" --timeout 60 -- python proof/VERIFY.py
```

The planner prints the sealed plan path in its JSON result. Pass that absolute
path to `run --plan PATH`; use the resulting attempt path with
`verify --attempt PATH`, `report --attempt PATH`, or
`dashboard --attempt PATH --output .um-arts-dashboard.html`.
Resume with `resume --attempt PATH`. Reports and dashboards must be written
outside immutable evidence bundles. A previous attempt can be supplied with
`report --attempt PATH --baseline BASELINE_PATH`; incompatible baselines cannot
support a regression comparison.

For another repository, use `plan --adapter generic --root /absolute/repo
--store /absolute/evidence --config /absolute/adapter.json`. The trusted JSON
configuration declares uniquely named suites with repository-relative `paths`,
optional `requires` dependencies, and a `serial` flag, plus bounded `workers`
and `timeout_seconds`. A minimal configuration is:

```json
{
  "adapter": "generic",
  "workers": 2,
  "timeout_seconds": 600,
  "suites": [{"name": "unit", "paths": ["tests"], "serial": false}]
}
```

The generic adapter does not inherit UM constants, pillar labels, or formal
claims. Changes mode conservatively falls back to the declared suite scope
until there is a sound change-dependency mapping; it never infers safety from
filenames alone.

The evidence option is opt-in on the existing supervised runner; its legacy
invocation remains available. Captured pytest commands disable nested xdist
workers so that the evidence collector has one authoritative stream per
process. CI retains its existing independent fast-suite shards.
The capture wrapper records the original and effective execution settings;
capturing one shard is not an aggregate certification of other shards.

The existing Tests and Lean workflows preserve UM-ARTS artifacts with
`if: always()` even when a check fails. They do not add another overlapping
full-suite execution. GitHub's shard-outcome gate remains distinct from an
independently verified, compatible full-run evidence bundle.

### Scope and verdicts

Change feedback, integration validation, and full certification are different
scopes. A successful focused run must not be published as a full-repository
baseline. The default UM scope covers the tests, recycling, and Pentad roots. Claims,
isolated executable proof checks, Lean builds, and product-specific suites
require explicitly configured or captured checks; “full” means the adapter's
disclosed scope, not every repository check. The orchestration adapter currently
inherits configured pytest filters; use `"pytest_args": ["-m", ""]` to include
slow tests. This differs from the corrected supervised full-core runner.

The supervised full-core runner now explicitly overrides pytest's default
`not slow` marker filter with an empty marker expression. Its existing
supervisor still verifies file partitioning only. Test-execution completeness
requires collected identities and terminal outcomes, not a matching number of
files or a line in pytest's console summary.

### Evidence and trust boundaries

Keep local evidence under the ignored `.um-arts/` directory or another output
directory outside tracked source. Preserve run manifests, collection reports,
attempt logs, receipts, and the SQLite index together. Interrupted or timed-out
attempts are not passes. Resume must reject incompatible source, environment,
or execution settings rather than combine unrelated totals.

Each completed orchestration job now has an independently sealed checkpoint
with its exact job identity and before/after compatibility fingerprints.
The attempt identity is persisted before execution. After a coordinator is
hard-killed, `report` exposes an **incomplete** attempt, and `resume` creates a
new attempt reusing only compatible, validated checkpoints. Missing, corrupt,
unfinished, or source-unstable checkpoints must rerun. An unsealed attempt never
certifies a baseline and cannot be imported as completed evidence.

A runner lock prevents simultaneous recovery or recovery of an active
coordinator. A hard kill cannot clean up independent child process groups:
terminate orphaned workers before recovery. Preserve the original attempt;
recovery never repairs or rewrites its receipts. A partially written final
attempt seal is rejected rather than silently downgraded to recoverable evidence.
To avoid overrunning a caller's session, `run --max-jobs N` and
`resume --max-jobs N` execute at most N new pytest jobs per invocation.
Verified compatible successes are copied without spending this budget.
The limit is invocation metadata, not a change to the frozen plan or its settings,
so subsequent invocations may choose another limit. Each slice seals its attempt
and records `execution_budget.json`; deferred or missing identities remain
**blocked**, not passing. Dependent suites wait for their prerequisites, and
requested Lean work waits until no eligible pytest jobs are deferred.
Use the existing per-job timeout and worker count to choose a manageable slice;
this is not a wall-clock deadline and cannot bound planning, hashing, copying or
a later Lean build. Across currently eligible suites, never-attempted jobs take priority
over retries, with attempted-job history carried across slices. Failed jobs
remain blocked and are retried after fresh work; retries count toward the limit.
Inherited history and per-suite dispatch receipts are written before workers
start, so hard-kill recovery does not depend solely on finalization. Dispatch
history guides scheduling only; it never counts as completed test evidence.

```bash
python -m TOOLS.um_arts run --plan /absolute/store/plans/ID/plan.json --max-jobs 4
python -m TOOLS.um_arts resume --attempt /absolute/store/attempts/ID --max-jobs 4
```

The local dashboard now exposes the same new-job budget, defaulting to one
job per run/resume click. It persists the requested budget with the queued task
and forwards it unchanged to the engine; it cannot change the frozen plan.
The authenticated task API accepts an optional positive integer `max_jobs`
for run/resume only. Omitting it preserves the existing unlimited API behavior.
Planning does not accept this option. A completed resume executes zero jobs;
a partially covered slice remains blocked even when every dispatched job passes.

Legacy sealed attempts remain readable; source-unstable attempts cannot be
reused merely by restoring their original inputs. Legacy jobs without independent
checkpoints are rerun when resuming into the checkpoint-aware format.
The tracker's ignored `.um-arts-test-work/` fixture directory is excluded from
source fingerprints so parallel tracker tests do not invalidate one another's
checkpoints. Ordinary test inputs and datasets remain fingerprinted.
For large discovery passes, trusted execution configs may set
`collection_timeout_seconds` independently of `timeout_seconds`. For example,
600 seconds for initial suite collection can coexist with 120-second execution
jobs and `files_per_job: 32`. Omission preserves the existing shared timeout;
both budgets must be finite, positive and at most 86,400 seconds. Changing an
explicit budget changes settings compatibility and requires a fresh plan.
Execution timeouts include each job's own imports/collection. A timeout or
missing receipt still blocks coverage; a larger collection budget never
turns unfinished tests into passes.
Keep downloaded compilers, scanner binaries, dependency archives and analysis
databases outside the checkout (for example, in an external temporary directory).
The legacy `.um-arts-completion/` and `.lean-library-check/` provisioning directories are explicitly
Git-ignored and excluded from source fingerprints and snapshots. A previous
agent run aborted with `stdout maxBuffer length exceeded` while Git enumerated
an unpacked Lean toolchain in each location in separate failed runs. These exact directories are reserved for generated
tooling, never source or tests; ordinary `.um-arts-*` directories are not broadly
excluded from fingerprints. Tool/environment identities remain separate
compatibility inputs. Git ignore rules do not seal artifacts, certify checks,
or provide durable storage. Preserve sealed receipts externally before a
sandbox ends, and never infer successful execution from a saved summary.
When pytest completion evidence is missing or malformed, reports retain any
explicit timeout, launch/interruption or nonzero-exit diagnosis from the process
receipt. Such jobs remain blocked with no inferred test counts or reusable
success; partial log output is not reconstructed into passing evidence.
Source aliases such as this repository's `az-os` and `az-kernel` are recorded
with both their link text and resolved in-repository target. Canonical target
contents remain fingerprinted once, without recursively following directory
aliases. Retargeting an alias invalidates compatibility even when both targets
have identical bytes. External, dangling, cyclic, excluded-cache, and artifact
store targets are rejected. This source policy does not relax the prohibition
on symlinks inside imported evidence bundles.
Nonexcluded directories, including empty ones, are source inputs too: adding or
removing a required directory invalidates compatibility. Generated pytest
benchmark caches (`.benchmarks/`) are explicitly excluded alongside other
disclosed caches. Git metadata is excluded whether `.git` is a directory or a
worktree/submodule pointer file; snapshots never copy pointers to the original
repository's index.

Integration mode and automatic change-impact selection are not yet implemented.
Collection-only captured pytest commands are labeled `collection_passed`, not
test execution, and never satisfy `test_gate`. Reasonless unexpected xfail
successes are blocked just like other XPASS outcomes.

Artifact hashes detect corruption and inconsistent bundles; they are not a
cryptographic attestation that an untrusted author executed the checks.
Run only reviewed repository code and trusted execution configurations.
Downloaded evidence is data, not permission to execute its commands. PsiCat
may explain reports and prepare review packets, but cannot waive gates or
manufacture evidence.

Captured command output is retained verbatim. Do not print credentials or
private data in checks, and review artifacts before publishing them. CI uploads
only the explicitly selected evidence directories; it does not grant PR code
additional secrets or write permissions.

### Formal interpretation

The existing `src/core/formal_traceability_spine.py`,
`src/core/formal_bridge_schema.py`, and `src/core/lean_python_bridge_ir.py`
remain the mapping and normalization authorities. Missing exact declarations,
unavailable checking tools, and unresolved correspondence must stay visible.
A Lean build is distinct from a checked declaration with disclosed axioms;
neither establishes that a Python implementation is mathematically equivalent.
Executable checks do not establish empirical confirmation of the framework.

### Repository inventory and bounded assistance

Inventory statically discovers canonical suite candidates across the repository,
including product, claim, proof, and other Python execution lanes. It separately
discloses excluded mirrors, unclassified/uncovered candidates, unselected suites,
and Lean projects. This is a **review-required inventory**, not executed coverage.

```bash
python 12-AZ-IP/26-um-arts/run.py inventory --root "$PWD" \
  --output .um-arts/inventory.json --config-output .um-arts/repository.json
python 12-AZ-IP/26-um-arts/run.py plan --root "$PWD" \
  --store .um-arts --adapter um --config .um-arts/repository.json
python 12-AZ-IP/26-um-arts/run.py assist --root "$PWD" \
  --query "collection evidence scope" --paths TOOLS/README.md proof/README.md
```

Review the generated trusted configuration before planning/execution. Repeated
`--suite NAME` options restrict config generation; `--lean-project PATH` explicitly
selects one discovered Lean project. Neither option executes it during inventory.
Generated configs request `-m ''` to include slow tests; real skips still apply.
Inventory and assistance outputs are created exclusively, never overwritten.
Generated configurations retain the UM adapter when its canonical formal
traceability spine is discovered, preserving formal registry capture; other
repositories use the generic adapter. Use the adapter disclosed in the config.

The Python APIs are also available after installation or from the product
directory:

```python
from pathlib import Path
from um_arts.inventory import discover_inventory, execution_config, selection_boundary

repo = Path("/absolute/repository")
inventory = discover_inventory(repo)
# Review exclusions, uncovered/unclassified files, and collection policy first.
config = execution_config(inventory, lean_project="lean4")
boundary = selection_boundary(inventory, lean_project="lean4")
```

Select `lean4` only when it is a discovered project. Serialize the reviewed
configuration into a JSON file, then pass that file to the engine planner;
planning and running execute trusted repository code, unlike static inventory.
Known Product 05/06/07 mirrors are excluded only when content-equal to their
canonical Pentad/root test copies; unique product files remain disclosed.

`assist --attempt PATH` explains checked attempt evidence; `assist --report PATH`
explains caller-supplied JSON without upgrading its trust. Optional `--output PATH`
saves the packet. Assistance returns bounded source excerpts with citations and
review guidance, not automatic edits, gate changes, or external model calls.
Command exit zero means retrieval/inventory succeeded, **not** that tests passed.
Programmatic assistance uses `retrieve_context(repo, query, paths=[...])` and
`diagnostic_packet(repo, reporting.report(attempt), query)` from
`um_arts.assistance`. Citations carry exact path/line ranges and read-prefix
SHA-256 provenance. Only the existing bot `DocumentChunk.score` utility is
optionally reused, with an explicit deterministic fallback; PsiCat runtime
state/training-linked engines are not imported or invoked by this read-only lane.

### Lean build boundaries

The `UM-ARTS Full Core Evidence` workflow runs independently of the cloud
agent's session limit. It collects a frozen plan for `tests/`, `recycling/`
and canonical Pentad with `-m ''`, uses 32-file physics checkpoints and
independent suites, and requires reconciled terminal outcomes before passing.
Larger bounded checkpoints amortize repeated interpreter imports and pure
symbolic caches; they do not change the selected identities. Main pushes,
`copilot/um-arts-*` development pushes, pull requests and manual dispatch start
this lane. Full Git history is available for audit tests that inspect commits.
It is not a claim that product, claims, or every other discovered monorepo
suite was executed. Inspect the inventory for those additional lanes.
The workflow preserves complete plans and job checkpoints with `always()`
uploads and 90-day retention; it does not cancel an older run when a new
commit arrives. An overall execution timeout leaves incomplete coverage,
not a pass. Download artifacts before their retention expires. Cross-run
resume still requires exact source/environment/settings compatibility;
an artifact download does not authorize automatic execution.

Full Python CodeQL now has an independent hosted job without changed-path
selection or product/test exclusions. Only agent instruction files are
excluded. It preserves SARIF separately from sliced analysis; the local
validation wrapper's database-size skip is never counted as this job's pass.
Lean supports manual workflow dispatch too. Mathlib cache retrieval is
captured with a 600-second limit after the independent exporter and numerical
checks. A failed download remains a failed captured command, while explicit
`continue-on-error` permits the mandatory source build without the cache.
The full library build still fails closed. Hosted workflow configuration is not execution
evidence; actual results must be read for the tested commit.

Selecting a discovered Lean project requests its full default build; the
canonical Lean project now includes the actual `UnitaryManifold` library as a
default target. An exporter executable build or passing exporter adapter tests
is **not** a full formal-library build. Record exporter, scoped inspection, and
full-library outcomes separately. Missing dependencies or unavailable Mathlib
caches leave affected builds incomplete/blocked, never certified passes.
The Lean workflow explicitly builds `um_arts_export` and runs its real compiler
integration tests with the pinned toolchain before the full-library build, so
a slow or failing library build cannot suppress these independent receipts.
NumericalChecks also runs before the full library. Local static-source tests and
skipped integration tests are not substitutes for this execution gate.
Even a successful full Lean build does not substitute for declaration-level
inspection with disclosed axioms or prove Python↔Lean correspondence.

### Explicit multi-check manifests

`certify --manifest PATH` reads and reconciles an explicitly disclosed manifest
without executing its commands:

```bash
python 12-AZ-IP/26-um-arts/run.py certify --manifest .um-arts/required-checks.json
```

Example `.um-arts/required-checks.json`, after separately capturing the named
checks against the same frozen source/environment:

```json
{
  "label": "Focused metric tests and isolated executable proof check",
  "checks": [
    {
      "id": "metric",
      "artifact": "metric-capture",
      "command": ["python", "-m", "pytest", "tests/test_metric.py", "-q"],
      "kind": "pytest",
      "scope": "Metric file only, with its recorded collection filters"
    },
    {
      "id": "proof",
      "artifact": "proof-capture",
      "command": ["python", "proof/VERIFY.py"],
      "kind": "command",
      "scope": "Isolated executable proof check, not the Lean library"
    }
  ]
}
```

Artifact paths are relative to the manifest directory. Use exactly the original
argument list recorded by each capture, including its executable spelling;
the example commands must not be substituted for different captured commands.
The manifest has exactly `label` and `checks`; each check has exactly the five
fields shown. Pytest identities across checks must be disjoint.

Each named check declares its artifact, exact command, execution kind, and scope;
the manifest labels the aggregate. Receipts must agree on source, environment,
engine, Git identity, and root. Collection-only receipts cannot substitute for
executed pytest checks; command receipts remain separate from test execution.
Duplicate test identities across split jobs are rejected. Compatible proof/Lean
command captures may be required alongside Python receipts, but their scope
must remain explicit. A passing aggregate certifies **only the manifest's
disclosed checks**, never an automatic full-repository badge or theorem claim.

### Explicit source snapshots

Use `snapshot` when tests must run against a separate source copy rather than
your live checkout:

```bash
python 12-AZ-IP/26-um-arts/run.py snapshot --root "$PWD" \
  --output /tmp/um-arts-source-snapshot
python 12-AZ-IP/26-um-arts/run.py plan \
  --root /tmp/um-arts-source-snapshot/source \
  --store "$PWD/.um-arts/snapshot-evidence" --mode full
```

A successful `snapshot_ready` result identifies `source_root` and `snapshot_root`
and records original/copy fingerprints. Review the copy before executing trusted
checks against its `snapshot_root`; use `run --plan PATH` with the plan path printed
by the second command. Keep evidence outside that copied source.
Snapshot success is **not** a test pass or baseline certification. Copying source
never waives the frozen-source gate: tests that mutate copied inputs still
invalidate source stability. This is source-copy isolation, not an operating
system security sandbox for untrusted code.
The snapshot destination must be new and outside the original source tree.
Ordinary empty directories are preserved, and internal aliases are redirected
into the copy.
Git metadata is deliberately not copied. Tests that audit commits or merge
history must run in a real checkout with the required history available, not a
Git-free snapshot. Keep that checkout unchanged throughout planning and execution;
do not replace missing Git evidence with simulated audit results.
Execution and captured commands place the selected source root before the
canonical engine/plugin bootstrap and inherited `PYTHONPATH`, so copied
repository modules take precedence over original-checkout modules.

### Product validation

From the repository root:

```bash
python -m pytest tests/test_um_arts*.py -m "" -q \
  --basetemp=.um-arts-test-work/product26
```

The canonical product description is recorded in
[`../12-AZ-IP/IP_REGISTRY.json`](../12-AZ-IP/IP_REGISTRY.json); `run.py --help`
provides the current command list. No standalone product Markdown document is
required for installation.

The core suite's pre-collection hook copies the committed PsiCat training
history and profile seeds, and any existing Lodge exchange history, into an
external temporary directory and redirects
runtime writes there for the pytest session. This preserves real training
execution without modifying committed evidence or relaxing source-stability
checks. Paths and caches are restored when the session closes.
UM-ARTS test fixtures use the disclosed `.um-arts-test-work` scratch boundary,
rather than creating new source directories during captured runs. Runtime
artifacts outside disclosed scratch boundaries still invalidate source stability.

### Large-repository code intelligence and scanner evidence

Code indexing, security scanning and test execution are separate lanes. DuckDB
and Tree-sitter can make syntax inventories queryable; neither an AST match nor
retrieval establishes interprocedural taint coverage. UM-ARTS uses its existing
standard-library SQLite stack for bounded Python AST facts without requiring a
database server, embedding provider, downloaded extension or new runtime
dependency. The index never imports repository modules.

```bash
python 12-AZ-IP/26-um-arts/run.py code-index --root "$PWD" \
  --output /tmp/um-code-index
python 12-AZ-IP/26-um-arts/run.py code-query --artifact /tmp/um-code-index \
  --kind calls --name subprocess.run --limit 100
python 12-AZ-IP/26-um-arts/run.py code-index --root "$PWD" \
  --output /tmp/um-code-index-next --previous /tmp/um-code-index
```

Indexes disclose parsed, oversized and failed files. Incremental runs reuse only
verified unchanged parsed files; deleted files are not carried forward.
Queries are bounded, parameterized and read-only, not an arbitrary SQL execution
endpoint. Calls are syntactic names, not resolved call graphs. A partial index
cannot certify complete analysis. Keep output outside the source tree.

For optional local pattern scanning, install a reviewed Opengrep release outside
the source tree and verify its published checksum. The adapter was smoke-tested
with the official **1.30.0** Linux binary. It does not install tools, fetch rule
registries, update itself or launch repository builds.

```bash
python 12-AZ-IP/26-um-arts/run.py scan --root "$PWD" \
  --executable /absolute/path/to/opengrep --output /tmp/um-scan \
  --paths 12-AZ-IP/26-um-arts/um_arts TOOLS/um_arts \
  --files-per-shard 64 --memory-mib 512 --timeout 120
python 12-AZ-IP/26-um-arts/run.py scan-report --artifact /tmp/um-scan
```

`--rules /absolute/path/to/reviewed-rules.yml` selects a trusted local rule file.
The bundled three-rule profile flags dynamic evaluation, shell commands and
pickle input for **human review**, not automatic vulnerability declarations.
Scanner and rule hashes, source/environment provenance, exact assigned/scanned
file identities, raw JSON, errors and skipped targets/rules are retained.
Oversized files, parse errors, timeouts, unexpected coverage, source drift or
missing tools block a clean result. Findings exit nonzero and remain review
candidates; `checked` means only these files completed these rules with no
findings. It never means secure or CodeQL-certified.

`--previous /tmp/um-scan` reuses only sealed completed shards with identical file,
tool, rule and resource-setting digests from a source-stable prior scan. Changed
inputs are rescanned. Output is new and external; old artifacts are not modified.
One subprocess per bounded shard limits repeated whole-repository database
construction. Tool memory/time flags are resource requests, not an OS sandbox.
Sharding deliberately does **not** promise cross-file data flow, and these scans
do not replace pytest or Lean compiler checks.

Opengrep's capabilities are release-sensitive: the 1.30.0 documentation describes
intrafile interprocedural taint, while later development documents interfile
analysis. This adapter's starter profile uses pattern rules only. Do not infer
newer development features or CodeQL-equivalent global analysis from a clean
profile run. See the primary documentation for
[CodeQL data flow](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/),
[sitting_duck architecture](https://github.com/teaguesterling/sitting_duck/blob/main/docs/explanation/architecture.md),
and [Opengrep 1.30.0](https://github.com/opengrep/opengrep/tree/v1.30.0).

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
