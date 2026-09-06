# Merlin Smart Roadmap (One-Page)

This is the short execution roadmap for Merlin under strict budget constraints.
It is designed for rapid orientation, public readability, and research-grade traceability.

For full details, see:
- `MERLIN_FRONTIER_ROADMAP.md` (full operating plan)
- `MERLIN_PROGRAM.md` (implementation ledger and API surface)

---

## Mission

Build a local-first, governance-constrained repository assistant that is:
- auditable,
- epistemically honest,
- affordable to run,
- and empirically gated before promotion.

OpenRouter remains compatibility fallback only, not primary runtime.

---

## What we optimize for

1. **Trust density:** visible evidence, visible limits, visible uncertainty.
2. **Budget survival:** highest signal per token; avoid paid generation unless necessary.
3. **Measured progress:** no capability claims without benchmark receipts.
4. **Public clarity:** outputs that readers can verify and researchers can reproduce.

---

## Five-lane architecture (Merlin Pentad)

- **Sage:** repository synthesis with boundary discipline
- **Prover:** formal-reasoning and Lean-oriented traces
- **Router:** schema-correct tool routing/orchestration
- **Auditor:** contradiction detection and memory integrity
- **Gate:** fail-closed governance enforcement

No monolithic "god model" target.

---

## Smart execution sequence

### Step 1 — Stabilize contracts and telemetry
- Lock lane contracts (inputs, outputs, fallback behavior)
- Emit lane/compression metadata for every run
- Track contract completion, boundary violations, contradiction misses, and tool precision

### Step 2 — Restructure data for lane specialization
- Export lane-specific train/dev/test splits
- Keep global compatibility export intact
- Fail export when provenance/gates/contract fields are missing

### Step 3 — Run low-token curation loops
- Priority order: repository-native data → deterministic local augmentation → selective teacher calls
- Track token spend per accepted sample
- Pause external generation when efficiency degrades

### Step 4 — Train compact lane kernels
- Conservative compression for reasoning-critical lanes
- Aggressive compression only where evidence allows
- Keep rollback checkpoints per lane/tier

### Step 5 — Promote lane by lane
- Shadow first, then staged promotion
- Immediate demotion on threshold misses
- Decision receipts required for every promotion/demotion

---

## Non-negotiable gates

- High-severity governance violations: **0 tolerated**
- Provenance completeness: **>= 99%**
- Contract completion: **>= 99.5%**
- Router tool precision: **>= 97%**
- Auditor contradiction recall: **>= 95%**
- Longitudinal acceptance: **3 of latest 4 clean windows**

Any miss blocks promotion.

---

## What we are not doing

- No broad frontier-superiority claims
- No evidence-empty marketing claims
- No token-heavy default workflow
- No promotion based on one-off benchmark spikes

---

## Reader/research path

1. Start here (`MERLIN_SMART_ROADMAP.md`)
2. Read full strategy (`MERLIN_FRONTIER_ROADMAP.md`)
3. Inspect implementation surfaces (`MERLIN_PROGRAM.md`)
4. Verify runtime/API behavior (`README.md`)
5. Run receipts (`python 12-AZ-IP/20-merlin-navigator/tools/run_merlin_stage_a_benchmarks.py --json`)

This path is intentionally short-to-deep so readers can orient first, then verify.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
