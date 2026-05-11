# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import numpy as np
import pytest

from src.quantum.benchmarks import (
    TDVPReference,
    build_scaling_curve,
    run_observable_benchmark,
    tdvp_parity_report,
)
from src.quantum.fermi_hubbard import build_fermi_hubbard_1d


def test_tdvp_parity_report_zero_error_for_identical_series() -> None:
    model = build_fermi_hubbard_1d(n_sites=2, hopping_t=1.0, interaction_u=2.0)
    res = run_observable_benchmark(model, total_time=0.1, trotter_steps=2)

    charge = np.array([s.charge_density for s in res.observable_history])
    spin = np.array([s.spin_density for s in res.observable_history])
    ref = TDVPReference(times=res.times, charge_density_series=charge, spin_density_series=spin)

    rep = tdvp_parity_report(res, ref)
    assert rep.charge_rmse == pytest.approx(0.0)
    assert rep.spin_rmse == pytest.approx(0.0)


@pytest.mark.slow
def test_scaling_curve_has_points_and_slope() -> None:
    models = [
        build_fermi_hubbard_1d(n_sites=2, hopping_t=1.0, interaction_u=2.0),
        build_fermi_hubbard_1d(n_sites=3, hopping_t=1.0, interaction_u=2.0),
    ]
    curve = build_scaling_curve(models, total_time=0.1, trotter_steps=2)
    assert len(curve.points) == 2
    assert np.isfinite(curve.loglog_slope)
