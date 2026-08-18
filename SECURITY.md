# Security Policy

## Supported versions

The most recent commit on the `main` branch is the only actively supported
version. There are no pinned release branches.

## Reporting a vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Send a private report via GitHub's Security Advisory feature:

1. Go to https://github.com/wuzbak/Unitary-Manifold-/security/advisories
2. Click **"New draft security advisory"**.
3. Describe the vulnerability, steps to reproduce, and potential impact.

Alternatively, email **wuzbak** via the contact on the GitHub profile.

We will acknowledge receipt within **48 hours** and aim to release a fix
within **14 days** for critical issues.

## Scope

This policy covers:

- The AxiomZero Python cognitive layer (`AxiomZero/`)
- The Unitary Pentad governance framework (`5-GOVERNANCE/Unitary Pentad/`)
- The UM-SOS FastAPI backend (`10-UM-SOS/backend/`, `src/core/um_sos_*.py`)
- The AZ-OS bare-metal kernel (`11-AZ-OS/`)
- All MCP servers (`AxiomZero/mcp/`)

**Out of scope:** third-party dependencies (report directly to those projects),
theoretical physics content, documentation.

## Security design principles

1. **No credentials in source code.** All secrets are loaded from environment
   variables via `pydantic-settings`. Pre-commit hooks (`detect-secrets`) block
   accidental commits.
2. **Path traversal prevention.** All filesystem operations resolve paths with
   `pathlib.Path.resolve()` and check against an explicit allowlist.
3. **Command execution sandboxing.** The MCP `execution_server` uses a strict
   whitelist and blocks dangerous commands (`rm -rf`, `dd`, `mkfs`, …).
4. **HILS gate.** Every mutating AI action requires explicit human approval
   before execution (`AxiomZero/governance/hils_gate.py`).
5. **JWT authentication.** All mutation endpoints on the AxiomZero API require
   a signed JWT bearer token.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
