# The CMB Acoustic Peak Problem: The One Gap We Cannot Hide

*Post 65 of the Unitary Manifold series.*
*Claim: the Unitary Manifold's predicted CMB power spectrum is suppressed by a factor
of approximately 4–7 at acoustic peaks relative to Planck satellite observations.
The spectral shape (n_s) matches; the amplitude does not. This is the most
significant known failure of the framework, and it is being stated directly, not
minimized. Pillars 57 and 63 address this gap; neither has fully resolved it.*

---

Every scientific framework has a gap it would rather not talk about.

This framework's gap is this: the predicted CMB power spectrum is off by a factor of
roughly four to seven at the acoustic peaks. The peaks are there — the oscillation
structure of the primordial sound waves is present. The tilt of the spectrum matches
Planck's measurement to within 1σ. But the amplitude is wrong.

We are not minimizing this. A factor of 4–7 is not a rounding error. If the
amplitude prediction were the same as the peak structure prediction, the framework
would be in much better shape than it currently is.

This post states the problem completely and honestly, describes what has been
attempted to resolve it, and acknowledges what has not yet been resolved.

---

## What the CMB power spectrum shows

The CMB power spectrum — the pattern of temperature fluctuations in the cosmic
microwave background as a function of angular scale — has two components that
the framework addresses separately:

**The spectral tilt (n_s):** the slope of the power spectrum at large scales.
The framework predicts n_s = 0.9635 from the 5D → 4D KK Jacobian applied to
the inflationary slow-roll parameters. Planck measures n_s = 0.9649 ± 0.0042.
Agreement is within Planck's 1σ. This is a genuine success.

**The power spectrum amplitude (A_s):** the overall normalization of the primordial
power spectrum. The COBE/Planck normalization gives A_s ≈ 2.1 × 10⁻⁹. The
framework's predicted A_s — derived from the radion field's energy density without
separate normalization — is suppressed by a factor of 4–7.

These two quantities are in principle independent: you can have the right shape
with the wrong amplitude. The framework currently has the right shape and the
wrong amplitude.

---

## What Pillars 57 and 63 address

**Pillar 57** (CMB transfer function corrections) examines whether the KK Boltzmann
corrections — modifications to the photon-baryon fluid dynamics from the compact
fifth dimension — can boost the predicted amplitude toward the observed value.
Result: the KK Boltzmann correction is smaller than the observed discrepancy by
an order of magnitude. The correction is real but insufficient.

**Pillar 63** (electromagnetic-holographic CMB transfer function) applies the
holographic boundary dynamics to the acoustic peak structure. The transfer function
correction improves agreement with the peak structure (positions and relative heights)
but does not recover the overall amplitude. The shape improves; the normalization
does not.

Both pillars were genuine attempts to close the gap. Neither succeeded.

---

## What the φ₀ self-consistency story says

The φ₀ self-consistency (Pillar 56, `src/core/phi0_closure.py`) closes the loop
on the radion field's initial value through internal curvature-vorticity feedback.
This is documented as a genuine solution to the φ₀ problem.

But closing φ₀ self-consistently does not automatically fix the amplitude. The
φ₀ closure determines the value of φ₀ from the framework's internal dynamics.
Whether that value, substituted into the primordial power spectrum normalization,
yields A_s ≈ 2.1 × 10⁻⁹ is an open calculation. The framework claims the closure;
it has not yet demonstrated that the closed value reproduces A_s.

This is the status as of April 2026: φ₀ is self-consistent; A_s remains a gap.

---

## Why the framework is published despite this gap

A framework with a known, significant quantitative failure is publishable if:

1. The failure is stated explicitly, prominently, and completely. ✓
2. The failure is in a specific, identifiable sector that is addressable. ✓
3. The framework's successes — n_s, β, r, w — are in separate sectors and are
   not invalidated by the amplitude failure. ✓
4. The gap is being actively worked on, with honest reporting of what has and hasn't
   closed it. ✓

All four conditions are met. The amplitude gap does not invalidate the spectral
tilt, birefringence, or tensor ratio predictions — these depend on different physics.
But it is a genuine failure, it is documented as a genuine failure, and any reader
who encounters this series should know about it.

---

## What would close it

The path toward closing the amplitude gap runs through the following:

**Step 1:** Demonstrate that the φ₀ self-consistency value from Pillar 56, substituted
into the primordial normalization, yields A_s within observational bounds.

**Step 2:** If Step 1 fails, identify whether the gap is in the inflation sector
(the primordial spectrum amplitude), the transfer function (the propagation from
primordial to observed), or the normalization convention.

**Step 3:** Address the identified sector with a derivation that does not introduce
free parameters.

This is the open problem. We state it as open. Anyone who closes it will deserve
credit for it.

---

*Full source code, derivations, and 14,183 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*CMB amplitude gap: `FALLIBILITY.md` (Admission 2)*
*φ₀ closure: `src/core/phi0_closure.py`*
*Transfer function: `src/core/cmb_transfer.py`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
