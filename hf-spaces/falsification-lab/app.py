import gradio as gr
import requests
import os

GITHUB_REPO = "wuzbak/Unitary-Manifold-"

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
"""

EXPERIMENTS = [
    {"id":"LiteBIRD","name":"LiteBIRD CMB","prediction":"r = 0.0315","kill":"r < 0.016 confirmed","status":"PENDING","detail":"~2032 launch. Tests tensor-to-scalar ratio. Pillar 396. ARCHITECTURE_LIMIT_CERTIFIED."},
    {"id":"DESI","name":"DESI DR3 Dark Energy","prediction":"w_a = 0","kill":"w_a != 0 at >3 sigma","status":"TENSION","detail":"2.30 sigma tension with DESI DR2. Pillar 301, 486. DR3 decision late-2026."},
    {"id":"JUNO","name":"JUNO Neutrino Mass","prediction":"dm2_21 in UM window","kill":"IH confirmed >3 sigma","status":"TENSION","detail":"1.71 sigma tension. Pillar 774/796. 2026 data will resolve."},
    {"id":"CMBS4","name":"CMB-S4 Spectral","prediction":"n_s = 0.9635","kill":"spectral features excluded","status":"PENDING","detail":"Tests scalar spectral index and spectral features."},
    {"id":"HLLHC","name":"HL-LHC KK Graviton","prediction":"M_KK ~ 1.0 TeV","kill":"No KK graviton at TeV scale","status":"PASS","detail":"HL-LHC PASS so far. Pillar 793. M_G*(n=1) ~ 1.0 TeV within reach."},
    {"id":"NEDM","name":"nEDM CP Violation","prediction":"CP from geometry","kill":"CP violation excluded by geometry","status":"PENDING","detail":"Tests CP violation geometry prediction."},
    {"id":"XENON","name":"XENON-nT Dark Matter","prediction":"M_KK ~ 1.0 TeV DM","kill":"DM mass excludes KK tower","status":"PENDING","detail":"Tests dark matter KK tower candidate. Pillar 790."},
]

def render_experiments():
    status_colors = {"PASS":"#3fb950","TENSION":"#FF9F00","FALSIFIED":"#ff6b6b","PENDING":"#8B949E"}
    html = '<div style="font-family:Inter,sans-serif;color:#E0E0E0;">'
    for e in EXPERIMENTS:
        color = status_colors.get(e["status"],"#8B949E")
        html += f'<div style="background:#111820;border:1px solid #1F2933;padding:1rem;margin:0.5rem 0;">'
        html += f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        html += f'<span style="color:#FF9F00;font-family:JetBrains Mono,monospace;font-weight:bold;">{e["name"]}</span>'
        html += f'<span style="color:{color};font-family:JetBrains Mono,monospace;padding:0.25rem 0.75rem;border:1px solid {color};font-size:0.75rem;">{e["status"]}</span>'
        html += f'</div><div style="color:#4DD0E1;margin-top:0.5rem;font-family:monospace;font-size:0.85rem;">Prediction: {e["prediction"]}</div>'
        html += f'<div style="color:#8B949E;font-size:0.85rem;margin-top:0.25rem;">Kill condition: {e["kill"]}</div>'
        html += f'<div style="color:#8B949E;font-size:0.85rem;margin-top:0.25rem;">{e["detail"]}</div>'
        html += '</div>'
    html += '</div>'
    return html

def get_repo_status():
    try:
        s = requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/9-INFRASTRUCTURE/um_live_status.json", headers={"User-Agent":"AZ"}, timeout=10).json()
        v = s.get("meta",{}).get("version","?")
        t = s.get("tests",{}).get("passed",0)
        l = s.get("lean4",{}).get("theorem_count",0)
        p = s.get("pillars",{}).get("total_slots",0)
        return f'<div style="font-family:monospace;color:#4DD0E1;"><span style="color:#FF9F00;">{v}</span> | TESTS: {t:,} | LEAN4: {l:,} | PILLARS: {p}</div>'
    except: return '<div style="color:#8B949E;">Status unavailable</div>'

with gr.Blocks(css=custom_css, title="Falsification Observatory — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">FALSIFICATION OBSERVATORY</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">LIVE EXPERIMENT TRACKER · AXIOMZERO</div></div>')
    status = gr.HTML()
    app.load(get_repo_status, [], [status])
    with gr.Tab("EXPERIMENTS"):
        exp_out = gr.HTML()
        app.load(render_experiments, [], [exp_out])
        refresh = gr.Button("REFRESH", variant="primary")
        refresh.click(render_experiments, [], [exp_out])
    with gr.Tab("ABOUT"):
        gr.HTML('<div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;"><h2 style="color:#FF9F00;">Falsification Routing Oracle</h2><p>Pillar 787 established 7 live experiments with explicit kill conditions. Each experiment has PASS/TENSION/FALSIFIED verdicts with z-test statistics.</p><h3 style="color:#4DD0E1;">Current Status</h3><ul><li><strong>HL-LHC</strong> — PASS (KK graviton in reach)</li><li><strong>DESI DR3</strong> — TENSION (w_a 2.30 sigma)</li><li><strong>JUNO</strong> — TENSION (dm2_21 1.71 sigma)</li><li><strong>LiteBIRD, CMB-S4, nEDM, XENON-nT</strong> — PENDING</li></ul><p style="color:#8B949E;font-size:0.85rem;">Results are SHA-256 signed. No falsification has occurred. The framework stands.</p></div>')

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
