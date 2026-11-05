# Pillar 1133 — Superfluid Effective-Theory Reference Calculation

🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM

**Status:** Bounded scientific reference calculation
**Date:** 2026-11-05
**Scope:** Bogoliubov dispersion for a homogeneous, dilute, repulsive 3D Bose gas
**Source module:** `src/core/pillar_1129_1168/pillar1133_superfluid_effective_theory.py`
**Tests:** `tests/test_pillar1133_superfluid_effective_theory.py`
**Article:** `7-OUTREACH/A Z PsiCat Literature/Articles/article-355-p1133-superfluid-connections-without-overclaiming.md`
**Tracker:** `docs/mas_tracker.yml`

## What this pillar does

`src/core/pillar_1129_1168/pillar1133_superfluid_effective_theory.py` provides a small SI-unit
toolkit for the zero-temperature, leading-order Bogoliubov spectrum, its
angular frequency, and the associated mean-field sound speed. The implemented
convention is

```text
epsilon_k = hbar^2 k^2 / (2 m)
g         = 4 pi hbar^2 a_s / m
E_k       = sqrt(epsilon_k (epsilon_k + 2 g n))
c_s       = sqrt(g n / m)
```

Here `k` is the magnitude of the wave vector in m⁻¹, `m` is particle mass in
kg, `n` is number density in m⁻³, `a_s` is the non-negative s-wave scattering
length in m, `g` has units J m³, `E_k` is in joules, and `c_s` is in m/s.
The contact-coupling convention assumes a uniform 3D gas with repulsive
short-range interactions, at zero temperature and within leading
Bogoliubov/mean-field theory. The module checks finite, physically admissible
input values and includes the noninteracting/free-particle limit.

## What this does not establish

This is not a derivation of superfluidity from the Unitary Manifold; it does
not validate UM, provide a UM-specific superfluid parameterization, derive
Son's relativistic equation-of-state EFT, or establish that superfluid dark
matter is realized in nature. It is not a calculation of an astrophysical
halo, galaxy rotation curve, cluster, merger, or analogue horizon. It also
does not include finite-temperature effects, trapping, depletion corrections,
strong coupling, or a relativistic dispersion relation. Results outside the
stated dilute-gas regime should not be read as predictions of this module.

## How to test

```bash
python -m pytest tests/test_pillar1133_superfluid_effective_theory.py -q
```

Tests check the declared dispersion formula, the zero-momentum gapless limit,
the free-particle limit, the long-wavelength sound-speed limit, the energy /
angular-frequency relation, and fail-closed input validation. These are
equation-level regression checks, not experimental confirmation.

## Falsification and research backlog

The bounded calculation can be challenged by independent implementations and
by measured excitation spectra of dilute Bose gases where the uniform,
zero-temperature, weak-coupling assumptions are controlled. Within that
regime, systematic disagreement with the stated spectrum beyond measurement
and model uncertainties would falsify this implementation or its applicability
to that system. It cannot alone falsify or confirm a broader dark-matter model.

Open work includes documenting a regime/uncertainty check such as the gas
parameter `n a_s^3`, comparing against independent experimental spectra,
extending only with explicit finite-temperature or beyond-mean-field models,
and mapping the separate astrophysical assumptions and constraints of
superfluid-dark-matter proposals. Cluster mixed-phase behavior, self-
interaction and merger constraints, and possible core fragmentation are
model-dependent open issues, not conclusions of this code. No precise
UM-specific parameterization or connection has been derived.

## References

- D. T. Son, [“Low-Energy Quantum Effective Action for Relativistic
  Superfluids”](https://arxiv.org/abs/hep-ph/0204199) (2002). The relativistic
  low-energy EFT is determined by the equation of state; this pillar does not
  implement it.
- M. Visser, [“Acoustic black holes: horizons, ergospheres, and Hawking
  radiation”](https://arxiv.org/abs/gr-qc/9712010) (1998). The acoustic
  geometry is a wave-equation correspondence under stated fluid assumptions,
  not emergent Einstein dynamics.
- N. N. Bogoliubov, [“On the theory of superfluidity”](https://doi.org/10.1016/S0031-8914(47)63753-6)
  (1947), historical foundation for the weakly interacting gas spectrum.
- L. J. Garay et al., [“Sonic analog of gravitational black holes in
  Bose-Einstein condensates”](https://doi.org/10.1103/PhysRevLett.85.4643)
  (2000); J. Steinhauer, [“Observation of quantum Hawking radiation and its
  entanglement in an analogue black hole”](https://doi.org/10.1038/nphys3863)
  (2016). Analogue-horizon results concern laboratory wave analogues, not
  astrophysical gravity.
- L. Berezhiani and J. Khoury, [“Theory of dark matter
  superfluidity”](https://arxiv.org/abs/1507.01019) (2015). This is a
  model-dependent dark-matter proposal.
- L. Berezhiani, G. Cintia, and M. Warkentin, [“Core Fragmentation in
  Simplest Superfluid Dark Matter Scenario”](https://arxiv.org/abs/2101.08117)
  (2021). The broader model's core structure and fragmentation are research
  questions.
- L. Berezhiani et al., [current review, arXiv:2505.23900v2](https://arxiv.org/abs/2505.23900v2)
  (2026). The review discusses model-dependent superfluid behavior in galaxies
  and mixed phases in clusters, alongside outstanding constraints and issues.

---
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
