# Snapshot Archive Manifest — 2026-04-12

This document records the **complete state** of the Unitary Manifold repository
as of **2026-04-12** (commit `b601882`).  It exists as a "just-in-case" reference
so the exact contents at this moment are permanently documented, regardless of
future changes to the live repository.

---

## Repository identity

| Field | Value |
|---|---|
| Repository | `wuzbak/Unitary-Manifold-` |
| Snapshot date | 2026-04-12 |
| Commit SHA | `b601882` |
| Branch at time of snapshot | `main` |
| Total files (excl. `.git`) | 161 |
| Total size (excl. `.git`) | 5.5 MB |
| Test suite | 678 fast + 11 slow tests, all passing |

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

### Source code (`src/`)
| File | Purpose |
|---|---|
| `src/__init__.py` | Package init |
| `src/core/__init__.py` | Core package init |
| `src/core/metric.py` | Kaluza-Klein metric, curvature computation |
| `src/core/evolution.py` | Walker-Pearson integrator, FieldState API |
| `src/core/inflation.py` | Inflationary dynamics |
| `src/core/transfer.py` | CMB transfer function, Planck 2018 reference data |
| `src/core/diagnostics.py` | CMB diagnostics: chi2, power spectra, observables |
| `src/holography/__init__.py` | Holography package init |
| `src/holography/boundary.py` | Holographic boundary dynamics |
| `src/multiverse/__init__.py` | Multiverse package init |
| `src/multiverse/fixed_point.py` | UEUM operator, FTUM iteration |

### Test suite (`tests/`) — 689 total tests (678 fast + 11 slow)
| File | Tests | Coverage |
|---|---|---|
| `tests/conftest.py` | — | Shared pytest fixtures |
| `tests/test_metric.py` | 30 | Metric & curvature |
| `tests/test_evolution.py` | 49 | Evolution + constraints |
| `tests/test_boundary.py` | 21 | Boundary & entropy |
| `tests/test_fixed_point.py` | 35 | FTUM & operator |
| `tests/test_convergence.py` | 10 | Numerical convergence |
| `tests/test_inflation.py` | 141 | Inflationary dynamics |
| `tests/test_closure_batch1.py` | 25 | Closure batch 1 |
| `tests/test_closure_batch2.py` | 31 | Closure batch 2 |
| `tests/test_fuzzing.py` | 20 | Fuzz / stress tests |
| `tests/test_dimensional_reduction.py` | 14 | Dimensional reduction |
| `tests/test_discretization_invariance.py` | 13 | Grid independence |
| `tests/test_arrow_of_time.py` | 22 | Entropy / irreversibility |
| `tests/test_cmb_landscape.py` | 24 | CMB chi2 landscape |
| `tests/test_e2e_pipeline.py` | 43 | End-to-end pipeline |
| `tests/test_observational_resolution.py` | 31 | Observational constraints |
| `tests/test_parallel_validation.py` | 38 | Parallel theory validation |
| `tests/test_quantum_unification.py` | 26 | BH info, CCR, Hawking T, ER=EPR |
| `tests/test_richardson_multitime.py` | 11 *(slow)* | Richardson extrapolation |

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

*Snapshot manifest generated: 2026-04-12 — commit b601882*
