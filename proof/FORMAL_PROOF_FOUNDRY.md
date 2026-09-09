# Formal Proof Foundry — Current Lean4/Python Frontier

This document defines the current proof-foundry surface for the Unitary Manifold repository.

The immediate formal program is intentionally narrowed to **two lanes only**:

1. **APS / orbifold / Dirac boundary machinery**
2. **Action-to-evolution equivalence for the implemented physics core**

The purpose of this narrowing is simple: theorem counts are no longer the right measure of progress. The right measures are which assumptions were retired, how much proof distance was reduced, which claims moved from proxy to conditional to checked, and how cleanly a claim traces from Lean to Python to tests to current status surfaces.

## Proof classes

Use the following proof classes consistently:

- **Lean unconditional** — a Lean theorem with no extra named axiom beyond the checked environment
- **Lean conditional with named axioms** — a Lean theorem whose burden is explicit and not hidden
- **Executable Python validation** — a numerical, structural, or audit surface that is useful evidence but not a Lean proof

These classes must not be merged together in reporting.

## Canonical machine-readable spine

The canonical registry for this surface is:

- `src/core/formal_traceability_spine.py`
- `tests/test_formal_traceability_spine.py`

That spine maps:

**axiom / open gap / theorem cluster → epistemic class → Lean file → Python module → tests → status entry → review packet**

## Reviewer intake order

For a first-pass review of the current honesty boundary, use:

1. `proof/README.md`
2. `proof/TIER_1_FORMAL.md`
3. `docs/TRUTH_LAYER.md`
4. one of the focused review packets below

## Focused review packets

- `proof/REVIEW_PACKET_APS_ORBIFOLD_DIRAC.md`
- `proof/REVIEW_PACKET_ACTION_TO_EVOLUTION.md`
- `proof/CURRY_HOWARD_WORKFLOW.md`
- `proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md`
- `proof/PSICAT_NAVIER_STOKES_CURRICULUM_PACKET.md`

Each packet is deliberately small:

- one claim cluster
- one assumptions boundary
- one Lean file or small Lean cluster
- one executable verification path
- one explicit falsifier or blocker request

## What this surface is for

This surface is for honest proof work and external review. It is not a claim that the whole formal build is closed. It is a way to expose the present frontier without mixing arithmetic proxies, conditional theorems, and executable validations into one undifferentiated count.

## PsiCat training and workflow upgrade

PsiCat should ingest this proof-foundry surface as a canonical corpus for train-and-work:

- the proof intake docs,
- the Curry-Howard workflow note,
- the focused review packets,
- the Navier-Stokes method-transfer intake and curriculum packets,
- the current truth-layer reassessment,
- and the machine-readable registry in `src/core/formal_traceability_spine.py`.

That keeps training aligned to the current honesty boundary instead of older closure phrasing alone.
