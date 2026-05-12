# Master Inventory — Programs, Suites, Languages, and AI Systems

## 1) Confirmed in-repo usage

### Languages and formats

| Category | Confirmed items | Evidence |
|---|---|---|
| Core implementation | Python | `src/**/*.py`, `tests/**/*.py`, `recycling/**/*.py` |
| CI/config | YAML | `.github/workflows/tests.yml`, `docs/mas_tracker.yml` |
| Documentation | Markdown | `README.md`, `FALLIBILITY.md`, `STATUS.md` |
| Publication sources | LaTeX, BibTeX | `arxiv/main.tex`, `arxiv/references.bib` |
| Metadata/exchange | JSON / JSON-LD / CFF YAML | `9-INFRASTRUCTURE/mcp-config.json`, `9-INFRASTRUCTURE/schema.jsonld`, `CITATION.cff` |
| Bot/web infra | JavaScript (Node) | `9-INFRASTRUCTURE/bot/copilot-extension/server.js`, `package.json` |
| RAG bot stack | Python (`fastapi`, `uvicorn`, `gradio`, `openai`, `python-dotenv`) | `9-INFRASTRUCTURE/bot/rag/requirements.txt`, `9-INFRASTRUCTURE/bot/rag/app.py` |
| Utility scripts | Shell, MATLAB | `9-INFRASTRUCTURE/update_numbers.sh`, `9-INFRASTRUCTURE/demo.m` |

### Programs and suites

| Function | Confirmed programs/suites | Evidence |
|---|---|---|
| Test execution | `pytest` | `.github/workflows/tests.yml`, `tests/` |
| Python dependency/env | `pip` | `.github/workflows/tests.yml`, `requirements.txt` |
| Core numerical stack | `numpy`, `scipy`, `mpmath`, `matplotlib` | `requirements.txt`, imports in `src/` |
| Optional high-compute lanes | `jax[cpu]`, `jaxlib` | `requirements.txt`, `tests/test_jax_backend.py` |
| Constraint/prover lanes | `z3-solver` | `requirements.txt`, `tests/test_z3_pentad_checker.py` |
| Experiment tracking lane | `wandb` | `requirements.txt`, `tests/test_wandb_logger.py` |
| Data pipeline lane | `dvc` | `requirements.txt` |
| Symbolic/formal checks | `sympy` | `.github/workflows/tests.yml` (`algebra-proof`), `requirements.txt` |
| Formal theorem lane | Lean 4 (`elan`/`lake`) | `.github/workflows/lean4-check.yml`, `lean4/` |
| Mutation hard gate | `mutmut` | `.github/workflows/mutation-hard-gate.yml` |
| Documentation build lane | `jupyter-book`, Jekyll/Pages actions | `.github/workflows/jupyterbook.yml`, `.github/workflows/pages.yml` |
| Release/archive lanes | `softprops/action-gh-release`, `tar`, IPFS (`kubo`) | `.github/workflows/release.yml`, `.github/workflows/build-download.yml`, `.github/workflows/ipfs-publish.yml` |
| CI/CD orchestration | GitHub Actions | `.github/workflows/*.yml` |
| Algebraic falsification harness | `ALGEBRA_PROOF.py` | `ALGEBRA_PROOF.py`, `.github/workflows/tests.yml` |
| Ledger + onboarding consistency | `canonical_ledger_consistency.py` + pytest job | `src/core/canonical_ledger_consistency.py`, `tests/test_canonical_ledger_consistency.py`, `.github/workflows/tests.yml` (`ledger-consistency` job) |
| Security transitive dep pins | `cryptography`, `pyasn1`, `pyOpenSSL`, `setuptools`, `urllib3`, `wheel` (patched floors) | `requirements.txt` (CVE section) |

### AI systems and agent surfaces

| Class | Confirmed system/surface | Evidence |
|---|---|---|
| Primary code/doc engineering agent | GitHub Copilot (AI) — chat + inline + coding agent (cloud) | repository-wide authorship statements in docs |
| Repository agent policy layer | MCP-connected agents (e.g., Mythos) | `AGENTS.md`, `9-INFRASTRUCTURE/mcp-config.json` |
| Copilot Chat integration | GitHub Copilot Extension (`@unitary-manifold`) | `9-INFRASTRUCTURE/bot/copilot-extension/` |
| RAG assistant pipeline | Python RAG bot (OpenAI-backed via `openai` SDK) | `9-INFRASTRUCTURE/bot/rag/` |
| Public Q&A assistants | ChatGPT Custom GPT + Claude Project (supported setup path) | `9-INFRASTRUCTURE/bot/custom-gpt/SETUP_GUIDE.md`, `SYSTEM_PROMPT.md` |
| Multi-model downstream support | OpenAI / Anthropic Claude / Google Gemini / Microsoft Copilot | documented in bot README + custom-gpt setup guide |

## 2) Available infrastructure (do not over-claim as always active)

| Option | Availability in repo | Evidence |
|---|---|---|
| Custom GPT / Claude Project setup | Supported by docs/prompts | `9-INFRASTRUCTURE/bot/custom-gpt/SETUP_GUIDE.md`, `SYSTEM_PROMPT.md` |
| GitHub Pages chatbot | Supported widget deployment path | `9-INFRASTRUCTURE/bot/pages-chatbot/README.md` |
| MCP GitHub server | Configuration available | `9-INFRASTRUCTURE/mcp-config.json`, `AGENTS.md` |
| MCP Bright Data server | Configuration available | `9-INFRASTRUCTURE/mcp-config.json`, `AGENTS.md` |

## 3) Canonical status pointers

- Current MAS/post-MAS tracker: `docs/mas_tracker.yml`
- Current wave-level changelog: `docs/WAVE_CHANGELOG.md`
- Canonical limitations/falsification framing: `FALLIBILITY.md`

## 4) Repository source map (confirmed modules)

### Core physics source tree (`src/`)

| Directory | Contents | Role |
|---|---|---|
| `src/core/` | 200+ modules — 5D metric, KK geometry, braided winding, SM params, inflation, CMB transfer; Pillars 200–217 (RGE through GN derivation); Pillars 218–232 adjacent tracks | Hardgated + adjacent physics |
| `src/holography/` | `boundary.py` — holographic boundary, entropy-area | Pillar 4 |
| `src/multiverse/` | `fixed_point.py` — FTUM fixed-point iteration | Pillars 5, 29, 38 |
| `src/quantum/` | `kk_vqe.py`, `fermi_hubbard.py`, `fermion_mapping.py`, `execution.py`, `observables.py`, `benchmarks.py`, `xdiag_bridge/` (contract, parity, routing, workflow) | Non-hardgate quantum simulation lane |
| `src/sixd/` – `src/eleventd/` | 6D–11D field equations, generation count, Higgs mass, CKM, anomaly cancellation, flux landscape, Hořava-Witten | Higher-dimensional extension pillars |
| `src/meta/` | MAS wave engine | Meta-analysis |
| `src/data/` | Planck data fetcher | External data ingestion |
| `src/consciousness/` | Coupled brain-universe attractor | Pillar 9 |
| `src/atomic_structure/`, `src/cold_fusion/`, `src/chemistry/`, `src/astronomy/` | Atomic orbitals, LENR tunneling, chemistry, stellar | Pillars 10–15 |
| `src/physics/` | `lattice_dynamics.py` — collective Gamow, phonon-radion bridge | Pillar 15-B |
| `src/earth/`, `src/biology/`, `src/medicine/`, `src/justice/`, `src/governance/` | Earth systems, biology, medicine, law, democracy | Pillars 12–13, 17–19 |
| `src/neuroscience/`, `src/ecology/`, `src/climate/`, `src/marine/` | Neurons, ecosystems, atmosphere, deep ocean | Pillars 20–23 |
| `src/psychology/`, `src/genetics/`, `src/materials/` | Cognition, genomics, condensed matter | Pillars 24–26 |

### Adjacent research track pillar modules (`src/core/`)

| Pillar | Module | Status |
|---|---|---|
| 218 | `pillar218_quantum_control.py` | 🔵 adjacent track |
| 219 | `pillar219_interstellar_travel.py` | 🔵 adjacent track |
| 220 | `pillar220_energy_manifold.py` | 🔵 adjacent track |
| 221 | `pillar221_sound_energy.py` | 🔵 adjacent track |
| 222 | `pillar222_nanotechnology_control_systems.py` | 🔵 adjacent track |
| 223 | `pillar223_medical_imaging_diagnosis.py` | 🔵 adjacent track |
| 224 | `pillar224_quantum_bottleneck_calculator.py` | 🔵 adjacent track |
| 227 | `pillar227_ai_robotics_bottleneck_engine.py` | 🔵 adjacent track |
| 228 | `pillar228_cancer_bottleneck_calculator.py` | 🔵 adjacent track |
| 229 | `pillar229_ai_robotics_solutions_engine.py` | 🔵 adjacent track |
| 230 | `pillar230_cancer_solutions_engine.py` | 🔵 adjacent track |
| 232 | `pillar232_universal_cancer_control_framework.py` | 🔵 adjacent track |
