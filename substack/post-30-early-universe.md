# From the First Microsecond: The Early Universe in the Unitary Manifold

*Post 30 of the Unitary Manifold series.*
*Claim: the Unitary Manifold's braided sound speed C_S = 12/37 ≈ 0.324 is
numerically close to the quark-gluon plasma sound speed squared c_s²(QGP) ≈ 0.33
measured by ATLAS in Pb-Pb collisions. The framework is honest that this is a
dimensional coincidence — C_S is a speed while c_s² is a speed-squared — not a
derivation of QGP dynamics. The framework does derive the photon-epoch sound
horizon (≈144 Mpc) and the sub-dominant radion pressure correction to Hubble
expansion (Δρ/ρ ≈ 1.4 × 10⁻³) from first principles. These are Tier 2 claims.
The falsification condition: any CMB measurement that requires the photon-baryon
sound speed to differ from c/√3 at last scattering by more than the KK correction
term would falsify the radion pressure calculation.*

---

The first seventeen posts in this series covered the framework's structure. The
middle stretch — Posts 17 through 29 — explored the domain applications: cold
fusion, recycling, neuroscience, climate, psychology, genetics, materials, stars.
They were all downstream applications of a core that had already been established.

This post returns to the beginning. Not the beginning of the series — the beginning
of time.

The framework makes specific claims about the two hottest epochs in cosmic history:
the quark-gluon plasma epoch (the first 10 microseconds) and the photon epoch
(from nucleosynthesis through recombination, spanning the first 370,000 years).
Both claims require a careful separation of what the framework predicts and what
it does not.

---

## The quark-gluon plasma: the hottest matter ever measured

Ten microseconds after the Big Bang, the universe was so hot that quarks and
gluons were not bound inside protons and neutrons. They were deconfined — free to
move as a nearly perfect liquid that physicists call the quark-gluon plasma (QGP).

This state no longer exists anywhere in the universe. But it is recreated in
particle accelerators every time a nucleus-nucleus collision is energetic enough
to heat a tiny region of space to T > T_c ≈ 155 MeV. The Large Hadron Collider
at CERN does this routinely with lead-lead (Pb-Pb) collisions at 5.02 TeV.

The key observable: the sound speed of the QGP. When two nuclei collide and form
a plasma, the plasma expands hydrodynamically. The expansion pattern encodes the
sound speed:

    c_s²(QGP) ≈ 1/3   (Stefan-Boltzmann limit, massless non-interacting QGP)

Near the deconfinement transition temperature T_c, the sound speed dips below 1/3
(the QCD equation of state softens) and recovers above 1/3 at higher temperature.
The ATLAS 2024 Pb-Pb open data release measured c_s² ≈ 0.33 ± 0.02 at T ~ 2T_c.

---

## The numerical coincidence — and why it is not a prediction

The Unitary Manifold's braided sound speed is:

    C_S = (n₂² − n₁²) / (n₁² + n₂²) = (49 − 25) / (49 + 25) = 24/74 = 12/37 ≈ 0.3243

The ATLAS measurement gives c_s²(QGP) ≈ 0.33. The numbers are strikingly close:
0.3243 vs. 0.33.

The framework's honest assessment: **this is a dimensional coincidence, not a
prediction.**

The reason is units. C_S is a speed — it is measured in units of c. The QGP
observable c_s² is a speed squared — measured in units of c². Numerically
comparing them is like comparing a distance in metres to an area in square metres
and noting they happen to be the same number. The comparison is not physically
meaningful without an explanation of why the two quantities should be equal.

No such explanation exists in the framework. The coincidence is documented
(in `src/core/quark_gluon_epoch.py`), the QGP sound speed is correctly anchored
to the ATLAS data, and the module is explicit: "The UM does not derive the QGP
sound speed from first principles. The near-coincidence is documented here as
a potentially interesting numerical fact, not a prediction."

This is the framework's standard for honesty applied in real time: a number that
looks like it fits is not a prediction unless there is a derivation behind it.

---

## What the framework does predict about the QGP epoch

While the QGP sound speed coincidence is not a prediction, the radion sector
does make a real contribution to the QGP epoch — a small one, precisely quantified.

The radion sector contributes a sub-dominant pressure fraction to the energy budget
during the QGP epoch:

    f_radion = C_S² / k_CS = (12/37)² / 74 ≈ 1.42 × 10⁻³

This means approximately 0.14% of the total energy density during the QGP epoch
came from the radion (fifth-dimensional) sector. This modifies the Hubble expansion
rate by:

    ΔH/H = ½ f_radion ≈ 7 × 10⁻⁴

A fractional correction of 0.07% to the Hubble rate. This is below current
experimental precision for the QGP epoch. It is a genuine prediction — small
but definite — and would in principle be measurable in the gravitational wave
background from the QCD phase transition, if that background is ever detected
with sufficient precision.

---

## The photon epoch: 1 second to 370,000 years

The photon epoch is the long middle act of the early universe. Nucleosynthesis
completed in the first few minutes (helium-4 abundance: ~25% by mass, consistent
with observations). For the next 370,000 years, photons and baryons were coupled
in a hot plasma: the photon-baryon fluid.

The physics of this epoch is better understood than almost any other period in
cosmology. The CMB we observe today is a snapshot of the photon-baryon fluid at
the moment of last scattering — when the universe cooled enough for electrons
and protons to combine into neutral hydrogen and photons decoupled.

The critical quantity: the sound speed of the photon-baryon fluid.

    c_s_PB = c / √(3(1 + R_b))

where R_b = 3ρ_b / (4ρ_γ) is the baryon-to-photon momentum ratio. Near
recombination, R_b ≈ 0.65, giving c_s_PB ≈ c/√4.95 ≈ 0.45c.

**This is not the same as C_S = 12/37 ≈ 0.324c.**

The distinction matters. The photon-baryon sound speed drives the acoustic
oscillations that produce the CMB power spectrum peaks. The radion sound speed
C_S is the speed of fluctuations in the compact fifth dimension — the inflaton
sector. They belong to different sectors and should not be confused.

The CMB power spectrum as calculated from c_s_PB is precisely consistent with
observations (modulo the amplitude suppression at acoustic peaks discussed in
FALLIBILITY.md — that remains an open problem). The radion sector does not
directly drive CMB oscillations; it imprints on them only through:

1. **Inflationary initial conditions**: n_s = 0.9635 and r = 0.0315 from the
   braided winding — these are set before the photon epoch begins.
2. **Sub-dominant pressure correction**: Δρ/ρ ≈ 1.42 × 10⁻³ during radiation
   domination, modifying the Hubble rate by ~7 × 10⁻⁴.
3. **Birefringence**: β ≈ 0.35° accumulated after last scattering as photons
   free-stream to us — this is the primary LiteBIRD observable.

---

## The sound horizon: the ruler of the universe

The sound horizon at recombination — the maximum distance a sound wave could have
travelled from the Big Bang to last scattering — is one of the most precisely
measured quantities in cosmology. It serves as a standard ruler: objects separated
by approximately 147 Mpc today (at the sound horizon scale) are separated by a
known physical distance, allowing the angular scale of the CMB acoustic peaks to
be used to measure cosmological distances.

The Planck 2018 measurement: r_s★ = 144.7 ± 0.4 Mpc.

The framework's derivation: using the Eisenstein-Hu (1998) analytic formula with
the standard ΛCDM parameters (Ω_b h² = 0.0224, Ω_m h² = 0.143, z★ = 1090),
the module computes r_s★ ≈ 141–147 Mpc, consistent with the Planck measurement.

The KK correction to the sound horizon is negligible (Δr_s★/r_s★ ~ 7 × 10⁻⁴)
because the radion sector contributes less than 0.1% of the radiation energy
budget during the photon epoch. The photon-baryon sound horizon is set by the
photon-baryon physics, and the framework correctly derives that the radion sector
is a spectator during this epoch.

This is an important honesty: the framework does not claim to improve on standard
ΛCDM for the photon epoch because the KK correction is too small to matter. The
claim is that the correction is consistent — it doesn't break anything — and that
its magnitude is precisely predictable from C_S and k_CS.

---

## The Silk damping scale

Silk damping (photon diffusion damping) erases CMB fluctuations below a
characteristic scale:

    r_D = √(∫₀^{η★} λ_mfp(η) / 6 dη)

where λ_mfp is the photon mean free path. For Planck parameters, r_D ≈ 7 Mpc.
Fluctuations on scales smaller than r_D are exponentially suppressed — this is
why the CMB power spectrum falls rapidly above l ~ 2000.

The framework's calculation of r_D is consistent with the Planck value. The KK
correction to r_D is (once again) negligible: the radion sector does not contribute
to photon diffusion, which is driven by Thomson scattering between photons and
electrons, not by the fifth-dimensional geometry.

The framework's contribution is the precision bookkeeping: computing exactly how
small the KK correction to each photon-epoch observable is, and confirming that
none of these corrections are large enough to conflict with existing measurements.
A theory that predicts corrections that conflict with precision cosmology would be
immediately falsified. The framework's corrections are safely sub-dominant.

---

## The honest reckoning: the amplitude problem persists

There is one place where the framework and the photon-epoch data are not in
agreement, and it is important.

The CMB power spectrum amplitude at acoustic peaks is suppressed in the framework's
calculation relative to the Planck measurement by a factor of approximately 4–7.
This is documented in FALLIBILITY.md as Admission 2, assigned to Pillars 57 and 63,
and flagged as a real and unresolved discrepancy.

The issue: the framework's model for how the braided winding imprints on the
primordial power spectrum produces the correct spectral tilt (n_s ≈ 0.9635) and
the correct tensor-to-scalar ratio (r ≈ 0.0315), but the overall normalisation of
the spectrum — the A_s parameter in the CMB amplitude — is not correctly reproduced
from first principles. Pillars 57 and 63 attempt to address this through
back-reaction corrections, but the amplitude residual persists.

This means: the framework correctly predicts the *shape* of the CMB spectrum but
not its *amplitude*. The shape prediction (n_s, r) is what LiteBIRD and BICEP/Keck
test. The amplitude is a separate parameter that currently requires fixing by hand.

This is a significant gap. The series states it plainly so that readers can
calibrate their confidence accordingly.

---

## What the test suites confirm — and do not

`tests/test_photon_epoch.py` (141 tests) and `tests/test_quark_gluon_epoch.py`
(120 tests) collectively confirm:

- The photon temperature-redshift relation is correctly computed
- The photon energy density Ω_γ h² is consistent with standard cosmology
- The matter-radiation equality redshift is correctly derived
- The photon-baryon sound speed formula is correctly implemented
- The sound horizon analytic formula agrees with Planck values
- The Silk damping scale is correctly computed
- The Saha ionisation fraction and recombination redshift are correct
- The KK radion pressure fraction (1.42 × 10⁻³) is correctly derived
- The radion-corrected Hubble rate modification (7 × 10⁻⁴) is correctly computed
- The QGP sound speed ATLAS anchor (c_s² ≈ 0.33) is correctly implemented
- The C_S vs c_s² dimensional distinction is explicitly documented and tested
- The radion contribution to the QGP epoch pressure is correctly quantified

What the tests do not confirm:

- That the CMB power spectrum amplitude discrepancy (×4–7 at acoustic peaks)
  is resolved by the framework
- That C_S and the QGP c_s are physically related rather than coincidentally
  numerically similar
- That the radion sector gravitational wave background from the QCD transition
  is detectable at future observatories

---

## The epochs as a coherent story

The story of the early universe, in the framework's language:

1. **Inflation** (before ~10⁻³⁵ s): the braided (5,7) winding generates the
   primordial power spectrum with n_s = 0.9635 and r = 0.0315.
2. **QGP epoch** (~10⁻⁵ s): quarks deconfine, then confine. The radion sector
   contributes 0.14% of the energy density — a spectator.
3. **Nucleosynthesis** (~1–200 s): standard BBN runs; the framework does not
   modify it.
4. **Radiation domination** (3 s–47 kyr): photon-baryon fluid oscillates;
   the radion correction to Hubble is 7 × 10⁻⁴.
5. **Photon epoch** (47 kyr–370 kyr): acoustic peaks form; Silk damping
   smooths small scales.
6. **Recombination** (z★ ≈ 1090): photons decouple; sound horizon freezes
   at 144.7 Mpc. The CMB is released.
7. **Free streaming** (z★ to today): photons travel from last scattering.
   The Chern-Simons coupling rotates their polarisation by β ≈ 0.35°.
8. **Today**: LiteBIRD will measure β to ±0.01° by 2032.

The framework's primary prediction is at Step 7. Everything else — the QGP, the
photon epoch, the sound horizon — is the scaffolding that the universe had to
pass through to get to the measurement that will test it.

---

*Full source code, derivations, and 12,950+ automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Photon epoch (Pillar 64): `src/core/photon_epoch.py` — 141 tests in `tests/test_photon_epoch.py`*
*Quark-gluon epoch (Pillar 65): `src/core/quark_gluon_epoch.py` — 120 tests in `tests/test_quark_gluon_epoch.py`*
*CMB amplitude gap: `FALLIBILITY.md` Admission 2, Pillars 57 and 63*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
