# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for the local text/grid event-simulation driver (ADJACENT TRACK).

Covers: boundary-rule correctness (toroidal wrap on x, orbifold fold on y),
event emission (wrap, crease_impact, collision), full episode determinism,
input clamping, ASCII rendering, and tool/server wiring.
"""

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine import merlin_grid_world as grid
from ox_navigator.engine.merlin_tools import _tool_manifest, route_tool
from ox_navigator.engine.merlin_toroidal_geometry import orbifold_fold, wrap

# --- boundary-rule correctness -----------------------------------------------------------


def test_wrap_x_matches_lattice_wrap_rule() -> None:
    for x in (-3, -1, 0, 5, 11, 12, 23):
        width = 12
        assert grid._wrap_x(x, width) == x % width


def test_fold_y_matches_lattice_orbifold_fold_shape() -> None:
    # On the Z_74 lattice, orbifold_fold has period 74 and fixed points {0, 37}.
    # _fold_y must reproduce the same qualitative shape for an arbitrary height:
    # period 2*(height-1) and fixed points {0, height-1}.
    height = 6
    period = 2 * (height - 1)
    for offset in range(period):
        folded = grid._fold_y(offset, height)
        assert 0 <= folded <= height - 1
    assert grid._fold_y(0, height) == 0
    assert grid._fold_y(height - 1, height) == height - 1
    assert grid._fold_y(height, height) == height - 2  # one step past the far edge reflects back


def test_fold_y_is_periodic() -> None:
    height = 8
    period = 2 * (height - 1)
    for offset in (0, 3, 7, 15, -4, -11):
        assert grid._fold_y(offset, height) == grid._fold_y(offset + period, height)


def test_lattice_reference_rules_are_unchanged() -> None:
    # Sanity: the lattice this module claims to mirror still behaves as documented.
    assert wrap(-1) == 73
    assert orbifold_fold(74) == 0
    assert orbifold_fold(37) == 37


# --- world construction and bounds -------------------------------------------------------


def test_create_world_clamps_out_of_range_inputs() -> None:
    world = grid.create_world(width=1000, height=1000, agent_count=1000, seed=1)
    assert world["width"] == grid.MAX_WIDTH
    assert world["height"] == grid.MAX_HEIGHT
    assert len(world["agents"]) == grid.MAX_AGENT_COUNT
    assert world["status"] == "ADJACENT_TRACK"


def test_create_world_places_agents_without_overlap() -> None:
    world = grid.create_world(width=10, height=10, agent_count=8, seed=3)
    positions = [(agent["x"], agent["y"]) for agent in world["agents"]]
    assert len(positions) == len(set(positions))


def test_create_world_is_deterministic_given_seed() -> None:
    a = grid.create_world(width=10, height=10, agent_count=5, seed=99)
    b = grid.create_world(width=10, height=10, agent_count=5, seed=99)
    assert a == b


# --- events: wrap, crease_impact, collision ----------------------------------------------


def test_step_world_emits_wrap_event_at_x_seam() -> None:
    world = {"width": 4, "height": 4, "tick": 0, "agents": [{"id": 0, "symbol": "A", "x": 3, "y": 1}]}
    import random

    new_world, events = grid.step_world(world, {0: "E"}, rng=random.Random(0))
    assert new_world["agents"][0]["x"] == 0
    assert any(e["kind"] == "wrap" for e in events)


def test_step_world_emits_crease_impact_at_y_edge() -> None:
    # Starting one cell away from the edge and stepping into it reproduces the
    # same crossing the lattice's own orbifold_bounce() records as an impact
    # (a move that *starts* exactly on the crease is not itself a new crossing).
    world = {"width": 4, "height": 4, "tick": 0, "agents": [{"id": 0, "symbol": "A", "x": 1, "y": 1}]}
    import random

    new_world, events = grid.step_world(world, {0: "N"}, rng=random.Random(0))
    assert new_world["agents"][0]["y"] == 0
    assert any(e["kind"] == "crease_impact" and e["crease"] == 0 for e in events)


def test_step_world_emits_collision_when_agents_share_a_cell() -> None:
    world = {
        "width": 4,
        "height": 4,
        "tick": 0,
        "agents": [
            {"id": 0, "symbol": "A", "x": 0, "y": 0},
            {"id": 1, "symbol": "B", "x": 2, "y": 0},
        ],
    }
    import random

    _, events = grid.step_world(world, {0: "E", 1: "W"}, rng=random.Random(0))
    collisions = [e for e in events if e["kind"] == "collision"]
    assert len(collisions) == 1
    assert sorted(collisions[0]["agent_ids"]) == [0, 1]


def test_step_world_ignores_unknown_direction_and_falls_back_to_rng() -> None:
    import random

    world = {"width": 4, "height": 4, "tick": 0, "agents": [{"id": 0, "symbol": "A", "x": 1, "y": 1}]}
    new_world, _ = grid.step_world(world, {0: "NOT_A_DIRECTION"}, rng=random.Random(0))
    assert new_world["agents"][0]["direction"] in grid.DIRECTIONS


# --- full episode: determinism, rendering, explicit actions -------------------------------


def test_episode_is_deterministic_given_seed() -> None:
    a = grid.run_grid_world_episode(width=6, height=6, agent_count=3, steps=15, seed=42)
    b = grid.run_grid_world_episode(width=6, height=6, agent_count=3, steps=15, seed=42)
    assert a == b


def test_episode_differs_across_seeds() -> None:
    a = grid.run_grid_world_episode(width=6, height=6, agent_count=3, steps=15, seed=1)
    b = grid.run_grid_world_episode(width=6, height=6, agent_count=3, steps=15, seed=2)
    assert a != b


def test_episode_respects_explicit_actions() -> None:
    result = grid.run_grid_world_episode(
        width=6, height=6, agent_count=1, steps=3, seed=1, actions={0: ["E", "E", "E"]},
    )
    agents = result["world"]["agents"]
    assert len(agents) == 1


def test_episode_clamps_steps() -> None:
    result = grid.run_grid_world_episode(width=4, height=4, agent_count=1, steps=10_000, seed=0)
    assert result["steps_run"] == grid.MAX_STEPS


def test_ascii_render_is_plain_text_with_expected_shape() -> None:
    result = grid.run_grid_world_episode(width=5, height=4, agent_count=2, steps=0, seed=0)
    rendered = result["ascii_render"]
    assert isinstance(rendered, str)
    lines = rendered.split("\n")
    assert len(lines) == 4
    assert all(len(line) == 5 for line in lines)


def test_boundary_rules_are_reported() -> None:
    result = grid.run_grid_world_episode(width=5, height=5, agent_count=1, steps=1, seed=0)
    assert "toroidal_wrap" in result["boundary_rules"]["x_axis"]
    assert "orbifold" in result["boundary_rules"]["y_axis"]


def test_status_label_is_adjacent_track_not_hardgate() -> None:
    result = grid.run_grid_world_episode(width=4, height=4, agent_count=1, steps=1, seed=0)
    assert result["status"] == "ADJACENT_TRACK"


# --- tool and server wiring ---------------------------------------------------------------


def test_tool_manifest_lists_get_merlin_grid_world() -> None:
    manifest = _tool_manifest()
    names = {entry["name"]: entry for entry in manifest["functions"]}
    assert "getMerlinGridWorld" in names
    assert "args_schema" in names["getMerlinGridWorld"]


def test_route_tool_runs_grid_world_episode() -> None:
    payload = route_tool("getMerlinGridWorld", {"width": 5, "height": 5, "agent_count": 2, "steps": 4, "seed": 7})
    assert payload["ok"] is True
    data = payload["result"]["data"]
    assert data["status"] == "ADJACENT_TRACK"
    assert "ascii_render" in data
    assert "events" in data


def test_route_tool_grid_world_defaults_when_args_missing() -> None:
    payload = route_tool("getMerlinGridWorld", {})
    assert payload["ok"] is True
    assert payload["result"]["data"]["world"]["width"] == grid.DEFAULT_WIDTH


# --- navigation-driven bridge --------------------------------------------------------------


def test_directions_from_toroidal_code_is_deterministic_and_bounded() -> None:
    code = [19, 38, 46, 31, 24, 0, 73, 1]
    directions = grid.directions_from_toroidal_code(code)
    assert len(directions) == len(code)
    assert all(direction in grid.DIRECTIONS for direction in directions)
    assert directions == grid.directions_from_toroidal_code(code)


def test_navigation_driven_episode_is_deterministic_given_query() -> None:
    a = grid.run_navigation_driven_episode("winding number five seven braided compactification")
    b = grid.run_navigation_driven_episode("winding number five seven braided compactification")
    assert a == b


def test_navigation_driven_episode_differs_across_queries() -> None:
    a = grid.run_navigation_driven_episode("winding number five seven braided compactification")
    b = grid.run_navigation_driven_episode("totally unrelated topic about something else entirely")
    assert a != b


def test_navigation_driven_episode_reports_navigation_source() -> None:
    result = grid.run_navigation_driven_episode("holographic boundary entropy")
    source = result["navigation_source"]
    assert source["query"] == "holographic boundary entropy"
    assert "primary_facet" in source
    assert "toroidal_address_code" in source
    assert len(source["directions_derived"]) == len(source["toroidal_address_code"])
    assert result["method"] == grid.NAVIGATION_DRIVEN_METHOD


def test_navigation_driven_episode_steps_match_code_length() -> None:
    result = grid.run_navigation_driven_episode("braided Chern-Simons level")
    assert result["steps_run"] == len(result["navigation_source"]["toroidal_address_code"])


def test_tool_manifest_lists_get_merlin_navigation_driven_grid_world() -> None:
    manifest = _tool_manifest()
    names = {entry["name"]: entry for entry in manifest["functions"]}
    assert "getMerlinNavigationDrivenGridWorld" in names
    assert "args_schema" in names["getMerlinNavigationDrivenGridWorld"]


def test_route_tool_runs_navigation_driven_grid_world() -> None:
    payload = route_tool("getMerlinNavigationDrivenGridWorld", {"query": "winding number five seven"})
    assert payload["ok"] is True
    data = payload["result"]["data"]
    assert data["status"] == "ADJACENT_TRACK"
    assert "navigation_source" in data


def test_route_tool_navigation_driven_grid_world_requires_query() -> None:
    assert route_tool("getMerlinNavigationDrivenGridWorld", {})["ok"] is False


def test_server_exposes_grid_world_endpoints() -> None:
    import ox_navigator.app.server as server_module

    source = Path(server_module.__file__).read_text(encoding="utf-8")
    assert "/api/psicat/grid-world" in source
    assert "/api/psicat/navigation-grid-world" in source
