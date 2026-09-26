import gradio as gr
import requests
import json

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
.gradio-container .gr-button-primary:hover { background: var(--az-teal) !important; }
"""

RB_MIRRORS = ["https://all.api.radio-browser.info", "https://fi1.api.radio-browser.info"]

def search_stations(query="", tag="", country="", limit=20):
    try:
        params = {"limit": str(limit), "order": "votes", "reverse": "true", "hidebroken": "true"}
        if query: params["name"] = query
        if tag: params["tag"] = tag
        if country: params["country"] = country
        for mirror in RB_MIRRORS:
            r = requests.get(f"{mirror}/json/stations/search", params=params, headers={"User-Agent":"AZ-SDR-Radio/1.0"}, timeout=10)
            if r.ok:
                stations = r.json()
                if stations:
                    lines = []
                    for s in stations[:limit]:
                        name = s.get("name", "?")
                        codec = s.get("codec", "?")
                        bitrate = s.get("bitrate", "?")
                        votes = s.get("votes", 0)
                        url = s.get("url_resolved", s.get("url", ""))
                        lines.append(f"{name} [{codec} {bitrate}kbps, {votes} votes]\n  {url}")
                    return "\n".join(lines)
        return "No stations found."
    except Exception as e: return f"Error: {e}"

def get_nasa_news():
    try:
        r = requests.get("https://www.nasa.gov/feed/", timeout=10, headers={"User-Agent":"AZ"})
        if not r.ok: return "NASA feed unavailable"
        import re
        titles = re.findall(r'<title>(.*?)</title>', r.text)[1:6]
        return "\n".join(titles) if titles else "No NASA news."
    except Exception as e: return f"Error: {e}"

def get_defense_news():
    try:
        r = requests.get("https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=1065&max=10", timeout=10, headers={"User-Agent":"AZ"})
        if not r.ok: return "Defense feed unavailable"
        import re
        titles = re.findall(r'<title>(.*?)</title>', r.text)[1:6]
        return "\n".join(titles) if titles else "No defense news."
    except Exception as e: return f"Error: {e}"

with gr.Blocks(css=custom_css, title="SDR Radio — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">SDR RADIO</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">ALL-BAND RADIO CONSOLE · AXIOMZERO</div></div>')
    with gr.Tabs():
        with gr.Tab("STATIONS"):
            gr.HTML('<div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;margin-bottom:1rem;">Browse 50,000+ radio stations via radio-browser API</div>')
            with gr.Row():
                q = gr.Textbox(label="Search by name", placeholder="e.g. NPR, BBC, Jazz...")
                tag = gr.Textbox(label="Filter by tag", placeholder="e.g. news, jazz, rock")
                country = gr.Textbox(label="Filter by country", placeholder="e.g. United States")
            search_btn = gr.Button("SEARCH STATIONS", variant="primary")
            results = gr.Textbox(label="Results", lines=15, interactive=False)
            search_btn.click(search_stations, [q, tag, country], [results])
            app.load(lambda: search_stations(limit=15), [], [results])
        with gr.Tab("NEWS FEEDS"):
            with gr.Row():
                nasa_out = gr.Textbox(label="NASA News", lines=8, interactive=False)
                def_out = gr.Textbox(label="Defense News", lines=8, interactive=False)
            refresh = gr.Button("REFRESH FEEDS", variant="primary")
            refresh.click(lambda: (get_nasa_news(), get_defense_news()), [], [nasa_out, def_out])
            app.load(lambda: (get_nasa_news(), get_defense_news()), [], [nasa_out, def_out])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
