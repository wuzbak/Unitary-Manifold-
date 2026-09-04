# 12-AZ-IP — Canonical AxiomZero IP Folder

All scattered AxiomZero software assets have been copied into `12-AZ-IP/` and consolidated here as the canonical software registry. The shared library at `12-AZ-IP/lib/az_ip_common/` remains in place for cross-product imports.

## Product registry (23 canonical software products / surfaces)

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
| 20 | Merlin Navigator (formerly OX Navigator) | 1.0.0 | TRL-4 | Browser + /api/merlin (+ /api/ox compatibility) | 149 | AI physics/governance navigator with identity trust policy, Sentinel do-no-harm enforcement, and compatibility shim endpoints. | [20-merlin-navigator/](20-merlin-navigator/) |
| 21 | UM Geophysical Monitor | 1.0.0 | TRL-5 | Browser / static | 121 | Live globe disaster monitor with USGS + NASA EONET feeds and UM φ-overlay (P806/P786/P16). | [21-geo-monitor/](21-geo-monitor/) |
| 22 | AxiomZero SGE | 1.0.0 | TRL-7 | http://localhost:7622 | 229 | Next-gen system security governance engine for anti-malware, zero-day detection, IDS, firewall, anti-surveillance, and governed protection workflows. | [22-az-sge/](22-az-sge/) |
| 23 | Merlin DM Guide & Player Assistant | 1.1.0 | TRL-3 | http://localhost:8033 | 17 | Offline-first Dungeons & Dragons 5e / 5.5e campaign assistant with separate DM/player dashboards, invite-code joins, character import, XP/treasure/gold/item tracking, maps, NPCs, image pushes, and Merlin expert guidance. | [23-merlin-dm-assistant/](23-merlin-dm-assistant/) |

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
- `20-merlin-navigator/` — Merlin Navigator canonical product folder (legacy OX name retained for compatibility), built from `public-site/js/19-ox-navigator.js` and expanded with identity/sentinel/runtime policy layers
- `21-geo-monitor/` — standalone product built from `src/core/pillar_geo_monitor.py` + `public-site/js/20-geo-monitor.js`
- `22-az-sge/` — standalone system security governance engine with governed protection workflows and tests
- `23-merlin-dm-assistant/` — standalone Merlin-powered D&D 5e/5.5e assistant built as an offline-first campaign, encounter, and image-brief product

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
