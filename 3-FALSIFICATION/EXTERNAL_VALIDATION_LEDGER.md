# External Validation Ledger (Pillar 236)

*Living ledger for externally measured constraints used in falsification routing and critique hardening.*

---

## Ledger Fields

Each row tracks:

- claim lane,
- UM predicted value,
- external observed value / bound,
- uncertainty model,
- verdict,
- source URL and source-quality tier,
- required next action.

---

## Current Baseline Rows

| Lane | UM prediction | External constraint | Current verdict | Source tier | Source |
|------|---------------|---------------------|-----------------|-------------|--------|
| `P2: n_s` | 0.9635 | 0.9649 ± 0.0042 (Planck 2018) | CONSISTENT | T2 | https://arxiv.org/abs/1807.06209 |
| `P3: r` | 0.0315 | r < 0.036 (95% CL, BK18) | CONSISTENT | T2 | https://arxiv.org/abs/2203.16556 |
| `P1: beta primary` | 0.331° | 0.342° ± 0.094° (Planck PR4/NPIPE) | CONSISTENT | T2 | https://arxiv.org/abs/2201.07241 |
| `P1: beta shadow` | 0.273° | 0.342° ± 0.094° (Planck PR4/NPIPE) | CONSISTENT / TENSION boundary depending dataset mix | T2 | https://arxiv.org/abs/2201.07241 |
| `P4: w0` | -0.9302 | -0.90 ± 0.055 (DESI DR2 combined) | CONSISTENT / TENSION boundary | T2 | https://arxiv.org/abs/2503.14738 |
| `P4: wa` | 0 | -0.55 ± 0.20 (DESI DR2 combined) | HIGH_TENSION | T2 | https://arxiv.org/abs/2503.14738 |
| `Readiness: LiteBIRD beta sigma` | theory windows: 0.273° / 0.331° | sigma_beta ≈ 0.02° forecast | INFORMATIONAL (pre-release) | T4 | https://arxiv.org/abs/2202.02773 |

---

## Update Rules

1. On new release (DESI DR3, CMB-S4, LiteBIRD), update this ledger within 30 days.
2. Same-day sync required with:
   - `3-FALSIFICATION/OBSERVATION_TRACKER.md`
   - `docs/CLAIM_MASTER_BOARD.md`
   - `FALLIBILITY.md` (if status label changes)
3. Never overwrite old rows without recording prior values in commit history.
4. Never downgrade a `FALSIFIED` verdict without a clearly documented correction
   to measurement processing.

---

## Reproducible Generation Path

Programmatic source of truth:

- `src/core/pillar236_critique_hardening_engine.py`
  - `critique_hardening_ledger()`
  - `ledger_summary()`
  - `pillar236_critique_hardening_report()`

This markdown ledger is the human-readable mirror of that executable output.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
