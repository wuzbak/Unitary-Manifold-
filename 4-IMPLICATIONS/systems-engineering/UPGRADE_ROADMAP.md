# Systems Upgrade Roadmap
### From Where You Are Today to Manifold-Aligned Stability

> *"You don't need to rebuild everything.  You need to know which three things to fix first,  
> which seven to fix next, and what the finish line looks like."*

**How to read this document:**  
Each phase stands alone.  You can implement Phase 0 and Phase 1 without committing to
Phase 2.  Each phase delivers measurable value independently.  Later phases build on
earlier ones but do not require them to have been perfect.

| Phase | Horizon | Investment | Expected return |
|-------|---------|-----------|----------------|
| [Phase 0 — Baseline](#phase-0--baseline-measurement) | Week 1–4 | < 1 engineer-week | Full visibility into current risk posture |
| [Phase 1 — Immediate wins](#phase-1--immediate-wins-06-months) | 0–6 months | 2–4 eng-weeks per system | 30–70% latency incident reduction |
| [Phase 2 — Architectural alignment](#phase-2--architectural-alignment-618-months) | 6–18 months | 2–6 eng-months per platform | Eliminate capacity-collapse failure mode |
| [Phase 3 — Systemic redesign](#phase-3--systemic-redesign-1836-months) | 18–36 months | Platform-level investment | Durable structural reliability advantage |
| [Phase 4 — Hardware integration](#phase-4--hardware-integration-35-years) | 3–5 years | R&D / standards investment | Silicon-level stability guarantees |

---

## Phase 0 — Baseline Measurement

**Goal:** Know your current numbers before changing anything.  
**Time:** 1–4 weeks.  
**Who:** 1–2 senior engineers per system.

Phase 0 is non-destructive.  Nothing is changed.  You are only measuring.

### The Four Numbers — Baseline Protocol

For each major system in your stack, compute and record:

**`φ_min` — Minimum headroom**

```
For each resource R in {CPU, memory, link bandwidth, IOPS, disk}:
    φ_R = 1 − peak_utilisation_over_last_30_days(R)

φ_min = min(φ_R for all R across all nodes)
```

Record the result as a heatmap: node × resource.  Mark any cell where `φ < 0.20`
in yellow (warning) and any cell where `φ < 0.10` in red (critical).

**`B_div` — Queue growth rate**

```
For each queue, buffer, or lag metric in the system:
    Fit a linear trend to queue depth over the last 30 days
    B_div = slope of the trend (units: fraction per second)
```

Any positive slope sustained over more than 30 minutes is a `B_div > 0` alarm.

**`Δφ` — Maximum clock/phase skew**

```
Collect all NTP/PTP offset measurements over the last 30 days
delta_phi_max = P99 of |offset|
delta_phi_p50 = median |offset|
```

Safe bound: `|Δφ| < T_step / 2`.  For most systems: `|Δφ| < 1 ms`.

**`entropy_balance` — Silent loss audit**

```
For each service boundary, over the last 30 days:
    produced  = total events / messages / records created
    consumed  = total events / messages / records acknowledged
    dropped   = total explicit drops logged

entropy_balance = produced − consumed − dropped
```

Any non-zero result indicates silent loss.  Quantify it.  This number is often
surprising the first time it is computed.

### Baseline Report Format

Produce a one-page baseline report with:

1. **`φ_min` heatmap** — colour-coded by node × resource
2. **`B_div` trend chart** — top 5 queues by growth rate
3. **`Δφ` distribution** — P50 / P95 / P99 clock skew
4. **`entropy_balance` table** — per service boundary, 30-day total

This report is the input to Phase 1 prioritisation.

### Phase 0 Decision Gate

Proceed to Phase 1 when you can answer:
- [ ] Which three resources have the lowest `φ_min`?
- [ ] Which three queues have the highest `B_div`?
- [ ] What is the worst-case `Δφ` in the system?
- [ ] How large is the entropy balance discrepancy, if any?

---

## Phase 1 — Immediate Wins (0–6 months)

**Goal:** Fix the highest-risk `B_div` and `entropy_balance` violations without
architectural changes.  All patches are reversible and deploy to existing infrastructure.  
**Time:** 2–4 engineer-weeks per major system.  
**Who:** Firmware/platform engineers; no architect-level decisions required.

### Priority Order

Prioritise fixes in this order, driven by the Phase 0 baseline:

| Priority | Fix | Target condition | Expected impact |
|---------|-----|----------------|----------------|
| P1 | Add AQM to top 3 queues by `B_div` | `∇_μ B^μ` bounded | P99 latency −30 to −70% |
| P2 | Add explicit drop ledger to every queue | `∇_μ J^μ = 0` | Silence-loss elimination |
| P3 | Add `φ_min` alarm to monitoring | `φ ≥ φ_min` | Early warning before capacity failure |
| P4 | Add geometric clock correction to NTP/PTP clients | `Δφ → 0` | Jitter reduction |
| P5 | Add information-balance watchdog | `∇_μ J^μ = 0` | Silent-loss continuous audit |
| P6 | Add `φ_min` dilaton floor alarm to embedded RTOS | `φ → 0` early warning | Pre-failure escalation |

The detailed pseudocode for each fix is in [`FIRMWARE_FIXES.md`](./FIRMWARE_FIXES.md):

| Fix | `FIRMWARE_FIXES.md` section |
|-----|---------------------------|
| AQM | F1 |
| Geometric clock correction | F2 |
| Radio phase correction | F3 |
| Sensor fusion dilaton weighting | F4 |
| Entropy-shedding buffer | F5 |
| TCP geometric congestion control | F6 |
| Information-balance watchdog | F7 |
| Hysteretic state machine | F8 |
| Causal jitter buffer | F9 |
| Dilaton floor alarm | F10 |

### Phase 1 Deployment Protocol

For each fix, follow this sequence:

1. **Baseline capture** (from Phase 0): record the four numbers before any change.
2. **Canary deployment**: roll out to 1–5% of production.  Monitor for 48 hours.
3. **Compare**: verify that `B_div` decreased, `entropy_balance` moved toward zero,
   or `φ_min` alarm is now firing correctly.
4. **Full rollout** if canary is clean.
5. **Post-deployment soak**: monitor for 7 days.  Update the baseline report.
6. **Rollback test**: verify the fix can be reverted in < 5 minutes without state loss.

### Phase 1 Success Criteria

At the end of Phase 1, the baseline report should show:

- [ ] All major queues have `B_div ≤ 0` under normal load
- [ ] `entropy_balance` discrepancy < 0.1% of total message volume
- [ ] `φ_min` alarm fires correctly in a controlled test (introduce artificial load until threshold)
- [ ] `Δφ` P99 within the `T_step / 2` bound
- [ ] P99 latency on the top 3 queues improved by at least 20%
- [ ] On-call alert volume from queue-related alarms reduced

### Phase 1 Decision Gate

Proceed to Phase 2 when:
- [ ] All four numbers are instrumented in production dashboards
- [ ] Phase 1 fixes are deployed, soak-tested, and stable
- [ ] The team has read and internalised [`MANIFOLD_SYSTEM_STABILITY.md`](./MANIFOLD_SYSTEM_STABILITY.md)

---

## Phase 2 — Architectural Alignment (6–18 months)

**Goal:** Redesign the system's architecture so that the three geometric conditions are
enforced by structure, not by monitoring-and-patch.  
**Time:** 2–6 engineer-months per platform.  
**Who:** Senior engineers, architects, product leads; requires cross-team coordination.

### The Seven Architectural Patterns

Each pattern enforces one or more geometric conditions at the architectural level.
See [`FUTURE_SOFTWARE_HARDWARE.md`](./FUTURE_SOFTWARE_HARDWARE.md) for full detail.

| Pattern | Condition enforced | Addresses from failure analysis |
|---------|------------------|-------------------------------|
| 1. Geometric backpressure | `∇_μ B^μ` bounded | Buffer bloat, queue explosion |
| 2. Dilaton-aware load balancing | `∇φ = 0` | Hotspots, throughput cliffs |
| 3. Fixed-point state machines | `k_cs` minimum complexity | Protocol oscillation, stuck states |
| 4. Information-conserving event arch | `∇_μ J^μ = 0` | Silent event loss, state divergence |
| 5. Geometric recommendation arch | Correct `Ψ*` | Polarisation, engagement trap |
| 6. Causal netcode protocol | Ordered `B_μ` | Game desync, rubber-banding |
| 7. Manifold-health dashboard | All four conditions | Unified observability |

### Phase 2 Implementation Sequence

**Step 1 — Service boundary hardening (months 1–3)**

For every internal service-to-service boundary:
- Implement backpressure with AQM (Pattern 1)
- Add the outbox pattern for all cross-service writes (Pattern 4)
- Export `φ_node` from every service to the central dashboard (Pattern 7)

This step requires no changes to the internal logic of any service.  It only adds
wrapping infrastructure at service boundaries.

**Step 2 — Load balancing upgrade (months 2–6)**

Replace round-robin or queue-depth load balancing with `φ²`-weighted routing (Pattern 2):
- Each node computes and exports `φ_node = 1 − utilisation`
- Load balancer weights = `φ_node²`
- Autoscaling trigger at `φ_min < 0.15` (not `φ_min < 0.0`)
- Scale-in requires drain-before-terminate (Pattern 4 compatibility)

**Step 3 — State machine redesign (months 4–12)**

Audit all recovery, retry, and adaptive control state machines.  For any with fewer
than 74 effective states, redesign using Pattern 3:
- Four explicit phases: `{NOMINAL, DEGRADED, CORRECTING, RECOVERING}`
- Hysteretic transitions: `N_UP = 7`, `N_DOWN = 3`
- 10-step transition history ring buffer
- Oscillation detector: > 4 transitions in recent history → escalate

**Step 4 — Recommendation and matchmaking (months 6–18)**

For systems with recommendation or matchmaking components, apply Pattern 5:
- Add Shannon diversity term to the reward function
- Implement `B_μ` alignment check: boost forward-propagating content
- A/B test for long-term diversity and wellbeing, not only engagement
- Define and monitor the "healthy `Ψ*`": diverse, information-rich fixed point

**Step 5 — Unified dashboard (months 8–12)**

Build the four-number manifold-health dashboard (Pattern 7):
- `phi_min`: minimum across all nodes and resources
- `B_div`: maximum queue growth rate across all queues
- `delta_phi`: maximum clock/phase skew across all nodes
- `entropy_balance`: system-wide produced − consumed − dropped

This dashboard replaces (or supplements) alert-by-alert incident response with a
single unified geometric health status.

### Phase 2 Success Criteria

- [ ] All service boundaries have backpressure and an explicit drop ledger
- [ ] Load balancer uses `φ²`-weighted routing; `φ_min` triggers autoscaling
- [ ] All recovery state machines have ≥ 74 effective states and hysteretic transitions
- [ ] Manifold-health dashboard is live and the team is trained on interpreting it
- [ ] The system's `Ψ*` has been explicitly defined and monitored (for platforms with recommendations)
- [ ] No `B_div > 0` events lasting more than 5 minutes in the past 30 days
- [ ] `entropy_balance` discrepancy < 0.01% of total message volume

### Phase 2 Decision Gate

Proceed to Phase 3 when:
- [ ] Phase 2 success criteria are met and stable for 60+ days
- [ ] The architecture review process now checks for `G_AB`, `B_div`, `φ` violations as a mandatory step
- [ ] New services are being designed with Phase 2 patterns from the start (not retrofitted)

---

## Phase 3 — Systemic Redesign (18–36 months)

**Goal:** Redesign next-generation systems and protocols with manifold-aligned stability
built in from the first line of design, not added later.  
**Time:** Platform-level investment; varies by organisation scale.  
**Who:** Architects, platform leads, product managers, external standards bodies.

### What Changes at Phase 3

Phase 1 and Phase 2 retrofitted existing systems.  Phase 3 designs new systems correctly
from the start.  The key decisions that are expensive to change later:

**Protocol design:** New network protocols should embed causal ordering (`B_μ` alignment),
geometric congestion control, and AQM as protocol-level requirements.  QUIC is a good
foundation; Phase 3 protocols add explicit manifold-health fields to protocol headers.

**API design:** Every API should expose:
- The service's current `φ_node` (capacity headroom) as a standard header
- An explicit `X-Entropy-Balance` audit field
- Backpressure signals (`Retry-After` with geometric backoff, not fixed delay)

**Data architecture:** All new data pipelines should use the outbox pattern with
idempotency keys from day one.  Schema evolution should be treated as a `G_AB` change —
requiring a migration plan that maintains metric non-degeneracy.

**ML/AI systems:** New model deployment pipelines should:
- Track KL divergence between training and deployment distributions (the `φ` gradient metric)
- Trigger retraining when distribution shift exceeds the dilaton threshold
- Include Shannon diversity as a first-class evaluation metric for recommendations

### Phase 3 New Architecture Targets

| Target | Manifold alignment | `FUTURE_SOFTWARE_HARDWARE.md` section |
|--------|-------------------|--------------------------------------|
| Isotropic service mesh | Uniform `G_AB` | HW Principle 1 |
| Hardware PTP in all new services | `Δφ → 0` | HW Principle 2 |
| Dilaton-aware power management | `φ ≥ φ_min` | HW Principle 3 |
| Write-journalled storage | `∇_μ J^μ = 0` | HW Principle 4 |
| Diversity-optimised recommendations | Correct `Ψ*` | Pattern 5 |
| Causal netcode | Ordered `B_μ` | Pattern 6 |

### Phase 3 Success Criteria

- [ ] All new services designed after Phase 3 start are manifold-aligned by default
- [ ] Architecture review rejects any new service that violates the three conditions
- [ ] At least one next-generation protocol or API standard is designed with manifold alignment
- [ ] ML/AI deployment includes distribution-shift monitoring (`φ_gradient` alarms)
- [ ] Post-incident reviews routinely identify the specific manifold condition that was violated

### Phase 3 Decision Gate

Proceed to Phase 4 when:
- [ ] Phase 3 patterns are organisational defaults, not exceptional practice
- [ ] The engineering culture uses manifold language naturally (field conditions, fixed points)
- [ ] You are ready to influence hardware and standards decisions at an industry level

---

## Phase 4 — Hardware Integration (3–5 years)

**Goal:** Embed manifold-aligned stability guarantees at the silicon and standards level,
making the three conditions physically enforced rather than software-enforced.  
**Time:** 3–5 years (R&D timeline; industry standards timeline).  
**Who:** Silicon architects, standards bodies, research organisations.

### The Four Hardware Principles

Each principle embeds one geometric condition into silicon.  See
[`FUTURE_SOFTWARE_HARDWARE.md` — Part B](./FUTURE_SOFTWARE_HARDWARE.md#part-b-hardware-design-principles).

| Principle | Geometric condition embedded | Implementation approach |
|-----------|---------------------------|------------------------|
| HW1: Geometric routing fabric | Uniform `G_AB` | Equal-cost ports; fat-tree topology; per-port latency published in datasheet |
| HW2: Phase-locked clock distribution | `Δφ → 0` | PTP hardware timestamping at PHY layer; geometric PLL gains |
| HW3: Dilaton-aware power management | `φ ≥ φ_min` | Predictive core wake-up; per-core `φ` as hardware performance counter |
| HW4: Entropy-aware memory | `∇_μ J^μ = 0` | Write journals at controller level; ECC syndrome logging; wear-levelling as `∇φ = 0` |

### Phase 4 Standards Targets

- Proposal to IETF: network protocol header field for `φ_node` (capacity headroom advertisement)
- Proposal to IEEE: PTP extension with geometric phase-correction gains
- Proposal to CPU ISA bodies: per-core dilaton counter as a hardware performance counter
- Proposal to storage standards: entropy-ledger extension in NVMe specification

### Phase 4 Research Agenda

Phase 4 is also the phase where empirical validation of the physical predictions matters most.

| Prediction | Experiment | Timeline |
|-----------|-----------|---------|
| Birefringence β ∈ {≈0.273°, ≈0.331°} | LiteBIRD CMB observation | ~2032 |
| Tensor-to-scalar ratio `r ≈ 0.0315` | BICEP Array / CMB-S4 | ~2030 |
| `k_cs = 74` as minimum self-stabilisation complexity | Formal verification in protocol design | Ongoing |
| FTUM convergence for software systems | Fleet-scale production measurement | Ongoing |

---

## Cross-Phase Metrics Summary

The four numbers that track progress across all phases:

| Metric | Phase 0 baseline | Phase 1 target | Phase 2 target | Phase 3 target | Phase 4 target |
|--------|-----------------|---------------|---------------|---------------|---------------|
| `φ_min` | Measured, unknown | Alarmed at 0.15 | Structurally maintained > 0.15 | Maintained > 0.20 by design | Hardware-enforced > 0.15 |
| `B_div` | Measured, unknown | ≤ 0 under normal load | ≤ 0 enforced by architecture | ≤ 0 guaranteed by protocol | ≤ 0 enforced by routing fabric |
| `Δφ` | Measured, unknown | Within T_step / 2 | Structurally maintained | Hardware PTP at PHY | Silicon PLL guarantee |
| `entropy_balance` | Measured, unknown | < 0.1% discrepancy | < 0.01% discrepancy | 0 by protocol design | Hardware journal guarantee |

---

## Who Does What — Responsibility Matrix

| Phase | Student / Hobbyist | Entry Engineer | Senior Engineer | Architect | Scientist | Educator | Executive | Board |
|-------|-------------------|---------------|----------------|-----------|-----------|---------|----------|-------|
| Phase 0 | Understand the four numbers | Collect baseline metrics | Lead baseline measurement | Define metric scope | Validate measurement methodology | Teach the framework | Approve resourcing | Receive risk report |
| Phase 1 | Study firmware fixes | Implement F1–F10 | Review and deploy fixes | Prioritise fix order | Validate fix derivations | Case-study the patches | Track incident reduction | Review ROI |
| Phase 2 | Build pattern demos | Implement patterns | Lead pattern adoption | Design pattern-aligned architecture | Audit mathematical alignment | Curriculum development | Approve architectural investment | Monitor strategic KPIs |
| Phase 3 | Contribute to open-source implementations | Implement new services manifold-aligned | Set design standards | Author architecture RFCs | Publish validation results | Update course materials | Sponsor standards participation | Govern competitive positioning |
| Phase 4 | Follow hardware publications | Monitor ISA proposals | Contribute to silicon design reviews | Draft standards proposals | Run physical experiments | Integrate into physics curriculum | Fund R&D | Governance of IP and standards strategy |

---

## Rollback Plan

At every phase, the following rollback guarantee applies:

> **Any change made in Phase N can be reverted to the Phase N−1 state in < 5 minutes
> without loss of durable state.**

This is enforced by:
1. **Feature flags** on all Phase 1 fixes (each fix has an on/off toggle)
2. **Blue/green deployment** for Phase 2 architectural changes
3. **Semantic versioning** for Phase 3 API and protocol changes
4. **Backwards compatibility** for all Phase 4 hardware proposals

The rollback plan is tested explicitly in the Phase 0 baseline audit (confirm you can
roll back *before* you roll anything out).

---

## The Falsification Commitment

This roadmap is built on a physical theory with explicit falsification conditions.
The primary falsifier is:

> **If LiteBIRD (launch ~2032) measures cosmic microwave background birefringence angle β
> outside the range [0.22°, 0.38°], or landing in the predicted gap [0.29°–0.31°],
> the braided-winding mechanism is falsified.**

If the primary falsifier is triggered, the framework's physical basis requires revision.
The engineering patterns (Phases 1–2) remain valid as heuristics independently of the
physics.  The architectural patterns and hardware principles derived from formal
geometric theorems would require re-derivation from whatever replaces the braided-winding
mechanism.

Known limitations are documented in [`../FALLIBILITY.md`](../FALLIBILITY.md).  The CMB
power spectrum amplitude suppression (×4–7 at acoustic peaks) is an open problem.

---

*Part of the `systems-engineering/` folder — v9.28 OMEGA EDITION (99 pillars + sub-pillars, 15,296 tests).*  
*See [`AUDIENCE_GUIDE.md`](./AUDIENCE_GUIDE.md) for level-scaled explanations of the concepts this roadmap applies.*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
