# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lithos_os.engine.crystal_symmetry import CRYSTAL_TO_ORBIFOLD, get_kk_dimension_analog
from lithos_os.engine.open_mineral_data import (
    MINERAL_DATABASE,
    RRUFF_BASE_URL,
    get_orbifold_bc,
    identify_mineral,
)


def test_rruff_constant():
    assert 'rruff.info' in RRUFF_BASE_URL


def test_database_has_30_entries():
    assert len(MINERAL_DATABASE) == 30


def test_database_entry_fields():
    quartz = MINERAL_DATABASE['quartz']
    assert set(quartz) == {
        'name', 'formula', 'crystal_system', 'hardness', 'specific_gravity',
        'color_range', 'raman_peaks_cm_inv', 'orbifold_symmetry_group'
    }


def test_all_minerals_have_peaks():
    assert all(entry['raman_peaks_cm_inv'] for entry in MINERAL_DATABASE.values())


def test_all_minerals_have_orbifold_groups():
    assert all(entry['orbifold_symmetry_group'] for entry in MINERAL_DATABASE.values())


def test_orbifold_groups_match_crystal_mapping():
    for mineral in MINERAL_DATABASE.values():
        assert mineral['orbifold_symmetry_group'] == CRYSTAL_TO_ORBIFOLD[mineral['crystal_system']]


def test_identify_quartz():
    result = identify_mineral([129.0, 208.0, 462.0], tolerance=15.0)
    assert result['name'] == 'Quartz'
    assert result['matched_peaks'] == 3


def test_identify_diamond():
    result = identify_mineral([1331.0], tolerance=10.0)
    assert result['name'] == 'Diamond'
    assert result['within_tolerance'] is True


def test_identify_calcite():
    result = identify_mineral([157.0, 282.0, 1087.0], tolerance=10.0)
    assert result['name'] == 'Calcite'


def test_identify_graphite():
    result = identify_mineral([1581.0], tolerance=8.0)
    assert result['name'] == 'Graphite'


def test_identify_with_loose_tolerance_still_returns_best_match():
    result = identify_mineral([440.0, 975.0], tolerance=60.0)
    assert result['name'] in {'Zircon', 'Barite', 'Apatite'}


def test_identify_empty_input_rejected():
    with pytest.raises(ValueError):
        identify_mineral([])


def test_identify_nonpositive_tolerance_rejected():
    with pytest.raises(ValueError):
        identify_mineral([100.0], tolerance=0.0)


def test_identify_returns_reference_url():
    result = identify_mineral([321.0], tolerance=5.0)
    assert result['reference_url'] == RRUFF_BASE_URL


def test_identify_returns_mean_distance():
    result = identify_mineral([322.0], tolerance=5.0)
    assert result['mean_peak_distance'] >= 0.0


def test_get_orbifold_bc_quartz():
    result = get_orbifold_bc('Quartz')
    assert result['mineral'] == 'Quartz'
    assert result['orbifold_group'] == 'Z3'
    assert result['pillar_ref'] == 'P001'


def test_get_orbifold_bc_case_insensitive():
    result = get_orbifold_bc('diamond')
    assert result['crystal_system'] == 'cubic'
    assert result['orbifold_group'] == 'Z4'


def test_get_orbifold_bc_unknown_rejected():
    with pytest.raises(KeyError):
        get_orbifold_bc('Unknownite')


@pytest.mark.parametrize(
    ('crystal_system', 'expected'),
    [
        ('cubic', 'Z4'),
        ('hexagonal', 'Z6'),
        ('trigonal', 'Z3'),
        ('tetragonal', 'Z4'),
        ('orthorhombic', 'Z2xZ2'),
        ('monoclinic', 'Z2'),
        ('triclinic', 'Z1'),
    ],
)
def test_crystal_to_orbifold_mapping(crystal_system, expected):
    assert CRYSTAL_TO_ORBIFOLD[crystal_system] == expected


def test_get_kk_dimension_analog_quartz_system():
    analog = get_kk_dimension_analog('trigonal')
    assert analog['orbifold_group'] == 'Z3'
    assert 'Z3' in analog['5d_bc_analog']


def test_get_kk_dimension_analog_normalizes_case():
    analog = get_kk_dimension_analog(' Hexagonal ')
    assert analog['crystal_system'] == 'hexagonal'


def test_get_kk_dimension_analog_unknown_rejected():
    with pytest.raises(KeyError):
        get_kk_dimension_analog('icosahedral')


def test_hardness_values_are_positive():
    assert all(entry['hardness'] > 0 for entry in MINERAL_DATABASE.values())
