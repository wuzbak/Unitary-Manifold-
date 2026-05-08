# Audit Workflow Map

## CI workflow map (GitHub Actions)

Source: `.github/workflows/tests.yml`

| Job | Purpose | Command |
|---|---|---|
| `test` | Fast test suite | `python -m pytest tests/ -v` |
| `test-slow` | Slow-marked tests | `python -m pytest tests/ -m slow -v` |
| `test-claims` | Claim package verification | `python -m pytest claims/ -v` |
| `test-recycling` | Pillar 16 recycling suite | `python -m pytest recycling/ -v` |
| `test-pentad` | Unitary Pentad governance suite | `python -m pytest "5-GOVERNANCE/Unitary Pentad/" -v` |
| `algebra-proof` | Formal algebraic check suite | `python3 ALGEBRA_PROOF.py` |

## Local regression path used for branch validation

- Full branch regression command used in this repository context:
  - `python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q`

## Validation intent boundaries

- Test/CI PASS indicates implementation and internal consistency checks passed.
- It does not by itself claim external empirical confirmation.
- Falsification conditions remain governed by the dedicated falsifier documents and observational windows.

