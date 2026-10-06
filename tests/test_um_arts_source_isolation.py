# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Regression execution must not rewrite committed training evidence."""

from pathlib import Path
from types import SimpleNamespace

from tests import conftest


def test_training_isolation_copies_seed_artifacts_and_restores_paths():
    from ox_navigator.engine import merlin_training_execution as training

    names = ["LANE_E_PROFILE_ARTIFACT_PATH", "PERFORMANCE_GATE_HISTORY_PATH"]
    originals = {name: getattr(training, name) for name in names}
    original_bytes = {name: path.read_bytes() for name, path in originals.items()}
    cleanups = []
    session = SimpleNamespace(config=SimpleNamespace(add_cleanup=cleanups.append))
    try:
        conftest.pytest_sessionstart(session)
        for name in names:
            isolated = getattr(training, name)
            assert isolated != originals[name]
            assert isolated.read_bytes() == original_bytes[name]
            assert not isolated.is_relative_to(Path(conftest._REPO_ROOT))
            isolated.write_text('{"test-only": true}')
            assert originals[name].read_bytes() == original_bytes[name]
        assert training._LANE_E_RUNTIME_PROFILE_CACHE is None
    finally:
        for cleanup in reversed(cleanups):
            cleanup()
    assert all(getattr(training, name) == originals[name] for name in names)
    assert not isolated.exists()
