# AI Agent Role Map

## Role classes

| Role class | Primary scope | Evidence |
|---|---|---|
| Theory stewardship (human-led) | Scientific direction and theory judgments | authorship statements in `README.md`, `AGENTS.md` |
| Copilot engineering agent | Code architecture, tests, and document engineering | authorship statements across core docs |
| MCP-connected research/automation agents | Repository ingest, retrieval, and tool-mediated operations | `AGENTS.md`, `9-INFRASTRUCTURE/mcp-config.json` |
| End-user Q&A agents | Public or developer-facing assistance surfaces | `9-INFRASTRUCTURE/bot/README.md` |

## Build vs audit vs deployment support split

| Function | Primary systems |
|---|---|
| Build + test execution | Python + pytest + GitHub Actions |
| Internal audit artifacts | Test suites, `ALGEBRA_PROOF.py`, tracker/changelog ledgers |
| Agent deployment support | Copilot Extension, RAG bot, Pages chatbot, Custom GPT/Claude setup docs |
| Multi-model assistant support (documented) | OpenAI/Claude/Gemini/Microsoft support paths in bot + repository docs |

## Provenance interpretation rule

- Presence of an integration path in repo documentation means the path is supported.
- Only executable workflow/config artifacts in this repository count as confirmed active usage.
