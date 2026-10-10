# 12-AZ-IP — Canonical AxiomZero IP Folder

All scattered AxiomZero software assets have been copied into `12-AZ-IP/` and consolidated here as the canonical software registry. The shared library at `12-AZ-IP/lib/az_ip_common/` remains in place for cross-product imports.

## Brand notice

- Rebrand label: **REBRAND-2026-09-PSICAT**
- Legal separation notice: [`BRAND_SEPARATION_NOTICE_PSICAT.md`](./BRAND_SEPARATION_NOTICE_PSICAT.md)
- Portfolio license schedule: [`PORTFOLIO_LICENSE_SCHEDULE.md`](./PORTFOLIO_LICENSE_SCHEDULE.md)
- Internal/steward-facing identity for ThomasCory remains **Merlin**.
- Canonical convergence charter: [`../9-INFRASTRUCTURE/EXECUTION_SPINE_CONVERGENCE_CHARTER.md`](../9-INFRASTRUCTURE/EXECUTION_SPINE_CONVERGENCE_CHARTER.md)
- External PsiCat submissions and unreviewed test artifacts: [`psicat-external-intake/`](./psicat-external-intake/).

## Product registry (40 canonical software products / surfaces)

| # | Product | Version | TRL | Port / Endpoint | Tests | Description | Folder |
|---|---|---:|---|---|---:|---|---|
| 01 | Axiom OS Core Suite | 1.0.0 | TRL-5 | http://localhost:8000 | 162 | Canonical merge of AxiomZero full-stack plus az-os legacy agent/φ infrastructure. | [01-axiom-os/](01-axiom-os/) |
| 02 | AZ-KERNEL Rust Kernel | 0.1.0 | TRL-3 | UEFI / QEMU | 1 | Bare-metal Rust kernel with merged fuller az-kernel tree and legacy kk_channel IPC primitive. | [02-az-kernel/](02-az-kernel/) |
| 03 | EIGE Governance Engine | 21.0.0 | TRL-7 | CLI / Docker / notebook | 449 | Deterministic election integrity and governance stack with full source, infra, schemas, and tests. | [03-eige/](03-eige/) |
| 04 | UM-SOS Scientific OS | 15.8 | TRL-6 | /api/v1/* | 1 | Seven-layer scientific operating system with backend, frontend, DAG explorer, and preregistration registry. | [04-um-sos/](04-um-sos/) |
| 05 | UOS Kernel Prototype | 0.1 | TRL-3 | Python library | 566 | Geometric OS prototype copied from the Pentad with dedicated UOS regression tests. | [05-uos-kernel/](05-uos-kernel/) |
| 06 | Omega Synthesis Engine | 20.1 | TRL-5 | Python library | 170 | Universal mechanics calculator spanning cosmology, particle physics, HILS, and falsifiers. | [06-omega-synthesis/](06-omega-synthesis/) |
| 07 | Holon Zero Engine | 1.0 | TRL-5 | Python library | 347 | Ground-state engine merged from holon-zero and holon_zero, including subpillars and repo-root tests. | [07-holon-zero/](07-holon-zero/) |
| 08 | AxiomZero Journalist AI | 1.0.0 | TRL-4 | http://localhost:8008 | 40 | AI-assisted investigative research platform: entity mapping, source classification, confidence scoring. | [08-axiom-journalist/](08-axiom-journalist/) |
| 09 | OmegaHolon Engine | 1.0.0 | TRL-4 | Python library | 60 | Combined Omega + Holon ground-state engine with unified KK tensor pipeline. | [09-omegaholon/](09-omegaholon/) |
| 10 | Filmer's Companion | 1.0.0 | TRL-3 | http://localhost:8010 | 30 | Physics-grounded creative AI tool for worldbuilding, narrative, and science communication. | [10-filmers-companion/](10-filmers-companion/) |
| 11 | Terra OS | 1.0.0 | TRL-4 | http://localhost:8011 | 45 | Earth-systems OS integrating climate, geology, and ecological UM pillars into a unified dashboard. | [11-terra-os/](11-terra-os/) |
| 12 | Lithos OS | 1.0.0 | TRL-3 | http://localhost:8012 | 35 | Lithospheric monitoring OS layer with seismic, geothermal, and mineral UM overlays. | [12-lithos-os/](12-lithos-os/) |
| 13 | Delphi | 1.0.0 | TRL-5 | http://localhost:8013 | 55 | Prediction-market and scenario-planning engine grounded in UM falsification logic. | [13-delphi/](13-delphi/) |
| 14 | SDAM | 1.0.0 | TRL-3 | Mobile / Android | 20 | Spatial Decision Awareness Module — mobile situational-awareness tool with UM φ-overlay. | [14-sdam/](14-sdam/) |
| 15 | Pentacorder | 1.0.0 | TRL-3 | Mobile / Android | 25 | Physics measurement companion for Android: spectral analysis, winding-mode detector. | [15-pentacorder/](15-pentacorder/) |
| 16 | AxiomZero Ω Oracle | 1.0.0 | TRL-4 | http://localhost:7872 | 83 | Capstone synthesis engine: Pentad modelling, Omega score, epistemic audit, falsifiable commitments. | [16-oracle/](16-oracle/) |
| 17 | UM Physics Image Generator | 1.0.0 | TRL-5 | Browser / static | 113 | Canvas 2D browser tool generating PNG visualizations for 8 UM physics concepts. | [17-um-image-generator/](17-um-image-generator/) |
| 18 | UM Reader / Educator | 1.0.0 | TRL-5 | Browser / static | 90 | 302-entry reading & TTS platform for the UM framework — offline, KaTeX, 9 categories. | [18-um-reader/](18-um-reader/) |
| 19 | Falsification Observatory | 1.0.0 | TRL-5 | Browser / static | 112 | Live tracker for 7 experiments testing UM predictions — PASS / TENSION / FALSIFIED verdicts. | [19-falsification-observatory/](19-falsification-observatory/) |
| 20 | PsiCat Navigator (formerly Merlin Navigator) | 1.0.0 | TRL-4 | Browser + /api/psicat (+ /api/ox compatibility) | 149 | AI physics/governance navigator and canonical execution/control plane with identity trust policy, Sentinel do-no-harm enforcement, and compatibility shim endpoints. | [20-psicat-navigator/](20-psicat-navigator/) |
| 21 | UM Geophysical Monitor | 1.0.0 | TRL-5 | Browser / static | 121 | Live globe disaster monitor with USGS + NASA EONET feeds and UM φ-overlay (P806/P786/P16). | [21-geo-monitor/](21-geo-monitor/) |
| 22 | AxiomZero SGE | 1.0.0 | TRL-7 | http://localhost:7622 | 229 | Next-gen system security governance engine for anti-malware, zero-day detection, IDS, firewall, anti-surveillance, and governed protection workflows. | [22-az-sge/](22-az-sge/) |
| 23 | PsiCat DM Guide & Player Assistant | 1.1.0 | TRL-3 | http://localhost:8033 | 17 | Offline-first Dungeons & Dragons 5e / 5.5e campaign assistant with separate DM/player dashboards, invite-code joins, character import, XP/treasure/gold/item tracking, maps, NPCs, image pushes, and PsiCat expert guidance. | [23-psicat-dm-assistant/](23-psicat-dm-assistant/) |
| 24 | PsiCat Web Browser | 1.0.0 | TRL-3 | Electron / Android / Extension | 15 | Chromium-based next-gen browser foundation with Electron desktop, native-tab Android shell, split-workspace desktop scaffolding, embedded PsiCat research sidebar, local sync backend scaffold, Playwright-first browser proving ground, notebook, sync packet workflows, and import/export. | [24-psicat-web-browser/](24-psicat-web-browser/) |
| 25 | PsiCat Braided Brain | 1.1.0 | TRL-3 | Browser / PWA | 25 | Toroidal brain simulator game for desktop and mobile with science missions, local training-packet export, and optional PsiCat coaching through Product 20. | [25-psicat-braided-brain/](25-psicat-braided-brain/) |
| 26 | UM-ARTS | 1.0.0 | Not assessed | CLI / local browser | Focused pytest suites | Evidence-first regression application: supervised execution, immutable receipts, compatible resume, inventory, and bounded assistance; no scientific claim promotion. | [26-um-arts/](26-um-arts/) |
| 27 | PsiCat's Vite Web Workbench | 1.0.0 | Not assessed | http://127.0.0.1:8327 | 10 targeted tests | Standalone loopback-only Vite project workbench with curated starters and native Product 20 tools; project configs/plugins are not loaded and arbitrary commands are not run. | [27-psicat-vite-web-workbench/](27-psicat-vite-web-workbench/) |
| 28 | AZ Calorimetry Console | 1.1.0 | TRL-2 | CLI / Python library + web | 15 | Cold-fusion run-sheet generator and COP tracker wrapping `src/physics/lattice_dynamics.py` and `src/cold_fusion/`. | [28-az-calorimetry-console/](28-az-calorimetry-console/) |
| 29 | AZ Polariton Vortex Analyzer | 1.1.0 | TRL-2 | CLI / Python library + web | 10 | Pump-probe vortex feature extraction and comparison against `src/materials/polariton_vortex.py` predictions. | [29-az-polariton-vortex-analyzer/](29-az-polariton-vortex-analyzer/) |
| 30 | AZ Materials Screening Engine | 1.1.0 | TRL-2 | CLI / Python library + web | 12 | Candidate-material screening and ranking against the canonical UM Fröhlich-polaron/metamaterial formulas. | [30-az-materials-screening-engine/](30-az-materials-screening-engine/) |
| 31 | AZ Braided Qubit Ansatz Studio | 1.1.0 | TRL-2 | CLI / Python library + web | 13 | Hardware-portable gate-list export and independent re-simulation of `src/quantum/kk_vqe.py`'s ansatz. | [31-az-braided-qubit-ansatz-studio/](31-az-braided-qubit-ansatz-studio/) |
| 32 | AZ Phi-Debt Early Warning Library | 1.1.0 | TRL-3 | CLI / Python library + web | 15 | Domain-agnostic capacity/discharge/debt monitor generalized from `recycling/entropy_ledger.py`. | [32-az-phi-debt-early-warning/](32-az-phi-debt-early-warning/) |
| 33 | AZ Accessibility Pipeline | 1.1.0 | TRL-2 | CLI / Python library + web | 13 | Reading-segment, visual-concept, and falsifiable-claim routing pipeline reusing Products 17 and 19. | [33-az-accessibility-pipeline/](33-az-accessibility-pipeline/) |
| 34 | AZ Domain Experts Pack | 1.1.0 | TRL-3 | CLI / Python library + web | 15 | AST-based domain-expert retrieval over `src/materials/` and `src/atomic_structure/`. | [34-az-domain-experts-pack/](34-az-domain-experts-pack/) |
| 35 | AZ UOS/AZ-KERNEL Bridge | 1.1.0 | TRL-2 | CLI / Python library + web | 14 | Interface contract plus winding-aware IPC addressing scheme, cross-checked against the real `kk_channel.rs`. | [35-az-uos-kernel-bridge/](35-az-uos-kernel-bridge/) |
| 36 | AZ Differentiable Cosmology Slider | 1.1.0 | TRL-4 | CLI / Python library + web | 14 | Real-time (n_s, gradient) slider API wrapping `src/core/jax_backend.grad_spectral_index`. | [36-az-cosmology-slider/](36-az-cosmology-slider/) |
| 37 | AZ Holographic Condensed-Matter Comparator | 1.1.0 | TRL-3 | CLI / Python library + web | 14 | Compares `src/holography/dual_cft_spectrum.py` KK-tower operator dimensions against illustrative literature benchmarks. | [37-az-holographic-condensed-matter-comparator/](37-az-holographic-condensed-matter-comparator/) |
| 38 | AZ Formal Verification Library | 1.1.0 | TRL-4 | CLI / Python library + web | 16 | Generic Z3 safety-property template generalized from `src/core/z3_pentad_checker.py`. | [38-az-formal-verification-library/](38-az-formal-verification-library/) |
| 39 | AZ Research-Debt Tracker | 1.1.0 | TRL-4 | CLI / Python library + web | 19 | Domain-agnostic project-health tracker generalized from `src/meta/mas_wave_engine.py`, dogfooded against UM's own live gap list. | [39-az-research-debt-tracker/](39-az-research-debt-tracker/) |
| 40 | AZ Live-Data Harness | 1.1.0 | TRL-4 | CLI / Python library + web | 13 | Shared fetch/normalize/fallback/verdict harness demonstrated against `src/data/fetch_planck.py`. | [40-az-live-data-harness/](40-az-live-data-harness/) |

*Sub-surfaces and shared infrastructure (part of Product 01):*

| Surface | Port | Tests | Folder |
|---|---|---:|---|
| AxiomZero REST API | http://localhost:8000/api | 162 inh. | [01-axiom-os/api/](01-axiom-os/api/) |
| AxiomZero Android Client | Thin client → API | 162 inh. | [01-axiom-os/android/](01-axiom-os/android/) |
| AxiomZero Web Dashboard | http://localhost:8000 | 162 inh. | [01-axiom-os/ui/](01-axiom-os/ui/) |
| AxiomZero MCP Stack | Filesystem / execution / browser MCP | 162 inh. | [01-axiom-os/mcp/](01-axiom-os/mcp/) |
| AxiomZero Memory Stack | SQLite / vector store | 162 inh. | [01-axiom-os/memory/](01-axiom-os/memory/) |
| UM-SOS Frontend & Graph | Static frontend / GitHub Pages | 1 inh. | [04-um-sos/frontend/](04-um-sos/frontend/) |
| AZ IP Common Library | Python import | shared | [lib/az_ip_common/](lib/az_ip_common/) |
| IP & Products Catalog | Registry docs | — | [tools/](tools/) |

## Canonical consolidated folders

- `01-axiom-os/` — merged `AxiomZero/` + `az-os/`
- `02-az-kernel/` — merged `az-kernel/` + `11-AZ-OS/ax-kernel/`
- `03-eige/` — copied from `EIGE/`
- `04-um-sos/` — copied from `10-UM-SOS/`
- `05-uos-kernel/` — copied from Pentad `UOS/` plus UOS tests
- `06-omega-synthesis/` — copied from Pentad `omega/`
- `07-holon-zero/` — merged `holon-zero/` + `holon_zero/` plus root Holon tests
- `17-um-image-generator/` — standalone product built from `public-site/js/um-image-generator.js`
- `18-um-reader/` — standalone product built from `public-site/js/um-reader.js`
- `19-falsification-observatory/` — standalone product built from `public-site/js/17-falsification-observatory.js`
- `20-psicat-navigator/` — PsiCat Navigator canonical product folder (legacy OX name retained for compatibility), built from `public-site/js/19-ox-navigator.js` and expanded with identity/sentinel/runtime policy layers
- `21-geo-monitor/` — standalone product built from `src/core/pillar_geo_monitor.py` + `public-site/js/20-geo-monitor.js`
- `22-az-sge/` — standalone system security governance engine with governed protection workflows and tests
- `23-psicat-dm-assistant/` — standalone PsiCat-powered D&D 5e/5.5e assistant built as an offline-first campaign, encounter, and image-brief product
- `24-psicat-web-browser/` — advanced Chromium-based PsiCat browser product with Electron desktop, split-workspace scaffolding, native-tab Android shell, local sync backend scaffold, Playwright-first testing, and Chrome/Edge extension companion
- `25-psicat-braided-brain/` — responsive toroidal brain simulator game with PsiCat/PhiCat teaching loops, voluntary training-packet export, and optional Product 20 coaching
- `26-um-arts/` — canonical UM-ARTS regression application and Python package; `TOOLS.um_arts` retains backwards-compatible CLI, submodule, and pytest-plugin imports
- `27-psicat-vite-web-workbench/` — standalone local Vite app with curated frontend starters and human-gated native Product 20 actions
- `28-az-calorimetry-console/` through `40-az-live-data-harness/` — thirteen new standalone products (direct Python packages, not merges of pre-existing folders), each built against one of the thirteen "Phase 0/1 buildable now" directions named in `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-the-untouched-manifold-what-this-monorepo-could-still-become.md`; see each product's own README "Epistemic status" section for exactly which article phase is and is not implemented

## Product 26 operational entrypoints

UM-ARTS is regression infrastructure, not a physics pillar or a scientific
certificate; technology readiness has not been assessed. Its canonical product
description lives in `IP_REGISTRY.json`. Full operational documentation is in the
existing [`../TOOLS/README.md`](../TOOLS/README.md#um-arts--regression-evidence-application).

From the repository root:

```bash
python 12-AZ-IP/26-um-arts/run.py --help
python 12-AZ-IP/26-um-arts/run.py serve \
  --root "$PWD" --store "$PWD/.um-arts" --host 127.0.0.1 --port 8765
```

The application is loopback-only. `inventory` discovers review-required
repository-wide candidates; `assist` retrieves bounded cited context without
changing evidence gates. `snapshot` explicitly copies source but never waives
frozen-input checks. `certify --manifest PATH` only reconciles the explicit,
disclosed compatible checks in a manifest, not an automatic full-repository
badge. Python, exporter, scoped Lean, and full formal-library outcomes remain
separate. Existing legacy module/CLI/plugin imports stay supported.
Execution/recovery supports Python 3.12+ on Linux/macOS using Unix `fcntl` and
POSIX process groups, not native Windows. Product release 1.0.0 is distinct from
the preserved evidence schema `VERSION = "1"` displayed by legacy CLI version output.

## Product 27 operational entrypoints

Product 27 requires Node.js `^20.19.0 || >=22.12.0`. Install its pinned
dependencies, build the Workbench dashboard, configure a local token, and start
the loopback service:

```bash
cd 12-AZ-IP/27-psicat-vite-web-workbench
npm install && npm run build
export PSICAT_VITE_WORKBENCH_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
npm start
```

Open `http://127.0.0.1:8327/` in Product 24 or another browser. To expose the
native PsiCat tools, set `PSICAT_VITE_WORKBENCH_URL` and the same token in
Product 20's environment before launching it. Project creation, preview
lifecycle, and builds require explicit tool approval. The service is a local
developer workbench, not an OS sandbox; only preview code you trust.

## Shared assets retained

- `LICENSE-AGPL`
- `NOTICE`
- `IP_REGISTRY.json`
- `FINGERPRINT_MANIFEST.md`
- `lib/az_ip_common/`
- `tools/`
- `engines/`
- `calculators/`

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
