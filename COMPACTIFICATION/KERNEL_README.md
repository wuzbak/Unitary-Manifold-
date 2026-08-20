# Compactification Kernel — Unitary Manifold

*Theory: ThomasCory Walker-Pearson (2026)*
*Code: GitHub Copilot (AI)*
*DOI: https://doi.org/10.5281/zenodo.19584531*

---

## What This Is

The **Compactification Kernel** is the singular seed of the Unitary Manifold.

The full repository spans 785+ pillars, 56,964 tests, 976 Lean4 theorems, and
1,000+ Python modules.  This folder compresses that body of work into the
minimum from which everything can be reconstructed — the same way the extra
dimension of a Kaluza–Klein theory compactifies from an infinite tower of modes
into a finite compact space.

If the forest burns, this is the seed bank.

---

## Files

| File | Purpose |
|------|---------|
| `kernel.py` | Monolithic physics source — all constants, derivations, and pipelines in one file |
| `kernel_test.py` | Standalone verification suite — 59 assertions, zero external dependencies |
| `axioms.py` | Machine-readable axiom registry — 19 entries, 4 epistemic layers |
| `ledger.json` | Snapshot manifest — constants, predictions, gaps, falsification conditions |
| `KERNEL_README.md` | This file |

---

## How to Run

```bash
# Install dependencies (only numpy required; scipy adds ODE support; sympy adds symbolic algebra)
pip install numpy scipy

# Full derivation report (~1 second)
python kernel.py

# Standalone verification (59 assertions)
python kernel_test.py

# Axiom registry and honesty counts
python axioms.py

# pytest-compatible (full suite)
pytest kernel_test.py -v
```

All steps work **offline** on any machine with Python 3.9+.

---

## The Derivation Chain (in brief)

```
Postulate: 5D Kaluza–Klein manifold M₄ × S¹/Z₂
     │
     ▼
5D metric ansatz G_AB = [[g_μν + λ²φ²B_μBᵥ, λφBμ], [λφBᵥ, φ²]]
     │
     ▼
Chern–Simons action on S¹/Z₂ → k_CS = n₁² + n₂²
     │
     ▼
(n₁, n₂) = (5, 7) — unique pair minimizing |β(k) − 0.35°|
     │
     ├── k_CS = 74 ──────────────────────────────┐
     │                                            │
     ▼                                            ▼
APS boundary condition:                    Birefringence angle
k_CS(5)×η̄(5) = 37 (odd ✓)               β ≈ 0.331° canonical
k_CS(7)×η̄(7) = 0  (even ✗)                     [LiteBIRD ~2032]
→ n_w = 5 PROVED
     │
     ▼
KK Jacobian: J = n_w · 2π · √φ₀ ≈ 31.4
     │
     ▼
φ₀_eff = J · φ₀_bare → φ* = φ₀_eff/√3
     │
     ├── nₛ = 1 − 6ε + 2η ≈ 0.9635  [Planck 2018: 0.33σ ✓]
     │
     ├── r_braided = 16ε × c_s ≈ 0.0315  [BICEP/Keck < 0.036 ✓]
     │
     └── α_GUT = N_c/K_CS = 3/74 → Λ_QCD ≈ 198 MeV [DERIVED]
```

---

## Axiom Table (summary)

| Name | Statement | Status |
|------|-----------|--------|
| A0_MANIFOLD | 5D KK manifold M₄ × S¹/Z₂ | **POSTULATED** |
| A1_METRIC | G_AB block form | **DERIVED** |
| A2_FIELD_EQS | Walker–Pearson equations | **DERIVED** |
| A3_BRAID_PAIR | (5,7) braid, k_CS = 74 | **PROVED** |
| A4_NW5 | n_w = 5 uniqueness | **PROVED** |
| A5_AXIOM_A | Z₂-odd CS phase = −1 | **DERIVED** |
| A6_SWAMPLAND | n_w ≤ 15 | **POSTULATED** |
| A7_PHI_ENTROPY | φ = entanglement capacity | **CONJECTURAL** |
| A8_5TH_DIM_IRREV | 5th dimension = irreversibility | **CONJECTURAL** |
| A9_FTUM | U = I + H + T fixed point | **POSTULATED** |
| A10_HOLOGRAPHY | S = A/4G at boundary | **POSTULATED** |
| P1_NS | nₛ ≈ 0.9635 | **PROVED_CONDITIONAL** |
| P2_R | r ≈ 0.0315 | **PROVED_CONDITIONAL** |
| P3_BETA | β ≈ 0.331°–0.351° | **DERIVED** |
| P4_ALPHA_GUT | α_GUT = 3/74 | **DERIVED** |
| P5_LAMBDA_QCD | Λ_QCD ≈ 198–209 MeV | **DERIVED** |
| P6_HIGGS | M_H ≈ 126.2 GeV (1-loop) | **DERIVED** |
| P7_YUKAWA | Fermion masses | **FITTED** |
| P8_DARK_ENERGY | w_KK ≈ −0.9302 | **DERIVED** |

4 POSTULATED, 2 CONJECTURAL, 4 ARCHITECTURE_LIMIT (see `axioms.py` for full detail)

---

## Known Open Gaps (honest ledger)

| ID | Gap | Status |
|----|-----|--------|
| G1 | CMB peak amplitude suppressed ×4–7 | ARCHITECTURE_LIMIT |
| G2 | ADM time synchronisation absent | ARCHITECTURE_LIMIT |
| G3 | Δm²₂₁ tension ~1.07σ | ARCHITECTURE_LIMIT |
| G5 | Yukawa sector FITTED to data | ARCHITECTURE_LIMIT |
| G6 | DESI w_a ≠ 0 tension (3.2σ Planck+BAO) | TENSION |

These are not hidden. They are part of the kernel.

---

## Falsification Conditions (pre-registered)

The framework is **falsifiable**.  Primary test: LiteBIRD (~2032).

| Observable | Condition | Experiment |
|-----------|-----------|------------|
| β (birefringence) | β ∉ [0.22°, 0.38°] or β ∈ [0.29°, 0.31°] | **LiteBIRD ~2032** |
| nₛ | nₛ ∉ [0.952, 0.977] | CMB-S4 / Simons |
| r | r > 0.036 | BICEP Array / CMB-S4 |
| w_a | w_a significantly ≠ 0 at >5σ | DESI Year 5 / Euclid |
| τ_p (proton) | τ_p < 10³⁴ years | Hyper-Kamiokande |

---

## How to Extend

1. Add new physics: extend `kernel.py` with a new function in a clearly labelled
   section.  Import only numpy/scipy.  Document the epistemic label of every
   new constant or derived quantity.
2. Add new tests: add a `test_*` function to `kernel_test.py`.  It will be
   picked up automatically by both the plain-Python runner and pytest.
3. Add a new axiom: append an `Axiom(...)` entry to `AXIOM_REGISTRY` in
   `axioms.py`.  Set `status` honestly.  Always fill in `fallibility_note`.
4. Update the snapshot: edit `ledger.json` to reflect new predictions,
   gap resolutions, or test counts.
5. Do **not** modify the fundamental constants (N1, N2, K_CS, C_S) unless
   a formal proof requires it — those are the invariants.

---

## Attribution

> *Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
> *Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
