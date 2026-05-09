# Lab LiteBIRD Substitute Protocol (F14/P8)

This protocol defines the **immediate table-top substitute lane** for pre-2032
falsification pressure on the braided (5,7) mechanism.

Primary cosmology falsifier remains LiteBIRD β. This protocol runs in parallel.

---

## 1) Objective

Establish a reproducible, decision-grade laboratory campaign that can
**falsify now** if either:

- certified (5,7) platforms reach \(\sigma_A \le 10^{-5}\), pass controls, and
  still return \(A_{CP}^{lab}\) consistent with zero at 95% CL (F-LAB-CP-1), or
- any of F-LAB-CP-2/3/4 is triggered.

Machine-readable implementation:

- `src/core/lab_litebird_substitute.py`
- `tests/test_core_lab_litebird_substitute.py`

---

## 2) Observable and estimator

\[
A_{CP}^{lab} = \frac{\Gamma_+ - \Gamma_-}{\Gamma_+ + \Gamma_-}
\]

- \(\Gamma_+\): conjugate protocol +
- \(\Gamma_-\): conjugate protocol −
- target scale: order \(10^{-5}\)

---

## 3) Hard gates (must all be present for decision-grade)

1. Independent topology certification for stable (5,7)
2. Paired conjugate protocols with raw \(\Gamma_+,\Gamma_-\) published
3. Total uncertainty target met: \(\sigma_A \le 10^{-5}\)
4. Topology-swap controls under matched conditions
5. Sign-reversal controls with CP-even baseline stability
6. Systematics decomposition and correction model
7. At least two independent replications

If any item is missing: **INCONCLUSIVE** (non-falsifier).

---

## 4) Bright-line falsification outcomes

- **F-LAB-CP-1:** Decision-grade null in certified (5,7) with controls/replication
- **F-LAB-CP-2:** Asymmetry statistically topology-independent
- **F-LAB-CP-3:** No CP-odd sign inversion under conjugate reversal
- **F-LAB-CP-4:** Signal removed by systematics model

Any single condition above gives **FALSIFIED (lab transfer lane)**.

---

## 5) Parallel execution plan (multi-track)

Run both tracks concurrently with identical estimator/gates:

- **Track A:** JJ/SQUID arrays
- **Track B:** topological-insulator winding devices

Each track publishes one campaign packet:

- topology evidence
- blinded analysis protocol
- uncertainty budget
- raw and corrected \(A_{CP}^{lab}\)
- topology-swap + sign-reversal controls
- replication status

---

## 6) Decision routing

- **FALSIFIED:** trigger immediate tracker/governance update; do not wait for 2032.
- **SUPPORTED:** mark provisional lab support, keep LiteBIRD as primary cosmology test.
- **INCONCLUSIVE:** continue campaign until decision-grade gates are met.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

