# hf-spaces/az-os/app.py
# AxiomZero OS Environment — Hugging Face Space (Gradio)
#
# Unified OS environment: AxiomOS + Terra-OS + Lithos-OS
# Pulls from 12-AZ-IP/az-os/ and 11-AZ-OS/
#
# AxiomZero Technologies & Consulting, SPC — UBI 606 239 876

import os
import sys
import math
import json
import hashlib
import datetime
import numpy as np

try:
    import gradio as gr
except ImportError:
    sys.exit(1)

try:
    import httpx
    HTTPX_OK = True
except ImportError:
    HTTPX_OK = False

# ── Constants ─────────────────────────────────────────────────────────────────
WINDING_NUMBER = 5
K_CS = 74
BRAIDED_CS = 12 / 37
XI_C = 35 / 74
PHI = (1 + math.sqrt(5)) / 2
VERSION = "v24.1"
FOOTER = (
    "\n\n---\n"
    f"*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876 · {VERSION}*\n"
    "*Open science artifact under Defensive Public Commons License v1.0*"
)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OX_MODEL = "stealth/ox-alpha"

def ox_query(system: str, user: str, max_tokens: int = 2048) -> str:
    if not HTTPX_OK or not OPENROUTER_API_KEY:
        return "*OX Alpha unavailable — set OPENROUTER_API_KEY.*"
    try:
        resp = httpx.post(OPENROUTER_URL, json={
            "model": OX_MODEL, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
        }, headers={"Authorization": f"******",
                    "Content-Type": "application/json"}, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"*Error: {e}*"

# ══════════════════════════════════════════════════════════════════════════════
# AxiomOS — 7-Manager × 5-Sub-Agent Network
# ══════════════════════════════════════════════════════════════════════════════
AXIOM_OS_SYSTEM = """\
You are AxiomOS — the AZ-OS cognitive kernel (12-AZ-IP/az-os/).
Architecture: 7 manager agents × 5 sub-agents = 35-node AI network.
You maintain persistent memory, hierarchical goal trees, and φ-field belief states.

Managers:
1. MemoryManager — persistent session/long-term memory
2. GoalScheduler — hierarchical goal tree (φ-weighted priority)
3. BeliefEngine — KK-grounded belief update (Bayesian + φ-trust)
4. AgentCoordinator — routes tasks to sub-agents
5. StateMonitor — kernel-cognitive shared state
6. HILSBridge — Human-in-the-Loop Systems integration
7. PhiRouter — φ-field decision routing

Sub-agents: Analyst, Executor, Reflector, Synthesizer, Auditor

RULES: Cite pillar numbers. Never confabulate. No "ToE score" language.
Label all outputs with gate status.
"""

def axiom_os_run(goal: str, manager: str, memory_tag: str, history: list) -> tuple:
    if not goal.strip():
        return history, "Enter a goal."
    prompt = f"[MANAGER: {manager}] [TAG: {memory_tag or 'default'}]\n\n{goal}"
    resp = ox_query(AXIOM_OS_SYSTEM, prompt)
    history = (history or []) + [(goal, resp + FOOTER)]
    return history, ""

def axiom_os_state() -> str:
    """Show kernel state snapshot."""
    state = {
        "version": VERSION,
        "kernel": "AZ-OS v3.0 (12-AZ-IP/az-os/)",
        "architecture": "7 managers × 5 sub-agents",
        "phi_coupling": round(PHI, 6),
        "braided_cs": round(BRAIDED_CS, 6),
        "k_cs": K_CS,
        "n_w": WINDING_NUMBER,
        "xi_c": round(XI_C, 6),
        "hils_active": True,
        "memory_backend": "persistent_session",
        "state_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "open_gaps": [
            "CMB amplitude suppression ×4-7 (ARCHITECTURE_LIMIT)",
            "DESI Year 2 tension (w_a≠0)",
        ],
    }
    lines = [
        "## AxiomOS — Kernel State Snapshot",
        "```json",
        json.dumps(state, indent=2),
        "```",
        FOOTER,
    ]
    return "\n".join(lines)

def phi_decision_engine(decision_input: str, options: str, phi_weight: float) -> str:
    """φ-field decision routing (12-AZ-IP/az-os/phi_decision_engine.py)."""
    opts = [o.strip() for o in options.split(",") if o.strip()]
    if not opts:
        return "Enter at least one option (comma-separated)."

    # φ-weighted scoring
    phi_n = PHI
    scores = []
    for i, opt in enumerate(opts):
        # Score = φ^(-i) * (hash-based pseudo-score) * phi_weight
        h = int(hashlib.md5((decision_input + opt).encode()).hexdigest(), 16)
        base = (h % 1000) / 1000
        score = base * phi_n**(-i) * phi_weight
        scores.append((opt, score))
        phi_n = phi_n  # reset for next

    scores.sort(key=lambda x: x[1], reverse=True)
    best_opt, best_score = scores[0]

    lines = [
        "## AZ-OS φ-Decision Engine",
        f"**Source:** `12-AZ-IP/az-os/phi_decision_engine.py`",
        f"**Gate:** ADJACENT_TRACK",
        "",
        f"**Input:** {decision_input}",
        f"**φ-weight:** {phi_weight:.4f}",
        "",
        "### Option Scores (φ-weighted)",
        "| Option | φ-score | Rank |",
        "|--------|---------|------|",
    ]
    for rank, (opt, sc) in enumerate(scores, 1):
        lines.append(f"| {opt} | {sc:.5f} | #{rank} |")
    lines += [
        "",
        f"**Decision:** ✅ **{best_opt}** (score: {best_score:.5f})",
        "",
        "*φ-decision routing weights options by powers of φ = (1+√5)/2.*",
        "*Not a deterministic logic rule — a probabilistic φ-field heuristic.*",
        FOOTER,
    ]
    return "\n".join(lines)

def hils_status(n_operators: int, saturation_check: bool) -> str:
    """HILS framework status (12-AZ-IP/az-os/hils.py)."""
    threshold = 15  # HIL_PHASE_SHIFT_THRESHOLD
    sentinel = BRAIDED_CS  # per axiom
    total_capacity = n_operators * sentinel
    aligned = n_operators >= threshold

    lines = [
        "## AZ-OS HILS Status",
        f"**Source:** `12-AZ-IP/az-os/hils.py` · Gate: GOVERNANCE",
        "",
        f"| Parameter | Value |",
        f"|-----------|-------|",
        f"| HIL operators | {n_operators} |",
        f"| Phase threshold | {threshold} |",
        f"| Sentinel capacity | {sentinel:.5f} per operator |",
        f"| Total capacity | {total_capacity:.5f} |",
        f"| Phase aligned | {'✅ YES' if aligned else '⚠️ NO (n < 15)'} |",
        "",
        f"**Status:** {'🟢 HILS ACTIVE' if aligned else '🟡 HILS PARTIAL (build to n≥15)'}",
        "",
        "**Reminder:** HILS is a governance framework — independent of UM physics.",
        "It borrows mathematical structure but does NOT depend on physics being correct.",
        FOOTER,
    ]
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# Terra-OS — Soil & Water (duplicated from az-tools for unified OS)
# ══════════════════════════════════════════════════════════════════════════════
def terra_full_report(soil_type: str, ph: float, moisture: float, organic: float,
                      turbidity: float, water_ph: float, nitrates: float,
                      location: str, date: str) -> str:
    """Full Terra-OS environmental report."""
    from datetime import date as ddate
    report_date = date or ddate.today().isoformat()

    soil_scores = {
        "Loam": 85, "Clay": 65, "Sandy": 55, "Silt": 70, "Peat": 60
    }
    base_score = soil_scores.get(soil_type, 70)
    ph_adj = max(-20, min(0, -abs(ph - 6.5) * 10))
    org_adj = min(15, organic * 3)
    moist_adj = max(-10, min(5, -abs(moisture - 40) * 0.2))
    soil_health = max(0, min(100, base_score + ph_adj + org_adj + moist_adj))

    wqi_turb = max(0, 100 - turbidity * 10)
    wqi_ph = max(0, 100 - abs(water_ph - 7.0) * 20)
    wqi_no3 = max(0, 100 - max(0, nitrates - 5) * 10)
    wqi = (wqi_turb + wqi_ph + wqi_no3) / 3

    overall = "EXCELLENT" if (soil_health > 75 and wqi > 80) else \
              "ADEQUATE" if (soil_health > 55 and wqi > 60) else "NEEDS REMEDIATION"

    report = [
        f"# Terra-OS Environmental Report",
        f"**Location:** {location or 'Not specified'} | **Date:** {report_date}",
        f"**Gate:** ADJACENT_TRACK · Product 11",
        "",
        f"## Soil Assessment — {soil_type}",
        f"| Indicator | Value | Score |",
        f"|-----------|-------|-------|",
        f"| pH | {ph:.1f} | {'✅' if 6.0 <= ph <= 7.5 else '⚠️'} |",
        f"| Organic matter | {organic:.1f}% | {'✅' if organic >= 3 else '⚠️'} |",
        f"| Moisture | {moisture:.0f}% | {'✅' if 30 <= moisture <= 55 else '⚠️'} |",
        f"**Soil health index: {soil_health:.0f}/100**",
        "",
        f"## Water Quality",
        f"| Parameter | Value | WHO Limit | Status |",
        f"|-----------|-------|-----------|--------|",
        f"| Turbidity | {turbidity:.1f} NTU | 4 NTU | {'✅' if turbidity < 4 else '❌'} |",
        f"| pH | {water_ph:.1f} | 6.5–8.5 | {'✅' if 6.5 <= water_ph <= 8.5 else '❌'} |",
        f"| Nitrates | {nitrates:.1f} mg/L | 10 mg/L | {'✅' if nitrates < 10 else '❌'} |",
        f"**Water quality index: {wqi:.0f}/100**",
        "",
        f"## Overall Assessment: **{overall}**",
        f"Soil health: {soil_health:.0f}/100 | Water quality: {wqi:.0f}/100",
        FOOTER,
    ]
    return "\n".join(report)

# ══════════════════════════════════════════════════════════════════════════════
# Lithos-OS — Mineral Identifier (enhanced version)
# ══════════════════════════════════════════════════════════════════════════════
EXTENDED_MINERAL_DB = {
    "Quartz": {"H": 7.0, "SG": 2.65, "luster": "vitreous", "streak": "white", "system": "trigonal",
               "formula": "SiO₂", "uses": "Glass, electronics, gemstones"},
    "Feldspar (Orthoclase)": {"H": 6.0, "SG": 2.56, "luster": "vitreous", "streak": "white", "system": "monoclinic",
               "formula": "KAlSi₃O₈", "uses": "Ceramics, glass"},
    "Calcite": {"H": 3.0, "SG": 2.71, "luster": "vitreous", "streak": "white", "system": "trigonal",
               "formula": "CaCO₃", "uses": "Cement, lime, antacid"},
    "Pyrite": {"H": 6.2, "SG": 5.01, "luster": "metallic", "streak": "greenish-black", "system": "cubic",
               "formula": "FeS₂", "uses": "Sulfuric acid, pigment"},
    "Mica (Muscovite)": {"H": 2.5, "SG": 2.83, "luster": "pearly", "streak": "white", "system": "monoclinic",
               "formula": "KAl₂(AlSi₃O₁₀)(OH)₂", "uses": "Electronics, pigment"},
    "Olivine": {"H": 6.5, "SG": 3.3, "luster": "vitreous", "streak": "colorless", "system": "orthorhombic",
               "formula": "(Mg,Fe)₂SiO₄", "uses": "Refractory, gemstone (peridot)"},
    "Garnet (Almandine)": {"H": 7.5, "SG": 4.3, "luster": "vitreous", "streak": "white", "system": "cubic",
               "formula": "Fe₃Al₂(SiO₄)₃", "uses": "Abrasive, gemstone"},
    "Diamond": {"H": 10.0, "SG": 3.52, "luster": "adamantine", "streak": "none", "system": "cubic",
               "formula": "C", "uses": "Cutting tools, gemstone"},
    "Halite": {"H": 2.5, "SG": 2.16, "luster": "vitreous", "streak": "white", "system": "cubic",
               "formula": "NaCl", "uses": "Food seasoning, chemical industry"},
    "Magnetite": {"H": 5.5, "SG": 5.18, "luster": "metallic", "streak": "black", "system": "cubic",
               "formula": "Fe₃O₄", "uses": "Iron ore, magnetic media"},
    "Corundum (Ruby/Sapphire)": {"H": 9.0, "SG": 4.0, "luster": "vitreous", "streak": "white", "system": "trigonal",
               "formula": "Al₂O₃", "uses": "Gemstone, abrasive, laser rods"},
    "Fluorite": {"H": 4.0, "SG": 3.18, "luster": "vitreous", "streak": "white", "system": "cubic",
               "formula": "CaF₂", "uses": "Flux in steelmaking, optics"},
}

def lithos_extended(hardness: float, sg: float, luster: str, color: str) -> str:
    """Extended mineral identification with full database."""
    scores = {}
    for name, props in EXTENDED_MINERAL_DB.items():
        s = 0
        if abs(props["H"] - hardness) <= 0.5: s += 35
        elif abs(props["H"] - hardness) <= 1.0: s += 15
        if abs(props["SG"] - sg) <= 0.3: s += 35
        elif abs(props["SG"] - sg) <= 0.8: s += 15
        if luster.lower() in props["luster"]: s += 20
        if any(c in color.lower() for c in ["white", "clear", "colorless"]): s += 5
        scores[name] = s

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:6]
    top_name, top_score = ranked[0]
    top_props = EXTENDED_MINERAL_DB.get(top_name, {})
    conf = "HIGH" if top_score >= 75 else "MEDIUM" if top_score >= 45 else "LOW"

    lines = [
        "## 💎 Lithos-OS — Extended Mineral Identification",
        f"**Product 12** | H={hardness}, SG={sg}, luster={luster}, color={color}",
        "",
        "### Top Matches",
        "| Rank | Mineral | Formula | H | SG | Match |",
        "|------|---------|---------|---|-----|-------|",
    ]
    for i, (name, sc) in enumerate(ranked, 1):
        p = EXTENDED_MINERAL_DB[name]
        lines.append(f"| {i} | {name} | {p['formula']} | {p['H']} | {p['SG']} | {sc}/100 |")

    lines += [
        "",
        f"**Best match:** {top_name} (confidence: {conf})",
        f"**Formula:** {top_props.get('formula', 'N/A')}",
        f"**Crystal system:** {top_props.get('system', 'N/A')}",
        f"**Uses:** {top_props.get('uses', 'N/A')}",
        "",
        "*Lab analysis (XRD/SEM/EDX) required for definitive identification.*",
        FOOTER,
    ]
    return "\n".join(lines)

# ── Gradio UI ─────────────────────────────────────────────────────────────────
THEME = gr.themes.Base(
    primary_hue="purple", secondary_hue="blue",
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
)

HEADER = f"""
<div style="text-align:center; padding:1rem 0; border-bottom:1px solid #1a2a4a; margin-bottom:1rem;">
  <h1 style="font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#e8ecf4,#7c4dff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:.3rem;">
    🖥️ AZ-OS Environment
  </h1>
  <p style="color:#7a8ba8; font-size:.9rem;">
    AxiomOS · Terra-OS · Lithos-OS · {VERSION} ·
    <a href="https://axiomzerospc.org" style="color:#7c4dff;" target="_blank">axiomzerospc.org</a>
  </p>
</div>
"""

with gr.Blocks(theme=THEME, title="AZ-OS Environment") as demo:
    gr.HTML(HEADER)

    with gr.Tabs():

        # AxiomOS
        with gr.Tab("AxiomOS 🧠"):
            gr.Markdown("## AxiomOS — Persistent AI Cognitive Layer\n"
                        "7-Manager × 5-Sub-Agent network · Source: `12-AZ-IP/az-os/`")
            with gr.Tabs():
                with gr.Tab("Agent Query"):
                    with gr.Row():
                        with gr.Column():
                            ao_goal = gr.Textbox(label="Goal / directive", lines=4)
                            ao_mgr = gr.Dropdown(
                                ["MemoryManager", "GoalScheduler", "BeliefEngine",
                                 "AgentCoordinator", "StateMonitor", "HILSBridge", "PhiRouter"],
                                label="Route to manager", value="AgentCoordinator")
                            ao_tag = gr.Textbox(label="Memory tag", placeholder="session-001")
                            ao_btn = gr.Button("Submit to AxiomOS", variant="primary")
                        with gr.Column():
                            ao_chat = gr.Chatbot(height=400)
                    ao_stat = gr.Textbox(interactive=False)
                    ao_btn.click(axiom_os_run, [ao_goal, ao_mgr, ao_tag, ao_chat], [ao_chat, ao_stat])

                with gr.Tab("Kernel State"):
                    ks_btn = gr.Button("Load state", variant="primary")
                    ks_out = gr.Markdown()
                    ks_btn.click(axiom_os_state, [], ks_out)
                    demo.load(axiom_os_state, [], ks_out)

                with gr.Tab("φ-Decision Engine"):
                    with gr.Row():
                        pd_input = gr.Textbox(label="Decision context", placeholder="Which research direction should we prioritize?")
                        pd_opts = gr.Textbox(label="Options (comma-separated)", placeholder="Birefringence study, VQE sandbox, IP expansion")
                        pd_phi = gr.Slider(0.1, 2.0, value=PHI, step=0.01, label="φ-weight")
                    pd_btn = gr.Button("Route decision", variant="primary")
                    pd_out = gr.Markdown()
                    pd_btn.click(phi_decision_engine, [pd_input, pd_opts, pd_phi], pd_out)

                with gr.Tab("HILS Status"):
                    with gr.Row():
                        hl_n = gr.Slider(1, 30, value=12, step=1, label="HIL operators active")
                        hl_sat = gr.Checkbox(label="Check saturation (n≥15)", value=True)
                    hl_btn = gr.Button("Check HILS status", variant="primary")
                    hl_out = gr.Markdown()
                    hl_btn.click(hils_status, [hl_n, hl_sat], hl_out)

        # Terra-OS
        with gr.Tab("Terra-OS 🌱"):
            gr.Markdown("## Terra-OS — Soil & Water Expert System · Product 11")
            with gr.Row():
                with gr.Column():
                    tr_soil = gr.Dropdown(["Loam", "Clay", "Sandy", "Silt", "Peat"], value="Loam", label="Soil type")
                    tr_ph = gr.Slider(3.0, 9.0, value=6.5, step=0.1, label="Soil pH")
                    tr_moist = gr.Slider(0, 100, value=35, label="Moisture (%)")
                    tr_org = gr.Slider(0, 10, value=3.5, step=0.1, label="Organic matter (%)")
                    tr_turb = gr.Slider(0, 20, value=1.5, step=0.5, label="Turbidity (NTU)")
                    tr_wph = gr.Slider(5.0, 10.0, value=7.2, step=0.1, label="Water pH")
                    tr_no3 = gr.Slider(0, 50, value=4.0, step=0.5, label="Nitrates (mg/L)")
                    tr_loc = gr.Textbox(label="Location (optional)")
                    tr_date = gr.Textbox(label="Date (YYYY-MM-DD, optional)")
                    tr_btn = gr.Button("Generate full report", variant="primary")
                with gr.Column():
                    tr_out = gr.Markdown()
            tr_btn.click(terra_full_report, [tr_soil, tr_ph, tr_moist, tr_org, tr_turb, tr_wph, tr_no3, tr_loc, tr_date], tr_out)

        # Lithos-OS
        with gr.Tab("Lithos-OS 💎"):
            gr.Markdown("## Lithos-OS — Mineral & Gemstone Identifier · Product 12\n12-mineral extended database.")
            with gr.Row():
                with gr.Column():
                    li_h = gr.Slider(1.0, 10.0, value=7.0, step=0.5, label="Hardness (Mohs)")
                    li_sg = gr.Slider(1.5, 8.0, value=2.65, step=0.05, label="Specific gravity")
                    li_lust = gr.Dropdown(["vitreous", "metallic", "pearly", "adamantine", "waxy"],
                                          value="vitreous", label="Luster")
                    li_color = gr.Textbox(label="Color", placeholder="colorless, white, gray")
                    li_btn = gr.Button("Identify mineral", variant="primary")
                with gr.Column():
                    li_out = gr.Markdown()
            li_btn.click(lithos_extended, [li_h, li_sg, li_lust, li_color], li_out)

    gr.Markdown(
        f"---\n*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876 · {VERSION} · "
        f"[GitHub](https://github.com/wuzbak/Unitary-Manifold-)*"
    )

if __name__ == "__main__":
    demo.launch()
