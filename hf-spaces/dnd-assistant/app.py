import gradio as gr
import random
import json
import os

HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")

custom_css = """
:root { --az-bg: #0B0F13; --az-panel: #111820; --az-amber: #FF9F00; --az-teal: #4DD0E1; --az-text: #E0E0E0; --az-muted: #8B949E; --az-border: #1F2933; }
.gradio-container { background: var(--az-bg) !important; color: var(--az-text) !important; font-family: 'Inter', system-ui, sans-serif !important; }
.gradio-container h1, .gradio-container h2 { font-family: 'JetBrains Mono', monospace !important; color: var(--az-amber) !important; }
.gradio-container .gr-block { background: var(--az-panel) !important; border: 1px solid var(--az-border) !important; border-radius: 0 !important; }
.gradio-container .gr-button-primary { background: var(--az-amber) !important; color: var(--az-bg) !important; border: none !important; border-radius: 0 !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; }
.gradio-container .gr-button-primary:hover { background: var(--az-teal) !important; }
"""

# ── Dice Roller ──
def roll_dice(notation):
    try:
        parts = notation.lower().replace(" ", "").split("d")
        n = int(parts[0]) if parts[0] else 1
        d = int(parts[1].split("+")[0].split("-")[0].split("*")[0])
        rolls = [random.randint(1, d) for _ in range(n)]
        total = sum(rolls)
        # Handle modifiers
        mod = 0
        if "+" in parts[1]: mod = int(parts[1].split("+")[1])
        elif "-" in parts[1]: mod = -int(parts[1].split("-")[1])
        total += mod
        crit = " [NAT 20!]" if d == 20 and 20 in rolls else ""
        fumble = " [NAT 1!]" if d == 20 and 1 in rolls else ""
        return f"{notation}: {rolls} = {total}{mod:+d if mod else ''}{crit}{fumble}".replace("+0","")
    except: return f"Invalid notation. Use format: 2d6, 1d20+5, 3d8-2"

# ── NPC Generator ──
NAMES = ["Theren", "Mira", "Kael", "Lyra", "Dorn", "Sera", "Vex", "Nyx","Bram", "Elara", "Gareth", "Thalia"]
RACES = ["Human", "Elf", "Dwarf", "Halfling", "Tiefling", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc"]
CLASSES = ["Fighter", "Wizard", "Rogue", "Cleric", "Ranger", "Barbarian", "Bard", "Paladin", "Warlock", "Druid", "Monk", "Sorcerer"]
PERSONALITIES = ["gruff but kind", "cheerful and naive", "suspicious of strangers", "haughty and proud", "quietly observant", "boisterous and loud", "melancholy and wise", "nervous and fidgety"]
HOOKS = ["owes a debt to the local thieves guild", "searching for a lost sibling", "hiding from the law", "secretly a spy", "cursed by a hag", "on a holy pilgrimage", "looking for revenge", "guarding a terrible secret"]

def gen_npc():
    name = random.choice(NAMES)
    race = random.choice(RACES)
    cls = random.choice(CLASSES)
    level = random.randint(1, 10)
    personality = random.choice(PERSONALITIES)
    hook = random.choice(HOOKS)
    hp = level * random.randint(6, 10)
    ac = random.randint(12, 18)
    return f"Name: {name}\nRace: {race}\nClass: {cls} (Level {level})\nHP: {hp} | AC: {ac}\nPersonality: {personality}\nPlot Hook: {hook}"

# ── Encounter Builder ──
CR_TABLE = {
    "0": 10, "1/8": 25, "1/4": 50, "1/2": 100,
    "1": 200, "2": 450, "3": 700, "4": 1100, "5": 1800,
    "6": 2300, "7": 2900, "8": 3900, "9": 5000, "10": 5900,
    "11": 7200, "12": 8400, "13": 10000, "14": 11500, "15": 13000,
    "16": 15000, "17": 18000, "18": 20000, "19": 22000, "20": 25000
}

def build_encounter(party_level, party_size, difficulty):
    try:
        pl = int(party_level)
        ps = int(party_size)
        diff_mult = {"Easy": 0.5, "Medium": 1.0, "Hard": 1.5, "Deadly": 2.0}.get(difficulty, 1.0)
        cr_key = str(pl) if pl <= 20 else "20"
        xp_threshold = CR_TABLE.get(cr_key, 200) * ps * diff_mult
        # Suggest monsters
        monster_cr = str(pl) if pl <= 20 else "20"
        num_monsters = max(1, int(xp_threshold / CR_TABLE.get(monster_cr, 200)))
        num_monsters = min(num_monsters, 12)
        return f"Encounter: {difficulty} for {ps} Level {pl} players\nXP Budget: {int(xp_threshold):,} XP\nSuggested: {num_monsters} monsters at CR {monster_cr} ({CR_TABLE.get(monster_cr, 200):,} XP each)\n\nAdjust monster count and CR based on your party composition. Environmental factors (terrain, surprise, objectives) significantly affect difficulty."
    except: return "Enter valid party level (1-20) and party size."

# ── DM AI Assistant (via HF Inference) ──
def dm_assistant(question):
    if not HF_API_KEY:
        return "AI assistant requires HUGGINGFACE_API_KEY. Set it in Space secrets."
    import requests
    system = "You are a D&D 5e Dungeon Master assistant. Be concise, creative, and fair. Follow the rules but prioritize fun. If unsure about a rule, say so and suggest a ruling."
    messages = [{"role":"system","content":system},{"role":"user","content":question}]
    try:
        r = requests.post("https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct",
            headers={"Authorization":f"Bearer {HF_API_KEY}","Content-Type":"application/json"},
            json={"model":"meta-llama/Meta-Llama-3.1-8B-Instruct","messages":messages,"max_tokens":512,"temperature":0.8,"stream":False}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if "choices" in data: return data["choices"][0]["message"]["content"]
        return f"AI unavailable (HTTP {r.status_code})"
    except Exception as e: return f"Error: {e}"

with gr.Blocks(css=custom_css, title="D&D Assistant — AxiomZero") as app:
    gr.HTML('<div style="text-align:center;padding:2rem 0;border-bottom:2px solid #FF9F00;margin-bottom:1rem;"><h1 style="font-size:2.5rem;color:#FF9F00 !important;font-family:JetBrains Mono,monospace !important;margin:0;">D&D ASSISTANT</h1><div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;letter-spacing:0.1em;margin-top:0.5rem;">5e/5.5e CAMPAIGN MANAGER · AXIOMZERO</div></div>')
    with gr.Tabs():
        with gr.Tab("DICE"):
            dice_input = gr.Textbox(label="Dice Notation", placeholder="e.g. 2d6, 1d20+5, 3d8-2", value="1d20")
            roll_btn = gr.Button("ROLL", variant="primary")
            dice_out = gr.Textbox(label="Result", lines=3, interactive=False)
            roll_btn.click(roll_dice, [dice_input], [dice_out])
        with gr.Tab("NPC GENERATOR"):
            gen_btn = gr.Button("GENERATE NPC", variant="primary")
            npc_out = gr.Textbox(label="NPC", lines=8, interactive=False)
            gen_btn.click(gen_npc, [], [npc_out])
        with gr.Tab("ENCOUNTER BUILDER"):
            with gr.Row():
                pl = gr.Number(label="Party Level", value=3)
                ps = gr.Number(label="Party Size", value=4)
                diff = gr.Dropdown(["Easy","Medium","Hard","Deadly"], value="Medium", label="Difficulty")
            enc_btn = gr.Button("BUILD ENCOUNTER", variant="primary")
            enc_out = gr.Textbox(label="Encounter", lines=8, interactive=False)
            enc_btn.click(build_encounter, [pl, ps, diff], [enc_out])
        with gr.Tab("DM ASSISTANT"):
            gr.HTML('<div style="color:#4DD0E1;font-family:monospace;font-size:0.85rem;margin-bottom:1rem;">Ask the AI Dungeon Master for rulings, descriptions, or ideas.</div>')
            dm_input = gr.Textbox(label="Your Question", placeholder="e.g. What happens when a player tries to grapple a dragon?", lines=2)
            dm_btn = gr.Button("ASK DM", variant="primary")
            dm_out = gr.Textbox(label="Answer", lines=10, interactive=False)
            dm_btn.click(dm_assistant, [dm_input], [dm_out])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
