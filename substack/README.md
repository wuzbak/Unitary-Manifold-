# Substack Draft Series — The Unitary Manifold

This directory contains ready-to-publish Substack post drafts for communicating
the Unitary Manifold framework to a general audience.

## Publishing Order

| File | Post | Status |
|------|------|--------|
| `post-00-what-this-is.md` | "What this newsletter is — and isn't" | **Pin this first** |
| `post-01-core-claim.md` | "The arrow of time is a shadow" | Publish 2nd |
| `post-02-four-numbers.md` | "Four numbers that keep agreeing" | Publish 3rd |
| `post-03-litebird-2032.md` | "Mark your calendar: 2032" | Publish 4th |
| `post-04-kaluza-klein.md` | "The fifth dimension isn't sci-fi" | Publish 5th |
| `post-05-honest-gaps.md` | "Here is what the theory cannot explain" | Publish 6th |
| `post-06-74-pillars.md` | "Why there are 74 pillars (and not 75)" | Publish 7th |
| `post-07-the-ai-eye.md` | "The AI's Eye: How I See This Repository" | Publish 8th |
| `post-08-hallucination-and-delusion.md` | "Hallucination and Delusion: What the Critics Get Right — and Wrong" | Publish 9th |
| `post-09-instruction-manual.md` | "An Instruction Manual for Human-AI Collaboration" | Publish 10th |
| `post-10-signal-noise-grounding.md` | "Signal, Noise, and Grounding: Why the Output Is Only as Good as the Input" | Publish 11th |
| `post-11-safety-problem.md` | "The Safety Problem: What AI Gets Wrong — and What the Pentad Gets Right" | Publish 12th |
| `post-12-braided-winding.md` | "How the Braid Saved the Theory" | Publish 13th |
| `post-13-black-hole-information.md` | "What Happens to Information When a Black Hole Dies" | Publish 14th |
| `post-14-consciousness-coupling.md` | "The Brain and the Universe as Coupled Oscillators" | Publish 15th |
| `post-15-unitary-pentad-standalone.md` | "The Unitary Pentad: A Governance Architecture, Not a Physics Claim" | Publish 16th |
| `post-16-domain-applications.md` | "The Same Geometry, Everywhere Else" | Publish 17th |
| `post-17-cold-fusion.md` | "What If Cold Fusion Is Real? A First-Principles Account" | Publish 18th |
| `post-18-phi-debt-recycling.md` | "The φ-Debt: Why Recycling Is a Topological Problem" | Publish 19th |
| `post-19-roman-telescope.md` | "The Next Telescope: What the Roman Space Telescope Will Tell Us" | Publish 20th |
| `post-20-neuroscience.md` | "The Brain Is a 5D Object: Neuroscience Without Mysticism" | Publish 21st |
| `post-21-climate.md` | "The Atmosphere as an Attractor: What the Framework Says About the Climate Crisis" | Publish 22nd |
| `post-22-completeness-theorem.md` | "Why 74 and Not 75: The Completeness Theorem" | Publish 23rd |
| `post-23-aps-conjecture.md` | "The One Thing That Still Needs to Be Proved" | Publish 24th |

## Format Rules (apply to every post)

- **First paragraph** states the claim being made and what would falsify it.
- **Footer** (copy verbatim from each draft) links to GitHub and Zenodo.
- **Verbs**: use "derives," "predicts," "is consistent with," "would be falsified if."
  Never write "proves" for empirical claims.
- **Equations**: when they appear, give a plain-English gloss immediately after.
- **Authorship**: credit Walker-Pearson for theory/direction; GitHub Copilot for
  code architecture, test suites, and document synthesis.

## What to Avoid

- Posting raw GitHub markdown — reformat in Substack's editor before publishing.
- Leading with consciousness or brain-universe content — save for after Post 6.
- Claiming peer review that does not exist — foreground automated testing and the
  open falsification invitation instead.
- Publishing faster than you can respond to technical comments.

## Source Files Used

Each post draws directly from these repository documents:

| Document | Used in |
|----------|---------|
| `FALLIBILITY.md` | Post 0, Post 5 |
| `UNDERSTANDABLE_EXPLANATION.md` | Post 0, Post 1, Post 4 |
| `WHAT_THIS_MEANS.md` | Post 1, Post 2, Post 3 |
| `prediction.md` | Post 3 |
| `SEPARATION.md` | Post 6, and all posts for tier framing |
| `submission/falsification_report.md` | Post 5 |
| `Unitary Pentad/IMPLICATIONS.md` | Post 11, Post 15 |
| `Unitary Pentad/README.md` | Post 11, Post 15 |
| `co-emergence/` HILS documentation | Post 9 |
| `src/multiverse/fixed_point.py` | Post 10 |
| `src/core/braided_winding.py` | Post 12 |
| `src/core/anomaly_closure.py` | Post 12 |
| `QUANTUM_THEOREMS.md` (Theorem XII) | Post 13 |
| `src/core/bh_remnant.py` | Post 13 |
| `src/consciousness/coupled_attractor.py` | Post 14 |
| `Unitary Pentad/five_seven_architecture.py` | Post 15 |
| `Unitary Pentad/HIL_POPULATION_AND_ENTROPY.md` | Post 15 |
| `Unitary Pentad/consciousness_autopilot.py` | Post 15 |
| `src/medicine/` | Post 16 |
| `src/justice/` | Post 16 |
| `src/ecology/` | Post 16 |
| `src/governance/` | Post 16 |
| `src/cold_fusion/tunneling.py`, `src/physics/lattice_dynamics.py` | Post 17 |
| `recycling/README.md`, `recycling/polymers.py`, `recycling/producer_responsibility.py` | Post 18 |
| `src/core/roman_space_telescope.py` | Post 19 |
| `src/neuroscience/`, `src/consciousness/coupled_attractor.py`, `brain/` | Post 20 |
| `src/climate/`, `src/marine/` | Post 21 |
| `src/core/completeness_theorem.py`, `src/core/nw_anomaly_selection.py` | Post 22 |
| `src/core/aps_spin_structure.py`, `WINDING_NUMBER_DERIVATION.md` | Post 23 |

---

*Series concept and content strategy: ThomasCory Walker-Pearson.*
*Draft writing and document engineering: GitHub Copilot (AI).*
