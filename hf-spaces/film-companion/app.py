import gradio as gr
import os
import json
import random

HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
"""

DEPARTMENTS = ["Camera", "Lighting", "Sound", "Art", "Wardrobe", "HMU", "Props", "Set Dec", "Grip", "Stunts"]
SAG_MINIMUM = 1082.00

def gen_call_sheet(project_name, shoot_date, call_time, scenes, location):
    try:
        lines = [f"CALL SHEET", f"Production: {project_name}", f"Shoot Day: {shoot_date}", f"Call Time: {call_time}", f"Location: {location}", f"Scenes: {scenes}", "", "DEPARTMENTS:"]
        for dept in DEPARTMENTS:
            dept_call = call_time
            lines.append(f"  {dept}: {dept_call}")
        lines.append("")
        lines.append(f"SAG Day Rate: ${SAG_MINIMUM:.2f}")
        lines.append("OSHA compliance: required")
        lines.append("Turnaround: 12 hours minimum")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

def calc_budget(days, crew_size, sag_cast, equipment_daily, location_daily):
    try:
        d = int(days)
        cs = int(crew_size)
        sc = int(sag_cast)
        eq = float(equipment_daily)
        loc = float(location_daily)
        crew_daily = cs * 350  # average IATSE day player
        sag_daily = sc * SAG_MINIMUM
        equip_total = eq * d
        loc_total = loc * d
        crew_total = crew_daily * d
        sag_total = sag_daily * d
        subtotal = crew_total + sag_total + equip_total + loc_total
        contingency = subtotal * 0.10
        total = subtotal + contingency
        return f"BUDGET ESTIMATE\n\nDays: {d}\nCrew: {cs} @ $350/day = ${crew_total:,.2f}\nSAG Cast: {sc} @ ${SAG_MINIMUM:.2f}/day = ${sag_total:,.2f}\nEquipment: ${eq:,.2f}/day x {d} = ${equip_total:,.2f}\nLocation: ${loc:,.2f}/day x {d} = ${loc_total:,.2f}\n\nSubtotal: ${subtotal:,.2f}\nContingency (10%): ${contingency:,.2f}\n\nTOTAL: ${total:,.2f}"
    except Exception as e: return f"Error: {e}"

def check_turnaround(wrap_time, next_call_time):
    try:
        from datetime import datetime, timedelta
        fmt = "%H:%M"
        wrap = datetime.strptime(wrap_time, fmt)
        call = datetime.strptime(next_call_time, fmt)
        if call < wrap: call = call.replace(day=call.day + 1)
        diff = call - wrap
        hours = diff.total_seconds() / 3600
        if hours >= 12: return f"\u2705 PASS: {hours:.1f} hours turnaround (12h minimum met)"
        else: return f"\u274c FAIL: Only {hours:.1f} hours turnaround (12h minimum required). SAG violation."
    except Exception as e: return f"Error: {e}"

def ai_ad_assistant(question):
    if not HF_API_KEY: return "AI requires HUGGINGFACE_API_KEY."
    import requests
    system = "You are an Assistant Director and Unit Production Manager for a film production. You know SAG/DGA/WGA/IATSE rules, OSHA compliance, budget allocation, call sheet generation, DOOD (Day Out of Days), and turnaround requirements. Be concise and practical."
    messages = [{"role":"system","content":system},{"role":"user","content":question}]
    try:
        r = requests.post("https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct",
            headers={"Authorization":f"Bearer {HF_API_KEY}","Content-Type":"application/json"},
            json={"model":"meta-llama/Meta-Llama-3.1-8B-Instruct","messages":messages,"max_tokens":512,"temperature":0.6,"stream":False}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "choices" in data: return data["choices"][0]["message"]["content"]
        return f"AI unavailable (HTTP {r.status_code})"
    except Exception as e: return f"Error: {e}"

with gr.Blocks(css=custom_css, title="Film Companion — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">FILMER\'S COMPANION</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">FILM PRODUCTION SUITE · AXIOMZERO</div></div>')
    with gr.Tabs():
        with gr.Tab("CALL SHEET"):
            with gr.Row():
                pn = gr.Textbox(label="Project Name", value="Untitled Project")
                sd = gr.Textbox(label="Shoot Date", value="2026-01-15")
                ct = gr.Textbox(label="Call Time", value="07:00")
            with gr.Row():
                sc = gr.Textbox(label="Scenes", value="1-3")
                loc = gr.Textbox(label="Location", value="Studio A")
            btn = gr.Button("GENERATE CALL SHEET", variant="primary")
            out = gr.Textbox(label="Call Sheet", lines=18, interactive=False)
            btn.click(gen_call_sheet, [pn, sd, ct, sc, loc], [out])
        with gr.Tab("BUDGET"):
            with gr.Row():
                d = gr.Number(label="Shoot Days", value=5)
                cs = gr.Number(label="Crew Size", value=12)
                sa = gr.Number(label="SAG Cast", value=3)
            with gr.Row():
                eq = gr.Number(label="Equipment $/day", value=500)
                lc = gr.Number(label="Location $/day", value=1000)
            bbtn = gr.Button("CALCULATE BUDGET", variant="primary")
            bout = gr.Textbox(label="Budget", lines=12, interactive=False)
            bbtn.click(calc_budget, [d, cs, sa, eq, lc], [bout])
        with gr.Tab("TURAROUND"):
            with gr.Row():
                wt = gr.Textbox(label="Wrap Time", value="20:00")
                nct = gr.Textbox(label="Next Call Time", value="07:00")
            tbtn = gr.Button("CHECK TURAROUND", variant="primary")
            tout = gr.Textbox(label="Result", lines=3, interactive=False)
            tbtn.click(check_turnaround, [wt, nct], [tout])
        with gr.Tab("AI AD ASSISTANT"):
            q = gr.Textbox(label="Question", placeholder="e.g. What are SAG turnaround rules for a 12-hour shoot?", lines=2)
            abtn = gr.Button("ASK AD", variant="primary")
            aout = gr.Textbox(label="Answer", lines=10, interactive=False)
            abtn.click(ai_ad_assistant, [q], [aout])
        with gr.Tab("ABOUT"):
            gr.HTML('<div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;"><h2 style="color:#FF9F00;">Filmer\'s Companion</h2><p>Product 10 \u2014 the Ultimate Film/Television Production Suite.</p><h3 style="color:#4DD0E1;">Features</h3><ul><li>Call sheet generator (10 IATSE departments)</li><li>Budget calculator (crew, SAG, equipment, location)</li><li>SAG turnaround checker (12-hour rule)</li><li>AI Assistant Director (rules, compliance, guidance)</li></ul><p style="color:#8B949E;font-size:0.85rem;">SAG minimum: $1,082/day. OSHA compliance required. 12-hour turnaround enforced.</p></div>')

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
