# Pillar 247 — Unified Observation Ingest & Verdict Routing Engine (UOIVR)

**Track label:** 🔵 ADJACENT TRACK (non-hardgate)  
**Registry label target (Claim Master Board):** `SCAFFOLD_PRODUCTION`  
**Scope:** deterministic observation ingestion + routing across DESI, ACT/SPT/CMB-S4, JUNO/Hyper-K, LiteBIRD, and lab substitutes.

---

## 1) Purpose and boundary

Pillar 247 defines a single deterministic orchestration layer that consumes release payloads, runs lane-specific falsifier logic, and emits one integrated decision packet.

It is an **adjacent operations track**:
- does **not** change ToE score,
- does **not** promote/demote hardgate claims automatically,
- does enforce same-day sync targets when a route is `FALSIFIED`.

---

## 2) API shape (proposed)

```python
from dataclasses import dataclass
from typing import Literal, Any

ObservatorySource = Literal[
    "DESI", "ACT", "SPT", "CMB-S4", "JUNO", "Hyper-K", "LiteBIRD", "LAB_SUBSTITUTE"
]
Route = Literal["PASS", "TENSION", "FALSIFIED", "INCONCLUSIVE"]

@dataclass(frozen=True)
class Measurement:
    value: float
    sigma: float

@dataclass(frozen=True)
class ObservationPayload:
    source: ObservatorySource
    release_name: str
    year: int
    observables: dict[str, Measurement]  # e.g. {"wa": Measurement(value=-0.55, sigma=0.20)}
    metadata: dict[str, Any]           # reference, datasets, campaign_id, etc.

@dataclass(frozen=True)
class RoutedVerdict:
    source: ObservatorySource
    route: Route
    severity: Literal["LOW", "ELEVATED", "CRITICAL"]
    gate_hits: list[str]
    rationale: list[str]
    required_sync_targets: list[str]

def separation_guard() -> dict[str, Any]: ...
def validate_payload(payload: ObservationPayload) -> dict[str, Any]: ...
def route_single(payload: ObservationPayload) -> RoutedVerdict: ...
def route_batch(payloads: list[ObservationPayload]) -> dict[str, Any]: ...
def integrated_report(payloads: list[ObservationPayload]) -> dict[str, Any]: ...
```

Determinism rules:
- no random branch logic,
- canonical key order in emitted dict/json,
- stable `deterministic_run_id` hash from normalized payloads,
- identical input → byte-identical output packet.

---

## 3) Deterministic routing rules by lane

### 3.1 DESI lane (`w_a`, optional `w_0`)

Aligned to `src/core/desi_year3_monitor.py`:
- `FALSIFIED` if \(|w_a - 0|/σ_{w_a} \ge 3.0\)
- `TENSION` if \(1.0 \le |w_a|/σ_{w_a} < 3.0\) or \(w_0\)-tension \(\ge 2.0σ\)
- `PASS` otherwise

Required sync on `FALSIFIED`:
- `src/core/kk_de_wa_cpl.py`
- `3-FALSIFICATION/OBSERVATION_TRACKER.md`
- `src/core/canonical_falsifier_evidence_feed.py`

### 3.2 ACT/SPT/CMB-S4 lane (`n_s`, `r`)

Unified route wrapper over `src/core/cmbs4_ns_r_joint_falsifier.py`:
- `FALSIFIED` if:
  - \(n_s \notin [0.955, 0.972]\) at \(σ_{n_s}<0.001\), or
  - \(r<0.010\) confirmed at \(>3σ\), or
  - \(r>0.036\) confirmed at \(>3σ\)
- `TENSION` if joint \(σ_{\text{joint}}\ge2.0\) or 1D tension \(\ge2.0σ\)
- `PASS` otherwise

Source-tag convention:
- `ACT` and `SPT`: standalone pre-CMB-S4 releases,
- `CMB-S4`: unified Stage-4 release packets.

All three source tags feed one unified **CMB lane** and share the same deterministic formulas; only confidence tier differs in metadata (`precision_tier = "pre-CMBS4"` vs `cmbs4_decision_grade`).

### 3.3 JUNO/Hyper-K lane (`Δm²₃₁`)

Aligned to `src/core/hyperk_juno_dm31_readiness.py`:
- `FALSIFIED` if tension \(\ge3σ\) **or** observed value outside \([2.2,2.7]\times10^{-3}\,\text{eV}^2\)
- `TENSION` if \(2σ \le\) tension \(<3σ\)
- `PASS` otherwise

### 3.4 LiteBIRD lane (`β`)

Aligned to `src/core/litebird_gap_hardening.py`:
- `FALSIFIED` zones:
  - `BELOW_WINDOW` (\(β<0.22^\circ\) at ≥3σ),
  - `ABOVE_WINDOW` (\(β>0.38^\circ\) at ≥3σ),
  - `GAP` (\(β\in(0.29^\circ,0.31^\circ)\) at ≥3σ)
- `PASS`/support zones:
  - `PRIMARY_SECTOR` near \(0.331^\circ\),
  - `SHADOW_SECTOR` near \(0.273^\circ\)
- `AMBIGUOUS` trigger condition:
  - \(β\in[0.22^\circ,0.38^\circ]\), not in strict `GAP` falsifier, and farther than sector-support tolerance from both 0.273° and 0.331° modes.
- `AMBIGUOUS` mapping is deterministic:
  - if \(σ_β \le 0.02^\circ\) (LiteBIRD-grade precision) → `TENSION`,
  - if \(σ_β > 0.02^\circ\) → `INCONCLUSIVE`.

Boundary convention (explicit):
- broad-window thresholds use strict inequalities for falsification (`<0.22`, `>0.38`);
- gap falsifier uses an open interval (`0.29 < β < 0.31`);
- exact boundaries (`β=0.22`, `0.29`, `0.31`, `0.38`) route as non-falsifying `AMBIGUOUS` unless strict-inequality falsifier conditions are met at ≥3σ.
- gap condition "both penetrations ≥3σ" means:
  - \((β-0.29)/σ \ge 3\), and
  - \((0.31-β)/σ \ge 3\).
- this is intentionally strict and mirrors `litebird_gap_hardening.py`; at the center point \(β=0.30^\circ\), strict gap-falsification requires \(σ_β \le 0.01/3 = 0.00333^\circ\). LiteBIRD-expected \(σ_β\approx0.02^\circ\) therefore routes center-gap outcomes to `TENSION`/`INCONCLUSIVE`, not strict `GAP_FALSIFIED`.

| Case | Zone |
|---|---|
| central \(β=0.22^\circ\), \(σ_β=0.01^\circ\) | `AMBIGUOUS` (not `<0.22` at ≥3σ) |
| central \(β=0.29^\circ\) or \(0.31^\circ\) (strict boundary central values) | boundary, not `GAP` |
| central \(β=0.38^\circ\), \(σ_β=0.01^\circ\) | `AMBIGUOUS` (not `>0.38` at ≥3σ) |
| \(0.29<β<0.31\) and both gap penetrations ≥3σ | `GAP` → `FALSIFIED` |

### 3.5 Lab-substitute lane (`A_CP^lab`)

Aligned to `src/core/lab_litebird_substitute.py` and F-LAB-CP-1..4:
- `FALSIFIED` if any of:
  - F-LAB-CP-1 null at decision-grade \(σ_A\le10^{-5}\) with controls + replication,
  - F-LAB-CP-2 topology-independence,
  - F-LAB-CP-3 no sign inversion,
  - F-LAB-CP-4 systematics-only pseudo-signal
- lane route remains `PASS` when decision-grade nonzero topology-locked signal survives controls on both tracks (`supported=True` metadata flag)
- otherwise `INCONCLUSIVE`

Dual-track consensus:
- any track falsifies → lane `FALSIFIED`
- both support → lane `PASS` (`supported=True` marker)
- else `INCONCLUSIVE`

---

## 4) Integrated report schema (canonical)

```json
{
  "pipeline": "PILLAR247_UOIVR",
  "version": "v11.0-p247-spec",
  "deterministic_run_id": "p247-<sha256-16>",
  "generated_at_utc": "ISO-8601",
  "separation_guard": {
    "label": "ADJACENT_TRACK_NON_HARDGATE",
    "track": "PILLAR247_OBSERVATION_ROUTING_TRACK",
    "hardgate_isolation": true,
    "toe_score_delta_allowed": false,
    "physics_claim_promotion_allowed": false
  },
  "inputs": [{ "source": "DESI", "release_name": "...", "year": 2027, "observables": {}, "metadata": {} }],
  "lane_results": {
    "DESI": { "route": "TENSION", "severity": "ELEVATED", "gate_hits": ["DESI_WA_2SIGMA"] },
    "CMB": { "route": "PASS", "severity": "LOW", "gate_hits": [] },
    "NEUTRINO": { "route": "PASS", "severity": "LOW", "gate_hits": [] },
    "LITEBIRD": { "route": "INCONCLUSIVE", "severity": "ELEVATED", "gate_hits": ["BETA_AMBIGUOUS"] },
    "LAB_SUBSTITUTE": { "route": "INCONCLUSIVE", "severity": "ELEVATED", "gate_hits": [] }
  },
  "global_route": "INCONCLUSIVE",
  "required_same_day_sync": ["3-FALSIFICATION/OBSERVATION_TRACKER.md", "docs/CLAIM_MASTER_BOARD.md"],
  "integration_targets": ["docs/TRUTH_LAYER.md", "docs/GATEKEEPER_SUMMARY.md", "docs/WAVE_CHANGELOG.md"]
}
```

Global route precedence:
1. if any lane `FALSIFIED` → global `FALSIFIED`
2. else if any lane `TENSION` → global `TENSION`
3. else if any lane `INCONCLUSIVE` → global `INCONCLUSIVE` (insufficient precision and/or ambiguous measurement region; unlike `TENSION`, this is not a quantified prediction conflict)
4. else global `PASS`

---

## 5) Separation guard (explicit)

Required callable:

```python
def separation_guard() -> dict[str, object]:
    return {
        "label": "ADJACENT_TRACK_NON_HARDGATE",
        "track": "PILLAR247_OBSERVATION_ROUTING_TRACK",
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "message": (
            "Pillar 247 orchestrates ingest/routing only; it cannot by itself "
            "upgrade/downgrade hardgate physics claims."
        ),
    }
```

---

## 6) Targeted test matrix (64 assertions)

Planned file: `tests/test_pillar247_unified_observation_ingest_routing_engine.py`

| Block | Target | Assertions |
|---|---|---:|
| A | payload validation (source enums, required keys, finite numeric guards, alias normalization) | 12 |
| B | DESI routing thresholds (`<1σ`, `1–<3σ`, `≥3σ`, bad sigma, same-day sync flags) | 10 |
| C | ACT/SPT/CMB-S4 routing (`n_s` window, `r` high/low falsifiers, joint 2σ tension, PASS cases) | 10 |
| D | JUNO/Hyper-K routing (window guard, 2σ/3σ boundaries, precision sensitivity) | 8 |
| E | LiteBIRD zone classification (`BELOW_WINDOW`, `ABOVE_WINDOW`, `GAP`, sector support, ambiguous) | 8 |
| F | Lab-substitute routing (F-LAB-CP-1..4, dual-track consensus, unsupported/inconclusive) | 8 |
| G | integrated report + deterministic run-id + global precedence + separation guard invariants | 8 |
|  | **Total** | **64** |

Minimum must-cover assertions:
1. identical normalized payload sets produce identical `deterministic_run_id`,
2. any lane `FALSIFIED` forces global `FALSIFIED`,
3. separation guard always reports `toe_score_delta_allowed=False`.

---

## 7) Label and tracker alignment

- In `3-FALSIFICATION/OBSERVATION_TRACKER.md`: reference as **Lane C orchestration adjacent track**.
- In `docs/CLAIM_MASTER_BOARD.md` Lane F: register as adjacent engineering claim with label `SCAFFOLD_PRODUCTION`, gatekeeper `PASS (engineering lane)`.

This preserves existing hardgate boundaries while giving one reproducible ingest-and-verdict control plane across all active observational lanes.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
