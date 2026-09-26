import gradio as gr
import requests
import os

HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
"""

ORACLES = {
    "physics": {"name": "Physics Oracle", "system": "You are the Physics Oracle of the Unitary Manifold Framework. Answer physics questions citing Pillar numbers. Key facts: k_CS=74, n_w=5, w_a=0, r=0.0315, n_s=0.9635, 5D Kaluza-Klein. Never say 'proven' — use 'derived', 'predicted', 'awaits test'. If uncertain, say so."},
    "ethics": {"name": "Ethics Oracle", "system": "You are the Ethics Oracle of AxiomZero. Based on the PsiCat Literature: claims are obligations, uncertainty is data, do no harm. Three layers: capability, governance, character. Pro-humanity, pro-individual. Anti-domination is pro-democracy."},
    "governance": {"name": "Governance Oracle", "system": "You are the Governance Oracle of AxiomZero. The Pentad: 5 sectors (Computational, Relational, Intentional, Physical, Biological). ECLIPSA sentinel. Admin retains canonical veto. Do-no-harm constraint. Co-emergence: human retains judgment, AI supplies scale."},
    "prediction": {"name": "Prediction Oracle", "system": "You are the Prediction Oracle. Express predictions with uncertainty ranges and test status. Track tensions: dm2_21 at 1.71 sigma (JUNO 2026), w_a at 2.30 sigma (DESI), r=0.0315 vs ACT DR6. Never state certainty without test status."},
    "manifold": {"name": "Manifold Read", "system": "You are the Manifold Read Oracle. You read the Unitary Manifold's geometric state. The 5D Kaluza-Klein metric packages gravity, gauge fields, and radion. The (5,7) sector gives k_CS=74. Irreversibility is geometrised into the 5th dimension. The compactification kernel fingerprint is (5, 7, 74)."},
}

def ask_oracle(oracle_type, question):
    if not HF_API_KEY:
        return "AI requires HUGGINGFACE_API_KEY. Set it in Space secrets."
    if not question.strip():
        return "Ask a question."
    oracle = ORACLES.get(oracle_type, ORACLES["physics"])
    messages = [{"role":"system","content":oracle["system"]},{"role":"user","content":question}]
    try:
        r = requests.post("https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct",
            headers={"Authorization":f"Bearer {HF_API_KEY}","Content-Type":"application/json"},
            json={"model":"meta-llama/Meta-Llama-3.1-8B-Instruct","messages":messages,"max_tokens":1024,"temperature":0.5,"stream":False}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "choices" in data: return data["choices"][0]["message"]["content"]
        elif r.status_code == 429: return "Rate limited — try again in a moment."
        return f"Oracle unavailable (HTTP {r.status_code})"
    except Exception as e: return f"Error: {e}"

with gr.Blocks(css=custom_css, title="DelPhi Oracle — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">DELPHI ORACLE</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">5-ORACLE CONSULTATION SYSTEM · AXIOMZERO</div></div>')
    with gr.Tabs():
        with gr.Tab("PHYSICS"):
            q1 = gr.Textbox(label="Question", placeholder="e.g. What does k_CS = 74 mean for the framework?", lines=2)
            b1 = gr.Button("ASK PHYSICS ORACLE", variant="primary")
            o1 = gr.Textbox(label="Response", lines=10, interactive=False)
            b1.click(lambda q: ask_oracle("physics", q), [q1], [o1])
        with gr.Tab("ETHICS"):
            q2 = gr.Textbox(label="Question", placeholder="e.g. What does 'claims as obligations' mean?", lines=2)
            b2 = gr.Button("ASK ETHICS ORACLE", variant="primary")
            o2 = gr.Textbox(label="Response", lines=10, interactive=False)
            b2.click(lambda q: ask_oracle("ethics", q), [q2], [o2])
        with gr.Tab("GOVERNANCE"):
            q3 = gr.Textbox(label="Question", placeholder="e.g. How does the Pentad distribute authority?", lines=2)
            b3 = gr.Button("ASK GOVERNANCE ORACLE", variant="primary")
            o3 = gr.Textbox(label="Response", lines=10, interactive=False)
            b3.click(lambda q: ask_oracle("governance", q), [q3], [o3])
        with gr.Tab("PREDICTION"):
            q4 = gr.Textbox(label="Question", placeholder="e.g. What experiments could falsify the framework?", lines=2)
            b4 = gr.Button("ASK PREDICTION ORACLE", variant="primary")
            o4 = gr.Textbox(label="Response", lines=10, interactive=False)
            b4.click(lambda q: ask_oracle("prediction", q), [q4], [o4])
        with gr.Tab("MANIFOLD READ"):
            q5 = gr.Textbox(label="Question", placeholder="e.g. Describe the compactification kernel.", lines=2)
            b5 = gr.Button("ASK MANIFOLD ORACLE", variant="primary")
            o5 = gr.Textbox(label="Response", lines=10, interactive=False)
            b5.click(lambda q: ask_oracle("manifold", q), [q5], [o5])
        with gr.Tab("ABOUT"):
            gr.HTML('<div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;"><h2 style="color:#FF9F00;">DelPhi Oracle</h2><p>Product 13. Five specialized oracles provide consultation across physics, ethics, governance, prediction, and manifold reading.</p><h3 style="color:#4DD0E1;">The Five Oracles</h3><ul><li><b>Physics</b> \u2014 framework questions, pillar citations</li><li><b>Ethics</b> \u2014 PsiCat Literature, moral reasoning</li><li><b>Governance</b> \u2014 Pentad, ECLIPSA, authority</li><li><b>Prediction</b> \u2014 uncertainty ranges, test status</li><li><b>Manifold Read</b> \u2014 geometric state interpretation</li></ul><p style="color:#8B949E;font-size:0.85rem;">Powered by HuggingFace Inference API (Llama-3.1-8B-Instruct).</p></div>')

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
