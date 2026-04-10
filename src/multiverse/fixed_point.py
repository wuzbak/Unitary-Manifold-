"""
src/multiverse/fixed_point.py
=============================
Pillar 5 — Multiverse Dynamics and the Fixed-Point Theorem (FTUM).

Models a network of holographic universes (nodes) interacting exclusively
through inter-manifold information flow (edges), and iterates the combined
operator U = I + H + T until a fixed point is reached.

Theory summary (Chapters 56–62)
--------------------------------
UEUM geodesic equation:
    Ẍ^a + Γ^a_{bc} Ẋ^b Ẋ^c = G_U^{ab} ∇_b S_U
                               + δ/δX^a (Σ A_∂/4G + Q_top)

Operator decomposition:
    I  — Irreversibility operator  (entropy-weighted metric update)
    H  — Holography operator       (boundary entropy injection)
    T  — Topology operator         (inter-manifold information transfer)
    U  = I + H + T

Fixed-Point Theorem (FTUM):
    There exists a state Ψ* such that  U Ψ* = Ψ*  (fixed point).
    The iteration  Ψ^{n+1} = U(Ψ^n)  converges to Ψ*.

Public API
----------
MultiverseNode
    Single universe: holds entropy S, boundary area A, topology charge Q,
    and the UEUM state vector X.

MultiverseNetwork
    Graph of MultiverseNodes with weighted edges (information coupling).

apply_irreversibility(node, dt)
    I operator: update node entropy via dS/dt = κ A.

apply_holography(node, G4)
    H operator: inject boundary entropy S_∂ = A / 4G into node.

apply_topology(network, node_idx, dt)
    T operator: transfer information between connected nodes.

ueum_acceleration(node, network, node_idx)
    Evaluate right-hand side of the UEUM geodesic equation.

fixed_point_iteration(network, max_iter, tol, dt, G4)
    Iterate U = I + H + T until ||Ψ^{n+1} − Ψ^n|| < tol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# MultiverseNode
# ---------------------------------------------------------------------------

@dataclass
class MultiverseNode:
    """Single universe in the thermodynamic multiverse.

    Parameters
    ----------
    dim   : int   — dimension of the UEUM state vector X (default 4)
    S     : float — bulk entropy
    A     : float — boundary area
    Q_top : float — topological charge
    X     : ndarray, shape (dim,) — UEUM geodesic position
    Xdot  : ndarray, shape (dim,) — UEUM geodesic velocity
    """

    dim: int = 4
    S: float = 1.0
    A: float = 1.0
    Q_top: float = 0.0
    X: np.ndarray = field(default_factory=lambda: np.zeros(4))
    Xdot: np.ndarray = field(default_factory=lambda: np.zeros(4))

    # ------------------------------------------------------------------
    @classmethod
    def random(cls, dim: int = 4,
               rng: Optional[np.random.Generator] = None) -> "MultiverseNode":
        """Create a node with random initial state."""
        if rng is None:
            rng = np.random.default_rng()
        return cls(
            dim=dim,
            S=float(rng.exponential(1.0)),
            A=float(rng.exponential(1.0)),
            Q_top=float(rng.standard_normal()),
            X=rng.standard_normal(dim),
            Xdot=1e-2 * rng.standard_normal(dim),
        )

    def state_vector(self) -> np.ndarray:
        """Concatenate (S, A, Q_top, X, Xdot) into a single vector."""
        return np.concatenate([[self.S, self.A, self.Q_top], self.X, self.Xdot])

    def norm(self) -> float:
        return float(np.linalg.norm(self.state_vector()))


# ---------------------------------------------------------------------------
# MultiverseNetwork
# ---------------------------------------------------------------------------

@dataclass
class MultiverseNetwork:
    """Graph of holographic universes with information-flow edges.

    Parameters
    ----------
    nodes         : list of MultiverseNode
    adjacency     : ndarray, shape (n_nodes, n_nodes) — coupling weights
    """

    nodes: List[MultiverseNode]
    adjacency: np.ndarray   # shape (n, n), symmetric, zero diagonal

    # ------------------------------------------------------------------
    @classmethod
    def chain(cls, n: int, coupling: float = 0.1,
              rng: Optional[np.random.Generator] = None) -> "MultiverseNetwork":
        """Create a chain network of n nodes."""
        if rng is None:
            rng = np.random.default_rng(42)
        nodes = [MultiverseNode.random(rng=rng) for _ in range(n)]
        adj = np.zeros((n, n))
        for i in range(n - 1):
            adj[i, i + 1] = adj[i + 1, i] = coupling
        return cls(nodes=nodes, adjacency=adj)

    @classmethod
    def fully_connected(cls, n: int, coupling: float = 0.1,
                        rng: Optional[np.random.Generator] = None
                        ) -> "MultiverseNetwork":
        """Create a fully connected network of n nodes."""
        if rng is None:
            rng = np.random.default_rng(42)
        nodes = [MultiverseNode.random(rng=rng) for _ in range(n)]
        adj = coupling * (np.ones((n, n)) - np.eye(n))
        return cls(nodes=nodes, adjacency=adj)

    def n_nodes(self) -> int:
        return len(self.nodes)

    def global_state(self) -> np.ndarray:
        """Flatten all node state vectors into one array."""
        return np.concatenate([nd.state_vector() for nd in self.nodes])


# ---------------------------------------------------------------------------
# Operator I — Irreversibility
# ---------------------------------------------------------------------------

def apply_irreversibility(node: MultiverseNode, dt: float,
                          kappa: float = 0.25,
                          G4: float = 1.0) -> MultiverseNode:
    """I operator: entropy relaxation toward holographic bound (second law).

    dS/dt = κ (A/4G − S)   — contraction toward S* = A/4G

    Parameters
    ----------
    node  : MultiverseNode
    dt    : float
    kappa : surface gravity coefficient (default 0.25)
    G4    : Newton's constant (default 1 in Planck units)

    Returns
    -------
    MultiverseNode with updated S
    """
    dS = kappa * (node.A / (4.0 * G4) - node.S) * dt
    return MultiverseNode(
        dim=node.dim, S=node.S + dS, A=node.A,
        Q_top=node.Q_top, X=node.X.copy(), Xdot=node.Xdot.copy()
    )


# ---------------------------------------------------------------------------
# Operator H — Holography
# ---------------------------------------------------------------------------

def apply_holography(node: MultiverseNode,
                     G4: float = 1.0) -> MultiverseNode:
    """H operator: set boundary entropy S_∂ = A / 4G and update node.

    The holographic principle requires S ≤ A / 4G.  This operator
    projects the node entropy onto the holographic bound.

    Parameters
    ----------
    node : MultiverseNode
    G4   : Newton's constant

    Returns
    -------
    MultiverseNode with S clamped to A / 4G
    """
    S_holo = node.A / (4.0 * G4)
    S_new = min(node.S, S_holo)          # entropy cannot exceed holographic bound
    return MultiverseNode(
        dim=node.dim, S=S_new, A=node.A,
        Q_top=node.Q_top, X=node.X.copy(), Xdot=node.Xdot.copy()
    )


# ---------------------------------------------------------------------------
# Operator T — Topology / inter-manifold transfer
# ---------------------------------------------------------------------------

def apply_topology(network: MultiverseNetwork,
                   node_idx: int,
                   dt: float) -> MultiverseNode:
    """T operator: transfer information entropy from connected nodes.

    ΔS_i = dt * Σ_j w_{ij} (S_j − S_i)   (gradient flow on graph)

    Parameters
    ----------
    network  : MultiverseNetwork
    node_idx : int — index of node to update
    dt       : float

    Returns
    -------
    MultiverseNode (updated node i)
    """
    node = network.nodes[node_idx]
    dS = 0.0
    for j, other in enumerate(network.nodes):
        w = network.adjacency[node_idx, j]
        dS += w * (other.S - node.S)
    S_new = node.S + dt * dS
    return MultiverseNode(
        dim=node.dim, S=S_new, A=node.A,
        Q_top=node.Q_top, X=node.X.copy(), Xdot=node.Xdot.copy()
    )


# ---------------------------------------------------------------------------
# UEUM geodesic RHS
# ---------------------------------------------------------------------------

def ueum_acceleration(node: MultiverseNode,
                      network: MultiverseNetwork,
                      node_idx: int,
                      G4: float = 1.0) -> np.ndarray:
    """Evaluate the RHS of the UEUM geodesic equation.

    Ẍ^a = −Γ^a_{bc} Ẋ^b Ẋ^c
           + G_U^{ab} ∇_b S_U
           + δ/δX^a (Σ A_∂/4G + Q_top)

    In the reduced (flat G_U = δ^{ab}) approximation:
        Ẍ^a = −|Ẋ|² X^a / (|X|²+ε)   (centripetal)
               + ∇_a S_U               (entropic force)
               + ∂_a (Σ A_j/4G + Q_top)

    Parameters
    ----------
    node      : MultiverseNode — target node
    network   : MultiverseNetwork
    node_idx  : int
    G4        : float

    Returns
    -------
    Xddot : ndarray, shape (dim,)
    """
    X, Xdot = node.X, node.Xdot
    dim = node.dim

    X_norm2 = np.dot(X, X) + 1e-12
    speed2 = np.dot(Xdot, Xdot)

    # Geodesic (centripetal) term  −Γ Ẋ Ẋ  (flat-space proxy)
    geodesic = -speed2 * X / X_norm2

    # Entropic force  G_U^{ab} ∇_b S_U ≈ ∇S in direction of X
    S_U = node.S
    entropic = S_U * X / (X_norm2)

    # Holographic + topological variation — Hooke-law restoring force on all axes
    A_sum = sum(nd.A for nd in network.nodes)
    C = A_sum / (4.0 * G4) + node.Q_top
    holo_force = -C * X

    return geodesic + entropic + holo_force


# ---------------------------------------------------------------------------
# Apply U = I + H + T (one full operator sweep)
# ---------------------------------------------------------------------------

def _apply_U(network: MultiverseNetwork, dt: float,
             G4: float = 1.0,
             kappa: float = 0.25,
             gamma: float = 5.0) -> MultiverseNetwork:
    """Apply the combined operator U = I + H + T and advance UEUM geodesic."""
    new_nodes: List[MultiverseNode] = []
    for i, node in enumerate(network.nodes):
        # I — irreversibility
        node = apply_irreversibility(node, dt, kappa, G4)
        # T — topology: compute flow delta from old network states (Jacobi),
        #     then accumulate on top of the post-I entropy
        dS_topo = dt * sum(
            network.adjacency[i, j] * (network.nodes[j].S - network.nodes[i].S)
            for j in range(len(network.nodes))
        )
        node = MultiverseNode(
            dim=node.dim, S=node.S + dS_topo, A=node.A,
            Q_top=node.Q_top, X=node.X.copy(), Xdot=node.Xdot.copy()
        )
        # H — holography (project onto bound)
        node = apply_holography(node, G4)

        # UEUM geodesic integration — semi-implicit friction damping
        Xddot = ueum_acceleration(node, network, i, G4)
        Xdot_new = (node.Xdot + dt * Xddot) / (1.0 + dt * gamma)
        X_new = node.X + dt * Xdot_new

        new_nodes.append(MultiverseNode(
            dim=node.dim, S=node.S, A=node.A,
            Q_top=node.Q_top, X=X_new, Xdot=Xdot_new
        ))
    return MultiverseNetwork(nodes=new_nodes, adjacency=network.adjacency.copy())


# ---------------------------------------------------------------------------
# Fixed-point iteration
# ---------------------------------------------------------------------------

def fixed_point_iteration(
    network: MultiverseNetwork,
    max_iter: int = 500,
    tol: float = 1e-6,
    dt: float = 0.2,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
) -> Tuple[MultiverseNetwork, List[float], bool]:
    """Iterate U = I + H + T until the holographic defect ‖A/4G − S‖ < tol.

    Implements the Fixed-Point Theorem of the Unitary Manifold (FTUM):
    reality is a fixed point of the combined operator U acting on the
    multiverse state.  Convergence is measured by the defect

        defect = ‖A_i/4G − S_i‖  (should vanish at the fixed point)

    rather than the step-size ‖Ψ^{n+1} − Ψ^n‖, which can plateau even
    when the system is near the fixed point.

    Parameters
    ----------
    network  : MultiverseNetwork — initial multiverse state
    max_iter : int   — maximum iterations (default 500)
    tol      : float — convergence tolerance on the defect (default 1e-6)
    dt       : float — pseudo-timestep per iteration (default 0.2)
    G4       : float — Newton's constant
    kappa    : float — surface gravity coefficient
    gamma    : float — friction coefficient for UEUM geodesic (default 5.0)

    Returns
    -------
    (converged_network, residual_history, converged_flag)
    """
    residuals: List[float] = []
    converged = False

    for iteration in range(max_iter):
        network = _apply_U(network, dt, G4, kappa, gamma)

        # Defect: how far each node's entropy is from the holographic bound
        defect = float(np.linalg.norm(
            [node.A / (4.0 * G4) - node.S for node in network.nodes]
        ))
        residuals.append(defect)

        if defect < tol:
            converged = True
            break

    return network, residuals, converged
