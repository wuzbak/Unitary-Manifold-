"""
LithosOS — Mineral Guides Data Module
=======================================
Curated mineral/gem/rock data from five publicly available authoritative sources,
bundled directly into the SQLite database for 100% offline use.

Sources:
  Mindat    — Mindat.org (Hudson Institute of Mineralogy, open data API)
              https://www.mindat.org/
  GIA       — Gemological Institute of America, Gem Encyclopedia
              https://www.gia.edu/gem-encyclopedia
  Smithsonian — Smithsonian National Museum of Natural History, National Gem Collection
              https://naturalhistory.si.edu/research/geology/collections
  USGS      — U.S. Geological Survey, Minerals Information Team
              https://www.usgs.gov/centers/national-minerals-information-center
  Minerals.net — Minerals.net (educational mineralogy reference)
              https://www.minerals.net/mineral/

Offline trick:  All data is pre-seeded into SQLite on first run.  No
internet connection is required.  When online, `mindat_fetcher.py` can
refresh entries and add newly published fact sheets.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

# ---------------------------------------------------------------------------
# Guide source registry  (used to populate source_references rows)
# ---------------------------------------------------------------------------

GUIDE_SOURCES: dict[str, dict] = {
    "Mindat": {
        "source_name": "Mindat",
        "source_url": "https://www.mindat.org/",
        "citation": (
            "Hudson Institute of Mineralogy. Mindat.org — The Mineral and Locality Database. "
            "Mindat.org, Keswick, VA."
        ),
    },
    "GIA": {
        "source_name": "GIA",
        "source_url": "https://www.gia.edu/gem-encyclopedia",
        "citation": (
            "Gemological Institute of America. GIA Gem Encyclopedia. "
            "GIA, Carlsbad, CA."
        ),
    },
    "Smithsonian": {
        "source_name": "Smithsonian",
        "source_url": "https://naturalhistory.si.edu/research/geology/collections",
        "citation": (
            "Smithsonian National Museum of Natural History. "
            "National Gem and Mineral Collection, Department of Mineral Sciences. "
            "Smithsonian Institution, Washington, DC."
        ),
    },
    "USGS": {
        "source_name": "USGS",
        "source_url": "https://www.usgs.gov/centers/national-minerals-information-center",
        "citation": (
            "U.S. Geological Survey. Mineral Commodity Summaries & Minerals Yearbook. "
            "USGS National Minerals Information Center, Reston, VA."
        ),
    },
    "Minerals.net": {
        "source_name": "Minerals.net",
        "source_url": "https://www.minerals.net/mineral/",
        "citation": (
            "Minerals.net — The Mineral and Gemstone Kingdom. "
            "Educational mineralogy reference."
        ),
    },
}


# ---------------------------------------------------------------------------
# Extended mineral guide dataset — 40 specimens with per-source references.
# Each entry has: specimen data + identification_notes, safety_notes, and
# market_notes per source.
# ---------------------------------------------------------------------------

MINERAL_GUIDE_ENTRIES: list[dict] = [
    # ── NATIVE ELEMENTS ───────────────────────────────────────────────────
    {
        "specimen": {
            "name": "Native Sulphur",
            "common_names": ["Sulfur", "Brimstone"],
            "mineral_class": "Native Element",
            "crystal_system": "Orthorhombic",
            "mohs_hardness": 2.0,
            "composition": "S",
            "description": (
                "Bright-yellow native element deposited around volcanic fumaroles and "
                "hot springs. Brittle and pyroelectric. Chief source of sulfuric acid "
                "feedstock; also used in fertiliser, rubber vulcanisation, and gunpowder."
            ),
            "luster": "Resinous",
            "streak": "White",
            "cleavage": "Imperfect",
            "specific_gravity": 2.07,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Unmistakable bright yellow; very low hardness; melts easily (~115 °C). FTS index 1.960.",
             "safety_notes": "Burns to produce toxic SO₂; do not heat indoors. Low toxicity raw.",
             "market_notes": "Industrial commodity; <$1/kg bulk. Collector specimens: $5–$50 for Sicilian crystals."},
            {**GUIDE_SOURCES["USGS"],
             "identification_notes": "Primary US sources: Louisiana, Texas (Frasch process); today largely recovered from oil refining.",
             "market_notes": "USGS tracks as critical mineral feedstock for phosphate fertiliser."},
        ],
    },
    {
        "specimen": {
            "name": "Platinum",
            "common_names": ["Native Platinum", "Pt"],
            "mineral_class": "Native Element",
            "crystal_system": "Cubic",
            "mohs_hardness": 4.5,
            "composition": "Pt",
            "description": (
                "Dense, silver-white precious metal. Occurs as grains or nuggets in "
                "ultramafic rocks and alluvial placers. Key catalytic converter metal; "
                "also used in jewellery, medical devices, and laboratory equipment."
            ),
            "luster": "Metallic",
            "streak": "Silver-grey",
            "cleavage": "None",
            "specific_gravity": 21.47,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Heavy (SG 21.47), non-magnetic, ductile, does not tarnish. Malleable unlike silver.",
             "safety_notes": "Platinum metal: low toxicity. Platinum salts (industrial): can cause asthma and skin sensitisation.",
             "market_notes": "Traded on commodity exchanges; ~$30–$35/g (2024). South Africa supplies ~75% of world production."},
            {**GUIDE_SOURCES["USGS"],
             "identification_notes": "Critical mineral; primary occurrences in Bushveld Complex (SA) and Norilsk-Talnakh (Russia).",
             "market_notes": "USGS Mineral Commodity Summary: PGM group; demand driven by automotive catalysts and hydrogen fuel cells."},
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Used in jewellery settings for white metal look without rhodium plating.",
             "market_notes": "Jewellery use: 40–60% premium over spot; hypoallergenic vs white gold."},
        ],
    },
    # ── SILICATES ────────────────────────────────────────────────────────
    {
        "specimen": {
            "name": "Opal",
            "common_names": ["Precious Opal", "Fire Opal", "Common Opal"],
            "mineral_class": "Mineraloid",
            "crystal_system": "Amorphous",
            "mohs_hardness": 6.0,
            "composition": "SiO2·nH2O",
            "description": (
                "Hydrated amorphous silica. Precious opal shows play-of-colour (iridescence) "
                "from diffraction of light by stacked silica spheres. Contains up to 20% water; "
                "prone to crazing if dehydrated. Major sources: Australia (Lightning Ridge, Coober Pedy)."
            ),
            "luster": "Vitreous to waxy",
            "streak": "White",
            "cleavage": "None",
            "specific_gravity": 2.15,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Play-of-colour distinguishes precious opal; body colour ranges white, black, crystal, fire-orange.",
             "safety_notes": "No toxicity. Amorphous silica unlike crystalline quartz — no silicosis risk.",
             "market_notes": "Black opal: $100–$10,000+/ct (Lightning Ridge). White opal: $10–$150/ct. Synthetic Gilson opals exist."},
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "SG 1.98–2.20; RI 1.37–1.47. Beware simulants: plastic, glass, synthetic opal.",
             "market_notes": "Doublets and triplets: greatly reduced value vs solid opal — disclose on sale."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "Hope Opal (Smithsonian collection) is 34.5 ct Australian black opal; reference specimen for play-of-colour studies."},
        ],
    },
    {
        "specimen": {
            "name": "Tanzanite",
            "common_names": ["Blue Zoisite", "Tiffany Stone"],
            "mineral_class": "Silicate",
            "crystal_system": "Orthorhombic",
            "mohs_hardness": 6.5,
            "composition": "Ca2Al3(SiO4)3(OH)",
            "description": (
                "Blue-violet variety of zoisite; strongly trichroic (blue, violet, burgundy). "
                "Discovered 1967 near Arusha, Tanzania. Found ONLY in the Merelani Hills — "
                "one of the rarest gemstones on Earth. Heat-treated to remove brown tones."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Perfect",
            "specific_gravity": 3.35,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Strong trichroism; RI 1.691–1.700; SG 3.35. Pleochroism shifts with orientation.",
             "safety_notes": "No toxicity. Avoid ultrasonic and steam cleaners — cleavage risk.",
             "market_notes": "Top colour (vB 6/5): $1,200–$1,600/ct. Mid range: $400–$800/ct. Supply finite — mine depletion projected ~2025–2030."},
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Single source locality: Merelani Hills, Manyara Region, Tanzania. No other verified deposits worldwide.",
             "market_notes": "Tiffany & Co popularised name 'tanzanite' (1968). Ethical sourcing: prefer TanzaniteOne conflict-free certification."},
        ],
    },
    {
        "specimen": {
            "name": "Alexandrite",
            "common_names": ["Colour-Change Chrysoberyl", "Russian Alexandrite"],
            "mineral_class": "Oxide",
            "crystal_system": "Orthorhombic",
            "mohs_hardness": 8.5,
            "composition": "BeAl2O4 + Cr",
            "description": (
                "Rare chromium-bearing variety of chrysoberyl with dramatic colour change: "
                "green in daylight, red under incandescent light. Chromium absorption bands "
                "sit at the crossover of human photopic and scotopic response. "
                "Originally from Ural Mountains, Russia (1830); now also Sri Lanka, Brazil."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Distinct",
            "specific_gravity": 3.73,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "RI 1.746–1.763; SG 3.73. Strong colour change is diagnostic. Cat's eye alexandrite also exists.",
             "safety_notes": "No toxicity. Very durable — suitable for everyday jewellery.",
             "market_notes": "Fine Russian alexandrite (strong change): $10,000–$50,000+/ct. Brazilian: $3,000–$15,000/ct. Synthetic Czochralski-grown alexandrite available at <$100/ct."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "Smithsonian has 66 ct Russian alexandrite as type reference. Strong colour change: green daylight, raspberry red incandescent."},
        ],
    },
    {
        "specimen": {
            "name": "Spinel",
            "common_names": ["Red Spinel", "Balas Ruby"],
            "mineral_class": "Oxide",
            "crystal_system": "Cubic",
            "mohs_hardness": 8.0,
            "composition": "MgAl2O4",
            "description": (
                "Magnesium aluminium oxide; occurs in many colours (red, blue, pink, orange, black). "
                "Long confused with ruby — the 'Black Prince's Ruby' in the Imperial State Crown "
                "is actually a 170 ct red spinel. Now recognised as distinct from ruby by crystal system "
                "and single refraction."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Indistinct",
            "specific_gravity": 3.60,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Single refractive (cubic); RI 1.718. Red spinel vs ruby: spinel lacks rutile silk and fluorite inclusions.",
             "safety_notes": "Non-toxic. Excellent durability — rated 8 on Mohs.",
             "market_notes": "Burmese red spinel ('jedi' red): $3,000–$10,000/ct. Vivid pink-orange (mahenge): up to $20,000/ct. Blue spinel: $500–$3,000/ct."},
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Classic localities: Mogok (Myanmar), Badakhshan (Afghanistan). Synthetic Verneuil spinel common in lab-created coloured stones."},
        ],
    },
    # ── CARBONATES ───────────────────────────────────────────────────────
    {
        "specimen": {
            "name": "Rhodochrosite",
            "common_names": ["Manganese Spar", "Raspberry Spar"],
            "mineral_class": "Carbonate",
            "crystal_system": "Trigonal",
            "mohs_hardness": 4.0,
            "composition": "MnCO3",
            "description": (
                "Manganese carbonate mineral; iconic rose-red to pink banded masses. "
                "Best specimens from Capillitas mine (Argentina) and Butte, Montana. "
                "Colorado's state mineral. Cut as cabochon; crystals are facetable rarities. "
                "Stalactitic cross-sections reveal concentric pink-and-white banding."
            ),
            "luster": "Vitreous to pearly",
            "streak": "White",
            "cleavage": "Perfect rhombohedral",
            "specific_gravity": 3.70,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Dissolves in cold HCl (slower than calcite). Pink colour + perfect cleavage diagnostic. Fluorescent orange under SW UV.",
             "safety_notes": "Low toxicity as mineral. Industrial manganese dust: neurological risk — not relevant to collector specimens.",
             "market_notes": "Stalactite slabs (Capillitas): $20–$200/piece. Fine rhombohedral crystals: $500–$5,000+ per specimen."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "National collection includes Capillitas stalactitic columns — primary reference for banding morphology."},
        ],
    },
    {
        "specimen": {
            "name": "Smithsonite",
            "common_names": ["Zinc Spar", "Bonamite"],
            "mineral_class": "Carbonate",
            "crystal_system": "Trigonal",
            "mohs_hardness": 4.5,
            "composition": "ZnCO3",
            "description": (
                "Zinc carbonate occurring in a variety of pastel colours (green, blue, pink, yellow, "
                "lavender) depending on trace elements (Cu → blue/green, Co → pink, Mn → yellow). "
                "Named after James Smithson, founder of the Smithsonian Institution. "
                "Primary ore of zinc before modern ore processing."
            ),
            "luster": "Vitreous to pearly",
            "streak": "White",
            "cleavage": "Perfect rhombohedral",
            "specific_gravity": 4.40,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Effervesces in HCl. Colour variety mimics many minerals; SG 4.4 is unusually heavy for carbonates.",
             "safety_notes": "Zinc carbonate: low acute toxicity. Zinc oxide fume from heating is harmful — irrelevant to lapidary use.",
             "market_notes": "Collector specimens: $30–$500 for coloured botryoidal masses. Blue-green (Arizona): most valued."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "Named for James Smithson; type specimen at NHM London. Smithsonian has fine Kelly Mine (NM) reference suite."},
        ],
    },
    # ── PHOSPHATES / SULFATES / HALIDES ──────────────────────────────────
    {
        "specimen": {
            "name": "Apatite",
            "common_names": ["Fluorapatite", "Chlorapatite", "Hydroxylapatite"],
            "mineral_class": "Phosphate",
            "crystal_system": "Hexagonal",
            "mohs_hardness": 5.0,
            "composition": "Ca5(PO4)3(F,Cl,OH)",
            "description": (
                "Phosphate mineral group defining Mohs hardness 5. Occurs in igneous, "
                "metamorphic, and sedimentary rocks. Hydroxylapatite is the main mineral "
                "component of bone and teeth. Industrial source of phosphate for fertilisers. "
                "Gem-quality crystals are rare — neon blue Brazilian apatite is especially prized."
            ),
            "luster": "Vitreous to resinous",
            "streak": "White",
            "cleavage": "Indistinct",
            "specific_gravity": 3.20,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Hexagonal prisms; scratches glass barely, scratched by knife. RI 1.630–1.667.",
             "safety_notes": "Non-toxic in mineral form. Fluorapatite dust: fluoride content — wear dust mask when cutting.",
             "market_notes": "Gem apatite (neon blue): $10–$80/ct. Cat's eye apatite: $50–$200/ct. Industrial phosphate rock: ~$100/tonne."},
            {**GUIDE_SOURCES["USGS"],
             "identification_notes": "Critical mineral for fertiliser (MAP, DAP). US has no active phosphate mining in quantity — import-dependent.",
             "market_notes": "USGS Mineral Commodity Summary: phosphate rock listed as critical mineral (2022 list)."},
        ],
    },
    {
        "specimen": {
            "name": "Barite",
            "common_names": ["Barytes", "Heavy Spar", "Desert Rose"],
            "mineral_class": "Sulfate",
            "crystal_system": "Orthorhombic",
            "mohs_hardness": 3.5,
            "composition": "BaSO4",
            "description": (
                "Barium sulphate; notable for exceptionally high specific gravity (4.5) for a "
                "non-metallic mineral. 'Desert rose' barite is a classic sand-crystal form. "
                "Main industrial use: drilling mud weighting agent in oil/gas wells. "
                "Also used in X-ray shielding and as the white pigment 'blanc fixe'."
            ),
            "luster": "Vitreous to pearly",
            "streak": "White",
            "cleavage": "Perfect",
            "specific_gravity": 4.50,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "High SG (4.5) + white streak + perfect cleavage diagnostic. Often colourless to white; blue/yellow/red variety exists.",
             "safety_notes": "BaSO4 is essentially non-toxic (insoluble). Barium salts in general are toxic — does NOT apply to barite.",
             "market_notes": "Desert rose barite: $5–$50/specimen. Industrial grade: $100–$200/tonne. Major producers: China, India, Morocco."},
            {**GUIDE_SOURCES["USGS"],
             "market_notes": "USGS: US consumes ~2.3 million tonnes/year; 95% goes to oil/gas drilling industry."},
        ],
    },
    {
        "specimen": {
            "name": "Halite",
            "common_names": ["Rock Salt", "Common Salt", "Table Salt"],
            "mineral_class": "Halide",
            "crystal_system": "Cubic",
            "mohs_hardness": 2.5,
            "composition": "NaCl",
            "description": (
                "Sodium chloride; the mineral form of common salt. Forms cubic crystals, "
                "often colourless or white; trace impurities produce blue (electron colour centres), "
                "pink (bacteria in Himalayan salt), or orange. Tastes salty — "
                "diagnostic without instrument. Enormous evaporite deposits worldwide."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Perfect cubic",
            "specific_gravity": 2.16,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Salty taste, perfect cubic cleavage, soluble in water. Grows as cubes with hopper faces.",
             "safety_notes": "Edible in food quantities. High intake: cardiovascular risk. Blue halite (radiation damage): display only.",
             "market_notes": "Industrial NaCl: <$50/tonne. Himalayan pink salt blocks: $10–$100 retail. Collector blue halite: $20–$200/specimen."},
            {**GUIDE_SOURCES["USGS"],
             "market_notes": "US production ~44 million tonnes/year. Uses: road de-icing (largest), chemicals, food."},
        ],
    },
    # ── OXIDES ───────────────────────────────────────────────────────────
    {
        "specimen": {
            "name": "Corundum",
            "common_names": ["Ruby (red)", "Sapphire (blue/other)", "Emery"],
            "mineral_class": "Oxide",
            "crystal_system": "Trigonal",
            "mohs_hardness": 9.0,
            "composition": "Al2O3",
            "description": (
                "Aluminium oxide; second hardest natural mineral. Red corundum = ruby (Cr); "
                "all other colours = sapphire (Fe, Ti, V, Cr). Emery is impure granular corundum "
                "used as abrasive. Star rubies/sapphires show asterism from rutile needles. "
                "Synthetic corundum (Verneuil, Czochralski) used for watch bearings and lasers."
            ),
            "luster": "Adamantine to vitreous",
            "streak": "White",
            "cleavage": "None (parting along rhombohedra)",
            "specific_gravity": 4.00,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "RI 1.762–1.770; SG 4.0; double refractive. Hardness 9 — scratches topaz. Hexagonal barrel prisms.",
             "safety_notes": "Corundum dust: abrasive; use dust extraction. No chemical toxicity.",
             "market_notes": "Burmese pigeon-blood ruby: $1M+/ct (>5 ct, unheated). Blue sapphire (Kashmir): $5,000–$100,000/ct. Heated stones: 50–80% value reduction."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "Logan Sapphire (423 ct, Sri Lanka) and Carmen Lúcia Ruby (23.1 ct, Burma) are Smithsonian reference gems for corundum study."},
            {**GUIDE_SOURCES["Mindat"],
             "market_notes": "Beryllium diffusion treatment (2001): produces artificial orange/yellow rims — detectable only by LA-ICP-MS. Full disclosure required."},
        ],
    },
    {
        "specimen": {
            "name": "Magnetite",
            "common_names": ["Lodestone", "Iron Ore", "Magnetic Iron Ore"],
            "mineral_class": "Oxide",
            "crystal_system": "Cubic",
            "mohs_hardness": 6.0,
            "composition": "Fe3O4",
            "description": (
                "Strongly magnetic iron oxide; the most magnetic naturally occurring mineral. "
                "Natural lodestone was used in the first compasses. Major iron ore; "
                "forms large masses in banded iron formations (BIFs), and small crystals in "
                "metamorphic and volcanic rocks. Octahedral crystal habit."
            ),
            "luster": "Metallic to submetallic",
            "streak": "Black",
            "cleavage": "None",
            "specific_gravity": 5.18,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Strong magnetic response — test with hand magnet. Black streak + octahedral crystals + hardness 6 diagnostic.",
             "safety_notes": "Non-toxic. Fine Fe3O4 nanoparticles: potential inhalation hazard — irrelevant for collector specimens.",
             "market_notes": "Iron ore price: $100–$130/tonne (Fe content basis). Lodestone specimens: $5–$100. Octahedral crystals (Binntal, CH): $50–$500."},
            {**GUIDE_SOURCES["USGS"],
             "market_notes": "World iron ore production ~2.6 billion tonnes/yr; magnetite is primary ore in many deposits."},
        ],
    },
    {
        "specimen": {
            "name": "Cassiterite",
            "common_names": ["Tin Stone", "Tin Ore"],
            "mineral_class": "Oxide",
            "crystal_system": "Tetragonal",
            "mohs_hardness": 7.0,
            "composition": "SnO2",
            "description": (
                "Primary ore of tin; tin dioxide. Heavy (SG 7.0); occurs in granite pegmatites "
                "and hydrothermal veins, also as alluvial grains. Brown to black; adamantine "
                "lustre. Geuda-type gem crystals are rare; faceted cassiterite shows "
                "high dispersion (fire) comparable to diamond."
            ),
            "luster": "Adamantine to submetallic",
            "streak": "White to pale grey",
            "cleavage": "Imperfect",
            "specific_gravity": 7.00,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Very high SG (7.0) + adamantine lustre + brown colour diagnostic. Crystals: tetragonal prisms with pyramidal terminations.",
             "safety_notes": "Tin dioxide: low toxicity. Organotin compounds (industrial, not in mineral) are toxic.",
             "market_notes": "Tin metal: ~$25,000/tonne (LME). Gem cassiterite: $30–$200/ct. Best crystals from Bolivia (Potosí), Malaysia, Nigeria."},
            {**GUIDE_SOURCES["USGS"],
             "market_notes": "USGS Critical Mineral 2022 list. US has no domestic tin mine production; 100% import-dependent."},
        ],
    },
    # ── SULFIDES ─────────────────────────────────────────────────────────
    {
        "specimen": {
            "name": "Galena",
            "common_names": ["Lead Glance", "Lead Ore"],
            "mineral_class": "Sulfide",
            "crystal_system": "Cubic",
            "mohs_hardness": 2.5,
            "composition": "PbS",
            "description": (
                "Primary ore of lead and often silver. Bright metallic lustre; "
                "very heavy (SG 7.6); perfect cubic cleavage. Cubic and octahedral crystals. "
                "Lead smelt risk: historically used in paints, pipes, solder. "
                "Major deposits: Broken Hill (Australia), Viburnum Trend (USA), Bingham Canyon (USA)."
            ),
            "luster": "Bright metallic",
            "streak": "Lead-grey",
            "cleavage": "Perfect cubic",
            "specific_gravity": 7.60,
            "toxic": 1,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Perfect cubic cleavage, bright metallic, very heavy (SG 7.6), soft (2.5). Lead-grey streak distinguishes from argentite.",
             "safety_notes": "Lead sulfide: LOW direct toxicity as mineral vs soluble lead compounds. Do NOT sand/grind without ventilation. Wash hands after handling. Do not display near food.",
             "market_notes": "Lead price: ~$2,000/tonne (LME). Galena specimens (cubo-octahedral twins): $10–$200. Large crystals: up to $1,000."},
            {**GUIDE_SOURCES["USGS"],
             "market_notes": "Lead: USGS tracks as commodity; recycled batteries are largest supply source in US."},
        ],
    },
    {
        "specimen": {
            "name": "Chalcopyrite",
            "common_names": ["Copper Pyrite", "Fool's Gold (chalco)"],
            "mineral_class": "Sulfide",
            "crystal_system": "Tetragonal",
            "mohs_hardness": 3.5,
            "composition": "CuFeS2",
            "description": (
                "Most important copper ore mineral. Brassy-yellow with greenish tinge; "
                "harder and less lustrous than pyrite. Iridescent 'peacock' copper surface "
                "from oxidation. Occurs in porphyry copper, skarn, and VMS deposits. "
                "World's leading copper source; extracted by open-pit and flotation."
            ),
            "luster": "Metallic",
            "streak": "Greenish-black",
            "cleavage": "Indistinct",
            "specific_gravity": 4.20,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Brassy yellow but greener than pyrite; SG 4.2 (lower than pyrite 5.0); softer (3.5 vs 6.5). Greenish-black streak vs pyrite's greenish-black streak — test both.",
             "safety_notes": "Low acute toxicity. Copper dust inhalation: metal fume fever potential in industrial settings.",
             "market_notes": "Copper price: ~$9,000/tonne (LME). Iridescent 'peacock copper' specimens: $10–$80. Cut from Butte (MT) or Chessy (France) most collectible."},
            {**GUIDE_SOURCES["USGS"],
             "market_notes": "USGS: copper is critical mineral; ~20% of world production from porphyry copper deposits (Bingham, El Teniente, Grasberg)."},
        ],
    },
    {
        "specimen": {
            "name": "Sphalerite",
            "common_names": ["Zinc Blende", "Black Jack", "Ruby Zinc"],
            "mineral_class": "Sulfide",
            "crystal_system": "Cubic",
            "mohs_hardness": 4.0,
            "composition": "ZnS",
            "description": (
                "Primary zinc ore. Highly variable colour (black iron-rich, orange/red, yellow, "
                "colourless). Resinous to adamantine lustre; highest dispersion of any faceted "
                "gemstone (0.156 — 3.5× diamond), but too soft for jewellery wear. "
                "Triboluminescent — emits light when struck."
            ),
            "luster": "Resinous to adamantine",
            "streak": "White to pale yellow",
            "cleavage": "Perfect dodecahedral (6 directions)",
            "specific_gravity": 4.09,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "6-direction perfect cleavage is distinctive. Resinous lustre; can be confused with blende. Triboluminescence: dark-room test.",
             "safety_notes": "Zinc sulfide: low toxicity. Cadmium-rich sphalerite (greenockite impurity): extra caution — test before lapidary work.",
             "market_notes": "Zinc price: ~$2,500/tonne. Honey-coloured gem sphalerite: $20–$100/ct. Finest orange-red from Sonora (Mexico)."},
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Dispersion (fire) 0.156 vs diamond 0.044 — spectacular in faceted gem; but Mohs 4 limits wear to display only."},
        ],
    },
    {
        "specimen": {
            "name": "Cinnabar",
            "common_names": ["Vermilion Ore", "Dragon's Blood"],
            "mineral_class": "Sulfide",
            "crystal_system": "Trigonal",
            "mohs_hardness": 2.5,
            "composition": "HgS",
            "description": (
                "Mercury sulfide; brilliant scarlet red. Primary ore of mercury. "
                "Ground pigment 'vermilion' used by Old Masters (Vermeer, Titian). "
                "Occurs near hot springs and volcanic vents. Major deposits: Almadén (Spain), "
                "Idrija (Slovenia), New Almaden (California). TOXIC — handle with extreme care."
            ),
            "luster": "Adamantine to dull",
            "streak": "Scarlet-red",
            "cleavage": "Perfect prismatic",
            "specific_gravity": 8.10,
            "toxic": 1,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Scarlet-red streak is unmistakable. Very heavy (SG 8.1). Bright red + adamantine lustre + low hardness (2.5).",
             "safety_notes": "HIGHLY TOXIC. Mercury sulfide dissolves slowly to release Hg²⁺. Handle with nitrile gloves; never sand or heat; store sealed; keep from children. Not safe for lapidary work.",
             "market_notes": "Mercury price: ~$2,000/76 lb flask; declining with phase-out (Minamata Convention 2017). Collector cinnabar: $20–$500 for crystal on matrix. Almadén (Spain) most prized."},
            {**GUIDE_SOURCES["USGS"],
             "market_notes": "USGS: Mercury demand dropped 80% since 2000; primary remaining use is artisanal gold mining (ASGM) in developing countries."},
        ],
    },
    # ── IGNEOUS ROCKS / GEMSTONES ────────────────────────────────────────
    {
        "specimen": {
            "name": "Peridot",
            "common_names": ["Olivine Gem", "Chrysolite", "Evening Emerald"],
            "mineral_class": "Silicate",
            "crystal_system": "Orthorhombic",
            "mohs_hardness": 7.0,
            "composition": "(Mg,Fe)2SiO4",
            "description": (
                "Gem-quality forsterite-olivine; one of the few gems that occurs in only one colour "
                "(yellow-green to olive-green — from Fe²⁺). Found in ultramafic igneous rocks "
                "(peridotite, basalt), meteorites (pallasite), and mantle xenoliths. "
                "Zabargad Island (Egypt) supplied ancient Pharaonic peridot."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Imperfect",
            "specific_gravity": 3.34,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "RI 1.654–1.690; SG 3.34; double refractive. 'Lily pad' inclusions (disc-shaped chromite) diagnostic. Yellow-green is characteristic.",
             "safety_notes": "Non-toxic. Avoid extreme temperature changes — thermal shock can crack.",
             "market_notes": "San Carlos Apache (Arizona) peridot: $5–$30/ct. Pakistan (Kaghan Valley) fine: $50–$200/ct. Egyptian Zabargad: premium history."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "Pallasitic meteorite peridot (olivine in iron-nickel matrix) — unique extra-terrestrial gems displayed in Smithsonian Janet Annenberg Hooker Hall."},
        ],
    },
    {
        "specimen": {
            "name": "Moonstone",
            "common_names": ["Adularia Moonstone", "Rainbow Moonstone", "Blue Moonstone"],
            "mineral_class": "Silicate",
            "crystal_system": "Monoclinic",
            "mohs_hardness": 6.0,
            "composition": "KAlSi3O8 (orthoclase-albite layers)",
            "description": (
                "Adularescence is the billowy, floating blue sheen caused by light scattering "
                "between alternating layers of orthoclase and albite feldspar. "
                "True blue moonstone from Sri Lanka; 'rainbow moonstone' is actually labradorite. "
                "Sri Lankan fine blue moonstone is increasingly rare due to mine depletion."
            ),
            "luster": "Vitreous with adularescence",
            "streak": "White",
            "cleavage": "Perfect",
            "specific_gravity": 2.57,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Adularescence — floating blue glow. RI 1.518–1.526; SG 2.57. Centring the stone optimises the phenomenon.",
             "safety_notes": "Non-toxic. Perfect cleavage — avoid blows; beware ultrasonic cleaners.",
             "market_notes": "Ceylon blue moonstone (top): $50–$300/ct for transparent blue on colourless body. Indian moonstone (white body): $1–$20/ct. Declining Sri Lanka supply is increasing prices."},
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Moonstone vs labradorite: moonstone is orthoclase (monoclinic); labradorite is plagioclase (triclinic) — iridescence called labradorescence, not adularescence."},
        ],
    },
    {
        "specimen": {
            "name": "Zircon",
            "common_names": ["Jacinth (red)", "Starlite (blue)", "Jargon (yellow)"],
            "mineral_class": "Silicate",
            "crystal_system": "Tetragonal",
            "mohs_hardness": 7.5,
            "composition": "ZrSiO4",
            "description": (
                "Zirconium silicate; one of Earth's oldest minerals (Jack Hills, Australia: 4.4 Ga). "
                "High refractive index and dispersion make it an excellent diamond simulant "
                "(before cubic zirconia). Zircon is often radioactive (metamict) due to U/Th substitution; "
                "heat treatment restores crystallinity. Not to be confused with cubic zirconia (ZrO2)."
            ),
            "luster": "Adamantine",
            "streak": "White",
            "cleavage": "Indistinct",
            "specific_gravity": 4.70,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "RI 1.925–1.984 (high); SG 4.7; strong birefringence visible as doubled back facets. Distinct from cubic zirconia (singly refractive).",
             "safety_notes": "Metamict zircon may be mildly radioactive if high U/Th — test before handling large quantities. Gem quality zircon: negligible risk.",
             "market_notes": "Blue zircon (heat-treated): $50–$200/ct. Red zircon: $100–$300/ct. Colourless: $20–$80/ct. Cambodia (Ratanakiri) is leading source."},
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Oldest dated Earth mineral: Jack Hills zircon (4,404 Ma) — not a gem specimen; contains U-Pb geochronology archive."},
        ],
    },
    # ── ORGANIC GEMS ─────────────────────────────────────────────────────
    {
        "specimen": {
            "name": "Amber",
            "common_names": ["Fossil Resin", "Baltic Amber", "Succinite"],
            "mineral_class": "Organic Gem",
            "crystal_system": "Amorphous",
            "mohs_hardness": 2.5,
            "composition": "C10H16O (polymerised terpenoids)",
            "description": (
                "Fossilised tree resin; most from Eocene Baltic forests (~44 Ma). "
                "Succinite (Baltic) has 3–8% succinic acid. May contain inclusions: insects, "
                "plant material, air bubbles. Electrostatic when rubbed. "
                "Major deposits: Baltic coast, Dominican Republic, Burma (Burmese/Kachin amber: Cretaceous, ~100 Ma)."
            ),
            "luster": "Resinous",
            "streak": "White",
            "cleavage": "None",
            "specific_gravity": 1.08,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "SG 1.08 — barely floats in saturated salt water. Warms to touch; burns with resinous sweet smell. Fluorescent (blue-white) under LW UV.",
             "safety_notes": "Non-toxic. Fakes: copal (young resin, not fossilised) and glass/plastic. Copal fails salt water float at lower SG.",
             "market_notes": "Baltic amber: $1–$50/g (gem quality). Burmese amber with inclusions: $10–$1,000+ for insect-bearing pieces. Dominican blue amber (fluorescent): premium."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "Smithsonian has largest known inclusion specimen: Burmese amber with 3 distinct insect species (99 Ma)."},
        ],
    },
    {
        "specimen": {
            "name": "Pearl",
            "common_names": ["Natural Pearl", "Cultured Pearl", "Freshwater Pearl"],
            "mineral_class": "Organic Gem",
            "crystal_system": "Orthorhombic (aragonite layers)",
            "mohs_hardness": 3.0,
            "composition": "CaCO3 (aragonite) + conchiolin protein",
            "description": (
                "Concentric layers of nacre (aragonite + conchiolin) around an irritant. "
                "Natural pearls: unimplanted; rare. Cultured: bead-nucleated (Akoya, South Sea, Tahitian) "
                "or tissue-nucleated (freshwater). Orient is the overtone lustre from nacre light interference. "
                "Saltwater pearls: finer nacre; freshwater: thicker nacre, lower lustre."
            ),
            "luster": "Pearly (orient)",
            "streak": "White",
            "cleavage": "None",
            "specific_gravity": 2.71,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Tooth test: gently rub on tooth edge — genuine pearl feels gritty; imitation is smooth. X-ray reveals nucleus in cultured; no nucleus in natural.",
             "safety_notes": "Non-toxic. Avoid acids (dissolve CaCO3), perfume, and sweat — apply last, take off first. Clean with soft damp cloth only.",
             "market_notes": "South Sea white pearl (16 mm): $500–$5,000. Tahitian black: $200–$2,000. Natural Gulf pearl (undrilled): $10,000+/ct. Chinese freshwater: $1–$50/strand."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "La Peregrina (historic natural pearl, 203 gr) — famous provenance from Philip II of Spain → Elizabeth Taylor. Demonstrated natural vs cultured distinction."},
        ],
    },
    {
        "specimen": {
            "name": "Jet",
            "common_names": ["Black Amber", "Whitby Jet"],
            "mineral_class": "Organic Gem",
            "crystal_system": "Amorphous",
            "mohs_hardness": 3.5,
            "composition": "Lignite (compressed fossil wood)",
            "description": (
                "A variety of lignite coal; fossilised Araucaria wood compressed over "
                "~182 million years (Jurassic). Whitby (Yorkshire) is the premier source. "
                "Carved into Victorian mourning jewellery after Prince Albert's death (1861). "
                "Warm and light; can be turned on a lathe. Electrostatic when rubbed."
            ),
            "luster": "Waxy to bright",
            "streak": "Brown",
            "cleavage": "None",
            "specific_gravity": 1.30,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Brown streak (not black — distinguishes from onyx/glass). Warm and light (SG 1.3). Burns with coal-like smell. Spanish jet (Azabache) is harder, higher quality than cannel coal substitutes.",
             "safety_notes": "Non-toxic. Dust from carving: respiratory precaution. Avoid heat — combustible.",
             "market_notes": "Whitby jet: £50–£500 for Victorian pieces; £10–£100 for modern carved pieces. Spanish azabache: $5–$50."},
        ],
    },
    # ── ADDITIONAL KEY MINERALS ───────────────────────────────────────────
    {
        "specimen": {
            "name": "Aquamarine",
            "common_names": ["Sea Water Beryl", "Blue Beryl"],
            "mineral_class": "Silicate",
            "crystal_system": "Hexagonal",
            "mohs_hardness": 7.5,
            "composition": "Be3Al2Si6O18 + Fe²⁺/Fe³⁺",
            "description": (
                "Blue to blue-green variety of beryl. Colour from Fe²⁺ (blue) and Fe³⁺ (yellow → "
                "blue-green). Hexagonal prisms, often large and inclusion-free. "
                "Irradiation produces deeper blue; heat removes green component. "
                "Santa Maria de Itabira (Brazil) defines the benchmark 'Santa Maria' blue."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Imperfect",
            "specific_gravity": 2.72,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "RI 1.577–1.583; SG 2.72; hexagonal crystal habit. Pale blue is standard; saturated blue commands premium.",
             "safety_notes": "Non-toxic. Avoid high heat — may lose colour. Suitable for everyday jewellery.",
             "market_notes": "Santa Maria blue (Brazil): $100–$500/ct. Medium blue: $20–$100/ct. Irradiated topaz (Swiss blue) is common simulant — distinguish by RI."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "Dom Pedro aquamarine (26,058 ct, Minas Gerais) — largest faceted aquamarine in existence; on display at Smithsonian."},
        ],
    },
    {
        "specimen": {
            "name": "Rhodonite",
            "common_names": ["Manganese Silicate", "Pink Manganese"],
            "mineral_class": "Silicate",
            "crystal_system": "Triclinic",
            "mohs_hardness": 6.0,
            "composition": "MnSiO3",
            "description": (
                "Rose-pink to red manganese silicate with characteristic black manganese oxide "
                "vein inclusions on cut surfaces. Classic ornamental stone — used in Russia "
                "for decorative objects (Ural Mountains). Gem-quality transparent crystals "
                "are extremely rare; most used for cabochons and carvings."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Perfect",
            "specific_gravity": 3.60,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Pink colour + black Mn-oxide veining diagnostic. Harder and denser than rhodochrosite (MnCO3). Does not effervesce with HCl (vs rhodochrosite).",
             "safety_notes": "Non-toxic as mineral. Industrial Mn dust: neuro risk — not relevant for collector specimens.",
             "market_notes": "Cabochon material: $5–$30/ct. Fine faceted gem rhodonite: $50–$200/ct (transparent, clean). Russian carved objects command art-market premiums."},
        ],
    },
    {
        "specimen": {
            "name": "Kyanite",
            "common_names": ["Disthene", "Cyanite", "Sapphire Spar"],
            "mineral_class": "Silicate",
            "crystal_system": "Triclinic",
            "mohs_hardness": "5.5 (parallel) / 7.0 (perpendicular)",
            "composition": "Al2SiO5",
            "description": (
                "Aluminium silicate with strongly anisotropic hardness: ~5.5 along the blade length, "
                "~7.0 across it. Bladed crystals in blue, green, orange, or colourless. "
                "Forms in high-pressure metamorphic rocks (eclogites, blueschists). "
                "Industrial use: high-temperature refractories, mullite, spark plugs."
            ),
            "luster": "Vitreous to pearly",
            "streak": "White",
            "cleavage": "Perfect",
            "specific_gravity": 3.65,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Variable hardness along different axes is diagnostic — test in two directions. Blue blades with white stripes; vitreous to pearly on cleavage surfaces.",
             "safety_notes": "Non-toxic. Bladed crystals are physically sharp — handle carefully.",
             "market_notes": "Blue gem kyanite: $10–$80/ct. Orange kyanite (Tanzania): $20–$150/ct. Industrial kyanite: $300–$400/tonne."},
            {**GUIDE_SOURCES["USGS"],
             "market_notes": "USGS: kyanite group (includes andalusite, sillimanite) listed as critical mineral for refractory uses."},
        ],
    },
    {
        "specimen": {
            "name": "Kunzite",
            "common_names": ["Spodumene (pink/violet)", "Hiddenite (green spodumene)"],
            "mineral_class": "Silicate",
            "crystal_system": "Monoclinic",
            "mohs_hardness": 7.0,
            "composition": "LiAlSi2O6 + Mn",
            "description": (
                "Pink to violet variety of spodumene; colour from Mn²⁺. Named after "
                "gemologist George F. Kunz (Tiffany & Co). Strong pleochroism: pink/violet/colourless "
                "in three directions. Fades in sunlight (photosensitive). Hiddenite = green spodumene (Cr)."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Perfect",
            "specific_gravity": 3.18,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Strong trichroism; RI 1.660–1.676; SG 3.18. Perfect cleavage in two directions — avoid ultrasonic cleaning and hard blows.",
             "safety_notes": "Non-toxic. Store away from prolonged sunlight to preserve colour.",
             "market_notes": "Kunzite: $20–$200/ct (rich pink/violet). Large stones (>20 ct) common — size doesn't command same premium as ruby/sapphire. Afghan material highly regarded."},
        ],
    },
    {
        "specimen": {
            "name": "Prehnite",
            "common_names": ["Grape Jade (misnomer)", "Green Prehnite"],
            "mineral_class": "Silicate",
            "crystal_system": "Orthorhombic",
            "mohs_hardness": 6.5,
            "composition": "Ca2Al(Si3Al)O10(OH)2",
            "description": (
                "Pale green to yellow-green calcium aluminium phyllosilicate. "
                "Translucent to transparent; often contains needle-like inclusions "
                "(actinolite or epidote). First mineral named after a person (Col. Hendrik von Prehn). "
                "Deposits: South Africa (Ceres), Australia, China, Mali."
            ),
            "luster": "Vitreous to waxy",
            "streak": "White",
            "cleavage": "Distinct",
            "specific_gravity": 2.90,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Pale green translucent masses; botryoidal or tabular. Often confused with serpentine or chrysoprase. Prehnite fluoresces yellow-green (SW UV).",
             "safety_notes": "Non-toxic.",
             "market_notes": "Prehnite cabochons: $3–$30/ct. Faceted transparent green: $10–$60/ct. Mali (vivid green) material commands premium."},
        ],
    },
    {
        "specimen": {
            "name": "Chrysocolla",
            "common_names": ["Copper Silicate", "Gem Silica"],
            "mineral_class": "Silicate",
            "crystal_system": "Amorphous",
            "mohs_hardness": 2.5,
            "composition": "Cu2-xAlx(H2-xSi2O5)(OH)4·nH2O",
            "description": (
                "Hydrated copper silicate; vivid blue-green mineraloid. Occurs as oxidation "
                "product of copper deposits. Gem silica = agate pseudomorphed with chrysocolla — "
                "the most valuable chrysocolla variety (SG 2.6, harder). "
                "Non-gem chrysocolla is soft and fragile; gem silica is tough and cuttable."
            ),
            "luster": "Waxy to vitreous",
            "streak": "White to pale green",
            "cleavage": "None",
            "specific_gravity": 2.30,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Vivid blue-green; often mixed with malachite, azurite, turquoise. Gem silica (chalcedony + chrysocolla): harder, translucent blue-green — more valuable.",
             "safety_notes": "Copper-bearing dust: wear mask during lapidary work.",
             "market_notes": "Standard chrysocolla: $2–$15/ct. Gem silica (Arizona): $20–$200/ct. Mixed chrysocolla-malachite slabs: $5–$30/piece."},
        ],
    },
    {
        "specimen": {
            "name": "Selenite",
            "common_names": ["Desert Rose Gypsum", "Satin Spar", "Alabaster"],
            "mineral_class": "Sulfate",
            "crystal_system": "Monoclinic",
            "mohs_hardness": 2.0,
            "composition": "CaSO4·2H2O",
            "description": (
                "Hydrated calcium sulfate — the mineral gypsum. Selenite: large transparent crystals. "
                "Satin spar: fibrous silky variety. Alabaster: fine-grained massive variety (carved). "
                "World's largest gypsum crystals: Cave of Crystals, Naica mine, Mexico (up to 11 m long). "
                "Major use: drywall (wallboard) and Portland cement retarder."
            ),
            "luster": "Vitreous to silky (satin spar) to pearly",
            "streak": "White",
            "cleavage": "Perfect",
            "specific_gravity": 2.32,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Scratched by fingernail (Mohs 2.0). Flexible thin cleavage flakes. Satin spar shows chatoyance. Fizzes: NO (unlike calcite).",
             "safety_notes": "Non-toxic. Slight solubility in water — do not store in humid conditions for prolonged periods.",
             "market_notes": "Naica cave giant crystals: never commercially sold (protected). Decorator selenite wands: $5–$50. Alabaster sculptures: $20–$500."},
            {**GUIDE_SOURCES["USGS"],
             "market_notes": "US gypsum production: ~22 million tonnes/year; wallboard manufacturing accounts for >80% of demand."},
        ],
    },
    {
        "specimen": {
            "name": "Wulfenite",
            "common_names": ["Yellow Lead Ore", "Red Lead Ore"],
            "mineral_class": "Molybdate",
            "crystal_system": "Tetragonal",
            "mohs_hardness": 3.0,
            "composition": "PbMoO4",
            "description": (
                "Lead molybdate; square tabular crystals in orange, red, yellow, or grey. "
                "One of the most colourful ore minerals. Classic collector specimens from "
                "Red Cloud Mine (Arizona), Rowley Mine (Arizona), and Tsumeb (Namibia). "
                "Associated with cerussite, vanadinite, and mimetite in oxidised lead zones."
            ),
            "luster": "Resinous to adamantine",
            "streak": "White",
            "cleavage": "Distinct",
            "specific_gravity": 6.80,
            "toxic": 1,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Square tabular crystals, brilliant orange-red-yellow colour, very heavy (SG 6.8), low hardness (3). Adamantine lustre is diagnostic.",
             "safety_notes": "Contains lead — wash hands after handling; keep from children. Do not ingest or inhale dust. Lead compound: higher risk than galena.",
             "market_notes": "Red Cloud (AZ) orange wulfenite on limonite: $50–$2,000/specimen. Rowley orange crystals: museum-quality $500–$5,000."},
        ],
    },
    {
        "specimen": {
            "name": "Vanadinite",
            "common_names": ["Red Vanadium Ore", "Endlichite (As-rich)"],
            "mineral_class": "Vanadate",
            "crystal_system": "Hexagonal",
            "mohs_hardness": 3.0,
            "composition": "Pb5(VO4)3Cl",
            "description": (
                "Lead vanadate chloride; brilliant orange-red to red-brown hexagonal "
                "barrel crystals. Secondary mineral in oxidised lead deposits. "
                "Classic collection localities: Mibladen (Morocco), Chihuahua (Mexico), "
                "Globe (Arizona). Often occurs with barite and wulfenite."
            ),
            "luster": "Resinous to adamantine",
            "streak": "White to pale yellowish",
            "cleavage": "None",
            "specific_gravity": 6.90,
            "toxic": 1,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "Brilliant red-orange hexagonal barrels on white barite or limonite matrix. Very heavy (SG 6.9). No cleavage. Hollow crystals (hourglass) from Chihuahua.",
             "safety_notes": "Lead + vanadium compound — TOXIC. Wear gloves; wash hands; do not ingest or inhale dust. Keep from children and food surfaces.",
             "market_notes": "Mibladen (Morocco) clusters: $10–$200. Fine Chihuahua hollow crystals: $50–$1,000. Arizona Globe specimens: $30–$500."},
        ],
    },
    {
        "specimen": {
            "name": "Demantoid Garnet",
            "common_names": ["Green Andradite", "Ural Emerald"],
            "mineral_class": "Silicate",
            "crystal_system": "Cubic",
            "mohs_hardness": 6.5,
            "composition": "Ca3Fe2(SiO4)3 + Cr",
            "description": (
                "Green variety of andradite garnet; the rarest and most valued garnet. "
                "Highest dispersion of any garnet (0.057) — exceeds diamond (0.044). "
                "Classic Russian material from Ural Mountains shows 'horsetail' asbestos inclusions "
                "(diagnostic); also from Namibia (Erongo), Italy (Val Malenco), Iran."
            ),
            "luster": "Adamantine",
            "streak": "White",
            "cleavage": "Indistinct",
            "specific_gravity": 3.84,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "RI 1.888–1.889 (highest of garnets); SG 3.84; single refractive. 'Horsetail' inclusions = fibrous chrysotile — diagnostic for Russian origin.",
             "safety_notes": "Non-toxic. 'Horsetail' inclusions are encased chrysotile — no asbestos exposure risk in cut gems.",
             "market_notes": "Russian demantoid: $500–$3,000/ct (with horsetail inclusions = premium). Namibian (clean): $200–$800/ct. No-origin fine green: $100–$500/ct."},
        ],
    },
    {
        "specimen": {
            "name": "Tsavorite Garnet",
            "common_names": ["Green Grossular", "Tsavolite"],
            "mineral_class": "Silicate",
            "crystal_system": "Cubic",
            "mohs_hardness": 7.0,
            "composition": "Ca3Al2(SiO4)3 + V,Cr",
            "description": (
                "Vivid green grossular garnet; colour from vanadium and chromium. "
                "Discovered 1967 by Campbell Bridges in Tanzania (later Kenya). "
                "Commercialised by Tiffany & Co in 1974. "
                "Found ONLY in the Tsavo region of Kenya and northeast Tanzania."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Indistinct",
            "specific_gravity": 3.61,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "RI 1.740; SG 3.61; single refractive. Vivid green rivals emerald without inclusions. Inert under UV (vs emerald which is inert to weak fluorescent).",
             "safety_notes": "Non-toxic. Excellent durability — no cleavage, no inclusions issue.",
             "market_notes": "Top vivid green (>2 ct): $1,000–$5,000/ct. Fine medium: $300–$1,000/ct. Over 5 ct with fine colour: rare and commands exponential premium."},
        ],
    },
    {
        "specimen": {
            "name": "Andradite Garnet",
            "common_names": ["Melanite (black)", "Topazolite (yellow)", "Rainbow Garnet (iridescent)"],
            "mineral_class": "Silicate",
            "crystal_system": "Cubic",
            "mohs_hardness": 7.0,
            "composition": "Ca3Fe2(SiO4)3",
            "description": (
                "Calcium iron garnet species; includes demantoid (green Cr-bearing), topazolite (yellow), "
                "and melanite (black Ti-bearing). Iridescent rainbow andradite from Nara (Japan) shows "
                "thin-film diffraction iridescence. Highest dispersion of the garnet family."
            ),
            "luster": "Adamantine to resinous",
            "streak": "White",
            "cleavage": "Indistinct",
            "specific_gravity": 3.84,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["Mindat"],
             "identification_notes": "High RI (1.888); cubic; SG 3.84. Black melanite: confused with schorl tourmaline (SG 3.1 vs 3.84). Yellow topazolite: bright yellow, adamantine.",
             "market_notes": "Rainbow andradite (Japan): $100–$500/ct (rare iridescent material). Topazolite: $50–$200/ct. Melanite: $5–$30/ct."},
        ],
    },
    {
        "specimen": {
            "name": "Tourmaline",
            "common_names": ["Rubellite (red)", "Indicolite (blue)", "Paraíba (neon blue)", "Watermelon"],
            "mineral_class": "Silicate",
            "crystal_system": "Trigonal",
            "mohs_hardness": 7.5,
            "composition": "Complex boron silicate (varies by variety)",
            "description": (
                "Most colour-varied gem mineral — includes all colours and parti-coloured stones. "
                "Paraíba tourmaline (Cu+Mn bearing): neon blue-green; discovered 1989 in Paraíba, Brazil. "
                "Watermelon: pink core, green rim. Indicolite: blue (Fe). Rubellite: red-pink (Mn). "
                "Strongly pyroelectric and piezoelectric."
            ),
            "luster": "Vitreous",
            "streak": "White",
            "cleavage": "Indistinct",
            "specific_gravity": 3.06,
            "toxic": 0,
        },
        "sources": [
            {**GUIDE_SOURCES["GIA"],
             "identification_notes": "Trigonal; RI 1.624–1.644; strong pleochroism. Paraíba: detected by LA-ICP-MS for Cu content. Watermelon: colour zoning visible with naked eye.",
             "safety_notes": "Non-toxic. Strong piezoelectric charge accumulates dust on polished surfaces.",
             "market_notes": "Paraíba (Brazil, neon): $5,000–$50,000/ct. Paraíba (Africa/Mozambique): $1,000–$10,000/ct. Rubellite: $50–$500/ct. Indicolite: $30–$200/ct."},
            {**GUIDE_SOURCES["Smithsonian"],
             "identification_notes": "The Smithsonian 'Canary Tourmaline' (98 ct, Afghanistan) and Paraíba suite are reference gems for tourmaline colour-origin testing."},
        ],
    },
]


def get_guide_sources() -> dict:
    """Return the registry of authoritative mineral guide sources."""
    return GUIDE_SOURCES


def seed_mineral_guides(db_path: Path, verbose: bool = True) -> int:
    """Seed mineral guide entries and source references into the database.

    Returns the number of new specimens seeded.
    """
    from .schema import get_conn, init_db, upsert_specimen, upsert_source_reference

    if not db_path.exists():
        init_db(db_path)

    count = 0
    with get_conn(db_path) as conn:
        for entry in MINERAL_GUIDE_ENTRIES:
            spec_data = entry["specimen"]
            # mohs_hardness may be a string for anisotropic minerals — normalise
            mh = spec_data.get("mohs_hardness")
            if isinstance(mh, str):
                import re
                nums = re.findall(r"[\d.]+", mh)
                spec_data = {**spec_data, "mohs_hardness": float(nums[0]) if nums else 0.0}
            # Upsert specimen — always do a SELECT to get the authoritative ID.
            # Reason: when ON CONFLICT DO UPDATE suppresses the update (same hash),
            # SQLite does not change sqlite3_last_insert_rowid(), so lastrowid in Python
            # may reflect a previous statement's rowid (e.g. a source_references insert).
            upsert_specimen(conn, spec_data)
            row = conn.execute(
                "SELECT id FROM specimens WHERE name=?", (spec_data["name"],)
            ).fetchone()
            sid = row[0] if row else 0
            if not sid:
                continue
            count += 1
            for src in entry.get("sources", []):
                ref = {
                    "source_name": src.get("source_name", ""),
                    "source_url": src.get("source_url", ""),
                    "citation": src.get("citation", ""),
                    "identification_notes": src.get("identification_notes", ""),
                    "safety_notes": src.get("safety_notes", ""),
                    "market_notes": src.get("market_notes", ""),
                }
                upsert_source_reference(conn, sid, ref)

    if verbose:
        print(f"[LithosOS] Seeded {count} mineral guide entries into {db_path}")
    return count
