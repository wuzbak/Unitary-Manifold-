import gradio as gr
import requests
import json

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
"""

def search_sec(query):
    try:
        url = f"https://efts.sec.gov/LATEST/search-index?q={query}&forms=10-K,10-Q,8-K,4,SC-13D"
        r = requests.get(url, headers={"User-Agent":"AxiomZero-Journalist admin@axiomzerospc.org"}, timeout=15)
        if not r.ok: return f"SEC EDGAR error: {r.status_code}"
        data = r.json()
        hits = (data.get("hits",{}).get("hits",[]))[:5]
        if not hits: return "No SEC filings found."
        lines = []
        for h in hits:
            s = h.get("_source",{})
            form = s.get("form","?")
            name = (s.get("display_names") or [query])[0]
            date = s.get("file_date","?")
            cik = (s.get("ciks") or ["?"])[0]
            lines.append(f"[{form}] {name} \u2014 Filed: {date} \u2014 CIK: {cik}")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

def search_icij(query):
    try:
        results = []
        for entity_type in ["Officer", "Entity", "Intermediary"]:
            r = requests.post("https://offshoreleaks.icij.org/api/v1/reconcile",
                headers={"Content-Type":"application/json","User-Agent":"AZ-Journalist"},
                json={"query": query, "type": entity_type, "limit": 5}, timeout=10)
            if r.ok:
                for item in r.json().get("result",[]):
                    if item.get("score",0) >= 0.3:
                        name = item.get("name","?")
                        score = item.get("score",0)
                        nid = item.get("id","")
                        results.append(f"[{entity_type}] {name} \u2014 Score: {score:.2f} \u2014 ID: {nid}")
        return "\n".join(results[:10]) if results else "No ICIJ matches found."
    except Exception as e: return f"Error: {e}"

def search_propublica(query):
    try:
        r = requests.get(f"https://projects.propublica.org/nonprofits/api/v2/search.json?q={query}", timeout=10)
        if not r.ok: return "ProPublica unavailable"
        orgs = r.json().get("organizations",[])[:5]
        if not orgs: return "No nonprofits found."
        lines = []
        for o in orgs:
            lines.append(f"{o.get('name','?')} \u2014 EIN: {o.get('ein','?')} \u2014 State: {o.get('state','?')} \u2014 Income: {o.get('income_amount','?')}")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

def search_wayback(url):
    try:
        target = url if url.startswith("http") else f"http://{url}"
        r = requests.get(f"https://web.archive.org/cdx/search/cdx?url={target}&output=json&limit=5", timeout=10)
        if not r.ok: return "Wayback unavailable"
        rows = r.json()
        if len(rows) < 2: return "No archives found."
        lines = []
        for row in rows[1:6]:
            ts = row[1] if len(row) > 1 else ""
            date = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 else "?"
            lines.append(f"Snapshot: {date} \u2014 {row[2] if len(row) > 2 else target}")
        return "\n".join(lines)
    except Exception as e: return f"Error: {e}"

with gr.Blocks(css=custom_css, title="AXIOM Journalist — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">AXIOM JOURNALIST</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">INVESTIGATIVE RESEARCH · AXIOMZERO</div></div>')
    with gr.Tabs():
        with gr.Tab("SEC EDGAR"):
            q1 = gr.Textbox(label="Company or Person", placeholder="e.g. BlackRock, Tesla")
            b1 = gr.Button("SEARCH SEC", variant="primary")
            o1 = gr.Textbox(label="SEC Filings", lines=10, interactive=False)
            b1.click(search_sec, [q1], [o1])
        with gr.Tab("ICIJ OFFSHORE"):
            q2 = gr.Textbox(label="Name to Search", placeholder="e.g. shell company name")
            b2 = gr.Button("SEARCH LEAKS", variant="primary")
            o2 = gr.Textbox(label="ICIJ Results", lines=10, interactive=False)
            b2.click(search_icij, [q2], [o2])
        with gr.Tab("NONPROFITS"):
            q3 = gr.Textbox(label="Organization Name", placeholder="e.g. Clinton Foundation")
            b3 = gr.Button("SEARCH 990s", variant="primary")
            o3 = gr.Textbox(label="ProPublica Results", lines=10, interactive=False)
            b3.click(search_propublica, [q3], [o3])
        with gr.Tab("WAYBACK"):
            q4 = gr.Textbox(label="URL", placeholder="e.g. example.com")
            b4 = gr.Button("SEARCH ARCHIVES", variant="primary")
            o4 = gr.Textbox(label="Wayback Results", lines=8, interactive=False)
            b4.click(search_wayback, [q4], [o4])
        with gr.Tab("ABOUT"):
            gr.HTML('<div style="color:#E0E0E0;line-height:1.8;max-width:800px;margin:0 auto;"><h2 style="color:#FF9F00;">AXIOM Journalist</h2><p>Product 08 \u2014 autonomous investigative journalism platform.</p><h3 style="color:#4DD0E1;">Sources (all free, no API keys needed)</h3><ul><li><b>SEC EDGAR</b> \u2014 federal filings (10-K, 10-Q, 8-K)</li><li><b>ICIJ Offshore Leaks</b> \u2014 Panama/Pandora/Paradise Papers</li><li><b>ProPublica Nonprofits</b> \u2014 Form 990 disclosures</li><li><b>Wayback Machine</b> \u2014 archived web pages</li></ul><p style="color:#8B949E;font-size:0.85rem;">All sources are public records. HILS gate on all publications.</p></div>')

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
