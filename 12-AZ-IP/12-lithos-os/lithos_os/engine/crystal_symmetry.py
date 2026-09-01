# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Crystal-system analogies for 5D KK orbifold boundary conditions."""
from __future__ import annotations

CRYSTAL_TO_ORBIFOLD = {
    'cubic': 'Z4',
    'hexagonal': 'Z6',
    'trigonal': 'Z3',
    'tetragonal': 'Z4',
    'orthorhombic': 'Z2xZ2',
    'monoclinic': 'Z2',
    'triclinic': 'Z1',
}

_KK_ANALOGS = {
    'cubic': 'Fourfold isotropy maps to a balanced Z4 compactification sector.',
    'hexagonal': 'Sixfold symmetry tracks a Z6 orbifold with dense angular closure.',
    'trigonal': 'Threefold rotational closure acts like a Z3 fixed-point quotient.',
    'tetragonal': 'Axial fourfold structure maps to an anisotropic Z4 KK boundary.',
    'orthorhombic': 'Three unequal axes behave like a product Z2xZ2 reflection sector.',
    'monoclinic': 'Single-shear geometry resembles a one-plane Z2 parity reduction.',
    'triclinic': 'No rotational simplification corresponds to a trivial Z1 boundary.',
}


def get_kk_dimension_analog(crystal_system: str) -> dict[str, str]:
    """Map a crystal system onto a 5D orbifold boundary-condition analogy."""
    key = crystal_system.strip().lower()
    if key not in CRYSTAL_TO_ORBIFOLD:
        raise KeyError(f'Unknown crystal system: {crystal_system}')
    return {
        'crystal_system': key,
        'orbifold_group': CRYSTAL_TO_ORBIFOLD[key],
        '5d_bc_analog': _KK_ANALOGS[key],
        'pillar_ref': 'P001',
    }
