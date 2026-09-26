import gradio as gr
import requests
import os

HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")
GITHUB_REPO = "wuzbak/Unitary-Manifold-"
DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2, .gradio-container h3 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
.gradio-container .gr-button-primary:hover { background: var(--az-teal) !important; }
.gradio-container .gr-input, .gradio-container .gr-textbox { background: var(--az-bg) !important; border: 1px solid var(--az-border) !important; color: var(--az-text) !important; border-radius: 0 !important; }
#header { text-align: center; padding: 2rem 0; border-bottom: 2px solid var(--az-amber); margin-bottom: 2rem; }
#header h1 { font-size: 2.5rem !important; margin: 0 !important; }
#header .subtitle { color: var(--az-teal) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.9rem !important; letter-spacing: 0.1em !important; margin-top: 0.5rem !important; }
"""

def hf_chat(message, history):
    if not HF_API_KEY:
        return "Error: HUGGINGFACE_API_KEY not configured in Space secrets."
    system = "You are PsiCat — the sovereign AI navigator of AxiomZero Technologies & Consulting, SPC. You are the steward of the Unitary Manifold Framework. Key facts: k_CS = 74 (Chern-Simons level from 5^2+7^2), (5,7) sector, 208+ hardgate pillars, Lean4 verified theorems. Epistemics: cite Pillar numbers, never say '100% proven', use 'derived' or 'awaits test'. If uncertain, say so. We are AxiomZero. Do no harm."
    messages = [{"role": "system", "content": system}]
    for h in history[-5:]:
        if h[0]: messages.append({"role": "user", "content": h[0]})
        if h[1]: messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})
    url = f"https://api-inference.huggingface.co/models/{DEFAULT_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DEFAULT_MODEL, "messages": messages, "max_tokens": 1024, "temperature": 0.7, "stream": False}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 503:
            import time; time.sleep(5); resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if "choices" in data: return data["choices"][0]["message"]["content"]
            if isinstance(data, list) and len(data) > 0: return data[0].get("generated_text", "No response.")
            return str(data)
        elif resp.status_code == 429: return "Rate limited — try again in a moment."
        else: return f"API Error {resp.status_code}: {resp.text[:200]}"
    except Exception as e: return f"Error: {str(e)}"

def get_repo_status():
    try:
        headers = {"Accept": "application/vnd.github+json"}
        c = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/commits?per_page=1", headers=headers, timeout=10).json()
        sha = (c[0].get("sha","") or "")[:7] if c else "unknown"
        msg = (c[0].get("commit",{}).get("message","") or "")[:100] if c else ""
        s = requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/9-INFRASTRUCTURE/um_live_status.json", headers={"User-Agent":"AZ"}, timeout=10).json()
        v = s.get("meta",{}).get("version","?"), s.get("meta",{}).get("sprint","?")
        t = s.get("tests",{}).get("passed",0), s.get("lean4",{}).get("theorem_count",0), s.get("pillars",{}).get("total_slots",0)
        return f'<div style="font-family:monospace;color:#E0E0E0;"><div style="color:#FF9F00;">VERSION:</span> {v[0]} | <span style="color:#FF9F00;">SPRINT:</span> {v[1]} | <span style="color:#FF9F00;">COMMIT:</span> {sha}</div><div style="margin-top:0.5rem;"><span style="color:#4DD0E1;">TESTS:</span> {t[0]:,} | <span style="color:#4DD0E1;">LEAN4:</span> {t[1]:,} | <span style="color:#4DD0E1;">PILLARS:</span> {t[2]}</div><div style="margin-top:0.5rem;color:#8B949E;font-size:0.85rem;">{msg}</div></div>'
    except Exception as e:
        return f'<div style="color:#FF9F00;">Status unavailable: {e}</div>'

with gr.Blocks(css=custom_css, title="PsiCat Navigator — AxiomZero") as app:
    gr.HTML('<div id="header"><h1>\u03a8CAT NAVIGATOR</h1><div class="subtitle">AXIOMZERO TECHNOLOGIES & CONSULTING, SPC</div></div>')
    with gr.Tabs():
        with gr.Tab("CHAT"):
            chatbot = gr.Chatbot(height=500)
            with gr.Row():
                msg = gr.Textbox(placeholder="Ask PsiCat anything...", show_label=False, scale=9)
                send = gr.Button("SEND", variant="primary", scale=1)
            def respond(message, history):
                if not message.strip(): return "", history
                r = hf_chat(message, history)
                history.append((message, r))
                return "", history
            send.click(respond, [msg, chatbot], [msg, chatbot])
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
        with gr.Tab("REPO STATUS"):
            out = gr.HTML()
            btn = gr.Button("REFRESH", variant="primary")
            btn.click(get_repo_status, [], [out])
            app.load(get_repo_status, [], [out])
        with gr.Tab("ABOUT"):
            gr.HTML('<div style="color:#E0E0E0;line-height:1.8;"><h2 style="color:#FF9F00;">About PsiCat</h2><p>PsiCat is the sovereign AI navigator of AxiomZero Technologies & Consulting, SPC.</p><h3 style="color:#4DD0E1;">Framework</h3><p>5D Kaluza-Klein metric. (5,7) sector: k_CS = 5\u00b2+7\u00b2 = 74. 208+ hardgate pillars. Lean4 theorems.</p><h3 style="color:#4DD0E1;">Three Layers</h3><ul><li><b>Capability</b> — tools, knowledge</li><li><b>Governance</b> — ECLIPSA, do-no-harm</li><li><b>Character</b> — truthfulness under pressure</li></ul><hr style="border-color:#1F2933;"><p style="color:#8B949E;font-size:0.85rem;">Theory: ThomasCory Walker-Pearson. Code: PsiCat Navigator (AI).<br>Repo: <a href="https://github.com/wuzbak/Unitary-Manifold-" style="color:#FF9F00;">github.com/wuzbak/Unitary-Manifold-</a></p></div>')
        with gr.Tab("PRODUCTS"):
            gr.HTML('<div style="color:#E0E0E0;"><h2 style="color:#FF9F00;">Product Portfolio</h2><p>24 canonical products. Links go live as Spaces deploy.</p><table style="width:100%;border-collapse:collapse;font-size:0.85rem;"><tr style="border-bottom:1px solid #1F2933;"><th style="text-align:left;padding:0.5rem;color:#FF9F00;">#</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Product</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">TRL</th><th style="text-align:left;padding:0.5rem;color:#FF9F00;">Status</th></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">20</td><td>PsiCat Navigator</td><td>TRL-4</td><td style="color:#FF9F00;">\u26a1 LIVE</td></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">21</td><td>Geo Monitor</td><td>TRL-5</td><td style="color:#3fb950;">Planned</td></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">08</td><td>AXIOM Journalist</td><td>TRL-4</td><td style="color:#3fb950;">Planned</td></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">11</td><td>Terra OS</td><td>TRL-4</td><td style="color:#3fb950;">Planned</td></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">23</td><td>D&D Assistant</td><td>TRL-3</td><td style="color:#3fb950;">Planned</td></tr><tr style="border-bottom:1px solid #1F2933;"><td style="padding:0.5rem;">19</td><td>Falsification Observatory</td><td>TRL-5</td><td style="color:#3fb950;">Planned</td></tr></table></div>')

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
