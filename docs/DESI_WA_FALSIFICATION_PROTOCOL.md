# DESI w_a Falsification Protocol — Pre-Registered

*Unitary Manifold v24.5 — Red-team accountability document.*  
*Created: 2026-08-25 per red-team honest accountability sprint.*  
*Author: GitHub Copilot (AI), scientific direction: ThomasCory Walker-Pearson.*

> This document pre-registers the exact falsification conditions for the Unitary Manifold
> dark energy sector. It cannot be modified after DESI DR3 is published without an explicit
> versioned amendment record.

---

## The UM Dark Energy Prediction

The Unitary Manifold predicts a frozen-radion dark energy equation of state:

```
w₀ = −1 + (2/3) c_s²  ≈  −0.9302    [no free parameters; c_s = 12/37]
w_a = 0                              [frozen radion — no evolution]
```

This is a CPL (w₀, w_a) point at (−0.9302, 0).

**Important caveats:**
- The identification of w_KK with the *present-day* dark energy EoS is an **ansatz**, not a
  derivation. No calculation spanning ~60 e-folds from inflation to today exists in the framework.
- The braided sound speed c_s = 12/37 is an inflationary-era parameter. Its persistence to
  late-time dark energy is motivated but not proved.
- See `FALLIBILITY.md §4.4` for the full honest status.

---

## Current Tension Status (DESI DR2, as of v24.5)

The correct comparison is the DESI CPL fit (w_a free), not the DESI w₀CDM fit (w_a forced to 0).
Using the w₀CDM fit to "validate" the UM's w_a=0 prediction is circular — both assume w_a=0
by construction.

| Quantity | UM Prediction | DESI DR2 CPL Value | Current Tension |
|----------|--------------|-------------------|----------------|
| w₀ | −0.9302 | −0.838 ± 0.072 | ~1.28σ |
| w_a | 0 (frozen) | −0.62 ± 0.30 | **2.07σ** |
| 2D joint (CPL ellipse) | (−0.9302, 0) | ρ(w₀,w_a) = −0.97 | **~2.30σ** |

**Status: LIVE FALSIFIER — below threshold but rising.**

---

## Pre-Registered Falsification Conditions

### Condition F-DE1: 1D w_a falsification (primary)
**If** the DESI DR3 (or any subsequent published result with comparable precision)
measures w_a and the tension between w_a(DESI) and w_a(UM)=0 exceeds **3.0σ**:

→ The UM frozen-radion dark energy sector is **FALSIFIED**.

This means: if DESI DR3 confirms w_a = −0.62 with σ(w_a) ≤ 0.207, the UM dark energy
prediction is falsified at the pre-registered threshold.

### Condition F-DE2: 2D joint falsification (secondary)
**If** the 2D CPL joint tension between the DESI CPL ellipse and the frozen-radion
point (w₀ = −0.9302, w_a = 0) exceeds **3.0σ** in properly computed χ²:

→ The UM frozen-radion dark energy sector is **FALSIFIED**.

### Condition F-DE3: w₀ falsification (tertiary)
**If** a future w₀CDM measurement with σ(w₀) < 0.03 places the UM prediction
w₀ = −0.9302 outside the 3σ window (i.e., w₀ < −1.02 or w₀ > −0.84 at 3σ):

→ The UM dark energy w₀ prediction is **FALSIFIED**.

---

## Projected Tension at DESI DR3

If the DESI DR2 central value w_a = −0.62 holds in DR3:
- Statistical uncertainty shrinks as ~1/√N_modes
- Estimated DR3 σ(w_a) ≈ 0.17–0.20 (depending on additional data vectors)
- Projected 1D tension: |0 − (−0.62)| / 0.17 ≈ **3.6σ**
- Projected 2D tension: > 3.0σ
- **This would cross the pre-registered falsification threshold.**

DESI DR3 is expected 2026–2027.

---

## What Would NOT Falsify the DE Sector

- DESI DR3 measuring w_a = −0.62 ± 0.30 (same as DR2): tension at 2.07σ — below threshold
- Any measurement consistent with w_a = 0 at < 3σ
- Roman Space Telescope measuring w₀ closer to −0.93 than to −1.00

---

## Response Protocol

If DESI DR3 crosses the 3σ falsification threshold:

1. Update `FALLIBILITY.md` §4.4 with: `DARK_ENERGY_SECTOR: FALSIFIED — DESI DR3 w_a tension ≥ 3σ`
2. Update `docs/CLAIM_MASTER_BOARD.md` dark energy row to FALSIFIED
3. Update `VERIFY.py` Check 13 to report FAIL
4. Retire the frozen-radion dark energy prediction from all public-facing summaries
5. Investigate whether the breathing-mode quintessence extension (Pillar 808) can accommodate
   the observed w_a without new free parameters

---

## Code Implementation

The monitoring check is in `VERIFY.py` Check 13, which now reports:
- DESI DR2 CPL w_a tension (2.07σ) with the pre-registered 3σ threshold
- The circular w₀CDM comparison is labeled explicitly as non-validating

The underlying physics is in:
- `src/core/kk_radion_dark_energy.py` — `roman_um_dark_energy_eos()`, tension functions
- `src/core/pillar428_desi_cpl_consistency_audit.py` — six-issue DESI audit
- `src/core/kk_de_wa_cpl.py` — joint 2D CPL tension calculation

---

## Amendment Record

| Date | Change | Trigger |
|------|--------|---------|
| 2026-08-25 | Document created, thresholds pre-registered | Red-team accountability sprint |

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Document engineering and synthesis: **GitHub Copilot** (AI).*
