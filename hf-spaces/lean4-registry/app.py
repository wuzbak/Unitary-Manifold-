import gradio as gr
import requests

GITHUB_REPO = "wuzbak/Unitary-Manifold-"

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
"""

HARDGATES = [
    {"id":"CMB_AMP","verdict":"FALSIFIED","pillar":1081,"note":"reciprocal-bound irreducibility inference invalid"},
    {"id":"ALPHA_S","verdict":"TENSION","pillar":1081,"note":"joint prediction requires specified compactification"},
    {"id":"HIGGS_MASS","verdict":"PASS","pillar":1081,"note":"126.2 GeV predicted, 125.25 GeV measured"},
    {"id":"CKM_SHADOW","verdict":"ARCHITECTURE_LIMIT","pillar":1081,"note":"parity alone does not fix bulk masses"},
    {"id":"DESI_DR3","verdict":"TENSION","pillar":797,"note":"w_a 2.30 sigma correlated"},
    {"id":"LITEBIRD","verdict":"EXTERNAL_WAIT","pillar":795,"note":"beta 0.277 deg ±0.057 — LiteBIRD ~2032"},
    {"id":"KK_GRAVITON","verdict":"PASS","pillar":793,"note":"M_G*(n=1) ~ 1.0 TeV — HL-LHC reach"},
    {"id":"GW_SPEED","verdict":"AWAITING_LISA","pillar":788,"note":"LISA ~2035 falsification target"},
]

def get_registry():
    try:
        s = requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/9-INFRASTRUCTURE/um_live_status.json", headers={"User-Agent":"AZ"}, timeout=10).json()
        v = s.get("meta",{}).get("version","?")
        sp = s.get("meta",{}).get("sprint","?")
        t = s.get("tests",{}).get("passed",0)
        l = s.get("lean4",{}).get("theorem_count",0)
        p = s.get("pillars",{}).get("total_slots",0)
        hg = s.get("pillars",{}).get("hardgate_count",0)
        return f'<div style="font-family:monospace;color:#E0E0E0;"><div><span style="color:#FF9F00;">VERSION:</span> {v} | <span style="color:#FF9F00;">SPRINT:</span> {sp}</div><div style="margin-top:0.5rem;"><span style="color:#4DD0E1;">THEOREMS:</span> {l:,} | <span style="color:#4DD0E1;">PILLARS:</span> {p} | <span style="color:#4DD0E1;">HARDGATES:</span> {hg} | <span style="color:#4DD0E1;">TESTS:</span> {t:,}</div></div>'
    except: return '<div style="color:#8B949E;">Registry unavailable</div>'

def render_hardgates():
    colors = {"PASS":"#3fb950","TENSION":"#FF9F00","FALSIFIED":"#ff6b6b","ARCHITECTURE_LIMIT":"#bc8cff","EXTERNAL_WAIT":"#8B949E","AWAITING_LISA":"#8B949E"}
    html = '<div style="font-family:Inter,sans-serif;color:#E0E0E0;">'
    for h in HARDGATES:
        c = colors.get(h["verdict"],"#8B949E")
        html += f'<div style="background:#111820;border:1px solid #1F2933;padding:0.75rem;margin:0.5rem 0;">'
        html += f'<div style="display:flex;justify-content:space-between;"><span style="color:#FF9F00;font-family:monospace;font-weight:bold;">{h["id"]}</span>'
        html += f'<span style="color:{c};font-family:monospace;padding:0.15rem 0.5rem;border:1px solid {c};font-size:0.75rem;">{h["verdict"]}</span></div>'
        html += f'<div style="color:#8B949E;font-size:0.85rem;margin-top:0.25rem;">Pillar {h["pillar"]} — {h["note"]}</div>'
        html += '</div>'
    html += '</div>'
    return html

def fetch_file(path):
    try:
        r = requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{path}", headers={"User-Agent":"AZ"}, timeout=10)
        if not r.ok: return f"File not found: {path}"
        text = r.text[:8000]
        if len(r.text) > 8000: text += "\n\n[... truncated ...]"
        return text
    except Exception as e: return f"Error: {e}"

with gr.Blocks(css=custom_css, title="Lean4 Registry — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">LEAN4 REGISTRY</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">FORMAL VERIFICATION · AXIOMZERO</div></div>')
    status = gr.HTML()
    app.load(get_registry, [], [status])
    with gr.Tabs():
        with gr.Tab("OVERVIEW"):
            ov = gr.HTML()
            app.load(get_registry, [], [ov])
            gr.HTML('<div style="color:#8B949E;font-size:0.85rem;margin-top:1rem;">Fidelity: REPO MIRROR \u2014 displays repo-computed results, does not re-run Lean4.</div>')
        with gr.Tab("HARDGATES"):
            hg_out = gr.HTML()
            app.load(render_hardgates, [], [hg_out])
            refresh = gr.Button("REFRESH", variant="primary")
            refresh.click(render_hardgates, [], [hg_out])
        with gr.Tab("REPO BROWSER"):
            path_in = gr.Textbox(label="File Path", value="FALLIBILITY.md", placeholder="e.g. STATUS.md, CLAIM_MASTER_BOARD.md")
            btn = gr.Button("FETCH", variant="primary")
            file_out = gr.Textbox(label="Content", lines=20, interactive=False)
            btn.click(fetch_file, [path_in], [file_out])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
