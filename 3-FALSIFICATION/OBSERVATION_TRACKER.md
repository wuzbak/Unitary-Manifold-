# OBSERVATION_TRACKER.md — Unitary Manifold Prediction Registry

*Living document — update within 30 days of any new observational result.*  
*Last updated: 2026-07-09 (v19.0 — Pillar 543 DESI DR3 Decision-Day Readiness: routing rehearsal complete (5 synthetic scenarios, all branches verified), live tension 2.30σ (DR2 CPL-corrected), falsification threshold σ≥3.0, DR3 expected late 2026, preregistration hash recorded; Pillar 544 P17 Δm²₃₁ routing: JUNO Phase 1 best projection 3.33σ above 2.411e-3 eV², ARCHITECTURE_LIMIT_CERTIFIED; no primary falsifier window changed; full regression 47,424 passed · 23 skipped · 12 deselected · 0 failed.)*
*See `STEWARDSHIP.md §3.2` for the data integration protocol.*  
*Self-executing check: `python src/core/falsification_check.py --beta [value] --sigma [uncertainty]`*

> **Dual-publication system active (v10.28+):** This tracker is the
> observation-by-observation routing layer. All claims are simultaneously
> published at:
> - `docs/TRUTH_LAYER.md` — full derivation context and gap accounting
> - `docs/GATEKEEPER_SUMMARY.md` — concise PASS/TENSION/FALSIFIED verdicts
> - `docs/CLAIM_MASTER_BOARD.md` — canonical single-source claim registry
>
> All five finish-line lanes are active simultaneously:
> - **Lane A:** P16 closure hardgate
> - **Lane B:** P28 / α_GW architecture frontier
> - **Lane C:** Observational integration (DESI DR2/DR3, CMB-S4, JUNO, Hyper-K, LiteBIRD)
> - **Lane D:** Stress / robustness protection
> - **Lane E:** Truth-sync docs and release governance
>
> No lane is queued behind another. All run concurrently.

> **Lane C orchestration adjacent-track spec (Pillar 247):**
> `3-FALSIFICATION/PILLAR247_UNIFIED_OBSERVATION_INGEST_AND_VERDICT_ROUTING_ENGINE.md`
> defines the deterministic multi-observatory ingest + verdict router (DESI,
> ACT/SPT/CMB-S4, JUNO/Hyper-K, LiteBIRD, and lab substitutes) with explicit
> separation guard (`🔵 ADJACENT TRACK`, non-hardgate).

---

> **Operational hardening note:** Same-day decision routing is now backed by executable adjacent-track packs (`desi_dr3_publication_day_runbook.py`, `litebird_synthetic_rehearsal.py`, `lab_cp_execution_report.py`) and final sprint aggregation (`proof_close_certification_report.py`) for deterministic verdict handoff.

> **v11.4 freshness note:** Canonical observation-routing surfaces are synchronized to the 2026-05-19 branch state. Residual execution priority remains `T3 → A3 → SC2 → SC4`; all observational falsifier windows and same-day routing rules are unchanged.

> **v15.3 freshness note:** P503–P506 add machine-readable PMNS, lattice-braid, nEDM@SNS, and HL-LHC audit/tripwire surfaces. P505 records the nEDM@SNS 2028 adjacent-track band; P506 records the HL-LHC Run-4 m_G_KK ≥ 5 TeV routing. No primary falsifier window changed.

> **v15.2 freshness note:** P495–P501 keep DESI DR3, SO DR1, JUNO, SPHEREx, HL-LHC, CMB amplitude, and CKM residual windows active. P502 adds a completion audit only; it does not alter any observational prediction or falsification threshold.

## Decision Tree (LiteBIRD / CMB-S4)

```
Measure β:
├── β < 0.22° at ≥ 3σ  ──→  FALSIFIED  (braided-winding mechanism excluded)
├── β ∈ (0.29°, 0.31°) at ≥ 3σ  ──→  FALSIFIED  (inter-sector gap; neither branch consistent)
├── β > 0.38° at ≥ 3σ  ──→  FALSIFIED  (braided-winding mechanism excluded)
├── β ≈ 0.331° ± 0.02°  ──→  (5,7) PRIMARY SECTOR SUPPORTED
├── β ≈ 0.273° ± 0.02°  ──→  (5,6) SHADOW SECTOR SUPPORTED
└── β ∈ [0.22°, 0.38°] but not near 0.273° or 0.331°  ──→  CONSISTENT, NOT DISCRIMINATING
```

Execute immediately with: `python src/core/falsification_check.py --beta VALUE --sigma UNCERTAINTY`

Parallel immediate lane: execute decision-grade lab falsifier conditions
F-LAB-CP-1..4 from `3-FALSIFICATION/LAB_LITEBIRD_SUBSTITUTE_PROTOCOL.md`
and `3-FALSIFICATION/LAB_SCALE_CP_VIOLATION_FALSIFIER.md`.

---

## Primary Predictions

| # | Prediction | Observable | Predicted Value | Experiment | Expected Date | Status | Last Updated | Action Required |
|---|-----------|------------|----------------|------------|---------------|--------|--------------|-----------------|
| **P1** | Cosmic birefringence — (5,7) primary sector | β (polarization rotation angle) | **0.331° ± 0.007°** | LiteBIRD (primary) + lab substitute lane (parallel) | ~2032 (LiteBIRD), active now (lab lane) | 🟡 PENDING — consistent with current hint β=0.35°±0.14° | 2026-05-09 | Run `falsification_check.py` for LiteBIRD and enforce F-LAB-CP-1..4 in `LAB_LITEBIRD_SUBSTITUTE_PROTOCOL.md` |
| **P1b** | Cosmic birefringence — (5,6) shadow sector | β | **0.273° ± 0.007°** | LiteBIRD (primary) + lab substitute lane (parallel) | ~2032 (LiteBIRD), active now (lab lane) | 🟡 PENDING — second viable lossless branch | 2026-05-09 | Await LiteBIRD sector discrimination; keep lab decision-grade CP campaign running in parallel |
| **P2** | CMB scalar spectral index | nₛ | **0.9635** | Planck 2018, ACT DR6, SPT-3G | Ongoing | 🟢 CONSISTENT — Planck: 0.9649±0.0042 (0.33σ) | 2026-05-04 | Monitor if error bar tightens below ±0.002; check ACT DR6 |
| **P3** | Tensor-to-scalar ratio (braided) | r | **0.0315** | BICEP/Keck, ACT DR6, SPT-3G, Simons Observatory, CMB-S4 | ~2027 (SO), ~2030 (CMB-S4) | 🟠 HIGH_TENSION — BICEP/Keck: r<0.036 ✓; SPT-3G: r<0.036 ✓ (CONSISTENT); ACT DR6 (2024): r<0.016 (95%CL) → UM r=0.0315 exceeds bound by ~2×; P2 falsifier NOT triggered (P2 condition: r<0.010 at ≥3σ *measured*, not upper-bounded); SO preregistered: CONSISTENT if r_meas≥0.020; FALSIFIED if r<0.010 at ≥3σ | 2026-05-20 | Await Simons Observatory DR1 (~2027) — first measurement-capable instrument; SO 5-yr should detect r at ~10σ if UM correct; CMB-S4 (~2030) definitive |
| **P4** | Dark energy equation of state | wₐ (CPL parametrization) | **wₐ = 0, w₀ = −1** (frozen radion; single coherent mechanism) | DESI Year 3 / DR2; DR3 | DR2 published (arXiv:2503.14738); DESI 5-yr complete Apr 2026; DR3 expected late 2026 | 🟠 HIGH_TENSION — DESI Y3/DR2 CPL (wₐ free): wₐ = −0.62±0.30 → **2.07σ**; w₀ = −0.838±0.072 → 2.25σ; combined BAO+CMB+SNe: 2.75σ; 2D joint χ² (ρ=−0.97): **≈ 2.30σ** (correlation reduces tension for frozen-radion point); NOT falsified. **Pillar 428 correction:** w₀CDM comparison (0.11σ) is circular and is retired; correct comparison uses CPL fit (wₐ free). | 2026-05-25 | **PILLAR 428 CORRECTED:** strict ingest + mock-drill implemented; correct comparison = CPL fit (NOT w₀CDM); route DESI DR3 within 30 days; sync `kk_de_wa_cpl.py`, `pillar428_desi_cpl_consistency_audit.py`, this tracker, and canonical falsifier feed same day |

> **DESI Y3 Routing Protocol (execute immediately on publication):**
> ```python
> # src/core/desi_year3_monitor.py — run with actual Y3 values
> route_desi_y3(wa, sigma):
>     if sigma >= 3.0 and abs(wa) > 0:
>         verdict = "FALSIFIED — frozen radion mechanism excluded; wₐ≠0 confirmed"
>         # Required action: mark P28/T1 FALSIFIED in CLAIM_MASTER_BOARD.md
>         # Required action: open retraction issue; update WAVE_CHANGELOG.md
>     elif sigma >= 2.5:
>         verdict = "HIGH TENSION — imminent falsification risk; escalate monitoring"
>     elif sigma < 2.1:
>         verdict = "RESOLVED — tension reduced; frozen radion consistent"
>     else:
>         verdict = "TENSION MAINTAINED at {sigma}σ — monitor Y4"
>     # Update: OBSERVATION_TRACKER.md, CLAIM_MASTER_BOARD.md, TRUTH_LAYER.md same day
> ```
> Full truth context: `docs/TRUTH_LAYER.md §3 T1`

> **DESI escalation matrix (v11.2 canonical):**
>
> | Condition | Verdict | Required same-day updates |
> |---|---|---|
> | σ ≥ 3.0 with wₐ ≠ 0 | **FALSIFIED** | `docs/CLAIM_MASTER_BOARD.md` (T1), `docs/TRUTH_LAYER.md` §3, `docs/GATEKEEPER_SUMMARY.md`, `docs/WAVE_CHANGELOG.md` |
> | 2.5 ≤ σ < 3.0 | **HIGH_TENSION** | Keep T1 as HIGH_TENSION and maintain 30-day ingest cycle |
> | 2.1 ≤ σ < 2.5 | **TENSION** | Keep T1 as TENSION and monitor DR3/Year-5 |
> | σ < 2.1 | **RESOLVED** | Downgrade T1 tension flags and record closure in changelog |
>
> Canonical source row for T1 status: `docs/CLAIM_MASTER_BOARD.md` (Lane C).
| **P5** | CMB acoustic peak amplitude | A_s | Suppressed ×4.2–6.1 vs ΛCDM (α_GW Casimir target band 4.2e-10–4.8e-10; Pillar 52 fixes the gravity-scale decade and the 10D bridge gives α_GW≈4.49e-10) | Planck, CMB-S4 | ~2030 | 🟢 CLOSED_WITH_PILLAR52_10D_BRIDGE — framework closure achieved; the RS1-only undershoot is retained as provenance, while the live missing link is resolved by the Pillar 52 + 10D bridge | 2026-05-09 | Maintain closed status under hardgate policy; re-open only if future 10D consistency gates fail or the Pillar 52 normalization anchor is invalidated |
| **P6** | PMNS solar mixing angle (Route A + RS see-saw cross-route) | sin²θ₁₂ | **0.302252** Route A baseline + RS see-saw cross-route packet (`src/core/pmns_seesaw_5d.py`) | Ongoing neutrino experiments | Ongoing | 🟢 CONSISTENT — Route A remains canonical (1.55% from PDG 0.307); v10.52 adds RS see-saw cross-route closure surface in CKM/PMNS lane | 2026-05-11 | Monitor NuFIT updates; keep Route A canonical and use see-saw lane as executable cross-check |
| **P7** | Cold fusion: φ-enhanced Gamow factor / COP | Excess heat at predicted COP | Falsifiable COP prediction (Pillar 15) | Calorimetry experiments | Ongoing | 🟡 PENDING — no confirmed measurement; prediction explicitly framed as falsifiable | 2026-05-04 | Monitor LENR experimental literature |
| **P8** | Lab-scale CP asymmetry in certified (5,7) condensed matter | \(A_{CP}^{lab}=(\Gamma_+-\Gamma_-)/(\Gamma_++\Gamma_-)\) | **Order \(10^{-5}\)** (geometry-transfer target from \(J_{geo}\)) | JJ/SQUID arrays; topological-insulator winding devices | Now | 🟡 PENDING — no decision-grade \(\sigma_A\le10^{-5}\) campaign logged yet | 2026-05-09 | Execute canonical substitute lane in `src/core/lab_litebird_substitute.py` and `3-FALSIFICATION/LAB_LITEBIRD_SUBSTITUTE_PROTOCOL.md`; falsify on F-LAB-CP-1..4 at decision-grade controls |

| **P9** | 6D baryogenesis adjacent-track nEDM | neutron EDM d_n | Pillar 505 band around ~10⁻²⁶–10⁻²⁷ e·cm with sub-10% internal uncertainty | nEDM@SNS | ~2028 | 🟡 PENDING 🔵 — adjacent-track, no ToE hardgate impact | 2026-06-01 | Use `src/core/pillar505_sixd_baryogenesis_phase3_nedm.py`; route result without changing core falsifier windows |
| **P10** | LHC gluon-channel KK graviton audit | m_G_KK exclusion / dilepton-gluon channel | formal routing bound m_G_KK ≥ 5 TeV | HL-LHC Run 4 | 2029–2033 | 🟡 PENDING — Admission 10 routing, no current exclusion | 2026-06-01 | Use `src/core/pillar506_lhc_gluon_channel_formal_audit.py`; reroute Admission 10 if G_KK excluded below 5 TeV at ≥2σ |

---

## Secondary / Derived Predictions

| # | Prediction | Observable | Predicted Value | Status | Notes |
|---|-----------|------------|----------------|--------|-------|
| **D1** | k_CS = 74 (Chern-Simons level) | Algebraic — no direct observable | 5² + 7² = 74 | ✅ DERIVED — algebraic identity (Pillar 58, 99-B) | Confirmed indirectly via β prediction |
| **D2** | n_w = 5 winding number | Cosmological (nₛ, r) | Pure theorem from Z₂ orbifold | ✅ PROVED — pure theorem (Pillars 39, 67, 70-B, 70-D) | No observational input required |
| **D3** | SU(3)_C × SU(2)_L × U(1)_Y from geometry | SM gauge group | n_w=5 → SU(5) → Kawamura Z₂ orbifold | ✅ DERIVED (Pillar 148) | |
| **D4** | Higgs VEV from geometry | v_EW = 246.22 GeV | Within 0.10% | ✅ DERIVED (Pillar 139) | |
| **D5** | sin²θ_W, αs from SU(5) orbifold | EW mixing angle | GUT-scale derivation | ✅ PROVED (Pillar 94) | |
| **D6** | Λ_QCD from AdS/QCD KK spectrum | QCD confinement scale | ρ meson as first KK gluon: 198 MeV vs PDG 332 MeV (factor 1.7) | 🟡 CONSTRAINED — AdS/QCD order-of-magnitude (dilaton factor input) | Pillar 162 |
| **D7** | A_s normalization: Casimir energy naturally bounds α_GW | CMB amplitude | α_GW ∈ [4.2×10⁻¹⁰, 4.8×10⁻¹⁰] (Casimir bound interval) | 🟡 CONSTRAINED — bounded to factor-5 envelope; exact UV-brane closure still open | Pillar 165 + v10.28 α_GW closure attempt |

---

## ADM / Framework Structural Gaps

| # | Gap | Status | Module | Action |
|---|-----|--------|--------|--------|
| **G1** | ADM 3+1 decomposition of time parameterization | 🟢 QUANTITATIVE_CLOSURE — dS/dt = φ × K × A_horizon / (4G): quantitative entropy production rate derived from ADM 3+1 evolution of 5D KK metric (Pillar 107); formula evaluated with canonical UM values (φ₀≈10π, H₀=67.4 km/s/Mpc); geometric second law verified numerically; 40 tests pass. | `src/core/adm_entropy_production_rate.py` (Pillar 107); `src/core/adm_decomposition.py` (Pillar 100) | Run `quantitative_aot_closure()` to verify verdict |
| **G2** | CMB peak amplitude suppression ×4.2–6.1 | 🟢 CLOSED_WITH_PILLAR52_10D_BRIDGE — the historical 5D RS1 UV estimate remains ~4.3×10⁻⁶⁵ for provenance, Pillar 52 fixes the absolute gravity-scale decade at α_eff≈9.79×10⁻¹⁰, and the 10D UV completion package computes c_UV≈5.42×10⁵⁴ with α_GW≈4.49×10⁻¹⁰ in-band; consistency gates pass; robustness overlap=1.0; the missing link is treated as resolved. CMB-S4 still cannot distinguish point values inside the interval. | `src/core/cmb_acoustic_amplitude_rg.py`, `src/core/alpha_gw_casimir_closure.py`, `src/core/alpha_gw_uv_brane_derivation.py`, `src/core/alpha_gw_pillar52_10d_bridge.py`, `src/core/alpha_gw_10d_uv_completion.py` | Maintain closed status under hardgate policy; re-open only if future 10D consistency gates fail or the Pillar 52 normalization anchor fails. |
| **G3** | DESI wₐ = 0 vs DESI Year 3 / DR2 HIGH TENSION | 🟠 HIGH_TENSION — **Pillar 428 corrected:** DESI Y3/DR2 CPL (arXiv:2503.14738, March 2025): BAO-only wₐ = −0.62±0.30 → 2.07σ; combined BAO+CMB+SNe wₐ ≈ −0.55±0.20 → 2.75σ; 2D joint (ρ=−0.97): ≈ 2.30σ (correlation REDUCES tension for frozen-radion point). w₀CDM comparison (0.11σ) is CIRCULAR (both UM and DESI w₀CDM fit have wₐ = 0) and is retired. Frozen radion predicts wₐ = 0; neither BAO-only nor combined reaches 3σ falsification threshold. NOT FALSIFIED. | `src/core/kk_de_wa_cpl.py`, `src/core/pillar428_desi_cpl_consistency_audit.py`, `src/core/desi_year3_monitor.py`, `src/core/desi_dr2_gap_report.py` (Pillars 155, 160, 428) | **PILLAR 428 AUDIT (2026-05-25):** six-issue correction applied; 2D tension with ρ=−0.97 shows ~2.30σ (reduced from naive 3.06σ); inflationary w₀ point gives 3.63σ 2D (correlation increases for off-axis point); await DESI DR3 (late 2026). |
| **G4** | sin²θ₁₂ Route A consolidation | ✅ CLOSED (v10.27) — Route A (1.55% from PDG); Route B (4/15, 13% residual) retired as incomplete GUT BC | `src/core/neutrino_p18_route_consolidation.py` | P18 promoted to GEOMETRIC_PREDICTION in mas_tracker v10.27 |

---

## Observational Record

*This section records every integration of new data into the framework.*

| Date | Observation | Result | Impact | Reference | Action Taken |
|------|------------|--------|--------|-----------|--------------|
| 2020 | Minami & Komatsu birefringence | β = 0.35° ± 0.14° | CONSISTENT — (5,7) sector prediction 0.331° within 1σ of central value | arXiv:2011.11612 | Used as validation reference in `inflation.py` |
| 2022 | Diego-Palazuelos et al. birefringence | Independent confirmation β ≈ 0.35° | CONSISTENT — reconfirms existing result | arXiv:2201.07241 | Noted in FALLIBILITY.md |
| 2022 | BICEP/Keck r < 0.036 | Tensor-to-scalar ratio constraint | CONSISTENT — r_braided = 0.0315 satisfies bound | arXiv:2203.16556 | Resolved Admission 3 in FALLIBILITY.md (Pillar 27) |
| 2018 | Planck nₛ = 0.9649 ± 0.0042 | CMB spectral index | CONSISTENT — predicted 0.9635 is 0.33σ from central value | Planck 2018 X | Reference value in `inflation.py` |
| 2024 | DESI Year 1 dark energy | wₐ ≠ 0 at 2.1σ | 🟠 TENSION — UM predicts wₐ = 0 (frozen radion) | arXiv:2404.03002 | Flagged as OPEN in Pillar 155/160; tracked as G3 above |
| 2025 | DESI DR2 = Year 3 BAO-only (arXiv:2503.14738) | w₀ = −0.838 ± 0.072, wₐ = −0.62 ± 0.30 | 🟠 TENSION — BAO-only: 2.07σ on wₐ; below 3σ falsification threshold; UM wₐ=0 NOT FALSIFIED | DESI Collaboration (2025), arXiv:2503.14738 | `src/core/desi_dr2_gap_report.py::execute_dr2_bao_routing()` executed; route=TENSION; sync kk_de_wa_cpl.py and canonical falsifier feed |
| 2025 | DESI DR2 = Year 3 BAO+CMB+SNe combined (arXiv:2503.14738) | wₐ ≈ −0.55 ± 0.20 (combined), significance up to 3-4σ vs ΛCDM | 🟠 HIGH_TENSION — combined analysis: 2.75σ from UM wₐ=0; still below 3σ UM-falsification threshold; NOT FALSIFIED | DESI Collaboration (2025), arXiv:2503.14738 | `src/core/desi_dr2_gap_report.py::execute_dr2_combined_routing()` executed; route=TENSION (2.75σ < 3σ). If DR3 confirms wₐ ≈ −0.62 with σ=0.18 → 3.44σ FALSIFIED. |
| 2022 | SPT-3G 2022 (South Pole Telescope) | nₛ (SPT-3G+Planck) = 0.9657 ± 0.0040; r < 0.036 (SPT-3G+BK 95%CL) | nₛ: 🟢 CONSISTENT — UM 0.9635 is 0.55σ from central value; r: 🟢 CONSISTENT — UM r=0.0315 < 0.036 bound | Balkenhol et al. 2023, arXiv:2212.05642; Dutcher et al. 2021, arXiv:2109.11953 | SPT-3G independently confirms CONSISTENT on n_s and r. Second ground-based instrument to verify CONSISTENT status. ACT DR6 remains the only HIGH_TENSION data point. Pillar 297 routing registered. |
| 2024 | Hyper-Kamiokande — first operation year | No proton decay signal yet (first data run). SK limit holds: τ(p→e⁺π⁰) > 2.4×10³⁴ yr. | 🟡 OBSERVABLE_WINDOW_OPEN — UM predicts τ ≈ 5×10³⁴ yr; HK sensitivity grows linearly with exposure. First-year HK sensitivity ~5×10³⁴ yr. | Hyper-K Collaboration (2024); arXiv:1805.04163 (design report) | Run `proton_decay_timeline_report()` from Pillar 299 when HK publishes annual limit updates. Year-by-year routing table preregistered at v11.9/v11.10. |

---

## Upcoming Observation Schedule

| Date | Experiment | Observable | UM Prediction | σ Resolution | Action |
|------|-----------|------------|---------------|--------------|--------|
| **2025 (published)** | **DESI DR2 = Year 3 (EXECUTED)** | wₐ, w₀ | wₐ = 0 | BAO-only: 2.07σ TENSION; combined: 2.75σ HIGH_TENSION; both < 3σ | **ROUTING EXECUTED 2026-05-09** — `src/core/desi_dr2_gap_report.py::full_dr2_gap_report()` run; verdict: NOT FALSIFIED. 7-scenario DR3/Y5 table built. **v12.5 UPGRADE (P367):** routing now uses canonical w₀=−1 (prior routing used deprecated w_KK≈−0.930). Roman Space Telescope lane added (σ_w₀≈0.02, σ_wₐ≈0.10). Run `desi_dr3_canonical_routing()` within 30 days of DR3. |
| ~2026 | **SPHEREx f_NL** | **f_NL^equil** | **f_NL ∈ [−3, 0] (DBI + KK braid correction; NEW PREDICTION P375)** | σ(f_NL) ~ 0.5–5 | Run `src/core/pillar375_fnl_non_gaussianity.py::fnl_prediction()`. Planck 2018 consistent (f_NL=−26±47). SPHEREx: borderline discriminator from ΛCDM (f_NL=0). FALSIFIED if f_NL > +10 at ≥3σ (rules out sub-luminal sound speed). |
| ~2027 | **Simons Observatory DR1 (UPGRADED v12.5)** | **r, nₛ** | **r = 0.0315; nₛ = 0.9635** | **σ_r ~ 0.006 (DR1), σ_ns ~ 0.004** | **PREREGISTERED (P298, P368). Run `so_dr1_joint_routing(r_meas, sigma_r)` within 24 hrs. CONFIRMED if r≥0.020 at ≥3σ; FALSIFIED if r<0.010 at ≥3σ. Joint composite posterior with ACT DR6 and SPT-3G implemented in P368.** |
| ~2027 | **JUNO (UPGRADED v12.5)** | **Δm²₃₁** | **2.452×10⁻³ eV² (NLO, P274; P369)** | ~0.5% | **PREREGISTERED (P369; SHA-256 hash committed). Run `juno_2027_verdict(dm31_measured, sigma)`. NLO residual 0.004% → CONSISTENT expected. FALSIFIED if |residual| ≥ 3σ_JUNO. Hyper-K 2028 cross-check protocol active.** |
| ~2027 | DESI DR3 / Y5 | wₐ | wₐ = 0 | Projected: σ_wₐ ~ 0.14–0.18 | Run `desi_dr3_canonical_routing()` on DR3 within 30 days (P367, canonical w₀=−1). Roman lane: `roman_routing()` with σ_w₀≈0.02, σ_wₐ≈0.10. |
| ~2027 | Roman Space Telescope | w₀, wₐ | w₀=−1, wₐ=0 | σ_w₀≈0.02, σ_wₐ≈0.10 (P367) | Run `roman_routing(w0, sigma_w0, wa, sigma_wa)`. FALSIFIED if |w₀+1|>3σ_w0 or |wₐ|>3σ_wa. |
| ~2027 | ACT DR6 joint w/ SPT-3G | r, nₛ | r = 0.0315; nₛ = 0.9635 | σ_r ~ 0.010 (joint) | Run `joint_actdr6_spt3g_preregistration()` from Pillar 297. CONSISTENT if r≥0.020; FALSIFIED if r<0.010 at ≥3σ. |
| ~2028 | Hyper-Kamiokande | Δm²₃₁ | 2.452e-3 eV² (NLO, P369) | ~1% | Run `hyperk_2028_verdict()` from P369. Hyper-K cross-check of JUNO verdict. |
| ~2029 | **Simons Observatory 5-yr** | **r, nₛ** | **r = 0.0315; nₛ = 0.9635** | **σ_r ~ 0.003, σ_ns ~ 0.002** | **PREREGISTERED (Pillar 298, v11.10). SO 5-yr should detect r at ~10σ if UM correct. Non-detection at ≥5σ sensitivity → P2 FALSIFIED if r<0.010.** |
| ~2030 | CMB-S4 | β, r, n_s | r = 0.0315; β ∈ {0.273°, 0.331°} | σ_r ~ 0.001, σ_ns ~ 0.002 | **Run `src/core/cmbs4_ns_r_joint_falsifier.py::joint_ns_r_verdict()`. FALSIFIED if r < 0.010 at 3σ or n_s ∉ [0.955, 0.972] at <0.001.** |
| ~2032 | **LiteBIRD** | **β** | **β ∈ {0.273°, 0.331°} ± 0.007°** | **σ_β ~ 0.02°** | **PRIMARY EVENT — run `src/core/litebird_gap_hardening.py::classify_beta()` and `falsification_check.py` immediately. Check inter-sector gap (0.29°, 0.31°) as separate falsifier.** |
| ~2032 | LiteBIRD | r | 0.0315 | σ_r ~ 0.001 | Secondary test; constrains braided sound speed |
| ~2034 | Hyper-K Year 10 | τ(p→e⁺π⁰) | τ_UM ≈ 5×10³⁴ yr (Pillar 293 central) | 90%CL limit ≥ 1×10³⁵ yr | Run `proton_decay_timeline_report()`. FALSIFIED if non-observation at year 10 with sensitivity > UM upper band (matrix-element × 1.69). |
| ~2035 | LISA | Ω_GW | ~10⁻¹⁵ | σ_Ω ~ 10⁻¹² (design) | Run `lisa_dr1_routing(omega_gw_measured, sigma)`. Non-detection → CONSISTENT. |

---

## How to Use This Document

1. **When new data arrives:** Update the relevant row in "Observational Record" within 30 days.
2. **When a gap closes:** Update the gap row and update FALLIBILITY.md simultaneously. Do not close a gap here without closing it in FALLIBILITY.md.
3. **When LiteBIRD publishes:** clear the `litebird_readiness_hardening.py` checklist, run `python src/core/falsification_check.py --beta VALUE --sigma UNCERTAINTY`, and record the verdict in this tracker and the canonical falsifier feed in the same update.
4. **Status codes:**
   - ✅ DERIVED / PROVED — mathematical theorem or algebraic identity
   - 🟢 CONSISTENT — observationally validated, not discriminating
   - 🟡 PENDING — prediction made; awaiting measurement
   - 🟠 TENSION — observational data disfavours but does not yet falsify (< 3σ)
   - 🔴 OPEN GAP — acknowledged gap; no current resolution
   - ❌ FALSIFIED — the prediction was tested and failed at ≥ 3σ

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
