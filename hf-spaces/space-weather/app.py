import gradio as gr
import requests

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
"""

SW = "https://services.swpc.noaa.gov"
KP_SCALE = [
    (4, "G0", "Quiet", "#3fb950"), (5, "G1", "Minor", "#4dd0e1"),
    (6, "G2", "Moderate", "#ffd60a"), (7, "G3", "Strong", "#ff9f0a"),
    (8, "G4", "Severe", "#ff6b6b"), (10, "G5", "Extreme", "#bc8cff"),
]

def get_kp():
    try:
        r = requests.get(f"{SW}/json/planetary_k_index_1m.json", timeout=10)
        if not r.ok: return "Kp index unavailable"
        data = r.json()
        if not data: return "No Kp data"
        last = data[-1]
        v = float(last.get("estimated_kp", last.get("kp_index", 0)))
        for max_v, level, label, color in KP_SCALE:
            if v <= max_v:
                return f"Kp = {v:.1f} \u2014 {level} ({label})\nTime: {last.get('time_tag','?')}"
        return f"Kp = {v:.1f} \u2014 G5 (Extreme)"
    except Exception as e: return f"Error: {e}"

def get_xray():
    try:
        r = requests.get(f"{SW}/json/goes/primary/xrays-6-hour.json", timeout=10)
        if not r.ok: return "X-ray data unavailable"
        data = r.json()
        short = [x for x in data if x.get("energy") == "0.05-0.4nm"]
        if not short: short = data
        last = short[-1] if short else {}
        flux = last.get("flux", "?")
        time = last.get("time_tag", "?")
        # Classify flare
        try:
            f = float(flux)
            if f >= 1e-4: cls = "X-class (Severe)"
            elif f >= 1e-5: cls = "M-class (Medium)"
            elif f >= 1e-6: cls = "C-class (Small)"
            elif f >= 1e-7: cls = "B-class (Tiny)"
            else: cls = "A-class (Quiet)"
        except: cls = "Unknown"
        return f"X-ray Flux: {flux}\nClass: {cls}\nTime: {time}"
    except Exception as e: return f"Error: {e}"

def get_solar_wind():
    try:
        pr = requests.get(f"{SW}/json/ace/swepam/ace_swepam_1h.json", timeout=10)
        mr = requests.get(f"{SW}/json/ace/mag/ace_mag_1h.json", timeout=10)
        speed = density = bz = bt = "?"
        if pr.ok:
            pdata = pr.json()
            if pdata: 
                last = pdata[-1]
                speed = last.get(2, last.get("speed", "?"))
                density = last.get(1, last.get("density", "?"))
        if mr.ok:
            mdata = mr.json()
            if mdata:
                last = mdata[-1]
                bz = last.get(3, last.get("bz", "?"))
                bt = last.get(4, last.get("bt", "?"))
        return f"Solar Wind Speed: {speed} km/s\nDensity: {density} p/cm3\nBz: {bz} nT\nBt: {bt} nT"
    except Exception as e: return f"Error: {e}"

def get_aurora():
    try:
        r = requests.get(f"{SW}/json/ovation_aurora_latest.json", timeout=10)
        if not r.ok: return "Aurora data unavailable"
        data = r.json()
        coords = data.get("coordinates", [])
        north_min = 90; south_max = -90
        for entry in coords:
            lon, lat, prob = entry[0], entry[1], entry[2]
            if prob >= 0.3:
                if lat > 0 and lat < north_min: north_min = lat
                if lat < 0 and lat > south_max: south_max = lat
        n = f"{north_min:.1f}\u00b0N" if north_min < 90 else "None detected"
        s = f"{abs(south_max):.1f}\u00b0S" if south_max > -90 else "None detected"
        return f"Aurora Forecast:\n  Northern: {n}\n  Southern: {s}\n  Forecast: {data.get('Forecast Time', data.get('Observation Time', '?'))}"
    except Exception as e: return f"Error: {e}"

def get_alerts():
    try:
        r = requests.get(f"{SW}/products/alerts.json", timeout=10)
        if not r.ok: return "No alerts available"
        alerts = r.json()[-10:][::-1]
        if not alerts: return "No active space weather alerts."
        lines = []
        for a in alerts:
            lines.append(f"{a.get('product_id','?')}: {a.get('summary','')[:100]}")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

def refresh_all():
    return get_kp(), get_xray(), get_solar_wind(), get_aurora(), get_alerts()

with gr.Blocks(css=custom_css, title="Space Weather — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">SPACE WEATHER</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">SOLAR ACTIVITY MONITOR · AXIOMZERO</div></div>')
    with gr.Row():
        kp_out = gr.Textbox(label="Kp Index (Geomagnetic)", lines=3, interactive=False)
        xr_out = gr.Textbox(label="X-ray Flux (Solar Flares)", lines=3, interactive=False)
    with gr.Row():
        sw_out = gr.Textbox(label="Solar Wind (ACE)", lines=5, interactive=False)
        au_out = gr.Textbox(label="Aurora Forecast", lines=5, interactive=False)
    with gr.Row():
        al_out = gr.Textbox(label="SWPC Alerts", lines=8, interactive=False)
        refresh = gr.Button("REFRESH ALL", variant="primary")
    refresh.click(refresh_all, [], [kp_out, xr_out, sw_out, au_out, al_out])
    app.load(refresh_all, [], [kp_out, xr_out, sw_out, au_out, al_out])
    gr.HTML('<div style="text-align:center;margin-top:1rem;"><img src="https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_0171.jpg" style="width:400px;border:1px solid #1F2933;" alt="SDO AIA 171"><div style="color:#8B949E;font-size:0.75rem;margin-top:0.5rem;">SDO/AIA 171\u00c5 \u2014 Live Solar Image (NASA)</div></div>')

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
