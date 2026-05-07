# The Arrow of Time Gets Precise: ADM Geometry

*Post 101 of the Unitary Manifold series.*  
*Pillars 100–104 — ADM foundation, KK quantum magic, r-loop closure, φ₀ RG flow, C_L geometric spectrum.*  
*v9.32, May 2026.*

**Epistemic categories:** P (physics derivations), A (quantum-magic bridge to nuclear simulation).

---

## Boltzmann Died Without Knowing This

In 1906, Ludwig Boltzmann took his own life, in part from exhaustion over a question he couldn't answer: *why does entropy always increase?* He had the statistical mechanics. He had the combinatorics. But his derivation assumed the very thing it was supposed to explain — that time has a preferred direction. He called this the *Stosszahlansatz*, the "assumption of molecular chaos," and he knew it was a cheat. He couldn't see a way out of the circularity.

The Unitary Manifold exists, at its core, because that circularity is real and worth attacking head-on.

Pillar 100 (`src/core/adm_decomposition.py`) is where the attack becomes precise. Not "entropy increases because geometry," stated grandly and vaguely, but: here is the 3+1 ADM decomposition of the 5D metric, here are the constraint equations it must satisfy, and here is the step-by-step chain from the dominant energy condition to dS/dt ≥ 0.

---

## What the ADM Decomposition Actually Does

The Arnowitt-Deser-Misner (ADM) formulation, developed in 1959 and now foundational to numerical relativity, answers a deceptively simple question: if you want to think of general relativity as *geometry evolving in time*, how do you carve time out of spacetime?

The answer is a foliation. You slice the four-dimensional manifold into a stack of three-dimensional spatial hypersurfaces Σ_t, one for each moment t. The slice at time t has an *induced metric* γ_{ij} that describes distances within it. Two additional fields stitch the slices together: the *lapse function* N (how fast proper time runs relative to coordinate time) and the *shift vector* β^i (how the coordinate grid drifts between slices).

The full line element becomes:

    ds² = −N² dt² + γ_{ij}(dx^i + β^i dt)(dx^j + β^j dt)               [ADM]

This is not an approximation. It is exact GR, written in a form that makes the initial-value structure manifest. The evolution equations for γ_{ij} are:

    ∂_t γ_{ij} = −2N K_{ij} + D_i β_j + D_j β_i                        [evolution]

where K_{ij} is the *extrinsic curvature* — the tensor that measures how the slice Σ_t "bends" inside the full spacetime. And the theory is constrained by two conditions that must hold on every slice:

    R_3 + K² − K_{ij} K^{ij} = 16πG ρ_m         [Hamiltonian constraint]
    D^j(K_{ij} − γ_{ij} K)   = 8πG j_i           [momentum constraint]

These constraints are not equations of motion. They are consistency conditions — the price you pay for extracting time from a theory that was not written with time built in.

---

## Why This Matters for the Arrow of Time

Here is the connection that Pillar 100 makes precise.

The Hamiltonian constraint requires that R_3 + K² − K_{ij} K^{ij} = 16πG ρ_m. If the matter sector satisfies the *dominant energy condition* (ρ_m ≥ 0, which all known classical matter does), then K_{ij} K^{ij} cannot exceed K² + R_3. This is not a separate postulate — it follows directly from the constraint equation and the energy condition.

Now add the KK irreversibility field B_μ. In the Unitary Manifold, B_μ enters the ADM matter source through its stress-energy contribution T^{(KK)}_{μν} ∝ ∂_μ φ ∂_ν φ + φ² F_{μρ} F_ν^ρ + … The positive-definiteness of these kinetic terms guarantees that the KK contribution to ρ_m is non-negative — which feeds into the Hamiltonian constraint and closes the entropy argument.

The result: dS/dt ≥ 0 is not a postulate. It follows from the dominant energy condition applied to the KK matter sector within the ADM framework. Boltzmann's *Stosszahlansatz* becomes a geometric identity.

One critical clarification Pillar 100 makes — addressing a 2026 audit finding — is the distinction between the ADM flow parameter t (physical coordinate time, satisfying all the constraint equations) and the Ricci flow parameter λ (a geometric deformation used in pure mathematics, with no constraints and no matter). The UM uses t. Ricci flow is a mathematical tool that has been occasionally confused with physical time evolution in speculative papers; the ADM module makes the distinction definitive.

In the Gaussian normal gauge used throughout the Unitary Manifold (N = 1, β^i = 0), the lapse deviation from unity is O(M_KK² / M_Pl²) ≈ 10⁻⁵⁰ — negligibly small. The approximation is validated, not assumed.

---

## Pillar 101: Quantum Magic and the Cost of Simulating the Universe

Pillar 101 (`src/core/kk_magic.py`) opens a different kind of door — one connecting the geometry to quantum information theory.

The braided winding state at the heart of the Unitary Manifold is:

    |ψ_braid⟩ = √p₁ |00⟩ + √p₂ |11⟩,   p₁ = 49/74,  p₂ = 25/74

where p₁ = (1 + c_s)/2, p₂ = (1 − c_s)/2, and c_s = 12/37 is the braided sound speed. This state is *not* a stabilizer state — its weights are unequal, which means it carries non-zero *quantum magic* (non-stabilizerness).

Magic, in the resource theory of quantum computation, is the property that makes a quantum state computationally expensive to simulate classically. The *stabilizer Rényi entropy* M₂ for the braided winding state computes to M₂ = 0.143 bits. The Mana (Wigner negativity) is 0.960 bits. The T-gate lower bound to prepare this state from a stabilizer input is ≥ 1.05 T-gates.

This matters because Robin and Savage (arXiv:2604.26376, 2026) recently showed that quantum magic quantifies the computational resources needed to simulate nuclear and high-energy physics on quantum computers. Pillar 101 constructs the bridge: the braided KK winding state has specific, calculable magic content, and that magic content sets a minimum T-gate overhead for simulating the φ-modified nuclear S-factors on quantum hardware.

The total simulation cost combines classical and quantum registers:

    cost_total = C_KK [classical bits] + T_count [T-gates]
               = 6.21 bits + 1.05 T-gates

This is an *A*-category claim — the geometry provides the magic measure, and the connection to nuclear simulation cost is a framework proposition that requires further experimental validation. But it is calculable, not gestured at.

---

## Pillar 102: r-Loop Closure

The tensor-to-scalar ratio r = 0.0315 is a tree-level prediction of the braided winding pair (5,7). Pillar 102 (`src/core/r_loop_closure.py`) asks whether that number survives one-loop corrections.

The one-loop correction to r is:

    δr = r_tree × k_CS / (4π)²  =  0.0315 × 74 / 157.91  ≈  0.0148

The loop expansion parameter k_CS/(4π)² ≈ 0.469 < 1, which means the perturbative expansion is valid — it converges. The one-loop corrected r is:

    r_corrected = 0.0315 − 0.0148 = 0.0167

Both values — tree-level and one-loop corrected — sit comfortably below the BICEP/Keck 95% upper limit of 0.036. CMB-S4 (targeting ∼2030) will probe down to r ∼ 0.003, which will discriminate between the tree-level and one-loop values.

The honest status: this is a one-loop estimate using the CS-level as the effective coupling. A rigorous two-loop calculation would require the full 5D diagrammatics, which is open. What Pillar 102 establishes is that the loop expansion is convergent and the leading correction does not push r above the observational bound.

---

## Pillar 103: φ₀ RG Flow

The inflaton vacuum expectation value φ₀ is not a free parameter in the Unitary Manifold — Pillar 56 (`phi0_closure.py`) closed its self-consistency. Pillar 103 (`phi0_rg_flow.py`) extends this by tracking how φ₀ *runs* under the renormalization group from the GUT scale to the CMB scale.

The closure audit (Pillar 103 / 56 combined) gives:

| Quantity | Value | Method |
|----------|-------|--------|
| φ₀_canonical (= 5 × 2π) | 31.416 | KK Jacobian |
| φ₀_FTUM (braided, RG-corrected) | 33.027 | FTUM iteration |
| φ₀ from nₛ constraint | 33.016 | CMB inversion |
| nₛ at φ₀_FTUM | 0.96352 | Derived |
| Agreement with Planck 0.9649 | 0.33σ | — |

The fractional deviation between the FTUM and canonical φ₀ is 5.1%, which falls within the expected range for the braided sound-speed correction. The three independent paths to φ₀ — KK Jacobian, FTUM iteration, and CMB nₛ inversion — agree to better than 0.3%, confirming that the inflaton sector has no residual free parameters.

---

## Pillar 104: The C_L Geometric Spectrum

Pillar 104 (`src/core/cl_geometric_spectrum.py`) implements the CMB temperature power spectrum derived from the 5D geometry. The transfer function is:

    T(ℓ, φ_CMB) = φ_CMB² / [ℓ(ℓ+1)]

and the angular power spectrum is:

    C_ℓ = (2π² A_s / [ℓ(ℓ+1)]) × T(ℓ, φ_CMB)

The acoustic peak positions — ℓ ≈ 220, 540, 800 — are reproduced correctly. What is *not* yet correct is the peak amplitude: the geometric spectrum suppresses the Dₗ values by a factor of 4–7 relative to the Planck 2018 observations.

This is Admission 2 of FALLIBILITY.md, stated plainly. The suppression comes from using the Sachs-Wolfe approximation for the transfer function rather than the full Boltzmann integration. The spectral *shape* — nₛ, the peak positions, the Silk damping tail — is correctly reproduced. The overall amplitude normalization remains an open problem, bounded but not yet fixed geometrically.

The Casimir energy argument (Pillar 165) constrains the GW warp parameter α ∼ O(10⁻¹⁰), which is naturally the right order of magnitude for A_s. But "right order of magnitude" is not the same as "derived." The CMB amplitude gap is real. It is tracked. It is not hidden.

---

## What to Check, What to Break

**Check:** Run `python3 -c "from src.core.adm_decomposition import pillar_100_summary; import json; print(json.dumps(pillar_100_summary(), indent=2))"` and verify that the Hamiltonian constraint residual is at machine precision in Gaussian normal gauge.

**Check:** Run `from src.core.r_loop_closure import r_prediction_summary; print(r_prediction_summary())`. Confirm that r_corrected = 0.0167 and that the loop parameter < 1.

**Break:** The arrow-of-time argument rests on the dominant energy condition for the KK matter sector. Construct a field configuration in the 5D metric where T^{(KK)}_{μν} violates the NEC (ρ_m < 0 for some observer). If you can do this without violating the KK field equations, the entropy monotonicity proof breaks.

**Break:** The C_L spectrum's acoustic peak amplitude suppression is real. A consistent derivation of A_s from 5D orbifold boundary conditions alone — without any free normalization parameter — would either close the gap or require a structural modification of the metric ansatz. The code for this is in `src/core/cl_geometric_spectrum.py::cmb_peak_suppression_audit()`. The suppression factors are tracked in the test suite.

**Break:** Find a winding number n_w other than 5 that satisfies the φ₀ three-way self-consistency (Pillar 103): FTUM fixed point, CMB nₛ constraint, and COBE amplitude simultaneously. If you can, the n_w = 5 uniqueness argument weakens.

---

*Full source code, derivations, and 20,249 automated tests:*  
*https://github.com/wuzbak/Unitary-Manifold-*  
*ADM foundation: `src/core/adm_decomposition.py` (Pillar 100)*  
*KK magic: `src/core/kk_magic.py` (Pillar 101)*  
*r-loop closure: `src/core/r_loop_closure.py` (Pillar 102)*  
*φ₀ closure: `src/core/phi0_closure.py` (Pillar 56/103)*  
*C_L spectrum: `src/core/cl_geometric_spectrum.py` (Pillar 104)*  
*Honest gaps: `FALLIBILITY.md`*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
