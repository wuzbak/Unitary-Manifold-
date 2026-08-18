# ADR-001: Use LangGraph for Multi-Agent Orchestration

**Date:** 2026-08-18
**Status:** Accepted
**Deciders:** ThomasCory Walker-Pearson, GitHub Copilot (AI)

---

## Context

AxiomZero requires a multi-agent orchestration framework that can:
1. Run 7 specialized managers (M1–M7) with conditional routing.
2. Support **mandatory gateways** (M3 Symbolic, M4 Test) that every physics claim must pass through.
3. Persist intermediate state across sessions (crash recovery / resumption).
4. Allow human-approval checkpoints (HILS gate) to pause the graph.
5. Gracefully degrade when the framework is absent (stub mode must remain functional).

## Decision

Use **LangGraph** as the primary orchestration framework.

## Rationale

| Requirement | LangGraph | Alternative: plain asyncio |
|---|---|---|
| State persistence / resumption | ✅ Built-in SQLite checkpointing | ❌ Manual |
| Conditional edges / branching | ✅ Native graph API | ⚠ Requires custom router |
| Human-in-the-loop pause | ✅ `interrupt_before` / `interrupt_after` | ❌ Manual |
| Streaming output | ✅ `.astream()` | ⚠ Manual |
| Graceful degradation | ✅ Wrapped in try/except with functional stub | ✅ |

The 7-manager × 5-sub-agent topology maps naturally to a `StateGraph` with each
manager as a node and conditional edges encoding the mandatory gateway rules.

## Consequences

* **Positive:** State-machine semantics make the HILS gate formally verifiable.
* **Positive:** Checkpoint resumption means no work is lost on crash.
* **Negative:** LangGraph adds a dependency (~30 MB); mitigated by graceful degradation.
* **Negative:** LangGraph API evolves quickly; pin to `>=0.1,<1` and test on every minor bump.

## Stub mode requirement

When LangGraph is absent, `agent_core.py` MUST run a real sequential
`asyncio.gather` pipeline that exercises all seven managers.  The stub must
**not** be a no-op — it must produce real output.

*Theory: ThomasCory Walker-Pearson. Code: GitHub Copilot (AI).*
