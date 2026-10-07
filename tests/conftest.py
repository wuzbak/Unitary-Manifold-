"""
tests/conftest.py
=================
Shared pytest fixtures for the Unitary Manifold test suite.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Ensure moved top-level packages remain importable after the v9.28
# repository reorganisation (realworld, brain, botanical, etc. now live under
# 4-IMPLICATIONS/).  Insert the directory on sys.path only if it isn't there
# already, so this is safe to run multiple times.
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PENTAD_DIR = os.path.join(_REPO_ROOT, "5-GOVERNANCE", "Unitary Pentad")
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)
_IMPLICATIONS_DIR = os.path.join(_REPO_ROOT, "4-IMPLICATIONS")
if _IMPLICATIONS_DIR not in sys.path:
    sys.path.insert(0, _IMPLICATIONS_DIR)
_SAFETY_DIR = os.path.join(_REPO_ROOT, "8-SAFETY")
if _SAFETY_DIR not in sys.path:
    sys.path.insert(0, _SAFETY_DIR)
# v3 — geo-monitor package (wm_feeds, etc.)
_GEO_MONITOR_DIR = os.path.join(_REPO_ROOT, "12-AZ-IP", "21-geo-monitor")
if _GEO_MONITOR_DIR not in sys.path:
    sys.path.insert(0, _GEO_MONITOR_DIR)

from src.core.evolution import FieldState
from src.holography.boundary import BoundaryState
from src.multiverse.fixed_point import MultiverseNetwork


def pytest_sessionstart(session):
    """Isolate runtime writes before collection can evaluate pillar proxies."""
    from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded

    ensure_merlin_package_loaded(Path(_REPO_ROOT) / "12-AZ-IP" / "20-psicat-navigator")
    from ox_navigator.engine import merlin_training_execution

    directory = tempfile.TemporaryDirectory(prefix="um-regression-training-")
    patches = pytest.MonkeyPatch()
    session.config.add_cleanup(directory.cleanup)
    session.config.add_cleanup(patches.undo)
    for name in ["LANE_E_PROFILE_ARTIFACT_PATH", "PERFORMANCE_GATE_HISTORY_PATH"]:
        original = getattr(merlin_training_execution, name)
        isolated = Path(directory.name) / original.name
        if original.is_file():
            shutil.copy2(original, isolated)
        patches.setattr(merlin_training_execution, name, isolated)
    patches.setattr(merlin_training_execution, "_LANE_E_RUNTIME_PROFILE_CACHE", None)
    from lodge import rag_bridge

    original = rag_bridge._HISTORY_FILE
    isolated = Path(directory.name) / "lodge" / original.name
    isolated.parent.mkdir()
    if original.is_file():
        shutil.copy2(original, isolated)
    patches.setattr(rag_bridge, "_HISTORY_FILE", isolated)


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
