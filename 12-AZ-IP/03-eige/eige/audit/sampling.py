# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Publicly verifiable random sampling for audits.

The ceremony follows the widely used SHA-256 "consistent sampler" approach
(R. L. Rivest, *sampler.py*): after results are committed, a public seed of at
least 20 decimal digits is generated in public (e.g. by rolling ten-sided
dice), and draw ``i`` selects ballot position

    1 + (int(SHA-256(f"{seed},{i}")) mod N)

Anyone with the seed and the manifest can recompute every draw.  Sampling is
with replacement; the modulo bias is below 2^-200 for any realistic N.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List, Tuple

from ..model.election import BallotManifest

MIN_SEED_DIGITS = 20
SAMPLE_FORMAT = "eige.sample.v1"


class SamplingError(ValueError):
    """Raised for invalid seeds or sample requests."""


def validate_seed(seed: str) -> str:
    if not isinstance(seed, str) or not seed.isdigit() or not seed.isascii() or len(seed) < MIN_SEED_DIGITS:
        raise SamplingError(f"seed must be a string of at least {MIN_SEED_DIGITS} decimal digits")
    return seed


def draw_position(seed: str, draw_number: int, population: int) -> int:
    digest = hashlib.sha256(f"{seed},{draw_number}".encode("ascii")).digest()
    return 1 + int.from_bytes(digest, "big") % population


@dataclass(frozen=True)
class Draw:
    draw_number: int
    position: int
    batch_id: str
    index_in_batch: int

    def as_dict(self) -> dict:
        return {"draw": self.draw_number, "position": self.position, "batch_id": self.batch_id, "index_in_batch": self.index_in_batch}


def draw_sample(seed: str, manifest: BallotManifest, n: int, start: int = 1) -> List[Draw]:
    """Draws ``start .. start+n-1``; ``start`` > 1 lets an audit escalate without redrawing."""
    validate_seed(seed)
    population = manifest.total_ballots
    if population < 1:
        raise SamplingError("manifest has no ballots")
    if n < 0 or start < 1:
        raise SamplingError("n must be >= 0 and start >= 1")
    out = []
    for i in range(start, start + n):
        pos = draw_position(seed, i, population)
        batch_id, idx = manifest.locate(pos)
        out.append(Draw(i, pos, batch_id, idx))
    return out


def sample_record(seed: str, manifest: BallotManifest, draws: List[Draw]) -> dict:
    return {
        "format": SAMPLE_FORMAT,
        "seed": seed,
        "population": manifest.total_ballots,
        "draws": [d.as_dict() for d in draws],
    }


def verify_sample_record(record: dict, manifest: BallotManifest) -> Tuple[bool, List[str]]:
    """Recompute every draw in a published sample record."""
    problems: List[str] = []
    if record.get("format") != SAMPLE_FORMAT:
        return False, ["unsupported sample format"]
    try:
        seed = validate_seed(record.get("seed"))
    except SamplingError as exc:
        return False, [str(exc)]
    if record.get("population") != manifest.total_ballots:
        problems.append(f"population {record.get('population')} != manifest total {manifest.total_ballots}")
        return False, problems
    for d in record.get("draws", []):
        n = d.get("draw")
        if not isinstance(n, int) or n < 1:
            problems.append(f"invalid draw number {n!r}")
            continue
        pos = draw_position(seed, n, manifest.total_ballots)
        batch_id, idx = manifest.locate(pos)
        if (d.get("position"), d.get("batch_id"), d.get("index_in_batch")) != (pos, batch_id, idx):
            problems.append(f"draw {n}: published {d.get('position')}/{d.get('batch_id')}#{d.get('index_in_batch')}, expected {pos}/{batch_id}#{idx}")
    return not problems, problems
