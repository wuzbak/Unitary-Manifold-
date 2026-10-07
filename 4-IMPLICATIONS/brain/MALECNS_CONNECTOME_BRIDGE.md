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

- `data/malecns/benchmark_panel.json`

The parser/test fixtures live at:

- `tests/fixtures/malecns/`

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

- `src/core/pillar1129_malecns_connectome_empirical_bridge.py`
- `tests/test_pillar1129_malecns_connectome_empirical_bridge.py`

### Bounded offline empirical reproduction

Run `python -m src.neuroscience.empirical_benchmark` to reproduce **published
source-table summaries**, not an experiment or full paper replication.
`tests/test_neuroscience_empirical_benchmark.py` independently counts integer
`∑ connections` attributes and partner labels in the already committed LPLC2
extracts; expected counts are not read from the panel JSON.

The executable verifies SHA-256 hashes of all three extracts before parsing.
It reproduces 536 upstream and 692 downstream partner types, 350,542 input
and 182,982 output synapses, 440 reciprocal types in a union of 788, and eight
ROI rows. Top-five displayed partner masses are 127,817 input and 86,491 output
synapses. Both directions contain 46,178 same-type LPLC2 connections; these
aggregate across neurons and **must not be called individual-neuron autapses**.
ROI totals are not summed because ROI overlap can double-count synapses.

An exact downstream weight-label permutation control assigns each of the 692
displayed weights to the LPLC2 label once, preserving partner count and total
mass. Observed same-type output share is 46,178 / 182,982 (25.2364%); mean
shuffled share is 1 / 692 (0.1445%), with one assignment at least as large as
observed. This is a descriptive label-sensitivity control, **not a biological
p-value**: exchangeable type labels are not established by these data.

The full-page hash in the panel is recorded provenance, not verified by table
extracts; local hashes establish byte integrity, not independent authenticity.
No new external dataset is copied or license inferred from public access.
The default run is offline and covers only this displayed one-type slice.
Experimental replication, full paper replication, and **Gardner activity-space
topology reproduction remain pending**: no activity data or full connectivity
simulation is supplied, and no UM physics validation is claimed.

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.  
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
