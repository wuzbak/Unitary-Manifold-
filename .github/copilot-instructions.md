# GitHub Copilot Instructions — Unitary Manifold

This file provides context for GitHub Copilot and AI coding assistants working
on the Unitary Manifold repository.

## What This Repository Is

A 5-dimensional Kaluza-Klein physics framework — **v11.0** — with:
- **208 core physics pillars** (hardgate, formally closed)
- **24+ adjacent research tracks** (Pillars 218–232: applied domains, non-hardgate)
- **Ω₀ Holon Zero** + sub-pillars (Pillar 70-B, 70-C, 70-D)
- **Independent HILS governance framework** (Unitary Pentad)
- **Quantum simulation layer** (`src/quantum/`: KK VQE, Fermi–Hubbard, XDiag bridge)
- **Supporting AI assistant infrastructure** (RAG, Copilot Extension, Custom GPT)

**Theory:** ThomasCory Walker-Pearson (2026)  
**Implementation:** GitHub Copilot (AI)  
**Status:** Active — pillar set CLOSED; 0 test failures required at all times

## Test Suite — Always Run Before and After Changes

```bash
# Fast suite (core physics, run first):
python -m pytest tests/ -q
# Expected: see STATUS.md for current tests/-only sub-suite total (≥ 27,000 passed)

# Recycling suite:
python -m pytest recycling/ -q
# Expected: 316 passed, 0 failed

# Unitary Pentad suite:
python -m pytest "5-GOVERNANCE/Unitary Pentad/" -q
# Expected: ~1,487 passed, 254 skipped, 0 failed

# Full repository (takes ~130 seconds):
python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q
# Expected: 34 411 passed · 393 skipped · 12 deselected · 0 failed
```

## Repository Structure

```
src/core/           ← 200+ modules: 5D metric, KK geometry, braided winding, SM params,
                      inflation, CMB transfer, adjacent pillars 200–232
src/holography/     ← holographic boundary, entropy-area (Pillar 4)
src/multiverse/     ← FTUM fixed-point iteration (Pillar 5, 29, 38)
src/quantum/        ← quantum layer: kk_vqe, fermi_hubbard (JW/BK), execution,
                      benchmarks, xdiag_bridge/ (XDiag↔UM contract, parity, routing)
src/sixd/           ← 6D field equations, generation count, Higgs mass, CW limit
src/sevend/         ← 7D CKM ρ̄ integration, discrete torsion CP
src/eightd/         ← 8D Wilson-line gauge
src/nined/          ← 9D anomaly cancellation, CP phase refinement
src/tend/           ← 10D flux landscape, CY₃ moduli/flux/α_s
src/eleventd/       ← 11D Hořava-Witten reduction, UV vacuum selection
src/meta/           ← MAS wave engine
src/data/           ← Planck data fetcher
src/consciousness/  ← coupled brain-universe attractor (Pillar 9)
src/atomic_structure/ src/cold_fusion/ src/chemistry/ src/astronomy/ (Pillars 10–15)
src/physics/        ← Pillar 15-B: lattice_dynamics.py (collective Gamow, phonon-radion bridge)
src/earth/ src/biology/ src/medicine/ src/justice/ src/governance/ (Pillars 12–13, 17–19)
src/neuroscience/ src/ecology/ src/climate/ src/marine/ (Pillars 20–23)
src/psychology/ src/genetics/ src/materials/ (Pillars 24–26)
recycling/          ← Pillar 16: φ-debt entropy accounting
5-GOVERNANCE/Unitary Pentad/ ← Independent HILS governance framework
tests/              ← 200+ test files, 30k+ passing tests (all pillars, adjacent tracks, integrations)
bot/                ← AI assistant infrastructure (RAG, Copilot Extension, Custom GPT)
5-GOVERNANCE/co-emergence/ ← HILS framework documentation
```

## Coding Conventions

- **Python 3.12+**, numpy/scipy for core modules
- **Optional integrations** (guarded via `pytest.importorskip` or try/except):
  - JAX — GPU/TPU acceleration and automatic differentiation (`src/core/jax_backend.py`)
  - Lean4 — formal proof bridge (`src/core/formal_proof_hardening.py`)
  - Z3 — SMT bounds verification (`src/core/z3_pentad_checker.py`)
  - SymPy — symbolic metric bridge (`src/core/symbolic_metric.py`)
  - XDiag — quantum many-body simulation (`src/quantum/xdiag_bridge/`)
  - W&B — experiment tracking (`src/core/wandb_logger.py`)
- All physical quantities in **natural units** (Planck units unless otherwise noted)
- Every new module must have a corresponding test file
- Test files live in `tests/` (for core physics modules) or alongside the module (for Unitary Pentad)
- **0 test failures is a hard requirement** — never merge code that breaks existing tests
- Use `@pytest.mark.slow` for tests that take > 2 seconds (Richardson extrapolation, etc.)
- Constants live at module top level in ALL_CAPS; derived in `__init__`

## Key Constants

```python
# Core physics
WINDING_NUMBER = 5          # n_w; selected by Planck nₛ data
K_CS = 74                   # = 5² + 7² = k_cs; selected by birefringence data
BRAIDED_SOUND_SPEED = 12/37 # c_s; from (5,7) braid resonance

# Predictions
N_S = 0.9635                # CMB spectral index (Planck: 0.9649 ± 0.0042 ✅)
R_BRAIDED = 0.0315          # tensor-to-scalar ratio (BICEP/Keck < 0.036 ✅)
# Birefringence: β ∈ {≈0.273°, ≈0.331°} canonical / {≈0.290°, ≈0.351°} derived
# ToE score: 100% (28.0/28) — 1 external measurement window open (LiteBIRD ~2032)

# Unitary Pentad
XI_C = 35/74                # Ξ_c consciousness coupling constant
SENTINEL_CAPACITY = 12/37   # per-axiom entropy capacity
SUM_OF_SQUARES_RESONANCE = 74  # = 5² + 7²
HIL_PHASE_SHIFT_THRESHOLD = 15  # saturation: n ≥ 15 aligned HIL operators
```

## Epistemics — What Is and Isn't a Physics Claim

**Hardgated physics claims (Pillars 1–208, `src/core/`, `tests/`, `recycling/`):**
- All modules are geometric derivations from the 5D metric ansatz
- Honest gaps are documented in `FALLIBILITY.md`
- The cold fusion module (Pillar 15) is explicitly framed as a falsifiable COP prediction, NOT a confirmation that LENR occurs

**Adjacent research tracks (Pillars 218–232, `src/core/pillar218_*` … `pillar232_*`):**
- Honest quantitative explorations connecting UM geometry to applied domains
- NOT hardgate physics claims; labeled 🔵 ADJACENT TRACK throughout
- Have full test suites and markdown documentation; do NOT affect the core ToE score

**Quantum simulation lane (`src/quantum/`):**
- Fermi–Hubbard and XDiag bridge are non-hardgate adjacent tracks
- Require steward approval before any formal pillar numbering

**NOT physics claims (`Unitary Pentad/`):**
- The Pentad is an independent governance/HILS framework
- It borrows mathematical structure from the Unitary Manifold but does NOT depend on the physics being correct
- See `SEPARATION.md` for the precise boundary

## Authorship Standard

Every substantive **document** (`.md`, `.tex`, `.pdf`, `AUTHORS`, `LICENSE` preamble) may end with:
> *Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
> *Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

**Do not** include this two-sentence credit inside Python source file docstrings or test file
docstrings. The legal copyright is carried by the `# Copyright (C) 2026  ThomasCory Walker-Pearson`
SPDX header at the top of every `.py` file — that is the authoritative, legally meaningful
attribution for source and test files.

## Known Open Problems (Do Not Try to "Fix" by Hiding Them)

1. CMB power spectrum amplitude suppressed ×4–7 at acoustic peaks — documented in `FALLIBILITY.md` (Admission 2; addressed by Pillars 57+63)
2. n_w = 5 uniqueness not yet proved from first principles alone — Steps 1–3 in Pillar 67 narrow to {5,7}; Planck nₛ provides the final selection (Admission 3 in `FALLIBILITY.md`)
   - Note: φ₀ self-consistency was **closed** by Pillar 56 (`src/core/phi0_closure.py`) and is no longer an open problem
3. DESI Year 2 tension on dark energy EoS (wₐ≠0) vs KK prediction wₐ=0 — tracked in `docs/CLAIM_MASTER_BOARD.md`
4. XDiag bridge and Fermi–Hubbard lane are IN DEVELOPMENT (non-hardgate) — see `STATUS.md §Side projects`

## Falsification Conditions

**The birefringence β ∈ {≈0.273°, ≈0.331°} prediction will be tested by LiteBIRD (launch ~2032).**
Any β outside the admissible window [0.22°, 0.38°], or landing in the predicted gap [0.29°–0.31°], falsifies the braided-winding mechanism. This is the primary falsifier; do not weaken this statement in any document.

## AI Ethics Note

This repository was built by a human-AI collaboration under the HILS (Human-in-the-Loop Systems)
framework documented in `5-GOVERNANCE/co-emergence/`. The AI (Copilot) was responsible for code architecture,
test suites, and document synthesis; the human (ThomasCory Walker-Pearson) was responsible for
scientific direction, theory, and judgment. This role partition is documented in every file.
