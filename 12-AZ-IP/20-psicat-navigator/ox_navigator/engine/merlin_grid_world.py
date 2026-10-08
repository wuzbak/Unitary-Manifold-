# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Local, deterministic text/grid event-simulation driver for Merlin/PsiCat.

ADJACENT TRACK (software emulation, not a hardgate physics claim, not a
robotics claim).

This is the "state-to-event translator" that was missing between PsiCat's
pure navigation/routing surfaces and any notion of an environment the
Navigator can act in and observe. It answers the "Decart replacement"
question honestly: instead of 30-FPS pixel diffusion, Merlin gets a bounded
discrete-event grid world, rendered as ASCII text and a structured event
log, with every step fully reproducible from an integer seed.

Why this makes PsiCat/Merlin genuinely *both* a text-and-logic agent and a
toy physics/robotics simulation substrate, rather than two unrelated
products bolted together: the world's boundary conditions are not an
arbitrary new toy geometry. They reuse the exact two boundary rules the
toroidal navigation lane (``merlin_toroidal_geometry``) already uses on the
Z_74 phase lattice:

* the x-axis wraps toroidally (``(x + step) mod width``), the same
  constant-time modular arithmetic as ``wrap`` on the lattice circle;
* the y-axis folds elastically at its two edges, the same "orbifold crease"
  reflection as ``orbifold_fold``/``orbifold_bounce`` on the S¹/Z₂ orbifold,
  generalised here from the fixed modulus 74 to an arbitrary grid height.

So a single mental model — wrap one axis, bounce the other — now drives both
Merlin's repository-routing lattice and this small grid world. That is the
honest sense in which the two "modes" share one substrate; it is not a claim
that either one is a validated physics simulator.

What this is not:

* not a rigid-body or continuous-time physics engine (no forces, no mass,
  no collision response beyond "two agents occupy the same cell");
* not a renderer: there are no pixels, no video, no GPU dependency;
* not a claim about robotics hardware; it is a bounded, local, in-process
  event log a caller can read to decide what an agent "sees" after a move.
"""

from __future__ import annotations

import random
from typing import Any

STATUS_LABEL = "ADJACENT_TRACK"
METHOD = "discrete_grid_event_simulation_v1"

DEFAULT_WIDTH = 12
DEFAULT_HEIGHT = 12
DEFAULT_AGENT_COUNT = 3
DEFAULT_STEPS = 20
MAX_WIDTH = 64
MAX_HEIGHT = 64
MAX_AGENT_COUNT = 26
MAX_STEPS = 200

DIRECTIONS: dict[str, tuple[int, int]] = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
    "STAY": (0, 0),
}
_AGENT_SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_EMPTY_CELL = "."


def _wrap_x(x: int, width: int) -> int:
    """Toroidal wrap on the x-axis: the same modular rule as the lattice's ``wrap``."""
    return int(x) % int(width)


def _fold_y(y: int, height: int) -> int:
    """Elastic orbifold-style fold on the y-axis, generalised to arbitrary height.

    Mirrors ``merlin_toroidal_geometry.orbifold_fold`` (fixed modulus 74,
    fundamental domain ``[0, 37]``): here the modulus is ``2 * (height - 1)``
    and the fundamental domain is ``[0, height - 1]``, so a trajectory
    crossing either edge reflects rather than wraps.
    """
    if height <= 1:
        return 0
    period = 2 * (height - 1)
    k = int(y) % period
    return k if k <= height - 1 else period - k


def _crossed_y_crease(y_before: int, y_after_unfolded: int, height: int) -> list[int]:
    """Report which folded edges (0 and/or height-1) a y-move passed through."""
    if height <= 1:
        return []
    creases: list[int] = []
    lo, hi = sorted((y_before, y_after_unfolded))
    first_multiple = -((-lo) // (height - 1)) if (height - 1) else 0
    multiple = first_multiple
    while (height - 1) * multiple <= hi:
        boundary = (height - 1) * multiple
        if boundary != y_before and lo <= boundary <= hi:
            creases.append(_fold_y(boundary, height))
        multiple += 1
    return creases


def create_world(
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    agent_count: int = DEFAULT_AGENT_COUNT,
    seed: int = 0,
) -> dict[str, Any]:
    """Build a deterministic initial grid world with agents placed by a seeded RNG."""
    width = max(2, min(int(width), MAX_WIDTH))
    height = max(2, min(int(height), MAX_HEIGHT))
    agent_count = max(1, min(int(agent_count), MAX_AGENT_COUNT, width * height))
    rng = random.Random(int(seed))
    occupied: set[tuple[int, int]] = set()
    agents = []
    for i in range(agent_count):
        while True:
            x, y = rng.randrange(width), rng.randrange(height)
            if (x, y) not in occupied:
                occupied.add((x, y))
                break
        agents.append({"id": i, "symbol": _AGENT_SYMBOLS[i % len(_AGENT_SYMBOLS)], "x": x, "y": y})
    return {
        "status": STATUS_LABEL,
        "method": METHOD,
        "width": width,
        "height": height,
        "tick": 0,
        "seed": int(seed),
        "agents": agents,
    }


def step_world(world: dict[str, Any], actions: dict[int, str] | None, *, rng: random.Random) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Advance the world by one tick; returns the new world and a list of events.

    ``actions`` maps agent id to a direction in ``DIRECTIONS``; an agent with
    no explicit action takes a seeded random step. Unknown directions and
    out-of-range agent ids are ignored (fail-closed: no action, no crash).
    """
    width, height = int(world["width"]), int(world["height"])
    actions = dict(actions or {})
    events: list[dict[str, Any]] = []
    new_agents = []
    next_positions: dict[int, tuple[int, int]] = {}
    for agent in world["agents"]:
        agent_id = int(agent["id"])
        direction = actions.get(agent_id)
        if direction not in DIRECTIONS:
            direction = rng.choice(list(DIRECTIONS.keys()))
        dx, dy = DIRECTIONS[direction]
        x_before, y_before = int(agent["x"]), int(agent["y"])
        x_unwrapped = x_before + dx
        y_unfolded = y_before + dy
        x_after = _wrap_x(x_unwrapped, width)
        y_after = _fold_y(y_unfolded, height)
        if x_unwrapped < 0 or x_unwrapped >= width:
            events.append({"kind": "wrap", "agent_id": agent_id, "axis": "x"})
        creases = _crossed_y_crease(y_before, y_unfolded, height)
        for crease in creases:
            events.append({"kind": "crease_impact", "agent_id": agent_id, "axis": "y", "crease": crease})
        next_positions[agent_id] = (x_after, y_after)
        new_agents.append({**agent, "x": x_after, "y": y_after, "direction": direction})
    occupancy: dict[tuple[int, int], list[int]] = {}
    for agent_id, pos in next_positions.items():
        occupancy.setdefault(pos, []).append(agent_id)
    for pos, ids in occupancy.items():
        if len(ids) > 1:
            events.append({"kind": "collision", "position": list(pos), "agent_ids": sorted(ids)})
    new_world = {**world, "tick": int(world["tick"]) + 1, "agents": new_agents}
    return new_world, events


def render_ascii(world: dict[str, Any]) -> str:
    """Render the world as a plain-text grid (no pixels, no colour, no GPU)."""
    width, height = int(world["width"]), int(world["height"])
    grid = [[_EMPTY_CELL for _ in range(width)] for _ in range(height)]
    for agent in world["agents"]:
        x, y = int(agent["x"]), int(agent["y"])
        if 0 <= y < height and 0 <= x < width:
            grid[y][x] = str(agent["symbol"])
    return "\n".join("".join(row) for row in grid)


def run_grid_world_episode(
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    agent_count: int = DEFAULT_AGENT_COUNT,
    steps: int = DEFAULT_STEPS,
    seed: int = 0,
    actions: dict[int, list[str]] | None = None,
) -> dict[str, Any]:
    """Run a bounded, deterministic grid-world episode and report state and events.

    ``actions`` optionally maps agent id to an explicit per-step direction
    list; any step beyond the provided list (or any agent without an entry)
    falls back to the seeded random walk, so the episode is always fully
    reproducible from ``seed`` alone when ``actions`` is omitted.
    """
    steps = max(0, min(int(steps), MAX_STEPS))
    world = create_world(width=width, height=height, agent_count=agent_count, seed=seed)
    rng = random.Random(int(seed) + 1)
    actions = actions or {}
    event_log: list[dict[str, Any]] = []
    for step_index in range(steps):
        step_actions = {
            agent_id: directions[step_index]
            for agent_id, directions in actions.items()
            if step_index < len(directions)
        }
        world, events = step_world(world, step_actions, rng=rng)
        for event in events:
            event_log.append({"tick": world["tick"], **event})
    counts: dict[str, int] = {}
    for event in event_log:
        counts[event["kind"]] = counts.get(event["kind"], 0) + 1
    return {
        "status": STATUS_LABEL,
        "method": METHOD,
        "seed": int(seed),
        "steps_run": steps,
        "world": world,
        "ascii_render": render_ascii(world),
        "events": event_log,
        "event_counts": counts,
        "boundary_rules": {
            "x_axis": "toroidal_wrap (same rule as merlin_toroidal_geometry.wrap)",
            "y_axis": "orbifold_elastic_fold (same rule as merlin_toroidal_geometry.orbifold_fold, generalised height)",
        },
    }


__all__ = [
    "DEFAULT_AGENT_COUNT",
    "DEFAULT_HEIGHT",
    "DEFAULT_STEPS",
    "DEFAULT_WIDTH",
    "DIRECTIONS",
    "MAX_AGENT_COUNT",
    "MAX_HEIGHT",
    "MAX_STEPS",
    "MAX_WIDTH",
    "METHOD",
    "STATUS_LABEL",
    "create_world",
    "render_ascii",
    "run_grid_world_episode",
    "step_world",
]
