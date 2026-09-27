# MaleCNS Connectome Bridge — Pillar 1129

**Status:** 🔵 ADJACENT TRACK — empirical connectome bridge, not a hardgate physics claim.

## What this imports

This lane uses the public **MaleCNS v1.0** fruit-fly connectome release as a real
external data surface for the repository's neuroscience work. The imported
benchmark is intentionally compact and reproducible:

- dataset identity: `male-cns:v1.0`
- dataset UUID: `4b2087c0fbe046bfaf0d60bc970e3e5d`
- public scope: adult male *Drosophila melanogaster* CNS
- public headline scale: ~166,700 neurons and ~125 million synapses
- imported benchmark panel: 7 public neuron-type pages with deterministic
  summaries and provenance hashes

The committed benchmark panel lives at:

- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/data/malecns/benchmark_panel.json`

The parser/test fixtures live at:

- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/tests/fixtures/malecns/`

## Why this matters

Before this pillar, the repository already had an extensive brain lane, but most
of it was either conceptual correspondence, reduced phenomenology, or disorder
classification. This pillar adds a stricter surface: **public connectome-derived
observables from a whole-CNS dataset**.

That does not prove the broader brain-universe story. It does something more
honest and more useful: it forces the language of topology, directionality,
bridge structure, and coupling to touch a real wiring map.

## What was actually measured

The pillar does not vendor the full MaleCNS raw connectome. Instead it extracts
compact summaries from real public neuron-type pages and computes:

- upstream partner counts
- downstream partner counts
- total input and output synapse mass
- reciprocal-partner overlap
- top-partner concentration
- neurotransmitter diversity
- ROI balance across optic-lobe, central-brain, and VNC/motor surfaces
- cross-domain bridge signatures

## Imported benchmark panel

The committed panel spans seven distinct functional roles:

- `LPLC2` — optic projection / looming-associated visual integration surface
- `LC4` — optic feature-detector surface
- `EPG` — central-complex compass surface
- `AN01B004` — ascending VNC-to-brain bridge surface
- `DNa02` — descending brain-to-motor command surface
- `MN5` — motor-output surface
- `5-HTPLP01` — neuromodulatory broadcast surface

This is not the whole fly. It is a deliberate, auditable benchmark slice that
covers sensory, integrative, descending, ascending, motor, and modulatory roles.

## What we found

From the committed benchmark panel:

1. **The optic lane dominates throughput in this slice.** `LPLC2` carries the
   largest benchmark input mass and the largest benchmark output mass.
2. **Reciprocity is high, not negligible.** Partner-set overlap is substantial
   across the panel; `LC4` is the most reciprocal imported type.
3. **Bridge neurons are explicit.** `AN01B004` and `DNa02` both carry nonzero
   central-brain and VNC/motor load, making them useful reduced surfaces for
   brain↔nerve-cord coupling analysis.
4. **The central-complex benchmark is not a narrowly single-channel relay.**
   In this panel, `EPG` has the highest downstream neurotransmitter entropy.
5. **The fly CNS gives us a tractable whole-system bridge.** Even this compact
   panel already separates optic-heavy, central-complex, bridge, motor, and
   neuromodulatory roles in a way the existing prose-only brain lane could not.

## What this does **not** establish

This pillar does **not** establish:

- a proof that consciousness is a 5D geometric fact
- a proof that the MaleCNS connectome validates the Unitary Manifold
- a proof that any benchmark neuron type is an ontological analog of a UM field
- a first-principles derivation of cognition from connectome structure alone

The correct interpretation is narrower:

> the repository now has a real, public, executable connectome benchmark that
> can pressure-test its neuroscience language against empirical wiring data.

## Interfaces

Primary public interfaces tracked by this pillar:

- neuPrint dataset: `male-cns:v1.0`
- Cell Type Explorer repo: `https://github.com/reiserlab/celltype-explorer-drosophila-male-cns`
- public type-index snapshot: `https://raw.githubusercontent.com/reiserlab/celltype-explorer-drosophila-male-cns/main/data/neurons.json`
- Neuroglancer compartment source: `precomputed://gs://flyem-male-cns/rois/malecns-major-compartments-v2`

## Repository surface

Implementation:

- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/src/core/pillar1129_malecns_connectome_empirical_bridge.py`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/tests/test_pillar1129_malecns_connectome_empirical_bridge.py`

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.  
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
