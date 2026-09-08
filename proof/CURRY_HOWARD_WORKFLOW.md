# Curry-Howard Workflow — Proofs as Programs in the Current Lean4 Stack

Lean 4 does not split “proof work” from “program work.” In this repository, the Curry-Howard point is practical: a proposition is a type, a proof is a term inhabiting that type, and every increase in geometric sophistication raises the amount of explicit computational structure the checker requires.

## Core alignment

Use this matrix as the working lens:

| Logic side | Program side | Repository Lean example |
|---|---|---|
| Proposition | Type | `NWUniquenessHonest.lean::proof_distance_map` |
| Proof | Term / value | `SprintCAFormalTraceability.lean::ca_trace_kernel_02` |
| Implication | Function type | `SprintCAFormalTraceability.lean::ca_trace_kernel_02` |
| Conjunction | Product type | `NWUniquenessHonest.lean::proof_distance_map` |
| Disjunction | Sum type | `SprintCAFormalTraceability.lean::ca_trace_kernel_06` |
| Falsehood | Empty type / contradiction | `SprintCAFormalTraceability.lean::ca_trace_kernel_07` |

## Where this matters most right now

The computational content is showing up most sharply in two places:

1. **APS / orbifold / Dirac boundary machinery**
2. **Action-to-evolution equivalence**

Those are not “big theorem count” problems. They are dependent-structure problems. As the mathematics gets closer to manifolds with boundary, spectra, parity projections, and action-level coherence, more of the proof must be carried explicitly as terms rather than informal paper steps.

## Current runtime reality

At present, the repository should be treated as a **manual-port-with-traceability** system:

- Lean files state or scaffold proof structure.
- Python modules implement the executable physics/runtime layer.
- Tests and status documents carry the bridge.

That means the practical question is not “are the engines calling Lean terms directly?” but “is the ported runtime logic traceable back to an explicit Lean or honesty boundary?” Right now the answer is yes for selected surfaces, but the bridge is still documentation-and-registry mediated rather than direct term execution.

## Smarter integration direction

The next upgrade path is:

1. Keep the two-lane formal frontier fixed.
2. Use `src/core/formal_traceability_spine.py` as the canonical bridge registry.
3. Expand each review packet into a training-ready artifact bundle.
4. Export those bundles into PsiCat’s existing training/tooling pipeline.
5. Only claim stronger integration when a direct Lean-to-runtime artifact actually exists.

## PsiCat training surface

PsiCat should be trained on the current proof-foundry set, not on diffuse historical closure language alone:

- `proof/README.md`
- `proof/TIER_1_FORMAL.md`
- `proof/FORMAL_PROOF_FOUNDRY.md`
- `proof/CURRY_HOWARD_WORKFLOW.md`
- `proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md`
- `proof/REVIEW_PACKET_ACTION_TO_EVOLUTION.md`
- `docs/TRUTH_LAYER.md`

The existing export and benchmark tooling already lives under `12-AZ-IP/20-psicat-navigator/tools/`. The immediate workflow improvement is to treat these proof-foundry documents as a canonical training corpus and keep them synchronized with the machine-readable spine.
