# API Reference

Complete public API documentation for all Python modules in the Unitary Manifold package.

---

## `src.core.metric`

Kaluza–Klein metric assembly and curvature computation.

---

### `field_strength(B, dx)`

Compute the antisymmetric field-strength tensor $H_{\mu\nu} = \partial_\mu B_\nu - \partial_\nu B_\mu$.

| Parameter | Type | Description |
|-----------|------|-------------|
| `B` | `ndarray (N, 4)` | Gauge field $B_\mu$ on N grid points |
| `dx` | `float` | Spatial grid spacing |

**Returns:** `H : ndarray (N, 4, 4)` — antisymmetric field-strength tensor.

---

### `assemble_5d_metric(g, B, phi, lam=1.0)`

Build the 5×5 Kaluza–Klein metric $G_{AB}$ at each grid point.

| Parameter | Type | Description |
|-----------|------|-------------|
| `g` | `ndarray (N, 4, 4)` | 4D metric |
| `B` | `ndarray (N, 4)` | Irreversibility gauge field |
| `phi` | `ndarray (N,)` | Entanglement-capacity scalar |
| `lam` | `float` | KK coupling constant λ (default 1.0) |

**Returns:** `G5 : ndarray (N, 5, 5)` — full 5D parent metric.

---

### `christoffel(g, dx)`

Compute Christoffel symbols $\Gamma^\sigma_{\mu\nu}$ from the 4D metric.

| Parameter | Type | Description |
|-----------|------|-------------|
| `g` | `ndarray (N, 4, 4)` | 4D metric |
| `dx` | `float` | Spatial grid spacing |

**Returns:** `Gamma : ndarray (N, 4, 4, 4)` — Gamma[n, sigma, mu, nu].

---

### `compute_curvature(g, B, phi, dx, lam=1.0)`

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

## `src.core.evolution`

Walker–Pearson field evolution and diagnostics.

---

### `class FieldState`

Container for the three dynamical fields on a 1D spatial grid.

| Attribute | Type | Description |
|-----------|------|-------------|
| `g` | `ndarray (N, 4, 4)` | 4D metric |
| `B` | `ndarray (N, 4)` | Irreversibility gauge field |
| `phi` | `ndarray (N,)` | Entanglement-capacity scalar |
| `t` | `float` | Current simulation time |
| `dx` | `float` | Grid spacing |
| `lam` | `float` | KK coupling λ |
| `alpha` | `float` | Nonminimal coupling α |

#### `FieldState.flat(N=64, dx=0.1, lam=1.0, alpha=0.1, rng=None)`

Factory: flat Minkowski background with small random perturbations. `rng` is a `numpy.random.Generator` for reproducibility.

---

### `step(state, dt)`

Advance a `FieldState` by one explicit-Euler timestep.

| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | `FieldState` | Current state |
| `dt` | `float` | Timestep |

**Returns:** `FieldState` at time `t + dt`.

---

### `run_evolution(state, dt, steps, callback=None)`

Integrate the field equations for `steps` timesteps.

| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | `FieldState` | Initial state |
| `dt` | `float` | Timestep |
| `steps` | `int` | Number of steps |
| `callback` | `callable(state, i)` or `None` | Called after each step |

**Returns:** `list[FieldState]` of length `steps + 1` (includes initial state).

---

### `information_current(g, phi, dx)`

Compute the conserved information current $J^\mu_{\rm inf} = \phi^2 u^\mu$.

**Returns:** `J : ndarray (N, 4)`.

---

### `constraint_monitor(Ricci, R, B, phi)`

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

## `src.holography.boundary`

Holographic boundary dynamics (Pillar 4).

---

### `boundary_area(h)`

Proper area of a 2D boundary: $A = \int \sqrt{\det h}\, da$.

| Parameter | Type | Description |
|-----------|------|-------------|
| `h` | `ndarray (M, 2, 2)` | Induced 2D metric |

**Returns:** `float`.

---

### `entropy_area(h, G4=1.0)`

Bekenstein–Hawking entropy $S = A / (4G_4)$.

**Returns:** `float`.

---

### `class BoundaryState`

Induced boundary metric and information flux at the holographic screen.

| Attribute | Type | Description |
|-----------|------|-------------|
| `h` | `ndarray (M, 2, 2)` | Induced 2D metric |
| `J_bdry` | `ndarray (M,)` | Normal information flux |
| `kappa` | `ndarray (M,)` | Surface gravity κ |
| `t` | `float` | Current time |

#### `BoundaryState.from_bulk(g, B, phi, dx, t=0.0)`

Project bulk fields onto the holographic boundary.

---

### `evolve_boundary(bstate, bulk_state, dt)`

Advance the boundary metric by one timestep using:
$$\partial_t h_{ab} = -2K_{ab} + \theta_{ab}[J_{\rm inf}] + \omega_{ab}[\kappa]$$

**Returns:** `BoundaryState`.

---

### `information_conservation_check(J_bulk, J_bdry, dx)`

Check bulk information conservation via Gauss's theorem. Returns a relative residual (0 = perfectly conserved).

---

## `src.multiverse.fixed_point`

Multiverse fixed-point dynamics (Pillar 5).

---

### `class MultiverseNode`

Single universe in the thermodynamic multiverse.

| Attribute | Type | Description |
|-----------|------|-------------|
| `dim` | `int` | Dimension of UEUM state vector (default 4) |
| `S` | `float` | Bulk entropy |
| `A` | `float` | Boundary area |
| `Q_top` | `float` | Topological charge |
| `X` | `ndarray (dim,)` | UEUM geodesic position |
| `Xdot` | `ndarray (dim,)` | UEUM geodesic velocity |

#### `MultiverseNode.random(dim=4, rng=None)`

Create a node with random initial state.

#### `MultiverseNode.state_vector()`

Concatenate `(S, A, Q_top, X, Xdot)` into a single vector.

---

### `class MultiverseNetwork`

Graph of holographic universes.

| Attribute | Type | Description |
|-----------|------|-------------|
| `nodes` | `list[MultiverseNode]` | Universe nodes |
| `adjacency` | `ndarray (n, n)` | Coupling weights (symmetric) |

#### `MultiverseNetwork.chain(n, coupling=0.1, rng=None)`

Create a linear chain of `n` nodes with nearest-neighbour coupling.

#### `MultiverseNetwork.fully_connected(n, coupling=0.1, rng=None)`

Create a fully connected graph of `n` nodes.

#### `MultiverseNetwork.global_state()`

Flatten all node state vectors into one array.

---

### `apply_irreversibility(node, dt, kappa=0.25)`

**I operator:** entropy growth $dS/dt = \kappa A$. Returns updated `MultiverseNode`.

### `apply_holography(node, G4=1.0)`

**H operator:** clamp entropy to holographic bound $S \leq A / 4G_4$. Returns updated `MultiverseNode`.

### `apply_topology(network, node_idx, dt)`

**T operator:** gradient-flow entropy transfer $\Delta S_i = \Delta t \sum_j w_{ij}(S_j - S_i)$. Returns updated `MultiverseNode`.

### `ueum_acceleration(node, network, node_idx, G4=1.0)`

Evaluate the RHS of the UEUM geodesic equation. Returns `ndarray (dim,)`.

---

### `fixed_point_iteration(network, max_iter=500, tol=1e-6, dt=1e-3, G4=1.0, kappa=0.25)`

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
