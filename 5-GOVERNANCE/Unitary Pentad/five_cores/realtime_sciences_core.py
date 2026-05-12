# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/realtime_sciences_core.py
=====================================
Real-Time Sciences Core — live data ingestion, automatic model updates,
evidence synthesis, and instant query readiness.

The Real-Time Sciences Core is the epistemic layer of the Five-Cores
architecture.  It continuously ingests new data streams, updates an internal
Bayesian belief state, synthesises evidence across multiple domains, and
maintains a **readiness score** R ∈ [0, 1] that indicates how prepared the
system is to answer questions in any given domain.

JAX Acceleration
-----------------
When JAX is available (``import jax``), the Bayesian update step uses
``jax.numpy`` for vectorised belief updates across all domains simultaneously.
When JAX is unavailable, a pure-NumPy fallback is used — same API, same
numerical results (within float32/float64 precision).

Mathematical Framework
-----------------------
Each domain has a belief vector b ∈ ℝ^K (K hypotheses) with Σ b_k = 1 (prior).
On receiving observation datum d the likelihood ℓ(d | h_k) is used to compute:

    b_k ← b_k × ℓ_k / Z          (Bayesian update, Z = Σ b_k ℓ_k)

Readiness score for domain i:

    R_i = 1 − H(b_i) / log(K)

where H(b) = −Σ b_k log(b_k) is the Shannon entropy of the belief.  When
the belief is maximally uncertain (uniform), H = log(K) and R = 0.  When
the belief is perfectly concentrated on one hypothesis, H = 0 and R = 1.

Evidence Synthesis
-------------------
Cross-domain evidence synthesis uses a geometric mean of readiness scores
weighted by the φ_trust field:

    R_system = (Π_i R_i^{φ_trust})^{1/N}

This ensures that low trust suppresses the overall readiness estimate, even
if individual domains appear well-understood.

Public API
----------
DataDomain
    Domain constants.

Observation
    Dataclass: domain, likelihood_ratios, timestamp (step).

SciencesState
    Full state snapshot including per-domain readiness.

RealTimeSciencesCore
    Main engine.  Methods:
        ingest(observation) → SciencesState
        tick(observations, trust_delta) → SciencesState
        readiness(domain) → float
        system_readiness() → float
        query(domain, question) → dict
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
    "fingerprint": "(5, 7, 74)",
}

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Conditional JAX import
# ---------------------------------------------------------------------------
try:
    import jax
    import jax.numpy as jnp

    _JAX_AVAILABLE = True

    @jax.jit
    def _jax_bayesian_update(b: "jax.Array", likelihood: "jax.Array") -> "jax.Array":
        """Vectorised single-domain Bayesian update in JAX."""
        unnorm = b * likelihood
        Z = jnp.sum(unnorm)
        return jnp.where(Z > 0, unnorm / Z, b)

    @jax.jit
    def _jax_entropy(b: "jax.Array") -> "jax.Array":
        safe_b = jnp.where(b > 0, b, 1e-12)
        return -jnp.sum(b * jnp.log(safe_b))

except ImportError:
    _JAX_AVAILABLE = False

    def _jax_bayesian_update(b, likelihood):  # type: ignore[misc]
        raise RuntimeError("JAX not available")

    def _jax_entropy(b):  # type: ignore[misc]
        raise RuntimeError("JAX not available")


def _np_bayesian_update(b: np.ndarray, likelihood: np.ndarray) -> np.ndarray:
    unnorm = b * likelihood
    Z = unnorm.sum()
    return unnorm / Z if Z > 0 else b.copy()


def _np_entropy(b: np.ndarray) -> float:
    safe = np.where(b > 0, b, 1e-300)
    return float(-np.sum(b * np.log(safe)))


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

C_S: float = 12 / 37

#: Default number of hypotheses per domain.
DEFAULT_N_HYPOTHESES: int = 5

#: Minimum readiness to declare a domain "query-ready".
QUERY_READY_THRESHOLD: float = 0.60

#: Domains tracked by default.
DEFAULT_DOMAINS = [
    "ASTROPHYSICS",
    "NAVIGATION",
    "PROPULSION_PHYSICS",
    "BIOLOGY",
    "MATERIALS",
    "ATMOSPHERE",
    "QUANTUM_FIELD",
]


class DataDomain:
    ASTROPHYSICS = "ASTROPHYSICS"
    NAVIGATION = "NAVIGATION"
    PROPULSION_PHYSICS = "PROPULSION_PHYSICS"
    BIOLOGY = "BIOLOGY"
    MATERIALS = "MATERIALS"
    ATMOSPHERE = "ATMOSPHERE"
    QUANTUM_FIELD = "QUANTUM_FIELD"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Observation:
    """A single incoming data observation."""

    domain: str
    likelihood_ratios: np.ndarray   # shape (K,) — ℓ(d | h_k) for each hypothesis
    step: int = 0

    def __post_init__(self) -> None:
        lr = np.asarray(self.likelihood_ratios, dtype=float)
        lr = np.clip(lr, 1e-12, None)
        self.likelihood_ratios = lr / lr.sum()   # normalize to sum-1


@dataclass
class SciencesState:
    """Snapshot of the Real-Time Sciences Core."""

    phi_trust: float
    step_count: int
    per_domain_readiness: Dict[str, float]
    system_readiness: float
    query_ready_domains: List[str]
    jax_active: bool
    recent_ingestion_count: int


# ---------------------------------------------------------------------------
# Core Implementation
# ---------------------------------------------------------------------------

class RealTimeSciencesCore:
    """
    Real-Time Sciences Core — JAX-accelerated Bayesian evidence engine.

    Parameters
    ----------
    phi_trust : float
        Initial trust radion.
    domains : list[str] | None
        Domain labels to track.  Defaults to DEFAULT_DOMAINS.
    n_hypotheses : int
        Number of hypotheses per domain.
    use_jax : bool | None
        If True, require JAX (raise if unavailable).
        If False, force NumPy.
        If None (default), use JAX when available.
    """

    def __init__(
        self,
        phi_trust: float = 1.0,
        domains: Optional[List[str]] = None,
        n_hypotheses: int = DEFAULT_N_HYPOTHESES,
        use_jax: Optional[bool] = None,
    ) -> None:
        self._phi_trust = float(np.clip(phi_trust, 0.0, 1.0))
        self._step_count = 0
        self._n_hypotheses = n_hypotheses
        self._ingestion_count = 0

        if use_jax is True and not _JAX_AVAILABLE:
            raise ImportError("JAX requested but not installed")
        self._use_jax: bool = (use_jax is not False) and _JAX_AVAILABLE

        _domains = domains if domains is not None else list(DEFAULT_DOMAINS)

        # Uniform prior for each domain
        uniform = np.ones(n_hypotheses, dtype=float) / n_hypotheses
        self._beliefs: Dict[str, np.ndarray] = {d: uniform.copy() for d in _domains}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _update_belief(self, domain: str, likelihood: np.ndarray) -> None:
        b = self._beliefs.get(domain, np.ones(self._n_hypotheses) / self._n_hypotheses)
        k = b.shape[0]
        l = np.asarray(likelihood, dtype=float)
        if l.shape[0] != k:
            # Truncate or pad
            l_adj = np.ones(k, dtype=float) / k
            l_adj[:min(k, l.shape[0])] = l[:min(k, l.shape[0])]
            l = l_adj / l_adj.sum()

        if self._use_jax:
            import jax.numpy as jnp
            b_jax = jnp.array(b)
            l_jax = jnp.array(l)
            b_new = np.array(_jax_bayesian_update(b_jax, l_jax))
        else:
            b_new = _np_bayesian_update(b, l)
        self._beliefs[domain] = b_new

    def _readiness_from_belief(self, domain: str) -> float:
        b = self._beliefs.get(domain, np.ones(self._n_hypotheses) / self._n_hypotheses)
        k = b.shape[0]
        if k <= 1:
            return 1.0
        max_entropy = float(np.log(k))
        if self._use_jax:
            import jax.numpy as jnp
            h = float(_jax_entropy(jnp.array(b)))
        else:
            h = _np_entropy(b)
        return float(np.clip(1.0 - h / max_entropy, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_domain(self, domain: str) -> None:
        """Register a new domain with a uniform prior."""
        if domain not in self._beliefs:
            self._beliefs[domain] = (
                np.ones(self._n_hypotheses, dtype=float) / self._n_hypotheses
            )

    def ingest(self, observation: Observation) -> None:
        """
        Ingest a single observation and update the domain belief.

        Parameters
        ----------
        observation : Observation
            Must supply domain and likelihood_ratios.
        """
        if observation.domain not in self._beliefs:
            self.add_domain(observation.domain)
        self._update_belief(observation.domain, observation.likelihood_ratios)
        self._ingestion_count += 1

    def readiness(self, domain: str) -> float:
        """Return the readiness score R_i ∈ [0, 1] for a domain."""
        return self._readiness_from_belief(domain)

    def system_readiness(self) -> float:
        """
        Geometric-mean readiness across all domains, weighted by φ_trust.

        R_system = (Π_i R_i^{φ_trust})^{1/N}
        """
        scores = [self._readiness_from_belief(d) for d in self._beliefs]
        if not scores:
            return 0.0
        safe = [max(s, 1e-12) for s in scores]
        log_geo = self._phi_trust * np.mean(np.log(safe))
        return float(np.clip(np.exp(log_geo), 0.0, 1.0))

    def query(self, domain: str, question: str = "") -> Dict:
        """
        Query the system's understanding of a domain.

        Returns a dict with:
            domain, readiness, query_ready, belief (numpy array),
            dominant_hypothesis (index of argmax), confidence.
        """
        b = self._beliefs.get(domain, np.ones(self._n_hypotheses) / self._n_hypotheses)
        r = self._readiness_from_belief(domain)
        dominant = int(np.argmax(b))
        confidence = float(b[dominant])
        return {
            "domain": domain,
            "readiness": r,
            "query_ready": r >= QUERY_READY_THRESHOLD,
            "belief": b.copy(),
            "dominant_hypothesis": dominant,
            "confidence": confidence,
            "question": question,
        }

    def tick(
        self,
        observations: Optional[Sequence[Observation]] = None,
        trust_delta: float = 0.0,
    ) -> SciencesState:
        """
        Advance the Sciences Core by one step.

        Parameters
        ----------
        observations : sequence of Observation | None
            New data received this step.
        trust_delta : float
            Change in the trust radion.
        """
        self._step_count += 1
        self._phi_trust = float(np.clip(self._phi_trust + trust_delta, 0.0, 1.0))

        if observations:
            for obs in observations:
                self.ingest(obs)

        per_domain = {d: self._readiness_from_belief(d) for d in self._beliefs}
        query_ready = [d for d, r in per_domain.items() if r >= QUERY_READY_THRESHOLD]

        return SciencesState(
            phi_trust=self._phi_trust,
            step_count=self._step_count,
            per_domain_readiness=per_domain,
            system_readiness=self.system_readiness(),
            query_ready_domains=sorted(query_ready),
            jax_active=self._use_jax,
            recent_ingestion_count=self._ingestion_count,
        )

    @classmethod
    def default(cls) -> "RealTimeSciencesCore":
        """Factory: canonical sciences core with all default domains."""
        return cls()
