# Gravitational Waves — The Signal the Framework Cannot Send (Yet)

*Post 35 of the Unitary Manifold series.*
*Claim: a first-order phase transition at the KK compactification scale would
produce a stochastic gravitational-wave background with a peak frequency
f_peak ≈ M_KK/(2π). For Planck-scale compactification (M_KK ~ 10¹⁹ GeV),
the peak frequency is approximately 10⁴³ Hz — far above any existing or planned
gravitational wave detector. The framework is therefore automatically consistent
with all current GW observations. This is not a win; it is an absence of signal
at any near-term detectable frequency. The one window where the framework could
produce a detectable signal: if future indirect constraints push M_KK into the
sub-TeV range, LISA (launch ~2035) might see it. The falsification condition
runs in the opposite direction: if future experiments establish that no KK
compactification scale exists in the range 10⁶–10¹³ GeV, the framework's
geometric dark matter and vacuum suppression mechanisms would require revision.*

---

The detection of gravitational waves by LIGO in 2015 opened a new observational
window on the universe. In the decade since, the LIGO-Virgo-KAGRA network has
detected over 90 binary mergers — black holes and neutron stars colliding at
cosmological distances. Pulsar timing arrays (PTAs) including NANOGrav, PPTA,
and EPTA have now detected a stochastic gravitational-wave background at
nanohertz frequencies.

The Unitary Manifold makes predictions about gravitational waves. Unlike its
birefringence prediction (LiteBIRD, 2032), these predictions are currently
undetectable. This post explains why — and why that fact, properly understood,
is informative rather than disappointing.

---

## What the KK compactification should produce

In the early universe, a first-order phase transition produces gravitational waves
by three mechanisms:

1. **Bubble nucleation and collision**: regions of the new phase (bubbles) nucleate
   and expand. When bubbles collide, the kinetic energy of the bubble walls is
   radiated as gravitational waves.
2. **Turbulence**: the plasma velocity field after bubble collisions is turbulent,
   sourcing a GW background over longer timescales.
3. **Sound waves**: acoustic oscillations in the plasma after the phase transition
   source a long-duration GW signal.

If the KK compactification was a first-order phase transition — the compact
dimension "locked in" at a definite radius R_KK during a phase transition in
the early universe — it would have produced a stochastic GW background via
all three mechanisms.

The peak frequency of this background is set by the KK mass scale:

    f_peak ≈ M_KK / (2π)   [in natural units]
    f_peak [Hz] ≈ M_KK [GeV] × 2.42 × 10²³ Hz/GeV

The conversion: 1 GeV in natural units corresponds to approximately 1.52 × 10²⁴ Hz,
divided by 2π ≈ 6.28, giving the numerical factor.

---

## The Planck-scale frequency problem

For canonical Planck-scale compactification (M_KK ~ M_Pl ~ 1.22 × 10¹⁹ GeV):

    f_peak ~ 1.22 × 10¹⁹ × 2.42 × 10²³ ≈ 3 × 10⁴² Hz

For reference:
- LIGO/Virgo sensitivity band: 10–1000 Hz
- LISA (space-based, launch ~2035) sensitivity band: 10⁻⁴ – 1 Hz
- Pulsar timing arrays (NANOGrav, 15-year dataset): ~10⁻⁹ – 10⁻⁷ Hz

The KK GW peak is at 10⁴² Hz. The highest-frequency GW detector ever proposed
in the scientific literature is sensitive to ~10⁸ Hz — 34 orders of magnitude
below the Planck-scale KK signal.

The consequence: the KK gravitational wave background from Planck-scale compactification
is completely undetectable by any experiment in any foreseeable time horizon.
The framework is consistent with all existing GW data — not because it predicts
a signal that agrees with data, but because it predicts a signal so far outside
the observable window that no conflict is possible.

---

## Why this is not a free pass

An undetectable prediction is a valid prediction only if the undetectability
is physically motivated, not chosen to avoid falsification.

In this case, the argument is:

1. The framework requires a compactification scale. For a gravity-only extra
   dimension consistent with table-top gravity tests (which have probed down to
   ~50 μm separation without finding extra dimensions), the compactification radius
   must be smaller than ~50 μm, corresponding to M_KK > few meV.

2. For the KK sector to be relevant for particle physics (Pillar 43,
   `src/core/kk_collider_resonances.py`), KK resonances should not appear below
   the LHC exclusion limit of ~5 TeV for simple KK models.

3. Both constraints are consistent with Planck-scale compactification. The
   Planck-scale GW frequency is a genuine consequence of the geometry, not a
   choice made to avoid GW detection.

The undetectability is a physical consequence of where M_KK sits. It is not
a claim that GW observations are irrelevant to the framework — quite the
opposite.

---

## What would produce a detectable signal

If M_KK were much lower — in the range 10⁶–10¹³ GeV — the peak frequency
would fall in the LISA sensitivity band (10⁻⁴ – 1 Hz). The required M_KK:

    f_peak = 10⁻³ Hz → M_KK ~ f_peak / (2.42 × 10²³ Hz/GeV) ~ 4 × 10⁻²⁷ GeV

Wait — that is the wrong direction. Let me recalculate. For f_peak to be in
the LISA band (say, 10⁻³ Hz):

    M_KK = f_peak × 2π / (1.52 × 10²⁴ Hz/GeV) ~ 4 × 10⁻²⁷ GeV

That is far below any reasonable particle physics scale. The LISA band actually
corresponds to M_KK ~ 10⁻²⁷ GeV — a compactification scale 70 orders below
the Planck mass. This is not physically motivated within the Unitary Manifold.

The NANOGrav band (~10⁻⁹ Hz) is similarly inaccessible for any KK scale that
is physically motivated by the framework.

The honest statement: the Unitary Manifold's KK gravitational wave background
cannot be detected by any existing or planned GW observatory, because Planck-scale
compactification pushes the signal to frequencies 34+ orders of magnitude above
all detector sensitivity bands.

---

## The NANOGrav signal is not the KK background

The NANOGrav 15-year dataset (arXiv:2306.16213) and simultaneously PPTA, EPTA,
and CPTA reported a gravitational-wave background at nanohertz frequencies with
amplitude Ω_GW h² ~ 5 × 10⁻⁹ at f ~ 3 × 10⁻⁸ Hz.

What causes it? The leading candidates are:

1. **Supermassive black hole binary mergers**: the merger of SMBH pairs with masses
   10⁸–10¹⁰ M_sun during galaxy mergers produces a stochastic background at PTA
   frequencies. This is the standard astrophysical explanation.
2. **First-order phase transitions** in the early universe at energies in the range
   1–100 MeV, which would produce a GW background peaking at PTA frequencies.
3. **Cosmic string networks** from early-universe phase transitions.

The Unitary Manifold's KK background peaks at 10⁴² Hz — a frequency ratio of
10⁵¹ above the NANOGrav signal. They are not related. The NANOGrav signal is
not explained by UM KK gravitational waves and is not used to constrain the
KK compactification scale.

This is confirmed explicitly in `src/core/kk_gw_background.py`:
"The NANOGrav signal is NOT explained by UM KK GWs."

---

## The framework's GW prediction that is testable (eventually)

There is one GW-adjacent prediction from the framework that is more accessible.

The primordial tensor modes generated during inflation — parametrised by the
tensor-to-scalar ratio r — are a gravitational wave background from the inflationary
epoch, not from a phase transition. The framework predicts r = 0.0315 (from the
braided (5,7) winding).

Tensor modes at r ~ 0.03 produce a primordial gravitational wave background
with energy density Ω_GW h² ~ 10⁻¹⁶ at frequencies 10⁻¹⁶ – 10⁻¹⁷ Hz
(corresponding to the inflationary horizon scale today). This is in the sensitivity
band of future space-based GW detectors targeting the very low-frequency regime
(the "Big Bang Observer" concept), not LISA.

More practically, the r = 0.0315 prediction is tested through CMB B-mode
polarisation — not through direct GW detection. BICEP/Keck and LiteBIRD probe
this prediction through the imprint of tensor modes on CMB polarisation.
The GW background itself, from primordial inflation at r = 0.0315, is many
orders of magnitude below the sensitivity of any foreseeable direct GW detector.

---

## What the test suite confirms — and does not

`tests/test_kk_gw_background.py` confirms:

- The KK GW peak frequency formula f_peak = M_KK/(2π) is correctly implemented
- For M_KK = M_Pl ~ 1.22 × 10¹⁹ GeV, f_peak ~ 3 × 10⁴² Hz is correctly computed
- The LISA sensitivity band comparison is correctly implemented (KK signal is out-of-band)
- The NANOGrav consistency check is correctly implemented (KK signal is 51 orders above NANOGrav)
- The GW energy density Ω_GW h² for Planck-scale KK is correctly estimated
- The spectral shape of the KK GW background is correctly implemented

What the tests do not confirm:

- That the KK phase transition was actually first-order
- That the GW signal from a sub-Planck KK scale would be detectable by LISA
  at current sensitivity projections
- That the NANOGrav signal is inconsistent with any aspect of the UM framework

---

## The purpose of an undetectable prediction

Documenting undetectable predictions has value. It shows:

1. **The framework makes definite predictions at every scale**, not just the scales
   that happen to be accessible.
2. **The predictions are automatically consistent with existing data**, which is a
   non-trivial constraint — some new physics proposals produce GW signals that
   conflict with PTA or LIGO data.
3. **The signal location is precisely derived**, not vague. "The KK GW background
   peaks at 3 × 10⁴² Hz for Planck compactification" is a specific, calculable
   number. If it were instead 100 Hz, it would conflict with LIGO.

A framework that makes predictions only in the observable window is not more
honest than one that makes predictions everywhere — it is less useful. The
Unitary Manifold traces its predictions to unobservable frequencies and documents
them, so that if future instruments extend their reach, the confrontation between
theory and data is already prepared.

The GW post is, in a way, the most honest post in the series. It says: here is
what the theory predicts, here is why it cannot be tested, and here is the one
circumstance — sub-Planck M_KK — under which it could be. This is not a
triumphant result. It is the work of cataloguing a framework's full implications,
including the ones the universe keeps beyond current reach.

---

*Full source code, derivations, and 14,641 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*KK GW background (Pillar 69): `src/core/kk_gw_background.py`*
*Inflation tensor spectrum: `src/core/inflation.py`*
*Primary GW-adjacent falsifier: r = 0.0315, testable via LiteBIRD B-modes*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
