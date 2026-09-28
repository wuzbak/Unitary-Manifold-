# PsiCat Braided Brain
## Product 25 — Toroidal brain simulator game for desktop and mobile

PsiCat Braided Brain is a responsive, installable browser game built for **desktop and mobile** that turns real neuroscience ideas into a playful toroidal puzzle loop. The player moves PsiCat through wrapped boards, stabilizes gut-brain and fly-brain lanes, braids PsiCat with PhiCat, and exports explicit training packets derived from solved missions and science-card choices.

> **Integrity boundary:** this product uses real brain-science inspiration, public connectome references, and repository neuroscience documents, but it does **not** claim to prove consciousness theory, validate every repository-wide brain correspondence, or collect hidden biometric/user-surveillance data.

## What ships in v1.0.0

- **Playable toroidal puzzle campaign** with four science-backed levels.
- **Desktop + mobile responsive UI** with keyboard buttons and touch swipes.
- **PsiCat coach lane** that can optionally call Product 20 via `/api/psicat`.
- **Science checks** tied to explicit sources and boundaries rather than lore-only trivia.
- **Voluntary training-packet export** in JSON and JSONL formats for downstream PsiCat review or transformation.
- **Local-only default retention** using browser storage; nothing leaves the device unless the player explicitly exports it or points the coach at a local Product 20 endpoint.

## Design sources inside this repository

- `4-IMPLICATIONS/brain/TORUS_ARCHITECTURE.md` — toroidal navigation and wrapping intuition.
- `src/core/pillar538_enteric_neural_core.py` — ENS / gut-brain adjacent-track framing and explicit honesty boundary.
- `4-IMPLICATIONS/brain/MALECNS_CONNECTOME_BRIDGE.md` — compact fruit-fly connectome bridge and role taxonomy.
- `data/malecns/benchmark_panel.json` — committed MaleCNS benchmark slice used for role cues.
- `12-AZ-IP/20-psicat-navigator/README.md` — optional PsiCat coaching endpoint and Product 20 integration surface.

## External research inspiration

This build was also shaped by contemporary citizen-science / serious-game patterns such as Foldit, EteRNA, Borderlands Science, and Sea Hero Quest, plus public fruit-fly connectome interfaces like Virtual Fly Brain and FlyWire. The game uses those lessons carefully: short loops, meaningful choices, visible real-world grounding, and reusable structured outputs.

## Privacy and training stance

- **No surveillance:** no hidden telemetry, biometrics, ads, or remote account requirement.
- **Local by default:** progress is stored in browser `localStorage`.
- **Explicit export only:** training packets are generated only when the player clicks export.
- **Task-derived records only:** exports capture mission outcomes, concept choices, and lightweight puzzle traces — not personal profile inference.

## Quick start

```bash
cd /home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/25-psicat-braided-brain
python3 run.py --no-open
# Open http://127.0.0.1:8025/ui/index.html
```

## Validation

```bash
cd /home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/25-psicat-braided-brain
npm run lint
npm test
python3 -m unittest tests/test_product25_structure.py
pytest tests/test_browser_contract.py -q
```

## File structure

- `ui/index.html` — main desktop/mobile game shell.
- `ui/game-core.js` — deterministic campaign and training-packet logic shared by browser and tests.
- `ui/app.js` — UI rendering, controls, export actions, and optional PsiCat coach fetch.
- `css/main.css` — responsive styling for desktop/mobile play.
- `run.py` — local static launcher on port `8025`.
- `tests/` — Node logic tests, Python structure tests, and optional Playwright browser contract.
- `SESSION_RESUME.json` — interruption-safe resume ledger.

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
