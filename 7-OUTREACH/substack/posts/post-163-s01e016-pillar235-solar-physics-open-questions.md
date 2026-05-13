# The Sun's 12 Biggest Open Questions: A Rigorous, Falsifiable Pillar 235

*Post 163 of the Unitary Manifold series.*  
*Series S01, Episode E016.*  
*Epistemic category: **A/P** — adjacent applied research mapping with explicit status labels. This article summarizes deterministic outputs from `src/core/pillar235_solar_physics_open_questions_engine.py`; it does **not** claim that solar physics is solved. Every result is labeled as [CALCULATED], [EMPIRICAL], or [SPECULATIVE].*  
*May 2026.*

---

## Claim (and strict boundary)

Pillar 235 contributes a scientific *workbench* for the Sun's major unanswered
questions. It provides testable diagnostics, uncertainty runs, and explicit
falsification conditions for each question.

It does **not** claim final proof of any of the 12 mysteries.

---

## Why this matters

Most discussions of solar mysteries stop at lists.
Pillar 235 turns the list into a reproducible pipeline:

1. define observables,
2. compute diagnostics,
3. state mechanism candidates,
4. attach falsification tests,
5. run uncertainty sensitivity.

That is the shift: from commentary to auditable computation.

---

## The 12 questions — with scientific solution lanes

### 1) Coronal heating
- **Open question:** Why is the corona far hotter than the photosphere?
- **Pillar 235 lane:** Alfvén-wave damping + intermittent reconnection heating [CALCULATED diagnostic, EMPIRICAL/SPECULATIVE mechanism].
- **Test:** Compare measured deposition flux vs required heating flux across radius.

### 2) Solar dynamo mechanics
- **Open question:** What exact nonlinear plasma dynamics generate the 11-year polarity cycle?
- **Pillar 235 lane:** supercritical tachocline-shear dynamo with memory effects [CALCULATED reduced-order diagnostic].
- **Test:** Reproduce phase and amplitude statistics under measured shear/diffusivity constraints.

### 3) Slow solar wind origin
- **Open question:** Where does the slow wind originate and how is it accelerated?
- **Pillar 235 lane:** open-closed boundary interchange reconnection + expansion mixing [CALCULATED routing metric].
- **Test:** Validate with composition/charge-state fingerprints of source plasma.

### 4) Flare/CME triggering
- **Open question:** What tips a region from stressed to eruptive?
- **Pillar 235 lane:** threshold non-potentiality and runaway reconnection topology [CALCULATED eruption-risk proxy].
- **Test:** Out-of-sample predictive skill on active-region catalogs.

### 5) Polar temperature asymmetry
- **Open question:** Why do poles differ and why can asymmetry persist?
- **Pillar 235 lane:** hemispheric transport + open-flux topology asymmetry [CALCULATED asymmetry quantification].
- **Test:** multi-cycle persistence after instrument cross-calibration.

### 6) Core rotation / neutrino consistency
- **Open question:** How can near-uniform core rotation coexist with differential outer layers?
- **Pillar 235 lane:** magneto-gravity-wave coupling across the tachocline [CALCULATED consistency metric].
- **Test:** helioseismic inversion updates + neutrino anisotropy constraints.

### 7) Solar metallicity discrepancy
- **Open question:** Why do surface spectroscopic and helioseismic abundance inferences differ?
- **Pillar 235 lane:** opacity revision + diffusion/mixing correction pathway [CALCULATED discrepancy metric].
- **Test:** simultaneous fit to seismic and spectroscopic observables.

### 8) Faint young Sun paradox
- **Open question:** How did early Earth avoid global glaciation under a dimmer Sun?
- **Pillar 235 lane:** required forcing closure via greenhouse + cloud/albedo feedback [CALCULATED energy-balance requirement].
- **Test:** geochemical proxy constraints must allow required forcing.

### 9) Alfvén-wave acceleration
- **Open question:** How do waves transfer energy/momentum into wind particles?
- **Pillar 235 lane:** wave-pressure + turbulent damping efficiency [CALCULATED acceleration proxy].
- **Test:** in-situ damping rates must match momentum-flux demand.

### 10) SEP shock acceleration physics
- **Open question:** How do shocks accelerate particles to extreme energies?
- **Pillar 235 lane:** diffusive shock acceleration checked by compression-ratio spectral predictions [CALCULATED DSA consistency check].
- **Test:** corrected spectral indices vs Mach-number predictions.

### 11) Grand minima
- **Open question:** What causes multi-decade near-collapse of sunspot activity?
- **Pillar 235 lane:** stochastic intermittency near dynamo threshold [CALCULATED intermittency proxy].
- **Test:** reconstructed minima frequency statistics vs model ensembles.

### 12) IBEX ribbon source
- **Open question:** What creates the ribbon of energetic neutral atoms at the heliosphere boundary?
- **Pillar 235 lane:** secondary ENA production organized by near-perpendicular local interstellar magnetic geometry [CALCULATED geometry consistency metric].
- **Test:** future ENA maps must preserve geometry relation.

---

## Simulations now included

Pillar 235 includes Monte Carlo perturbation of observable inputs to quantify
which question-lanes are robust and which are fragile to uncertainty.

That matters operationally: fragile lanes get priority for new mission time,
instrument upgrades, and coordinated observing campaigns.

---

## Scientific honesty checklist

- No claim that "the Sun is solved."  
- No claim that one model component is final.  
- Every lane includes an explicit failure condition.  
- Adjacent-track status is explicit and does not alter hardgate ToE score.

---

## Bottom line

The best way to respect hard solar mysteries is not to hand-wave them.
It is to compute, test, and be clear about what would prove us wrong.

Pillar 235 is exactly that: a falsifiable quantitative scaffold for the 12
largest open questions in solar physics.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
