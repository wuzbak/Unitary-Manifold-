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

UM-ARTS lives in `TOOLS/um_arts/`, outside the physics implementation. It
orchestrates existing checks and preserves their evidence; it does not generate
new physics certificates, decide merges, or promote scientific claims. Its
repository adapter uses the existing supervised suite planner and formal
traceability contracts rather than a second pillar or theorem registry.

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
`dashboard --attempt PATH --output /tmp/um-arts-dashboard.html`.
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

Recovery currently reuses validated successes from sealed attempts only.
Hard-killed, unsealed attempts are not resumable; preserve their logs and re-plan.
Integration mode and automatic change-impact selection are not yet implemented.

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
