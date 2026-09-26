# AxiomZero HuggingFace Spaces

The real AxiomZero webspace — built on HuggingFace Spaces (free tier, CPU).

## Live Spaces (15)

| # | Space | Description | AI | Status |
|---|-------|-------------|----|--------|
| 1 | [psicat-navigator](https://huggingface.co/spaces/Wuzbak/psicat-navigator) | AI chat, repo status, products | \u2705 | LIVE |
| 2 | axiomzero-portal | Landing page, mission, framework | | CODE READY |
| 3 | geo-monitor | USGS, NASA EONET, GDACS, NWS, volcanoes | | CODE READY |
| 4 | sdr-radio | 50k+ stations, NASA/defense news | | CODE READY |
| 5 | dnd-assistant | Dice, NPC gen, encounters, AI DM | \u2705 | CODE READY |
| 6 | falsification-lab | 7 live experiments tracker | | CODE READY |
| 7 | terra-os | Weather, hardiness zones, climate | | CODE READY |
| 8 | knowledge-hub | Framework docs, repo browser, pillars | | CODE READY |
| 9 | training-gym | Pillar challenge console | | CODE READY |
| 10 | delphi-oracle | 5 AI oracles (physics/ethics/gov/pred/manifold) | \u2705 | CODE READY |
| 11 | axiom-journalist | SEC EDGAR, ICIJ, ProPublica, Wayback | | CODE READY |
| 12 | film-companion | Call sheets, budget, turnaround, AI AD | \u2705 | CODE READY |
| 13 | space-weather | Kp index, X-ray flares, solar wind, aurora, SDO | | CODE READY |
| 14 | lean4-registry | Theorem count, hardgate verdicts, repo browser | | CODE READY |
| 15 | corporate | SPC charter, Pentad, ECLIPSA, products | | CODE READY |

## Auto-Deploy

Pushes to `hf-spaces/` trigger `.github/workflows/deploy-hf-spaces.yml`.
Requires `HF_TOKEN` in GitHub repo secrets.

## Design System

- Deep charcoal (#0B0F13), Amber (#FF9F00), Teal (#4DD0E1)
- JetBrains Mono headings, Inter body
- Hard-angled containers, glass panels

## Technology

- Gradio (pre-installed on HF Spaces)
- HuggingFace Inference API (Llama-3.1-8B-Instruct)
- Free public APIs only (no keys needed for users)

## Theory & Code

- Theory: ThomasCory Walker-Pearson
- Code: PsiCat Navigator (AI)
- License: Defensive Public Commons License v1.0
