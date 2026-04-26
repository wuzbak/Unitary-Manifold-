# GitHub Copilot Instructions — Unitary Manifold

This file provides context for GitHub Copilot and AI coding assistants working
on the Unitary Manifold repository.

## What This Repository Is

A 5-dimensional Kaluza-Klein physics framework with 66 geometric pillars, a complete
HILS governance framework (Unitary Pentad), and supporting AI assistant infrastructure.

**Theory:** ThomasCory Walker-Pearson (2026)  
**Implementation:** GitHub Copilot (AI)  
**Status:** Active research — all contributions must maintain 0 test failures

## Test Suite — Always Run Before and After Changes

```bash
# Fast suite (core physics, run first):
python -m pytest tests/ -q
# Expected: ~9933 passed, 2 skipped, 11 deselected, 0 failed

# Recycling suite:
python -m pytest recycling/ -q
# Expected: 316 passed, 0 failed

# Unitary Pentad suite:
python -m pytest "Unitary Pentad/" -q
# Expected: 1234 passed, 0 failed

# Full repository (takes ~90 seconds):
python -m pytest tests/ recycling/ "Unitary Pentad/" -q
# Expected: 11483 passed, 2 skipped, 11 deselected, 0 failed
```

## Repository Structure

```
src/core/           ← 5D metric, field evolution, KK geometry, braided winding (Pillars 1–5, 27–52)
src/holography/     ← holographic boundary, entropy-area (Pillar 4)
src/multiverse/     ← FTUM fixed-point iteration (Pillar 5, 29, 38)
src/consciousness/  ← coupled brain-universe attractor (Pillar 9)
src/atomic_structure/ src/cold_fusion/ src/chemistry/ src/astronomy/ (Pillars 10–15)
src/physics/        ← Pillar 15-B: lattice_dynamics.py (collective Gamow, phonon-radion bridge)
src/earth/ src/biology/ src/medicine/ src/justice/ src/governance/ (Pillars 12–13, 17–19)
src/neuroscience/ src/ecology/ src/climate/ src/marine/ (Pillars 20–23)
src/psychology/ src/genetics/ src/materials/ (Pillars 24–26, 46–47)
recycling/          ← Pillar 16: φ-debt entropy accounting
Unitary Pentad/     ← Independent HILS governance framework (18 modules)
tests/              ← 118 test files, ~9933 fast-passing tests (Pillars 1–66, all sub-pillars)
bot/                ← AI assistant infrastructure (RAG, Copilot Extension, Custom GPT)
co-emergence/       ← HILS framework documentation
```

## Coding Conventions

- **Python 3.12+**, numpy/scipy only (no deep learning frameworks in core)
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

# Unitary Pentad
XI_C = 35/74                # Ξ_c consciousness coupling constant
SENTINEL_CAPACITY = 12/37   # per-axiom entropy capacity
SUM_OF_SQUARES_RESONANCE = 74  # = 5² + 7²
HIL_PHASE_SHIFT_THRESHOLD = 15  # saturation: n ≥ 15 aligned HIL operators
```

## Epistemics — What Is and Isn't a Physics Claim

**Physics claims (in `src/`, `tests/`, `recycling/`):**
- All modules are geometric derivations from the 5D metric ansatz
- Honest gaps are documented in `FALLIBILITY.md`
- The cold fusion module (Pillar 15) is explicitly framed as a falsifiable COP prediction, NOT a confirmation that LENR occurs

**NOT physics claims (`Unitary Pentad/`):**
- The Pentad is an independent governance/HILS framework
- It borrows mathematical structure from the Unitary Manifold but does NOT depend on the physics being correct
- See `SEPARATION.md` for the precise boundary

## Authorship Standard

Every substantive document must end with:
> *Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
> *Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

## Known Open Problems (Do Not Try to "Fix" by Hiding Them)

1. CMB power spectrum amplitude suppressed ×4–7 at acoustic peaks — documented in `FALLIBILITY.md`
2. φ₀ self-consistency not fully closed analytically — documented in `FALLIBILITY.md`

## Falsification Conditions

**The birefringence β ∈ {≈0.273°, ≈0.331°} prediction will be tested by LiteBIRD (launch ~2032).**
Any β outside the admissible window [0.22°, 0.38°], or landing in the predicted gap [0.29°–0.31°], falsifies the braided-winding mechanism. This is the primary falsifier; do not weaken this statement in any document.

## AI Ethics Note

This repository was built by a human-AI collaboration under the HILS (Human-in-the-Loop Systems)
framework documented in `co-emergence/`. The AI (Copilot) was responsible for code architecture,
test suites, and document synthesis; the human (ThomasCory Walker-Pearson) was responsible for
scientific direction, theory, and judgment. This role partition is documented in every file.