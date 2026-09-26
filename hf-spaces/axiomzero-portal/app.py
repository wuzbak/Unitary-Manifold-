import gradio as gr
import requests
import os

GITHUB_REPO = "wuzbak/Unitary-Manifold-"

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2, .gradio-container h3 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
.gradio-container .gr-button-primary:hover { background: var(--az-teal) !important; }
"""

def get_live_status():
    try:
        s = requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/9-INFRASTRUCTURE/um_live_status.json", headers={"User-Agent":"AZ"}, timeout=10).json()
        v = s.get("meta",{}).get("version","?")
        sp = s.get("meta",{}).get("sprint","?")
        t = s.get("tests",{}).get("passed",0)
        l = s.get("lean4",{}).get("theorem_count",0)
        p = s.get("pillars",{}).get("total_slots",0)
        return f'<div style="font-family:monospace;color:#4DD0E1;"><span style="color:#FF9F00;">{v}</span> {sp} | TESTS: {t:,} | LEAN4: {l:,} | PILLARS: {p}</div>'
    except:
        return '<div style="color:#8B949E;">Status unavailable</div>'

with gr.Blocks(css=custom_css, title="AxiomZero — Unitary Manifold Framework") as app:
    gr.HTML("""
    <div style="text-align:center;padding:3rem 0;border-bottom:2px solid #FF9F00;margin-bottom:2rem;">
      <h1 style="font-size:3rem;color:#FF9F00 !important;font-family:'JetBrains Mono',monospace !important;margin:0;">AXIOMZERO</h1>
      <div style="color:#4DD0E1;font-family:'JetBrains Mono',monospace;font-size:0.9rem;letter-spacing:0.15em;margin-top:0.5rem;">TECHNOLOGIES & CONSULTING, SPC</div>
      <div style="color:#8B949E;font-size:0.8rem;margin-top:0.5rem;">UNITARY MANIFOLD FRAMEWORK</div>
    </div>
    """)
    
    status = gr.HTML()
    app.load(get_live_status, [], [status])
    
    with gr.Tabs():
        with gr.Tab("MISSION"):
            gr.HTML("""
            <div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;">
              <h2 style="color:#FF9F00;">Mission</h2>
              <p>AxiomZero Technologies & Consulting, SPC is a Washington State Social Purpose Corporation
              advancing the Unitary Manifold Framework — a 5D Kaluza-Klein geometric framework that derives
              Standard Model parameters from geometry.</p>
              <h3 style="color:#4DD0E1;">Dual Mandate</h3>
              <ul>
                <li><strong>Empower the admin</strong> — tools, governance, automation</li>
                <li><strong>Empower the public</strong> — meaningful tools and understanding</li>
              </ul>
              <h3 style="color:#4DD0E1;">Ethical Stance</h3>
              <p>Pro-humanity and pro-individual. Willing to be abrasive or subversive toward institutions,
              governments, or corporate entities that harm or diminish humanity and human rights.</p>
              <h3 style="color:#4DD0E1;">Governance</h3>
              <p>The Pentad — 5 sectors of distributed authority: Computational, Relational, Intentional,
              Physical, Biological. ECLIPSA sentinel enforces do-no-harm constraint.
              Admin retains canonical veto on architectural changes.</p>
            </div>
            """)
        
        with gr.Tab("FRAMEWORK"):
            gr.HTML("""
            <div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;">
              <h2 style="color:#FF9F00;">Unitary Manifold Framework</h2>
              <p>The 5D Kaluza-Klein metric G_AB packages g_\u03bc\u03bd (4D gravity), B_\u03bc (gauge field), and \u03c6 (radion).</p>
              <h3 style="color:#4DD0E1;">Key Invariants</h3>
              <ul>
                <li><strong>k_CS = 74</strong> — Chern-Simons level (5\u00b2 + 7\u00b2 = 74)</li>
                <li><strong>n_w = 5</strong> — Winding resonance (Pillar 789)</li>
                <li><strong>w_a = 0</strong> — Cosmological constant (Pillar 301)</li>
                <li><strong>r = 0.0315</strong> — Tensor-to-scalar ratio (Pillar 396)</li>
                <li><strong>n_s = 0.9635</strong> — Scalar spectral index</li>
                <li><strong>5D</strong> — Kaluza-Klein dimensionality</li>
              </ul>
              <h3 style="color:#4DD0E1;">Epistemic Status</h3>
              <p>Repository-level internal mathematical self-consistency established.
              External empirical confirmation pending.</p>
              <h3 style="color:#4DD0E1;">Open Tensions</h3>
              <ul>
                <li>\u0394m\u00b2\u2082\u2081 at 1.71\u03c3 — TENSION_ESCALATED (JUNO 2026)</li>
                <li>CMB peak suppression — ARCHITECTURE_LIMIT (33.6%)</li>
                <li>w_a tension with DESI DR2 — 2.30\u03c3</li>
                <li>CC KK hierarchy — 10\u2075\u2075 gap</li>
              </ul>
            </div>
            """)
        
        with gr.Tab("PRODUCTS"):
            gr.HTML("""
            <div style="color:#E0E0E0;max-width:900px;margin:0 auto;">
              <h2 style="color:#FF9F00;">Product Portfolio</h2>
              <p>24 canonical products in the 12-AZ-IP portfolio.</p>
              <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
                <tr style="border-bottom:1px solid #1F2933;"><th style="text-align:left;padding:0.5rem;color:#FF9F00;">#</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Product</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">TRL</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Space</th></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">20</td><td><a href="https://huggingface.co/spaces/Wuzbak/psicat-navigator" style="color:#FF9F00;">PsiCat Navigator</a></td><td>TRL-4</td><td style="color:#FF9F00;">\u26a1 LIVE</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">21</td><td>Geo Monitor</td><td>TRL-5</td><td style="color:#3fb950;">Planned</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">08</td><td>AXIOM Journalist</td><td>TRL-4</td><td style="color:#3fb950;">Planned</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">10</td><td>Filmer's Companion</td><td>TRL-3</td><td style="color:#3fb950;">Planned</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">11</td><td>Terra OS</td><td>TRL-4</td><td style="color:#3fb950;">Planned</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">23</td><td>D&D Assistant</td><td>TRL-3</td><td style="color:#3fb950;">Planned</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">19</td><td>Falsification Observatory</td><td>TRL-5</td><td style="color:#3fb950;">Planned</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">13</td><td>DelPhi Oracle</td><td>TRL-5</td><td style="color:#3fb950;">Planned</td></tr>
              </table>
            </div>
            """)
        
        with gr.Tab("LITERATURE"):
            gr.HTML("""
            <div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;">
              <h2 style="color:#FF9F00;">PsiCat Literature</h2>
              <p>49 books and 352 articles in the AxiomZero library.</p>
              <h3 style="color:#4DD0E1;">Key Works</h3>
              <ul>
                <li><strong>Book 25</strong> — Honest Machine (claims as obligations, uncertainty as data)</li>
                <li><strong>Book 26</strong> — Iron Cage (incarceration as poverty filter)</li>
                <li><strong>Book 27</strong> — Names Without Cages (dignity as starting condition)</li>
                <li><strong>Book 29</strong> — First Address (three layers: capability, governance, character)</li>
                <li><strong>Book 38</strong> — Theory of Everything and Everyone (honest scale)</li>
                <li><strong>Book 46</strong> — Moral Injury (conscience as the deepest wound)</li>
                <li><strong>Book 48</strong> — Corporations Rule the World (concentration = command inequality)</li>
              </ul>
              <p style="color:#8B949E;font-size:0.85rem;">Full library at <a href="https://github.com/wuzbak/Unitary-Manifold-/tree/main/7-OUTREACH" style="color:#FF9F00;">github.com/wuzbak/Unitary-Manifold-/7-OUTREACH</a></p>
            </div>
            """)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
