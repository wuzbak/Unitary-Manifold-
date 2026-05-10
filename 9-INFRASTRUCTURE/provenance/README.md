# Toolchain & AI Provenance (Canonical Source)

This folder is the canonical source for what programs, suites, languages, and AI systems were used to build, test, audit, and operate this repository.

## Start here

- [MASTER_INVENTORY.md](MASTER_INVENTORY.md) — consolidated inventory with confirmed vs available scope
- [AUDIT_WORKFLOW_MAP.md](AUDIT_WORKFLOW_MAP.md) — CI/test/audit workflow map
- [AI_AGENT_ROLE_MAP.md](AI_AGENT_ROLE_MAP.md) — AI system role boundaries and usage classes
- [DOC_FRESHNESS_POLICY.md](DOC_FRESHNESS_POLICY.md) — update order and stale-doc policy

## Scope rule

- **Confirmed in-repo usage** = backed by executable code, workflow files, or committed docs in this repository.
- **Available infrastructure** = documented deployment/integration options present in-repo but not claimed as always active.

## Current verification snapshot

- Latest full local regression on this branch:
  - `python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q`
  - `28560 passed, 329 skipped, 11 deselected, 0 failed`

- Current dependency stack used in validation lanes:
  - `numpy`, `scipy`, `pytest`, `sympy`, `jax[cpu]`, `jaxlib`, `z3-solver`, `wandb`, `dvc`

## Evidence roots

- CI workflows: `/.github/workflows/`
- Core runtime/tests: `/src/`, `/tests/`, `/recycling/`, `/5-GOVERNANCE/Unitary Pentad/`
- Bot/agent infrastructure: `/9-INFRASTRUCTURE/bot/`, `/AGENTS.md`, `/9-INFRASTRUCTURE/mcp-config.json`

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
