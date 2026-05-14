# Critique Hardening Protocol (Pillar 236)

*Unitary Manifold v10.54+ operational protocol for critique-integrated scientific rigor.*

---

## Purpose

This protocol strengthens repository scientific discipline by making critique
processing explicit, auditable, and simulation-backed.

It adds three additive layers:

1. **External Validation Ledger** — each major observable claim is compared
   against tracked external measurements with source URLs and confidence context.
2. **Source-Quality Ladder** — every evidence input is tier-labeled before use.
3. **Preregistered Falsification Table** — falsification conditions are declared before
   the decisive data release.

This protocol does **not** delete or downgrade existing derivation records.
It tightens routing and evidentiary hygiene.

---

## Layer 1 — External Validation Ledger

Primary implementation: `src/core/pillar236_critique_hardening_engine.py`
(`critique_hardening_ledger`, `ledger_summary`,
`monte_carlo_critique_stability`).

Current tracked lanes:

- `n_s` (Planck 2018)
- `r` (BICEP/Keck BK18)
- `beta` (Planck PR4 / NPIPE)
- `w0`, `wa` (DESI DR2 combined)
- LiteBIRD beta precision forecast (readiness lane)

Output verdict labels:

- `CONSISTENT`
- `TENSION`
- `HIGH_TENSION`
- `FALSIFIED`
- `INFORMATIONAL`

---

## Layer 2 — Source-Quality Ladder

Canonical tiering:

| Tier | Meaning | Allowed usage |
|------|---------|---------------|
| **T1** | First-principles derivation + executable verification | Hardgate derivation lane |
| **T2** | Peer-reviewed measurement / major collaboration result | External validation and claim checking |
| **T3** | Independent cross-check analysis | Triangulation only |
| **T4** | Forecast / planning methodology | Readiness and scenario planning |
| **T5** | Outreach / speculative discussion | Not standalone quantitative evidence |

Rule: high-level summaries must not elevate T3–T5 inputs to T1-equivalent
status.

---

## Layer 3 — Preregistered Falsification Table

Primary callable: `preregistered_falsification_table()` in Pillar 236.

Current preregistered rows:

- `F-BETA-1` — LiteBIRD beta window and inter-sector gap criterion
- `F-NS-1` — CMB-S4 mismatch threshold for `n_s`
- `F-R-1` — tensor lane conditions for `r`
- `F-WA-1` — DESI `wa != 0` persistent high-significance criterion

Rule: preregistered falsification conditions are not relaxed post hoc after data release.

---

## Simulation Requirement

Pillar 236 includes Monte Carlo robustness checks of verdict stability under
measurement uncertainty. This prevents overconfidence from single-point matches.

Minimum simulation acceptance:

- deterministic seed reproducibility,
- explicit per-claim dominant verdict fraction,
- entropy summary for verdict dispersion.

---

## Governance Boundary

This protocol is **adjacent hardening infrastructure**. It does not alter the
hardgate core score by itself.

It improves:

- auditability,
- external reproducibility posture,
- robustness against critique drift,
- transparent separation between derivation status and observational status.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
