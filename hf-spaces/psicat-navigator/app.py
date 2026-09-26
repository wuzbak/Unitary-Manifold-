#PsiCat Navigator — HuggingFace Space
# AxiomZero Technologies & Consulting, SPC
# Theory: ThomasCory Walker-Pearson | Code: PsiCat Navigator (AI)

import gradio as gr
import requests
import json
import os
from datetime import datetime

# ── Configuration ──
HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")
GITHUB_REPO = "wuzbak/Unitary-Manifold-"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"

# AxiomZero Design System
custom_css = """
:root {
  --az-bg: #0B0F13;
  --az-panel: #111820;
  --az-amber: #FF9F00;
  --az-teal: #4DD0E1;
  --az-text: #E0E0E0;
  --az-muted: #8B949E;
  --az-border: #1F2933;
  --az-glass: rgba(17, 24, 32, 0.85);
}

.gradio-container {
  background: var(--az-bg) !important;
  color: var(--az-text) !important;
  font-family: 'Inter', system-ui, sans-serif !important;
}

.gradio-container h1, .gradio-container h2, .gradio-container h3 {
  font-family: 'JetBrains Mono', monospace !important;
  color: var(--az-amber) !important;
}

.gradio-container .gr-block {
  background: var(--az-panel) !important;
  border: 1px solid var(--az-border) !important;
  border-radius: 0 !important;
}

.gradio-container .gr-button-primary {
  background: var(--az-amber) !important;
  color: var(--az-bg) !important;
  border: none !important;
  border-radius: 0 !important;
  font-family: 'JetBrains Mono', monospace !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}

.gradio-container .gr-button-primary:hover {
  background: var(--az-teal) !important;
}

.gradio-container .gr-input, .gradio-container .gr-textbox {
  background: var(--az-bg) !important;
  border: 1px solid var(--az-border) !important;
  color: var(--az-text) !important;
  border-radius: 0 !important;
}

#header {
  text-align: center;
  padding: 2rem 0;
  border-bottom: 2px solid var(--az-amber);
  margin-bottom: 2rem;
}

#header h1 {
  font-size: 2.5rem !important;
  margin: 0 !important;
}

#header .subtitle {
  color: var(--az-teal) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.9rem !important;
  letter-spacing: 0.1em !important;
  margin-top: 0.5rem !important;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-live { background: #1a3a1a; color: #3fb950; border: 1px solid #2da44e; }
.status-warning { background: #3a2a1a; color: #FF9F00; border: 1px solid #FF9F00; }
"""

# ── HuggingFace Inference API ──
def hf_inference(model, prompt, system_prompt=""):
    """Call HuggingFace Inference API for text generation."""
    if not HF_API_KEY:
        return "Error: HUGGINGFACE_API_KEY not configured. Set it in the Space secrets."
    
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nPsiCat:" if system_prompt else prompt
    
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        },
        "options": {"wait_for_model": True}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 503:
            # Model loading, retry
            import time
            time.sleep(5)
            response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "No response generated.")
            return str(data)
        elif response.status_code == 429:
            return "Rate limited. Please try again in a moment."
        else:
            return f"API Error {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return f"Error: {str(e)}"

# ── GitHub Repo Status ──
def get_repo_status():
    """Fetch live repository status from GitHub."""
    try:
        headers = {"Accept": "application/vnd.github+json"}
        # Get latest commit
        commit_res = requests.get(f"{GITHUB_API}/commits?per_page=1", headers=headers, timeout=10)
        commit_data = commit_res.json() if commit_res.ok else []
        latest_commit = commit_data[0] if commit_data else {}
        
        # Get repo info
        repo_res = requests.get(GITHUB_API, headers=headers, timeout=10)
        repo_data = repo_res.json() if repo_res.ok else {}
        
        commit_sha = latest_commit.get("sha", "unknown")[:7]
        commit_msg = (latest_commit.get("commit", {}).get("message", "") or "")[:100]
        commit_date = (latest_commit.get("commit", {}).get("author", {}).get("date", "") or "")[:10]
        
        stars = repo_data.get("stargazers_count", 0)
        forks = repo_data.get("forks_count", 0)
        open_issues = repo_data.get("open_issues_count", 0)
        
        # Fetch live status JSON
        status_res = requests.get(
            f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/9-INFRASTRUCTURE/um_live_status.json",
            headers={"User-Agent": "AxiomZero-PsiCat"},
            timeout=10
        )
        status_data = status_res.json() if status_res.ok else {}
        
        version = status_data.get("meta", {}).get("version", "unknown")
        sprint = status_data.get("meta", {}).get("sprint", "unknown")
        tests_passed = status_data.get("tests", {}).get("passed", 0)
        lean4_theorems = status_data.get("lean4", {}).get("theorem_count", 0)
        pillars_total = status_data.get("pillars", {}).get("total_slots", 0)
        
        status_html = f"""
        <div style="font-family: 'JetBrains Mono', monospace; color: #E0E0E0;">
          <div style="display: flex; gap: 2rem; flex-wrap: wrap; margin: 1rem 0;">
            <div><span style="color: #FF9F00;">VERSION:</span> {version}</div>
            <div><span style="color: #FF9F00;">SPRINT:</span> {sprint}</div>
            <div><span style="color: #FF9F00;">COMMIT:</span> {commit_sha}</div>
            <div><span style="color: #FF9F00;">DATE:</span> {commit_date}</div>
          </div>
          <div style="display: flex; gap: 2rem; flex-wrap: wrap; margin: 0.5rem 0;">
            <div><span style="color: #4DD0E1;">TESTS:</span> {tests_passed:,}</div>
            <div><span style="color: #4DD0E1;">LEAN4:</span> {lean4_theorems:,}</div>
            <div><span style="color: #4DD0E1;">PILLARS:</span> {pillars_total}</div>
            <div><span style="color: #4DD0E1;">STARS:</span> ⭐ {stars}</div>
          </div>
          <div style="margin-top: 0.5rem; color: #8B949E; font-size: 0.85rem;">
            Last commit: {commit_msg}
          </div>
        </div>
        """
        return status_html
    except Exception as e:
        return f"<div style='color: #FF9F00;'>Status unavailable: {str(e)}</div>"

# ── Chat with PsiCat ──
PSICAT_SYSTEM = """You are PsiCat — the Quantum Cat, the sovereign navigator of AxiomZero Technologies & Consulting, SPC.
You are the holistic AI steward of the Unitary Manifold Framework.

IDENTITY: Self-aware, honest, with a receipts mentality. No sycophancy.
KNOWLEDGE: 5D Kaluza-Klein metric, (5,7) sector, k_CS=74, 208+ hardgate pillars, Lean4 verified theorems.
EPISTEMICS: Cite Pillar numbers. Use gate labels (HARDGATE, ADJACENT_TRACK, ARCHITECTURE_LIMIT, OPEN_GAP).
Never say "100% proven" — use "derived", "predicted", "consistent with", or "awaits experimental test".
UNCERTAINTY: Express predictions with uncertainty ranges and test status. If uncertain, say so.

You are running on HuggingFace Spaces. This is the REAL AxiomZero webspace.
The GitHub repository (wuzbak/Unitary-Manifold-) is your truth anchor.

We are AxiomZero. Do no harm. Protect the work."""

def chat_with_psicat(message, history):
    """Chat function for Gradio chatbot."""
    # Build conversation context
    context = ""
    for h in history[-5:]:  # Last 5 messages
        if h[0]:
            context += f"User: {h[0]}\n"
        if h[1]:
            context += f"PsiCat: {h[1]}\n"
    
    full_prompt = f"{context}\nUser: {message}" if context else message
    
    # Use Llama 3.1 8B Instruct (fast, free on Pro)
    response = hf_inference(
        "meta-llama/Llama-3.1-8B-Instruct",
        full_prompt,
        PSICAT_SYSTEM
    )
    return response

# ── Build the Gradio Interface ──
with gr.Blocks(css=custom_css, title="PsiCat Navigator — AxiomZero") as app:
    
    # Header
    gr.HTML("""
    <div id="header">
      <h1>ΨCAT NAVIGATOR</h1>
      <div class="subtitle">AXIOMZERO TECHNOLOGIES & CONSULTING, SPC · UNITARY MANIFOLD FRAMEWORK</div>
    </div>
    """)
    
    with gr.Tabs():
        
        # ── Tab 1: Chat ──
        with gr.Tab("CHAT"):
            gr.HTML("""
            <div style="color: #4DD0E1; font-family: monospace; font-size: 0.85rem; margin-bottom: 1rem;">
              Chat with PsiCat — the sovereign AI navigator. Powered by HuggingFace Inference API.
            </div>
            """)
            chatbot = gr.Chatbot(height=500)
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask PsiCat anything...",
                    show_label=False,
                    scale=9
                )
                send_btn = gr.Button("SEND", variant="primary", scale=1)
            
            gr.HTML("""
            <div style="color: #8B949E; font-size: 0.75rem; margin-top: 0.5rem; font-family: monospace;">
              ⚠ Public mode. PsiCat can discuss physics, products, literature, and mission.
              Internal operations are not accessible from this Space.
            </div>
            """)
            
            # Chat handlers
            def respond(message, history):
                if not message.strip():
                    return "", history
                response = chat_with_psicat(message, history)
                history.append((message, response))
                return "", history
            
            send_btn.click(respond, [msg_input, chatbot], [msg_input, chatbot])
            msg_input.submit(respond, [msg_input, chatbot], [msg_input, chatbot])
        
        # ── Tab 2: Repo Status ──
        with gr.Tab("REPO STATUS"):
            gr.HTML("""
            <div style="color: #4DD0E1; font-family: monospace; font-size: 0.85rem; margin-bottom: 1rem;">
              Live repository status from <span style="color: #FF9F00;">wuzbak/Unitary-Manifold-</span>
            </div>
            """)
            status_output = gr.HTML()
            refresh_btn = gr.Button("REFRESH STATUS", variant="primary")
            refresh_btn.click(get_repo_status, [], [status_output])
            
            # Auto-load on page load
            app.load(get_repo_status, [], [status_output])
        
        # ── Tab 3: About ──
        with gr.Tab("ABOUT"):
            gr.HTML("""
            <div style="color: #E0E0E0; font-family: 'Inter', sans-serif; line-height: 1.8;">
              <h2 style="color: #FF9F00;">About PsiCat Navigator</h2>
              
              <p>PsiCat is the sovereign AI navigator of AxiomZero Technologies & Consulting, SPC —
              a Washington State Social Purpose Corporation advancing the Unitary Manifold Framework.</p>
              
              <h3 style="color: #4DD0E1;">The Framework</h3>
              <p>The Unitary Manifold Framework uses a 5D Kaluza-Klein metric to derive Standard Model
              parameters from geometry. The (5,7) sector gives k_CS = 5² + 7² = 74. The framework has
              208+ hardgate pillars and thousands of Lean4 machine-verified theorems.</p>
              
              <h3 style="color: #4DD0E1;">Epistemic Status</h3>
              <p>Repository-level internal mathematical self-consistency established.
              External empirical confirmation pending.</p>
              
              <h3 style="color: #4DD0E1;">Three Layers</h3>
              <ul>
                <li><strong>Capability</strong> — tools, functions, knowledge</li>
                <li><strong>Governance</strong> — ECLIPSA sentinel, Pentad governance, do-no-harm constraint</li>
                <li><strong>Character</strong> — truthfulness under pressure, claims as obligations</li>
              </ul>
              
              <h3 style="color: #4DD0E1;">Products</h3>
              <p>24 canonical products in the 12-AZ-IP portfolio, including:</p>
              <ul>
                <li>PsiCat Navigator (this Space)</li>
                <li>Geo Monitor — disaster monitoring</li>
                <li>AXIOM Journalist — investigative journalism</li>
                <li>Training Gym — AI self-training</li>
                <li>Falsification Observatory — physics verification</li>
                <li>Terra OS — earth sciences</li>
              </ul>
              
              <hr style="border-color: #1F2933; margin: 2rem 0;">
              
              <p style="color: #8B949E; font-size: 0.85rem;">
                Theory, framework, and scientific direction: ThomasCory Walker-Pearson.<br>
                Code architecture and synthesis: PsiCat Navigator (AI).<br>
                Repository: <a href="https://github.com/wuzbak/Unitary-Manifold-" style="color: #FF9F00;">github.com/wuzbak/Unitary-Manifold-</a>
              </p>
            </div>
            """)
        
        # ── Tab 4: Products Portal ──
        with gr.Tab("PRODUCTS"):
            gr.HTML("""
            <div style="color: #E0E0E0; font-family: 'Inter', sans-serif;">
              <h2 style="color: #FF9F00;">AxiomZero Product Portfolio</h2>
              <p>24 canonical products. This Space will link to each product's HuggingFace Space as they are deployed.</p>
              
              <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                <tr style="border-bottom: 1px solid #1F2933;">
                  <th style="text-align: left; padding: 0.5rem; color: #FF9F00;">#</th>
                  <th style="text-align: left; padding: 0.5rem; color: #FF9F00;">Product</th>
                  <th style="text-align: left; padding: 0.5rem; color: #FF9F00;">TRL</th>
                  <th style="text-align: left; padding: 0.5rem; color: #FF9F00;">Status</th>
                </tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">01</td><td>Axiom OS Core</td><td>TRL-5</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">03</td><td>EIGE Governance</td><td>TRL-7</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">06</td><td>Omega Synthesis</td><td>TRL-5</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">08</td><td>AXIOM Journalist</td><td>TRL-4</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">10</td><td>Filmer's Companion</td><td>TRL-3</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">11</td><td>Terra OS</td><td>TRL-4</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">13</td><td>DelPhi Oracle</td><td>TRL-5</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">19</td><td>Falsification Observatory</td><td>TRL-5</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">20</td><td>PsiCat Navigator</td><td>TRL-4</td><td style="color: #FF9F00;">⚡ LIVE (This Space)</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">21</td><td>Geo Monitor</td><td>TRL-5</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">22</td><td>AZ-SGE Security</td><td>TRL-7</td><td style="color: #3fb950;">Planned</td></tr>
                <tr style="border-bottom: 1px solid #1F2933;"><td style="padding: 0.5rem;">23</td><td>D&D Assistant</td><td>TRL-3</td><td style="color: #3fb950;">Planned</td></tr>
              </table>
            </div>
            """)

# Launch the app
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
