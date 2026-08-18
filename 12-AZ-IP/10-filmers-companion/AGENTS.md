# AGENTS.md — FilmersCompanion AI Agent Policies

## 1. Agent Architecture

FilmersCompanion uses a **tiered resolver** pattern for all production queries:

```
BaseAgent.resolve(question)
  1. Remote LLM   → OpenAI API (if FILM_OPENAI_API_KEY set)
  2. Local LLM    → Ollama at FILM_LLM_URL (default: localhost:11434)
  3. Static KB    → search_kb() always answers (offline-safe)
```

## 2. Specialist Agents

| Agent | Class | Role |
|-------|-------|------|
| Cinematography | `CinematographyAdvisor` | Coverage, lighting, shot validation |
| Locations | `LocationManager` | Scout reports, permit checks |
| Finance | `FinanceOfficer` | Budget, ROI, DOOD, burn rate |
| AD Chief | `ADChief` | Call sheets, turnaround, one-liners |
| Master | `ProductionMasterAgent` | Health check across all modules |

## 3. Offline Mode

Set `FILM_OFFLINE=true` (or `1`) to force static KB only.
All agents remain fully functional — the KB covers all core production topics.

## 4. Adding KB Entries

Add entries to `desktop/app/kb/film_kb.py` — `KB_ENTRIES` list:
```python
{
    "keyword": "short search term",
    "content": "Full answer text. Be specific and actionable.",
    "source": "Source reference",
    "tags": ["optional", "tags"],
}
```

Minimum 3 characters per search word. Search is multi-word OR.

## 5. LLM Integration

### OpenAI (remote)
```bash
export FILM_OPENAI_API_KEY=sk-...
export FILM_OPENAI_MODEL=gpt-4o-mini  # default
```

### Ollama (local)
```bash
ollama pull llama3.2:3b
export FILM_LLM_URL=http://localhost:11434/api/generate
export FILM_LLM_MODEL=llama3.2:3b
```

## 6. Agent Permissions

Agents may:
- Read from the SQLite database (read-only queries)
- Call external LLM APIs (when keys are configured)
- Write to DB via explicit API endpoints only (not autonomously)

Agents must not:
- Store sensitive crew/cast PII beyond what production requires
- Make financial commitments or sign permits autonomously
- Override HILS (human-in-the-loop) checkpoints

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
