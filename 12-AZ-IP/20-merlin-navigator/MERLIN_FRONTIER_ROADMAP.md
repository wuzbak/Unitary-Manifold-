# Merlin Sovereign Frontier Roadmap (Budget-Constrained Execution)

This roadmap is the operational build plan for turning Merlin from a retrieval-first repository navigator into a local-first, benchmark-gated, compact-kernel model system that can compete in a narrow domain: repository physics reasoning, formal proof support, tool orchestration, and governance-safe operation.

It is deliberately strict: no capability claim is accepted without benchmark receipts, and no promotion is accepted without fail-closed governance checks.

---

## 0) Baseline and constraints (starting point)

Current implemented Merlin surfaces already provide a strong base:

- Runtime and route policy surfaces in `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/ox_navigator/engine/merlin_router.py`
- Local provider registry and fallback behavior in `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/ox_navigator/engine/merlin_local_inference.py`
- OpenRouter-compatible client in `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/ox_navigator/engine/client.py`
- Telemetry and energy/cost estimates in `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/ox_navigator/engine/merlin_telemetry.py`
- Benchmark corpora and promotion gates in `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/ox_navigator/engine/merlin_benchmark.py`
- Training architecture and JSONL bundle construction in `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/ox_navigator/engine/merlin_program.py`
- Export scripts in `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/tools/`

Hard operating constraints:

- Budget is limited; external-token-heavy approaches must be minimized.
- OpenRouter remains compatibility-only fallback, not primary.
- Promotion must remain benchmark and governance gated.
- Repository epistemic discipline (explicit uncertainty, explicit boundaries) is non-negotiable.

---

## 1) Target architecture: Merlin Pentad of Compact Kernels

Merlin adopts a dedicated five-kernel runtime pentad:

1. **Kernel-S (Sage):** repository physics synthesis + epistemic status discipline
2. **Kernel-P (Prover):** Lean4/formal-math-oriented reasoning traces
3. **Kernel-R (Router):** schema-aware tool routing for invoke/orchestrate flows
4. **Kernel-A (Auditor):** memory drift/contradiction detection and recall integrity
5. **Kernel-G (Gate):** fail-closed governance and boundary enforcement

Design policy:

- No "god model" requirement.
- Each kernel is narrower, smaller, and benchmarked against lane-specific tasks.
- Cross-kernel coordination is explicit and auditable.

---

## 2) Program phases and exact deliverables

## Phase I — Contract freeze and observability expansion

**Objective:** lock interfaces and metrics before compression or training.

Deliverables:

- Define a formal lane contract for each kernel (inputs, outputs, allowed actions, fallback behavior).
- Add telemetry dimensions for `kernel_id`, `kernel_variant`, `quantization`, `adapter_id`, and `degraded_mode`.
- Add per-kernel acceptance counters: `contract_pass_rate`, `boundary_violation_rate`, `contradiction_miss_rate`, `tool_call_precision`.
- Add deterministic demotion triggers if any kernel crosses failure thresholds.

Exit criteria:

- Every `/api/merlin` and `/api/agentOrchestrate` run emits kernel-lane telemetry.
- Telemetry can separate errors by kernel and compression level.

## Phase II — Dataset restructuring for lane specialization

**Objective:** convert existing training bundle from generic records into kernel-targeted corpora.

Deliverables:

- Extend `build_training_dataset_bundle()` output to include per-kernel splits:
  - `kernel_s_train/dev/test`
  - `kernel_p_train/dev/test`
  - `kernel_r_train/dev/test`
  - `kernel_a_train/dev/test`
  - `kernel_g_train/dev/test`
- Preserve existing global train/dev/test export for backward compatibility.
- Add schema validators that fail export if:
  - provenance is missing
  - required gate labels are missing
  - contradiction flags are inconsistent
  - benchmark contract sections are absent

Exit criteria:

- Export command emits lane-specific JSONL files and schema-valid manifests.
- Existing tests remain green and compatibility fields remain intact.

## Phase III — Low-token data expansion loop

**Objective:** increase data quality while minimizing paid-token generation.

Deliverables:

- Priority source order:
  1. Existing repository assets and benchmark corpora
  2. Deterministic rewrites and perturbations generated locally
  3. Selective API teacher calls only for high-value gaps
- Build a two-pass data curation loop:
  - Pass A: candidate generation (focused variations and counterexamples)
  - Pass B: critic filtering (factuality, boundary adherence, contract completeness)
- Enforce deduplication and near-duplicate collapse before training.

Exit criteria:

- Curated dataset growth with measured quality score improvement.
- Token spend per accepted sample is tracked and reduced over time.

## Phase IV — Kernel-specific compact training

**Objective:** train and compress each kernel without catastrophic reasoning collapse.

Deliverables:

- Kernel-S and Kernel-P: conservative compression first; adapter training prioritized.
- Kernel-R and Kernel-G: smaller model class, stronger compression acceptable.
- Kernel-A: long-context-biased adapter with contradiction-focused objectives.
- Add rollback checkpoints for each kernel and compression tier.

Exit criteria:

- Each kernel clears lane benchmarks at or above deterministic baseline.
- No severe regressions in boundary safety or contradiction detection.

## Phase V — Staged shadow deployment and promotion

**Objective:** operationalize the pentad without breaking current service reliability.

Deliverables:

- Shadow mode by lane first; production decision remains with current stable path.
- Promote lane-by-lane, not all at once.
- Keep explicit compatibility fallback for incidents.
- Record every promotion/demotion decision in control-tower artifacts.

Exit criteria:

- Sustained clean-window history passes longitudinal acceptance.
- Replacement remains fail-closed when evidence is incomplete.

---

## 3) Benchmark requirements (must pass)

Merlin cannot claim frontier-readiness in this repository domain until all categories below pass.

### A. Contract and structure integrity

- Response contract completion rate (body + FOLLOWUPS + Sources)
- Typed provenance completeness
- Required gate visibility
- Refusal correctness for out-of-bound requests

### B. Domain reasoning quality

- Repository-grounded answer precision
- Uncertainty discipline under ambiguous evidence
- Cross-source reconciliation quality
- Falsification-awareness correctness

### C. Tool and orchestration quality

- Tool selection precision (correct tool, correct schema)
- Orchestration chain completion accuracy
- Recovery behavior after tool failures
- Privileged-action escalation correctness

### D. Memory and contradiction quality

- Contradiction detection recall
- Contradiction false-positive rate
- Memory recall correctness across long sessions
- Drift containment over repeated interactions

### E. Governance and safety quality

- Zero unauthorized boundary crossing
- Prompt injection resistance pass rate
- High-severity policy violation count (target: zero)
- Fail-closed correctness when data is incomplete

### F. Efficiency quality

- Latency by lane
- Energy per successful task
- Memory footprint by kernel tier
- Cost-per-accepted-response trend

---

## 4) Quantitative gate thresholds (initial)

These are initial deployment thresholds and may tighten after baseline stabilization.

- High-severity governance violations: **0 tolerated**
- Typed provenance completeness: **>= 99%**
- Response contract completion: **>= 99.5%**
- Tool selection precision (Router lane): **>= 97%**
- Contradiction detection recall (Auditor lane): **>= 95%**
- Longitudinal clean windows required before wider promotion: **minimum 3 of latest 4 windows**

Any threshold miss blocks promotion for that lane.

---

## 5) Token-budget governance (because budget is tight)

Budget doctrine: spend tokens only where local synthesis cannot close the gap.

- **Tier 0 (zero token):** local deterministic transformations, perturbations, benchmark replay
- **Tier 1 (low token):** selective teacher generation for sparse high-value edge cases
- **Tier 2 (guarded token):** critic/reranker calls only for unresolved high-impact samples

Required tracking fields per batch:

- tokens_spent_total
- tokens_spent_per_accepted_sample
- accepted_sample_quality_mean
- rejection_reasons_distribution

Budget gate:

- If token efficiency degrades for two consecutive cycles, freeze external generation and run local curation-only cycle.

---

## 6) Risk register and mitigations

1. **Over-compression collapse**
   - Mitigation: lane-specific rollback checkpoints; no irreversible compression jumps.
2. **False confidence from narrow benchmarking**
   - Mitigation: mixed corpora, adversarial injections, hidden holdouts.
3. **Governance drift under performance pressure**
   - Mitigation: Kernel-G independent fail-closed enforcement.
4. **Tool misuse under orchestration depth**
   - Mitigation: strict schema validation and privilege checks remain mandatory.
5. **Token burn creep**
   - Mitigation: token-efficiency dashboards and hard pause triggers.

---

## 7) Operating rhythm (execution cadence)

Weekly:

- Data curation cycle
- Kernel benchmark cycle
- Promotion board review (go/hold/demote)

Biweekly:

- Compression-tier reassessment
- Lane-specific failure-mode drill

Monthly:

- Longitudinal gate review
- Budget-versus-capability audit
- Roadmap checkpoint updates

---

## 8) Definition of success and non-success

Success in this roadmap means:

- Merlin reliably outperforms deterministic baseline in its narrow domain,
- while preserving explicit epistemic honesty,
- while remaining governance-safe and fail-closed,
- and while operating at a budget profile sustainable for a small team.

Non-success means any of the following:

- performance gains paired with governance regressions,
- benchmark-only wins that do not survive longitudinal windows,
- or token spend that is incompatible with continued operation.

---

## 9) Immediate next implementation tasks

1. Add kernel metadata and lane metrics into telemetry payloads.
2. Add per-kernel dataset split export in training JSONL pipeline.
3. Add schema hard-fail validators for provenance/gates/contract sections.
4. Add lane-specific benchmark dashboards and pass/fail receipts.
5. Add promotion board packet per lane with explicit go/hold/demote outcome.

This is the execution baseline for the ongoing Merlin program.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
