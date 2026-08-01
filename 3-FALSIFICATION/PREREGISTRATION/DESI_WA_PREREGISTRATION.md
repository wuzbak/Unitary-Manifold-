# DESI wₐ Preregistration Packet

**Pillar 421 audit (v13.4, 2026-05-25) — corrected analysis applied. Current version: v20.1.**

- UM prediction: wₐ = 0 (frozen EW radion; m_r >> H₀ — single coherent mechanism)
- UM w₀ prediction: w₀ = −1 (frozen radion; same mechanism as wₐ = 0)
- Note: w_KK = −0.9302 applies to the INFLATIONARY epoch only and is NOT used here.

## Current observational status (DESI Year 3 / DR2)

**Dataset:** DESI Year 3 / DR2 (arXiv:2503.14738, March 2025)
**Fit used for comparison:** CPL (w₀ free; wₐ free) — the CORRECT independent comparison.
**Do NOT use:** w₀CDM fit (wₐ forced to 0) — circular comparison for wₐ = 0 predictions.

| Parameter | UM | DESI Y3/DR2 CPL | 1D Tension | 2D Joint |
|---|---|---|---|---|
| w₀ | −1 | −0.838 ± 0.072 | 2.25σ | — |
| wₐ | 0 | −0.62 ± 0.30 | 2.07σ | — |
| Joint | (−1, 0) | CPL, ρ = −0.97 | — | ≈ 2.30σ (ρ reduces tension) |

The DESI CPL anti-correlation ρ = −0.97 REDUCES the 2D tension for the frozen-radion
point from naive 3.06σ to correct 2.30σ. DESI's 3.9σ ΛCDM exclusion comes from
the full likelihood, not just the CPL summary statistics.

**Bayesian context:** P(|wₐ| < 0.10 | DESI Y3 combined) ≈ 1.2% — Bayesian evidence
consistently disfavours wₐ ≈ 0.

## Falsification criteria (unchanged)

- |wₐ| > 0 confirmed at ≥3σ in DESI DR3/Y5 → KK radion dark energy falsified
- Same finding from a second independent survey (EUCLID, LSST) → hard falsification

**Current status:** 2.07σ (BAO-only). NOT reached.
**Projected DR3:** If central value holds and σ_wₐ ≈ 0.12 → tension ≈ 5.2σ (FALSIFIED).

## DESI data version (Issue 5 of Pillar 428)

- **DESI Year 3 / DR2**: correct name for arXiv:2503.14738 (March 2025)
- **DESI DR3 / Y5**: Full 5-year analysis; expected late 2026 to 2027

## Same-day sync targets

- `src/core/kk_de_wa_cpl.py`
- `src/core/pillar428_desi_cpl_consistency_audit.py`
- `3-FALSIFICATION/OBSERVATION_TRACKER.md`
- `src/core/canonical_falsifier_evidence_feed.py`
- `FALLIBILITY.md` §4.4

## Version history

| Date | Version | Change |
|---|---|---|
| 2026-05-19 | v1 | Initial preregistration |
| 2026-05-25 | v2 | Pillar 428 six-issue audit: corrected comparison (CPL, not w₀CDM), 2D tension with ρ = −0.97, updated DESI naming (Y3/DR2), Bayesian context |

Timestamp: 2026-05-25T03:00:00Z
