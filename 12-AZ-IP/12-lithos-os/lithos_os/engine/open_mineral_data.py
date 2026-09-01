# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Open mineral reference data and Raman matching helpers."""
from __future__ import annotations

from lithos_os.engine.crystal_symmetry import CRYSTAL_TO_ORBIFOLD, get_kk_dimension_analog

RRUFF_BASE_URL = 'https://rruff.info/R040031/download?type=Raman'

_MINERALS = [
    ('Quartz', 'SiO2', 'trigonal', 7.0, 2.65, 'colorless-white', [128.0, 206.0, 464.0]),
    ('Calcite', 'CaCO3', 'trigonal', 3.0, 2.71, 'white-colorless', [156.0, 281.0, 712.0, 1086.0]),
    ('Dolomite', 'CaMg(CO3)2', 'trigonal', 3.5, 2.85, 'white-pink-gray', [174.0, 300.0, 724.0, 1097.0]),
    ('Gypsum', 'CaSO4·2H2O', 'monoclinic', 2.0, 2.31, 'white-gray', [414.0, 494.0, 1008.0, 1134.0]),
    ('Halite', 'NaCl', 'cubic', 2.5, 2.17, 'colorless-white', [178.0, 260.0]),
    ('Fluorite', 'CaF2', 'cubic', 4.0, 3.18, 'purple-green-colorless', [321.0]),
    ('Pyrite', 'FeS2', 'cubic', 6.5, 5.02, 'brassy-yellow', [343.0, 379.0, 430.0]),
    ('Hematite', 'Fe2O3', 'trigonal', 5.5, 5.26, 'red-black', [225.0, 247.0, 293.0, 412.0, 613.0]),
    ('Magnetite', 'Fe3O4', 'cubic', 6.0, 5.18, 'black', [193.0, 306.0, 538.0, 668.0]),
    ('Feldspar', 'KAlSi3O8-NaAlSi3O8-CaAl2Si2O8', 'triclinic', 6.0, 2.56, 'white-pink-gray', [290.0, 476.0, 512.0]),
    ('Muscovite', 'KAl2(AlSi3O10)(OH)2', 'monoclinic', 2.5, 2.83, 'colorless-silvery', [188.0, 265.0, 410.0, 702.0]),
    ('Biotite', 'K(Mg,Fe)3AlSi3O10(F,OH)2', 'monoclinic', 3.0, 3.10, 'black-brown', [190.0, 279.0, 675.0]),
    ('Olivine', '(Mg,Fe)2SiO4', 'orthorhombic', 6.5, 3.32, 'olive-green', [304.0, 605.0, 823.0, 856.0]),
    ('Pyroxene', '(Mg,Fe,Ca)SiO3', 'monoclinic', 5.5, 3.40, 'green-black-brown', [326.0, 665.0, 1010.0]),
    ('Amphibole', 'Ca2(Mg,Fe)5Si8O22(OH)2', 'monoclinic', 5.5, 3.20, 'green-black', [224.0, 665.0, 1031.0]),
    ('Kaolinite', 'Al2Si2O5(OH)4', 'triclinic', 2.5, 2.60, 'white-cream', [143.0, 271.0, 367.0, 912.0]),
    ('Illite', 'K0.65Al2.0[Al0.65Si3.35O10](OH)2', 'monoclinic', 1.5, 2.80, 'gray-white', [195.0, 267.0, 708.0]),
    ('Montmorillonite', '(Na,Ca)0.33(Al,Mg)2Si4O10(OH)2·nH2O', 'monoclinic', 1.5, 2.35, 'white-cream', [245.0, 467.0, 1045.0]),
    ('Talc', 'Mg3Si4O10(OH)2', 'triclinic', 1.0, 2.75, 'white-green', [196.0, 367.0, 680.0]),
    ('Graphite', 'C', 'hexagonal', 1.5, 2.23, 'gray-black', [1580.0]),
    ('Diamond', 'C', 'cubic', 10.0, 3.51, 'colorless-yellow', [1332.0]),
    ('Corundum', 'Al2O3', 'trigonal', 9.0, 4.02, 'colorless-red-blue', [378.0, 418.0, 430.0, 578.0, 751.0]),
    ('Beryl', 'Be3Al2Si6O18', 'hexagonal', 7.5, 2.76, 'green-blue-colorless', [320.0, 398.0, 686.0, 1068.0]),
    ('Topaz', 'Al2SiO4(F,OH)2', 'orthorhombic', 8.0, 3.53, 'colorless-blue-yellow', [265.0, 857.0, 929.0]),
    ('Apatite', 'Ca5(PO4)3(F,Cl,OH)', 'hexagonal', 5.0, 3.20, 'green-blue-brown', [430.0, 590.0, 962.0, 1047.0]),
    ('Zircon', 'ZrSiO4', 'tetragonal', 7.5, 4.65, 'brown-red-colorless', [356.0, 438.0, 974.0, 1008.0]),
    ('Tourmaline', 'Na(Mg,Fe,Li,Al)3Al6(BO3)3Si6O18(OH)4', 'trigonal', 7.5, 3.10, 'black-green-pink', [227.0, 362.0, 639.0, 1252.0]),
    ('Rutile', 'TiO2', 'tetragonal', 6.5, 4.25, 'red-brown-black', [143.0, 447.0, 612.0]),
    ('Anatase', 'TiO2', 'tetragonal', 5.5, 3.89, 'blue-brown-black', [144.0, 197.0, 399.0, 513.0, 639.0]),
    ('Barite', 'BaSO4', 'orthorhombic', 3.5, 4.48, 'white-yellow', [187.0, 461.0, 617.0, 988.0]),
]

MINERAL_DATABASE = {
    name.lower(): {
        'name': name,
        'formula': formula,
        'crystal_system': crystal_system,
        'hardness': hardness,
        'specific_gravity': specific_gravity,
        'color_range': color_range,
        'raman_peaks_cm_inv': peaks,
        'orbifold_symmetry_group': CRYSTAL_TO_ORBIFOLD[crystal_system],
    }
    for name, formula, crystal_system, hardness, specific_gravity, color_range, peaks in _MINERALS
}


def identify_mineral(raman_peaks: list[float], tolerance: float = 50.0) -> dict[str, object]:
    """Return the best Raman-pattern match from the in-repo mineral database."""
    if not raman_peaks:
        raise ValueError('raman_peaks must not be empty')
    if tolerance <= 0:
        raise ValueError('tolerance must be positive')
    observed = [float(peak) for peak in raman_peaks]
    best_name = None
    best_score = None
    best_matches = 0
    best_distance = float('inf')
    for name, mineral in MINERAL_DATABASE.items():
        reference = mineral['raman_peaks_cm_inv']
        distances = [min(abs(obs - ref) for ref in reference) for obs in observed]
        matches = sum(distance <= tolerance for distance in distances)
        mean_distance = sum(distances) / len(distances)
        score = (matches, -mean_distance, -abs(len(reference) - len(observed)))
        if best_score is None or score > best_score:
            best_score = score
            best_name = name
            best_matches = matches
            best_distance = mean_distance
    assert best_name is not None
    result = dict(MINERAL_DATABASE[best_name])
    result.update({
        'matched_peaks': best_matches,
        'mean_peak_distance': round(best_distance, 3),
        'within_tolerance': best_matches > 0,
        'reference_url': RRUFF_BASE_URL,
    })
    return result


def get_orbifold_bc(mineral_name: str) -> dict[str, str]:
    """Return the orbifold boundary-condition analogy for a named mineral."""
    key = mineral_name.strip().lower()
    if key not in MINERAL_DATABASE:
        raise KeyError(f'Unknown mineral: {mineral_name}')
    mineral = MINERAL_DATABASE[key]
    analog = get_kk_dimension_analog(mineral['crystal_system'])
    return {
        'mineral': mineral['name'],
        'crystal_system': mineral['crystal_system'],
        'orbifold_group': mineral['orbifold_symmetry_group'],
        '5d_bc_analog': analog['5d_bc_analog'],
        'pillar_ref': 'P001',
    }
