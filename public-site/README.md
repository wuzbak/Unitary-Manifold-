# Unitary Manifold — Public Site

This directory contains the **5D public-facing website** for the Unitary Manifold physics framework. It is a static site (HTML/CSS/JS) deployable on GitHub Pages without a build step.

## What This Is

A science artifact and public interface: every number shown is derived from committed code in the parent repository. The site is itself a proof of concept — demonstrating that a 5D physics framework can have a fully functional public web presence with live calculators and interactive visualizations.

## Structure

```
public-site/
├── index.html              # Main landing page — WebGL hero, stats, app grid
├── css/
│   └── main.css            # Complete design system (dark theme, all components)
├── js/
│   ├── physics-engine.js   # JS port of core Python physics modules
│   └── visualizations.js   # Three.js 5D viz, BraidViz, PentadOrbitalViz, Charts
├── apps/
│   ├── index.html                  # Apps hub
│   ├── kk-mass-calculator.html     # KK graviton mass: m_n = n·c_s·M_Pl/R
│   ├── birefringence-predictor.html # β ∈ {0.273°, 0.331°} prediction + viz
│   ├── toe-score.html              # ToE score dashboard (29.0/28)
│   ├── cmb-parameters.html         # CMB n_s / r / f_NL calculator
│   ├── desi-tracker.html           # DESI tension tracker (w₀–wₐ plane)
│   ├── lean4-progress.html         # Lean4 theorem progress dashboard
│   └── pentad-simulator.html       # 5-body Pentad orbital simulator
├── explore/
│   └── index.html          # Full-screen WebGL 5D space explorer
├── pentad/
│   └── index.html          # HILS governance interface + certification tool
├── status/
│   └── index.html          # Science artifact dashboard (sprint history, residuals)
├── about/
│   └── index.html          # About, citation, authorship, license
└── data/
    └── status.json         # Machine-readable state snapshot (CI-updatable)
```

## Deployment

### GitHub Pages

Enable Pages on the `main` branch (root or `docs/` folder). If using root, the site
is served from `public-site/` as a sub-path. For a dedicated Pages deployment point
the source to this folder directly (requires repo settings).

### Local Preview

No build step required. Open any `.html` file directly, or serve with:

```bash
python3 -m http.server 8080 --directory public-site/
# → http://localhost:8080/
```

## Technology

- **HTML5 / CSS3 / Vanilla JS** — no framework required
- **Three.js r128** (CDN) — 5D WebGL particle system
- **Chart.js 3.9.1** (CDN) — all data charts
- Physics computed in `js/physics-engine.js` which mirrors:
  - `src/core/metric.py` (KK mass ladder)
  - `src/core/pillar591_dm21_ratio_fn_correction.py` (DM21 chain)
  - `src/core/cmb_transfer.py` (CMB parameters)
  - `5-GOVERNANCE/Unitary Pentad/pentad_api.py` (Pentad simulator)

## Updating `data/status.json`

This file is the machine-readable state snapshot. Update it after every sprint or
add it to the CI pipeline to auto-update from `docs/mas_tracker.yml`:

```bash
python3 TOOLS/export_status_json.py > public-site/data/status.json
```

## Authorship

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
