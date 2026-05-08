# Master Inventory — Programs, Suites, Languages, and AI Systems

## 1) Confirmed in-repo usage

### Languages and formats

| Category | Confirmed items | Evidence |
|---|---|---|
| Core implementation | Python | `src/**/*.py`, `tests/**/*.py`, `recycling/**/*.py` |
| CI/config | YAML | `.github/workflows/tests.yml`, `docs/mas_tracker.yml` |
| Documentation | Markdown | `README.md`, `FALLIBILITY.md`, `STATUS.md` |
| Publication sources | LaTeX, BibTeX | `arxiv/main.tex`, `arxiv/references.bib` |
| Metadata/exchange | JSON / JSON-LD / CFF YAML | `9-INFRASTRUCTURE/mcp-config.json`, `9-INFRASTRUCTURE/schema.jsonld`, `CITATION.cff` |
| Bot/web infra | JavaScript (Node) | `9-INFRASTRUCTURE/bot/copilot-extension/server.js`, `package.json` |
| Utility scripts | Shell, MATLAB | `9-INFRASTRUCTURE/update_numbers.sh`, `9-INFRASTRUCTURE/demo.m` |

### Programs and suites

| Function | Confirmed programs/suites | Evidence |
|---|---|---|
| Test execution | `pytest` | `.github/workflows/tests.yml`, `tests/` |
| Python dependency/env | `pip` | `.github/workflows/tests.yml`, `requirements.txt` |
| Core numerical stack | `numpy`, `scipy` | `requirements.txt`, imports in `src/` |
| Symbolic/formal checks | `sympy` | `.github/workflows/tests.yml` (`algebra-proof`), `requirements.txt` |
| CI/CD orchestration | GitHub Actions | `.github/workflows/*.yml` |
| Algebraic falsification harness | `ALGEBRA_PROOF.py` | `ALGEBRA_PROOF.py`, `.github/workflows/tests.yml` |

### AI systems and agent surfaces

| Class | Confirmed system/surface | Evidence |
|---|---|---|
| Primary code/doc engineering agent | GitHub Copilot (AI) | repository-wide authorship statements in docs |
| Repository agent policy layer | MCP-connected agents (e.g., Mythos) | `AGENTS.md`, `9-INFRASTRUCTURE/mcp-config.json` |
| Copilot Chat integration | GitHub Copilot Extension (`@unitary-manifold`) | `9-INFRASTRUCTURE/bot/copilot-extension/` |
| RAG assistant pipeline | Python RAG bot | `9-INFRASTRUCTURE/bot/rag/` |

## 2) Available infrastructure (do not over-claim as always active)

| Option | Availability in repo | Evidence |
|---|---|---|
| Custom GPT / Claude Project setup | Supported by docs/prompts | `9-INFRASTRUCTURE/bot/custom-gpt/SETUP_GUIDE.md`, `SYSTEM_PROMPT.md` |
| GitHub Pages chatbot | Supported widget deployment path | `9-INFRASTRUCTURE/bot/pages-chatbot/README.md` |
| MCP GitHub server | Configuration available | `9-INFRASTRUCTURE/mcp-config.json`, `AGENTS.md` |
| MCP Bright Data server | Configuration available | `9-INFRASTRUCTURE/mcp-config.json`, `AGENTS.md` |

## 3) Canonical status pointers

- Current MAS/post-MAS tracker: `docs/mas_tracker.yml`
- Current wave-level changelog: `docs/WAVE_CHANGELOG.md`
- Canonical limitations/falsification framing: `FALLIBILITY.md`

