import gradio as gr
import requests
import re

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
.gradio-container .gr-button-primary:hover { background: var(--az-teal) !important; }
"""

def get_earthquakes():
    try:
        r = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_day.geojson", timeout=10)
        if not r.ok: return "USGS unavailable"
        quakes = r.json().get("features", [])
        if not quakes: return "No significant earthquakes in the last 24h."
        lines = []
        for q in quakes[:10]:
            p = q.get("properties", {})
            lines.append(f"M{p.get('mag','?')} — {p.get('title','Earthquake')}")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

def get_eonet():
    try:
        r = requests.get("https://eonet.gsfc.nasa.gov/api/v2.1/events?limit=10&days=1", timeout=10)
        if not r.ok: return "EONET unavailable"
        events = r.json().get("events", [])
        if not events: return "No natural events detected."
        lines = []
        for e in events[:10]:
            cats = [c.get("title","") for c in e.get("categories",[])]
            lines.append(f"{e.get('title','Event')} ({', '.join(cats)})")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

def get_gdacs():
    try:
        r = requests.get("https://www.gdacs.org/xml/rss_24h.xml", timeout=10, headers={"User-Agent":"AZ"})
        if not r.ok: return "GDACS unavailable"
        titles = re.findall(r'<title>(.*?)</title>', r.text)[1:11]
        return "\n".join(titles) if titles else "No GDACS alerts."
    except Exception as e: return f"Error: {e}"

def get_volcanoes():
    try:
        r = requests.get("https://volcanoes.usgs.gov/hans-public/api/volcano/getElevatedVolcanoes", timeout=10, headers={"User-Agent":"AZ"})
        if not r.ok: return "Volcano data unavailable"
        data = r.json()
        if not data: return "No elevated volcanoes."
        lines = []
        for v in data[:10]:
            lines.append(f"{v.get('volcano_name','?')} — {v.get('color_code','?')}/{v.get('alert_level','?')}")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

def get_nws():
    try:
        r = requests.get("https://api.weather.gov/alerts/active?status=actual&message_type=alert", timeout=10, headers={"User-Agent":"AZ"})
        if not r.ok: return "NWS unavailable"
        alerts = r.json().get("features", [])
        if not alerts: return "No active NWS alerts."
        lines = []
        for a in alerts[:10]:
            p = a.get("properties", {})
            lines.append(f"[{p.get('severity','?')}] {p.get('event','Alert')} — {p.get('areaDesc','?')}")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

def refresh_all():
    return get_earthquakes(), get_eonet(), get_gdacs(), get_volcanoes(), get_nws()

with gr.Blocks(css=custom_css, title="Geo Monitor — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">GEO MONITOR</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">LIVE DISASTER MONITORING · AXIOMZERO</div></div>')
    with gr.Row():
        eq = gr.Textbox(label="Earthquakes (USGS)", lines=8, interactive=False)
        eo = gr.Textbox(label="Natural Events (NASA EONET)", lines=8, interactive=False)
    with gr.Row():
        gd = gr.Textbox(label="GDACS Alerts", lines=8, interactive=False)
        vc = gr.Textbox(label="Volcanoes (USGS)", lines=8, interactive=False)
    with gr.Row():
        nw = gr.Textbox(label="NWS Weather Alerts", lines=8, interactive=False)
        refresh = gr.Button("REFRESH ALL FEEDS", variant="primary")
    refresh.click(refresh_all, [], [eq, eo, gd, vc, nw])
    app.load(refresh_all, [], [eq, eo, gd, vc, nw])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
