"""
tests/conftest.py
=================
Shared pytest fixtures for the Unitary Manifold test suite.
"""

import numpy as np
import pytest

from src.core.evolution import FieldState
from src.holography.boundary import BoundaryState
from src.multiverse.fixed_point import MultiverseNetwork


# ---------------------------------------------------------------------------
# Reproducible RNGs
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def rng():
    """Session-scoped NumPy random generator for reproducibility."""
    return np.random.default_rng(0)


# ---------------------------------------------------------------------------
# Minimal field states
# ---------------------------------------------------------------------------

@pytest.fixture
def flat_state_small():
    """Flat Minkowski FieldState on a 16-point grid — fast for unit tests."""
    return FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(1))


@pytest.fixture
def flat_state_medium():
    """Flat Minkowski FieldState on a 32-point grid — moderate accuracy."""
    return FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(2))


# ---------------------------------------------------------------------------
# Boundary state
# ---------------------------------------------------------------------------

@pytest.fixture
def boundary_state_small(flat_state_small):
    """BoundaryState derived from the small flat bulk."""
    s = flat_state_small
    return BoundaryState.from_bulk(s.g, s.B, s.phi, s.dx)


# ---------------------------------------------------------------------------
# Multiverse networks
# ---------------------------------------------------------------------------

@pytest.fixture
def chain_network():
    """5-node chain network with coupling=0.05."""
    return MultiverseNetwork.chain(n=5, coupling=0.05, rng=np.random.default_rng(42))


@pytest.fixture
def full_network():
    """4-node fully-connected network with coupling=0.1."""
    return MultiverseNetwork.fully_connected(n=4, coupling=0.1,
                                             rng=np.random.default_rng(42))
