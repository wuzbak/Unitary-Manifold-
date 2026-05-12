# AI Agent Role Map

## Role classes

| Role class | Primary scope | Evidence |
|---|---|---|
| Theory stewardship (human-led) | Scientific direction and theory judgments | authorship statements in `README.md`, `AGENTS.md` |
| Copilot engineering agent (chat + inline + cloud coding agent) | Code architecture, tests, and document engineering | authorship statements across core docs; this PR session |
| MCP-connected research/automation agents | Repository ingest, retrieval, and tool-mediated operations | `AGENTS.md`, `9-INFRASTRUCTURE/mcp-config.json` |
| Public Q&A assistants (ChatGPT Custom GPT, Claude Project) | End-user theory Q&A; zero-code deployment | `9-INFRASTRUCTURE/bot/custom-gpt/SETUP_GUIDE.md` |
| RAG bot | Embedded knowledge-base Q&A with OpenAI backend | `9-INFRASTRUCTURE/bot/rag/` |
| Copilot Chat Extension | In-IDE / GitHub.com assistant surface | `9-INFRASTRUCTURE/bot/copilot-extension/` |

## Build vs audit vs deployment support split

| Function | Primary systems |
|---|---|
| Build + test execution | Python + pytest + GitHub Actions (7 CI jobs) |
| Internal audit artifacts | Test suites, `ALGEBRA_PROOF.py`, ledger-consistency, tracker/changelog ledgers |
| Agent deployment support | Copilot Extension, RAG bot, Pages chatbot, Custom GPT / Claude Project setup docs |
| Multi-model assistant support (documented) | OpenAI / Anthropic Claude / Google Gemini / Microsoft Copilot support paths in bot + repository docs |

## Provenance interpretation rule

- Presence of an integration path in repo documentation means the path is supported.
- Only executable workflow/config artifacts in this repository count as confirmed active usage.
