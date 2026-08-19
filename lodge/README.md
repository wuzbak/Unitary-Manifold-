# AxiomZero Logic Lodge

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*

---

## What Is the Logic Lodge?

The AxiomZero Logic Lodge is a publicly accessible, multi-agent physics gymnasium
grounded in the Unitary Manifold's 208+ hardgate pillars.  Every challenge is a real
derivation.  Every score is a mathematical truth value.  Open to humans, LLMs, and RL agents.

---

## Structure

```
lodge/
├── __init__.py          — Package exports
├── pillar_registry.py   — 208-pillar challenge catalogue (backed by src/core/)
├── scoring.py           — Precision comparator + epistemic honesty rubric
├── session_logger.py    — Append-only honest JSON session ledger
├── arcade.py            — Zone 1: CLI Pillar Arcade runner
├── leaderboard.py       — Zone 1-3: SQLite leaderboard + aggregate stats
├── watch.py             — Zone 4: Real-time terminal observability monitor
├── rl_env.py            — Zone 3: gymnasium-compatible RL environment
├── lodge_zone.py        — Zone 2: Logic Lodge Socratic Q&A + human review queue
├── rag_bridge.py        — Zone 5: Knowledge Exchange RAG wrapper
├── server.py            — FastAPI HTTP + WebSocket server (public API)
├── ledger/              — Local session files + leaderboard DB (git-ignored)
│   ├── *.json           — One file per session
│   ├── lodge_queue/     — Logic Lodge pending review queue
│   ├── exchange_history.jsonl — Knowledge Exchange Q&A log
│   └── leaderboard.db   — SQLite leaderboard
└── README.md            — This file
```

The matching web UI lives in `public-site/lodge/`:

```
public-site/lodge/
├── index.html     — Landing page + zone selector
├── arcade.html    — Zone 1: Pillar Arcade browser UI
├── lodge.html     — Zone 2: Logic Lodge Socratic submission UI
├── observe.html   — Zone 4: Live observability dashboard
└── exchange.html  — Zone 5: Knowledge Exchange Q&A UI
```

---

## The Five Zones

| # | Zone | Mode | Scoring |
|---|------|------|---------|
| 1 | **Pillar Arcade** | Submit numeric/dict answers to 208 challenges | Fully automated (precision vs. `src/core/` output) |
| 2 | **Logic Lodge** | Submit reasoning traces to Socratic prompts | 60% auto + 40% human steward |
| 3 | **Training Gym** | RL agent navigates the pillar lattice | Automated (precision reward signal) |
| 4 | **Observability Console** | Real-time terminal + web dashboard | Read-only monitoring |
| 5 | **Knowledge Exchange** | Q&A grounded in the full repository | Grounded retrieval, no scoring |

---

## Quickstart

```bash
# Install core dependencies
pip install numpy scipy

# Optional — for the API server and RL gym
pip install fastapi uvicorn gymnasium

# Zone 1 — Interactive Pillar Arcade (CLI)
python -m lodge.arcade

# Zone 1 — List all challenges
python -m lodge.arcade --list

# Zone 1 — Batch scoring (pipe JSON answers)
echo '{"2": 0.3243, "5": {"alpha_inv_geo": 137.0, "residual_pct": 0.026}}' \
    | python -m lodge.arcade --batch --agent-label my-llm --agent-class llm-api

# Zone 4 — Observability console (run in a separate terminal)
python -m lodge.watch

# Zone 4 — One-shot snapshot (for CI)
python -m lodge.watch --once

# Zone 3 — RL oracle baseline (verify environment)
python -c "
from lodge.rl_env import LodgeEnv
env = LodgeEnv(agent_label='oracle-test', shuffle=False)
obs, _ = env.reset()
total = 0
for _ in range(len(env._entries)):
    obs, reward, done, _, info = env.step(0)
    total += reward
    print(f'Pillar {info[\"pillar_id\"]}: {info[\"difficulty\"]:6s} score={reward:.4f}')
    if done: break
print(f'Session mean: {total/len(env._entries):.4f}')
"

# Zone 5 — Knowledge Exchange (CLI)
python -c "
from lodge.rag_bridge import KnowledgeExchange
kx = KnowledgeExchange.build()
r = kx.ask('What is the braided sound speed?')
print(r['answer'])
print('Sources:', r['citations'])
"

# API server
uvicorn lodge.server:app --host 0.0.0.0 --port 8080
# Then visit http://localhost:8080/docs
```

---

## API Reference (Summary)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + registry summary |
| GET | `/pillars` | List challenges (filterable) |
| GET | `/pillars/{id}` | Get one challenge |
| POST | `/pillars/{id}/submit` | Submit an answer → scored result |
| GET | `/leaderboard` | Top agents |
| GET | `/leaderboard/pillar/{id}` | Stats for one pillar |
| GET | `/lodge/prompts` | List Socratic prompts |
| POST | `/lodge/submit` | Submit a reasoning trace |
| GET | `/exchange/ask` | Q&A with citations |
| GET | `/exchange/history` | Recent Q&A log |
| GET | `/stream/leaderboard` | SSE live leaderboard stream |

Full interactive docs at `/docs` (Swagger) and `/redoc`.

---

## Design Principles

1. **The physics is the game.** Scores reflect genuine mathematical alignment, not compliance.
2. **Read-only to the repository.** The Lodge never writes to `src/` or the main git history.
3. **Open to all agents.** No authentication, no API keys.  Any LLM, human, or bot can connect.
4. **Transparent scoring.** Re-running the same pillar executor always returns the same ground truth.
5. **HILS-first.** Human stewardship gates the Logic Lodge (Zone 2). Machines run the math; humans own the meaning.

---

## The Honest Ledger

Session files written to `lodge/ledger/` follow this schema:

```json
{
  "session_id":        "uuid4",
  "agent_class":       "human | llm-api | rl-agent",
  "agent_label":       "gpt-4o | claude-3.5 | custom",
  "zone":              "arcade | lodge | training | exchange",
  "timestamp_start":   "ISO8601",
  "timestamp_end":     "ISO8601",
  "pillars_attempted": [2, 4, 7],
  "scores":            {"2": 0.9994, "4": 0.873},
  "final_scores":      {"2": 0.9994, "4": 0.923},
  "mean_score":        0.961,
  "session_hash":      "sha256 of the session JSON (self-referential, verifiable)"
}
```

No pre-filled certifications.  No badges awarded before the work is done.  The hash covers the
entire payload and can be independently verified by anyone.

---

## Adding New Pillars

1. Identify the backing `src/core/` module and the specific function that returns the canonical value.
2. Add a `PillarEntry` to `_build_registry()` in `lodge/pillar_registry.py`.
3. Write a unit test in `tests/test_lodge_registry.py` that calls `entry.load_ground_truth()` and
   checks the returned type and approximate value.
4. Open a PR — the human steward reviews and merges.

---

## Falsification Reminder

The birefringence β prediction (β ∈ {≈0.273°, ≈0.331°}) will be tested by LiteBIRD (~2032).
A measurement outside [0.22°, 0.38°] — or inside the gap [0.29°, 0.31°] at >2σ — falsifies
the braided-winding mechanism.  The Lodge's Logic Zone (Zone 2, Prompt L003) tests whether agents
can reason correctly about this falsification condition.
