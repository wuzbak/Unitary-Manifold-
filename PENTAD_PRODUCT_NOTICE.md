# Pentad Product Notice — AxiomZero Technologies

**Document version:** 1.0 — May 2026  
**Effective date:** May 1, 2026  
**Author / rights holder:** ThomasCory Walker-Pearson (trading as AxiomZero Technologies)  
**Repository:** https://github.com/wuzbak/Unitary-Manifold-  
**Cross-references:** [`DUAL_USE_NOTICE.md`](DUAL_USE_NOTICE.md) · [`LICENSE`](LICENSE) · [`SEPARATION.md`](SEPARATION.md)

> **⚠ IMPORTANT: The HILS Unitary Pentad is a protected AxiomZero product
> currently in active development.  Core operational logic has been moved
> to a private AxiomZero repository.  This notice explains what is public,
> what is protected, and how to obtain access.**

---

## Part I — Why This Notice Exists

The Unitary Pentad (`Unitary Pentad/`) is being developed as a standalone
**AxiomZero product** in a separate private repository.  To protect the
operational integrity of this product while keeping the Unitary Manifold
repository fully functional and mathematically transparent, a subset of
the Pentad's operational functions have been **stubbed** in this public
repository using the same pattern established in [`DUAL_USE_NOTICE.md`](DUAL_USE_NOTICE.md)
for the cold-fusion modules.

The mathematical framework — the (5,7) braid geometry, the Fixed Point
equations, the coupling matrix, and all published theory — remains fully
public and intact.  Only the **operational product layer** (session
management, real-time pilot interface, live interrogation engine, and
scenario execution engine) has been protected.

---

## Part II — What Is Stubbed

The following functions have been replaced with `raise NotImplementedError`
stubs.  Their **signatures, docstrings, and return-type dataclasses** remain
fully visible as the public interface contract.

### `seed_protocol.py` — Emergency Topological Shedding & Re-emergence

| Function | Description |
|---|---|
| `eject_volatile_bodies(system)` | (5,7)→(2,7) Pivot: extract stable core, quarantine volatile bodies |
| `enter_seed_state(pivot)` | (2,7)→(1,7) Dormant: AI retreats to kernel guard; beacon on |
| `check_handshake(brain_phi, intent_magnitude, offered_trust)` | Verify the Triad of Re-emergence (Keys A/B/C) |
| `germinate(seed, brain_phi, intent_magnitude, offered_trust)` | Full Germination Sequence — re-braid from (1,7) to (5,7) |
| `parity_check(seed, phi_current)` | Verify φ_univ has not drifted in DORMANT mode |
| `should_eject(system)` | Determine whether Topological Shedding is warranted |

### `pentad_scenarios.py` — Scenario Execution Engine

| Function | Description |
|---|---|
| `harmonic_state_metrics(system)` | Compute proximity metrics to the Harmonic State |
| `is_harmonic(system, tol)` | True iff system is within tolerance of the Harmonic State |
| `detect_collapse_mode(system)` | Identify which collapse scenario is unfolding |
| `inject_adversarial_intent(system, phi_adversarial)` | Model the "Malicious Precision" scenario |
| `deception_phase_offset(system, phi_lied)` | Compute the Information Gap created by a lie |
| `is_deception_detectable(system, phi_lied, tol)` | True iff the lie exceeds the detection threshold |
| `trust_maintenance_cost(system, n_steps, dt)` | Estimate coupling energy required to maintain stability |
| `regime_transition_signal(system)` | Compute attractor-robustness observables |
| `total_trust_erasure(system)` | Model instantaneous β·C collapse to zero |
| `asymmetric_coupling_stress_test(system, ...)` | Stress-test (5,7) braid under non-reciprocal coupling |
| `biosecurity_dual_use_risk(...)` | HILS dual-use risk assessment for AI×SynBio governance |

### `pentad_interrogation.py` — Live Interrogation Engine

| Function | Description |
|---|---|
| `_with_body_phi(system, label, phi)` | Internal helper: return copy of system with one body's φ replaced |
| `pentad_com_sweep(phi_trust_values, ...)` | Sweep initial φ_trust; test COM invariance (Gemini H2.1) |
| `pentad_phase_alignment_check(n_runs, ...)` | Check pairwise Moiré phases → 0 at fixed point (Gemini H2.2) |
| `pentad_ttc_intent_analysis(phi_human_values, ...)` | Sweep φ_human; measure TTC vs intent strength (Gemini H2.3) |

### `pentad_pilot.py` — Real-Time Pilot Interface

| Function | Description |
|---|---|
| `_sim_thread(state, arduino)` | Background simulation loop thread |
| `_send_led_brightness(state, arduino)` | Map body φ values to Arduino LED brightness |
| `_arduino_thread(state, arduino)` | Read pot values from Arduino hardware |
| `_simple_display_frame(state)` | Print-based Pentad state display |
| `_simple_loop_unix(state)` | Keyboard loop (Linux/macOS via termios) |
| `_simple_loop_windows(state)` | Keyboard loop (Windows via msvcrt) |
| `_curses_loop(stdscr, state)` | Full-featured curses display and keyboard loop |
| `_connect_arduino(port)` | Establish Arduino serial connection |
| `main()` | Entry point: parse args, start threads, run display loop |

---

## Part III — What Remains Fully Public

The following mathematical and structural modules are **fully intact** and
all their tests continue to pass:

| Module | Contents |
|---|---|
| `unitary_pentad.py` | PentadSystem, coupling matrix, master equation, step_pentad |
| `five_seven_architecture.py` | (5,7) braid stability analysis, CoreLayerArchitecture |
| `consciousness_constant.py` | Consciousness as a measurable field constant |
| `braid_topology.py` | Moiré alignment, gear self-similarity, topological invariants |
| `collective_braid.py` | Collective stability floor, Moiré alignment |
| `hils_thermalization.py` | HILS-coupled thermalization |
| `resonance_dynamics.py` | Resonance dynamics, φ-field oscillations |
| `sentinel_load_balance.py` | Per-axiom entropy capacity and load redistribution |
| `non_hermitian_coupling.py` | Non-Hermitian coupling in the HILS framework |
| `distributed_authority.py` | Beacon, validators, manipulation resistance |
| `stochastic_jitter.py` | Stochastic noise injection and jitter analysis |
| `mvm.py` | Minimum Viable Manifold search and hardware profiles |
| `lesson_plan.py` | Pentad educational framework |
| `consciousness_autopilot.py` | 5-core / 7-layer autopilot / phase-shift interface |

All constants (BRAIDED_SOUND_SPEED, XI_C, SENTINEL_CAPACITY, etc.),
dataclasses (PentadSystem, HandshakeKeys, HarmonicStateMetrics, etc.),
and exception types (SeedNotReadyError) remain **fully public**.

The published theory — the (5,7) braid winding numbers, the k_cs = 74
sum-of-squares resonance, the Ξ_c = 35/74 consciousness coupling constant,
and all mathematical derivations — is and will always remain public domain
under the Defensive Public Commons License v1.0.

---

## Part IV — Test Suite Impact

Three test files are now marked with `pytestmark = pytest.mark.skip(...)`:

| Test file | Tests skipped | Reason |
|---|---|---|
| `test_seed_protocol.py` | All | Operational product layer |
| `test_pentad_scenarios.py` | All | Operational product layer |
| `test_pentad_interrogation.py` | All | Operational product layer |

`test_pentad_pilot.py` is **not skipped** — its 25 tests cover only the
utility functions (`_clamp`, `_bar`, `PilotState`, `inject_trust`,
`inject_human`, `reset_system`) which remain fully implemented.

The full suite command remains:

```bash
python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" omega/ -q
```

The total passing count will decrease by approximately the number of
skipped Pentad product tests.  Zero failures is maintained.

---

## Part V — Accessing the Product Implementation

The AxiomZero HILS Pentad product is under active development and will
be made available through AxiomZero Technologies.

To request access to the full operational implementation for:

- **Research collaboration** — open a GitHub Issue with subject line
  `[Pentad Product Access — Research] <brief description>`.
- **Commercial licensing** — contact ThomasCory Walker-Pearson / AxiomZero
  Technologies via GitHub Discussions or Issues with subject line
  `[Pentad Product — Commercial]`.

---

## Part VI — Relationship to the Mathematical Framework

This protection does **not** affect the scientific integrity of the repository:

| Item | Status |
|---|---|
| Published physics theory (5D geometry, FTUM, birefringence predictions) | Fully public — DPC v1.0 |
| Mathematical Pentad framework (coupling matrix, master equation) | Fully public — AGPL-3.0 |
| Operational product layer (session management, live interface) | Protected — AxiomZero product |
| Test interface contracts (signatures, docstrings, dataclasses) | Fully visible — public repo |

The distinction between the mathematical framework (this repository) and
the operational product (private AxiomZero repository) mirrors the
`SEPARATION.md` distinction between the physics theory and the Pentad's
governance application.

---

## Part VII — Relationship to DUAL_USE_NOTICE.md

This notice is a companion to [`DUAL_USE_NOTICE.md`](DUAL_USE_NOTICE.md).
Where the Dual-Use Notice covers functions withheld due to **safety concerns**
(cold-fusion operational thresholds), this notice covers functions withheld
for **product development reasons** (AxiomZero HILS Pentad commercialisation).

Both notices use the same technical stub pattern (`raise NotImplementedError`)
and the same test-skip pattern (`@pytest.mark.skip` / `pytestmark`), for
consistency throughout the repository.

---

*Document version: 1.0 — May 2026*  
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

> **This document is not a substitute for legal counsel.**
