# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Sprint BA pillar dependency graph helpers."""
from __future__ import annotations

from collections import deque

PILLAR_DEPENDENCY_GRAPH: dict[int, list[int]] = {
    837: [],
    838: [],
    839: [837],
    840: [837, 839],
    841: [840],
    842: [838, 839, 840, 841],
    843: [840],
    844: [843],
    845: [],
    846: [842, 843, 844],
    847: [],
    848: [],
    849: [846],
    850: [849],
    851: [],
    852: [849, 850],
    853: [852],
    854: [853],
    855: [852, 853, 854],
    856: [853, 854, 855],
    857: [],
    858: [842, 846, 852, 856],
    859: [858],
    860: [859],
}

__all__ = [
    'PILLAR_DEPENDENCY_GRAPH',
    'get_dependencies',
    'get_dependents',
    'find_critical_path',
]


def get_dependencies(pillar_id: int) -> list[int]:
    """Return direct dependencies for a pillar."""
    return list(PILLAR_DEPENDENCY_GRAPH.get(pillar_id, []))


def get_dependents(pillar_id: int) -> list[int]:
    """Return reverse dependencies for a pillar."""
    dependents = [node for node, deps in PILLAR_DEPENDENCY_GRAPH.items() if pillar_id in deps]
    return sorted(dependents)


def find_critical_path(start: int, end: int) -> list[int]:
    """Find the shortest dependency-forward path from *start* to *end*."""
    if start == end:
        return [start]
    if start not in PILLAR_DEPENDENCY_GRAPH or end not in PILLAR_DEPENDENCY_GRAPH:
        return []

    queue: deque[list[int]] = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        for dependent in get_dependents(node):
            if dependent in seen:
                continue
            next_path = path + [dependent]
            if dependent == end:
                return next_path
            seen.add(dependent)
            queue.append(next_path)
    return []
