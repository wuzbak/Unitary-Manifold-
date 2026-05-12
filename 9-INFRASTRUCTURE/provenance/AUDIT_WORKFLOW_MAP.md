# Audit Workflow Map

## CI workflow map (GitHub Actions)

Primary source: `.github/workflows/tests.yml`

| Job | Purpose | Command |
|---|---|---|
| `test` | Fast test suite | `python -m pytest tests/ -v` |
| `test-slow` | Slow-marked tests | `python -m pytest tests/ -m slow -v` |
| `test-claims` | Claim package verification | `python -m pytest claims/ -v` |
| `test-recycling` | Pillar 16 recycling suite | `python -m pytest recycling/ -v` |
| `test-pentad` | Unitary Pentad governance suite | `python -m pytest "5-GOVERNANCE/Unitary Pentad/" -v` |
| `algebra-proof` | Formal algebraic check suite | `python3 ALGEBRA_PROOF.py` |
| `ledger-consistency` | Canonical ledger + onboarding doc consistency | `python -m pytest tests/test_canonical_ledger_consistency.py -v` |

## Local regression path used for branch validation

- Full branch regression command used in this repository context:
  - `python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q`
  - Latest local result: `31008 passed, 393 skipped, 12 deselected, 0 failed`

## Additional active workflow gates

| Workflow file | Purpose |
|---|---|
| `.github/workflows/lean4-check.yml` | Lean 4 formal proof build/check lane |
| `.github/workflows/mutation-hard-gate.yml` | Mutation testing hard gate (`mutmut`) |
| `.github/workflows/staleness-honesty-gate.yml` | Documentation staleness + honesty checks |
| `.github/workflows/external-constants-crosscheck.yml` | Constants cross-check lane |
| `.github/workflows/pages.yml` / `jupyterbook.yml` | Pages and JupyterBook publishing |
| `.github/workflows/release.yml` / `build-download.yml` / `ipfs-publish.yml` / `dco.yml` | Release, archive, IPFS publish, and DCO verification |

## Validation intent boundaries

- Test/CI PASS indicates implementation and internal consistency checks passed.
- It does not by itself claim external empirical confirmation.
- Falsification conditions remain governed by the dedicated falsifier documents and observational windows.
