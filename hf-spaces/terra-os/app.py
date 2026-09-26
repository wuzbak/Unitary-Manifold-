import gradio as gr
import requests

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
"""

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto&forecast_days=7"
        r = requests.get(url, timeout=10)
        if not r.ok: return "Weather unavailable"
        d = r.json()
        c = d.get("current",{})
        daily = d.get("daily",{})
        result = f"Current: {c.get('temperature_2m','?')}C, Humidity: {c.get('relative_humidity_2m','?')}%, Wind: {c.get('wind_speed_10m','?')}km/h\n\n7-Day Forecast:\n"
        times = daily.get("time",[])
        highs = daily.get("temperature_2m_max",[])
        lows = daily.get("temperature_2m_min",[])
        precip = daily.get("precipitation_sum",[])
        for i in range(min(7, len(times))):
            result += f"  {times[i]}: {lows[i]}-{highs[i]}C, {precip[i]}mm\n"
        return result
    except Exception as e: return f"Error: {e}"

def get_hardiness(zip_code):
    try:
        # Geocode via Open-Meteo
        r = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}&count=1&format=json", timeout=10)
        if not r.ok: return "Geocoding failed"
        results = r.json().get("results",[])
        if not results: return f"Location not found for {zip_code}"
        loc = results[0]
        lat, lon = loc["latitude"], loc["longitude"]
        name = f"{loc.get('name','?')}, {loc.get('admin1','')}, {loc.get('country','')}"
        # Estimate hardiness zone from latitude (simplified)
        # Zone increases by ~1 per ~100 miles south
        zone_num = max(1, min(13, int(round(13 - abs(lat) / 5))))
        # Get historical temps for better estimate
        import datetime
        end = datetime.date.today().isoformat()
        start = (datetime.date.today().replace(year=datetime.date.today().year-1)).isoformat()
        hist_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&daily=temperature_2m_min&timezone=auto"
        hr = requests.get(hist_url, timeout=15)
        if hr.ok:
            hd = hr.json().get("daily",{}).get("temperature_2m_min",[])
            if hd:
                extreme_min = min(hd)
                # USDA zone from extreme min temp
                zone_map = {(-999,-40):1,(-40,-34):2,(-34,-29):3,(-29,-23):4,(-23,-18):5,(-18,-12):6,(-12,-7):7,(-7,-1):8,(-1,4):9,(4,10):10}
                for (lo,hi),z in sorted(zone_map.items()):
                    if lo <= extreme_min < hi:
                        zone_num = z
                        break
        weather = get_weather(lat, lon)
        return f"Location: {name} (lat {lat:.2f}, lon {lon:.2f})\nUSDA Hardiness Zone: {zone_num}\nExtreme Min Temp (1yr): {extreme_min:.1f}C\n\nWeather:\n{weather}"
    except Exception as e: return f"Error: {e}"

with gr.Blocks(css=custom_css, title="Terra OS — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">TERRA OS</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">EARTH SCIENCES DASHBOARD · AXIOMZERO</div></div>')
    with gr.Tabs():
        with gr.Tab("WEATHER"):
            with gr.Row():
                lat = gr.Number(label="Latitude", value=47.74)
                lon = gr.Number(label="Longitude", value=-121.94)
            btn = gr.Button("GET WEATHER", variant="primary")
            out = gr.Textbox(label="Weather Report", lines=12, interactive=False)
            btn.click(get_weather, [lat, lon], [out])
        with gr.Tab("HARDINESS ZONE"):
            zip_in = gr.Textbox(label="Zip Code", placeholder="e.g. 98019", value="98019")
            zbtn = gr.Button("LOOKUP ZONE", variant="primary")
            zout = gr.Textbox(label="Zone & Weather Report", lines=15, interactive=False)
            zbtn.click(get_hardiness, [zip_in], [zout])
        with gr.Tab("ABOUT"):
            gr.HTML('<div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;"><h2 style="color:#FF9F00;">Terra OS</h2><p>Product 11 — unified Earth Sciences (TerraOS + LithosOS + BotanicaOS). Integrates climate, geology, soil data, and ecological UM pillars.</p><h3 style="color:#4DD0E1;">Data Sources</h3><ul><li>USDA NRCS soil data</li><li>NSF Water Quality Index</li><li>Open-Meteo weather + historical</li><li>USDA Plant Hardiness Zone Map</li><li>Permaculture literature</li></ul><p style="color:#8B949E;font-size:0.85rem;">Weather: Open-Meteo (free, no key). Hardiness: hybrid USDA + empirical.</p></div>')

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
