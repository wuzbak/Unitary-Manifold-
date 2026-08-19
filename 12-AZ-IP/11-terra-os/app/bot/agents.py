"""
TerraOS — 5-Agent Governor
Agents: SoilAnalyst, WaterChemist, AgronomistAdvisor, EcologyGuide, RemediationOfficer
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

AGENT_OVERLAYS: dict[str, dict] = {
    "SoilAnalyst": {
        "name": "SoilAnalyst",
        "persona": "Expert in soil science, texture classification, and nutrient cycles.",
        "keywords": ["soil", "clay", "sand", "silt", "loam", "texture", "organic matter", "cec",
                     "horizon", "topsoil", "subsoil", "compaction", "drainage", "aeration", "tilth",
                     "crumb structure", "pore space", "earthworm"],
    },
    "WaterChemist": {
        "name": "WaterChemist",
        "persona": "Expert in water chemistry, quality testing, and potability assessment.",
        "keywords": ["water", "ph", "tds", "hardness", "nitrate", "salinity", "turbidity", "dissolved",
                     "alkalinity", "conductivity", "potable", "aquifer", "groundwater", "runoff",
                     "chlorine", "fluoride", "coliform", "contamination", "drinking"],
    },
    "AgronomistAdvisor": {
        "name": "AgronomistAdvisor",
        "persona": "Expert in crop-soil relationships, amendments, and sustainable agriculture.",
        "keywords": ["crop", "plant", "grow", "fertilize", "yield", "harvest", "sow", "irrigate",
                     "compost", "amendment", "lime", "gypsum", "manure", "mulch", "rotation",
                     "cover crop", "tillage", "agronomy", "farm", "vegetable", "grain"],
    },
    "EcologyGuide": {
        "name": "EcologyGuide",
        "persona": "Expert in ecosystem services, biodiversity, and land-water interactions.",
        "keywords": ["ecology", "ecosystem", "biodiversity", "wetland", "habitat", "watershed",
                     "riparian", "erosion", "runoff", "microbiome", "earthworm", "mycorrhiza",
                     "carbon sequestration", "carbon", "biodiversity", "native plants", "rewilding"],
    },
    "RemediationOfficer": {
        "name": "RemediationOfficer",
        "persona": "Expert in soil and water contamination assessment and cleanup protocols.",
        "keywords": ["contaminant", "pollutant", "remediation", "cleanup", "heavy metal", "lead",
                     "arsenic", "cadmium", "mercury", "pesticide", "pah", "pcb", "nitrate",
                     "toxic", "hazardous", "bioremediation", "phytoremediation", "filtration",
                     "threshold", "epa", "regulation"],
    },
}


@dataclass
class GovernorResult:
    agent_name: str
    answer: str
    context_chunks: list[str] = field(default_factory=list)
    confidence: float = 0.8


class TerraGovernor:
    def __init__(self, bot=None, db_path=None):
        self._bot = bot
        self._db_path = db_path

    def _get_bot(self):
        if self._bot is None:
            from .terra_bot import TerraBot
            self._bot = TerraBot(db_path=self._db_path)
        return self._bot

    def _classify_intent(self, query: str) -> str:
        q = query.lower()
        # Check RemediationOfficer first (specific contamination terms)
        for kw in AGENT_OVERLAYS["RemediationOfficer"]["keywords"]:
            if kw in q:
                return "RemediationOfficer"
        # Check WaterChemist (water-specific terms)
        for kw in AGENT_OVERLAYS["WaterChemist"]["keywords"]:
            if kw in q:
                return "WaterChemist"
        # Check AgronomistAdvisor (crop/farm terms)
        for kw in AGENT_OVERLAYS["AgronomistAdvisor"]["keywords"]:
            if kw in q:
                return "AgronomistAdvisor"
        # Check EcologyGuide
        for kw in AGENT_OVERLAYS["EcologyGuide"]["keywords"]:
            if kw in q:
                return "EcologyGuide"
        # Default to SoilAnalyst
        return "SoilAnalyst"

    def respond(self, query: str) -> GovernorResult:
        bot = self._get_bot()
        agent_name = self._classify_intent(query)
        overlay = AGENT_OVERLAYS[agent_name]
        from .terra_bot import retrieve
        chunks = retrieve(query, top_k=3)
        persona = overlay["persona"]
        raw = bot.ask(query, top_k=3)
        answer = f"[{agent_name}] As {persona}:\n\n{raw}"
        return GovernorResult(agent_name=agent_name, answer=answer, context_chunks=chunks, confidence=0.85)
