# Book 28 — F-theory Rung 8 and DESI DR3 Hardening

*Unitary Manifold v20.1 — August 2026*

*Synthesized with GitHub Copilot (AI)*

---

## Chapter 1 — Rung 7 Recap, Rung 8 Opens

Rung 7 built the 12D F-theory scaffold: a reference CY4, an elliptic fiber, and
three anchors. Anchor A handled the D3-tadpole context, Anchor B linked Kodaira
monodromy to the UM winding number, and Anchor C proposed a matter-curve origin
for the neutrino c_L lower bound. But three residuals remained. Rung 8 does not
pretend to solve everything. It closes the reference-CY4 pieces that can be
closed honestly, and names what still remains open.

---

## Chapter 2 — APS Discriminator and the n_w=5 Selection

The F-theory SU(5) GUT uses the Kodaira I₅ fiber. Its monodromy matrix is

    T₅ = [[1, 5], [0, 1]]

The off-diagonal entry is exactly 5, matching the UM winding number n_w = 5.
For a hypothetical I₇ fiber,

    T₇ = [[1, 7], [0, 1]]

which does not match the UM winding. Pillar 576 quantifies the scaffold-level
selection strength with the algebraic APS proxy

    |η(T₅) - η(T₇)|  ~  |5² - 7²| / 74  = 24 / 74  ≈ 0.324

This is an honest improvement: the selection is now quantified on the reference
scaffold, while the full η-invariant on a generic Weierstrass model remains open.

---

## Chapter 3 — c_L from F-theory: Gap B Closed at Reference CY4

Pillar 573 identified the mechanism: F-theory matter-curve normalizability can
explain why the lightest neutrino requires a lower bound on c_L. Pillar 577 goes
one step further by fixing the compact surface to the reference CY4 proxy:

    Vol(S)_ref = sqrt(chi(CY4)/(24 h11))  ≈ 275.5

Using πkR = 37, M_KK = 1 TeV, and m_ν1,max = 4×10⁻¹¹ GeV gives

    c_L,min = 0.5 + ln(10^3 / 4×10⁻¹¹) / 74  ≈ 0.917

That is slightly stronger than the manually enforced c_L ≥ 0.88 cutoff. So Gap B
advances from MECHANISM_IDENTIFIED to PROVED_AT_REFERENCE_CY4. Two residuals
remain open: explicit Weierstrass data and matter-curve genus/curvature.

---

## Chapter 4 — D3-Tadpole and Braid Consistency

Pillar 578 verifies the reference-CY4 tadpole identity exactly:

    N_D3 + N_flux = chi(CY4)/24

For zero flux on the scaffold,

    N_D3 = 75840 = 1820160 / 24

and the braid/tadpole ratio is

    k_CS × N_D3 / chi(CY4) = 74 / 24 = 37 / 12

This is a consistency check, not a derivation of k_CS from tadpole cancellation.
But it matters: it shows the Rung 8 reference geometry does not clash with the
UM braid invariant.

---

## Chapter 5 — DESI DR3: Three Branches, One Hardened Decision Tree

Sprint C hardens the dark-energy response before DESI DR3 arrives. Pillar 580
locks three outcome branches:

- **PASS** if σ_DR3 < 2.0
- **TENSION** if 2.0 ≤ σ_DR3 < 3.0
- **FALSIFIED** if σ_DR3 ≥ 3.0

The DR2 combined baseline is 2.75σ. Pillar 551 projects a Year-5 central value
of 3.64σ if the current central trend survives. Rung C therefore adds an
explicit **EXTENSION_TRIGGER** overlay at 3.64σ: if the data land there, the
dark-energy extension lane activates immediately.

---

## Chapter 6 — Why the Frozen Radion Predicts wₐ = 0

Pillar 581 makes the analytic argument explicit. The radion is stabilized by a
steep Goldberger-Wise potential. For a heavy modulus,

    m_phi >> H0

and the field cannot roll on cosmological timescales. Using the canonical values

    m_phi ~ 10⁻³ eV
    H0    ~ 1.5×10⁻³³ eV

gives

    m_phi / H0 ≈ 6.67×10²⁹

which is overwhelmingly in the frozen regime. Therefore the minimal UM prediction
is

    w0 = -1,   wₐ = 0

The certificate is honest: it is conditional on the Goldberger-Wise sector being
natural, which is the standard UM assumption.

---

## Chapter 7 — Preregistration v2 and What Comes Next

Pillar 582 upgrades the DESI preregistration to a deterministic v2 string and
computes its SHA-256 hash at import time. The new format hard-locks the PASS and
FALSIFIED thresholds, the Euclid cross-check windows, and the Hyper-K/SPHEREx
couplings before DR3 lands.

So where does this leave the framework?

1. **F-theory Rung 8**: partial closure at the reference CY4, with two named
   residuals still open.
2. **Dark-energy routing**: fully hardened before DESI DR3.
3. **Next frontier**: explicit Weierstrass-model geometry for F-theory, and a
   real observational verdict from DESI DR3/Year 5.

The point is not to claim victory too early. The point is to make the next
failure or success impossible to reinterpret after the fact.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
