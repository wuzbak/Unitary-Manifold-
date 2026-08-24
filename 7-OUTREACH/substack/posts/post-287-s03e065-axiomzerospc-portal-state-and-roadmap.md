# The Portal, the Repository, and Where We Go Next

**Unitary Manifold — S03E065 · v24.1**

---

There is now a live website where you can walk into a Kaluza-Klein physics framework and poke at it.

Not a landing page. Not a brochure. A working testbed: [axiomzerospc.org](https://axiomzerospc.org) — twenty interactive applications, all running in the browser, all connected to the same underlying theory. This post covers what it is, what the state of the project actually looks like right now, and the honest roadmap for making the infrastructure match the ambition.

---

## What axiomzerospc.org is

The portal started as a way to make the Unitary Manifold legible. The theory lives in a GitHub repository — 800+ derivation pillars, 57,000+ automated tests, 1,246 Lean4 formal theorems, raw Python — and almost none of that is navigable by a curious reader who isn't already deep in the work. The portal is the interface layer.

What's there now:

**Physics testbeds**

- **Falsification Observatory** — seven live experiments (LiteBIRD, DESI, JUNO, ACT, HL-LHC, nEDM@SNS, XENON-nT) displayed as a mission-control dashboard. Every experiment has a pre-registered kill condition. Green means passing. Orange means tension. Red means the theory is in trouble. You can simulate a future measurement and watch the verdict route in real time.

- **Axiom Zero Interrogator** — three modes: Challenge (search any claim, get the gate status and falsification condition), Experiment (trace any pillar against any experiment), Tension Map (a Canvas-rendered σ-deviation chart across the theory's known open problems). Twenty kilobytes of physics entries, fully offline.

- **UM Physics Image Generator** — eight Canvas 2D visualisation types: KK metric topology, winding number diagrams, CMB power spectrum, braid geometry, dimensional hierarchy, and more. No server required; exports PNG.

- **Flashcard Trainer** — 60 cards across seven categories (constants, predictions, open architecture limits, geometry, experiments, Lean4 theorems). Spaced repetition via keyboard. Offline.

**Research tools**

- **OX Navigator** — OX Alpha AI assistant (OpenRouter backend), context-packed with the full theory (~85k tokens). Interrogates claims, proposes Lean4 proof sketches, flags architecture limits. Requires an API key but runs entirely in the browser once loaded.

- **Axiom Journalist** — six-tab workbench for generating empirical dossier outputs: runs a claim through the gate registry, cross-references open tensions, and exports a structured PDF. Designed for anyone writing about the project who wants source-traceable output rather than marketing copy.

- **UM Reader** — 302 indexed entries (300 Substack posts, 2 books), nine topic categories, text-to-speech, KaTeX math rendering. A searchable archive of the project's public writing.

**Infrastructure apps**

- **UM-SOS Registry** — live view of the claim registry: what is hardgated, what is an adjacent track, what is explicitly open.
- **Omega Synthesis** — the FTUM fixed-point attractor visualised.
- **Holon Zero** — Ω₀ pillar explorer.
- **Oracle** — the core RAG assistant backed by the HuggingFace knowledge dataset.

There are twenty apps in total. All are offline-capable (no server round-trips for the core functionality). All have automated test suites — 41 to 92 tests each — that run on every push to main.

---

## Where the repository actually is

This is not a summary designed to impress. It is the literal current state.

**Version:** v24.1, Sprint AT (2026-08-23)

**Test suite:** 57,927 passing · 47 skipped · 12 deselected · **0 failed**. The zero-failures constraint is enforced as a hard gate — no merge goes in that breaks it.

**Lean4 formal theorems:** 1,246 across ~80 `.lean` files. These are machine-checked proofs inside Mathlib, not assertions.

**Pillar slots:** 806 derivation pillars registered. 208 are hardgate (formally closed). The remainder are adjacent tracks — applied domains, quantum simulation, F-theory extensions — labeled clearly as non-hardgate.

**Live experimental status (as of this writing):**

| Experiment | Status | Detail |
|---|---|---|
| Birefringence β | **First-detection candidate** | ACT+Planck DR6: β=0.277°±0.057° at 4.8σ. Low branch (0.273°) central value match at 0.07σ. LiteBIRD (~2032) is the discriminant. |
| DESI dark energy wₐ | **Dataset-dependent** | BAO-only, Pantheon+, Union3: all PASS. DESY5: 3.18σ raw, FALSIFIED_CANDIDATE gate. Loop-QKK alternative reduces to 1.82σ. Not resolved. |
| JUNO Δm²₂₁ | **Escalating tension** | First data: tension re-computed 1.07σ → 1.71σ with tighter JUNO 2026 error bar. Year 2 projection is the next gate. |
| ACT r | PASS | r=0.0315, BICEP/Keck < 0.036. |
| HL-LHC M_G* | PASS | KK graviton M₁≈1.0 TeV; exclusion < 4.0 TeV. |
| nEDM@SNS | PASS (awaiting data) | d_n≈7.8×10⁻²⁷ e·cm; experiment scheduled 2028. |
| XENON-nT | TENSION | σ_SI≈6×10⁻⁴⁷ cm² below current limit, but KK DM tree-level architecture limit applies. |

**Known open architecture limits** (not hidden, not softened):
- CMB acoustic-peak amplitude suppressed ×4–7 (documented in FALLIBILITY.md, Admission 2; addressed but not closed by Pillars 57+63).
- Higgs mass: 1-loop CW from KK tower gives ~34 GeV; PDG is ~125 GeV. Architecture limit survives.
- n_w=5 uniqueness: Planck nₛ provides the observational selection; first-principles uniqueness proof is not complete.
- Cosmological constant: KK tower hierarchy 10⁵⁵ above observed Λ. Pre-registered as shared with all quantum gravity frameworks.

The theory is internally self-consistent. External confirmation is pending. The birefringence signal from ACT+Planck DR6 is the most significant recent development — a 4.8σ detection compatible with the low branch — but LiteBIRD is required for a decisive test.

---

## The roadmap: migrating the portal off Base44

The current portal runs on Base44, a rapid-deployment platform. It got us to a working site fast, and that was the right call. The limitations are now visible: uptime is not guaranteed by SLA, CI/CD integration is manual, deploys are not versioned, and the cost model does not scale if traffic grows.

The migration target is a split architecture:

**HuggingFace Spaces for compute-heavy backends**

The backends that require server-side computation — OX Alpha, the Oracle RAG assistant, the CMB calculator, the VQE sandbox — are already partially migrated. The repository has four live HF Spaces: `oracle-space`, `cmb-calc-space`, `vqe-sandbox`, and `um-knowledge-dataset`. The path forward is completing that migration: containerise the FastAPI backend in `bot/assistant_api.py`, deploy it as a Gradio or Docker Space, and update the frontend `fetch()` calls to point at the new endpoint.

**Azure Static Web Apps (or equivalent) for the SPA shell**

The twenty frontend apps are static: HTML + vanilla JS + Canvas. They have no build step, no framework, no bundler. This makes them ideal for Azure Static Web Apps (or GitHub Pages with a custom domain, which is already configured for the portal index). The migration steps are:

1. **Inventory**: audit each app's external dependencies (currently: KaTeX CDN, one OpenRouter API call in OX Navigator). All other apps are fully self-contained.
2. **CI/CD hook**: add a workflow that deploys `public-site/` to the static host on every merge to main. The test suite already runs on every push; the deploy step is a one-line addition.
3. **Custom domain**: `axiomzerospc.org` already resolves. Point the DNS CNAME at the new host.
4. **Versioned rollback**: static hosts give you deployment history. If an app ships broken, roll back in one click.
5. **Gradual cutover**: migrate one app at a time. Keep Base44 live until all twenty are verified on the new infrastructure.

**What does not change**

The physics does not change. The test suite does not change. The Lean4 proofs do not change. The migration is purely infrastructure — a better home for the same content.

**Timeline**

There is no artificial deadline. The birefringence decision window is ~2032 (LiteBIRD). The JUNO Year 2 decision is ~2027. The DESI DR3 audit is ongoing. The portal migration will happen in parallel with the physics work, one app at a time, as sprint bandwidth allows.

---

## Why this matters

A physical theory that cannot be interrogated publicly is not doing its job. Every architecture limit, every open tension, every pre-registered falsification condition in this project is machine-readable — in Python dicts, in Lean4 propositions, in JSON gate registries. The portal is how that machine-readable honesty becomes human-readable.

The goal is not to convince you the theory is correct. The goal is to make it falsifiable in a way you can actually see. The Falsification Observatory shows you exactly what would break the framework. The Interrogator lets you challenge any specific claim. The UM Reader gives you two years of public writing on the project, searchable and cited.

That is the portal. The infrastructure will improve. The physics work continues.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
