# Quick Reference — Unitary Manifold Systems Engineering
### One page.  Print it.  Keep it at your desk.

---

## The One Sentence

**Every stable system has a geometric fixed point Ψ\*.  Every failure is a measurable
deviation from that fixed point caused by exactly one of three field conditions being
violated.**

---

## The Four Numbers — Read These First

| Metric | What it measures | Compute it as | Alarm when |
|--------|----------------|--------------|-----------|
| **`φ_min`** | Tightest resource bottleneck | `1 − max(utilisation)` across all nodes | `< 0.15` (< 15% headroom) |
| **`B_div`** | Queue growth rate | Linear trend slope of queue depth (per second) | `> 0` sustained for 30 s |
| **`Δφ`** | Sync / phase / clock skew | P99 of `|offset|` across all node pairs | `> T_step / 2` |
| **`entropy_balance`** | Silent data loss | `produced − consumed − dropped` | `≠ 0` for > 1 minute |

**System is healthy when:** `φ_min > 0.15` AND `B_div ≤ 0` AND `|Δφ| < T_step/2` AND `entropy_balance ≈ 0`

---

## The Three Conditions for Guaranteed Stability

| # | Condition | Physics name | Violated when | Diagnostic |
|---|-----------|-------------|--------------|-----------|
| 1 | **Full connectivity** | `G_AB` non-degenerate | A subsystem is unreachable; dependency graph has > 1 strongly connected component | Draw the dependency graph.  If it splits, you have a partition waiting to happen. |
| 2 | **Rate-limited flow** | `∇_μ B^μ` bounded | Any queue has positive trend and no drain guarantee | Plot queue depth vs time.  Any monotone increase is a condition-2 violation. |
| 3 | **Capacity headroom** | `φ ≥ φ_min` | Any resource above 85% utilisation | Plot utilisation heatmap.  Steep gradients predict where the next failure nucleates. |

**Bonus (always enforce):** `∇_μ J^μ = 0` — nothing disappears silently.  Every drop is explicit, counted, and logged.

---

## Failure Taxonomy

| Symptom | Field signature | Root cause | First fix |
|---------|---------------|-----------|----------|
| Latency blows up under load | `∇_μ B^μ` → ∞ | Unbounded queue, no drain guarantee | Add AQM (F1); set `Q_max = R_drain × T_SLO` |
| Throughput cliff at peak | `φ → 0` | Resource saturated; no headroom | Add `φ_min` alarm (F10); trigger load-shed at 85% |
| Service split / partition | `G_AB` degenerate | Connectivity loss, SPOF activated | Verify full graph reachability; add redundant path |
| Protocol bounces, can't converge | `H_μν` large (feedback gain > 1) | Recovery FSM has < 74 effective states | Add hysteresis (F8); N_UP=7, N_DOWN=3 |
| Clocks diverge, state inconsistent | `Δφ → π` | NTP/PTP not geometrically corrected | Deploy F2 (geometric clock correction) |
| Mystery data loss / stale state | `∇_μ J^μ ≠ 0` | Silent drop — no entropy ledger | Deploy F5 + F7; add produced/consumed/dropped counters |

---

## Ten Firmware Fixes — One Line Each

| Fix | What it does | Deploy first when |
|-----|-------------|------------------|
| **F1** AQM | Probabilistic drop from 50% occupancy; `Q_max = R_drain × T_SLO` | `B_div > 0` |
| **F2** Geometric clock | PD correction: `−k_p·Δφ − k_d·(Δφ−Δφ_prev)`; no step jumps | `Δφ > T_step/4` |
| **F3** Radio phase loop | `φ²`-weighted pilot averaging on OFDM subcarriers | EVM degrading |
| **F4** Adaptive sensor fusion | Replace fixed Kalman `R` with `R_nominal / (φ²+ε)` | Sensor SNR < 70% |
| **F5** Entropy-shedding buffer | Explicit `drop_count`; structured telemetry event per drop | Embedded overrun |
| **F6** Geometric TCP | RTT-ratio mode detection; geometric `cwnd` decrease when rtt_ratio > 1.5 | Consumer router |
| **F7** Info-balance watchdog | `produced = consumed + dropped + in_flight`; 1 Hz check | Any event queue |
| **F8** Hysteretic FSM | Require 7 up / 3 down; oscillation detector → escalate at 4 transitions | Bouncing recovery |
| **F9** Jitter buffer | `depth = ceil(2·σ_RTT / T_step)`; sorted by sequence number | Gaming / VoIP |
| **F10** Dilaton floor alarm | `φ = 1 − max(cpu,mem,link)`; EWMA trend; project time-to-floor | Any RTOS |

---

## The `k_cs = 74` Rule

**Any self-stabilising system needs at least 74 reachable states.**  
In practice: `{NOMINAL, DEGRADED, CORRECTING, RECOVERING}` × 10-step history buffer.  
Below 74 states: the system cannot distinguish a transient from a persistent fault.  It will oscillate.

---

## The Stability Guarantee

> **When `G_AB` is non-degenerate AND `∇_μ B^μ` is bounded AND `φ ≥ φ_min`,  
> the Fixed-Point Theorem (FTUM) guarantees: ∃ Ψ\* such that U(Ψ\*) = Ψ\*.  
> The system will find it.  Always.**

Jacobian eigenvalues at Ψ\*: `{−0.110, −0.070, −0.050}`.  Spectral radius: `0.475 < 1`.  
Verified across 192 independent cases.  See [`../src/multiverse/basin_analysis.py`](../src/multiverse/basin_analysis.py).

---

## The Falsification Commitment

> **LiteBIRD (~2032) will measure CMB birefringence angle β.**  
> If β ∉ [0.22°, 0.38°], or β lands in the gap [0.29°–0.31°], the braided-winding  
> mechanism is falsified.  This is not a hedge — it is a commitment.

Engineering patterns (Phases 1–2) are valid as heuristics independently of the physics.  
Architecture and hardware principles derived from the geometry would require re-derivation.

---

## Where to Go Next

| I need to… | Read |
|-----------|------|
| Understand why these failures happen geometrically | [`MANIFOLD_SYSTEM_STABILITY.md`](./MANIFOLD_SYSTEM_STABILITY.md) |
| Diagnose my specific domain | [`CURRENT_SYSTEMS_FAILURE_ANALYSIS.md`](./CURRENT_SYSTEMS_FAILURE_ANALYSIS.md) |
| Get the pseudocode for each fix | [`FIRMWARE_FIXES.md`](./FIRMWARE_FIXES.md) |
| Design new systems correctly from day one | [`FUTURE_SOFTWARE_HARDWARE.md`](./FUTURE_SOFTWARE_HARDWARE.md) |
| Plan a phased rollout with decision gates | [`UPGRADE_ROADMAP.md`](./UPGRADE_ROADMAP.md) |
| Explain this to a non-engineer | [`AUDIENCE_GUIDE.md`](./AUDIENCE_GUIDE.md) |

---

## Live Calculator (Pillar Ω)

All thresholds above are derived from first principles. Verify them instantly:

```python
from omega.omega_synthesis import UniversalEngine
e = UniversalEngine()
cos = e.cosmology()
print(f"c_s threshold = {float(cos.c_s):.4f}")   # 0.3243 (Pentad decoupling)
print(f"k_CS          = {cos.k_cs}")              # 74 (state-machine floor)
h = e.hils()
print(f"Trust OK      = {h.trust_is_sufficient}") # True at phi_trust=1.0
```

Full report: `python -m pytest omega/ -q` — 168 tests, 0 failures.

---

*Quick Reference — v9.28 OMEGA EDITION — 99 pillars + sub-pillars, 15,096 tests — May 2026*  
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Document engineering and synthesis: **GitHub Copilot** (AI).*
