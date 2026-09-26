# AxiomZero HuggingFace Spaces

The real AxiomZero webspace — built on HuggingFace Spaces (free tier, CPU).

## Live Spaces

| # | Space | Description | Status |
|---|-------|-------------|--------|
| 1 | [psicat-navigator](https://huggingface.co/spaces/Wuzbak/psicat-navigator) | AI chat, repo status, products | LIVE |
| 2 | axiomzero-portal | Landing page, mission, framework | CODE READY |
| 3 | geo-monitor | Live disaster monitoring (USGS, NASA, GDACS) | CODE READY |
| 4 | sdr-radio | Radio station browser + news feeds | CODE READY |
| 5 | dnd-assistant | Dice roller, NPC gen, encounter builder, AI DM | CODE READY |
| 6 | falsification-lab | 7 live experiment tracker | CODE READY |
| 7 | terra-os | Weather, hardiness zones, earth sciences | CODE READY |
| 8 | knowledge-hub | Framework docs, repo browser, pillars | CODE READY |
| 9 | training-gym | Pillar challenge console | CODE READY |
| 10 | delphi-oracle | 5-oracle consultation system | CODE READY |
| 11 | axiom-journalist | SEC, ICIJ, nonprofits, Wayback | CODE READY |

## Auto-Deploy

Pushes to `hf-spaces/` trigger the GitHub Action (`.github/workflows/deploy-hf-spaces.yml`)
which auto-creates and deploys each Space on HuggingFace.

Requires `HF_TOKEN` secret in GitHub repo settings.

## Design System

All Spaces use the AxiomZero design system:
- Deep charcoal background (#0B0F13)
- Amber (#FF9F00) for headers/actions
- Ice Blue/Teal (#4DD0E1) for framework data
- JetBrains Mono for headings, Inter for body
- Hard-angled containers (no rounded corners)
- Glass panels with border treatment

## Technology

- **Gradio** (pre-installed on HF Spaces)
- **HuggingFace Inference API** (Llama-3.1-8B-Instruct)
- **Free public APIs** (USGS, NASA EONET, GDACS, NWS, radio-browser, SEC EDGAR, ICIJ, ProPublica, Wayback)
- No API keys required for end users

## Theory & Code

- Theory: ThomasCory Walker-Pearson
- Code: PsiCat Navigator (AI)
- License: Defensive Public Commons License v1.0
