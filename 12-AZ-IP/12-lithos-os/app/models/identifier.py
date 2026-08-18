"""
LithosOS — Mineral/Gemstone Identifier
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class SpecimenCandidate:
    name: str
    common_names: list[str]
    confidence: float
    confidence_label: str
    mineral_class: str = ""
    description: str = ""
    source: str = "unknown"

@dataclass
class SpecimenResult:
    candidates: list[SpecimenCandidate]
    top: Optional[SpecimenCandidate] = None
    raw_response: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.candidates and not self.top:
            self.top = self.candidates[0]

    def summary(self) -> str:
        if not self.candidates:
            return "No candidates found."
        top = self.candidates[0]
        label = f"{top.name} ({top.confidence_label}, {top.confidence:.0%})"
        if len(self.candidates) > 1:
            others = ", ".join(c.name for c in self.candidates[1:3])
            label += f"; also possible: {others}"
        return label


_KEYWORD_MAP = [
    (["shiny yellow", "fool's gold", "pyrite", "cubic iron sulfide"], "Pyrite", ["Fool's Gold", "Iron Pyrite"], 0.75, "Sulfide"),
    (["gold", "metallic yellow", "native gold", "nugget"], "Gold", ["Native Gold", "Au"], 0.70, "Native Element"),
    (["purple", "violet quartz", "amethyst"], "Amethyst", ["Purple Quartz"], 0.65, "Silicate"),
    (["green blue", "malachite", "banded green"], "Malachite", ["Green Copper Carbonate"], 0.65, "Carbonate"),
    (["clear hexagonal", "rock crystal", "quartz", "silica"], "Quartz", ["Rock Crystal", "Silica"], 0.65, "Silicate"),
    (["blue green", "turquoise", "waxy blue"], "Turquoise", ["Persian Turquoise"], 0.60, "Phosphate"),
    (["deep blue", "lapis", "azure stone"], "Lapis Lazuli", ["Lapis", "Azure Stone"], 0.60, "Rock"),
    (["red garnet", "almandine", "dark red"], "Garnet", ["Almandine", "Red Garnet"], 0.60, "Silicate"),
    (["metallic silver", "native silver", "silver wire"], "Silver", ["Native Silver", "Ag"], 0.65, "Native Element"),
    (["red streak", "iron ore", "hematite"], "Hematite", ["Iron Ore", "Blood Stone"], 0.65, "Oxide"),
    (["pink quartz", "rose quartz", "pink crystal"], "Rose Quartz", ["Pink Quartz"], 0.60, "Silicate"),
    (["diamond", "hardest", "adamantine", "octahedral carbon"], "Diamond", ["Brilliant", "Rock"], 0.70, "Native Element"),
    (["copper", "reddish metal", "native copper"], "Copper", ["Native Copper", "Cu"], 0.65, "Native Element"),
    (["blue copper", "azurite", "dark blue carbonate"], "Azurite", ["Blue Copper Carbonate"], 0.60, "Carbonate"),
    (["green beryl", "emerald", "chrome green"], "Emerald", ["Green Beryl"], 0.65, "Silicate"),
]


class MindatIdentifier:
    def __init__(self, mindat_api_key: str = "", inaturalist_token: str = "",
                 local_model_path: Path | None = None):
        self._mindat_key = mindat_api_key
        self._inat_token = inaturalist_token
        self._model_path = local_model_path

    def identify_from_bytes(self, image_bytes: bytes) -> SpecimenResult:
        return SpecimenResult(candidates=[SpecimenCandidate(
            name="Unknown — offline mode",
            common_names=["No image model available"],
            confidence=0.0,
            confidence_label="Low",
            description="Provide a text description for analysis",
            source="offline_stub",
        )])

    def identify_from_description(self, description: str) -> SpecimenResult:
        desc_lower = description.lower()
        candidates = []
        for keywords, name, common, confidence, mineral_class in _KEYWORD_MAP:
            if any(kw in desc_lower for kw in keywords):
                label = "High" if confidence >= 0.7 else "Medium" if confidence >= 0.55 else "Low"
                candidates.append(SpecimenCandidate(
                    name=name,
                    common_names=common,
                    confidence=confidence,
                    confidence_label=label,
                    mineral_class=mineral_class,
                    description=f"Matched keywords in description",
                    source="keyword_match",
                ))
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        if not candidates:
            candidates = [SpecimenCandidate(
                name="Unknown",
                common_names=["Unidentified specimen"],
                confidence=0.1,
                confidence_label="Low",
                description="No keyword matches found. Provide more diagnostic features.",
                source="offline_stub",
            )]
        return SpecimenResult(candidates=candidates[:5])
