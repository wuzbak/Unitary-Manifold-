"""
LithosOS — Database Seed Data
"""
from __future__ import annotations
import json
from pathlib import Path

SEED_DATA = [
    {"name": "Quartz", "common_names": ["Rock Crystal", "Silica"], "mineral_class": "Silicate", "crystal_system": "Trigonal", "mohs_hardness": 7.0, "composition": "SiO2", "description": "The most abundant mineral on Earth's surface. Forms hexagonal prismatic crystals.", "luster": "Vitreous", "streak": "White", "cleavage": "None", "specific_gravity": 2.65},
    {"name": "Obsidian", "common_names": ["Volcanic Glass"], "mineral_class": "Mineraloid", "crystal_system": "Amorphous", "mohs_hardness": 5.5, "composition": "SiO2 + MgO + Fe2O3", "description": "Naturally occurring volcanic glass formed from rapidly cooling lava.", "luster": "Vitreous", "streak": "White", "cleavage": "None", "specific_gravity": 2.4},
    {"name": "Pyrite", "common_names": ["Fool's Gold", "Iron Pyrite"], "mineral_class": "Sulfide", "crystal_system": "Cubic", "mohs_hardness": 6.5, "composition": "FeS2", "description": "Brass-yellow metallic mineral known as fool's gold.", "luster": "Metallic", "streak": "Greenish-black", "cleavage": "Indistinct", "specific_gravity": 5.0, "toxic": 1},
    {"name": "Gold", "common_names": ["Native Gold", "Au"], "mineral_class": "Native Element", "crystal_system": "Cubic", "mohs_hardness": 2.5, "composition": "Au", "description": "Precious metal with high malleability and conductivity.", "luster": "Metallic", "streak": "Golden-yellow", "cleavage": "None", "specific_gravity": 19.3},
    {"name": "Copper", "common_names": ["Native Copper", "Cu"], "mineral_class": "Native Element", "crystal_system": "Cubic", "mohs_hardness": 3.0, "composition": "Cu", "description": "Reddish metallic element essential in electrical wiring and alloys.", "luster": "Metallic", "streak": "Copper-red", "cleavage": "None", "specific_gravity": 8.9},
    {"name": "Diamond", "common_names": ["Brilliant", "Rock"], "mineral_class": "Native Element", "crystal_system": "Cubic", "mohs_hardness": 10.0, "composition": "C", "description": "Hardest natural substance; carbon in cubic crystal form.", "luster": "Adamantine", "streak": "None", "cleavage": "Perfect octahedral", "specific_gravity": 3.5},
    {"name": "Amethyst", "common_names": ["Purple Quartz"], "mineral_class": "Silicate", "crystal_system": "Trigonal", "mohs_hardness": 7.0, "composition": "SiO2 + Fe", "description": "Purple variety of quartz caused by iron impurities.", "luster": "Vitreous", "streak": "White", "cleavage": "None", "specific_gravity": 2.65},
    {"name": "Turquoise", "common_names": ["Persian Turquoise"], "mineral_class": "Phosphate", "crystal_system": "Triclinic", "mohs_hardness": 6.0, "composition": "CuAl6(PO4)4(OH)8·4H2O", "description": "Blue-green phosphate mineral valued as gemstone since antiquity.", "luster": "Waxy", "streak": "White to pale green", "cleavage": "None", "specific_gravity": 2.7},
    {"name": "Malachite", "common_names": ["Green Copper Carbonate"], "mineral_class": "Carbonate", "crystal_system": "Monoclinic", "mohs_hardness": 3.75, "composition": "Cu2CO3(OH)2", "description": "Bright green copper carbonate hydroxide mineral.", "luster": "Vitreous to silky", "streak": "Light green", "cleavage": "Perfect", "specific_gravity": 3.9, "toxic": 1},
    {"name": "Lapis Lazuli", "common_names": ["Lapis", "Azure Stone"], "mineral_class": "Rock", "crystal_system": "Cubic", "mohs_hardness": 5.5, "composition": "Lazurite + Calcite + Pyrite", "description": "Deep-blue metamorphic rock used as gemstone for thousands of years.", "luster": "Dull to waxy", "streak": "Blue-white", "cleavage": "None", "specific_gravity": 2.8},
    {"name": "Hematite", "common_names": ["Iron Ore", "Blood Stone"], "mineral_class": "Oxide", "crystal_system": "Trigonal", "mohs_hardness": 6.0, "composition": "Fe2O3", "description": "Primary iron ore; red-brown streak used as pigment in prehistoric art.", "luster": "Metallic to earthy", "streak": "Red-brown", "cleavage": "None", "specific_gravity": 5.3},
    {"name": "Rose Quartz", "common_names": ["Pink Quartz"], "mineral_class": "Silicate", "crystal_system": "Trigonal", "mohs_hardness": 7.0, "composition": "SiO2 + Ti/Fe/Mn", "description": "Pink variety of quartz with color from titanium impurities.", "luster": "Vitreous", "streak": "White", "cleavage": "None", "specific_gravity": 2.65},
    {"name": "Garnet", "common_names": ["Almandine", "Red Garnet"], "mineral_class": "Silicate", "crystal_system": "Cubic", "mohs_hardness": 7.5, "composition": "Fe3Al2(SiO4)3", "description": "Group of silicate minerals used as gemstones and abrasives.", "luster": "Vitreous to resinous", "streak": "White", "cleavage": "Indistinct", "specific_gravity": 4.3},
    {"name": "Topaz", "common_names": ["Imperial Topaz", "Blue Topaz"], "mineral_class": "Silicate", "crystal_system": "Orthorhombic", "mohs_hardness": 8.0, "composition": "Al2SiO4(F,OH)2", "description": "Aluminium silicate fluoride mineral prized as gemstone.", "luster": "Vitreous", "streak": "White", "cleavage": "Perfect basal", "specific_gravity": 3.5},
    {"name": "Feldspar", "common_names": ["Orthoclase", "Plagioclase"], "mineral_class": "Silicate", "crystal_system": "Monoclinic", "mohs_hardness": 6.0, "composition": "KAlSi3O8", "description": "Most abundant mineral group in Earth's crust.", "luster": "Vitreous to pearly", "streak": "White", "cleavage": "Perfect", "specific_gravity": 2.56},
    {"name": "Mica", "common_names": ["Muscovite", "Biotite"], "mineral_class": "Silicate", "crystal_system": "Monoclinic", "mohs_hardness": 2.5, "composition": "KAl2(AlSi3O10)(OH)2", "description": "Sheet silicate with perfect basal cleavage; used in electronics.", "luster": "Vitreous to pearly", "streak": "White", "cleavage": "Perfect basal", "specific_gravity": 2.8},
    {"name": "Calcite", "common_names": ["Calcspar", "Iceland Spar"], "mineral_class": "Carbonate", "crystal_system": "Trigonal", "mohs_hardness": 3.0, "composition": "CaCO3", "description": "Most stable polymorph of calcium carbonate; forms limestone.", "luster": "Vitreous", "streak": "White", "cleavage": "Perfect rhombohedral", "specific_gravity": 2.71},
    {"name": "Fluorite", "common_names": ["Fluorspar", "Calcium Fluoride"], "mineral_class": "Halide", "crystal_system": "Cubic", "mohs_hardness": 4.0, "composition": "CaF2", "description": "Highly variable color mineral; defines Mohs hardness 4.", "luster": "Vitreous", "streak": "White", "cleavage": "Perfect octahedral", "specific_gravity": 3.18},
    {"name": "Silver", "common_names": ["Native Silver", "Ag"], "mineral_class": "Native Element", "crystal_system": "Cubic", "mohs_hardness": 2.5, "composition": "Ag", "description": "Lustrous white precious metal with highest electrical conductivity.", "luster": "Metallic", "streak": "Silver-white", "cleavage": "None", "specific_gravity": 10.5},
    {"name": "Iron", "common_names": ["Native Iron", "Fe"], "mineral_class": "Native Element", "crystal_system": "Cubic", "mohs_hardness": 4.0, "composition": "Fe", "description": "Most used metal in industry; forms from meteorites naturally.", "luster": "Metallic", "streak": "Gray-black", "cleavage": "None", "specific_gravity": 7.87},
    {"name": "Emerald", "common_names": ["Green Beryl"], "mineral_class": "Silicate", "crystal_system": "Hexagonal", "mohs_hardness": 7.5, "composition": "Be3Al2Si6O18 + Cr/V", "description": "Green variety of beryl; one of the four precious gemstones.", "luster": "Vitreous", "streak": "White", "cleavage": "Imperfect", "specific_gravity": 2.76},
    {"name": "Azurite", "common_names": ["Blue Copper Carbonate"], "mineral_class": "Carbonate", "crystal_system": "Monoclinic", "mohs_hardness": 3.75, "composition": "Cu3(CO3)2(OH)2", "description": "Deep-blue copper carbonate mineral; often found with malachite.", "luster": "Vitreous", "streak": "Blue", "cleavage": "Perfect", "specific_gravity": 3.8, "toxic": 1},
]

def seed_database(db_path: Path, verbose: bool = True) -> None:
    from .schema import get_conn, upsert_specimen
    with get_conn(db_path) as conn:
        for item in SEED_DATA:
            upsert_specimen(conn, item)
    if verbose:
        print(f"[LithosOS] Seeded {len(SEED_DATA)} specimens into {db_path}")
    # Seed extended mineral guides (with per-source references)
    from .mineral_guides import seed_mineral_guides
    seed_mineral_guides(db_path, verbose=verbose)

if __name__ == "__main__":
    import sys
    from pathlib import Path
    db = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/lithos.db")
    seed_database(db)
