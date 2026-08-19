# 7-OUTREACH/substack/visuals — Substack Visual Assets

> **Epistemic notice:** These images are communication aids for Substack.  They
> summarize repository claims, verification status, falsification windows, and
> workflow structure; they do not replace `FALLIBILITY.md`,
> `1-THEORY/DERIVATION_STATUS.md`, `3-FALSIFICATION/`, or the executable tests.
> The images themselves have not undergone independent peer review.
> They provide visual summaries to orient readers before they enter the technical record.

Use these PNGs as headers, inline explainers, and figure inserts in Substack
posts.  Keep captions honest: automated tests demonstrate internal consistency
of the coded framework; empirical confirmation still requires external
observation and independent review.

## Recommended first-use set

| File | Use |
|------|-----|
| [`fig04_repository_layer_architecture.png`](fig04_repository_layer_architecture.png) | Orient new readers to the repository map and separate theory, falsification, governance, outreach, and infrastructure. |
| [`fig10_5d_metric_structure.png`](fig10_5d_metric_structure.png) | Explain the 5D Kaluza-Klein metric block structure behind the core model. |
| [`fig11_braid_topology.png`](fig11_braid_topology.png) | Visualize the `(5,7)` braid and the `K_CS = 5² + 7² = 74` hook. |
| [`fig01_cmb_ns_r_plane.png`](fig01_cmb_ns_r_plane.png) | Show where the CMB `n_s` and `r` prediction sits relative to common observational bands. |
| [`fig02_birefringence_window.png`](fig02_birefringence_window.png) | Lead falsification discussions with the LiteBIRD-facing birefringence window. |
| [`fig03_toe_parameter_dashboard.png`](fig03_toe_parameter_dashboard.png) | Summarize the claimed 28-parameter geometry dashboard. |
| [`fig08_test_suite_growth.png`](fig08_test_suite_growth.png) | Communicate the growth of executable regression coverage. |
| [`fig14_falsification_calendar.png`](fig14_falsification_calendar.png) | Explain what future observations could break or stress the framework. |
| [`fig17_human_ai_workflow.png`](fig17_human_ai_workflow.png) | Explain the human-AI co-creation and provenance story. |
| [`fig18_unitary_pentad_structure.png`](fig18_unitary_pentad_structure.png) | Explain the governance layer while keeping it separate from physics claims. |

## Complete gallery

| File | Caption seed |
|------|--------------|
| [`fig01_cmb_ns_r_plane.png`](fig01_cmb_ns_r_plane.png) | CMB `n_s`–`r` plane: Unitary Manifold point compared with Planck/BICEP-style constraint regions. |
| [`fig02_birefringence_window.png`](fig02_birefringence_window.png) | Birefringence prediction window and explicit kill zone for future polarization measurements. |
| [`fig03_toe_parameter_dashboard.png`](fig03_toe_parameter_dashboard.png) | 28-parameter dashboard for the repository's ToE claim record. |
| [`fig04_repository_layer_architecture.png`](fig04_repository_layer_architecture.png) | Numbered epistemic layers: theory, reproducibility, falsification, implications, governance, monograph, outreach, safety, and infrastructure. |
| [`fig05_pillar_domain_distribution.png`](fig05_pillar_domain_distribution.png) | Pillar distribution by domain and associated test-count framing. |
| [`fig06_derivation_status_breakdown.png`](fig06_derivation_status_breakdown.png) | Derivation/claim-status breakdown for explaining what is derived, constrained, or still bounded by caveats. |
| [`fig07_mas_wave_progress.png`](fig07_mas_wave_progress.png) | MAS wave progress and growth of the machine-audited sprint record. |
| [`fig08_test_suite_growth.png`](fig08_test_suite_growth.png) | Test suite growth over versions, useful for reproducibility and audit posts. |
| [`fig09_toe_score_timeline.png`](fig09_toe_score_timeline.png) | framework derivation coverage timeline as tracked by the repository's internal claim ledger. |
| [`fig10_5d_metric_structure.png`](fig10_5d_metric_structure.png) | 5D metric decomposition: 4D spacetime block, gauge field coupling, and radion/extra-dimensional term. |
| [`fig11_braid_topology.png`](fig11_braid_topology.png) | `(5,7)` braid topology and `K_CS = 74` visual hook. |
| [`fig12_quantum_lane_architecture.png`](fig12_quantum_lane_architecture.png) | Quantum simulation/interoperability lane architecture. |
| [`fig13_parameter_residuals.png`](fig13_parameter_residuals.png) | Sorted residual view for parameter-claim communication. |
| [`fig14_falsification_calendar.png`](fig14_falsification_calendar.png) | Falsification calendar for near-, mid-, and long-horizon observational checks. |
| [`fig15_ftum_convergence.png`](fig15_ftum_convergence.png) | FTUM fixed-point convergence visual for the fixed-point story. |
| [`fig16_dimensional_roadmap.png`](fig16_dimensional_roadmap.png) | Dimensional roadmap for the 5D-to-higher-dimensional bootstrap narrative. |
| [`fig17_human_ai_workflow.png`](fig17_human_ai_workflow.png) | Human scientific direction plus AI-assisted code/test/document architecture. |
| [`fig18_unitary_pentad_structure.png`](fig18_unitary_pentad_structure.png) | Unitary Pentad governance structure, explicitly separate from physics proof status. |

## Regeneration

```bash
python3 9-INFRASTRUCTURE/scripts/gen_visualizations.py
```

The generator writes identical PNGs to:

- `7-OUTREACH/substack/visuals/` — Substack-ready assets
- `7-OUTREACH/visualizations/` — canonical outreach gallery
- `9-INFRASTRUCTURE/results/` — infrastructure result archive

## Caption rule

When embedding a figure in Substack, include one sentence stating what the image
does **not** prove.  Example: “This chart summarizes the repository's internal
claim ledger; it is not independent empirical confirmation.”
