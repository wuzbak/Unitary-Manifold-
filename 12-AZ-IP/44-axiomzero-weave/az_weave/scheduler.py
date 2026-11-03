# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Bounded read/computation DAG; effectful actions use the separate executor."""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Any, Mapping


@dataclass(frozen=True)
class Output:
    state: str
    value: Any = None
    blocked_by: tuple[str, ...] = ()
    error: str | None = None

    def as_dict(self) -> dict:
        return {"state": self.state, "value": self.value,
                "blocked_by": list(self.blocked_by), "error": self.error}


@dataclass(frozen=True)
class Node:
    name: str
    dependencies: tuple[str, ...]
    worker: Callable[[Mapping[str, Output]], Any] = field(repr=False)


def run_dag(nodes: list[Node], *, max_workers: int = 3) -> dict[str, Output]:
    if type(max_workers) is not int or not 1 <= max_workers <= 5:
        raise ValueError("max_workers must be between 1 and 5")
    if not 1 <= len(nodes) <= 32 or len({node.name for node in nodes}) != len(nodes):
        raise ValueError("DAG requires 1..32 unique nodes")
    names = {node.name for node in nodes}
    if any(set(node.dependencies) - names for node in nodes):
        raise ValueError("unknown prerequisite")
    seen: set[str] = set()
    while True:
        ready = {node.name for node in nodes if set(node.dependencies) <= seen}
        expanded = seen | ready
        if expanded == seen:
            break
        seen = expanded
    if seen != names:
        raise ValueError("dependency cycle")
    remaining = {node.name: node for node in nodes}
    outputs: dict[str, Output] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        running = {}
        while remaining or running:
            for name, node in list(remaining.items()):
                if not set(node.dependencies) <= outputs.keys():
                    continue
                blocked = tuple(dep for dep in node.dependencies if outputs[dep].state != "OK")
                if blocked:
                    outputs[name] = Output("BLOCKED", blocked_by=blocked)
                elif len(running) < max_workers:
                    inputs = MappingProxyType({dep: deepcopy(outputs[dep]) for dep in node.dependencies})
                    running[pool.submit(node.worker, inputs)] = name
                else:
                    continue
                del remaining[name]
            if running:
                finished, _ = wait(running, return_when=FIRST_COMPLETED)
                for future in finished:
                    name = running.pop(future)
                    try:
                        outputs[name] = Output("OK", future.result())
                    except Exception as exc:
                        outputs[name] = Output("FAILED", error=f"{type(exc).__name__}: {exc}")
    return {node.name: outputs[node.name] for node in nodes}
