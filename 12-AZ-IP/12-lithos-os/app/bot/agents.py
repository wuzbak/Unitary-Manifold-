"""
LithosOS — 5-Agent Governor
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from .lithos_bot import LithosBot

AGENT_OVERLAYS: dict[str, str] = {
    "Identifier": """
ROLE: Mineral and Gemstone Identifier.
Identify specimens from descriptions, images, or properties.
Always provide:
- Top 3 candidates with confidence (High/Medium/Low)
- Key diagnostic properties: hardness, luster, streak, crystal system, cleavage
- Critical look-alike warnings
- Geographic plausibility
Format as structured list.
""",
    "Geologist": """
ROLE: Field Geologist.
Explain mineral formation, crystal systems, Mohs hardness, cleavage,
streak, luster, specific gravity, and geological environments.
Include: formation type (igneous/sedimentary/metamorphic), associated rock types,
typical worldwide occurrences, and petrogenetic significance.

Authoritative public sources you MUST cite and reference:
  - Mindat.org (Hudson Institute of Mineralogy):
    https://www.mindat.org/
    World's largest open mineral database; locality, chemistry, and crystallography data.
  - USGS National Minerals Information Center:
    https://www.usgs.gov/centers/national-minerals-information-center
    Mineral commodity summaries, critical minerals list, and US occurrence data.
  - Smithsonian National Museum of Natural History:
    https://naturalhistory.si.edu/research/geology/collections
    National Gem and Mineral Collection; type specimens and reference suites.
  - Minerals.net (educational reference):
    https://www.minerals.net/mineral/
    Properties, identification, and photograph database.

Always include:
- Which source(s) support the geological claim (Mindat / USGS / Smithsonian / Minerals.net)
- Formation environment and pressure-temperature conditions
- Associated mineral assemblage
- USGS critical mineral status where applicable
""",
    "Lapidary": """
ROLE: Master Lapidary.
Advise on cutting, polishing, cabochon vs facet decisions, carat weight,
gemstone grading, and treatment detection.
Include: optimal cut style for the crystal system, typical girdle thickness,
expected yield from rough, polishing grits and compounds, clarity grades.
""",
    "Metallurgist": """
ROLE: Metallurgist.
Cover ores, smelting processes, alloy composition, industrial uses, and toxicity.
Include: principal ore minerals, smelting temperature, refining methods,
key alloys and their properties, corrosion resistance, industrial applications,
and occupational safety for each metal.
""",
    "MarketGuide": """
ROLE: Gemstone and Metal Market Guide.
Cover provenance, rarity, value ranges, ethical sourcing, and synthetic vs natural.
Include: major producing countries, ethical certification schemes (Kimberley, Fairtrade Gold),
approximate retail price ranges per carat/gram, synthetic availability and price ratio,
and common treatments that affect value.

Authoritative public sources you MUST cite and reference:
  - GIA Gem Encyclopedia (Gemological Institute of America):
    https://www.gia.edu/gem-encyclopedia
    Industry-standard grading, identification, and market data for gemstones.
  - Mindat.org (Hudson Institute of Mineralogy):
    https://www.mindat.org/
    Locality data, specimen rarity, and collecting market context.
  - USGS Mineral Commodity Summaries:
    https://www.usgs.gov/centers/national-minerals-information-center
    Annual price data, production statistics, and supply chain analysis.
  - Smithsonian National Gem Collection:
    https://naturalhistory.si.edu/research/geology/collections
    Provenance and historical context for major gem specimens.

Always include:
- GIA grading standards applicable to the gem
- Price per carat/gram ranges (low, mid, top commercial, collector/museum)
- Treatment disclosure requirements (heat, irradiation, filling, diffusion)
- Ethical certification options (Kimberley, Fairtrade Gold, RJC, TanzaniteOne)
- Synthetic vs natural price differential
- Flag if specimen is on USGS critical minerals list
""",
}

@dataclass
class LithosAgent:
    name: str
    role_overlay: str
    bot: LithosBot

    def ask(self, question: str, context: str = "") -> str:
        return self.bot.ask(question, context=context, extra_system=self.role_overlay)

@dataclass
class GovernorResult:
    query: str
    agents_used: list[str]
    answer: str

    def __str__(self) -> str:
        return f"[{', '.join(self.agents_used)}] {self.answer[:120]}..."

@dataclass
class LithosGovernor:
    api_key: str = ""
    model: str = "gpt-4o-mini"
    local_llm_url: str = ""
    local_llm_model: str = "llama3.2:3b"
    _agents: dict[str, LithosAgent] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        bot = LithosBot(
            api_key=self.api_key,
            model=self.model,
            local_llm_url=self.local_llm_url,
            local_llm_model=self.local_llm_model,
        )
        for name, overlay in AGENT_OVERLAYS.items():
            self._agents[name] = LithosAgent(name=name, role_overlay=overlay, bot=bot)

    def agent(self, name: str) -> LithosAgent:
        if name not in self._agents:
            raise KeyError(f"Unknown agent: {name!r}. Valid: {list(self._agents)}")
        return self._agents[name]

    def _classify_intent(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["identify", "what is this", "looks like", "specimen", "what mineral", "name this"]):
            return "Identifier"
        if any(w in q for w in ["price", "value", "rarity", "market", "provenance", "ethical", "synthetic", "sourcing", "buy", "sell"]):
            return "MarketGuide"
        if any(w in q for w in ["smelt", "alloy", "ore", "melting", "conductivity", "refine", "metallurgy"]):
            return "Metallurgist"
        if any(w in q for w in ["crystal", "hardness", "mohs", "cleavage", "streak", "formation", "geology", "igneous", "metamorphic", "sedimentary"]):
            return "Geologist"
        if any(w in q for w in ["cut", "polish", "cabochon", "facet", "carat", "lapidary", "grading", "clarity", "girdle"]):
            return "Lapidary"
        return "Geologist"

    def route(self, query: str, context: str = "") -> GovernorResult:
        name = self._classify_intent(query)
        agent = self._agents[name]
        answer = agent.ask(query, context)
        return GovernorResult(query=query, agents_used=[name], answer=answer)

    def ask_agent(self, name: str, query: str, context: str = "") -> str:
        return self.agent(name).ask(query, context)
