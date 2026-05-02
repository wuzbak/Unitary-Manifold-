# Snapshot Archive Manifest — 2026-04-30

This document records the **complete state** of the Unitary Manifold repository
as of **2026-04-30** (commit `726ef95`).  It exists as a "just-in-case" reference
so the exact contents at this moment are permanently documented, regardless of
future changes to the live repository.

---

## Repository identity

| Field | Value |
|---|---|
| Repository | `wuzbak/Unitary-Manifold-` |
| Snapshot date | 2026-04-30 |
| Commit SHA | `726ef95` |
| Branch at time of snapshot | `main` (via PR from `copilot/fix-contributors-correspondence-map`) |
| Total files (excl. `.git`) | 728 |
| Total size (excl. `.git`) | ~21 MB |
| Version | v9.28 — Gap Closure |
| Test suite | 15,615 passed · 330 skipped · 11 slow-deselected · 0 failed |
| Pillars | 99 core + sub-pillars 70-C/99-B/15-F + Pillar Ω = complete |

---

## How to restore this exact snapshot

```bash
git clone https://github.com/wuzbak/Unitary-Manifold-
cd Unitary-Manifold-
git checkout b601882
```

Or download the auto-generated archive from the corresponding GitHub Release:
`https://github.com/wuzbak/Unitary-Manifold-/releases`

---

## Complete file inventory

### Root documentation
| File | Purpose |
|---|---|
| `README.md` | Project overview, equations, quickstart |
| `AGENTS.md` | AI agent access policies and preferred ingest order |
| `MCP_INGEST.md` | Complete structured summary for MCP/LLM ingestion |
| `WHAT_THIS_MEANS.md` | Core claim in plain language |
| `UNIFICATION_PROOF.md` | Formal proof: QM, EM, SM as projections of 5D geometry |
| `QUANTUM_THEOREMS.md` | New theorems: BH information, CCR, Hawking T, ER=EPR |
| `BIG_QUESTIONS.md` | 15 big open questions addressed through the framework |
| `CITATION.cff` | Machine-readable citation metadata |
| `CONTRIBUTING.md` | Contribution guidelines |
| `CONTRIBUTORS.md` | List of contributors |
| `DOWNLOAD_GUIDE.md` | How to download / mirror the project |
| `FALLIBILITY.md` | Epistemic limitations and falsifiability |
| `FINAL_REVIEW_CONCLUSION.md` | Final review summary |
| `LEGEND.md` | Symbol and notation legend |
| `LICENSE` | Defensive Public Commons License v1.0 |
| `LICENSE-AGPL` | AGPL-3.0 license (code) |
| `NOTICE` | Copyright and attribution notice |
| `RELAY.md` | AI relay instructions |
| `REVIEW_CONCLUSION.md` | Review conclusion document |
| `SIMULATION_RUNS.md` | Numerical simulation run records |
| `TABLE_OF_CONTENTS.md` | Full table of contents for the monograph |
| `UNDERSTANDABLE_EXPLANATION.md` | Lay-audience explanation |
| `llms.txt` | AI-discovery index |
| `schema.jsonld` | JSON-LD structured data for knowledge graphs |
| `mcp-config.json` | MCP server configuration |
| `_config.yml` | Jekyll / GitHub Pages configuration |
| `demo.m` | MATLAB demo script |
| `pytest.ini` | Pytest configuration |
| `requirements.txt` | Python dependencies (numpy≥1.24, scipy≥1.11) |

### Monograph (PDF)
| File | Purpose |
|---|---|
| `THEBOOKV9a (1).pdf` | Full 74-chapter monograph (v9a) |

### Source code (`src/`) — 96 modules across 15 packages
| Package | Key modules |
|---|---|
| `src/core/` | `metric.py`, `evolution.py`, `inflation.py`, `transfer.py`, `diagnostics.py`, `boltzmann.py`, `braided_winding.py`, `derivation.py`, `fiber_bundle.py`, `uniqueness.py`, `phi0_closure.py` (Pillar 56), `cmb_peaks.py` (Pillar 57), `anomaly_closure.py` (Pillar 58), `litebird_forecast.py` (Pillar 70-B), `wolfenstein_geometry.py` (Pillar 87), `sm_free_parameters.py` (Pillar 88), `vacuum_geometric_proof.py` (Pillar 89), `neutrino_majorana_dirac.py` (Pillar 90), `cc_suppression_mechanism.py` (Pillar 91), `uv_completion_constraints.py` (Pillar 92), `yukawa_geometric_closure.py` (Pillar 93), `su5_orbifold_proof.py` (Pillar 94), `dual_sector_convergence.py` (Pillar 95), `unitary_closure.py` (Pillar 96), `gw_yukawa_derivation.py` (Pillar 97), `universal_yukawa.py` (Pillar 98), and 70+ additional pillar modules |
| `src/holography/` | `boundary.py` — holographic boundary dynamics |
| `src/multiverse/` | `fixed_point.py` — UEUM operator, FTUM iteration; `basin_analysis.py`, `observational_frontiers.py` |
| `src/consciousness/` | `coupled_attractor.py` — Pillar 9: Brain-Universe coupled fixed point |
| `src/chemistry/` | `bonds.py`, `reactions.py`, `periodic.py` — Pillar 10 |
| `src/astronomy/` | `stellar.py`, `planetary.py` — Pillar 11 |
| `src/earth/` | `geology.py`, `oceanography.py`, `meteorology.py` — Pillar 12 |
| `src/biology/` | `life.py`, `evolution.py`, `morphogenesis.py` — Pillar 13 |
| `src/atomic_structure/` | `orbitals.py`, `spectroscopy.py`, `fine_structure.py` — Pillar 14 |
| `src/cold_fusion/` | `tunneling.py`, `lattice.py`, `excess_heat.py` — Pillar 15 |
| `src/physics/` | `lattice_dynamics.py` — Pillar 15-B: collective Gamow, phonon-radion bridge |
| `src/medicine/`, `src/justice/`, `src/governance/` | Pillars 17–19 |
| `src/neuroscience/`, `src/ecology/`, `src/climate/`, `src/marine/` | Pillars 20–23 |
| `src/psychology/`, `src/genetics/`, `src/materials/` | Pillars 24–26 |

### Pillar Ω — Universal Mechanics Engine (`omega/`)
| File | Purpose |
|---|---|
| `omega/omega_synthesis.py` | Universal Mechanics Engine: 5 seeds → all observables; `UniversalEngine.compute_all()` → `OmegaReport`; 6 domains |
| `omega/test_omega_synthesis.py` | 168 tests — all passing |
| `omega/README.md` | Pillar Ω documentation |
| `omega/CALCULATOR.md` | Observable calculator reference |

### Test suite (`tests/`) — 150+ test files, ~13,059 fast-passing tests
Full per-file breakdown includes all pillars 1–99 + Pillar 70-B + Ω.  Key files:

| File | Tests | Coverage |
|---|---|---|
| `tests/test_metric.py` | 36 | Metric & curvature |
| `tests/test_evolution.py` | 49 | Evolution + constraints |
| `tests/test_boundary.py` | 21 | Boundary & entropy |
| `tests/test_fixed_point.py` | 50 | FTUM & operator |
| `tests/test_inflation.py` | 271 | Inflationary dynamics |
| `tests/test_braided_winding.py` | 70 | Braided (5,7) resonance, r-tension resolution |
| `tests/test_fiber_bundle.py` | 96 | Fiber bundle topology, anomaly cancellation |
| `tests/test_atomic_structure.py` | 187 | Pillar 14: atomic orbitals, spectroscopy, fine structure |
| `tests/test_cold_fusion.py` | 240 | Pillar 15: φ-enhanced tunneling, Pd lattice, excess heat |
| `tests/test_wolfenstein_geometry.py` | 130 | Pillar 87: CKM Wolfenstein parameters |
| `tests/test_sm_free_parameters.py` | 139 | Pillar 88: SM 28-parameter audit |
| `tests/test_vacuum_geometric_proof.py` | 59 | Pillar 89: algebraic n_w = 5 proof |
| `tests/test_dual_sector_convergence.py` | 93 | Pillar 95: dual-sector convergence |
| `tests/test_unitary_closure.py` | 59 | Pillar 96: unitary closure |
| `tests/test_gw_yukawa_derivation.py` | 88 | Pillar 97: GW Yukawa |
| `tests/test_universal_yukawa.py` | 126 | Pillar 98: universal Yukawa |
| `tests/test_richardson_multitime.py` | 11 *(slow)* | Richardson extrapolation |
| *(…and 130+ additional test files)* | | |

**Grand total (tests/ + recycling/ + 5-GOVERNANCE/Unitary Pentad/ + omega/):** 15,615 passed · 330 skipped · 11 slow-deselected · 0 failed

### Additional test suites

| Suite | Tests | Coverage |
|---|---|---|
| `recycling/` | 316 | Pillar 16: φ-debt entropy accounting |
| `5-GOVERNANCE/Unitary Pentad/` | ~1,026 passed, 254 skipped | 18 HILS governance modules |
| `omega/test_omega_synthesis.py` | 168 | Pillar Ω: Universal Mechanics Engine |

### Notebooks (`notebooks/`)
| File | Purpose |
|---|---|
| `notebooks/01_quickstart.ipynb` | Runnable field evolution demo |
| `notebooks/02_holographic_boundary.ipynb` | Boundary dynamics demo |
| `notebooks/03_multiverse_fixed_point.ipynb` | FTUM convergence demo |

### Manuscripts & arXiv (`manuscript/`, `arxiv/`)
| File | Purpose |
|---|---|
| `manuscript/ch02_mathematical_preliminaries.md` | Chapter 2 draft |
| `arxiv/main.tex` | Full LaTeX source for arXiv submission |
| `arxiv/references.bib` | BibTeX reference list |
| `arxiv/SUBMISSION_GUIDE.md` | Step-by-step arXiv upload guide |

### Scripts (`scripts/`)
| File | Purpose |
|---|---|
| `scripts/create_archive.py` | Packages the project as a local .zip |
| `scripts/run_boundary.py` | Boundary dynamics runner |
| `scripts/run_evolution.py` | Evolution runner |
| `scripts/run_fixed_point.py` | Fixed-point runner |
| `scripts/run_inflation.py` | Inflation runner |
| `scripts/run_metric.py` | Metric runner |

### Results (`results/`)
| File | Purpose |
|---|---|
| `results/01_charge_conservation.png` | Charge conservation plot |
| `results/02_reconstruction.png` | Field reconstruction plot |
| `results/03_power_spectrum.png` | CMB power spectrum plot |
| `results/04_phase_space.png` | Phase space plot |
| `results/05_convergence.png` | Convergence plot |
| `results/06_falsification.png` | Falsification plot |
| `results/summary.txt` | Numerical results summary |

### Submission (`submission/`)
| File | Purpose |
|---|---|
| `submission/demo.py` | Submission demo script |
| `submission/falsification_report.md` | Falsification report |
| `submission/one_page_summary.md` | One-page summary |

### Zenodo (`zenodo/`)
| File | Purpose |
|---|---|
| `zenodo/.zenodo.json` | Zenodo deposit metadata |
| `zenodo/SUBMISSION_GUIDE.md` | Step-by-step Zenodo deposit guide |

### Wiki (`wiki/`)
| File | Purpose |
|---|---|
| `wiki/Home.md` | Wiki home |
| `wiki/API-Reference.md` | API reference |
| `wiki/Contributing.md` | Contributing guide |
| `wiki/Field-Equations.md` | Field equations reference |
| `wiki/Getting-Started.md` | Getting started guide |
| `wiki/Mathematical-Framework.md` | Mathematical framework |
| `wiki/Monograph-Structure.md` | Monograph structure |
| `wiki/Numerical-Methods.md` | Numerical methods |

### GitHub configuration (`.github/`)
| File | Purpose |
|---|---|
| `.github/workflows/tests.yml` | CI: run full test suite |
| `.github/workflows/release.yml` | CI: create GitHub Release on tag push (or manual dispatch) |
| `.github/workflows/build-download.yml` | CI: build download artifacts |
| `.github/workflows/pages.yml` | CI: deploy GitHub Pages |
| `.github/copilot-instructions.md` | Copilot AI instructions |
| `.github/topics.yml` | Repository topic tags |

---

## Creating a GitHub Release from this snapshot

The release workflow (`.github/workflows/release.yml`) supports **manual dispatch**.
To create a permanent GitHub Release with a downloadable zip archive:

1. Go to **Actions** → **Create GitHub Release**
2. Click **Run workflow**
3. Enter a tag name (e.g. `v9.0-snapshot-2026-04-12`)
4. Click **Run workflow**

GitHub will automatically create the tag, build a source archive zip, and publish
the release — all without any local tooling required.

Alternatively, a local archive can be created at any time:

```bash
python scripts/create_archive.py
# → unitary-manifold_<timestamp>.zip  (full project, ~5.5 MB)
```

---

*Snapshot manifest updated: 2026-05-01 — v9.29 (101 pillars + sub-pillars, 15,615 tests, 728+ files)*
