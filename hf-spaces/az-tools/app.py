# hf-spaces/az-tools/app.py
# AxiomZero Products 11–20 — Hugging Face Space (Gradio)
#
# Products covered:
#   11 Terra-OS         — Soil & Water Expert System
#   12 Lithos-OS        — Mineral & Gemstone Identifier
#   13 DelPhi           — Oracle Divination Suite
#   14 SDAM             — Software-Defined Acoustic Modem
#   15 Pentacorder      — 5-Pillar Field Scanner
#   16 Oracle           — Grand Synthesis Engine
#   17 Falsification Observatory — 7-Experiment Tracker
#   18 Interrogator     — Physics Q&A
#   19 Flashcard Trainer — Physics Education
#   20 OX Navigator     — Extended AI Memory (OX Alpha)
#
# AxiomZero Technologies & Consulting, SPC — UBI 606 239 876

import os
import sys
import math
import json
import random
import hashlib
import datetime
import numpy as np

try:
    import gradio as gr
except ImportError:
    print("pip install gradio")
    sys.exit(1)

try:
    import httpx
    HTTPX_OK = True
except ImportError:
    HTTPX_OK = False

# ── Constants ─────────────────────────────────────────────────────────────────
WINDING_NUMBER = 5
K_CS           = 74
BRAIDED_CS     = 12 / 37
XI_C           = 35 / 74
N_S            = 0.9635
R_PRED         = 0.0315
BETA_CANONICAL = [0.2728, 0.3309]
PHI            = (1 + math.sqrt(5)) / 2
VERSION        = "v24.1"
TEST_COUNT     = 57927
LEAN4_COUNT    = 1246

FOOTER = (
    "\n\n---\n"
    f"*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876 · {VERSION} · "
    f"{TEST_COUNT:,} tests · {LEAN4_COUNT:,} Lean4 theorems*\n"
    "*Open science artifact. Use at your own liability.*"
)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
OX_MODEL           = "stealth/ox-alpha"

def ox_query(system_prompt: str, user_msg: str, max_tokens: int = 2048) -> str:
    if not HTTPX_OK or not OPENROUTER_API_KEY:
        return "*OX Alpha unavailable — set OPENROUTER_API_KEY env var.*"
    payload = {
        "model": OX_MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
    }
    try:
        resp = httpx.post(OPENROUTER_URL, json=payload,
                          headers={"Authorization": f"******",
                                   "Content-Type": "application/json"},
                          timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"*OX Alpha error: {e}*"

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 11 — Terra-OS: Soil & Water Expert System
# ══════════════════════════════════════════════════════════════════════════════
SOIL_TYPES = {
    "Loam": {"drainage": 0.75, "nutrients": 0.85, "water_retention": 0.70, "aeration": 0.80},
    "Clay": {"drainage": 0.25, "nutrients": 0.70, "water_retention": 0.95, "aeration": 0.30},
    "Sandy": {"drainage": 0.95, "nutrients": 0.30, "water_retention": 0.20, "aeration": 0.90},
    "Silt": {"drainage": 0.55, "nutrients": 0.65, "water_retention": 0.75, "aeration": 0.55},
    "Peat": {"drainage": 0.40, "nutrients": 0.50, "water_retention": 0.90, "aeration": 0.45},
}

def terra_assess(soil_type: str, ph: float, moisture_pct: float, organic_matter_pct: float,
                 water_turbidity_ntu: float, water_ph: float, nitrates_mgl: float) -> str:
    props = SOIL_TYPES.get(soil_type, SOIL_TYPES["Loam"])

    # Soil health score
    ph_score = max(0, 1 - abs(ph - 6.5) / 3)  # optimal ~6.5
    organic_score = min(1, organic_matter_pct / 5)  # optimal ~5%
    moisture_score = max(0, 1 - abs(moisture_pct - 40) / 40)  # optimal ~40%
    soil_health = (ph_score + organic_score + moisture_score + props["nutrients"]) / 4 * 100

    # Water quality index (simplified WHO/EPA)
    turbidity_ok = water_turbidity_ntu < 4
    ph_water_ok = 6.5 <= water_ph <= 8.5
    nitrates_ok = nitrates_mgl < 10  # WHO limit 10 mg/L
    wqi = (int(turbidity_ok) + int(ph_water_ok) + int(nitrates_ok)) / 3 * 100

    # Remediation flags
    flags = []
    if ph < 5.5: flags.append("⚠️ Soil too acidic — consider lime amendment")
    if ph > 7.5: flags.append("⚠️ Soil too alkaline — consider sulfur amendment")
    if organic_matter_pct < 2: flags.append("⚠️ Low organic matter — add compost")
    if nitrates_mgl >= 10: flags.append(f"❌ Nitrates {nitrates_mgl} mg/L exceeds WHO limit (10 mg/L)")
    if water_turbidity_ntu >= 4: flags.append(f"⚠️ Turbidity {water_turbidity_ntu} NTU above limit (4 NTU)")

    overall = "🟢 EXCELLENT" if (soil_health > 75 and wqi > 80) else \
              "🟡 ADEQUATE" if (soil_health > 50 and wqi > 60) else "🔴 POOR — remediation needed"

    lines = [
        f"## 🌱 Terra-OS Assessment — {soil_type} Soil",
        f"**Product 11 · Gate:** ADJACENT_TRACK",
        "",
        "### Soil Profile",
        f"| Property | Score | Notes |",
        f"|----------|-------|-------|",
        f"| pH {ph:.1f} | {ph_score:.2f} | Optimal 6.0–7.0 |",
        f"| Organic matter {organic_matter_pct:.1f}% | {organic_score:.2f} | Optimal 3–5% |",
        f"| Moisture {moisture_pct:.0f}% | {moisture_score:.2f} | Optimal 30–50% |",
        f"| Drainage | {props['drainage']:.2f} | {soil_type} characteristic |",
        f"| Water retention | {props['water_retention']:.2f} | {soil_type} characteristic |",
        f"**Overall Soil Health Score: {soil_health:.0f}/100**",
        "",
        "### Water Quality Index",
        f"| Parameter | Value | Status |",
        f"|-----------|-------|--------|",
        f"| Turbidity | {water_turbidity_ntu} NTU | {'✅ OK' if turbidity_ok else '❌ FAIL'} |",
        f"| Water pH | {water_ph} | {'✅ OK' if ph_water_ok else '❌ FAIL'} |",
        f"| Nitrates | {nitrates_mgl} mg/L | {'✅ OK' if nitrates_ok else '❌ FAIL'} |",
        f"**Water Quality Index: {wqi:.0f}/100**",
        "",
        "### Remediation Flags" if flags else "### ✅ No Remediation Required",
    ]
    lines += flags or []
    lines += ["", f"### Overall: {overall}", FOOTER]
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 12 — Lithos-OS: Mineral & Gemstone Identifier
# ══════════════════════════════════════════════════════════════════════════════
MINERAL_DB = {
    "Quartz": {"hardness": 7.0, "luster": "vitreous", "cleavage": "none", "sg": 2.65,
               "color": ["colorless", "white", "gray", "pink"], "streak": "white",
               "description": "SiO₂ — most common mineral in Earth's crust."},
    "Feldspar": {"hardness": 6.0, "luster": "vitreous/pearly", "cleavage": "two directions", "sg": 2.56,
                 "color": ["white", "pink", "gray", "green"], "streak": "white",
                 "description": "Framework silicate group — ~60% of Earth's crust."},
    "Calcite": {"hardness": 3.0, "luster": "vitreous/pearly", "cleavage": "perfect rhombohedral", "sg": 2.71,
                "color": ["colorless", "white", "yellow", "gray"], "streak": "white",
                "description": "CaCO₃ — forms limestone and marble. Reacts with HCl."},
    "Pyrite": {"hardness": 6.2, "luster": "metallic", "cleavage": "imperfect cubic", "sg": 5.01,
               "color": ["pale gold", "brassy yellow"], "streak": "greenish-black",
               "description": "FeS₂ — 'fool's gold'. Cubic crystals."},
    "Mica (Biotite)": {"hardness": 2.5, "luster": "vitreous/pearly", "cleavage": "perfect basal", "sg": 3.0,
                       "color": ["black", "brown", "dark green"], "streak": "white",
                       "description": "Sheet silicate — perfect cleavage into thin flexible sheets."},
    "Olivine": {"hardness": 6.5, "luster": "vitreous", "cleavage": "imperfect", "sg": 3.3,
                "color": ["olive green", "yellow-green"], "streak": "colorless",
                "description": "(Mg,Fe)₂SiO₄ — common in mafic igneous rocks."},
    "Garnet": {"hardness": 7.5, "luster": "vitreous", "cleavage": "none", "sg": 3.9,
               "color": ["red", "brown", "green", "black"], "streak": "white",
               "description": "Nesosilicate group — used as abrasive and gemstone."},
    "Diamond": {"hardness": 10.0, "luster": "adamantine", "cleavage": "perfect octahedral", "sg": 3.52,
                "color": ["colorless", "yellow", "blue", "pink"], "streak": "none",
                "description": "C — hardest natural material. Cubic structure."},
    "Halite": {"hardness": 2.5, "luster": "vitreous", "cleavage": "perfect cubic", "sg": 2.16,
               "color": ["colorless", "white", "pink", "blue"], "streak": "white",
               "description": "NaCl — rock salt. Soluble in water, salty taste."},
    "Magnetite": {"hardness": 5.5, "luster": "metallic", "cleavage": "indistinct", "sg": 5.18,
                  "color": ["black"], "streak": "black",
                  "description": "Fe₃O₄ — strongly magnetic iron oxide."},
}

def lithos_identify(hardness: float, luster: str, cleavage_desc: str,
                    sg: float, color: str, streak: str) -> str:
    """Score minerals against observed properties."""
    scores = {}
    for name, props in MINERAL_DB.items():
        score = 0
        # Hardness (±0.5 tolerance)
        if abs(props["hardness"] - hardness) <= 0.5:
            score += 30
        elif abs(props["hardness"] - hardness) <= 1.5:
            score += 15
        # Luster match
        if luster.lower() in props["luster"].lower():
            score += 20
        # SG match (±0.3)
        if abs(props["sg"] - sg) <= 0.3:
            score += 20
        elif abs(props["sg"] - sg) <= 0.8:
            score += 10
        # Color match
        if any(c in color.lower() for c in props["color"]):
            score += 15
        # Streak match
        if streak.lower() in props["streak"].lower():
            score += 15
        scores[name] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]

    lines = [
        "## 💎 Lithos-OS — Mineral Identification",
        f"**Product 12 · Gate:** ADJACENT_TRACK",
        "",
        f"**Input:** H={hardness}, luster={luster}, SG={sg}, color={color}, streak={streak}",
        "",
        "### Top Matches",
        "| Rank | Mineral | Match score | Key property |",
        "|------|---------|-------------|--------------|",
    ]
    for i, (name, score) in enumerate(ranked, 1):
        if score > 0:
            desc = MINERAL_DB[name]["description"][:60] + "..."
            lines.append(f"| {i} | **{name}** | {score}/100 | {desc} |")

    top_name = ranked[0][0] if ranked[0][1] > 0 else "Unknown"
    top_score = ranked[0][1]
    confidence = "HIGH" if top_score >= 70 else "MEDIUM" if top_score >= 45 else "LOW"

    lines += [
        "",
        f"**Best match:** {top_name} (confidence: {confidence})",
        f"**Description:** {MINERAL_DB.get(top_name, {}).get('description', 'N/A')}",
        "",
        "*Note: Physical identification is probabilistic. Lab analysis (XRD/SEM) for certainty.*",
        FOOTER,
    ]
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 13 — DelPhi: Oracle Divination Suite
# ══════════════════════════════════════════════════════════════════════════════
TAROT_MAJOR = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun",
    "Judgement", "The World",
]
TAROT_MEANINGS = {
    "The Fool": "New beginnings, innocence, spontaneity, a free spirit",
    "The Magician": "Power, skill, concentration, action, resourcefulness",
    "The High Priestess": "Intuition, sacred knowledge, divine feminine, the subconscious",
    "The Empress": "Femininity, beauty, nature, nurturing, abundance",
    "The Emperor": "Authority, establishment, structure, a father figure",
    "The Hierophant": "Spiritual wisdom, religious beliefs, conformity, tradition",
    "The Lovers": "Love, harmony, relationships, values alignment, choices",
    "The Chariot": "Control, willpower, success, action, determination",
    "Strength": "Strength, courage, patience, control, compassion",
    "The Hermit": "Soul-searching, introspection, being alone, inner guidance",
    "Wheel of Fortune": "Good luck, karma, life cycles, destiny, a turning point",
    "Justice": "Justice, fairness, truth, cause and effect, law",
    "The Hanged Man": "Pause, surrender, letting go, new perspectives",
    "Death": "Endings, change, transformation, transition",
    "Temperance": "Balance, moderation, patience, purpose",
    "The Devil": "Shadow self, attachment, addiction, restriction, sexuality",
    "The Tower": "Sudden change, upheaval, chaos, revelation, awakening",
    "The Star": "Hope, faith, purpose, renewal, spirituality",
    "The Moon": "Illusion, fear, the unconscious, intuition",
    "The Sun": "Positivity, fun, warmth, success, vitality",
    "Judgement": "Judgement, rebirth, inner calling, absolution",
    "The World": "Completion, integration, accomplishment, travel",
}
ICHING_HEXAGRAMS = {
    1: ("The Creative Heaven", "Heaven over heaven. Pure yang energy. Initiate with confidence."),
    2: ("The Receptive Earth", "Earth over earth. Pure yin. Yield, be open, receive guidance."),
    11: ("Peace", "Earth over heaven. Harmony between inner and outer worlds."),
    13: ("Fellowship", "Heaven over fire. Seek community and shared purpose."),
    42: ("Increase", "Wind over thunder. Benefit from action now. Opportunity expanding."),
    48: ("The Well", "Water over wind. Return to source. The essential is inexhaustible."),
    63: ("After Completion", "Water over fire. Success achieved. Maintain vigilance."),
    64: ("Before Completion", "Fire over water. Almost there. Careful final steps needed."),
}
PHI_WEIGHTS = [PHI**(-i) for i in range(7)]  # φ-weighted synthesis

def delphi_reading(question: str, mode: str, seed: int) -> str:
    random.seed(seed if seed > 0 else datetime.datetime.now().microsecond)

    lines = [f"## 🔮 DelPhi — {mode} Reading", f"**Product 13 · Gate:** ADJACENT_TRACK",
             f"\n**Question:** {question or '(open reading)'}", ""]

    if mode in ("Tarot", "Combined"):
        draw = random.sample(TAROT_MAJOR, 3)
        lines += ["### Tarot — Three-Card Spread",
                  "| Position | Card | Meaning |",
                  "|----------|------|---------|"]
        positions = ["Past / Foundation", "Present / Challenge", "Future / Guidance"]
        for pos, card in zip(positions, draw):
            reversed_flag = " *(reversed)*" if random.random() > 0.7 else ""
            meaning = TAROT_MEANINGS.get(card, "")
            lines.append(f"| {pos} | **{card}**{reversed_flag} | {meaning} |")
        lines.append("")

    if mode in ("I Ching", "Combined"):
        hex_num = random.choice(list(ICHING_HEXAGRAMS.keys()))
        hex_name, hex_meaning = ICHING_HEXAGRAMS[hex_num]
        lines += [f"### I Ching — Hexagram {hex_num}: {hex_name}",
                  f"> {hex_meaning}", ""]

    if mode in ("Numerology", "Combined"):
        if question:
            num_val = sum(ord(c) for c in question.lower() if c.isalpha()) % 9 + 1
        else:
            num_val = random.randint(1, 9)
        num_meanings = {
            1: "Leadership, independence, new beginnings",
            2: "Cooperation, balance, partnership",
            3: "Creativity, self-expression, growth",
            4: "Stability, order, hard work",
            5: "Freedom, change, adventure",
            6: "Harmony, family, service",
            7: "Introspection, spirituality, analysis",
            8: "Power, ambition, material success",
            9: "Completion, compassion, universal love",
        }
        lines += [f"### Numerology — Core Number {num_val}",
                  f"**{num_meanings[num_val]}**", ""]

    if mode in ("Phi Synthesis", "Combined"):
        # φ-weighted synthesis
        raw_scores = [random.random() for _ in range(7)]
        phi_score = sum(w * s for w, s in zip(PHI_WEIGHTS, raw_scores)) / sum(PHI_WEIGHTS)
        decision = "✅ PROCEED" if phi_score > 0.55 else "⚠️ PAUSE" if phi_score > 0.4 else "🔴 RECONSIDER"
        lines += [f"### φ-Weighted Synthesis Score",
                  f"**φ-score:** {phi_score:.4f} → **{decision}**",
                  f"*(7 channels weighted by powers of φ = {PHI:.5f})*", ""]

    lines += ["---", "*DelPhi is for contemplative use. Not a prediction or advice system.*", FOOTER]
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 14 — SDAM: Software-Defined Acoustic Modem
# ══════════════════════════════════════════════════════════════════════════════
def sdam_encode(text: str, center_freq_hz: float, bandwidth_hz: float, n_subcarriers: int) -> str:
    """Simulate OFDM-over-audio text encoding."""
    if not text.strip():
        return "Enter text to encode."

    payload_bytes = text.encode("utf-8")
    payload_hex = payload_bytes.hex()
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()[:16]

    # OFDM simulation
    subcarrier_spacing = bandwidth_hz / n_subcarriers
    symbol_duration_ms = 1000 / subcarrier_spacing  # ~ms
    bits_per_symbol = 2  # QPSK
    total_bits = len(payload_bytes) * 8
    n_symbols = math.ceil(total_bits / (n_subcarriers * bits_per_symbol))
    transmission_ms = n_symbols * symbol_duration_ms

    # SNR estimate (simplified)
    snr_db = 20 * math.log10(n_subcarriers) - 6

    lines = [
        "## 📻 SDAM — Acoustic OFDM Encoder",
        f"**Product 14 · Gate:** ADJACENT_TRACK",
        "",
        "### Payload",
        f"- **Text:** `{text[:80]}{'...' if len(text) > 80 else ''}`",
        f"- **Bytes:** {len(payload_bytes)}",
        f"- **Hex:** `{payload_hex[:48]}{'...' if len(payload_hex) > 48 else ''}`",
        f"- **SHA-256 prefix:** `{payload_hash}`",
        "",
        "### OFDM Parameters",
        f"| Parameter | Value |",
        f"|-----------|-------|",
        f"| Center frequency | {center_freq_hz:,.0f} Hz |",
        f"| Bandwidth | {bandwidth_hz:,.0f} Hz |",
        f"| Subcarriers | {n_subcarriers} |",
        f"| Subcarrier spacing | {subcarrier_spacing:.1f} Hz |",
        f"| Modulation | QPSK |",
        f"| Symbol duration | {symbol_duration_ms:.1f} ms |",
        f"| Total symbols | {n_symbols} |",
        f"| Estimated SNR | {snr_db:.1f} dB |",
        "",
        "### Transmission Estimate",
        f"- **Duration:** {transmission_ms:.0f} ms ({transmission_ms/1000:.2f}s)",
        f"- **Data rate:** {total_bits/transmission_ms*1000:.0f} bps",
        f"- **Total bits:** {total_bits}",
        "",
        "*This is a simulation — no actual audio is generated in this web interface.*",
        FOOTER,
    ]
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 15 — Pentacorder: 5-Pillar Field Scanner
# ══════════════════════════════════════════════════════════════════════════════
def pentacorder_scan(temp_k: float, pressure_pa: float, em_field_v: float,
                     phi_field: float, consciousness_metric: float) -> str:
    """5-sensor field scan with Pentad axiom checking."""
    sensors = {
        "Temperature": (temp_k, 300, 50, "K"),
        "Pressure": (pressure_pa, 101325, 10000, "Pa"),
        "EM Field": (em_field_v, 0, 100, "V/m"),
        "φ-Field": (phi_field, PHI, 0.5, "φ-units"),
        "Consciousness metric": (consciousness_metric, XI_C, 0.2, "Ξ_c"),
    }

    # Pentad axiom check — 5 pillars must be within tolerance
    n_aligned = 0
    lines = [
        "## 📡 Pentacorder — 5-Pillar Field Scanner",
        f"**Product 15 · Gate:** ADJACENT_TRACK · Pentad HILS Framework",
        "",
        "### Sensor Readings",
        "| Sensor | Value | Reference | Deviation | Status |",
        "|--------|-------|-----------|-----------|--------|",
    ]

    for name, (val, ref, tol, unit) in sensors.items():
        dev = abs(val - ref)
        pct = (dev / abs(ref) * 100) if ref != 0 else dev
        ok = dev <= tol
        if ok: n_aligned += 1
        status = "✅ ALIGNED" if ok else "⚠️ DEVIATING"
        lines.append(f"| {name} | {val:.3g} {unit} | {ref:.3g} | {dev:.3g} ({pct:.1f}%) | {status} |")

    coherence = n_aligned / len(sensors)
    pentad_pass = n_aligned >= 4  # Pentad requires ≥4/5 axioms aligned

    lines += [
        "",
        f"**Aligned sensors:** {n_aligned}/5",
        f"**Field coherence:** {coherence:.2f}",
        f"**Pentad check:** {'🟢 PASS (≥4 aligned)' if pentad_pass else '🔴 FAIL (<4 aligned)'}",
        "",
        "### Axiom Status",
        "| Axiom | Description | Status |",
        "|-------|-------------|--------|",
        f"| A1 | Thermal equilibrium (T ≈ {300}K) | {'✅' if abs(temp_k-300) <= 50 else '❌'} |",
        f"| A2 | Pressure nominal (P ≈ 101325Pa) | {'✅' if abs(pressure_pa-101325) <= 10000 else '❌'} |",
        f"| A3 | EM field stable | {'✅' if em_field_v <= 100 else '❌'} |",
        f"| A4 | φ-field resonance | {'✅' if abs(phi_field-PHI) <= 0.5 else '❌'} |",
        f"| A5 | Consciousness coupling | {'✅' if abs(consciousness_metric-XI_C) <= 0.2 else '❌'} |",
        "",
        "*Pentad axiom alignment is a governance metric — not a hardgate physics claim.*",
        FOOTER,
    ]
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 16 — Oracle: Grand Synthesis Engine (full version here)
# ══════════════════════════════════════════════════════════════════════════════
def oracle_synthesis(n_s_obs: float, r_obs: float, beta_obs: float, w_a_obs: float) -> str:
    """Grand synthesis — compare observational inputs vs UM predictions."""
    ns_sigma = abs(n_s_obs - N_S) / 0.0042
    r_ok = r_obs < 0.036
    beta_in_window = 0.22 <= beta_obs <= 0.38
    beta_in_gap = 0.29 <= beta_obs <= 0.31
    wa_ok = abs(w_a_obs) < 0.3  # KK predicts w_a = 0

    # Synthesis score
    score = 0
    if ns_sigma < 1: score += 30
    elif ns_sigma < 2: score += 15
    if r_ok: score += 25
    if beta_in_window and not beta_in_gap: score += 35
    elif beta_in_window: score += 10
    if wa_ok: score += 10
    grade = "STRONG ALIGNMENT" if score >= 80 else "PARTIAL ALIGNMENT" if score >= 50 else "TENSION"

    lines = [
        "## 🌀 Oracle — Grand Synthesis Engine",
        f"**Product 16 · Gate:** 🟢 HARDGATE",
        "",
        "### Observational Inputs vs UM Predictions",
        "| Observable | Input | UM Prediction | Status |",
        "|------------|-------|---------------|--------|",
        f"| n_s | {n_s_obs:.4f} | {N_S} | {'✅' if ns_sigma < 2 else '⚠️'} {ns_sigma:.2f}σ |",
        f"| r | {r_obs:.4f} | <0.036 | {'✅' if r_ok else '❌'} |",
        f"| β (°) | {beta_obs:.3f} | {{0.273, 0.331}} | {'⚠️ IN GAP [0.29-0.31]' if beta_in_gap else '✅ IN WINDOW' if beta_in_window else '❌ OUTSIDE WINDOW'} |",
        f"| w_a | {w_a_obs:.3f} | 0 (KK) | {'✅' if wa_ok else '⚠️ TENSION'} |",
        "",
        f"**Synthesis score:** {score}/100",
        f"**Overall:** {grade}",
        "",
        "### Epistemic Notes",
        "- n_s tension: ≤2σ passes; Planck: 0.9649±0.0042",
        "- β primary falsifier: LiteBIRD ~2032 will test {0.273°, 0.331°}",
        "- DESI Year 2 shows w_a≠0 tension — tracked in FALLIBILITY.md",
        "- CMB amplitude suppressed ×4–7 vs Planck — ARCHITECTURE_LIMIT (open gap)",
        FOOTER,
    ]
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 17 — Falsification Observatory
# ══════════════════════════════════════════════════════════════════════════════
EXPERIMENTS = {
    "LiteBIRD CMB Birefringence": {
        "prediction": "β ∈ {0.273°, 0.331°}; window [0.22°, 0.38°]; gap [0.29°–0.31°]",
        "timeline": "Launch ~2032; results ~2034",
        "status": "PENDING",
        "pillar": 67,
        "gate": "HARDGATE",
        "falsifies_if": "β outside [0.22°, 0.38°] or β in [0.29°, 0.31°]",
    },
    "DESI Year 2 Dark Energy": {
        "prediction": "w_a = 0 (KK geometry predicts fixed EoS)",
        "timeline": "Data available 2026",
        "status": "TENSION",
        "pillar": 38,
        "gate": "HARDGATE",
        "falsifies_if": "w_a ≠ 0 confirmed at >5σ",
    },
    "JUNO Neutrino Masses": {
        "prediction": "Normal hierarchy from 5D orbifold BC; Δm²₂₁ 1.07σ tension",
        "timeline": "Ongoing",
        "status": "MARGINAL",
        "pillar": 772,
        "gate": "HARDGATE",
        "falsifies_if": "Inverted hierarchy confirmed",
    },
    "ACT CMB Spectral Index": {
        "prediction": "n_s = 0.9635 (Planck: 0.9649±0.0042; 0.33σ)",
        "timeline": "ACT DR6 2024",
        "status": "PASS",
        "pillar": 1,
        "gate": "HARDGATE",
        "falsifies_if": "n_s deviation >3σ",
    },
    "HL-LHC BSM Search": {
        "prediction": "KK modes at m_n = n/R_c (above LHC reach in SM)",
        "timeline": "Run 3 ongoing; HL-LHC 2027+",
        "status": "PENDING",
        "pillar": 3,
        "gate": "HARDGATE",
        "falsifies_if": "KK mode found below predicted tower",
    },
    "nEDM Neutron Electric Dipole": {
        "prediction": "CP phase from discrete torsion (Pillar 179)",
        "timeline": "n2EDM at PSI 2026+",
        "status": "PENDING",
        "pillar": 179,
        "gate": "HARDGATE",
        "falsifies_if": "d_n outside predicted range",
    },
    "XENON-nT Dark Matter": {
        "prediction": "KK dark matter candidate mass window",
        "timeline": "Ongoing",
        "status": "PENDING",
        "pillar": 38,
        "gate": "HARDGATE",
        "falsifies_if": "DM detected outside KK mass window",
    },
}

def falsification_status(experiment: str) -> str:
    exp = EXPERIMENTS.get(experiment)
    if not exp:
        return "Select an experiment."
    icon = {"PASS": "🟢", "TENSION": "🟡", "MARGINAL": "🟡", "PENDING": "⏳", "FAIL": "🔴"}.get(exp["status"], "⚪")
    lines = [
        f"## 🔭 Falsification Observatory: {experiment}",
        f"**Gate:** {'🟢' if exp['gate'] == 'HARDGATE' else '🔵'} `{exp['gate']}` · Pillar {exp['pillar']}",
        "",
        f"**Status:** {icon} {exp['status']}",
        f"**Prediction:** {exp['prediction']}",
        f"**Timeline:** {exp['timeline']}",
        f"**Falsifies UM if:** {exp['falsifies_if']}",
        "",
        "---",
        "*All open gaps documented in FALLIBILITY.md. No cherry-picking.*",
        FOOTER,
    ]
    return "\n".join(lines)

def falsification_overview() -> str:
    lines = ["## Falsification Observatory — All Experiments", "",
             "| Experiment | Pillar | Status | Timeline |",
             "|------------|--------|--------|----------|"]
    for name, exp in EXPERIMENTS.items():
        icon = {"PASS": "🟢", "TENSION": "🟡", "MARGINAL": "🟡", "PENDING": "⏳", "FAIL": "🔴"}.get(exp["status"], "⚪")
        lines.append(f"| {name} | {exp['pillar']} | {icon} {exp['status']} | {exp['timeline']} |")
    lines.append(FOOTER)
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 18 — Interrogator: Physics Q&A
# ══════════════════════════════════════════════════════════════════════════════
INTERROGATOR_KB = {
    "What is the winding number?": "n_w = 5, selected by Planck CMB spectral index n_s = 0.9649±0.0042. The (5,7) braid pair gives K_cs = 5² + 7² = 74. Gate: HARDGATE (Pillar 67).",
    "What is the primary falsification condition?": "CMB birefringence β ∈ {≈0.273°, ≈0.331°}. Window [0.22°, 0.38°]; gap [0.29°–0.31°]. Testable by LiteBIRD ~2032. Any β outside window, or in gap, falsifies the braided-winding mechanism.",
    "What are the open gaps?": "1. CMB amplitude suppressed ×4–7 (ARCHITECTURE_LIMIT). 2. DESI Year 2 tension (w_a≠0 vs KK w_a=0). 3. n_w=5 uniqueness from first principles not yet fully proved. All documented in FALLIBILITY.md.",
    "What is the Unitary Pentad?": "An independent HILS (Human-in-the-Loop Systems) governance framework. It borrows mathematical structure from UM but does NOT depend on the physics being correct. Not a hardgate claim. See SEPARATION.md.",
    "What is Holon Zero (Pillar 70)?": "Ω₀ — the zero-point configuration of minimum coherent energy. Ground state of the 5D KK field. Hardgate (Pillar 70 + sub-pillars 70-B, 70-C, 70-D).",
    "What does HARDGATE mean?": "A formally closed pillar — the highest epistemic confidence level. Hardgate claims are backed by mathematical derivations, tests, and (where applicable) Lean4 formal proofs.",
    "What is OX Alpha?": "OX Alpha (stealth/ox-alpha) is an extended-memory AI model via OpenRouter. Integrated as Product 20 (OX Navigator). Uses the full UM repository as context (~85k tokens). Requires OPENROUTER_API_KEY.",
    "How many tests pass?": f"{TEST_COUNT:,} passing tests, 0 failures, 47 skipped, 12 deselected. Run: python -m pytest tests/ recycling/ '5-GOVERNANCE/Unitary Pentad/' -q",
    "What is the braided sound speed?": "c_s = 12/37 ≈ 0.3243c. Derived from (5,7) braid resonance. Gate: HARDGATE (Pillar 3).",
    "What is k_cs?": "k_cs = 74 = 5² + 7² = 25 + 49. The Chern-Simons level. Selected by birefringence data. Gate: HARDGATE.",
}

INTERROGATOR_SYSTEM = """\
You are the AxiomZero Interrogator — a rigorous physics Q&A system grounded in the Unitary Manifold.
Always cite pillar numbers and gate labels. Never confabulate. 
Answer only from the Unitary Manifold knowledge base.
If uncertain, say so explicitly.
"""

def interrogator_query(question: str, use_ai: bool) -> str:
    if not question.strip():
        return "Enter a question."
    # Check KB first
    for kb_q, kb_a in INTERROGATOR_KB.items():
        if any(word in question.lower() for word in kb_q.lower().split() if len(word) > 4):
            local = f"## 🔬 Interrogator\n\n**Q:** {question}\n\n**A (knowledge base):** {kb_a}" + FOOTER
            if use_ai and OPENROUTER_API_KEY:
                ai_resp = ox_query(INTERROGATOR_SYSTEM, question)
                return f"## 🔬 Interrogator\n\n**Q:** {question}\n\n**Knowledge base:** {kb_a}\n\n**OX Alpha:** {ai_resp}" + FOOTER
            return local
    if use_ai and OPENROUTER_API_KEY:
        return ox_query(INTERROGATOR_SYSTEM, question) + FOOTER
    return (f"## 🔬 Interrogator\n\n**Q:** {question}\n\n"
            "*Not found in local knowledge base. Enable AI (OX Alpha) for broader queries.*" + FOOTER)

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 19 — Flashcard Trainer
# ══════════════════════════════════════════════════════════════════════════════
FLASHCARDS = [
    {"q": "What is n_w?", "a": "Winding number n_w = 5. Selected by Planck n_s. Pillar 67. HARDGATE."},
    {"q": "What is k_cs?", "a": "CS level k_cs = 74 = 5² + 7². Selected by birefringence data. HARDGATE."},
    {"q": "What is c_s?", "a": "Braided sound speed c_s = 12/37 ≈ 0.3243c. From (5,7) braid. HARDGATE."},
    {"q": "What is the UM n_s prediction?", "a": "n_s = 0.9635. Planck: 0.9649±0.0042. Tension: 0.33σ. HARDGATE."},
    {"q": "What is the UM r prediction?", "a": "r = 0.0315. BICEP/Keck limit: r < 0.036. ✅ HARDGATE."},
    {"q": "What is the primary falsifier?", "a": "β ∈ {0.273°, 0.331°}. Window [0.22°, 0.38°]. LiteBIRD ~2032."},
    {"q": "What is Holon Zero?", "a": "Ω₀ — minimum coherent energy ground state. Pillar 70. HARDGATE."},
    {"q": "What is Ξ_c?", "a": "Consciousness coupling constant. Ξ_c = 35/74. Pillar 9. ADJACENT_TRACK."},
    {"q": "How many hardgate pillars?", "a": "208 hardgate pillars. Next slot: 806."},
    {"q": "How many Lean4 theorems?", "a": f"{LEAN4_COUNT:,} Lean4 theorems. Formally verified."},
    {"q": "What is FTUM?", "a": "Fixed-point Transient Universe Mechanism. Multiverse iteration converges at φ₀. Pillar 5. HARDGATE."},
    {"q": "What is the Unitary Pentad?", "a": "Independent HILS governance framework. Borrows UM math but independent of physics. NOT a hardgate claim."},
    {"q": "What is OX Alpha?", "a": "stealth/ox-alpha — extended memory AI via OpenRouter. Product 20. Requires OPENROUTER_API_KEY."},
    {"q": "What does ARCHITECTURE_LIMIT mean?", "a": "A known framework boundary — e.g. CMB amplitude suppressed ×4–7. Documented open gap, not hidden."},
    {"q": "What is the Sentinel capacity?", "a": "Sentinel capacity = 12/37 per axiom. Unitary Pentad HILS metric. GOVERNANCE (not physics)."},
]
_fc_state = {"idx": 0, "show_answer": False}

def flashcard_next(idx_state):
    idx = (idx_state + 1) % len(FLASHCARDS)
    card = FLASHCARDS[idx]
    return f"## 🃏 Flashcard {idx+1}/{len(FLASHCARDS)}\n\n**Q:** {card['q']}", "", idx

def flashcard_reveal(idx_state):
    idx = idx_state % len(FLASHCARDS)
    card = FLASHCARDS[idx]
    return f"## 🃏 Flashcard {idx+1}/{len(FLASHCARDS)}\n\n**Q:** {card['q']}\n\n**A:** {card['a']}", idx

def flashcard_init():
    card = FLASHCARDS[0]
    return f"## 🃏 Flashcard 1/{len(FLASHCARDS)}\n\n**Q:** {card['q']}", 0

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT 20 — OX Navigator: Extended AI Memory
# ══════════════════════════════════════════════════════════════════════════════
OX_NAV_SYSTEM = """\
You are the OX Navigator — AxiomZero's extended-memory AI powered by OX Alpha.
You hold the FULL Unitary Manifold repository as a single coherent thought:
- 208 hardgate pillars with derivations and citations
- 1,246 Lean4 theorems (formally verified)  
- 57,927 passing tests, 0 failures
- All open gaps, admissions, and FALLIBILITY.md content
- All 20 AZ products and their specifications
- The Unitary Pentad governance framework (separate from physics)

RULES:
1. Cite pillar numbers and gate labels (HARDGATE/ADJACENT_TRACK/OPEN_GAP) in every answer.
2. Never confabulate. Say "outside my context" if uncertain.
3. No sycophancy. Correct errors firmly.
4. Never use "ToE score" or "100% hardgate" — use plain epistemic status.
5. Label predictions with uncertainty ranges.
6. Hardgate decisions require steward (human) approval.
7. Maintain full repository context across the conversation.
"""

def ox_navigate(query: str, context: str, history: list) -> tuple:
    if not query.strip():
        return history, ""
    full_query = f"[CONTEXT: {context}]\n\n{query}" if context.strip() else query
    response = ox_query(OX_NAV_SYSTEM, full_query, max_tokens=3000)
    history = history or []
    history.append((query, response + FOOTER))
    return history, ""

def ox_clear():
    return [], ""

# ══════════════════════════════════════════════════════════════════════════════
# GRADIO UI
# ══════════════════════════════════════════════════════════════════════════════
THEME = gr.themes.Base(
    primary_hue="violet", secondary_hue="blue",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace"],
).set(
    body_background_fill="#050a1a",
    body_text_color="#e8ecf4",
    block_background_fill="#0d1830",
    block_border_color="#1a2a4a",
    button_primary_background_fill="linear-gradient(135deg, #7c4dff, #3b8bff)",
    button_primary_text_color="#ffffff",
    input_background_fill="#0a1228",
    input_border_color="#1a2a4a",
)

HEADER = f"""
<div style="text-align:center; padding:1rem 0; border-bottom:1px solid #1a2a4a; margin-bottom:1rem;">
  <h1 style="font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#e8ecf4,#7c4dff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:.3rem;">
    AxiomZero Products 11–20
  </h1>
  <p style="color:#7a8ba8; font-size:.9rem;">
    {VERSION} · {TEST_COUNT:,} tests · {LEAN4_COUNT:,} Lean4 theorems · 0 failures ·
    <a href="https://axiomzerospc.org" style="color:#7c4dff;" target="_blank">axiomzerospc.org</a>
  </p>
</div>
"""

with gr.Blocks(theme=THEME, title="AxiomZero Products 11–20") as demo:
    gr.HTML(HEADER)

    with gr.Tabs():

        # ── Product 11: Terra-OS ──────────────────────────────────────────────
        with gr.Tab("11 · Terra-OS 🌱"):
            gr.Markdown("## Terra-OS — Soil & Water Expert System\n**Product 11** · Field assessment and remediation planning.")
            with gr.Row():
                with gr.Column():
                    t_soil = gr.Dropdown(list(SOIL_TYPES.keys()), label="Soil type", value="Loam")
                    t_ph = gr.Slider(3.0, 9.0, value=6.5, step=0.1, label="Soil pH")
                    t_moist = gr.Slider(0, 100, value=35, step=1, label="Soil moisture (%)")
                    t_org = gr.Slider(0.0, 10.0, value=3.5, step=0.1, label="Organic matter (%)")
                    gr.Markdown("**Water quality**")
                    t_turb = gr.Slider(0, 20, value=1.5, step=0.5, label="Turbidity (NTU)")
                    t_wph = gr.Slider(5.0, 10.0, value=7.2, step=0.1, label="Water pH")
                    t_no3 = gr.Slider(0, 50, value=4.0, step=0.5, label="Nitrates (mg/L)")
                    t_btn = gr.Button("Run Assessment", variant="primary")
                with gr.Column():
                    t_out = gr.Markdown()
            t_btn.click(terra_assess, [t_soil, t_ph, t_moist, t_org, t_turb, t_wph, t_no3], t_out)

        # ── Product 12: Lithos-OS ─────────────────────────────────────────────
        with gr.Tab("12 · Lithos-OS 💎"):
            gr.Markdown("## Lithos-OS — Mineral & Gemstone Identifier\n**Product 12** · Property-matrix scoring identification.")
            with gr.Row():
                with gr.Column():
                    l_h = gr.Slider(1.0, 10.0, value=7.0, step=0.5, label="Hardness (Mohs)")
                    l_lust = gr.Dropdown(["vitreous", "metallic", "pearly", "adamantine", "waxy", "resinous"],
                                         label="Luster", value="vitreous")
                    l_clv = gr.Textbox(label="Cleavage description", placeholder="e.g. perfect cubic")
                    l_sg = gr.Slider(1.0, 8.0, value=2.65, step=0.05, label="Specific gravity")
                    l_color = gr.Textbox(label="Color", placeholder="e.g. colorless, white")
                    l_streak = gr.Textbox(label="Streak color", placeholder="e.g. white")
                    l_btn = gr.Button("Identify mineral", variant="primary")
                with gr.Column():
                    l_out = gr.Markdown()
            l_btn.click(lithos_identify, [l_h, l_lust, l_clv, l_sg, l_color, l_streak], l_out)

        # ── Product 13: DelPhi ────────────────────────────────────────────────
        with gr.Tab("13 · DelPhi 🔮"):
            gr.Markdown("## DelPhi — Oracle Divination Suite\n**Product 13** · Tarot, I Ching, Numerology, φ-Synthesis.\n*Contemplative tool — not predictions or advice.*")
            with gr.Row():
                with gr.Column():
                    d_q = gr.Textbox(label="Your question (optional)", placeholder="What should I focus on this month?")
                    d_mode = gr.Radio(["Tarot", "I Ching", "Numerology", "Phi Synthesis", "Combined"],
                                      label="Mode", value="Combined")
                    d_seed = gr.Slider(0, 9999, value=0, step=1, label="Seed (0 = random)")
                    d_btn = gr.Button("Begin reading", variant="primary")
                with gr.Column():
                    d_out = gr.Markdown()
            d_btn.click(delphi_reading, [d_q, d_mode, d_seed], d_out)

        # ── Product 14: SDAM ──────────────────────────────────────────────────
        with gr.Tab("14 · SDAM 📻"):
            gr.Markdown("## SDAM — Software-Defined Acoustic Modem\n**Product 14** · OFDM-over-audio simulation. Text encoding, waveform metadata, hex payload.")
            with gr.Row():
                with gr.Column():
                    s_text = gr.Textbox(label="Text to encode", placeholder="Hello, acoustic world!")
                    s_freq = gr.Slider(1000, 8000, value=3000, step=100, label="Center frequency (Hz)")
                    s_bw = gr.Slider(100, 4000, value=1000, step=100, label="Bandwidth (Hz)")
                    s_sub = gr.Slider(4, 256, value=32, step=4, label="Subcarriers")
                    s_btn = gr.Button("Encode & simulate", variant="primary")
                with gr.Column():
                    s_out = gr.Markdown()
            s_btn.click(sdam_encode, [s_text, s_freq, s_bw, s_sub], s_out)

        # ── Product 15: Pentacorder ───────────────────────────────────────────
        with gr.Tab("15 · Pentacorder 📡"):
            gr.Markdown("## Pentacorder — 5-Pillar Field Scanner\n**Product 15** · 5-sensor scan with Pentad axiom alignment check.")
            with gr.Row():
                with gr.Column():
                    pc_temp = gr.Slider(200, 500, value=300, step=5, label="Temperature (K)")
                    pc_press = gr.Slider(80000, 120000, value=101325, step=100, label="Pressure (Pa)")
                    pc_em = gr.Slider(0, 500, value=10, step=5, label="EM field (V/m)")
                    pc_phi = gr.Slider(0.0, 3.0, value=round(PHI, 3), step=0.001, label="φ-field (φ-units)")
                    pc_cons = gr.Slider(0.0, 1.0, value=round(XI_C, 3), step=0.001, label="Consciousness metric (Ξ_c)")
                    pc_btn = gr.Button("Run 5-pillar scan", variant="primary")
                with gr.Column():
                    pc_out = gr.Markdown()
            pc_btn.click(pentacorder_scan, [pc_temp, pc_press, pc_em, pc_phi, pc_cons], pc_out)

        # ── Product 16: Oracle ────────────────────────────────────────────────
        with gr.Tab("16 · Oracle 🌀"):
            gr.Markdown("## Oracle — Grand Synthesis Engine\n**Product 16** · Full synthesis score vs UM predictions.")
            with gr.Row():
                with gr.Column():
                    o_ns = gr.Slider(0.90, 1.00, value=0.9649, step=0.0001, label="Observed n_s (CMB spectral index)")
                    o_r = gr.Slider(0.0, 0.10, value=0.020, step=0.001, label="Observed r (tensor-to-scalar)")
                    o_beta = gr.Slider(0.0, 0.5, value=0.30, step=0.001, label="Observed β (birefringence, degrees)")
                    o_wa = gr.Slider(-1.0, 1.0, value=0.0, step=0.01, label="Observed w_a (dark energy EoS)")
                    o_btn = gr.Button("Compute synthesis score", variant="primary")
                with gr.Column():
                    o_out = gr.Markdown()
            o_btn.click(oracle_synthesis, [o_ns, o_r, o_beta, o_wa], o_out)

        # ── Product 17: Falsification Observatory ─────────────────────────────
        with gr.Tab("17 · Falsification Obs. 🔭"):
            gr.Markdown("## Falsification Observatory\n**Product 17** · Track all 7 falsification experiments. Epistemic honesty — no cherry-picking.")
            with gr.Row():
                with gr.Column():
                    fo_exp = gr.Dropdown(list(EXPERIMENTS.keys()), label="Select experiment",
                                         value=list(EXPERIMENTS.keys())[0])
                    fo_btn = gr.Button("View experiment", variant="primary")
                    fo_all_btn = gr.Button("Overview: all experiments", variant="secondary")
                with gr.Column():
                    fo_out = gr.Markdown()
            fo_btn.click(falsification_status, [fo_exp], fo_out)
            fo_all_btn.click(falsification_overview, [], fo_out)
            demo.load(falsification_overview, [], fo_out)

        # ── Product 18: Interrogator ──────────────────────────────────────────
        with gr.Tab("18 · Interrogator 🔬"):
            gr.Markdown("## Interrogator — UM Physics Q&A\n**Product 18** · Ask anything about the Unitary Manifold.")
            with gr.Row():
                with gr.Column():
                    i_q = gr.Textbox(label="Question", placeholder="What is the primary falsification condition?")
                    i_ai = gr.Checkbox(label="Use OX Alpha AI (requires OPENROUTER_API_KEY)", value=False)
                    i_btn = gr.Button("Ask Interrogator", variant="primary")
                    gr.Markdown("**Quick questions:**")
                    for kb_q in list(INTERROGATOR_KB.keys())[:5]:
                        gr.Button(kb_q[:60], size="sm").click(
                            lambda q=kb_q: interrogator_query(q, False), [], gr.Markdown()
                        )
                with gr.Column():
                    i_out = gr.Markdown()
            i_btn.click(interrogator_query, [i_q, i_ai], i_out)

        # ── Product 19: Flashcard Trainer ─────────────────────────────────────
        with gr.Tab("19 · Flashcard Trainer 🃏"):
            gr.Markdown(f"## Flashcard Trainer — UM Physics Education\n**Product 19** · {len(FLASHCARDS)} cards covering key UM concepts.")
            fc_idx = gr.State(0)
            with gr.Row():
                with gr.Column():
                    fc_card = gr.Markdown()
                    fc_answer = gr.Markdown()
                with gr.Column():
                    fc_reveal_btn = gr.Button("Reveal answer", variant="secondary")
                    fc_next_btn = gr.Button("Next card →", variant="primary")
            fc_next_btn.click(flashcard_next, [fc_idx], [fc_card, fc_answer, fc_idx])
            fc_reveal_btn.click(flashcard_reveal, [fc_idx], [fc_card, fc_idx])
            demo.load(flashcard_init, [], [fc_card, fc_idx])

        # ── Product 20: OX Navigator ──────────────────────────────────────────
        with gr.Tab("20 · OX Navigator 🦉"):
            gr.Markdown("## OX Navigator — Extended AI Memory\n"
                        "**Product 20** · OX Alpha holds the FULL UM repository as a single coherent thought.\n"
                        "Requires `OPENROUTER_API_KEY` environment variable.")
            with gr.Row():
                with gr.Column():
                    ox_ctx = gr.Textbox(label="Context / session tag (optional)", placeholder="research-session-001")
                    ox_q = gr.Textbox(label="Query", lines=3, placeholder="Explain the relationship between Pillar 56 and φ₀ closure.")
                    ox_btn = gr.Button("Query OX Alpha", variant="primary")
                    ox_clr_btn = gr.Button("Clear thread", variant="secondary")
                with gr.Column():
                    ox_chat = gr.Chatbot(label="OX Navigator — Extended Memory Thread", height=500)
            ox_stat = gr.Textbox(label="Status", interactive=False)
            ox_btn.click(ox_navigate, [ox_q, ox_ctx, ox_chat], [ox_chat, ox_stat])
            ox_clr_btn.click(ox_clear, [], [ox_chat, ox_stat])

    gr.Markdown(
        f"---\n"
        f"*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876 · {VERSION} · "
        f"[axiomzerospc.org](https://axiomzerospc.org) · "
        f"[GitHub](https://github.com/wuzbak/Unitary-Manifold-) · "
        f"Open science artifact under Defensive Public Commons License v1.0*"
    )

if __name__ == "__main__":
    demo.launch()
