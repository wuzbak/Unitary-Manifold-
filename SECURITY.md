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

Alternatively, email **cpo@axiomzerospc.org**.

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

## Known dependency limitation

The 2026-10-08 environment audit found **CVE-2025-69872**
([GHSA-w8v5-vhqr-4h9v](https://github.com/advisories/GHSA-w8v5-vhqr-4h9v))
in `diskcache==5.6.3`, a transitive dependency of `dvc-data`. The latest
available DiskCache release is affected; the audit lists no patched version.
This finding is **unresolved**, not a clean dependency-audit result.

DVC is not required by the Python runtime or regression suites, so it is
excluded from `requirements.txt` and standard CI installs. The `dvc.yaml`
pipeline remains available for manual use. If you need to run it, install DVC
separately only after reviewing this advisory and securing its cache directories.
This dependency isolation is a mitigation, not a DiskCache patch.

DiskCache's default pickle deserialization can execute code if an attacker
can modify the cache contents. Keep DVC/DiskCache cache directories and their
parent directories private to the account running DVC; do not read caches
restored from untrusted archives, shared writable volumes, or other users.
Restricted filesystem access reduces exposure but does not patch the library.
Recheck the upstream advisory before using shared or externally supplied caches.

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
