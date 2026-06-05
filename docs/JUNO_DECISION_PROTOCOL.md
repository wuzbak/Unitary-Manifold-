# JUNO Decision Protocol

## Scope

Machine-readable monitoring protocol for the atmospheric neutrino mass-splitting lane,
focused on whether JUNO excludes the current Unitary Manifold (UM) baseline prediction for
\(\Delta m^2_{31}\).

## Current status

- **PDG central value:** \(\Delta m^2_{31,\mathrm{PDG}} = 2.453 \times 10^{-3}\ \mathrm{eV}^2\)
- **UM monitoring baseline used here:** \(\Delta m^2_{31,\mathrm{UM}} = 2.3995 \times 10^{-3}\ \mathrm{eV}^2\)
- **Absolute residual:** \(5.35 \times 10^{-5}\ \mathrm{eV}^2\)
- **Fractional residual:** **2.18%** below the PDG central value
- **Interpretation:** the present gap is small enough to monitor, but large enough that JUNO full-statistics precision can become decision-grade if the residual is irreducible.

## UM prediction vs PDG

| Quantity | Value |
|---|---:|
| UM baseline prediction | `2.3995e-3 eV^2` |
| PDG central value | `2.4530e-3 eV^2` |
| Absolute difference | `5.35e-5 eV^2` |
| Fractional residual | `2.18%` |
| Projected JUNO full-statistics precision | `0.5%` |
| Projected tension at 0.5% precision | `4.4σ` (more exactly `2.18 / 0.5 = 4.36σ`) |

## Monitoring lane references

- Existing adjacent-track tightening lane: `src/core/pillar274_juno_dm31_tightening.py`
- NLO + seesaw correction monitoring should be tracked under the **Pillar 274** lane and any direct follow-up monitor that supersedes it.
- This protocol treats the existing `pillar274_juno_dm31_tightening.py` module as the operative repository reference for the requested `pillar274_seesaw_nlo_monitor.py` role.

## Decision windows

| Window | Approx. date | Precision target | Expected interpretation |
|---|---|---:|---|
| JUNO Phase 1 | ~2026 | ~1.0% | Early warning only. A persistent 2.18% residual corresponds to ~2.2σ tension: monitor, do not formally falsify. |
| JUNO full statistics | ~2027 | 0.5% | Decision-grade window. If the 2.18% residual persists, projected tension is ~4.4σ and the atmospheric splitting derivation chain must be revised. |

## Exact falsification threshold

**If `Δm²₃₁_JUNO` excludes the UM prediction at `≥3σ`, the framework requires revision of the atmospheric mass-splitting derivation chain.**

This is a derivation-chain falsifier, not a reason to silently relabel the prediction. The update must be explicit, dated, and propagated to the framework's fallibility ledger.

## Response protocol

1. **30-day update rule:** within 30 days of any major JUNO release, update the repository monitoring status, residual table, and verdict language.
2. **Human steward escalation:** any tension at or above the escalation threshold must be surfaced to the human steward for adjudication.
3. **`FALLIBILITY.md` update required:** if the tension reaches the admission threshold, the repository must record the issue in `FALLIBILITY.md` with the observed central value, uncertainty, significance, and next-step plan.
4. **No silent reinterpretation:** the UM baseline number and the measured JUNO value must be shown side-by-side in the update.

## Remediation paths

- **If tension reaches `2.5σ`:** trigger an NLO correction sprint under the Pillar 274 follow-up lane, with explicit review of the NLO + seesaw correction budget.
- **If tension reaches `≥3σ`:** declare an admission, update `FALLIBILITY.md`, and initiate revision of the atmospheric mass-splitting derivation chain.
- **If tension falls back below `2σ`:** keep the lane open as monitored but non-critical; do not claim closure until the residual is shown to be theoretically reduced or empirically absorbed.

## Operational note

The present protocol is conservative. The monitoring trigger is tied to experimental exclusion significance, not to informal preference for a nearby fitted value. Pillar 274 remains the correct place to test whether NLO + seesaw corrections can absorb the residual before the `≥3σ` admission line is crossed.

## Machine-readable YAML

```yaml
monitor_id: JUNO_DM31_DECISION_PROTOCOL
observable: delta_m2_31
units: eV^2
status:
  pdg_central_value: 2.4530e-3
  um_prediction: 2.3995e-3
  absolute_residual: 5.35e-5
  fractional_residual_percent: 2.18
  projected_juno_precision_percent: 0.5
  projected_tension_sigma_at_full_statistics: 4.36
  public_rounding_label: 4.4σ
windows:
  - phase: JUNO Phase 1
    approximate_date: 2026
    precision_percent: 1.0
    projected_tension_sigma: 2.18
    decision: monitor_only
  - phase: JUNO full statistics
    approximate_date: 2027
    precision_percent: 0.5
    projected_tension_sigma: 4.36
    decision: revision_required_if_residual_irreducible
thresholds:
  escalation_sigma: 2.5
  falsification_sigma: 3.0
  exact_rule: If delta_m2_31_JUNO excludes the UM prediction at >=3σ, revise the atmospheric mass-splitting derivation chain.
response_protocol:
  update_deadline_days: 30
  escalate_to_human_steward: true
  fallibility_update_required: true
  silent_reinterpretation_allowed: false
remediation:
  tension_at_2p5sigma: trigger_pillar274_nlo_correction_sprint
  tension_at_3sigma_or_more: declare_admission_and_revise_derivation_chain
references:
  pillar274_monitor: src/core/pillar274_juno_dm31_tightening.py
  followup_role: Pillar 274 NLO+seesaw correction monitoring
```
