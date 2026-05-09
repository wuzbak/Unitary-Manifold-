# Lab-Scale CP Violation from (5,7) Braid Topology

## Executive statement

If Theorem XXIX fixes the geometric CP scale at the CKM order,
\(J_{\mathrm{geo}}\sim 3.3\times 10^{-5}\), then waiting for LiteBIRD is not the
only route to falsification pressure.

Any condensed-matter platform that **physically realizes the same (5,7) winding
geometry** should permit an immediate laboratory test of a CP-odd asymmetry at the
same order of magnitude.

This is a near-term, table-top program:

- engineer (or certify) a \((5,7)\) topological winding channel,
- measure a CP-odd observable under conjugate drive protocols,
- test whether
  \[
  A_{\mathrm{CP}}^{\mathrm{lab}} = \frac{\Gamma_+ - \Gamma_-}{\Gamma_+ + \Gamma_-}
  \]
  is nonzero at \(\mathcal{O}(10^{-5})\) and tracks the winding geometry.

The central claim is not that every material will show this instantly; it is that
**once the winding is physically realized and controls are done, the predicted
asymmetry scale is laboratory-accessible now**.

---

## 1) Mathematical bridge from braid geometry to lab asymmetry

The repository already contains two CP-scale statements:

1. **Geometric CP origin theorem (Pillar 145):**
   \(J\neq 0\iff n_1\neq n_2\), with CP asymmetry sourced by strand-phase
   mismatch for the canonical braid pair \((n_1,n_2)=(5,7)\).
2. **CKM-order effective scale in the Wolfenstein/Jarlskog route:**
   \(J\) at the observed sector is of order \(10^{-5}\), with canonical value
   near \(3.08\times10^{-5}\) and geometric estimates in the same band.

For lab transfer, define a topology-projection factor \(\Pi_{\mathrm{topo}}\in[0,1]\)
that measures how well the device realizes the ideal \((5,7)\) winding manifold.
Then the operational prediction is
\[
A_{\mathrm{CP}}^{\mathrm{lab}} \approx \Pi_{\mathrm{topo}}\,J_{\mathrm{geo}},
\qquad J_{\mathrm{geo}}\sim 3\times10^{-5}.
\]

Thus:

- high-fidelity \((5,7)\) realization: \(A_{\mathrm{CP}}^{\mathrm{lab}}\sim10^{-5}\),
- degraded winding realization: proportionally reduced signal.

This gives an immediate, quantitative target without cosmology timescales.

---

## 2) Candidate near-term platforms

## 2.1 Josephson junction arrays / SQUID networks

The repository already defines braid-linked Josephson frequency structure:
\[
\frac{f_{\mathrm{braid}}}{f_{\mathrm{plasma}}}=\frac{35}{74},
\qquad
\frac{\Delta f}{f}=\frac{5}{74},
\qquad
\frac{f_{\mathrm{beat}}}{f_{\mathrm{plasma}}}=\frac{22}{37}.
\]

Actionable extension: implement two conjugate drive protocols (+ and −) on the same
(5,7)-certified device, then compute
\(A_{\mathrm{CP}}^{\mathrm{lab}}\) from transition rates, switching rates, or
phase-slip rates.

## 2.2 Topological-insulator / engineered winding devices

Construct dual channels with opposite effective winding orientation while holding
material stack, temperature, field amplitude, and disorder fixed. Use a CP-odd
difference observable in transport or spectroscopy and form the same normalized
asymmetry ratio.

In both cases, the target is the same: geometry-locked asymmetry at
\(\mathcal{O}(10^{-5})\), not a free-fit number.

---

## 3) Minimal experimental protocol (concrete and immediate)

1. **Topology certification step**
   - Verify \((5,7)\) winding realization via independent structural/spectral
     diagnostics.
   - Reject runs with unstable or drifting topology class.

2. **Conjugate protocol pair**
   - Acquire \(\Gamma_+\) under forward winding/chirality condition.
   - Acquire \(\Gamma_-\) under conjugate condition (orientation/phase-inverted
     control preserving all non-topological settings).

3. **Primary estimator**
   \[
   A_{\mathrm{CP}}^{\mathrm{lab}}=\frac{\Gamma_+ - \Gamma_-}{\Gamma_+ + \Gamma_-}.
   \]

4. **Sensitivity requirement**
   - Statistical + systematic uncertainty must satisfy
     \(\sigma_A\le 1\times10^{-5}\) to test the claimed scale.

5. **Topology-swap control**
   - Repeat for non-(5,7) winding classes (or deliberately de-topologized sample).
   - Geometric prediction requires collapse or strong suppression of the CP-odd
     signal outside the target winding realization.

6. **Sign-reversal control**
   - Reverse winding orientation. CP-odd contribution must invert sign while
     CP-even backgrounds remain unchanged to first order.

---

## 4) Why this is scientifically urgent ("why wait until 2032?")

LiteBIRD remains the primary cosmological falsifier for \(\beta\), but the
(5,7)-geometry claim has **independent condensed-matter consequences** if the same
winding topology is physically instantiated.

So the correct strategy is parallel, not sequential:

- **Cosmology lane:** LiteBIRD/CMB-S4 for birefringence and inflation observables.
- **Laboratory lane (now):** table-top CP-asymmetry tests in engineered winding
  condensed matter.

A clean null at \(10^{-5}\) in a topology-certified (5,7) device is informative now;
a clean nonzero topology-locked signal is equally informative now.

---

## 5) Immediate action checklist for collaborating labs

- Identify one JJ-array/SQUID platform and one TI/winding platform capable of
  reproducible topology certification.
- Implement paired conjugate protocol acquisition with blind analysis.
- Publish estimator definition, run cuts, and systematics budget before unblinding.
- Hit \(\sigma_A\le10^{-5}\) and report:
  - raw \(\Gamma_+,\Gamma_-\),
  - corrected \(A_{\mathrm{CP}}^{\mathrm{lab}}\),
  - topology and sign-reversal controls,
  - non-(5,7) comparison runs.

This is a fully falsifiable near-term test path and does not depend on waiting for
2032 mission timelines.

---

## 6) Epistemic status

- **Claim class:** geometric transfer hypothesis from (5,7) braid CP curvature to
  condensed-matter realizations of the same winding topology.
- **Near-term testability:** high (table-top instrumentation exists).
- **Failure mode:** if topology-certified measurements at \(\sigma_A\le10^{-5}\)
  repeatedly return null with controls, this transfer hypothesis is falsified.

---

## Repository anchors

- `src/core/jarlskog_geometric.py` (Pillar 145, CP-origin theorem)
- `src/core/wolfenstein_geometry.py` (CKM-scale J estimate)
- `src/core/ckm_matrix_full.py` (`jarlskog_gap_honest()`)
- `src/core/josephson_resonance.py` (Pillar 195, table-top braid-frequency proxies)
- `3-FALSIFICATION/LAB_SCALE_CP_VIOLATION_FALSIFIER.md`

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
