# AxiomZero IP: 21 Products, One Physics Framework

**Product Announcement · 2026-08-26**

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*

---

Everything in AxiomZero derives from one equation. The 5-dimensional Kaluza-Klein
metric ansatz that underpins the Unitary Manifold is not decorative — it is
*operational*. Every product listed below is a direct application of that framework:
its constants, its geometry, its falsifiable predictions, or its governance philosophy.

At publication time, this post cataloged 21 canonical AxiomZero IP products in the `12-AZ-IP/` registry.
Each entry describes what the product is, where it sits on the Technology Readiness Level
(TRL) scale, its intended use, and the broader space of applications it can address.

---

## How to Read TRL Ratings

| TRL | Meaning |
|-----|---------|
| TRL-3 | Proof of concept; core algorithms working |
| TRL-4 | Lab prototype; functional in controlled setting |
| TRL-5 | Validated in relevant environment; deployable for research or enthusiast use |
| TRL-6 | Demonstrated in operational environment |
| TRL-7 | System prototype demonstrated in operational environment |

All TRL ratings are honest assessments. No product claims production readiness it hasn't earned.

---

## Product 01 — Axiom OS Core Suite

**Version:** 1.0.0 | **TRL:** 5 | **Tests:** 162 passing

### What It Is

AxiomZero is a persistent AI cognitive layer that runs *on top of any existing operating
system*. It is not a kernel replacement — it is an enrichment layer, the same way
Kaluza-Klein extra dimensions enrich 4D spacetime without abolishing it.

The architecture is a **7-manager × 5-sub-agent** network. The number 7 comes from the
braided winding pairs in the 5D geometry. The 5 sub-agents per manager mirror the winding
number n_w = 5. These numbers are not configuration choices; they are physics derivations.

The suite includes:
- **REST API** (FastAPI, localhost:8000) — query the Unitary Manifold programmatically
- **Web Dashboard** — browser-based status, pillar explorer, and query interface
- **Android Thin Client** — routes to the local or remote API
- **MCP Stack** — filesystem, execution, and browser Model Context Protocol tools
- **Memory Stack** — SQLite + vector store for persistent session state

### Intended Use

A developer or researcher who wants a physics-grounded AI assistant that
maintains context across sessions, can answer questions about the Unitary Manifold
framework, and orchestrates multi-agent reasoning tasks.

### Other Applications

- Edge AI nodes where the cognitive layer must survive reboots (idempotent bootstrap)
- Research groups integrating a common epistemic framework across team members
- Thin-client science communication terminals (Android or Raspberry Pi)
- Any project needing a multi-agent orchestration system with auditable provenance

---

## Product 02 — AZ-KERNEL Rust Kernel

**Version:** 0.1.0 | **TRL:** 3 | **Tests:** 1 (build-smoke)

### What It Is

A bare-metal Rust kernel targeting x86-64 and ARM64, bootable via UEFI or
QEMU. Every primitive is a direct translation of Unitary Manifold constants:

| Physics constant | Kernel primitive |
|-----------------|-----------------|
| 5 KK extra dimensions | 5 privilege rings |
| n_w = 5 | 5 interrupt priority levels |
| k_cs = 74 = 5² + 7² | 74 pages per compactification domain |
| Geodesic equations | CPU scheduler (process = point in metric space) |
| φ-debt entropy (Pillar 16) | Memory reclamation and filesystem eviction |
| Holographic boundary (Pillar 4) | IPC channel interface |
| πkR = 37 | Radion stability → kernel watchdog timeout |

Includes a unique legacy IPC primitive, `kk_channel.rs`, derived from the Kaluza-Klein
channel model.

### Intended Use

Research into physics-principled OS design. Demonstrates that OS architecture can be
derived from a geometric physics framework rather than accumulated engineering convention.
Boot it in QEMU; inspect the scheduler; compare the constants.

### Other Applications

- Educational platform for OS courses exploring first-principles architecture
- Embedded systems research where a provably minimal privilege model is required
- Foundation for a formally verified microkernel (Lean4 proofs are a natural next step)
- Exploration of non-UNIX OS design paradigms

---

## Product 03 — EIGE Governance Engine

**Version:** 21.0.0 | **TRL:** 7 | **Tests:** 449 passing

### What It Is

EIGE (Election Integrity Governance Engine) is a **deterministic, mathematically
verifiable chain-of-custody engine for elections**. It is the most operationally
mature product in the registry.

EIGE provides:
- Cryptographic ballot chain-of-custody (SHA-256 at every step)
- Deterministic vote tabulation with full audit trail
- Precinct-level reconciliation and anomaly detection
- Docker-deployable infrastructure, CLI interface, Jupyter notebook integration
- JSON schema validation for ballot data interchange

The epistemic label is 🔵 ADJACENT TRACK — this is a governance application of the
Unitary Manifold's φ-equity and entropy-accounting philosophy. It does not depend on
the physics being correct; it depends on the *methodology* being rigorous.

### Intended Use

Election administrators, civic technologists, and election integrity auditors who need
a transparent, reproducible tabulation system with a full cryptographic paper trail.

### Other Applications

- Corporate board elections and proxy voting with auditability requirements
- Academic conference paper ranking and selection (transparent, reproducible scoring)
- Community governance for DAOs and open-source projects
- Any decision process where chain-of-custody integrity is legally or ethically required

---

## Product 04 — UM-SOS Scientific Operating System

**Version:** 15.8 | **TRL:** 6 | **Tests:** 1 (API smoke; full suite via core tests)

### What It Is

UM-SOS is a **seven-layer scientific operating system** for the Unitary Manifold
research program. Think of it as mission control for an ongoing physics investigation.

The seven layers:
1. **Prediction API** — query any UM prediction by pillar number
2. **Experimental monitor** — live status of DESI, LiteBIRD, JUNO, ACT, and other experiments
3. **Derivation graph** — DAG (directed acyclic graph) of all pillar dependencies
4. **Preregistration registry** — immutable log of predictions made before experimental results
5. **Frontend explorer** — browser dashboard for the full derivation chain
6. **Governance-integrated AI query** — epistemic labels and governance lane classification
7. **Gap tracker** — open problems with honest status codes

### Intended Use

Researchers following or collaborating on the Unitary Manifold project — tracking
which predictions are open, which are confirmed, and which are in tension with data.

### Other Applications

- Template for any long-running theoretical research program that wants rigorous
  preregistration and falsification tracking
- Science communication: embedding live prediction dashboards in publications
- Reproducibility infrastructure for computational physics projects
- Research group coordination: shared epistemic status across collaborators

---

## Product 05 — UOS Kernel Prototype

**Version:** 0.1 | **TRL:** 3 | **Tests:** 566 passing

### What It Is

UOS (Unitary Operating System) is a **research-grade Python kernel layer** exploring
what it would mean to build an OS from 5-dimensional Kaluza-Klein geometry. Where
AZ-KERNEL (Product 02) is the bare-metal Rust implementation, UOS is the high-fidelity
Python simulation of the same architecture — faster to iterate on, easier to test, and
directly integrated with the Unitary Manifold test suite.

Key components:
- Geometric process scheduler (processes as geodesics)
- φ-debt memory manager
- Holographic IPC boundary
- Pentad security descriptor system
- 566 regression tests covering all kernel primitives

### Intended Use

OS research and education. UOS is the "flight simulator" for AZ-KERNEL: explore the
architecture, validate assumptions, and stress-test the physics-to-OS mapping before
committing to Rust.

### Other Applications

- Graduate OS courses where students explore non-UNIX design from first principles
- Formal verification research: UOS's Python layer is easier to annotate for Lean4 proofs
- Agent-based simulation of distributed systems modeled as KK compactification domains

---

## Product 06 — Omega Synthesis Engine

**Version:** 20.1 | **TRL:** 5 | **Tests:** 170 passing

### What It Is

The Omega Synthesis Engine is the **universal mechanics calculator** of the Unitary
Manifold. It is a Python library spanning:

- Cosmology: CMB spectral index, tensor-to-scalar ratio, dark energy EoS
- Particle physics: Standard Model parameters from KK geometry
- HILS governance: Human-in-the-Loop Systems metrics
- Falsification scoring: confidence levels for each experimental test

It is designated Pillar Ω — the omega point where all derivation chains converge.

### Intended Use

Researchers who want a single, coherent Python API for all Unitary Manifold
numerical predictions. Import `omega_synthesis` and compute any parameter from the
framework's constants.

### Other Applications

- Science education: interactive notebooks demonstrating how one geometry produces
  predictions across cosmology, particle physics, and complex systems
- Cross-domain numerical exploration: apply the same constants to new domains
- Baseline for new adjacent tracks (Pillars 218+)

---

## Product 07 — Holon Zero Engine

**Version:** 1.0 | **TRL:** 5 | **Tests:** 347 passing

### What It Is

Holon Zero is the **ground-state engine** of the Unitary Manifold — the mathematical
description of the lowest-energy configuration of the 5D compactification. It is both
the physical starting point of the framework and a practical Python library for:

- Computing the ground-state metric configuration
- Evaluating Ω₀ (the Holon Zero operator) and its sub-pillars (70-B, 70-C, 70-D)
- Deriving the braided winding numbers from first principles
- Stability analysis of the compactification

### Intended Use

Core physics computation within the Unitary Manifold. Holon Zero is called by most
other products as a dependency. Researchers studying the ground-state geometry use
it directly.

### Other Applications

- Quantum chemistry analogy: ground-state solvers in condensed matter
- Stability analysis tools for other compactification frameworks
- Educational: the clearest entry point into the Unitary Manifold mathematics

---

## Product 08 — AxiomZero Journalist AI

**Version:** 1.0.0 | **TRL:** 4 | **Tests:** 40 passing

### What It Is

AXIOM is an **AI-assisted investigative research platform**. Built on Gradio, it
provides:

- **Entity mapping** — extract and link people, organizations, and documents from
  uploaded source material
- **Source classification** — epistemic confidence scoring for primary, secondary,
  and tertiary sources
- **Confidence scoring** — every claim receives a verifiable confidence rating
- **Document-first methodology** — the document is the primary reality; AI assists
  rather than substitutes

The platform applies the same epistemic rigor as the Unitary Manifold's falsification
framework — every claim is labeled with its confidence level and the evidence supporting it.

### Intended Use

Investigative journalists, researchers, and fact-checkers who need to organize large
document sets, track entity relationships, and maintain clear epistemic provenance for
every claim.

### Other Applications

- Legal discovery: organizing and classifying large document productions
- Academic literature review: mapping citation networks and claim provenance
- Due diligence in M&A or investment research
- Whistleblower and public interest investigations with source protection requirements

---

## Product 09 — OmegaHolon Engine

**Version:** 1.0.0 | **TRL:** 4 | **Tests:** 60 passing

### What It Is

OmegaHolon is the **integration of the Omega Synthesis (Product 06) and Holon Zero
(Product 07) engines** into a unified KK tensor pipeline. It is a Gradio application
with SQLite persistence that allows users to:

- Compute the full KK tensor from ground-state initial conditions
- Trace a derivation from Holon Zero through the Omega synthesis to any prediction
- Store and retrieve session results for longitudinal comparison
- Visualize how the ground-state geometry propagates through the derivation chain

It is the most unified single-interface view of the framework's mathematics.

### Intended Use

Researchers who want to explore the *end-to-end* derivation pipeline interactively,
from ground state to observable prediction, in a single application.

### Other Applications

- Physics teaching: step-by-step walkthrough of a complete physical derivation
- Sensitivity analysis: vary initial conditions, observe prediction impact
- Cross-framework comparison: benchmark against other KK models

---

## Product 10 — Filmer's Companion

**Version:** 1.0.0 | **TRL:** 3 | **Tests:** 30 passing

### What It Is

Filmer's Companion is a **physics-grounded creative AI tool** for independent
filmmakers. It provides a multi-agent suite covering:

- **Cinematography assistant** — lens selection, depth of field, lighting ratios
  grounded in optical physics
- **Location scout** — geographic and environmental analysis tools
- **Production finance** — budget modeling and cash-flow projection
- **Assistant Director tools** — scheduling, call sheets, and crew logistics

The "physics-grounded" framing means recommendations are derived from first principles
where possible (e.g., diffraction limits for lens selection) rather than pure heuristics.

### Intended Use

Independent filmmakers and small production companies who want a unified AI assistant
that covers the full production workflow with honest, physics-informed reasoning.

### Other Applications

- Documentary production: location analysis using geographic and environmental data
- Film school curriculum: teaching production finance and cinematography physics
- Virtual production: physics-based camera simulation for pre-visualization
- Science communication films: ensuring physical accuracy in visual storytelling

---

## Product 11 — Terra OS

**Version:** 1.0.0 | **TRL:** 4 | **Tests:** 45 passing

### What It Is

Terra OS is a **soil and water expert system** — a FastAPI-based RAG (Retrieval
Augmented Generation) application integrating:

- Soil science: composition analysis, remediation recommendations, nutrient cycling
- Water quality: contamination detection, treatment protocols, watershed modeling
- Land remediation: pollution recovery pathways grounded in geochemistry
- UM pillar integration: Pillars 21 (ecology), 22 (climate), 23 (marine) provide
  the physics overlay

The "OS" framing means it operates as a unified decision-support layer across these
Earth-systems domains rather than a single-purpose tool.

### Intended Use

Environmental scientists, land managers, and remediation engineers who need integrated
decision support across soil, water, and ecosystem domains with a physics-grounded
analytical layer.

### Other Applications

- Agricultural advisory: soil health recommendations for farm management
- Environmental impact assessment: integrated ecosystem modeling
- Climate adaptation planning: land use and water resource management under changing conditions
- Regulatory compliance: documenting remediation pathways with scientific provenance

---

## Product 12 — Lithos OS

**Version:** 1.0.0 | **TRL:** 3 | **Tests:** 35 passing

### What It Is

Lithos OS is a **mineral and gemstone identifier** — a Gradio desktop application
that uses computer vision and a structured mineralogy knowledge base to:

- Identify minerals and gemstones from images
- Provide crystallographic data (crystal system, hardness, cleavage, luster)
- Map mineral properties to underlying UM geometry (lattice dynamics, phonon modes)
- Estimate geological provenance and formation conditions

The UM overlay connects mineralogy to the framework's materials science pillars
(Pillar 26) and phonon-radion bridge (Pillar 15-B).

### Intended Use

Geologists, gemologists, collectors, and students who want an identification tool
that explains the *physics* of what they're looking at, not just a classification label.

### Other Applications

- Mining and exploration: rapid field identification with provenance estimation
- Museum and collection cataloging: structured mineralogical data with crystallographic detail
- Education: teaching crystallography and materials science through real specimens
- Jewelry appraisal: gemological identification with quality and origin indicators

---

## Product 13 — Delphi

**Version:** 1.0.0 | **TRL:** 5 | **Tests:** 55 passing

### What It Is

Delphi is a **five-oracle divination suite** — and also a serious demonstration of
how structured symbolic reasoning can produce useful probabilistic framing even in
domains traditionally considered non-scientific.

The five oracles:
1. **Tarot** — 78-card deck, φ²-weighted Major Arcana, Celtic Cross / Three-Card / Single Card layouts
2. **Runes** — 24 Elder Futhark runes, single / three-rune / runic cross spreads
3. **Astrology** — Western sun/moon/rising calculation, daily horoscopes
4. **Chinese Zodiac** — 12 animals, five elements, compatibility analysis
5. **I-Ching** — 64 hexagrams, yarrow stalk and coin methods

The Delphi project makes no empirical claims about the predictive validity of
divination systems. It is an exploration of symbolic coherence, narrative structure,
and the human need for meaning-making frameworks. The φ-weighting of the Major
Arcana is an aesthetic and structural choice, not a physics claim.

### Intended Use

Creative writers, designers, and practitioners of contemplative traditions who want
a rigorous, well-implemented digital tool for exploring these symbol systems.

### Other Applications

- Narrative design: generating plot seeds and character archetypes for fiction
- Therapeutic reflection: structured journaling prompts (not clinical advice)
- Game design: symbolic systems for worldbuilding and procedural narrative
- Cultural and anthropological study of divination traditions

---

## Product 14 — SDAM (Software-Defined Acoustic Modem)

**Version:** 1.0.0 | **TRL:** 3 | **Tests:** 20 passing

### What It Is

SDAM turns every Android device into a **hardware-independent, RF-invisible acoustic
modem**. The speaker and microphone are the antenna. Sound is the carrier. No radio
hardware. No FCC license required. No infrastructure dependency.

At the physical layer it is a **frequency-shift keyed (FSK) digital radio**:
- Data rates: 300 – 2400 baud (configurable)
- Range: 1 – 50 meters (line-of-sight, acoustic)
- Encoding: FSK with error-correcting codes
- Platform: Native Android (Java/Kotlin), API 26+

The UM connection: the FSK frequency pairs are derived from the framework's
braid resonance frequencies, creating a system whose carrier design has a
physics rationale rather than arbitrary engineering convention.

### Intended Use

Emergency communication scenarios where RF infrastructure is unavailable or
compromised, and device-to-device local-area data exchange is needed.

### Other Applications

- Disaster response: mesh communication without cellular infrastructure
- Secure local communication: no RF emissions, no interception by standard RF scanners
- IoT device provisioning: acoustic configuration channel for devices without WiFi UI
- Accessibility: audio data transfer for environments where visual/RF channels are restricted
- Research: studying acoustic channel physics and FSK modulation performance on consumer hardware

---

## Product 15 — Pentacorder

**Version:** 1.0.0 | **TRL:** 3 | **Tests:** 25 passing

### What It Is

Pentacorder is a **physics measurement companion** for Android. It is named for
the winding number n_w = 5 that anchors the Unitary Manifold framework. Its
measurement tools include:

- **Spectral analyzer** — real-time FFT of microphone input, frequency identification
- **Winding-mode detector** — pattern recognition for the five KK resonance modes
  in acoustic and electromagnetic signals
- **Magnetic field mapper** — compass + magnetometer visualization
- **Gravitational anomaly logger** — accelerometer-based micro-g logging
- **Environmental sensor dashboard** — temperature, pressure, humidity (where available)

The "winding-mode detector" is the most distinctive feature: it applies the KK
frequency-spacing predictions to real sensor data and flags candidate resonance
patterns. This is a research tool, not a confirmed physics detector.

### Intended Use

Physics students, citizen scientists, and Unitary Manifold researchers who want a
mobile measurement suite that integrates directly with the framework's predictions.

### Other Applications

- Field data collection for acoustic and electromagnetic experiments
- Educational physics labs: smartphone-based spectral analysis and wave physics
- Environmental monitoring: portable multi-sensor logging for research fieldwork
- Science outreach: real-time physics demonstrations using everyday devices

---

## Product 16 — AxiomZero Ω Oracle

**Version:** 1.0.0 | **TRL:** 4 | **Tests:** 83 passing

### What It Is

The Ω Oracle is the **capstone synthesis engine** of the AxiomZero product family.
It is the instrument that asks: *"Given the full state of the Unitary Manifold —
its pillars, its gaps, its experimental tensions — what is the honest epistemic
status of the framework?"*

Capabilities:
- **Pentad modelling** — applies the Unitary Pentad governance framework to any system
- **Omega score** — a structured epistemic confidence metric (not a "ToE score"; this is
  an honest uncertainty quantification, not a brag)
- **Epistemic audit** — identifies overclaims, underclaims, and architectural gaps
- **Falsifiable commitments** — generates machine-readable preregistration records
- **φ_trust threshold analysis** — below what confidence level does a system lose coherence?

### Intended Use

Researchers, reviewers, and collaborators who want a rigorous, automated epistemic
audit of the Unitary Manifold or any other theoretical framework using the same
methodology.

### Other Applications

- AI safety: epistemic audit tools for large language models and AI systems
- Regulatory science: confidence quantification for novel therapeutic claims
- Policy analysis: structured uncertainty accounting for evidence-based decisions
- Scientific peer review support: automated claim classification and gap identification

---

## Product 17 — UM Physics Image Generator

**Version:** 1.0.0 | **TRL:** 5 | **Tests:** 113 passing

### What It Is

The UM Image Generator is a **Canvas 2D browser tool** that generates publication-quality
PNG visualizations of eight core Unitary Manifold physics concepts:

1. The 5D KK metric structure
2. The braided winding lattice (n_w = 5, k_cs = 74)
3. The CMB transfer function and spectral index
4. The φ-debt recycling cycle (Pillar 16)
5. The Holon Zero ground-state geometry
6. The Standard Model parameter derivation cascade
7. The falsification boundary map
8. The Omega synthesis convergence diagram

All images are generated client-side (no server, no data transmission) and export
as high-resolution PNG files suitable for papers, presentations, and publications.

### Intended Use

Researchers and science communicators who need accurate, reproducible visualizations
of the Unitary Manifold framework for papers, talks, and articles.

### Other Applications

- Physics education: auto-generated diagrams for KK compactification lectures
- Science journalism: accurate visualizations for physics reporting
- Open access publishing: no-cost, no-dependency figure generation
- Presentation design: consistent visual language across all UM communications

---

## Product 18 — UM Reader / Educator

**Version:** 1.0.0 | **TRL:** 5 | **Tests:** 90 passing (59 core, 90 with reader-specific)

### What It Is

The UM Reader is a **302-entry reading and text-to-speech platform** for the entire
Unitary Manifold framework. It operates fully offline in the browser and includes:

- **302 entries**: 300 Substack posts + 2 books (the full monograph and the technical companion)
- **9 topic categories**: Core Physics, Mathematics, Cosmology, Particle Physics,
  Applications, Philosophy, Governance, Outreach, Adjacent Tracks
- **Text-to-speech**: Web Speech API at 0.95× rate, 1.05× pitch — optimized for
  technical content listening
- **KaTeX math rendering**: equations display correctly in-browser, offline
- **No server required**: fully static, works on any device with a modern browser

### Intended Use

Readers who want to engage with the Unitary Manifold framework in depth — linearly
through the post sequence, or by topic — with the option to listen rather than read.

### Other Applications

- Accessibility: TTS for readers with visual impairments or reading difficulties
- Long-form audio science content: commute-length physics deep-dives
- Educational curriculum: structured reading list with category organization
- Archive and reference: complete framework documentation in a single offline tool

---

## Product 19 — Falsification Observatory

**Version:** 1.0.0 | **TRL:** 5 | **Tests:** 112 passing

### What It Is

The Falsification Observatory is a **live tracker for every experiment currently
testing the Unitary Manifold's predictions**. It is the most epistemically important
product in the registry — because a framework that cannot be falsified is not science.

Seven experiments tracked:
1. **LiteBIRD** (CMB birefringence β, launch ~2032) — *primary falsifier*
2. **DESI DR3** (dark energy EoS wₐ)
3. **JUNO** (neutrino mass ordering)
4. **ACT DR6** (CMB power spectrum)
5. **HL-LHC** (proton decay rate)
6. **nEDM** (neutron electric dipole moment)
7. **XENON-nT** (dark matter direct detection)

Each experiment shows: current status (OPEN / TENSION / PASS / FALSIFIED), the
specific UM prediction being tested, the threshold that would trigger falsification,
and the expected result date.

The Pillar 787 oracle provides machine-readable falsification verdicts for integration
with other tools.

### Intended Use

Anyone following the Unitary Manifold who wants to know, at a glance, whether any
experiment has returned a result that challenges or confirms the framework.

### Other Applications

- Science journalism: real-time dashboard for physics experiments with clear verdict criteria
- Physics education: teaching falsificationism with a live, real-world example
- Research group coordination: shared experiment monitoring across distributed teams
- Template for any theoretical framework wanting honest, public falsification tracking

---

## Product 20 — OX Navigator

**Version:** 1.0.0 | **TRL:** 4 | **Tests:** 149 passing

### What It Is

OX Navigator is an **AI physics navigator** powered by `stealth/ox-alpha` via
OpenRouter. It provides:

- **Physics Q&A**: query the full Unitary Manifold framework in natural language
- **Gate-badge extraction**: identifies which pillar and epistemic gate applies to
  any answer (HARDGATE / ADJACENT TRACK / OPEN)
- **Session history**: persistent conversation log with pillar citations
- **Interrogator sub-tool**: 20-KB structured knowledge base for challenge questions
- **Flashcard sub-tool**: spaced-repetition review of key framework concepts

The OX (Oracle X) model is accessed via OpenRouter; the OPENROUTER_API_KEY
environment variable is the only external dependency.

### Intended Use

Researchers, students, and curious readers who want to explore the Unitary Manifold
interactively, get direct answers to physics questions, and receive properly labeled
epistemic context for every response.

### Other Applications

- Physics tutoring: AI tutor grounded in a specific theoretical framework
- Research onboarding: new collaborators get up to speed through conversation
- Peer review preparation: challenge the framework with hard questions, get labeled responses
- Science communication: journalists and communicators accessing technical content accessibly

---

## Product 21 — UM Geophysical Monitor

**Version:** 1.0.0 | **TRL:** 5 | **Tests:** 121 passing (247 with full engine tests)

### What It Is

The UM Geophysical Monitor is a **live globe disaster monitor** with a physics overlay.
It aggregates real-time data from:

- **USGS Earthquake API** — global seismic events, magnitude and depth filtered
- **NASA EONET** — fires, storms, and volcanic activity
- **NOAA NWS** — weather alerts (US/PNW focus)
- **NWAC** — avalanche forecasts for Pacific Northwest backcountry

The UM physics overlay applies:
- **Pillar 806** (backreacted radion / geophysical stress coupling)
- **Pillar 786** (winding stability basin)
- **Pillar 16** (φ-debt entropy accounting for geological systems)

Seven hazard layers with time, magnitude, and geographic filters. The PNW filter
makes it particularly useful for Pacific Northwest preparedness.

### Intended Use

Emergency managers, outdoor safety professionals, and geoscience researchers who
want a unified, real-time view of multiple hazard types with a physics-grounded
analytical overlay.

### Other Applications

- Disaster preparedness: personal and organizational early-warning dashboard
- Geoscience research: multi-hazard correlation analysis using live data
- Outdoor recreation safety: integrated avalanche, weather, and seismic monitoring
- Climate and hazard journalism: live data visualization for reporting
- Insurance and risk modeling: real-time multi-hazard exposure tracking

---

## The Full Registry at a Glance

| # | Product | TRL | Tests | Primary Domain |
|---|---------|-----|-------|----------------|
| 01 | Axiom OS Core Suite | 5 | 162 | AI / Cognitive OS |
| 02 | AZ-KERNEL Rust Kernel | 3 | 1 | Bare-metal OS |
| 03 | EIGE Governance Engine | 7 | 449 | Election Integrity |
| 04 | UM-SOS Scientific OS | 6 | — | Research Infrastructure |
| 05 | UOS Kernel Prototype | 3 | 566 | OS Research |
| 06 | Omega Synthesis Engine | 5 | 170 | Physics Computation |
| 07 | Holon Zero Engine | 5 | 347 | Core Physics |
| 08 | AxiomZero Journalist AI | 4 | 40 | Investigative Research |
| 09 | OmegaHolon Engine | 4 | 60 | Physics Pipeline |
| 10 | Filmer's Companion | 3 | 30 | Creative / Production |
| 11 | Terra OS | 4 | 45 | Earth Systems |
| 12 | Lithos OS | 3 | 35 | Mineralogy |
| 13 | Delphi | 5 | 55 | Symbolic / Divination |
| 14 | SDAM | 3 | 20 | Acoustic Comms |
| 15 | Pentacorder | 3 | 25 | Physics Measurement |
| 16 | AxiomZero Ω Oracle | 4 | 83 | Epistemic Audit |
| 17 | UM Image Generator | 5 | 113 | Science Visualization |
| 18 | UM Reader / Educator | 5 | 90 | Education / Access |
| 19 | Falsification Observatory | 5 | 112 | Experiment Tracking |
| 20 | OX Navigator | 4 | 149 | AI Physics Q&A |
| 21 | UM Geophysical Monitor | 5 | 121 | Hazard Monitoring |

**Total: 2,773 product-specific tests across 21 products (in addition to the 58,790+ core framework tests).**

---

## What Connects All 21

Every product in this registry shares three properties:

**1. Physics derivation.** The architecture, constants, and design choices are
traceable to the 5D Kaluza-Klein metric ansatz. This is not a branding claim — it
is a verifiable provenance chain. The fingerprint manifest at `12-AZ-IP/FINGERPRINT_MANIFEST.md`
contains SHA-256 hashes for every canonical source file.

**2. Honest epistemic labeling.** Every product carries an epistemic status:
HARDGATE (formally closed physics claims), ADJACENT TRACK (quantitative applications
not dependent on the physics being correct), or OPEN (work in progress). No product
overclaims.

**3. Open by default.** The entire registry is published under the Defensive Public
Commons License v1.0 (2026) — freely usable, attributable but not legally required to
attribute, and non-patentable for the core equations and theorems.

---

## What Comes Next

The `12-AZ-IP/` registry is a living document. Products advance along the TRL scale
as testing, deployment, and real-world validation proceed. The Falsification
Observatory (Product 19) will update in real time as experimental results arrive.
The OX Navigator (Product 20) will grow as the framework's knowledge base expands.

LiteBIRD launches in approximately 2032. That is when the primary falsifier for the
birefringence prediction will return its verdict. Until then, every product in this
registry is built on a framework that is internally consistent, externally testable,
and honestly labeled as to what it does and does not claim.

That is the AxiomZero standard.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*

*All 21 products are in the public domain under the Defensive Public Commons License v1.0 (2026).*
*Source: https://github.com/wuzbak/Unitary-Manifold-/tree/main/12-AZ-IP*
