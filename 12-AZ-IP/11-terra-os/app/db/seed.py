"""
TerraOS — Database Seed Data
"""
from __future__ import annotations
from pathlib import Path

SOIL_SEED = [
    {"name": "Clay Soil", "type": "clay", "description": "Heavy soil with very fine particles; high water retention, poor drainage.", "ph_min": 5.5, "ph_max": 7.0, "texture": "fine", "organic_matter_pct": 2.0, "cec": 35.0, "typical_crops": ["rice", "wheat", "soybeans"], "native_region": "River deltas, floodplains", "drainage": "poor"},
    {"name": "Sandy Loam", "type": "loam", "description": "Ideal agricultural soil with balanced sand, silt, and clay.", "ph_min": 6.0, "ph_max": 7.0, "texture": "medium", "organic_matter_pct": 3.5, "cec": 15.0, "typical_crops": ["corn", "vegetables", "fruit trees"], "native_region": "Temperate regions", "drainage": "good"},
    {"name": "Sandy Soil", "type": "sandy", "description": "Coarse-grained soil with rapid drainage and low nutrient retention.", "ph_min": 5.0, "ph_max": 7.5, "texture": "coarse", "organic_matter_pct": 1.0, "cec": 5.0, "typical_crops": ["root vegetables", "melons", "groundnuts"], "native_region": "Coastal areas, deserts", "drainage": "excellent"},
    {"name": "Silt Soil", "type": "silt", "description": "Fine-grained soil with moderate fertility; prone to compaction.", "ph_min": 6.0, "ph_max": 7.0, "texture": "fine-medium", "organic_matter_pct": 2.5, "cec": 20.0, "typical_crops": ["wheat", "barley", "sugar beet"], "native_region": "River valleys, floodplains", "drainage": "moderate"},
    {"name": "Peat Soil", "type": "peat", "description": "High organic matter, acidic soil from decomposed plant material.", "ph_min": 3.5, "ph_max": 6.5, "texture": "spongy", "organic_matter_pct": 50.0, "cec": 100.0, "typical_crops": ["blueberries", "cranberries", "ornamentals"], "native_region": "Bogs, wetlands", "drainage": "very poor"},
    {"name": "Laterite", "type": "laterite", "description": "Tropical weathered soil rich in iron and aluminum oxides.", "ph_min": 4.5, "ph_max": 6.5, "texture": "variable", "organic_matter_pct": 1.0, "cec": 8.0, "typical_crops": ["cassava", "sweet potato", "yam"], "native_region": "Tropical regions", "drainage": "moderate to good"},
    {"name": "Chernozem", "type": "chernozem", "description": "Black earth; one of the most fertile soils with deep topsoil.", "ph_min": 6.0, "ph_max": 7.5, "texture": "loamy", "organic_matter_pct": 8.0, "cec": 40.0, "typical_crops": ["wheat", "sunflowers", "corn"], "native_region": "Eurasian steppes, North American prairies", "drainage": "good"},
    {"name": "Caliche", "type": "caliche", "description": "Calcium carbonate-cemented soil layer common in arid regions.", "ph_min": 7.5, "ph_max": 9.0, "texture": "variable", "organic_matter_pct": 0.5, "cec": 10.0, "typical_crops": ["drought-tolerant shrubs", "cacti"], "native_region": "Desert southwest USA, Mediterranean", "drainage": "poor"},
    {"name": "Volcanic Soil", "type": "volcanic", "description": "Andisol from volcanic ash; very fertile with high water retention.", "ph_min": 5.0, "ph_max": 7.0, "texture": "variable", "organic_matter_pct": 5.0, "cec": 30.0, "typical_crops": ["coffee", "cocoa", "tropical fruits"], "native_region": "Volcanic islands, ring of fire", "drainage": "good"},
    {"name": "Permafrost", "type": "permafrost", "description": "Permanently frozen subsoil; thin active layer supports only hardy plants.", "ph_min": 4.0, "ph_max": 6.5, "texture": "variable", "organic_matter_pct": 20.0, "cec": 15.0, "typical_crops": ["lichens", "mosses", "tundra grasses"], "native_region": "Arctic, sub-Arctic", "drainage": "very poor"},
    {"name": "Chalky Soil", "type": "chalky", "description": "Alkaline calcium carbonate-rich soil with poor nutrient availability.", "ph_min": 7.5, "ph_max": 8.5, "texture": "medium", "organic_matter_pct": 1.5, "cec": 12.0, "typical_crops": ["lavender", "asparagus", "brassicas"], "native_region": "Limestone regions, chalk downs", "drainage": "excellent"},
    {"name": "Saline Soil", "type": "saline", "description": "High soluble salt content inhibiting plant water uptake.", "ph_min": 7.5, "ph_max": 9.5, "texture": "variable", "organic_matter_pct": 0.5, "cec": 8.0, "typical_crops": ["salt-tolerant halophytes", "date palms"], "native_region": "Coastal areas, irrigated drylands", "drainage": "variable"},
    {"name": "Alluvial Soil", "type": "alluvial", "description": "Deposited by rivers; highly fertile with layered texture.", "ph_min": 6.0, "ph_max": 7.5, "texture": "loamy", "organic_matter_pct": 3.0, "cec": 20.0, "typical_crops": ["rice", "jute", "sugarcane"], "native_region": "River plains worldwide", "drainage": "moderate"},
    {"name": "Podzol", "type": "podzol", "description": "Acidic soil with leached gray eluvial horizon; low fertility.", "ph_min": 3.5, "ph_max": 5.5, "texture": "sandy to loamy", "organic_matter_pct": 4.0, "cec": 10.0, "typical_crops": ["conifers", "heather", "blueberries"], "native_region": "Boreal forests, northern Europe", "drainage": "good"},
    {"name": "Rendzina", "type": "rendzina", "description": "Shallow soil over limestone; rich in organic matter.", "ph_min": 6.5, "ph_max": 8.5, "texture": "clayey", "organic_matter_pct": 5.0, "cec": 30.0, "typical_crops": ["orchids", "herbs", "vines"], "native_region": "Limestone uplands, Mediterranean", "drainage": "good"},
]

WATER_SEED = [
    {"name": "Well Water", "source_type": "groundwater", "description": "Deep well groundwater; mineral-rich but may contain nitrates.", "ph_typical": 7.2, "tds_ppm": 450, "hardness_ppm": 200, "nitrate_ppm": 5.0, "dissolved_o2_ppm": 3.0, "potable": 1},
    {"name": "Municipal Tap Water", "source_type": "municipal", "description": "Treated city water; chlorinated and pH-adjusted.", "ph_typical": 7.5, "tds_ppm": 250, "hardness_ppm": 120, "nitrate_ppm": 2.0, "dissolved_o2_ppm": 8.0, "potable": 1},
    {"name": "Rainwater", "source_type": "precipitation", "description": "Soft, slightly acidic water with minimal minerals.", "ph_typical": 5.8, "tds_ppm": 10, "hardness_ppm": 5, "nitrate_ppm": 0.5, "dissolved_o2_ppm": 9.0, "potable": 1},
    {"name": "Greywater", "source_type": "recycled", "description": "Domestic wastewater from sinks/showers; not for drinking.", "ph_typical": 7.0, "tds_ppm": 600, "hardness_ppm": 150, "nitrate_ppm": 15.0, "dissolved_o2_ppm": 2.0, "potable": 0},
    {"name": "River Water", "source_type": "surface", "description": "Natural flowing water; quality varies by watershed.", "ph_typical": 7.0, "tds_ppm": 180, "hardness_ppm": 80, "nitrate_ppm": 8.0, "dissolved_o2_ppm": 7.0, "potable": 0},
    {"name": "Irrigation Canal Water", "source_type": "irrigation", "description": "Agricultural irrigation water; may contain agrochemicals.", "ph_typical": 7.2, "tds_ppm": 350, "hardness_ppm": 150, "nitrate_ppm": 20.0, "dissolved_o2_ppm": 5.0, "potable": 0},
    {"name": "Brackish Water", "source_type": "brackish", "description": "Saltier than freshwater but less than seawater; coastal zones.", "ph_typical": 7.5, "tds_ppm": 8000, "hardness_ppm": 1000, "nitrate_ppm": 3.0, "dissolved_o2_ppm": 6.0, "potable": 0},
    {"name": "Acidic Mine Water", "source_type": "acid_mine_drainage", "description": "Highly acidic runoff from mining operations; toxic metals.", "ph_typical": 2.5, "tds_ppm": 5000, "hardness_ppm": 500, "nitrate_ppm": 1.0, "dissolved_o2_ppm": 1.0, "potable": 0, "contaminants": ["iron", "arsenic", "sulfate"]},
    {"name": "Alkaline Spring Water", "source_type": "spring", "description": "High-pH spring water from limestone geology.", "ph_typical": 8.8, "tds_ppm": 300, "hardness_ppm": 250, "nitrate_ppm": 1.0, "dissolved_o2_ppm": 7.0, "potable": 1},
    {"name": "Contaminated Runoff", "source_type": "runoff", "description": "Agricultural runoff with nitrates, pesticides, sediment.", "ph_typical": 6.5, "tds_ppm": 800, "hardness_ppm": 100, "nitrate_ppm": 50.0, "dissolved_o2_ppm": 3.0, "potable": 0, "contaminants": ["nitrates", "pesticides", "coliform"]},
]

AMENDMENT_SEED = [
    {"name": "Compost", "type": "organic", "description": "Decomposed organic matter; improves structure and nutrition.", "application_rate": "5-10 cm layer or 100-200 kg/100m2", "ph_effect": "neutral to slightly alkaline", "nutrient_content": {"N": "1-2%", "P": "0.5-1%", "K": "0.5-1.5%"}},
    {"name": "Agricultural Lime", "type": "mineral", "description": "Calcium carbonate; raises pH of acid soils.", "application_rate": "1-4 tonnes/hectare", "ph_effect": "raises pH", "nutrient_content": {"Ca": "38%"}},
    {"name": "Sulfur", "type": "mineral", "description": "Elemental sulfur; lowers pH of alkaline soils.", "application_rate": "200-500 kg/hectare", "ph_effect": "lowers pH", "nutrient_content": {"S": "99%"}},
    {"name": "Gypsum", "type": "mineral", "description": "Calcium sulfate; improves clay soil structure without affecting pH.", "application_rate": "1-2 tonnes/hectare", "ph_effect": "neutral", "nutrient_content": {"Ca": "23%", "S": "18%"}},
    {"name": "Biochar", "type": "organic", "description": "Charcoal-like material; long-term soil carbon sequestration.", "application_rate": "5-20 tonnes/hectare", "ph_effect": "slightly alkaline", "nutrient_content": {"C": "70-90%"}},
    {"name": "Rock Phosphate", "type": "mineral", "description": "Slow-release phosphorus source for acidic soils.", "application_rate": "200-600 kg/hectare", "ph_effect": "neutral", "nutrient_content": {"P2O5": "25-35%"}},
    {"name": "Kelp Meal", "type": "organic", "description": "Seaweed-derived amendment rich in micronutrients and growth hormones.", "application_rate": "50-200 kg/hectare", "ph_effect": "slightly alkaline", "nutrient_content": {"N": "1%", "K": "2%"}},
    {"name": "Worm Castings", "type": "organic", "description": "Vermicompost; high in plant-available nutrients and beneficial bacteria.", "application_rate": "10-20% soil volume", "ph_effect": "neutral", "nutrient_content": {"N": "2%", "P": "1%", "K": "1%"}},
    {"name": "Perlite", "type": "mineral", "description": "Volcanic glass; improves drainage and aeration in potting mixes.", "application_rate": "10-30% of mix volume", "ph_effect": "neutral", "nutrient_content": {}},
    {"name": "Vermiculite", "type": "mineral", "description": "Expanded mica; retains moisture and improves cation exchange.", "application_rate": "10-20% of mix volume", "ph_effect": "slightly alkaline", "nutrient_content": {"Ca": "trace", "Mg": "trace"}},
]

REMEDIATION_SEED = [
    {"name": "Phytoremediation with Sunflowers", "method": "phytoremediation", "description": "Sunflowers (Helianthus annuus) extract heavy metals including lead and cesium.", "duration_months": 24, "effectiveness_pct": 60.0, "cost_estimate": "Low — seed + harvest"},
    {"name": "Activated Carbon Filtration", "method": "filtration", "description": "Granular activated carbon removes organic contaminants and chlorine from water.", "duration_months": 1, "effectiveness_pct": 95.0, "cost_estimate": "Medium — equipment + media"},
    {"name": "Lime Stabilization", "method": "chemical", "description": "Adding lime to immobilize heavy metals and reduce pathogen activity in soil.", "duration_months": 3, "effectiveness_pct": 70.0, "cost_estimate": "Low — bulk lime application"},
    {"name": "Bioremediation with Mycorrhizae", "method": "bioremediation", "description": "Mycorrhizal fungi degrade petroleum hydrocarbons and improve soil structure.", "duration_months": 18, "effectiveness_pct": 75.0, "cost_estimate": "Low-medium — inoculant + time"},
    {"name": "Reverse Osmosis Water Treatment", "method": "membrane_filtration", "description": "RO membrane removes dissolved salts, nitrates, and heavy metals from water.", "duration_months": 0, "effectiveness_pct": 99.0, "cost_estimate": "High — membrane system"},
    {"name": "Constructed Wetland", "method": "natural_treatment", "description": "Engineered wetland using reeds and cattails to filter wastewater and runoff.", "duration_months": 6, "effectiveness_pct": 80.0, "cost_estimate": "Medium — construction + plants"},
]

def seed_database(db_path: Path, verbose: bool = True) -> None:
    from .schema import get_conn, upsert_soil_profile, upsert_water_sample, upsert_amendment
    with get_conn(db_path) as conn:
        for item in SOIL_SEED:
            upsert_soil_profile(conn, item)
        for item in WATER_SEED:
            upsert_water_sample(conn, item)
        for item in AMENDMENT_SEED:
            upsert_amendment(conn, item)
        for item in REMEDIATION_SEED:
            conn.execute("""
                INSERT OR IGNORE INTO remediation_plans
                    (name, method, description, duration_months, effectiveness_pct, cost_estimate, version_hash, updated_at)
                VALUES (?,?,?,?,?,?,'',datetime('now'))
            """, (item["name"], item["method"], item["description"],
                  item.get("duration_months", 0), item.get("effectiveness_pct", 0),
                  item.get("cost_estimate", "")))
    if verbose:
        print(f"[TerraOS] Seeded {len(SOIL_SEED)} soil profiles, {len(WATER_SEED)} water samples, {len(AMENDMENT_SEED)} amendments")

if __name__ == "__main__":
    import sys
    db = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/terra.db")
    seed_database(db)
