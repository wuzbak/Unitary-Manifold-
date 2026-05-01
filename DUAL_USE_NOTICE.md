# Dual-Use Notice — AxiomZero Technologies / Unitary Manifold

**Document version:** 1.0 — May 2026  
**Effective date:** May 1, 2026  
**Author / rights holder:** ThomasCory Walker-Pearson (trading as AxiomZero Technologies)  
**Repository:** https://github.com/wuzbak/Unitary-Manifold-  
**Cross-references:** [`LICENSE`](LICENSE) · [`LICENSE-AGPL`](LICENSE-AGPL) · [`LEGAL.md`](LEGAL.md) · [`AXIOMZERO_DBA.md`](AXIOMZERO_DBA.md)

> **Note:** This document is an ethical declaration and a copyright-holder's
> notice under AGPL-3.0 § 7 (Additional Terms — preservation of notices).
> It is not a restriction on the intellectual content of the theory (which
> remains irrevocably public domain under DPC v1.0) and it does not create
> obligations beyond those already imposed by the AGPL-3.0 on the software.

---

## Part I — Why This Notice Exists

The Unitary Manifold framework includes modules that apply 5D Kaluza-Klein
geometry to nuclear tunneling in condensed-matter systems (Pillar 15 / Pillar 15-B,
`src/cold_fusion/`, `src/physics/lattice_dynamics.py`).  Taken in isolation,
portions of these modules could be adapted to model or optimise processes
other than the peaceful energy-research application for which they were derived.

The author — ThomasCory Walker-Pearson, operating as AxiomZero Technologies —
is committed to peaceful, open science.  This notice:

1. Records permanently and publicly that the author has considered dual-use risk.
2. Declares which applications are **incompatible** with the intent of this work.
3. Explains which specific implementations are **withheld** from the public
   repository under dual-use policy, and how legitimate researchers may
   access them under a supervised license.
4. Establishes a **Good Faith Use Affirmation** requirement for energy
   applications of the nuclear-tunneling modules.

---

## Part II — Prohibited Applications

The following uses of any software in this repository are **incompatible with
the intent of this work** and are **declared harmful by the copyright holder**:

1. **Weapons development** — any application whose primary purpose is to
   increase the lethality, yield, range, precision, or reliability of any
   weapon system, whether conventional, nuclear, radiological, biological,
   or chemical.

2. **Biological weapon design** — any application of the synthetic-biology
   modules (`src/genetics/synthetic_biology.py`, Pillar 25 extension) to
   the design, enhancement, or delivery of biological agents intended to
   cause harm to humans, animals, or ecosystems.

3. **Non-consensual surveillance** — any application of the governance,
   consciousness, or neuroscience modules to monitor, profile, or manipulate
   individuals without their informed, voluntary, and revocable consent.

4. **Circumventing safety-critical HILS constraints** — any use of the
   Unitary Pentad framework (`Unitary Pentad/`) that disables, weakens,
   or bypasses the Human-in-the-Loop requirements encoded in the framework's
   governance axioms, for the purpose of enabling autonomous decisions in
   safety-critical systems without human oversight.

5. **Enclosure of the public domain theory** — any use of the software to
   support a legal argument, patent claim, or trade-secret assertion that
   would restrict the public's free access to the Walker-Pearson field
   equations, the FTUM framework, or any other content dedicated to the
   public domain under DPC v1.0.

### Legal effect

The AGPL-3.0's "no additional restrictions" clause (§ 10) does not prohibit
this notice.  Section 7 of the AGPL-3.0 explicitly permits the copyright
holder to add "Further Restrictions" that include **"Preservation of
Notices"**.  This notice, once included in any copy or derivative work, must
be preserved under AGPL-3.0 § 7(b).

Furthermore, as the sole copyright holder of the software implementation
(retained copyright for AGPL enforcement — see `LICENSE` and `LEGAL.md`),
ThomasCory Walker-Pearson may terminate the AGPL-3.0 licence of any party
found to have used the software for Prohibited Applications listed above.
Such termination is consistent with AGPL-3.0 § 8 (Termination).

---

## Part III — Withheld Implementations

The following specific implementations have been **removed from the public
repository** and are held in a private AxiomZero repository:

| Function / module | Location (public stub) | Reason withheld |
|---|---|---|
| `ignition_N()` | `src/physics/lattice_dynamics.py` | Minimum coherence-domain size for measurable D-D fusion ignition; potential misuse in non-peaceful fusion device design |
| `lattice_coherence_gain()` | `src/physics/lattice_dynamics.py` | Computes collective Gamow factor and ignition condition across a coherence domain; same concern |
| `minimum_phi_for_fusion()` | `src/cold_fusion/tunneling.py` | Inverts the Gamow formula to give the minimum local field strength needed for a target tunneling probability — a direct device design parameter |
| `sites_in_coherence_volume()` | `src/cold_fusion/lattice.py` | Converts coherence length to active-site count; key multiplier bridging per-site rate to total device power |
| `loading_threshold_for_fusion()` | `src/cold_fusion/lattice.py` | Minimum D/Pd loading ratio for fusion onset — device engineering threshold |
| `fusion_rate_per_site()` | `src/cold_fusion/excess_heat.py` | Absolute per-site fusion rate in Planck units; needed to calculate total device power |
| `excess_heat_power()` | `src/cold_fusion/excess_heat.py` | Total excess heat power from N active sites — primary figure of merit for LENR device design |
| `heat_to_electrical_efficiency()` | `src/cold_fusion/excess_heat.py` | Converts LENR excess heat to net electrical output; completes the engineering pipeline |
| `cold_fusion_rate()` | `src/core/cold_fusion.py` | Absolute D-D fusion rate per cm³/s under 5D enhancement — volumetric device performance metric |
| `run_cold_fusion()` | `src/core/cold_fusion.py` | One-call pipeline: input device parameters → absolute rates + enhancement; highest-level operational calculator |

**What the public stubs preserve:**

- The full function signatures and docstrings, so that downstream code
  that imports these functions will fail gracefully with `NotImplementedError`
  rather than silently returning wrong results.
- The theoretical derivation documented in the docstring and the module
  overview, so that the scientific content remains in the public domain (DPC v1.0).
- All other functions in the affected modules that do not directly compute
  operational thresholds, absolute rates, or device-level power outputs.
  Specifically kept public: `gamow_factor`, `phi_enhanced_gamow`,
  `tunneling_probability`, `sommerfeld_parameter`, `coherence_length`,
  `enhancement_ratio`, `cop`, `is_excess_heat`, `anomalous_heat_signature`,
  `calculate_energy_branching_ratio`, `phonon_radion_bridge`,
  `bmu_time_arrow_lock`, and all lattice geometry functions that do not
  yield operational thresholds.

**Licensing withheld implementations:**

Researchers with a legitimate need for any withheld implementation
(e.g., academic cold-fusion experiments, energy policy analysis) may
request access by:

1. Opening a GitHub Issue at https://github.com/wuzbak/Unitary-Manifold-/issues
   with the subject line `[Dual-Use License Request] <brief description>`.
2. Describing the intended application, institutional affiliation, and
   safety/ethics review process in place.
3. Awaiting written approval from ThomasCory Walker-Pearson / AxiomZero Technologies.

Approved requests will receive a **Supervised Research License** (SRL) granting
access to the private implementation.  An SRL is free for academic
non-commercial use; commercial use is subject to the CLE tier in
`COMMERCIAL_TERMS.md § 4-A`.

---

## Part IV — Good Faith Use Affirmation (Energy Applications)

Any organisation or individual who uses **any** of the following public modules
for energy-research or energy-engineering applications must submit a one-time
Good Faith Use Affirmation:

- `src/physics/lattice_dynamics.py`
- `src/cold_fusion/tunneling.py`
- `src/cold_fusion/lattice.py`
- `src/cold_fusion/excess_heat.py`
- `src/core/cold_fusion.py`

**The affirmation is free and does not require approval.**  Submit by opening
a GitHub Issue at https://github.com/wuzbak/Unitary-Manifold-/issues with:

- Subject: `[Good Faith Use Affirmation] <organisation or name>`
- Body: A brief description of the application, confirming that it is for
  peaceful energy research and does not fall under any Prohibited Application
  listed in Part II.

**Purpose:** The affirmation creates a permanent, timestamped, public record.
If a party later misuses these modules, the absence of an affirmation —
or a false affirmation — is a relevant fact in any legal or regulatory proceeding.

---

## Part V — Biosecurity Note (Synthetic Biology)

`src/genetics/synthetic_biology.py` (Pillar 25 Extension) models gene circuits,
CRISPR precision, metabolic pathways, and biocontainment as φ-field attractors.
The module includes an explicit `biosafety_containment_phi()` function and the
Unitary Pentad includes a `biosecurity_dual_use_risk()` scenario precisely
because the authors took dual-use risk seriously in the design.

All synthetic-biology functions in this repository:

- Are mathematical models only.  They do not provide sequences, protocols,
  synthesis routes, or any actionable biological information.
- Explicitly include biosafety containment as a first-class parameter.
- Are accompanied by biosecurity HILS governance in `Unitary Pentad/pentad_scenarios.py`.

Nevertheless, any use of these functions for Prohibited Application 2
(Biological weapon design) is subject to the termination provisions in Part II.

---

## Part VI — AxiomZero Pentad Product Stubs

In addition to the dual-use cold-fusion stubs described in Part III, a second
category of protected implementations has been added: **the operational layer
of the HILS Unitary Pentad**, which is being developed as a standalone
AxiomZero product.

> **The HILS Unitary Pentad is a protected AxiomZero product currently in
> active development.**  Its operational session management, real-time pilot
> interface, live interrogation engine, and scenario execution engine reside
> in a private AxiomZero repository.

The reason for protection is **product development and commercial integrity**,
not dual-use safety.  The following modules are partially or fully stubbed:

| Module | Stubbed functions | Reason |
|---|---|---|
| `Unitary Pentad/seed_protocol.py` | `eject_volatile_bodies`, `enter_seed_state`, `check_handshake`, `germinate`, `parity_check`, `should_eject` | Pentad product — session initialisation and re-emergence protocol |
| `Unitary Pentad/pentad_scenarios.py` | `harmonic_state_metrics`, `is_harmonic`, `detect_collapse_mode`, `inject_adversarial_intent`, `deception_phase_offset`, `is_deception_detectable`, `trust_maintenance_cost`, `regime_transition_signal`, `total_trust_erasure`, `asymmetric_coupling_stress_test`, `biosecurity_dual_use_risk` | Pentad product — scenario execution engine |
| `Unitary Pentad/pentad_interrogation.py` | `_with_body_phi`, `pentad_com_sweep`, `pentad_phase_alignment_check`, `pentad_ttc_intent_analysis` | Pentad product — live interrogation engine |
| `Unitary Pentad/pentad_pilot.py` | `_sim_thread`, `_send_led_brightness`, `_arduino_thread`, `_simple_display_frame`, `_simple_loop_unix`, `_simple_loop_windows`, `_curses_loop`, `_connect_arduino`, `main` | Pentad product — real-time Human-in-the-Loop pilot interface |

Full details, including how to request access, are in
[`PENTAD_PRODUCT_NOTICE.md`](PENTAD_PRODUCT_NOTICE.md).

---

## Part VII — Relationship to Open Licenses

This notice operates within the existing license framework without
contradicting it:

| License | Effect | This notice |
|---------|--------|-------------|
| **DPC v1.0** | Theory is irrevocably public domain | Unaffected.  No restriction on the equations, derivations, or theoretical content. |
| **AGPL-3.0** | Software is open-source copyleft | Preserved.  This notice is an Additional Term under AGPL-3.0 § 7(b) requiring preservation of notices. |
| **Common Law Trademark** | "AxiomZero Technologies" brand protected | Unaffected. |
| **COMMERCIAL_TERMS.md** | Service and CLE terms | This notice adds the SRL tier for withheld implementations. |

---

## Part VIII — Contact and Reporting

To report a suspected Prohibited Application, request a Supervised Research
License, or submit a Good Faith Use Affirmation:

- **GitHub Issues:** https://github.com/wuzbak/Unitary-Manifold-/issues
- **Rights holder:** ThomasCory Walker-Pearson / AxiomZero Technologies (`@wuzbak`)

Suspected violations may also be reported anonymously via GitHub's
"Report content" feature; the rights holder will investigate and act
on credible reports.

---

*Document version: 1.0 — May 2026*  
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

> **This document is not a substitute for legal counsel.**  For binding
> commercial agreements or legal enforcement questions, consult a licensed
> attorney.
