# Lab-Scale CP Violation Falsifier (5,7) Braid Condensed Matter

This document defines **bright-line falsification conditions** for the claim that
(5,7)-topology condensed-matter realizations exhibit CP-odd asymmetry at the
CKM/Jarlskog scale (order \(10^{-5}\)).

Primary theory context lives in:
`../1-THEORY/LAB_SCALE_CP_VIOLATION_57_BRAID.md`.

---

## Observable and estimator

For conjugate protocols (+, −) on the same topology-certified device:
\[
A_{\mathrm{CP}}^{\mathrm{lab}}=\frac{\Gamma_+ - \Gamma_-}{\Gamma_+ + \Gamma_-}.
\]

Target scale:
\[
A_{\mathrm{CP}}^{\mathrm{lab}}\sim \Pi_{\mathrm{topo}}J_{\mathrm{geo}},
\quad J_{\mathrm{geo}}\sim 3\times10^{-5},
\quad 0\le\Pi_{\mathrm{topo}}\le1.
\]

---

## Bright-line falsification conditions

## F-LAB-CP-1 — Null at required sensitivity in certified (5,7) topology

**FALSIFIED if all are true:**

1. Device topology is independently certified as stable \((5,7)\),
2. total uncertainty reaches \(\sigma_A\le1\times10^{-5}\),
3. repeated independent runs give \(A_{\mathrm{CP}}^{\mathrm{lab}}\) consistent with zero
   at 95% CL,
4. control checks exclude dominant parity/chirality readout systematics.

Interpretation: the claimed transfer from braid CP geometry to lab condensed matter
fails at the predicted scale.

## F-LAB-CP-2 — No topology dependence

**FALSIFIED if:**

- measured asymmetry is statistically indistinguishable between
  topology-certified (5,7) and non-(5,7) control structures under matched
  conditions.

Interpretation: the effect is not locked to the claimed winding geometry.

## F-LAB-CP-3 — No conjugate sign behavior

**FALSIFIED if:**

- reversing winding/chirality protocol does not invert the CP-odd contribution,
  while CP-even baselines are stable.

Interpretation: observed offset is likely instrumental/background, not geometric CP.

## F-LAB-CP-4 — Systematics-dominated pseudo-signal

**FALSIFIED if:**

- the apparent \(10^{-5}\)-level signal is fully explained by calibrated
  drift/readout asymmetry/nonlinear mixer artifacts and vanishes after correction.

Interpretation: no surviving CP-odd residue attributable to topology.

---

## Non-falsifiers (important)

The following do **not** falsify the claim by themselves:

- sensitivity worse than \(\sigma_A>10^{-5}\),
- topology not independently certified,
- single-lab non-replicated positive or null result,
- uncontrolled thermal/disorder regime where \(\Pi_{\mathrm{topo}}\) is unknown.

---

## Decision table

| Measurement outcome | Verdict |
|---|---|
| \(A_{\mathrm{CP}}^{\mathrm{lab}}\neq0\) at \(\ge3\sigma\), sign flips under conjugate reversal, suppressed in non-(5,7) controls | **Supports** lab transfer hypothesis |
| \(A_{\mathrm{CP}}^{\mathrm{lab}}\approx0\) with \(\sigma_A\le10^{-5}\), certified topology, controls passed | **FALSIFIED** (F-LAB-CP-1) |
| Comparable asymmetry across (5,7) and non-(5,7) topologies | **FALSIFIED** (F-LAB-CP-2) |
| Non-inverting signal under conjugate reversal | **FALSIFIED** (F-LAB-CP-3) |
| Signal removed by systematics model | **FALSIFIED** (F-LAB-CP-4) |

---

## Experimental reporting minimum

A claim (positive or null) is considered decision-grade only if it reports:

- topology certification evidence,
- full estimator definition and blind-analysis protocol,
- uncertainty decomposition (stat + each systematic),
- raw and corrected \(\Gamma_+,\Gamma_-\),
- topology-swap and sign-reversal controls,
- independent replication status.

---

## Relationship to LiteBIRD timeline

This lab falsifier is **parallel** to cosmological falsification and should run now.
It does not replace LiteBIRD's birefringence test; it prevents unnecessary delay in
testing a core geometric consequence of (5,7) topology.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
