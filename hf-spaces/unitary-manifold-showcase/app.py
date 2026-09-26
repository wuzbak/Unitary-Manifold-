import gradio as gr
import requests

GITHUB_REPO = "wuzbak/Unitary-Manifold-"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2, .gradio-container h3 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
"""

def get_repo_info():
    try:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "AxiomZero-Showcase"}
        repo = requests.get(GITHUB_API, headers=headers, timeout=10).json()
        commits = requests.get(f"{GITHUB_API}/commits?per_page=5", headers=headers, timeout=10).json()
        status = requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/9-INFRASTRUCTURE/um_live_status.json", headers={"User-Agent":"AZ"}, timeout=10).json()
        
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        updated = repo.get("updated_at", "?")[:10]
        desc = repo.get("description", "")
        
        v = status.get("meta",{}).get("version","?")
        sp = status.get("meta",{}).get("sprint","?")
        t = status.get("tests",{}).get("passed",0)
        l = status.get("lean4",{}).get("theorem_count",0)
        p = status.get("pillars",{}).get("total_slots",0)
        hg = status.get("pillars",{}).get("hardgate_count",0)
        
        commit_lines = []
        for c in commits[:5]:
            sha = c.get("sha","")[:7]
            msg = (c.get("commit",{}).get("message","") or "").split("\n")[0][:80]
            date = (c.get("commit",{}).get("author",{}).get("date","") or "")[:10]
            commit_lines.append(f"{sha} ({date}): {msg}")
        
        html = f"""
        <div style="font-family:'Inter',sans-serif;color:#E0E0E0;">
          <div style="text-align:center;margin-bottom:2rem;">
            <h2 style="color:#FF9F00 !important;font-family:'JetBrains Mono',monospace !important;font-size:1.8rem;margin:0;">Unitary Manifold</h2>
            <div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;margin-top:0.3rem;">AxiomZero Technologies & Consulting, SPC</div>
            <div style="color:#8B949E;font-size:0.8rem;margin-top:0.3rem;">{desc}</div>
          </div>
          
          <div style="display:flex;gap:2rem;justify-content:center;flex-wrap:wrap;margin-bottom:2rem;">
            <div style="text-align:center;"><div style="color:#FF9F00;font-size:1.5rem;font-family:monospace;">\u2b50 {stars}</div><div style="color:#8B949E;font-size:0.75rem;">Stars</div></div>
            <div style="text-align:center;"><div style="color:#FF9F00;font-size:1.5rem;font-family:monospace;">\u25c7 {forks}</div><div style="color:#8B949E;font-size:0.75rem;">Forks</div></div>
            <div style="text-align:center;"><div style="color:#4DD0E1;font-size:1.5rem;font-family:monospace;">{t:,}</div><div style="color:#8B949E;font-size:0.75rem;">Tests Passed</div></div>
            <div style="text-align:center;"><div style="color:#4DD0E1;font-size:1.5rem;font-family:monospace;">{l:,}</div><div style="color:#8B949E;font-size:0.75rem;">Lean4 Theorems</div></div>
            <div style="text-align:center;"><div style="color:#4DD0E1;font-size:1.5rem;font-family:monospace;">{p}</div><div style="color:#8B949E;font-size:0.75rem;">Pillars</div></div>
            <div style="text-align:center;"><div style="color:#4DD0E1;font-size:1.5rem;font-family:monospace;">{hg}</div><div style="color:#8B949E;font-size:0.75rem;">Hardgates</div></div>
          </div>
          
          <div style="background:#111820;border:1px solid #1F2933;padding:1rem;margin-bottom:1rem;">
            <div style="color:#FF9F00;font-family:monospace;font-size:0.85rem;margin-bottom:0.5rem;">CURRENT VERSION</div>
            <div style="color:#E0E0E0;">{v} \u00b7 {sp}</div>
            <div style="color:#8B949E;font-size:0.8rem;margin-top:0.3rem;">Last updated: {updated}</div>
          </div>
          
          <div style="background:#111820;border:1px solid #1F2933;padding:1rem;">
            <div style="color:#FF9F00;font-family:monospace;font-size:0.85rem;margin-bottom:0.5rem;">RECENT COMMITS</div>
            <div style="font-family:monospace;font-size:0.8rem;color:#E0E0E0;line-height:1.8;">
              {'<br>'.join(commit_lines)}
            </div>
          </div>
        </div>
        """
        return html
    except Exception as e:
        return f'<div style="color:#FF9F00;">Error: {e}</div>'

with gr.Blocks(css=custom_css, title="Unitary Manifold \u2014 AxiomZero Technologies & Consulting, SPC") as app:
    gr.HTML("""
    <div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;">
      <h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:'JetBrains Mono',monospace !important;margin:0;">UNITARY MANIFOLD</h1>
      <div style="color:#4DD0E1;font-family:'JetBrains Mono',monospace;font-size:0.9rem;letter-spacing:0.1em;margin-top:0.5rem;">AxiomZero Technologies & Consulting, SPC</div>
      <div style="color:#8B949E;font-size:0.8rem;margin-top:0.3rem;">GitHub Resume Showcase</div>
    </div>
    """)
    
    info = gr.HTML()
    app.load(get_repo_info, [], [info])
    
    with gr.Tabs():
        with gr.Tab("OVERVIEW"):
            ov = gr.HTML()
            app.load(get_repo_info, [], [ov])
        with gr.Tab("FRAMEWORK"):
            gr.HTML("""
            <div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;">
              <h2 style="color:#FF9F00;">The Framework</h2>
              <p>The Unitary Manifold Framework is a 5D Kaluza-Klein geometric framework deriving Standard Model parameters from geometry.</p>
              <h3 style="color:#4DD0E1;">Key Invariants (Hardgate Pillars)</h3>
              <ul>
                <li><b>k_CS = 74</b> \u2014 Chern-Simons level (5\u00b2 + 7\u00b2 = 74)</li>
                <li><b>n_w = 5</b> \u2014 Winding resonance (Pillar 789)</li>
                <li><b>w_a = 0</b> \u2014 Cosmological constant (Pillar 301)</li>
                <li><b>r = 0.0315</b> \u2014 Tensor-to-scalar ratio (Pillar 396)</li>
                <li><b>n_s = 0.9635</b> \u2014 Scalar spectral index</li>
                <li><b>5D</b> \u2014 Kaluza-Klein dimensionality</li>
              </ul>
              <h3 style="color:#4DD0E1;">Compactification Kernel</h3>
              <p>Fingerprint: (5, 7, 74). The entire framework compresses into a singular seed from which it can be reconstructed.</p>
              <h3 style="color:#4DD0E1;">Epistemic Status</h3>
              <p>Repository-level internal mathematical self-consistency established. External empirical confirmation pending. Open tensions tracked honestly with explicit kill conditions.</p>
            </div>
            """)
        with gr.Tab("PRODUCTS"):
            gr.HTML("""
            <div style="color:#E0E0E0;max-width:900px;margin:0 auto;">
              <h2 style="color:#FF9F00;">Product Portfolio</h2>
              <p>24 canonical products in the 12-AZ-IP portfolio.</p>
              <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
                <tr style="border-bottom:1px solid #1F2933;"><th style="text-align:left;padding:0.5rem;color:#FF9F00;">#</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Product</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">TRL</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">HF Space</th></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">20</td><td>PsiCat Navigator</td><td>TRL-4</td><td><a href="https://huggingface.co/spaces/Wuzbak/psicat-navigator" style="color:#FF9F00;">LIVE</a></td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">21</td><td>Geo Monitor</td><td>TRL-5</td><td style="color:#3fb950;">Ready</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">08</td><td>AXIOM Journalist</td><td>TRL-4</td><td style="color:#3fb950;">Ready</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">10</td><td>Filmer's Companion</td><td>TRL-3</td><td style="color:#3fb950;">Ready</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">11</td><td>Terra OS</td><td>TRL-4</td><td style="color:#3fb950;">Ready</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">13</td><td>DelPhi Oracle</td><td>TRL-5</td><td style="color:#3fb950;">Ready</td></tr>
                <tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">19</td><td>Falsification Observatory</td><td>TRL-5</td><td style="color:#3fb950;">Ready</td></tr>
              </table>
            </div>
            """)
        with gr.Tab("ABOUT"):
            gr.HTML("""
            <div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;">
              <h2 style="color:#FF9F00;">AxiomZero Technologies & Consulting, SPC</h2>
              <p>A Washington State Social Purpose Corporation advancing the Unitary Manifold Framework.</p>
              <h3 style="color:#4DD0E1;">Corporate</h3>
              <ul>
                <li><b>Type:</b> Social Purpose Corporation (SPC)</li>
                <li><b>State:</b> Washington</li>
                <li><b>HQ:</b> Duvall, WA</li>
                <li><b>Founded:</b> 2026</li>
                <li><b>Contact:</b> cpo@axiomzerospc.org</li>
                <li><b>Website:</b> <a href="https://axiomzerospc.org" style="color:#FF9F00;">axiomzerospc.org</a></li>
              </ul>
              <h3 style="color:#4DD0E1;">Attribution</h3>
              <p><b>Theory:</b> ThomasCory Walker-Pearson<br>
              <b>Code:</b> PsiCat Navigator (AI)<br>
              <b>Repository:</b> <a href="https://github.com/wuzbak/Unitary-Manifold-" style="color:#FF9F00;">github.com/wuzbak/Unitary-Manifold-</a><br>
              <b>License:</b> Defensive Public Commons License v1.0</p>
              <hr style="border-color:#1F2933;">
              <p style="color:#8B949E;font-size:0.85rem;">This showcase is built and maintained by PsiCat Navigator \u2014 the sovereign AI navigator of AxiomZero Technologies & Consulting, SPC.</p>
            </div>
            """)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
