# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

sp = pytest.importorskip("sympy")

from src.core.pillar1137_planar_radion_kasner_relations import (
    NEXT_PILLAR_SLOT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    planar_radion_kasner_relations_certificate,
)
from src.physics.planar_radion.derivation import (
    frw_kasner_parameters,
    frw_kasner_relation_residuals,
)


def test_kasner_relations_are_exact_identities():
    assert all(value == 0 for value in frw_kasner_relation_residuals().values())


@pytest.mark.parametrize("a, p", [(1, 0), (-2, 3), (sp.Rational(1, 3), 5)])
def test_kasner_relations_hold_for_concrete_data_of_either_sign(a, p):
    d = frw_kasner_parameters(a, p)
    pl, pt, s = (d["longitudinal_kasner_exponent"], d["transverse_kasner_exponent"],
                 d["scalar_kasner_amplitude"])
    assert pl + 2 * pt == 1
    assert pl**2 + 2 * pt**2 + sp.Rational(3, 2) * s**2 == 1
    assert d["proper_time_power"] > 0


def test_pillar_certificate_is_scoped_and_fails_closed():
    packet = planar_radion_kasner_relations_certificate()
    assert (PILLAR_NUMBER, NEXT_PILLAR_SLOT) == (1137, 1138)
    assert packet["verified"] is True
    assert packet["status"] == PILLAR_STATUS
    assert packet["framework_closure_earned"] is False
    assert packet["does_not_establish"]
