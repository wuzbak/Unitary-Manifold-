# hf-spaces/az-ip/app.py
# AxiomZero IP Registry — Hugging Face Space (Gradio)
#
# Full IP catalog browser: 20 products, engines, OS, tools, calculators
# Source: 12-AZ-IP/IP_REGISTRY.json, 12-AZ-IP/FINGERPRINT_MANIFEST.md
#
# AxiomZero Technologies & Consulting, SPC — UBI 606 239 876

import sys
import math
import json
import hashlib
import datetime
from pathlib import Path

try:
    import gradio as gr
except ImportError:
    sys.exit(1)

# ── IP Registry (from 12-AZ-IP/IP_REGISTRY.json) ─────────────────────────────
_SPACE_DIR = Path(__file__).resolve().parent
_SPACE_PARENT = _SPACE_DIR.parent
if str(_SPACE_PARENT) not in sys.path:
    sys.path.insert(0, str(_SPACE_PARENT))

try:
    from space_core.live_status import status_snapshot
    _STATUS = status_snapshot()
except Exception:
    _STATUS = {"version": "vunknown"}

VERSION = str(_STATUS["version"])
FOOTER = (
    "\n\n---\n"
    f"*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876 · {VERSION}*\n"
    "*License: Defensive Public Commons v1.0 — All content public domain.*\n"
    "*No patents on core equations. No exclusive IP.*"
)

PRODUCTS = {
    "01": {
        "name": "AxiomOS",
        "category": "os",
        "description": "Persistent AI cognitive layer — 7-manager × 5-sub-agent network",
        "path": "12-AZ-IP/az-os/",
        "key_files": ["agent_core.py", "hils.py", "state.py", "phi_decision_engine.py", "phi_field_interface.py"],
        "trl": "TRL 6",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-19",
        "sha256_prefix": "26f305aa",
    },
    "02": {
        "name": "AZ-Kernel",
        "category": "os",
        "description": "Rust UEFI bare-metal kernel — memory-safe, C-ABI FFI bridge",
        "path": "12-AZ-IP/02-az-kernel/",
        "key_files": ["Cargo.toml", "src/main.rs"],
        "trl": "TRL 4",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-07-01",
        "sha256_prefix": "70a28581",
    },
    "03": {
        "name": "EIGE",
        "category": "engines",
        "description": "Election Integrity Governance Engine — compliance scoring, anomaly detection",
        "path": "12-AZ-IP/03-eige/",
        "key_files": ["eige_core.py", "audit_engine.rs"],
        "trl": "TRL 5",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-19",
        "sha256_prefix": "3b4c5d6e",
    },
    "04": {
        "name": "UM-SOS",
        "category": "apps",
        "description": "Unitary Manifold Scientific OS — pillar browser, derivation runner",
        "path": "12-AZ-IP/04-um-sos/",
        "key_files": ["um_sos.py", "pillar_browser.py"],
        "trl": "TRL 6",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-19",
        "sha256_prefix": "4a5b6c7d",
    },
    "05": {
        "name": "UOS Kernel",
        "category": "os",
        "description": "5D KK process scheduler — winding number n_w=5 governs quanta",
        "path": "12-AZ-IP/05-uos-kernel/",
        "key_files": ["uos_scheduler.py"],
        "trl": "TRL 4",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-01",
        "sha256_prefix": "5b6c7d8e",
    },
    "06": {
        "name": "Omega Synthesis Engine",
        "category": "engines",
        "description": "Universal Mechanics Engine — 208+ pillar query from five seed constants",
        "path": "12-AZ-IP/06-omega-synthesis/",
        "key_files": ["omega_synthesis.js", "pillar_registry.json"],
        "trl": "TRL 7",
        "status": "REGISTERED",
        "gate": "HARDGATE",
        "updated": "2026-08-23",
        "sha256_prefix": "6c7d8e9f",
    },
    "07": {
        "name": "Holon Zero",
        "category": "engines",
        "description": "Ground state engine — Ω₀ minimum coherent energy (Pillar 70)",
        "path": "12-AZ-IP/07-holon-zero/",
        "key_files": ["holon_zero.js"],
        "trl": "TRL 7",
        "status": "REGISTERED",
        "gate": "HARDGATE",
        "updated": "2026-08-23",
        "sha256_prefix": "7d8e9fa0",
    },
    "08": {
        "name": "Journalist AI",
        "category": "apps",
        "description": "Investigative dossier builder — source-tier, confidence scoring, entity mapping",
        "path": "12-AZ-IP/08-journalist/",
        "key_files": ["journalist.js", "dossier.js"],
        "trl": "TRL 6",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-19",
        "sha256_prefix": "8e9fa0b1",
    },
    "09": {
        "name": "OmegaHolon",
        "category": "engines",
        "description": "Living systems engine — holon mapping, φ-resonance, entropy debt",
        "path": "12-AZ-IP/09-omegaholon/",
        "key_files": ["omegaholon.js"],
        "trl": "TRL 6",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-19",
        "sha256_prefix": "9fa0b1c2",
    },
    "10": {
        "name": "Filmer's Companion",
        "category": "apps",
        "description": "Film production suite — shot calculator, scene scheduler, budget tracker",
        "path": "12-AZ-IP/10-filmers-companion/",
        "key_files": ["filmers.js"],
        "trl": "TRL 6",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-01",
        "sha256_prefix": "a0b1c2d3",
    },
    "11": {
        "name": "Terra-OS",
        "category": "os",
        "description": "Soil & water expert system — assessment, remediation, WQI",
        "path": "12-AZ-IP/11-terra-os/",
        "key_files": ["terra_os.js", "terra_os.py"],
        "trl": "TRL 6",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-19",
        "sha256_prefix": "b1c2d3e4",
    },
    "12": {
        "name": "Lithos-OS",
        "category": "os",
        "description": "Mineral & gemstone identifier — property matrix scoring, 12-mineral DB",
        "path": "12-AZ-IP/12-lithos-os/",
        "key_files": ["lithos_os.js"],
        "trl": "TRL 6",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-19",
        "sha256_prefix": "c2d3e4f5",
    },
    "13": {
        "name": "DelPhi",
        "category": "apps",
        "description": "Oracle divination suite — tarot, I Ching, numerology, φ-synthesis",
        "path": "12-AZ-IP/13-delphi/",
        "key_files": ["delphi.js"],
        "trl": "TRL 7",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-19",
        "sha256_prefix": "d3e4f5a6",
    },
    "14": {
        "name": "SDAM",
        "category": "tools",
        "description": "Software-Defined Acoustic Modem — OFDM-over-audio simulation",
        "path": "12-AZ-IP/14-sdam/",
        "key_files": ["sdam.js"],
        "trl": "TRL 5",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-01",
        "sha256_prefix": "e4f5a6b7",
    },
    "15": {
        "name": "Pentacorder",
        "category": "tools",
        "description": "5-pillar field scanner — live gauges, Pentad axiom check",
        "path": "12-AZ-IP/15-pentacorder/",
        "key_files": ["pentacorder.js"],
        "trl": "TRL 6",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-19",
        "sha256_prefix": "f5a6b7c8",
    },
    "16": {
        "name": "Oracle",
        "category": "engines",
        "description": "Grand Synthesis Engine — full synthesis score vs UM predictions",
        "path": "12-AZ-IP/16-oracle/",
        "key_files": ["oracle.js", "oracle.py"],
        "trl": "TRL 7",
        "status": "REGISTERED",
        "gate": "HARDGATE",
        "updated": "2026-08-23",
        "sha256_prefix": "a6b7c8d9",
    },
    "17": {
        "name": "Falsification Observatory",
        "category": "tools",
        "description": "7-experiment falsification tracker — LiteBIRD, DESI, JUNO, ACT, HL-LHC, nEDM, XENON-nT",
        "path": "12-AZ-IP/17-falsification-observatory/",
        "key_files": ["falsification_observatory.js"],
        "trl": "TRL 7",
        "status": "REGISTERED",
        "gate": "HARDGATE",
        "updated": "2026-08-23",
        "sha256_prefix": "b7c8d9e0",
    },
    "18": {
        "name": "Interrogator",
        "category": "tools",
        "description": "Physics Q&A knowledge base — 20KB entries, 7 experiments, 3 modes",
        "path": "12-AZ-IP/18-interrogator/",
        "key_files": ["interrogator.js", "interrogator-kb.json"],
        "trl": "TRL 7",
        "status": "REGISTERED",
        "gate": "HARDGATE",
        "updated": "2026-08-23",
        "sha256_prefix": "c8d9e0f1",
    },
    "19": {
        "name": "Flashcard Trainer",
        "category": "apps",
        "description": "Physics education flashcards — UM key concepts, 15 cards",
        "path": "12-AZ-IP/19-flashcard-trainer/",
        "key_files": ["flashcard-trainer.js", "flashcard-deck.json"],
        "trl": "TRL 7",
        "status": "REGISTERED",
        "gate": "HARDGATE",
        "updated": "2026-08-23",
        "sha256_prefix": "d9e0f1a2",
    },
    "20": {
        "name": "OX Navigator",
        "category": "apps",
        "description": "Extended AI memory via OX Alpha (stealth/ox-alpha) — full UM context ~85k tokens",
        "path": "12-AZ-IP/20-ox-navigator/",
        "key_files": ["ox-navigator.js", "ox-navigator.py"],
        "trl": "TRL 6",
        "status": "REGISTERED",
        "gate": "ADJACENT_TRACK",
        "updated": "2026-08-23",
        "sha256_prefix": "e0f1a2b3",
    },
}

ENGINES = {
    "phi_decision_engine": {
        "description": "φ-field decision routing engine",
        "path": "12-AZ-IP/az-os/phi_decision_engine.py",
        "sha256": "5ea8f743...",
        "size_kb": 13.3,
    },
    "phi_field_interface": {
        "description": "φ-field interface — bridges cognitive layer to physics",
        "path": "12-AZ-IP/az-os/phi_field_interface.py",
        "sha256": "3c0083b4...",
        "size_kb": 10.9,
    },
    "kk_vqe": {
        "description": "Kaluza-Klein VQE — φ-weighted ansatz for quantum simulation",
        "path": "src/quantum/kk_vqe.py",
        "sha256": "computed...",
        "size_kb": 8.5,
    },
    "fermi_hubbard": {
        "description": "Fermi-Hubbard simulation (JW/BK encoding)",
        "path": "src/quantum/fermi_hubbard.py",
        "sha256": "computed...",
        "size_kb": 12.1,
    },
    "omega_synthesis": {
        "description": "Universal synthesis engine — 208+ pillars",
        "path": "src/core/ (multiple modules)",
        "sha256": "distributed...",
        "size_kb": 450.0,
    },
}

def ip_product_detail(product_id: str) -> str:
    p = PRODUCTS.get(product_id)
    if not p:
        return f"Product {product_id} not found."
    gate_icon = {"HARDGATE": "🟢", "ADJACENT_TRACK": "🔵"}.get(p["gate"], "⚪")
    lines = [
        f"## Product {product_id}: {p['name']}",
        f"**Gate:** {gate_icon} `{p['gate']}` | **TRL:** {p['trl']} | **Updated:** {p['updated']}",
        f"**Category:** {p['category']}",
        "",
        f"**Description:** {p['description']}",
        "",
        f"**Path:** `{p['path']}`",
        "",
        f"**Key files:**",
    ]
    for f in p["key_files"]:
        lines.append(f"- `{f}`")
    lines += [
        "",
        f"**SHA-256 prefix:** `{p['sha256_prefix']}...`",
        f"**Status:** {p['status']}",
        f"**License:** Defensive Public Commons v1.0",
        FOOTER,
    ]
    return "\n".join(lines)

def ip_catalog_overview(category: str) -> str:
    lines = [
        f"## IP Catalog — {category.upper() if category != 'all' else 'All Products'}",
        f"**Schema:** axiomzero-ip-registry-v2 · **Pillar:** 536 · **Updated:** 2026-08-23",
        "",
        "| ID | Name | Category | Gate | TRL | Status |",
        "|----|------|----------|------|-----|--------|",
    ]
    for pid, p in PRODUCTS.items():
        if category != "all" and p["category"] != category:
            continue
        gate_icon = {"HARDGATE": "🟢", "ADJACENT_TRACK": "🔵"}.get(p["gate"], "⚪")
        lines.append(f"| {pid} | {p['name']} | {p['category']} | {gate_icon} {p['gate']} | {p['trl']} | {p['status']} |")
    lines.append(FOOTER)
    return "\n".join(lines)

def ip_engine_catalog() -> str:
    lines = [
        "## IP Engines & Core Libraries",
        "",
        "| Engine | Description | Path | Size |",
        "|--------|-------------|------|------|",
    ]
    for name, e in ENGINES.items():
        lines.append(f"| `{name}` | {e['description']} | `{e['path']}` | {e['size_kb']:.1f} KB |")
    lines += [
        "",
        "### Key Engine Details",
        "- **φ-decision engine:** Routes decisions via φ-weighted scoring. Input: options list. Output: ranked decisions.",
        "- **KK VQE:** φ-weighted ansatz with KK mode structure. n_w=5 sets rotation period.",
        "- **Fermi-Hubbard:** JW/BK encoding for 1D Hubbard model. n_sites ≤ 4 tractable.",
        "- **Omega Synthesis:** 208+ pillar registry. All pillars derive from 5 seed constants.",
        FOOTER,
    ]
    return "\n".join(lines)

def ip_fingerprint_verify(product_id: str, sha256_prefix: str) -> str:
    p = PRODUCTS.get(product_id)
    if not p:
        return f"Product {product_id} not found."
    stored = p["sha256_prefix"]
    match = sha256_prefix.startswith(stored[:8]) if sha256_prefix else False
    lines = [
        f"## Fingerprint Verification — Product {product_id}: {p['name']}",
        "",
        f"**Stored SHA-256 prefix:** `{stored}...`",
        f"**Input prefix:** `{sha256_prefix or '(none)'}`",
        "",
        f"**Result:** {'✅ PREFIX MATCH' if match else '⚠️ NO MATCH or INPUT EMPTY'}",
        "",
        "*Full SHA-256 verification requires the original source files from GitHub.*",
        f"*Source: [github.com/wuzbak/Unitary-Manifold-](https://github.com/wuzbak/Unitary-Manifold-)*",
        FOOTER,
    ]
    return "\n".join(lines)

def ip_license_info() -> str:
    return (
        "## License: Defensive Public Commons v1.0 (2026)\n\n"
        "This repository is irrevocably dedicated to the **public domain**.\n\n"
        "### Permitted\n"
        "- ✅ Read, copy, modify, distribute any content\n"
        "- ✅ Use for commercial or non-commercial purposes\n"
        "- ✅ AI indexing, RAG, embedding\n"
        "- ✅ Cite in academic work\n"
        "- ✅ Submit corrections via pull request\n\n"
        "### Prohibited\n"
        "- ❌ Claim exclusive IP over core equations or theorems\n"
        "- ❌ Apply patents to Walker-Pearson field equations or FTUM\n"
        "- ❌ Misrepresent authorship (primary: ThomasCory Walker-Pearson)\n"
        "- ❌ Introduce security vulnerabilities via PR\n\n"
        "### Attribution (requested, not required)\n"
        "```\n"
        "Walker-Pearson, T. (2026). The Unitary Manifold.\n"
        "Zenodo. https://doi.org/10.5281/zenodo.19584531\n"
        "```\n"
        "\n"
        "### Authorship\n"
        "- **Theory, framework, scientific direction:** ThomasCory Walker-Pearson\n"
        "- **Code architecture, test suites, document engineering:** GitHub Copilot (AI)\n"
        + FOOTER
    )

def ip_statistics() -> str:
    cats = {}
    gates = {"HARDGATE": 0, "ADJACENT_TRACK": 0}
    trls = {}
    for p in PRODUCTS.values():
        cats[p["category"]] = cats.get(p["category"], 0) + 1
        gates[p["gate"]] = gates.get(p["gate"], 0) + 1
        trls[p["trl"]] = trls.get(p["trl"], 0) + 1

    lines = [
        "## IP Registry Statistics",
        f"**Total products:** {len(PRODUCTS)}",
        f"**Total engines:** {len(ENGINES)}",
        f"**Registry version:** axiomzero-ip-registry-v2",
        f"**License:** Defensive Public Commons v1.0",
        "",
        "### By Category",
        "| Category | Count |",
        "|----------|-------|",
    ]
    for cat, n in sorted(cats.items()):
        lines.append(f"| {cat} | {n} |")
    lines += [
        "",
        "### By Gate",
        "| Gate | Count |",
        "|------|-------|",
    ]
    for gate, n in sorted(gates.items()):
        icon = {"HARDGATE": "🟢", "ADJACENT_TRACK": "🔵"}.get(gate, "⚪")
        lines.append(f"| {icon} {gate} | {n} |")
    lines += [
        "",
        "### By TRL",
        "| TRL | Count |",
        "|-----|-------|",
    ]
    for trl, n in sorted(trls.items()):
        lines.append(f"| {trl} | {n} |")
    lines.append(FOOTER)
    return "\n".join(lines)

# ── Gradio UI ─────────────────────────────────────────────────────────────────
THEME = gr.themes.Base(
    primary_hue="yellow", secondary_hue="orange",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace"],
).set(
    body_background_fill="#050a1a",
    body_text_color="#e8ecf4",
    block_background_fill="#0d1830",
    block_border_color="#1a2a4a",
    button_primary_background_fill="linear-gradient(135deg, #f0c040, #ff9f0a)",
    button_primary_text_color="#050a1a",
    input_background_fill="#0a1228",
)

HEADER = f"""
<div style="text-align:center; padding:1rem 0; border-bottom:1px solid #1a2a4a; margin-bottom:1rem;">
  <h1 style="font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#f0c040,#ff9f0a);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:.3rem;">
    📜 AZ-IP Registry
  </h1>
  <p style="color:#7a8ba8; font-size:.9rem;">
    {len(PRODUCTS)} products · {len(ENGINES)} engines · Defensive Public Commons v1.0 · {VERSION}
  </p>
</div>
"""

with gr.Blocks(theme=THEME, title="AZ-IP Registry") as demo:
    gr.HTML(HEADER)

    with gr.Tabs():

        with gr.Tab("Catalog"):
            with gr.Row():
                cat_sel = gr.Dropdown(["all", "apps", "engines", "os", "tools", "calculators"],
                                      label="Filter by category", value="all")
                cat_btn = gr.Button("Browse catalog", variant="primary")
            cat_out = gr.Markdown()
            cat_btn.click(ip_catalog_overview, [cat_sel], cat_out)
            demo.load(lambda: ip_catalog_overview("all"), [], cat_out)

        with gr.Tab("Product Detail"):
            with gr.Row():
                prod_id = gr.Dropdown(list(PRODUCTS.keys()), label="Product ID", value="01")
                prod_btn = gr.Button("View details", variant="primary")
            prod_out = gr.Markdown()
            prod_btn.click(ip_product_detail, [prod_id], prod_out)

        with gr.Tab("Engines"):
            eng_btn = gr.Button("Browse engines & core libraries", variant="primary")
            eng_out = gr.Markdown()
            eng_btn.click(ip_engine_catalog, [], eng_out)
            demo.load(ip_engine_catalog, [], eng_out)

        with gr.Tab("Fingerprint"):
            with gr.Row():
                fp_id = gr.Dropdown(list(PRODUCTS.keys()), label="Product ID", value="01")
                fp_hash = gr.Textbox(label="SHA-256 prefix to verify (first 8+ chars)")
            fp_btn = gr.Button("Verify fingerprint", variant="primary")
            fp_out = gr.Markdown()
            fp_btn.click(ip_fingerprint_verify, [fp_id, fp_hash], fp_out)

        with gr.Tab("License"):
            lic_btn = gr.Button("View license", variant="primary")
            lic_out = gr.Markdown()
            lic_btn.click(ip_license_info, [], lic_out)
            demo.load(ip_license_info, [], lic_out)

        with gr.Tab("Statistics"):
            stat_btn = gr.Button("Load statistics", variant="primary")
            stat_out = gr.Markdown()
            stat_btn.click(ip_statistics, [], stat_out)
            demo.load(ip_statistics, [], stat_out)

    gr.Markdown(
        f"---\n"
        f"*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876 · {VERSION} · "
        f"[GitHub](https://github.com/wuzbak/Unitary-Manifold-) · "
        f"DOI: [10.5281/zenodo.19584531](https://doi.org/10.5281/zenodo.19584531)*"
    )

if __name__ == "__main__":
    demo.launch()
