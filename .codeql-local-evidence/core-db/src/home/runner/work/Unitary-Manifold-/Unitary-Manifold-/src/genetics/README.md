# src/genetics — Analogical Application (TIER 3)

**Epistemic status: Mathematical framework applied to a domain — tests confirm code correctness ONLY**

This module uses the φ/Bμ mathematical language of the Unitary Manifold as a
modeling framework for genetics.  Every quantity in this package is defined in
terms of φ-fields, and the equations follow internally from those definitions.

## Sub-modules

| File | Scope |
|------|-------|
| `genomics.py` | Genome as φ-archive: mutation, repair, epigenetics, transposons |
| `evolution.py` | Selection, drift, speciation, HGT as φ-field dynamics |
| `expression.py` | Transcription, translation, splicing, protein folding as φ-flows |
| `synthetic_biology.py` | **Synthetic biology as attractor engineering** — gene circuits, CRISPR, metabolic engineering, AI×SynBio, chassis minimality, biosafety containment, DNA data storage, directed evolution, circuit noise, bioeconomy output |

## Synthetic Biology (Pillar 25 Extension)

Natural biology *discovers* FTUM fixed points through evolution; synthetic
biology *deliberately designs* them.  The key mappings:

| SynBio concept | UM equivalent |
|----------------|--------------|
| Gene circuit (toggle, oscillator) | Designed FTUM φ-attractor |
| CRISPR-Cas9 edit | Targeted B_μ perturbation of φ-archive |
| Metabolic pathway engineering | Rewired B_μ gauge network |
| AI-guided design-build-test | Gradient descent on φ-potential surface |
| Minimal chassis organism | Minimal FTUM attractor supporting a payload |
| Kill-switch / auxotrophy | Attractor stability radius (biosafety bound) |
| DNA data storage | High-fidelity digital φ-archive |
| Directed evolution | Iterative gradient ascent on φ-fitness landscape |
| Circuit noise reduction | B_μ averaging by gene copy redundancy |
| Biomanufacturing TRY metrics | Three independent B_μ flux components |

The convergence of AI and synthetic biology (Groff-Vindman 2026) represents a
φ-field criticality: AI learns the effective φ-potential landscape while SynBio
engineers new attractors within it.  Dual-use biosecurity governance is handled
in the Unitary Pentad (`pentad_scenarios.py`) as a HILS governance scenario.

## What passing tests mean here

> A passing test confirms that the code faithfully implements the stated
> definition (e.g., "disease = φ-deviation from homeostasis fixed point").
>
> It does **NOT** confirm that genetics phenomena are actually governed by
> 5D Kaluza–Klein geometry.

The definition could be wrong.  The test cannot see that.

## What this is useful for

This module is best understood as: *"if you model genetics using this
mathematical structure, here is what follows."*  That may yield useful
frameworks for thinking about complex systems in genetics and synthetic biology.

## What this is NOT

This is not a physics proof about genetics.  There is no single experiment
that would confirm or refute the claim that genetics dynamics are fundamentally
governed by the Walker–Pearson field equations.

## See also

[SEPARATION.md](../../SEPARATION.md) — the full four-tier epistemic map
