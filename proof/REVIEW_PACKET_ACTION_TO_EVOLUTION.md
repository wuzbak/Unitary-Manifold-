# Review Packet — Action-to-Evolution Equivalence

## Claim cluster

The current claim cluster is not that the implemented evolution is derived from the 5D action. The current honest claim is that the repository now exposes that this equivalence remains open and machine-readable.

## Assumptions boundary

Start with:

- `proof/TIER_1_FORMAL.md`
- `docs/TRUTH_LAYER.md`
- `src/core/action_to_evolution_contract.py`
- `src/core/evolution.py`
- `src/core/pillar1082_foundation_first_photon_action_audit.py`

Key honesty boundary (updated after the action-derived replacement):

- the default evolution engine now relaxes the Euler-Lagrange equations of the circle-reduced 5D Einstein-Hilbert action (`src/core/action_derived_flow.py`); the earlier phenomenological flow is retained only as `flow_law="phenomenological_legacy"`,
- the flow parameter is not coordinate time, and the t-relaxation law is declared, not derived,
- the derivation is verified only within a 1-D periodic zero-mode perimeter. The reduction identity is exact only on a restricted diagonal metric form, and the evidence class is executable Python validation (`src/core/action_to_evolution_derived_flow_certificate.py`), not Lean.

## Lean surface

Current traceability scaffold:

- `lean4/UnitaryManifold/SprintCAFormalTraceability.lean`

This file is only a traceability scaffold. It is not itself the missing derivation.

## Executable companion surface

Primary Python artifacts:

- `src/core/evolution.py::phenomenological_flow_boundary`
- `src/core/pillar1082_foundation_first_photon_action_audit.py`
- `src/core/metric_ansatz_derivation.py`
- `src/core/metric.py`

Primary tests:

- `tests/test_evolution.py`
- `tests/test_pillar1082_foundation_first_photon_action_audit.py`

These tests verify the explicit boundary and the audited bookkeeping content. They do not close the action-level derivation.

## Exact review question

Please answer one or more of the following:

1. What is the smallest exact action-and-variation package needed to test equivalence?
2. Which assumptions must be fixed before an Euler-Lagrange comparison is mathematically meaningful?
3. Is any part of the current evolution surface overstated relative to what is actually derived?
4. Is there a simpler falsifying mismatch between the implemented flow and any admissible 5D action candidate?

## Active work queue

Treat this packet as the live Lane B retirement board. The current exact units are:

1. variable identification
2. time / flow-parameter interpretation
3. action functional
4. variation rules
5. boundary terms
6. admissible function spaces
7. residual / error comparison

For each unit, the only acceptable end states are:

- `CLOSED_NOW`
- `CONDITIONAL_ONLY`
- `BLOCKED_NOT_YET_DERIVABLE`

The current doctrine is:

- action-to-evolution remains the **primary closure program**,
- no global master-theorem attempt should outrun these unit-level gates,
- and no floating-point comparison may strengthen the claim class without an
  explicit certificate surface.

## Explicit falsifier / blocker request

A successful review packet response is one that either:

- produces an action whose Euler-Lagrange equations can be checked against the implementation,
- proves such a match fails under the current assumptions,
- or sharpens the remaining blocker set without inflating closure claims.
