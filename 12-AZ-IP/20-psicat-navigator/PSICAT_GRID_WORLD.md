# PsiCat Grid World — a text/grid event-simulation driver

Status: 🔵 **ADJACENT TRACK** (software emulation). Not a hardgate physics
claim. Not a robotics claim. Not a rendering/video product.

## Why this exists

A public critique of PsiCat Navigator argued that, by deliberately not
depending on a pixel-diffusion product (Decart) or a hosted model vendor
(Anthropic), PsiCat was missing three bridging layers between its abstract
routing math and a working, embodied agent: a token-to-manifold embedder, an
execution harness, and a "state-to-event translator" standing in for live
pixel simulation.

The first gap was closed by `merlin_semantic_embedder.py` (a local, offline,
deterministic hashed n-gram projector — see `PSICAT_SEMANTIC_EMBEDDER.md`).
The second was already present: `merlin_local_execution.py` is a fail-closed,
allowlisted, token-gated local command harness.

This document covers the third: a lightweight, local, text-only grid world
that gives an agent something to act in and observe, without ever rendering
a pixel.

## What it is

`ox_navigator/engine/merlin_grid_world.py` implements a bounded discrete-time,
discrete-space grid:

* **Agents** occupy integer `(x, y)` cells on a `width × height` grid
  (defaults `12 × 12`, hard-capped at `64 × 64`, at most 26 agents).
* **Actions** are one of `N`, `S`, `E`, `W`, `STAY` per agent per tick. Any
  agent without an explicit action for that tick takes a step chosen by a
  seeded `random.Random`, so an entire episode — agent placement, every
  action, every event — is fully reproducible from one integer `seed`.
* **Boundary conditions** are not an arbitrary new toy geometry. They reuse
  the exact two rules the toroidal navigation lane
  (`merlin_toroidal_geometry.py`) already uses on the Z₇₄ phase lattice:
  * the **x-axis wraps toroidally**: `(x + step) mod width`, the same
    constant-time modular rule as `wrap()` on the lattice circle;
  * the **y-axis folds elastically** at its two edges: the same "orbifold
    crease" reflection as `orbifold_fold()` / `orbifold_bounce()` on the
    S¹/Z₂ orbifold, generalised from the fixed modulus 74 to an arbitrary
    grid height.
* **Events** are emitted, not inferred by the caller: `wrap` (an agent
  crossed the toroidal x seam), `crease_impact` (an agent's unfolded y
  trajectory passed through an elastic edge), and `collision` (two or more
  agents ended the tick on the same cell).
* **Rendering** is `render_ascii()`: one character per agent on a plain-text
  grid. No colour, no pixels, no video, no GPU dependency.

`run_grid_world_episode(width, height, agent_count, steps, seed, actions)` is
the single deterministic entry point: it builds the world, steps it `steps`
times, and returns the final world, the ASCII render, the full event log,
per-kind event counts, and an explicit `boundary_rules` field naming which
existing lattice rule backs each axis.

## Why this is the honest sense in which PsiCat/Merlin is "both"

The user's framing was that PsiCat/Merlin should be **both** a text-and-logic
navigation agent **and** a (toy) physics/robotics simulation substrate, not
two unrelated products stitched together under one name. Sharing the same
two boundary primitives (modular wrap, elastic fold) between the navigation
lattice and this grid world is the literal, checkable way that claim is
true here:

* the navigation lane uses `wrap()` / `orbifold_fold()` on a *fixed* Z₇₄
  lattice to route queries and detect creases in conversational state;
* the grid world uses the *same two rules*, generalised to arbitrary grid
  dimensions, to bound an agent's physical position and detect boundary
  events.

One mental model — wrap one axis, bounce the other — now drives both modes.
That is a real, auditable architectural fact (see
`tests/test_merlin_grid_world.py`), not a rebrand.

## What this explicitly is not

* **Not a physics engine.** There is no mass, force, velocity, momentum, or
  continuous-time integration. "Collision" means two agents share a cell at
  the end of a tick; there is no collision response.
* **Not a robotics claim.** Nothing here drives real actuators, sensors, or
  hardware. It is an in-process, local data structure.
* **Not a Decart replacement in the rendering sense.** It does not produce
  video or images. It produces a short ASCII string and a JSON event list —
  deliberately, to stay local, deterministic, and cheap, trading visual
  fidelity for auditability.
* **Not a hardgate physics claim.** It borrows the *software* boundary rules
  already implemented in the ADJACENT-TRACK toroidal navigation lane; it
  makes no claim about the 5D Kaluza-Klein metric, `src/core/`, or any
  hardgated pillar.

## The navigation-driven bridge

The honesty ledger above establishes that navigation and simulation share
one geometric *substrate* (the same wrap/fold rules). `run_navigation_driven_episode`
goes one step further and closes an actual *data* loop between them,
answering the second gap in the original critique directly: "a continuous
runtime loop that reads the Navigator's geometric output state and
translates it into operational actions."

`merlin_toroidal_router.build_toroidal_navigation_packet(query)` already
assigns every query a deterministic point on the Z₇₄ lattice —
`toroidal_address.code`, a list of integers in `[0, 73]`. `directions_from_toroidal_code`
reads that code out, one integer per tick, and maps each value's residue
modulo 5 onto one of the five grid actions (`N`, `S`, `E`, `W`, `STAY`).
`run_navigation_driven_episode(query, ...)` calls the Navigator's existing,
unchanged packet builder, derives the direction sequence from its code, and
runs that sequence through the same `run_grid_world_episode` used above.

No new or parallel randomness is introduced: the same query that the
Navigator would route to a lane/kernel/KB facet also produces this grid
world's trajectory, deterministically, from the Navigator's own output. The
routing decision and the simulated trajectory are two readings of one
computation, not two separately-tuned subsystems. The response includes a
`navigation_source` field recording the query, the Navigator's primary
facet, whether the query sat on a crease, the raw toroidal code, and the
directions derived from it, so the link is auditable in every response
rather than merely asserted in this document.

## API surface

* Tool: `getMerlinGridWorld(width?, height?, agent_count?, steps?, seed?)`
* Endpoint: `GET /api/psicat/grid-world?width=&height=&agent_count=&steps=&seed=`
* Tool: `getMerlinNavigationDrivenGridWorld(query, width?, height?, agent_count?, seed?, top_k?)`
* Endpoint: `GET /api/psicat/navigation-grid-world?query=&width=&height=&agent_count=&seed=&top_k=`
* Module: `ox_navigator.engine.merlin_grid_world`

All parameters are optional integers; out-of-range values are clamped
(`width`/`height` to `[2, 64]`, `agent_count` to `[1, min(26, width*height)]`,
`steps` to `[0, 200]`) rather than rejected, so the endpoint always returns a
bounded, safe response.

## Honesty ledger

| Claim | Status | Evidence |
| --- | --- | --- |
| Every episode is exactly reproducible from `seed` alone | Verified | `tests/test_merlin_grid_world.py::test_episode_is_deterministic_given_seed` |
| x-axis and y-axis boundary conditions match the existing lattice rules, generalised | Verified by construction | `_wrap_x`/`_fold_y` mirror `merlin_toroidal_geometry.wrap`/`orbifold_fold`; see module docstring |
| Output is text-only (no pixels, no binary image data) | Verified | `render_ascii` returns `str`; tested in `test_merlin_grid_world.py` |
| All inputs are bounded (no unbounded CPU/memory from the endpoint) | Verified | `MAX_WIDTH`/`MAX_HEIGHT`/`MAX_AGENT_COUNT`/`MAX_STEPS` enforced in `create_world`/`run_grid_world_episode` |
| This module is a physics or robotics simulator in any validated sense | **Not claimed** | Explicitly disclaimed above and in the module docstring |
| The navigation-driven bridge reuses the Navigator's existing packet builder unchanged, with no parallel randomness | Verified | `tests/test_merlin_grid_world.py::test_navigation_driven_episode_is_deterministic_given_query` |
