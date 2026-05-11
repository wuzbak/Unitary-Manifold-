# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import pytest

from src.quantum.fermi_hubbard import build_fermi_hubbard_1d


def test_model_basic_properties() -> None:
    model = build_fermi_hubbard_1d(n_sites=4, hopping_t=1.0, interaction_u=2.0)
    assert model.n_modes == 8
    assert model.hopping_edges() == [(0, 1), (1, 2), (2, 3)]


def test_periodic_edges_include_wrap() -> None:
    model = build_fermi_hubbard_1d(n_sites=4, hopping_t=1.0, interaction_u=2.0, periodic=True)
    assert (3, 0) in model.hopping_edges()


def test_fermionic_terms_include_hopping_interaction_and_mu() -> None:
    model = build_fermi_hubbard_1d(
        n_sites=2,
        hopping_t=1.0,
        interaction_u=4.0,
        chemical_potential=0.5,
    )
    terms = model.fermionic_terms()
    # 1 edge x 2 spins x (forward+backward)=4 hopping terms
    # + 2 interaction terms
    # + 4 chemical-potential number terms
    assert len(terms) == 10


def test_invalid_site_count_raises() -> None:
    with pytest.raises(ValueError):
        build_fermi_hubbard_1d(n_sites=1, hopping_t=1.0, interaction_u=1.0)
