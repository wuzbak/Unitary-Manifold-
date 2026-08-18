# ADR-003: HILS Gate Design

**Date:** 2026-08-18
**Status:** Accepted
**Deciders:** ThomasCory Walker-Pearson, GitHub Copilot (AI)

---

## Context

AxiomZero is an AI cognitive layer that can propose code changes, pillar
additions, and system mutations.  Without a hard gate, an AI inference error
could corrupt the physics framework (which has a hard requirement of 0 test
failures) or commit changes that have not been validated by the human operator.

## Decision

Every **mutating** action performed by the AI must pass the **HILS gate**
before execution.

The gate has two modes:
1. **Synchronous approval** — the agent submits an action to the API, which
   returns 202 Accepted and a `task_id`.  Execution is blocked until the human
   calls `POST /tasks/{task_id}/approve` with `approved: true`.
2. **Quorum bypass** — the canonical primary operator (`wuzbak`) may
   pre-authorize a class of actions (e.g., read-only operations) by setting
   `quorum_bypass: true` in their `HILOperator` record.

## Rationale

| Property | Design |
|---|---|
| Single point of human control | M7 Executive is the only manager that communicates with the human |
| Non-bypassable | M4 Test gate is hard-wired as a mandatory gateway in the LangGraph |
| Auditability | Every gate decision written to `state.db` and `agent_audit.jsonl` |
| Graceful degradation | If the gate is unreachable, the action is REJECTED (fail-closed) |
| Revocability | All approvals time-out after 24 hours unless refreshed |

## Consequences

* **Positive:** Formal proof that no AI action can occur without human awareness.
* **Positive:** Audit trail is immutable (append-only JSONL).
* **Negative:** Adds latency to every mutating action (typically 30–300 s for human response).
* **Negative:** If the human is unavailable, the agent is blocked.  Mitigated by
  pre-authorization classes and quorum bypass for low-risk actions.

## Open questions

1. What is the right timeout for an approval?  Currently 24 hours; may need
   to be configurable per action class.
2. Should the gate be federated (multiple humans must approve high-risk
   actions)?  Currently single-human; Pentad quorum model covers governance-level
   decisions separately.

*Theory: ThomasCory Walker-Pearson. Code: GitHub Copilot (AI).*
