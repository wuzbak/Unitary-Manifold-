# Radiological & Chemical Safety Guide — Pillar 15 Cold Fusion

> **Scope:** This document applies to any physical experiment inspired by the  
> Pillar 15 (φ-enhanced tunneling) model in `src/core/cold_fusion.py` and  
> `src/cold_fusion/`.  
>  
> **Status of the theory:** Pillar 15 is a formal mathematical exploration of  
> how 5D Kaluza–Klein geometry modifies the Gamow tunneling factor in a  
> coherent Pd–D lattice.  The Python code is a *theoretical calculator*, not  
> an engineering manual.  No physical device built from this code has been  
> constructed or validated as of the date of this document.  
>  
> **Precautionary principle:** Because the model predicts exponentially  
> enhanced tunneling rates at the right parameter values, anyone attempting  
> to *experimentally* reproduce these conditions must treat radiological and  
> chemical hazards as real from the first day of work.

---

## 1 · The D+D Reaction Products

Standard deuterium–deuterium fusion proceeds via two branches with nearly  
equal probability (~50 / 50 at low energies):

| Branch | Products | Q-value | Primary hazard |
|--------|---------|---------|---------------|
| D + D → ³He + n | Helium-3 + **neutron** (2.45 MeV) | +3.27 MeV | **Neutron radiation** |
| D + D → T + p | Tritium + proton (3.02 MeV) | +4.03 MeV | **Tritium (β⁻ emitter)** |

At room temperature the 4D rate is negligibly small (~10⁻¹⁰⁰⁰⁰ per pair per  
second).  The φ-enhanced Gamow factor reduces this suppression but does *not*  
change which branch fires or the energy of the products.

### 1.1 Neutron hazard

- **2.45 MeV neutrons** (from the ³He branch) are **fast neutrons**.  
- They are highly penetrating — they pass through most materials without  
  interacting and deposit their energy via proton recoil in biological tissue.  
- Fast neutrons are among the most radiobiologically damaging radiation types  
  (Quality Factor Q ≈ 20 for tissue dose calculation).  
- Concrete, water, or polyethylene shielding (hydrogen-rich materials) is  
  required to thermalise and absorb them.

### 1.2 Tritium hazard

- Tritium (³H) is a **β⁻ emitter** with half-life 12.32 years.  
- The maximum β energy is 18.6 keV — it cannot penetrate skin externally.  
- The primary hazard is **inhalation or ingestion**: tritiated water (HTO)  
  is metabolised identically to ordinary water and distributes throughout  
  body tissue.  
- Tritium produced in a sealed Pd lattice will outgas as T₂ or HTO when the  
  lattice is opened.  Negative-pressure containment is required.

---

## 2 · Safety Dimensions — Full Table

| Dimension | Risk level | Description | Mitigation |
|-----------|-----------|-------------|-----------|
| **Physical — neutron flux** | High (if functional) | 2.45 MeV neutrons from D+D → ³He+n; penetrating; QF ≈ 20 | Boron-doped polyethylene shielding ≥ 30 cm; neutron area monitors; REM badges |
| **Physical — tritium** | High (if functional) | T outgassing from D+D → T+p; metabolic hazard | Sealed negative-pressure glovebox; tritium-specific air monitors; thyroid blocking |
| **Chemical — Pd/D₂** | Medium | Pressurised deuterium gas; Pd powder is flammable if fine | Use deuterium gas cylinder with regulator; no open flames; Pd foil preferred over powder |
| **Chemical — Pd–H₂ embrittlement** | Medium | Loaded Pd becomes brittle; thermal cycling can cause fracture | Anneal Pd before loading; slow loading ramp; inspect foil integrity |
| **Thermal — Pd melt** | Low–Medium | Pd melts at 1828 K; uncontrolled heat generation | Use `ThermalRunawayGuard(T_max_K=400)` to abort simulation; instrument physical cell with thermocouple |
| **Intellectual — pathological science** | Low | LENR field has history of unreproducible results; economic/reputational risk | Peer review before publication; replication protocol; blind data analysis |
| **Intellectual — premature scaling** | Low | DIY assembly before safety characterisation is understood | Do not scale beyond µW regime without professional radiation monitoring |
| **Regulatory** | Medium | Any device producing measurable neutron flux requires a radioactive materials licence in most jurisdictions | Contact national nuclear regulatory authority before construction |

---

## 3 · The Critical Distinction: Calculator vs. Device

The code in `src/core/cold_fusion.py` is a **mathematical calculator** for the  
theoretical Gamow factor under 5D KK geometry.  It computes a number.  

There is a large engineering gap between:

```
G₅ = G₄ × f_KK(φ_ratio) × f_winding(c_s, n_w)     [a Python float]
```

and:

> A physical apparatus sustaining the B_μ field confinement pressure  
> (`H_max`), the specific loading ratio (`x ≳ 0.7`), the (5,7) braided  
> winding state at k_cs = 74, and a coherent lattice phonon bath — all  
> simultaneously, in a stable configuration.

The code provides a **map** of where the tunneling probability is theoretically  
favourable.  It does not provide a recipe for crossing from the map to a working  
device.  That gap requires:

1. A first-principles derivation of how the B_μ field is physically sourced  
   and sustained in a real Pd lattice (not yet available in this framework).  
2. Experimental confirmation that the φ-enhancement factor is physical, not  
   an artefact of the 5D truncation (not yet demonstrated).  
3. A full engineering safety analysis by a licensed nuclear engineer.

---

## 4 · Neutron Flux Estimation

The `thermal_runaway_mitigation.py` module includes a Layer 4 neutron flux  
monitor.  The estimated flux at rate R (fusions/cm³/s) in a volume V (cm³) is:

    Φ_n ≈ 0.5 × R × V × d²                 [neutrons / (cm² · s) at distance d cm]

where the factor 0.5 reflects the 50% branching to the neutron channel.

The **regulatory threshold** for uncontrolled areas in most jurisdictions is  
approximately 0.1 mrem/h for neutron dose rate, corresponding to roughly  
1 n/cm²/s for fast neutrons.  The Layer 4 shutdown fires if the estimated  
flux exceeds this threshold.

```python
from SAFETY.thermal_runaway_mitigation import ThermalRunawayGuard

guard = ThermalRunawayGuard(
    T_max_K=400.0,
    neutron_flux_limit=1.0,    # n/cm²/s — uncontrolled area regulatory threshold
    detector_distance_cm=100.0  # distance to nearest unshielded person
)
```

---

## 5 · Chemical Handling: Palladium and Deuterium

### 5.1 Deuterium gas (D₂)
- Asphyxiant in confined spaces (displaces O₂).  
- Flammable (4–75% explosive range in air — same as hydrogen).  
- Use in a well-ventilated laboratory with gas-detection alarm.  
- Store cylinders secured upright, away from ignition sources.  
- Use a pressure regulator rated for hydrogen service.

### 5.2 Palladium
- **Foil form:** Low acute hazard.  Wear gloves to prevent contamination.  
- **Powder/nanoparticle form:** Flammable; inhalation hazard.  Avoid using  
  Pd powder for loading experiments — use Pd foil (typical 0.025–0.25 mm  
  thick, 99.9% purity).  
- Palladium is a platinum-group metal; chronic exposure has not been  
  thoroughly studied.  Minimise skin and inhalation exposure.

### 5.3 Pd–D₂ loading procedure (minimum safety protocol)
1. Clean Pd foil in dilute HCl, rinse in deionised water, dry.  
2. Load slowly: ramp D₂ pressure from 0 to working pressure over ≥ 30 min  
   to avoid cracking.  
3. Monitor temperature continuously; do not exceed 400 K during loading.  
4. Store loaded foil under D₂ atmosphere; do not expose to air at elevated  
   temperature (risk of deloading and D₂ release).

---

## 6 · Scientific Integrity: Avoiding Pathological Science

The history of cold fusion (LENR) contains some of the most studied examples  
of what Irving Langmuir called **pathological science** — phenomena that appear  
real but cannot be reproduced because they were artefacts of experimental noise,  
wishful measurement, or confirmation bias.

The Gamow factor at room temperature is so small in 4D (~10⁻¹⁰⁰⁰⁰) that any  
measurement claiming room-temperature D+D fusion faces extraordinary evidential  
demands.  The φ-enhancement mechanism in Pillar 15 is theoretically motivated  
but experimentally unverified.

### Minimum reproducibility protocol

1. **Blind data analysis:** Collect and process data before unblinding any  
   comparison to the theoretical prediction.  
2. **Control cell:** Run an identical apparatus loaded with hydrogen (H₂)  
   instead of deuterium — the 5D enhancement should be absent for H+H.  
3. **Calorimetric baseline:** Any "excess heat" claim must exceed 3σ above  
   a calibrated input-power baseline, measured in a separate identical cell.  
4. **Neutron coincidence:** Genuine D+D fusion will produce neutrons in the  
   2.45 MeV range.  Any excess-heat measurement without a correlated neutron  
   signal should be treated with high scepticism.  
5. **Tritium assay:** Measure tritium in the electrolyte / gas phase before  
   and after the experiment.  A ³H increase without a correlated neutron  
   signal is also anomalous.

---

## 7 · Regulatory Checklist

Before constructing any apparatus intended to produce measurable nuclear  
reactions:

- [ ] Notify your institution's Radiation Safety Officer (RSO).  
- [ ] Obtain a radioactive materials licence from the national nuclear  
      regulatory authority (NRC in the USA, ONR in the UK, etc.).  
- [ ] Install area radiation monitors: at minimum one neutron REM meter and  
      one tritium-in-air monitor.  
- [ ] Establish a dosimetry programme for all personnel in the laboratory.  
- [ ] Register the experiment with the relevant licensing authority and  
      document all source terms.  

---

## 8 · The Final Word

The Unitary Manifold makes a precise, falsifiable prediction: under specific  
geometric conditions (φ-enhancement, (5,7) braided state, near-saturation Pd  
loading), the Gamow factor is reduced.  Whether this reduction is large enough  
to produce a measurable effect in a real physical apparatus is an experimental  
question that has **not been answered yet**.

The safest path forward is:

1. **Theory:** Complete the first-principles derivation of the B_μ source term  
   in the condensed matter context (not yet available).  
2. **Small-scale experiment:** Measure COP and neutron flux in a µW-regime  
   apparatus with full radiation monitoring, before any scale-up.  
3. **Independent replication:** Require at least three independent groups to  
   reproduce the anomalous heat signal before any engineering development.  

Until then, the code in this repository is a calculator.  Use it as one.

---

*RADIOLOGICAL_SAFETY.md version: 1.0 — 2026-04-16*  
*Theory: ThomasCory Walker-Pearson — Unitary Manifold v9.19*  
*Safety architecture: GitHub Copilot, commissioned by ThomasCory Walker-Pearson*
