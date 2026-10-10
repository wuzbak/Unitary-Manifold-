# AZ Phi-Debt Early Warning Library — Product 32

**Folder:** `12-AZ-IP/32-az-phi-debt-early-warning/`
**Version:** 1.0.0
**TRL:** TRL-3 (domain-agnostic library, cross-checked against one real internal source)
**Status:** Active — Phase 0 + partial Phase 1 of article-354's φ-debt roadmap

## What this is

Extracts the core φ-debt accounting math out of `recycling/entropy_ledger.py`
and the resonance-audit tooling in `src/governance/resonance_audit.py` into
a domain-agnostic library with a clean, nounless API: `DebtMonitor(capacity,
discharge_rate)` in, `accumulate(amount, dt)` and `time_to_saturation()` out.
No field in this API mentions physics, recycling, or governance by name —
it is a formalism for any bounded-capacity network accumulating unaddressed
structural debt faster than it discharges it, with an explicit saturation
threshold as a warning rail (`NOMINAL` / `WARNING` / `SATURATED`).

`run_recycling_dogfood()` demonstrates one real internal cross-check: it
replays `recycling/entropy_ledger.material_entropy_debt()` readings through
the extracted monitor, confirming the domain-agnostic library reproduces
sane saturation behavior against the framework-specific accounting it was
extracted from.

## Epistemic status

This is Phase 0 (extraction) plus a single Phase 1 demonstration
(recycling only). The article names five internal reuse targets — EIGE, the
Falsification Observatory, the Geophysical Monitor, the staleness-honesty
CI gate, and the Pentad itself — and this version wires up only the first.
External release (Phase 2) is not part of this version.

## Usage

```bash
python 12-AZ-IP/32-az-phi-debt-early-warning/run.py
```

```python
from az_phi_debt_early_warning import DebtMonitor

monitor = DebtMonitor(capacity=100.0, discharge_rate=2.0)
monitor.accumulate(amount=15.0, dt=1.0)
print(monitor.to_report())
```

## Tests

```bash
python -m pytest 12-AZ-IP/32-az-phi-debt-early-warning/tests -q
```

## Sources

- `recycling/entropy_ledger.py`
- `src/governance/resonance_audit.py`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #5

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
