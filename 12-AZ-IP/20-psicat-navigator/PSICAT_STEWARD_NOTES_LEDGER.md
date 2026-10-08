# PsiCat Steward Notes Ledger

**Purpose:** keep every steward note given for PsiCat/Merlin work in the repository, so no note is lost between sessions. Entries are append-only. Each records what was said, what was done with it, and what is still open.

**Status:** 🔵 ADJACENT TRACK (Product 20 engineering). Nothing here is a hardgate physics claim.

---

## Note 1 — Non-smooth manifold navigation (received 2026-10-08)

**What the steward said, in substance.** If the manifold PsiCat navigates is not smooth, the engineering playbook changes. Ordinary derivatives fail at creases, punctures and fractured boundaries, so the navigator should be treated as a non-smooth dynamical system with four mechanisms:

1. **Clarke generalised gradients.** At a non-differentiable point, use the set of admissible directions (the subdifferential), not a single gradient, and choose a path that slides along the intersecting facets.
2. **Hybrid automata.** Semantic shifts behave like phase changes. Crossing a boundary switches the discrete state; the unitary constraint acts like an elastic collision that keeps the norm and reflects or refracts the trajectory.
3. **Non-smooth geodesics.** Without smoothness the space behaves like a metric graph or piecewise-linear manifold (compare Alexandrov spaces). Shortest paths run along the ridges, and the creases separate concepts.
4. **Robustness against gradient collapse.** A unitary baseline keeps eigenvalues on the unit circle, so a jagged region can change the direction of data flow but not its magnitude.

The steward asked whether the non-smoothness comes from piecewise-linear constraints in the code, or from modelling the data as a fractured network of discrete pockets. The steward also said "more to come; hold work for all information".

**What was done.** All four mechanisms are implemented and measured in Product 20 (rounds one and two). See [`PSICAT_TOROIDAL_NONSMOOTH_NAVIGATION.md`](PSICAT_TOROIDAL_NONSMOOTH_NAVIGATION.md):
- the Clarke subdifferential of the Z₇₄ circular distance, with explicit descent directions;
- the hybrid automaton over Merlin's real lane, kernel and knowledge-base thresholds;
- exact toroidal geodesics and repository-graph geodesics;
- the unitary operator lab, where the L1 fit stays unitary to about 10⁻¹⁴ at every step.

**Answer to the steward's question, as built.** Both, and in a specific order:
- **Piecewise-linear constraints in the code.** This is the measured part. The non-smoothness Merlin actually has lives in its own decision rules: lane thresholds at 120 and 350 characters, kernel tie-breaks, and the knowledge-base cutoff at 0.15. It also lives in the piecewise-linear torus metric.
- **A fractured network.** This is a modelling choice for retrieval. The repository graph is a discrete metric graph; there is no smooth structure to assume.
- **What the unitary guarantee covers.** Bounded magnitude, nothing more. A badly fitted unitary is still unitary, so the guarantee does not stop Merlin hallucinating. Retrieval quality and the epistemic guard carry that.

## Note 2 — AxiomZero machine index v2 (received 2026-10-08)

**What arrived.** The `axiomzero.machine-index/v2` document for axiomzerospc.org: identity, purpose and authority split, reading instructions, provenance (generator hash, git commit, tree hash), coverage counts, redaction policy, and the SBOM. The text was truncated inside `sbom.packages`. The agents, workflows and function-contract sections were not received.

**What was done.** The received fields were transcribed into [`ox_navigator/engine/data/webspace_provenance_snapshot.json`](ox_navigator/engine/data/webspace_provenance_snapshot.json). Two things were deliberately left out: the phone-shaped sample strings and any mailbox. Merlin audits the snapshot via `merlin_webspace_provenance.py`. The index's own authority split is enforced: version and claims questions route to the repository live registry, and webspace structure questions route to the machine index.

**Open.** Fetch `machine-index.json`, `machine-source.json` and `machine-hashes.json` to audit the agents, workflows and contracts, and to recompute the tree hash.

## Note 3 — Data Provenance page (received 2026-10-08)

**What arrived, verbatim in substance:**
- **Chain hash.** `35ccd2ab4cfad3e47ed1b3f27a2d1392c608b33cbd21ea54b84aeb8d08aa9018`, defined as "SHA-256 of all component hashes concatenated".
- **Component registry.** Eight components, all labelled MIT:
  - AxiomOS Kernel, Unitary Manifold Engine, Pentad Governance Module and ECLIPSA Sentinel, all v33.1
  - Tarot Oracle Engine v1.0.0
  - Three.js v0.171.0, React v18.2.0, Tailwind CSS v3.4.0
- **Timeline.** Six events, with 8-character hash prefixes.
- **Licence summary.** "Physics & math: public domain · Code: copyleft (DPC v1.0 AND AGPL-3.0)". It lists 5 internal components as self-attested and 3 external packages as "audited and hash-verified".

**The steward's instruction.** Take it all in, fully incorporate it into PsiCat/Merlin, be expert, make PsiCat whole, continue all work, and do not lose these notes.

**What was done.** Merlin now runs `getMerlinWebspaceProvenance` (also served at `GET /api/psicat/webspace-provenance`). The findings are in [`PSICAT_WEBSPACE_PROVENANCE.md`](PSICAT_WEBSPACE_PROVENANCE.md). The most important ones:
- Internal components are labelled MIT, which contradicts the project licence (DPC + AGPL-3.0).
- The chain hash cannot be recomputed from what the page publishes.
- The per-component timeline prefixes follow a nibble-decrement pattern (27 of 32 steps) that real SHA-256 output would almost never produce.
- Component versions (v33.1) lag both the webspace's declared v37.7 and the repository's live version.

**Open.** Fixing the page belongs to the webspace codebase, not to this repository. The audit gives the exact fix for each finding, and it clears each finding once the corrected data is supplied (this is tested).

## Note 4 — Trust status, the 12/37 clock, and the full raw intake (received 2026-10-08)

**What the steward said.** The Base44 site is a problem: it is not trustworthy, but it is where things currently live. Two items follow:
1. There is a clock that was built from the ratio 12/37.
2. The steward has found the full raw machine index. It is very large and will arrive in several parts.

The instruction is to keep everything and to hold all work until every part has arrived.

**What this means for the work.** Treat everything that comes from Base44 as an unverified claim. The audit already works this way: nothing the webspace says counts as verified just because the webspace says it. In this repository the clock is the Merlin tick, set by `MERLIN_TICK_NUMERATOR = 12` and `MERLIN_TICK_DENOMINATOR = 37` in `ox_navigator/engine/constants.py` (lines 16–17). The tick also sets `TICK_PHASE_STEP` in `merlin_toroidal_geometry.py`. The webspace's own clock has not been seen yet.

**Raw parts received so far.** These are pieces of `sbom.packages`, in the order they arrived:
- **Part A.** From `@mapbox/whoots-js` 3.1.0 through `@radix-ui/react-scroll-area` 1.2.10.
- **Part B.** From `@esbuild/linux-s390x` 0.25.12 through `@mapbox/vector-tile` 1.3.1.
- **Part C.** From `@babel/generator` 7.29.7 through `@esbuild/linux-riscv64` 0.25.12.
- **Part D.** The machine-index header again, identical to Note 2, through `@babel/core` 7.29.7.

The parts arrived out of order and overlap, so they are not yet a complete list.

**Observation, not yet a finding.** Some entries appear more than once with identical integrity hashes:
- `@radix-ui/react-context` 1.1.3 appears twice.
- `@radix-ui/react-primitive` 2.1.4 appears five times.

The index says "every named array is the COMPLETE list", so repeated identical entries could inflate `package_count` (892). Two explanations fit: the paste repeated those entries, or the generator emits one entry per nested `node_modules` copy. This will be checked once the full list has arrived.

- **Part E.** From `@radix-ui/react-select` 2.2.6 through `@tensorflow/tfjs-backend-cpu` 3.21.0.

**Observations from Part E. These are leads to check, not findings yet.**
- **A likely cause for the inflated direct count.** `@radix-ui/react-slot` 1.2.3 appears 8 times, every copy byte-identical and every copy marked `"direct": true`. There is also one 1.2.4 entry, also marked direct. `package.json` declares `@radix-ui/react-slot` only once. This points to the generator writing one entry per nested `node_modules` copy and inheriting the `direct` flag from the package name instead of from the location. That would explain the earlier finding MI-DIRECT-COUNT: the SBOM says `direct_count` is 111, but `package.json` declares 96. It would also inflate `package_count` (892). To confirm, de-duplicate the full list by name, version and integrity, then count again.
- **One of the two Hippocratic-2.1 packages identified.** It is `@react-leaflet/core` 2.1.0, pulled in by `react-leaflet`.
- **Two TensorFlow versions in the tree.** `@tensorflow/tfjs-backend-cpu` 3.21.0 is present while the declared `@tensorflow/tfjs` is ^4.22.0. It is probably pulled in by `danfojs`, and would mean two TensorFlow.js major versions are bundled. This needs confirming against the dependency edges.

**Status: holding.** No work will start until the steward says the intake is finished.
