"""
TerraOS — TF-IDF RAG Bot
"""
from __future__ import annotations
import math
import re
from pathlib import Path

TERRA_DIR = Path(__file__).resolve().parents[3]
DOCS_DIR = TERRA_DIR / "docs"

TERRA_DOCS_ORDERED = [
    "SOIL_TEXTURE_TRIANGLE.md",
    "PH_GUIDE.md",
    "WATER_QUALITY_STANDARDS.md",
    "AMENDMENT_LIBRARY.md",
    "CONTAMINANT_DATABASE.md",
    "REMEDIATION_PROTOCOLS.md",
    "CROP_SUITABILITY.md",
]

BUILT_IN_DOCS: dict[str, str] = {
    "SOIL_TEXTURE_TRIANGLE.md": """
# Soil Texture Triangle
Soil texture is determined by the percentages of sand, silt, and clay particles.
- **Sandy** soils: >70% sand — drains fast, poor nutrients
- **Clay** soils: >40% clay — slow drainage, high CEC
- **Loam**: balanced mix — ideal for most crops
- **Silt loam**: fine particles, erosion prone
- Texture determines water retention, aeration, and workability.
""",
    "PH_GUIDE.md": """
# Soil and Water pH Guide
pH measures acidity/alkalinity on 0–14 scale.
## Soil pH
- pH < 6: acidic — aluminum/manganese toxicity, phosphorus lock-up
- pH 6–7: optimal for most vegetables, grains, and grasses
- pH > 7.5: alkaline — iron, manganese, zinc become unavailable
- Raise pH: add agricultural lime or wood ash
- Lower pH: add sulfur, acidifying fertilizers, or organic mulch
## Water pH
- Drinking water ideal: 6.5–8.5
- Irrigation optimal: 6.5–7.5
- Acidic mine drainage: pH < 4, harmful to ecosystems
""",
    "WATER_QUALITY_STANDARDS.md": """
# Water Quality Standards
## WHO Drinking Water Guidelines
- TDS < 500 ppm preferred (<1000 ppm acceptable)
- Nitrate < 50 mg/L (WHO), < 10 mg/L (US EPA MCL)
- pH: 6.5–8.5
- Hardness < 500 mg/L (CaCO3)
## Irrigation Water Quality
- EC < 0.7 mS/cm (low risk), 0.7–3 moderate, >3 high risk
- SAR (sodium adsorption ratio) < 6 safe, >18 high risk
- Nitrates < 30 mg/L preferred
## Contaminants
- Heavy metals: lead <10 ppb, arsenic <10 ppb, mercury <1 ppb
- Pesticides: atrazine <3 ppb, glyphosate <700 ppb
""",
    "AMENDMENT_LIBRARY.md": """
# Soil Amendment Library
## Organic Amendments
- **Compost**: 5–10 cm layer; balanced NPK, improves structure
- **Biochar**: 5–20 t/ha; long-term carbon sequestration
- **Worm Castings**: rich in plant-available nutrients and microbes
- **Kelp Meal**: trace elements, natural hormones
## Mineral Amendments
- **Agricultural Lime**: raises pH; 1–4 t/ha
- **Gypsum**: improves clay structure, neutral pH effect
- **Sulfur**: lowers pH; 200–500 kg/ha
- **Rock Phosphate**: slow-release P for acidic soils
## Soilless Amendments
- **Perlite**: improves drainage; 10–30% of mix
- **Vermiculite**: retains moisture; 10–20% of mix
""",
    "CONTAMINANT_DATABASE.md": """
# Soil and Water Contaminant Database
## Heavy Metals
- **Lead (Pb)**: smelters, old paint; threshold 400 ppm soil, 10 ppb water
- **Arsenic (As)**: mining, pesticides; 20 ppm soil, 10 ppb water
- **Cadmium (Cd)**: phosphate fertilizers; 1.4 ppm soil, 3 ppb water
- **Mercury (Hg)**: industrial; 0.5 ppm soil, 1 ppb water
## Organic Contaminants
- **PAHs**: fossil fuels; carcinogenic at >1 mg/kg soil
- **PCBs**: electrical equipment; >1 mg/kg soil requires remediation
- **Pesticides**: atrazine, chlorpyrifos; varies by compound
## Nitrates
- Excess from fertilizers; >50 ppm water causes blue baby syndrome
""",
    "REMEDIATION_PROTOCOLS.md": """
# Soil and Water Remediation Protocols
## Biological Methods
- Phytoremediation: sunflowers, Indian mustard for heavy metals; 2–5 years
- Bioremediation: bacteria, fungi for organic contaminants; 1–3 years
- Mycorrhizal inoculation: petroleum hydrocarbons; 18 months
## Chemical Methods
- Lime stabilization: immobilizes metals; cost-effective
- Activated carbon: adsorbs organics; weeks
- Chemical oxidation (ISCO): peroxide/permanganate; months
## Physical Methods
- Soil washing: excavation + washing; expensive but fast
- Pump-and-treat: groundwater extraction; years
- Constructed wetlands: passive water treatment; 6–12 months setup
## Water Filtration
- Sand filtration: suspended solids; simple
- Reverse osmosis: all dissolved salts, bacteria; high efficiency
- UV disinfection: pathogens; instantaneous
""",
    "CROP_SUITABILITY.md": """
# Crop Suitability by Soil Type
## Sandy Soils
- Root vegetables: carrots, parsnips, potatoes (need irrigation)
- Asparagus, groundnuts, melons
## Clay Soils
- Wheat, rice, soybeans
- Cabbages, broccoli
## Loam Soils (Ideal)
- Most crops; corn, tomatoes, beans, peppers
## Peat/Acidic Soils
- Blueberries, cranberries, azaleas
## Alkaline/Chalk Soils
- Lavender, asparagus, sweet corn
## Waterlogged/Saline
- Reeds, halophytes, mangroves
## pH Tolerance
- Potatoes: pH 4.5–6.0; Asparagus: pH 6.5–7.5
- Blueberries: pH 4.0–5.5; Most veg: pH 6.0–7.0
""",
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z]{3,}", text.lower())


def _split_paragraphs(text: str, max_tokens: int = 180) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    count = 0
    for line in text.split("\n"):
        words = line.split()
        for word in words:
            if count >= max_tokens and current:
                chunks.append(" ".join(current))
                current = []
                count = 0
            current.append(word)
            count += 1
        # paragraph break
        if not words and current:
            chunks.append(" ".join(current))
            current = []
            count = 0
    if current:
        chunks.append(" ".join(current))
    return [c for c in chunks if len(c.strip()) > 20]


def _build_chunks() -> list[str]:
    chunks: list[str] = []
    for doc_name in TERRA_DOCS_ORDERED:
        file_path = DOCS_DIR / doc_name
        if file_path.exists():
            text = file_path.read_text(encoding="utf-8")
        else:
            text = BUILT_IN_DOCS.get(doc_name, "")
        if text:
            chunks.extend(_split_paragraphs(text))
    return chunks


def _idf(corpus: list[list[str]]) -> dict[str, float]:
    N = len(corpus)
    df: dict[str, int] = {}
    for doc in corpus:
        for token in set(doc):
            df[token] = df.get(token, 0) + 1
    return {t: math.log((N + 1) / (df[t] + 1)) for t in df}


def _score(query_tokens: list[str], doc_tokens: list[str], idf: dict[str, float]) -> float:
    tf: dict[str, float] = {}
    for token in doc_tokens:
        tf[token] = tf.get(token, 0) + 1
    n = max(len(doc_tokens), 1)
    return sum(idf.get(t, 0.0) * (tf.get(t, 0) / n) for t in query_tokens)


def retrieve(query: str, top_k: int = 3) -> list[str]:
    chunks = _build_chunks()
    if not chunks:
        return []
    tokenized = [_tokenize(c) for c in chunks]
    idf = _idf(tokenized)
    q_tokens = _tokenize(query)
    if not q_tokens:
        return chunks[:top_k]
    scored = [(_score(q_tokens, tokenized[i], idf), chunks[i]) for i in range(len(chunks))]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


class TerraBot:
    def __init__(self, db_path=None):
        self.db_path = db_path
        self._chunks = _build_chunks()
        tokenized = [_tokenize(c) for c in self._chunks]
        self._idf = _idf(tokenized)

    def ask(self, question: str, top_k: int = 3) -> str:
        context_chunks = retrieve(question, top_k=top_k)
        if not context_chunks:
            return ("I specialize in soil science, water quality, and land remediation. "
                    "Please ask a specific question about soil types, pH, water quality, "
                    "amendments, or contaminant remediation.")
        context = "\n---\n".join(context_chunks)
        q = question.strip().rstrip("?")
        return (
            f"Based on TerraOS knowledge:\n\n"
            f"**Query:** {q}\n\n"
            f"**Relevant Information:**\n{context}\n\n"
            f"For precise analysis, consider soil testing or contacting a certified agronomist."
        )
