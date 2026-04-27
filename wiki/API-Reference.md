# API Reference

Complete public API documentation for all Python modules in the Unitary Manifold package. The 74 geometric pillars are organised by domain.

---

## Core Field Theory (Pillars 1–5)

### `src.core.metric`

Kaluza–Klein metric assembly and curvature computation.

---

#### `field_strength(B, dx)`

Compute the antisymmetric field-strength tensor $H_{\mu\nu} = \partial_\mu B_\nu - \partial_\nu B_\mu$.

| Parameter | Type | Description |
|-----------|------|-------------|
| `B` | `ndarray (N, 4)` | Gauge field $B_\mu$ on N grid points |
| `dx` | `float` | Spatial grid spacing |

**Returns:** `H : ndarray (N, 4, 4)` — antisymmetric field-strength tensor.

---

#### `assemble_5d_metric(g, B, phi, lam=1.0)`

Build the 5×5 Kaluza–Klein metric $G_{AB}$ at each grid point.

| Parameter | Type | Description |
|-----------|------|-------------|
| `g` | `ndarray (N, 4, 4)` | 4D metric |
| `B` | `ndarray (N, 4)` | Irreversibility gauge field |
| `phi` | `ndarray (N,)` | Entanglement-capacity scalar |
| `lam` | `float` | KK coupling constant λ (default 1.0) |

**Returns:** `G5 : ndarray (N, 5, 5)` — full 5D parent metric.

---

#### `christoffel(g, dx)`

Compute Christoffel symbols $\Gamma^\sigma_{\mu\nu}$ from the 4D metric.

| Parameter | Type | Description |
|-----------|------|-------------|
| `g` | `ndarray (N, 4, 4)` | 4D metric |
| `dx` | `float` | Spatial grid spacing |

**Returns:** `Gamma : ndarray (N, 4, 4, 4)` — Gamma[n, sigma, mu, nu].

---

#### `compute_curvature(g, B, phi, dx, lam=1.0)`

Full curvature pipeline: returns the complete hierarchy (Γ, Riemann, Ricci, R).

| Parameter | Type | Description |
|-----------|------|-------------|
| `g` | `ndarray (N, 4, 4)` | 4D metric |
| `B` | `ndarray (N, 4)` | Irreversibility gauge field |
| `phi` | `ndarray (N,)` | Entanglement-capacity scalar |
| `dx` | `float` | Grid spacing |
| `lam` | `float` | KK coupling λ (default 1.0) |

**Returns:** `(Gamma, Riemann, Ricci, R)` with shapes `(N,4,4,4)`, `(N,4,4,4,4)`, `(N,4,4)`, `(N,)`.

---

#### `extract_alpha_from_curvature(g, B, phi, dx)`

Derive $\alpha = \langle 1/\phi^2 \rangle$ from cross-block Riemann components.

**Returns:** `(alpha: float, cross_block_riem: ndarray)`.

---

### `src.core.evolution`

Walker–Pearson field evolution and diagnostics.

---

#### `class FieldState`

Container for the three dynamical fields on a 1D spatial grid.

| Attribute | Type | Description |
|-----------|------|-------------|
| `g` | `ndarray (N, 4, 4)` | 4D metric |
| `B` | `ndarray (N, 4)` | Irreversibility gauge field |
| `phi` | `ndarray (N,)` | Entanglement-capacity scalar |
| `t` | `float` | Current simulation time |
| `dx` | `float` | Grid spacing |
| `lam` | `float` | KK coupling λ |
| `alpha` | `float` | Nonminimal coupling α (= φ₀⁻²) |

##### `FieldState.flat(N=64, dx=0.1, lam=1.0, alpha=0.1, rng=None)`

Factory: flat Minkowski background with small random perturbations. `rng` is a `numpy.random.Generator` for reproducibility.

---

#### `step(state, dt)`

Advance a `FieldState` by one RK4 timestep (default integrator).

| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | `FieldState` | Current state |
| `dt` | `float` | Timestep |

**Returns:** `FieldState` at time `t + dt`.

---

#### `step_euler(state, dt)`

Legacy first-order Euler integrator. For benchmarking only — prefer `step` (RK4) for production.

**Returns:** `FieldState` at time `t + dt`.

---

#### `cfl_timestep(state)`

Estimate the CFL-stable maximum timestep for the current grid.

**Returns:** `float` — recommended maximum `dt`.

---

#### `run_evolution(state, dt, steps, callback=None)`

Integrate the field equations for `steps` timesteps using RK4.

| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | `FieldState` | Initial state |
| `dt` | `float` | Timestep |
| `steps` | `int` | Number of steps |
| `callback` | `callable(state, i)` or `None` | Called after each step |

**Returns:** `list[FieldState]` of length `steps + 1` (includes initial state).

---

#### `information_current(g, phi, dx)`

Compute the conserved information current $J^\mu_{\rm inf} = \phi^2 u^\mu$.

**Returns:** `J : ndarray (N, 4)`.

---

#### `conjugate_momentum_phi(phi, dx, dt)`

Canonical momentum $\pi_\phi = \partial_t\phi$ for the CCR derivation (Theorem XIII).

**Returns:** `ndarray (N,)`.

---

#### `hawking_temperature(phi, g, horizon_index)`

Hawking temperature $T_H = \|\partial_r\phi/\phi\|/2\pi$ at the horizon (Theorem XIV).

**Returns:** `float`.

---

#### `constraint_monitor(Ricci, R, B, phi)`

Return a dict of constraint violation norms:

```python
{
    "ricci_frob_mean": float,  # mean Frobenius norm of Ricci tensor
    "R_max": float,            # max |R| across grid
    "B_norm_mean": float,      # mean |B_μ|
    "phi_max": float,          # max |φ|
}
```

---

### `src.holography.boundary`

Holographic boundary dynamics (Pillar 4).

---

#### `boundary_area(h)`

Proper area of a 2D boundary: $A = \int \sqrt{\det h}\, da$.

| Parameter | Type | Description |
|-----------|------|-------------|
| `h` | `ndarray (M, 2, 2)` | Induced 2D metric |

**Returns:** `float`.

---

#### `entropy_area(h, G4=1.0)`

Bekenstein–Hawking entropy $S = A / (4G_4)$.

**Returns:** `float`.

---

#### `class BoundaryState`

Induced boundary metric and information flux at the holographic screen.

| Attribute | Type | Description |
|-----------|------|-------------|
| `h` | `ndarray (M, 2, 2)` | Induced 2D metric |
| `J_bdry` | `ndarray (M,)` | Normal information flux |
| `kappa` | `ndarray (M,)` | Surface gravity κ |
| `t` | `float` | Current time |

##### `BoundaryState.from_bulk(g, B, phi, dx, t=0.0)`

Project bulk fields onto the holographic boundary.

---

#### `evolve_boundary(bstate, bulk_state, dt)`

Advance the boundary metric by one timestep using:
$$\partial_t h_{ab} = -2K_{ab} + \theta_{ab}[J_{\rm inf}] + \omega_{ab}[\kappa]$$

**Returns:** `BoundaryState`.

---

#### `information_conservation_check(J_bulk, J_bdry, dx)`

Check bulk information conservation via Gauss's theorem. Returns a relative residual (0 = perfectly conserved).

---

### `src.multiverse.fixed_point`

Multiverse fixed-point dynamics (Pillar 5).

---

#### `class MultiverseNode`

Single universe in the thermodynamic multiverse.

| Attribute | Type | Description |
|-----------|------|-------------|
| `dim` | `int` | Dimension of UEUM state vector (default 4) |
| `S` | `float` | Bulk entropy |
| `A` | `float` | Boundary area |
| `Q_top` | `float` | Topological charge |
| `X` | `ndarray (dim,)` | UEUM geodesic position |
| `Xdot` | `ndarray (dim,)` | UEUM geodesic velocity |

##### `MultiverseNode.random(dim=4, rng=None)`

Create a node with random initial state.

##### `MultiverseNode.state_vector()`

Concatenate `(S, A, Q_top, X, Xdot)` into a single vector.

---

#### `class MultiverseNetwork`

Graph of holographic universes.

| Attribute | Type | Description |
|-----------|------|-------------|
| `nodes` | `list[MultiverseNode]` | Universe nodes |
| `adjacency` | `ndarray (n, n)` | Coupling weights (symmetric) |

##### `MultiverseNetwork.chain(n, coupling=0.1, rng=None)`

Create a linear chain of `n` nodes with nearest-neighbour coupling.

##### `MultiverseNetwork.fully_connected(n, coupling=0.1, rng=None)`

Create a fully connected graph of `n` nodes.

##### `MultiverseNetwork.global_state()`

Flatten all node state vectors into one array.

---

#### `apply_irreversibility(node, dt, kappa=0.25)`

**I operator:** entropy growth $dS/dt = \kappa A$. Returns updated `MultiverseNode`.

#### `apply_holography(node, G4=1.0)`

**H operator:** clamp entropy to holographic bound $S \leq A / 4G_4$. Returns updated `MultiverseNode`.

#### `apply_topology(network, node_idx, dt)`

**T operator:** gradient-flow entropy transfer $\Delta S_i = \Delta t \sum_j w_{ij}(S_j - S_i)$. Returns updated `MultiverseNode`.

#### `ueum_acceleration(node, network, node_idx, G4=1.0)`

Evaluate the RHS of the UEUM geodesic equation. Returns `ndarray (dim,)`.

---

#### `fixed_point_iteration(network, max_iter=500, tol=1e-6, dt=1e-3, G4=1.0, kappa=0.25)`

Iterate $U = \mathbf{I} + \mathbf{H} + \mathbf{T}$ until convergence.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `network` | `MultiverseNetwork` | — | Initial state |
| `max_iter` | `int` | 500 | Maximum iterations |
| `tol` | `float` | 1e-6 | Convergence tolerance |
| `dt` | `float` | 1e-3 | Pseudo-timestep |
| `G4` | `float` | 1.0 | Newton's constant |
| `kappa` | `float` | 0.25 | Surface gravity coefficient |

**Returns:** `(converged_network, residual_history, converged_flag)`.

#### `analytic_banach_proof(network)`

Return a dict verifying the Banach fixed-point conditions (contraction constant, domain bound, convergence guarantee).

#### `derive_alpha_from_fixed_point(phi_stabilized)`

Compute $\alpha = \phi_0^{-2}$ from the stabilised radion value.

**Returns:** `(alpha, phi0, L5)`.

#### `shared_fixed_point_norm(network_A, network_B)`

Measure the shared fixed-point alignment between two entangled networks (ER=EPR, Theorem XV).

**Returns:** `float` — norm; → 0 means maximally entangled.

---

## Inflation and CMB (Pillars 27–30, 56, 63)

### `src.core.inflation`

CMB power spectrum and inflation observables.

| Function | Description |
|----------|-------------|
| `ns_prediction(n_w)` | Spectral index from winding number |
| `r_prediction(n_w)` | Tensor-to-scalar ratio (single mode) |
| `birefringence_angle(k_cs)` | Birefringence $\beta$ from CS level |
| `jacobian_5d_4d(n_w, phi0)` | KK Jacobian $J = n_w \cdot 2\pi\sqrt{\phi_0}$ |
| `cmb_observables(n_w, k_cs)` | Dict of $(n_s, r, \beta, \alpha)$ |

---

### `src.core.braided_winding` (Pillar 27)

Braided-geometry extension of the winding sector. **118 tests.**

| Function | Description |
|----------|-------------|
| `braided_sound_speed(n1, n2, k_cs)` | $c_s = \|n_2^2 - n_1^2\|/k_\text{CS}$ |
| `braided_mixing_parameter(n1, n2, k_cs)` | $\rho = 2n_1 n_2/k_\text{CS}$ |
| `braided_r(n_w, c_s)` | $r_\text{braided} = r_\text{bare} \times c_s$ |
| `braided_ns(phi0, c_s)` | $n_s = 1 - 36(1+c_s^2)/\phi_0^2$ |
| `sum_of_squares_resonance(n1, n2)` | Returns $k_\text{CS} = n_1^2 + n_2^2$ |
| `braided_summary()` | Dict of all braided CMB predictions |

---

### `src.core.cmb_transfer` (Pillar 63)

Eisenstein–Hu (1998) CMB transfer function. **106 tests.**

| Function | Description |
|----------|-------------|
| `baryon_loading_R(z, params)` | Baryon-to-photon momentum ratio |
| `eh_transfer_no_baryon(k, params)` | E-H transfer without baryon loading |
| `baryon_acoustic_source(k, params)` | Baryon acoustic oscillation source |
| `angular_power_spectrum_eh(ell, params)` | $C_\ell$ from E-H transfer |
| `dl_from_cl_eh(ell, params)` | $D_\ell = \ell(\ell+1)C_\ell/2\pi$ |
| `um_dl_spectrum(ell, params)` | UM-corrected $D_\ell$ |
| `acoustic_peak_positions(params)` | Predicted $\ell$ values of CMB peaks |
| `suppression_gap_audit(params)` | Documents ×4–7 amplitude suppression |

---

### `src.core.phi0_closure` (Pillar 56)

φ₀ self-consistency and braided closure. **56 new tests.**

| Function | Description |
|----------|-------------|
| `phi0_ftum(n_w, c_s)` | FTUM fixed-point value $\phi_0 = n_w \cdot 2\pi\sqrt{1+c_s^2}$ |
| `ns_from_phi0_braided(phi0, c_s)` | $n_s = 1 - 36(1+c_s^2)/\phi_0^2$ |
| `phi0_eff_from_ns_braided(ns, c_s)` | Inverse: $\phi_0$ from $n_s$ and $c_s$ |
| `braided_closure_audit()` | Verify $n_s^\text{braided}(\phi_0^\text{FTUM}) = n_s^\text{canonical}$ |

---

## Cosmological Epochs (Pillars 63–65)

### `src.core.photon_epoch` (Pillar 64)

Photon epoch cosmology. **141 tests.**

| Function | Description |
|----------|-------------|
| `photon_temperature(z)` | CMB temperature at redshift $z$ |
| `omega_photon_h2()` | Photon density parameter |
| `matter_radiation_equality()` | Redshift of matter-radiation equality |
| `photon_baryon_sound_speed(R)` | $c_{s,\text{PB}} = c/\sqrt{3(1+R)}$ |
| `sound_horizon_analytic(params)` | Analytic sound horizon $r_s$ |
| `silk_diffusion_scale(params)` | Silk damping scale $k_D$ |
| `recombination_redshift(params)` | $z_\text{rec}$ from Saha equation |
| `kk_radion_photon_pressure_ratio(params)` | $P_\text{KK}/P_\gamma$ ratio |
| `photon_epoch_summary()` | Dict of all epoch quantities |

> **Key distinction:** $c_{s,\text{PB}} \approx 0.45$ (photon-baryon fluid) ≠ $c_s = 12/37$ (KK radion sector). These are different physical sound speeds.

---

### `src.core.quark_gluon_epoch` (Pillar 65)

QGP radion epoch. **120 tests.**

| Function | Description |
|----------|-------------|
| `qgp_sound_speed_um()` | Returns $c_s = 12/37$ (UM prediction) |
| `qgp_cs2_reference_values()` | Lattice QCD reference $c_s^2 \approx 0.33$ |
| `qgp_radion_cs_coincidence_audit()` | Documents the $c_s^2$ numerical coincidence |
| `qgp_radion_pressure_fraction(T)` | KK radion pressure fraction at temperature $T$ |
| `qgp_alpha_s_running(mu)` | Running strong coupling $\alpha_s(\mu)$ |
| `qgp_summary()` | Dict of QGP-epoch quantities |

> **Epistemic note:** $c_s = 12/37 \approx 0.324$ vs QGP $c_s^2 \approx 0.33$ is a **dimensional coincidence**, not a prediction.

---

## Observational Forecasts (Pillars 66–68)

### `src.core.roman_space_telescope` (Pillar 66)

Nancy Grace Roman Space Telescope UM falsification forecasts. **187 tests.**

| Function | Description |
|----------|-------------|
| `roman_um_dark_energy_eos()` | $w_\text{KK} = -1 + \tfrac{2}{3}c_s^2 \approx -0.930$ |
| `roman_cpl_w_at_z(z)` | CPL dark energy EoS $w(z)$ |
| `roman_wl_sigma_w()` | WL forecast $\sigma(w) \approx 0.02$ |
| `roman_wl_sigma_s8()` | WL forecast $\sigma(S_8)$ |
| `roman_sne_sigma_h0()` | SNe Ia forecast $\sigma(H_0)$ |
| `roman_bao_sigma_w()` | BAO forecast $\sigma(w)$ |
| `roman_combined_sigma_w()` | Combined Roman $\sigma(w)$ |
| `roman_bao_shift_kk()` | BAO shift from KK modification |
| `roman_s8_kk()` | $S_8$ prediction from KK dark energy |
| `roman_um_w_tension_audit()` | Hubble tension audit |
| `roman_um_s8_audit()` | $S_8$ tension audit |
| `roman_falsification_conditions()` | Dict of Roman falsification thresholds |
| `roman_summary()` | Full Roman forecast summary dict |

---

### `src.core.nw_anomaly_selection` (Pillar 67)

Anomaly-cancellation uniqueness argument for $n_w$ selection. **156 tests.**

| Function | Description |
|----------|-------------|
| `anomaly_cancel_constraint(n_w)` | Z₂ anomaly cancellation check |
| `n_gen_stability(n_w)` | $N_\text{gen}=3$ stability under CS gap |
| `k_eff(n_w)` | Effective CS level: $k_\text{eff}(5)=74$, $k_\text{eff}(7)=130$ |
| `nw_saddle_comparison()` | Comparison: $n_w=5$ is dominant saddle |
| `n_gen_derivation_status()` | Status of $N_\text{gen}$ derivation |

---

### `src.core.completeness_theorem` (Pillar 74)

k_CS = 74 Topological Completeness Theorem. **170 tests.**

| Function | Description |
|----------|-------------|
| `c1_sum_of_squares()` | C1: $5^2 + 7^2 = 74$ |
| `c2_cs_gap_saturation()` | C2: CS gap saturation |
| `c3_birefringence()` | C3: birefringence minimiser at $k=74$ |
| `c4_sound_speed_fraction()` | C4: $c_s = 12/37$ from $k=74$ |
| `c5_moduli_winding_link()` | C5: moduli-winding link |
| `c6_pillar_count()` | C6: 74 pillars closed |
| `c7_backreaction_eigenvalue()` | C7: back-reaction eigenvalue = 1 |
| `repository_closure_statement()` | Capstone: all 7 constraints → 74 |

---

## Extended Pillars — Natural Sciences

### `src.consciousness.coupled_attractor` (Pillar 9)

Coupled brain-universe attractor. **61 tests.**

The brain and universe share the same 5D geometry. Consciousness is the coupled fixed point of $U_\text{total}(\Psi_\text{brain} \otimes \Psi_\text{univ}) = \Psi_\text{brain} \otimes \Psi_\text{univ}$ with coupling constant $\beta = 0.3513°$ (birefringence angle).

---

### `src.chemistry` (Pillar 10)

φ-geometric chemistry: bonds, reactions, periodic table structure.
- `bonds.py` — chemical bond geometry from KK metric
- `reactions.py` — reaction rates from entropic suppression
- `periodic.py` — periodic table structure from winding modes

---

### `src.astronomy` (Pillar 11)

Stellar and planetary UM geometry.
- `stellar.py` — stellar structure with irreversibility field
- `planetary.py` — planetary formation and orbital dynamics

---

### `src.earth` (Pillar 12)

Earth sciences: geology, oceanography, meteorology under UM framework.

---

### `src.biology` (Pillar 13)

Life sciences: evolution, morphogenesis, and biological irreversibility.

---

### `src.atomic_structure` (Pillar 14)

Atomic orbitals, spectroscopy, and fine structure. **187 tests.**
- `orbitals.py` — KK-corrected hydrogen wavefunctions
- `spectroscopy.py` — spectral line predictions
- `fine_structure.py` — fine structure from radion coupling

---

### `src.cold_fusion` (Pillar 15)

φ-enhanced tunneling and Pd lattice dynamics. **215 tests.**
- `tunneling.py` — Gamow factor with φ-enhancement (falsifiable COP prediction)
- `lattice.py` — Pd lattice phonon-radion bridge
- `excess_heat.py` — excess heat prediction model

> **Epistemic note:** This is explicitly framed as a falsifiable prediction. It is NOT a confirmation that LENR occurs.

---

### `recycling/` (Pillar 16)

φ-debt entropy accounting system. **316 tests.**

---

### `src.medicine` (Pillar 17)

Diagnosis, treatment, and systemic φ homeostasis. **139 tests.**

---

### `src.justice` (Pillar 18)

Courts, sentencing, and reform as φ equity. **124 tests.**

---

### `src.governance` (Pillar 19)

Democracy, social contract, and stability. **115 tests.**

---

### `src.neuroscience` (Pillar 20)

Neurons, synaptic dynamics, and cognition as φ networks. **92 tests.**

---

### `src.ecology` (Pillar 21)

Ecosystems, biodiversity, and food webs. **70 tests.**

---

### `src.climate` (Pillar 22)

Atmosphere, carbon cycle, and feedback. **66 tests.**

---

### `src.marine` (Pillar 23)

Deep ocean, marine life, and ocean dynamics. **72 tests.**

---

### `src.psychology` (Pillar 24)

Cognition, behaviour, and social psychology. **82 tests.**

---

### `src.genetics` (Pillar 25)

Genomics, evolution, and gene expression. **78 tests.**

---

### `src.materials` (Pillar 26)

Condensed matter, semiconductors, and metamaterials. **75 tests.**

---

## Selected Additional Core Modules

### `src.core.kk_backreaction` (Pillar 52)

KK graviton back-reaction and irreversibility proof. Includes `kk_tower_irreversibility_proof()`.

### `src.core.three_generations` (Pillar 60)

Three-generation derivation from winding sector. Includes `n_gen_derivation_status()`.

### `src.core.muon_g2` (Pillar 51)

KK graviton and ALP Barr–Zee contributions to muon anomalous magnetic moment.

### `src.core.fiber_bundle`

Principal bundle topology, characteristic classes, and anomaly cancellation. **96 tests.**

### `src.core.kk_collider_resonances` (Pillar 43)

KK resonance forecasts for collider experiments (CMS/ATLAS). Includes `cms_run2_kk_exclusion_floor()` and `cms_95gev_diphoton_alp_check()` (CMS arXiv:2405.09320).

### `src.core.nonabelian_kk` (Pillar 62)

Non-Abelian KK gauge theory and running couplings. Includes `cms_alphas_rg_consistency()` with CMS $\alpha_s(M_Z) = 0.1179$ anchor.

### `src.core.litebird_forecast`

LiteBIRD birefringence forecast — primary near-term falsifier of the UM framework.

### `src.core.bh_remnant` (Theorem XVII)

KK black hole remnant mass: $M_\text{rem} = \phi_\text{min} / (8\pi m_\phi \Delta\phi)$.

---

## Unitary Pentad (Independent Governance Framework)

The `Unitary Pentad/` directory contains an independent HILS (Human-in-the-Loop Systems) governance framework with 18 modules and **1,234 tests**. It borrows mathematical structure from the Unitary Manifold but does **not** depend on the physics being correct. See [`SEPARATION.md`](../SEPARATION.md) for the precise boundary between the physics framework and the governance framework.
