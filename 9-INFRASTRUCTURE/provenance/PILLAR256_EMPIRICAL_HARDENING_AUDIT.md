# Pillar 256 Provenance Audit — Empirical Hardening & Falsification

Date: 2026-05-18

## Agent role map used for this implementation

1. **Agent 1 — Data Miner (Harvester)**
   - Gathered hard constants and source anchors for muon g-2, CMB r, Omega_Lambda / rho_Lambda, proton radius.
2. **Agent 2 — Logic Aggressor (Devil's Advocate)**
   - Enumerated edge-case inputs and fail-safe behavior (NaN/Inf guards, malformed windows, closure violations, overfit rejection).
3. **Agent 3 — Synthesizer (Builder)**
   - Integrated constants and stress-test logic into `src/core/pillar256_empirical_hardening_falsification.py`.
4. **Agent 4 — Falsification Auditor**
   - Produced measurable no-go thresholds, codified in `9-INFRASTRUCTURE/CRITICAL_FAILURE.md`.

## Strict provenance ledger

- Muon g-2 anchor: `a_mu(exp) = 116592059(22) x 10^-11`
  - Source: https://muon-g-2.fnal.gov/
- Tensor-to-scalar bound anchor: `r < 0.032 (95% CL)` and fixed prediction `r = 0.001`
  - Sources:
    - https://www.aanda.org/articles/aa/abs/2020/09/aa33910-18/aa33910-18.html
    - https://www.isas.jaxa.jp/en/missions/spacecraft/future/litebird.html
- Vacuum anchors:
  - `rho_lambda(obs) ~= (2.3 meV)^4`
  - `Omega_lambda(target) ~= 0.685`
  - Sources:
    - https://pdg.lbl.gov/
    - https://physics.nist.gov/constants
- Proton radius anchor:
  - `r_p = 0.84087(39) fm` (CREMA)
  - Source: https://doi.org/10.1126/science.1230016
- CERN Open Data falsification hooks:
  - https://opendata.cern.ch
  - https://opendata.cern.ch/search?experiment=NOMAD
  - https://opendata.cern.ch/search?experiment=CMS

## No-smoothing policy applied

- Muon g-2 mismatch is explicitly recorded as requiring refinement if over 5σ.
- No post-hoc parameter tuning was used to force proton-radius agreement; derivation is fixed from winding + Compton scale.
- Falsification thresholds are explicit and externally measurable.

## Hallucination guard

If any constant is changed without source update, this file must be updated in the same commit with:
- the exact new value,
- uncertainty and units,
- primary URL source,
- rationale for replacement.

## Reproducibility hardening additions (v1)

- Signed run manifests are now emitted per execution snapshot via:
  - `src/core/pillar256_reproducibility.py`
  - `9-INFRASTRUCTURE/scripts/pillar256_replay.py snapshot`
  - `2-REPRODUCIBILITY/pillar256/snapshots/<snapshot_id>/{snapshot.json,manifest.json}`
- Machine-readable CI threshold registry:
  - `docs/falsification/pillar256_thresholds.yml`
- Versioned threshold-governance ledger for consensus-driven revisions:
  - `docs/falsification/pillar256_threshold_governance.yml`
- Long-horizon gate trend panels:
  - `2-REPRODUCIBILITY/pillar256/trend_panels.json`
  - sourced from `2-REPRODUCIBILITY/pillar256/run_history.jsonl`
