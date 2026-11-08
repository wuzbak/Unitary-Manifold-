# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import numpy as np
import pytest

pytest.importorskip("sympy")

from src.core.pillar1136_planar_radion_scalar_energy_balance import (
    NEXT_PILLAR_SLOT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    planar_radion_scalar_energy_balance_certificate,
)
from src.physics.planar_radion.derivation import scalar_energy_balance_residual
from src.physics.planar_radion.evolution import (
    PlanarRadionState,
    planar_scalar_energy_budget,
)


def test_local_energy_balance_is_an_exact_reduced_equation_identity():
    residual, _ = scalar_energy_balance_residual()
    assert residual == 0


def test_energy_budget_matches_homogeneous_exact_solution():
    n, t, charge = 32, 0.7, 0.4
    dx = 2.0 * np.pi / n
    state = PlanarRadionState(
        t=t,
        dx=dx,
        r=np.full(n, np.sqrt(t)),
        sigma=np.zeros(n),
        psi=np.full(n, charge * np.log(t)),
        r_t=np.full(n, 1.0 / (2.0 * np.sqrt(t))),
        sigma_t=np.zeros(n),
        psi_t=np.full(n, charge / t),
    )

    budget = planar_scalar_energy_budget(state)
    assert budget["energy"] == pytest.approx(np.pi * charge**2 / t)
    assert budget["radion_work_rate"] == pytest.approx(-np.pi * charge**2 / t**2)


def test_energy_budget_rejects_nonfinite_arithmetic():
    n = 8
    state = PlanarRadionState(
        t=0.7,
        dx=0.1,
        r=np.full(n, 1e150),
        sigma=np.zeros(n),
        psi=np.zeros(n),
        r_t=np.zeros(n),
        sigma_t=np.zeros(n),
        psi_t=np.full(n, 1e100),
    )
    with pytest.raises(ValueError, match="finite physical domain"):
        planar_scalar_energy_budget(state)


def test_pillar_certificate_is_scoped_and_fails_closed():
    packet = planar_radion_scalar_energy_balance_certificate()
    assert PILLAR_NUMBER == 1136
    assert NEXT_PILLAR_SLOT == 1137
    assert packet["verified"] is True
    assert packet["status"] == PILLAR_STATUS
    assert packet["local_balance_residual"] == "0"
    assert packet["framework_closure_earned"] is False
    assert any("not a conservation law" in item for item in packet["does_not_establish"])
