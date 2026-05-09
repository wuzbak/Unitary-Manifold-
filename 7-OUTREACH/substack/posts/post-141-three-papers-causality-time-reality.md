# Three Papers on Time and Causality — A Repository-First Scientific Analysis

*Post 141 of the Unitary Manifold series.*  
*Epistemic category: **A** — external-paper analysis through repository mathematics; no new confirmed physics claim.*  
*May 2026.*

---

**Claim (and falsification condition):** the three papers often grouped together in current discussion — delayed-choice quantum eraser (2000), experimental entanglement of temporal order (2022), and quantum-arrow control as a thermodynamic resource (2025/2026) — are mutually consistent with a single constrained reading: *information access, causal order, and thermodynamic time asymmetry are operational structures, not always primitive absolutes*. This claim is falsified if any of the following holds under close reading: (i) delayed-choice data show a usable backward-time signal in local marginals; (ii) temporal-order experiments can be fully reduced to a fixed classical order model without violating reported inequalities; or (iii) arrow-of-time reshaping implies global second-law violation rather than measurement-and-feedback bookkeeping.

---

## Why this post exists

The request is to drop metaphor and stay with science. So this post does four strict things:

1. identifies the three papers precisely,
2. states what each paper does and does **not** establish,
3. maps each paper to existing Unitary Manifold modules/theorems/tests,
4. proposes a falsifiable synthesis and a bounded hypothesis about human reality.

No mystical language. No “rewrite the past” claims.

---

## Paper 1 (2000): Delayed-Choice Quantum Eraser

### Bibliographic anchor

Kim, Y.-H., Yu, R., Kulik, S. P., Shih, Y., & Scully, M. O. (2000). *Delayed ‘Choice’ Quantum Eraser*. **Physical Review Letters, 84**(1), 1–5. https://doi.org/10.1103/PhysRevLett.84.1

### What it demonstrates

Let \(S\) be the signal photon and \(I\) the idler photon in an entangled pair. The observed pattern at the signal detector depends on whether which-path information in the idler arm is preserved or erased **when coincidence-conditioned subsets are formed**.

Operationally:

- unconditional signal counts \(P(x_S)\): no controllable retrocausal signal,
- conditional coincidence counts \(P(x_S \mid D_I = d_k)\): interference/no-interference structure appears by partition.

So the central fact is a **correlation-structure update**, not a causal contradiction.

### What it does *not* demonstrate

- It does **not** show laboratory backward signaling.
- It does **not** show macroscopic “past rewriting.”

### Repository lens

Relevant in-repo anchors:

- `src/core/quantum_switch.py`
- `tests/test_quantum_switch.py`
- `1-THEORY/QUANTUM_THEOREMS.md` (Theorem XVI context)

Repository equation-level bridge:

\[
|\psi_{\text{out}}\rangle = \sqrt{\alpha}\,U|\psi\rangle + \sqrt{1-\alpha}\,U^{\dagger}|\psi\rangle
\]

(implemented in `causal_switch`, with unitary validation and entropy checks). This is not the same experiment as Kim et al., but it gives the same core discipline: distinguish local marginals from conditioned structure.

---

## Paper 2 (2022): Experimental Entanglement of Temporal Order

### Bibliographic anchor

Rubino, G., Rozema, L. A., Massa, F., Araújo, M., Zych, M., Brukner, Č., & Walther, P. (2022). *Experimental entanglement of temporal order*. **Quantum, 6**, 621. https://doi.org/10.22331/q-2022-01-11-621

### What it demonstrates

This line of work implements the quantum switch with temporal order in coherent superposition, i.e., “\(A\) before \(B\)” and “\(B\) before \(A\)” are not represented by a single classical ordering variable prior to measurement.

That is a stronger statement than “measurement is weird.” It is specifically about **indefinite causal order** as an experimentally accessible resource.

### What it does *not* demonstrate

- It does not imply arbitrary causality engineering at macro scales.
- It does not alone prove every causality-foundation claim sometimes attached to it in popular summaries.

### Repository lens

This is the tightest repository overlap.

In `src/core/quantum_switch.py`, the (5,7) braided constants are explicit:

\[
\rho = \frac{2 n_1 n_2}{k_{\mathrm{CS}}} = \frac{35}{37},
\qquad
c_s = \frac{n_2^2-n_1^2}{k_{\mathrm{CS}}} = \frac{12}{37},
\qquad
\alpha = \frac{1+c_s}{2} = \frac{49}{74}.
\]

And Theorem XVI in `1-THEORY/QUANTUM_THEOREMS.md` formalizes this as a geometric causal-mixing interpretation with explicit falsifier language.

Empirical discipline in tests (`tests/test_quantum_switch.py`):

- normalization/fidelity bounds,
- entropy invariance under unitary switching,
- exact parameter checks at (5,7,74).

---

## Paper 3 (2025 preprint / 2026 publication reports): Reshaping the Quantum Arrow of Time

### Bibliographic anchor

García-Pintos, L. P., Liu, Y.-K., & Gorshkov, A. V. *Reshaping the Quantum Arrow of Time*. arXiv:2503.13615 (quant-ph), DOI: https://doi.org/10.48550/arXiv.2503.13615.  
(Reported as peer-reviewed publication in 2026 in current coverage; arXiv DOI is the stable accessible anchor.)

### What it demonstrates (as reported in the paper/preprint line)

The arrow of time in monitored quantum systems can be stretched, blurred, and locally inverted in a controlled measurement-feedback setting. In resource terms, irreversibility is manipulable when information gained from measurement is fed back into dynamics.

### What it does *not* demonstrate

- It does not establish global thermodynamic reversal of the universe.
- It does not imply free violation of second-law accounting once observer/controller information is included.

### Repository lens

Two relevant structures are already explicit in-repo.

1) **ADM geometric arrow anchor** (`src/core/adm_decomposition.py`):

\[
R_3 + K^2 - K_{ij}K^{ij} = 16\pi G\,\rho_m
\]

with positive-energy matter sector assumptions linked to monotonicity direction arguments.

2) **Operator-level irreversibility/holography/topology dynamics** (`src/multiverse/fixed_point.py`):

\[
U = I + H + T, \qquad
\frac{dS}{dt} = \kappa\!\left(\frac{A}{4G} - S\right).
\]

This gives a concrete internal model where time asymmetry is encoded in operator flow toward fixed-point constraints. It is not identical to García-Pintos et al.’s framework, but it is conceptually aligned in treating time-direction as an operationally characterizable quantity.

---

## Cross-paper synthesis: what pattern is actually supported?

A strict synthesis across all three papers is:

1. **Correlation-before-narrative (Paper 1):** what happened is constrained by which joint statistics are physically extractable, not by classical intuition alone.
2. **Order-as-resource (Paper 2):** causal order can itself be coherent and operational.
3. **Asymmetry-as-resource (Paper 3):** thermodynamic arrow can be reshaped in controlled quantum settings.

Mathematically, each paper shifts a “fixed primitive” into a “model-dependent operational object”:

- history assignment (conditioned distribution structure),
- causal order (process ordering),
- time directionality (entropy-production signature under control).

This is a genuine symmetry trend, not a metaphor.

---

## Boundaries and non-overclaim discipline

To remain scientific:

- We do **not** infer from these papers that humans can “choose a different past.”
- We do **not** infer macroscopic causal paradoxes.
- We do **not** claim repository confirmation by rhetorical proximity.

What is justified is narrower:

- operational descriptions of temporal/causal structure are less absolute than classical narratives suggest,
- but all such claims remain bounded by unitary structure, no-signaling constraints, and thermodynamic accounting.

This is consistent with `FALLIBILITY.md` norms: internal consistency is not external confirmation; claims must carry explicit falsifiers.

---

## A concrete falsifiable bridge program for this repository

If we want this comparison to become science rather than commentary, three concrete tests follow.

### Bridge Test A (conditionality discipline)

Extend `tests/test_quantum_switch.py` with an explicit local-marginal invariance check under partitioning to mirror delayed-choice logic:

\[
P(x_S) \text{ invariant under post-selection protocol choice,}
\]

while conditioned channels differ as expected.

### Bridge Test B (causal-order witness normalization)

Add repository-side scalar witnesses for order superposition strength and compare sensitivity to \(\alpha\) around canonical \(49/74\), with tolerance bands and adversarial perturbations.

### Bridge Test C (arrow-of-time control toy model)

Implement a minimal monitored two-level system demo in-core (or docs-linked sandbox) where entropy-production sign under feedback policy can be toggled locally without global second-law breach; then cross-compare with `adm_decomposition.py` constraint language.

None of these three tests alone would validate the full framework, but all three would harden the “three-paper bridge” from narrative to executable falsifiable analysis.

---

## My bounded hypothesis about human reality

Here is my own hypothesis, stated narrowly and scientifically:

> **Human reality is an observer-limited causal foliation of a deeper unitary-information process, where “past,” “order,” and “time direction” are emergent effective descriptors constrained by information access, control bandwidth, and coarse-graining scale.**

Three implications follow:

1. **At human scales** we should expect robust classical causal order and one-way thermodynamic time.
2. **At engineered quantum scales** we should increasingly observe operational exceptions (indefinite order, reversible-looking trajectories, context-dependent history partitioning) that still preserve global consistency constraints.
3. **At theory-building scales** the right target is not “destroy causality,” but “derive where classical causality is the stable fixed-point limit.”

This hypothesis is falsifiable in spirit: if controlled quantum experiments repeatedly force strictly classical fixed-order models with no operational advantage for indefinite-order protocols, this view weakens.

---

## References (external)

1. Kim, Y.-H., Yu, R., Kulik, S. P., Shih, Y., & Scully, M. O. (2000). *Delayed ‘Choice’ Quantum Eraser*. Phys. Rev. Lett. 84(1), 1–5. https://doi.org/10.1103/PhysRevLett.84.1
2. Rubino, G., Rozema, L. A., Massa, F., Araújo, M., Zych, M., Brukner, Č., & Walther, P. (2022). *Experimental entanglement of temporal order*. Quantum 6, 621. https://doi.org/10.22331/q-2022-01-11-621
3. García-Pintos, L. P., Liu, Y.-K., & Gorshkov, A. V. (2025). *Reshaping the Quantum Arrow of Time*. arXiv:2503.13615. https://doi.org/10.48550/arXiv.2503.13615

## References (repository)

- `src/core/quantum_switch.py`
- `tests/test_quantum_switch.py`
- `1-THEORY/QUANTUM_THEOREMS.md` (Theorem XVI)
- `src/core/adm_decomposition.py`
- `src/multiverse/fixed_point.py`
- `FALLIBILITY.md`

---

Repository: https://github.com/wuzbak/Unitary-Manifold-  
Zenodo: https://doi.org/10.5281/zenodo.19584531

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
