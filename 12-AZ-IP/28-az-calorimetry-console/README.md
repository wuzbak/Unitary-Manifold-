# AZ Calorimetry Console — Product 28

**Folder:** `12-AZ-IP/28-az-calorimetry-console/`
**Version:** 1.0.0
**TRL:** TRL-2 (software instrumentation only; no lab run performed)
**Status:** Active — Phase 0 of article-354's cold-fusion roadmap

## What this is

Instrumentation software for the cold-fusion falsification protocol already
defined in `src/cold_fusion/` and `src/physics/lattice_dynamics.py`. It does
**not** claim cold fusion occurs, and it does not run or simulate a lab
experiment. It packages two already-tested, already-passing physics modules
into artifacts a real electrochemistry lab could use:

1. **Run-sheet generator** (`generate_run_sheet`) — reads the canonical
   D/Pd loading resonance `x = 7/8 = 0.875` from `lattice_dynamics.py` and
   the F1 calorimetry gate from `falsification_protocol.falsification_criteria()`,
   and emits a concrete temperature-ramp schedule paired with a monotonic
   loading-ratio curve.
2. **Live COP tracker** (`COPTracker`) — ingests `(power_in, power_out)`
   samples and reports a running verdict using the project's own `cop()`
   and `is_excess_heat()` functions from `src/cold_fusion/excess_heat.py`,
   against the pre-registered COP > 1.01 threshold. The verdict is always
   one of `AWAITING_DATA`, `NO_EXCESS_HEAT`, or `EXCESS_HEAT_OBSERVED` — it
   never claims more than the ingested data supports.

## Epistemic status

This is Phase 0 only, per article-354 direction #1 ("Cold fusion: from
calculation to calorimeter"). Phase 1 (lab-reproducible procedure document),
Phase 2 (an actual external lab run), and Phase 3 (honest reporting into
`FALLIBILITY.md`) are **not** part of this product and depend on an external
lab's willingness to run the protocol. The underlying field-theoretic vertex
bridging the radion's ~10⁻³⁵ m Compton wavelength to the ~10⁻¹⁰ m palladium
lattice scale has not been computed — see `src/cold_fusion/README.md`.

## Usage

```bash
python 12-AZ-IP/28-az-calorimetry-console/run.py run-sheet --loading-target 0.875
python 12-AZ-IP/28-az-calorimetry-console/run.py track --power-in-w 100 --power-out-w 102
```

## Tests

```bash
python -m pytest 12-AZ-IP/28-az-calorimetry-console/tests -q
```

## Sources

- `src/cold_fusion/excess_heat.py`, `falsification_protocol.py`
- `src/physics/lattice_dynamics.py`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-the-untouched-manifold-what-this-monorepo-could-still-become.md` — direction #1

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
