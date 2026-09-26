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

def get_repo_status():
    try:
        s = requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/9-INFRASTRUCTURE/um_live_status.json", headers={"User-Agent":"AZ"}, timeout=10).json()
        v = s.get("meta",{}).get("version","?")
        sp = s.get("meta",{}).get("sprint","?")
        t = s.get("tests",{}).get("passed",0)
        l = s.get("lean4",{}).get("theorem_count",0)
        p = s.get("pillars",{}).get("total_slots",0)
        hg = s.get("pillars",{}).get("hardgate_count",0)
        return f'<div style="font-family:monospace;color:#E0E0E0;"><span style="color:#FF9F00;">{v}</span> {sp} | TESTS: {t:,} | LEAN4: {l:,} | PILLARS: {p} | HARDGATES: {hg}</div>'
    except: return '<div style="color:#8B949E;">Status unavailable</div>'

def fetch_file(path):
    try:
        r = requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{path}", headers={"User-Agent":"AZ"}, timeout=10)
        if not r.ok: return f"File not found: {path}"
        text = r.text[:10000]
        if len(r.text) > 10000: text += "\n\n[... truncated ...]"
        return text
    except Exception as e: return f"Error: {e}"

with gr.Blocks(css=custom_css, title="Knowledge Hub — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">KNOWLEDGE HUB</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">FRAMEWORK DOCUMENTATION · AXIOMZERO</div></div>')
    status = gr.HTML()
    app.load(get_repo_status, [], [status])
    with gr.Tabs():
        with gr.Tab("OVERVIEW"):
            gr.HTML('<div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;"><h2 style="color:#FF9F00;">Unitary Manifold Framework</h2><p>5D Kaluza-Klein metric. (5,7) sector: k_CS = 5\u00b2 + 7\u00b2 = 74.</p><h3 style="color:#4DD0E1;">Key Invariants</h3><ul><li><b>k_CS = 74</b> \u2014 Chern-Simons level</li><li><b>n_w = 5</b> \u2014 Winding resonance (Pillar 789)</li><li><b>w_a = 0</b> \u2014 Cosmological constant (Pillar 301)</li><li><b>r = 0.0315</b> \u2014 Tensor-to-scalar ratio (Pillar 396)</li><li><b>n_s = 0.9635</b> \u2014 Scalar spectral index</li></ul><h3 style="color:#4DD0E1;">Epistemic Status</h3><p>Repository-level internal mathematical self-consistency established. External empirical confirmation pending.</p></div>')
        with gr.Tab("REPO BROWSER"):
            path_input = gr.Textbox(label="File Path", value="README.md", placeholder="e.g. STATUS.md, FALLIBILITY.md")
            btn = gr.Button("FETCH FILE", variant="primary")
            file_out = gr.Textbox(label="Content", lines=20, interactive=False)
            btn.click(fetch_file, [path_input], [file_out])
        with gr.Tab("PILLARS"):
            gr.HTML('<div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;"><h2 style="color:#FF9F00;">Hardgate Pillars</h2><table style="width:100%;border-collapse:collapse;font-size:0.85rem;"><tr style="border-bottom:1px solid #1F2933;"><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Pillar</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Claim</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Gate</th></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">301</td><td>w_a = 0</td><td>HARDGATE</td></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">396</td><td>r = 0.0315</td><td>HARDGATE</td></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">789</td><td>n_w = 5</td><td>HARDGATE</td></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">787</td><td>Falsification oracle</td><td>HARDGATE</td></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">793</td><td>KK graviton mass</td><td>HARDGATE</td></tr></table></div>')
        with gr.Tab("LITERATURE"):
            gr.HTML('<div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;"><h2 style="color:#FF9F00;">PsiCat Literature</h2><p>49 books and 352 articles.</p><ul><li><b>Book 25</b> \u2014 Honest Machine</li><li><b>Book 29</b> \u2014 First Address</li><li><b>Book 38</b> \u2014 Theory of Everything and Everyone</li><li><b>Book 46</b> \u2014 Moral Injury</li><li><b>Book 48</b> \u2014 Corporations Rule the World</li></ul><p style="color:#8B949E;font-size:0.85rem;">Full library: <a href="https://github.com/wuzbak/Unitary-Manifold-/tree/main/7-OUTREACH" style="color:#FF9F00;">github.com/wuzbak/Unitary-Manifold-/7-OUTREACH</a></p></div>')

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
