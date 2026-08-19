# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/chaos_injection.py — Chaos Injection Module for Adversarial Stress-Testing
=====================================================================================

The ChaosInjector wraps a CountyNode and introduces controlled adversarial
perturbations into the ballot ingestion stream.  Its purpose is to validate
that the EIGE engine:

  1. Survives noisy, ambiguous, or malformed input without silent corruption
  2. Detects replay attacks (duplicate ballot_id sequences)
  3. Fires the FreedomFloorViolation kill-switch before variance is suppressed
     below the `freedom_floor` parameter
  4. Maintains metric closure integrity across all noise scenarios

Design principles
-----------------
- The math core (ChernSimonChain, MetricClosure) is NEVER modified.
- All perturbations happen *before* data enters CountyNode.ingest_ballot().
- Every perturbation event is recorded in `injection_log` for full auditability.
- The FreedomFloorViolation kill-switch is a hard stop — it raises an exception
  rather than returning a failure flag, so callers cannot silently ignore it.

Noise modes
-----------
  NONE         — no perturbation (baseline passthrough)
  BITFLIP      — randomly flip one integer component in the selection vector
  ZERO_OUT     — replace the entire selection vector with zeros
  RANDOMIZE    — replace the entire selection vector with uniform random ints
  STOCHASTIC   — use a mark_confidence float to probabilistically round values

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

from .constants import (
    CHAOS_NOISE_BUDGET_DEFAULT,
    FREEDOM_FLOOR,
    FREEDOM_FLOOR_MIN_BALLOTS,
    K_CS,
)
from .county_node import BallotRecord, CountyNode


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class FreedomFloorViolation(Exception):
    """
    Raised when the ChaosInjector detects that the system is suppressing
    participation variance below the freedom_floor threshold.

    This is the explicit kill-switch that prevents the engine from "stabilising"
    φ_eff by silently zeroing out or homogenising ballot inputs — a mathematical
    optimisation that destroys democratic representation.

    Attributes
    ----------
    participating_fraction : float
        Fraction of counties/batches that contributed non-trivially at the
        moment the violation was detected.
    freedom_floor : float
        The configured minimum fraction that must be non-trivial.
    injection_log : list[dict]
        Full audit trail of injection events up to the violation point.
    """

    def __init__(
        self,
        participating_fraction: float,
        freedom_floor: float,
        injection_log: List[dict],
    ) -> None:
        self.participating_fraction = participating_fraction
        self.freedom_floor = freedom_floor
        self.injection_log = injection_log
        super().__init__(
            f"FreedomFloorViolation: participating fraction {participating_fraction:.3f} "
            f"is below freedom_floor {freedom_floor:.3f}. "
            f"The engine was suppressing participation variance. "
            f"Injection log contains {len(injection_log)} events."
        )


# ---------------------------------------------------------------------------
# Noise mode enum
# ---------------------------------------------------------------------------

class NoiseMode(Enum):
    """Perturbation strategy applied to each selected ballot vector."""

    NONE = auto()
    """No perturbation — baseline passthrough."""

    BITFLIP = auto()
    """Flip one randomly chosen component of the selection vector."""

    ZERO_OUT = auto()
    """Replace the entire selection vector with zeros."""

    RANDOMIZE = auto()
    """Replace the entire selection vector with random integers in [0, K_CS)."""

    STOCHASTIC = auto()
    """
    Use a mark_confidence float to round ambiguous marks.  Each component is
    interpreted as a float confidence and rounded stochastically:
      - confidence ≥ 0.5  → round to 1
      - confidence < 0.5  → round to 0
    This simulates the effect of poor-quality ballot scanning.
    """


# ---------------------------------------------------------------------------
# Injection event record
# ---------------------------------------------------------------------------

@dataclass
class InjectionEvent:
    """Record of a single chaos injection event.

    Attributes
    ----------
    event_index : int
        Sequential event number within this ChaosInjector session.
    event_type : str
        Descriptive type string (e.g. "BITFLIP", "REPLAY_ATTACK", "CLEAN").
    original_vector : list[int]
        The selection vector as supplied by the caller.
    perturbed_vector : list[int]
        The selection vector actually passed to CountyNode.ingest_ballot().
    ballot_id : int
        The ballot_id assigned by the CountyNode after ingestion.
    timestamp_ns : int
        Nanosecond timestamp at event creation.
    metadata : dict
        Any additional event-specific context.
    """

    event_index: int
    event_type: str
    original_vector: List[int]
    perturbed_vector: List[int]
    ballot_id: int
    timestamp_ns: int = field(default_factory=time.time_ns)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "event_index": self.event_index,
            "event_type": self.event_type,
            "original_vector": self.original_vector,
            "perturbed_vector": self.perturbed_vector,
            "ballot_id": self.ballot_id,
            "timestamp_ns": self.timestamp_ns,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# ChaosInjector
# ---------------------------------------------------------------------------

class ChaosInjector:
    """Adversarial stress-testing wrapper for a CountyNode.

    The ChaosInjector provides controlled noise injection, replay attack
    simulation, burst ingestion testing, and freedom-floor monitoring.

    It wraps — but does NOT replace — a CountyNode.  All perturbations happen
    before data enters the math core; the CountyNode is always called with
    its normal interface.

    Parameters
    ----------
    county_node : CountyNode
        The node to inject chaos into.
    noise_budget : float
        Fraction of ballots to perturb, in [0, 1].  Default 0.10 (10%).
    noise_mode : NoiseMode
        Perturbation strategy for selected ballots.  Default BITFLIP.
    freedom_floor : float
        Minimum fraction of batches that must contribute non-trivially
        before FreedomFloorViolation is raised.  Default FREEDOM_FLOOR.
    seed : int, optional
        Random seed for reproducible tests.
    """

    def __init__(
        self,
        county_node: CountyNode,
        noise_budget: float = CHAOS_NOISE_BUDGET_DEFAULT,
        noise_mode: NoiseMode = NoiseMode.BITFLIP,
        freedom_floor: float = FREEDOM_FLOOR,
        seed: Optional[int] = None,
    ) -> None:
        if not 0.0 <= noise_budget <= 1.0:
            raise ValueError(f"noise_budget must be in [0, 1], got {noise_budget}")
        if not 0.0 <= freedom_floor <= 1.0:
            raise ValueError(f"freedom_floor must be in [0, 1], got {freedom_floor}")

        self._node = county_node
        self.noise_budget = noise_budget
        self.noise_mode = noise_mode
        self.freedom_floor = freedom_floor
        self._rng = random.Random(seed)
        self._injection_log: List[InjectionEvent] = []
        self._event_index: int = 0
        self._seen_ballot_ids: set = set()

    # ------------------------------------------------------------------
    # Primary injection interface
    # ------------------------------------------------------------------

    def inject_ballot(self, selection_vector: List[int]) -> BallotRecord:
        """Inject one ballot with probabilistic perturbation.

        If a uniformly random draw is below noise_budget, the ballot is
        perturbed according to noise_mode.  Otherwise it passes through clean.

        Parameters
        ----------
        selection_vector : list[int]
            Original (clean) selection vector.

        Returns
        -------
        BallotRecord
            The record as returned by CountyNode.ingest_ballot().
        """
        perturbed = (
            self._apply_noise(selection_vector)
            if self._rng.random() < self.noise_budget
            else list(selection_vector)
        )
        record = self._node.ingest_ballot(perturbed)

        event_type = (
            self.noise_mode.name if perturbed != list(selection_vector) else "CLEAN"
        )
        self._log_event(event_type, selection_vector, perturbed, record.ballot_id)
        return record

    def inject_batch(
        self,
        selection_vectors: List[List[int]],
    ) -> List[BallotRecord]:
        """Inject a batch of ballots with per-ballot probabilistic noise.

        After the batch is ingested, the freedom floor is checked.

        Parameters
        ----------
        selection_vectors : list[list[int]]
            List of original selection vectors.

        Returns
        -------
        list[BallotRecord]

        Raises
        ------
        FreedomFloorViolation
            If the injected batch has suppressed participation variance below
            the configured freedom_floor.
        """
        records = [self.inject_ballot(sv) for sv in selection_vectors]
        self._check_freedom_floor_for_batch(selection_vectors)
        return records

    def inject_replay_attack(self, selection_vector: List[int]) -> dict:
        """Simulate a replay attack: submit an identical ballot twice.

        The second submission reuses the exact same selection_vector.  A
        well-implemented chain should produce a different hash state for the
        second submission (because sequence_index changes), but this test
        verifies the detection path.

        Parameters
        ----------
        selection_vector : list[int]
            The ballot selection vector to replay.

        Returns
        -------
        dict
            {
              'first_record': BallotRecord,
              'second_record': BallotRecord,
              'hash_states_differ': bool,  # True = replay detected by hash divergence
              'ballot_ids_differ': bool,   # Should always be True
            }
        """
        first = self._node.ingest_ballot(list(selection_vector))
        self._log_event("REPLAY_FIRST", selection_vector, selection_vector, first.ballot_id)

        second = self._node.ingest_ballot(list(selection_vector))
        self._log_event("REPLAY_SECOND", selection_vector, selection_vector, second.ballot_id, {
            "replayed_from_ballot_id": first.ballot_id,
        })

        # Compare hash states at the two ingestion points
        state_after_first = first.as_int()
        state_after_second = second.as_int()

        return {
            "first_record": first,
            "second_record": second,
            "hash_states_differ": state_after_first != state_after_second,
            "ballot_ids_differ": first.ballot_id != second.ballot_id,
        }

    def inject_burst(
        self,
        template_vector: List[int],
        burst_size: int,
        inter_burst_delay_ns: int = 0,
    ) -> List[BallotRecord]:
        """Submit a rapid burst of ballots to stress shard sync timing.

        Parameters
        ----------
        template_vector : list[int]
            Base selection vector; each burst ballot uses a minor variation.
        burst_size : int
            Number of ballots to submit in rapid succession.
        inter_burst_delay_ns : int
            Nanoseconds to sleep between submissions (0 = no delay).

        Returns
        -------
        list[BallotRecord]
        """
        records = []
        for i in range(burst_size):
            # Vary one component slightly per burst step so ballots are distinct
            vec = list(template_vector)
            if vec:
                vec[i % len(vec)] = (vec[i % len(vec)] + i) % max(K_CS, 2)
            record = self._node.ingest_ballot(vec)
            self._log_event("BURST", template_vector, vec, record.ballot_id, {
                "burst_index": i,
                "burst_size": burst_size,
            })
            records.append(record)
            if inter_burst_delay_ns > 0:
                time.sleep(inter_burst_delay_ns * 1e-9)
        return records

    def inject_fuzzy_marks(
        self,
        confidence_vector: List[float],
        rounding_strategy: str = "round",
    ) -> BallotRecord:
        """Inject a ballot from a float-confidence mark vector.

        Simulates the effect of a ballot scanner that assigns a confidence
        score (0–1) to each mark rather than a clean binary selection.

        Parameters
        ----------
        confidence_vector : list[float]
            Confidence scores for each race, in [0, 1].  Values near 0.5
            represent ambiguous marks.
        rounding_strategy : str
            One of "round" (standard rounding), "floor" (conservative), or
            "stochastic" (random round weighted by confidence).

        Returns
        -------
        BallotRecord
        """
        int_vector = self._confidence_to_int_vector(confidence_vector, rounding_strategy)
        record = self._node.ingest_ballot(int_vector)
        self._log_event("FUZZY_MARK", [], int_vector, record.ballot_id, {
            "confidence_vector": list(confidence_vector),
            "rounding_strategy": rounding_strategy,
        })
        return record

    # ------------------------------------------------------------------
    # Freedom floor monitoring
    # ------------------------------------------------------------------

    def check_freedom_floor(self, county_ballot_counts: List[int]) -> bool:
        """Check whether county participation is above the freedom floor.

        Parameters
        ----------
        county_ballot_counts : list[int]
            Ballot count per county.

        Returns
        -------
        bool
            True if the floor is intact (≥ freedom_floor fraction of counties
            are non-trivial contributors).

        Raises
        ------
        FreedomFloorViolation
            If the participation fraction falls below freedom_floor.
        """
        if not county_ballot_counts:
            return True

        non_trivial = sum(
            1 for c in county_ballot_counts if c >= FREEDOM_FLOOR_MIN_BALLOTS
        )
        fraction = non_trivial / len(county_ballot_counts)

        if fraction < self.freedom_floor:
            raise FreedomFloorViolation(
                participating_fraction=fraction,
                freedom_floor=self.freedom_floor,
                injection_log=[e.as_dict() for e in self._injection_log],
            )
        return True

    # ------------------------------------------------------------------
    # Audit & diagnostics
    # ------------------------------------------------------------------

    @property
    def injection_log(self) -> List[InjectionEvent]:
        """Return a copy of all injection events recorded this session."""
        return list(self._injection_log)

    def injection_log_as_dicts(self) -> List[dict]:
        """Return injection log as a list of plain dicts."""
        return [e.as_dict() for e in self._injection_log]

    def noise_count(self) -> int:
        """Return number of events that applied a noise perturbation."""
        return sum(
            1 for e in self._injection_log
            if e.event_type not in ("CLEAN", "REPLAY_FIRST", "REPLAY_SECOND", "BURST")
        )

    def clean_count(self) -> int:
        """Return number of events that passed through without perturbation."""
        return sum(1 for e in self._injection_log if e.event_type == "CLEAN")

    def total_events(self) -> int:
        """Return total number of injection events recorded."""
        return len(self._injection_log)

    def reset_log(self) -> None:
        """Clear the injection log and reset event counter."""
        self._injection_log.clear()
        self._event_index = 0
        self._seen_ballot_ids.clear()

    def __repr__(self) -> str:
        return (
            f"ChaosInjector(county={self._node.county_id!r}, "
            f"noise_budget={self.noise_budget:.2f}, "
            f"mode={self.noise_mode.name}, "
            f"events={self.total_events()})"
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_noise(self, vector: List[int]) -> List[int]:
        """Apply noise_mode perturbation to a selection vector."""
        vec = list(vector)
        if not vec:
            return vec

        if self.noise_mode == NoiseMode.BITFLIP:
            idx = self._rng.randrange(len(vec))
            vec[idx] = vec[idx] ^ 1

        elif self.noise_mode == NoiseMode.ZERO_OUT:
            vec = [0] * len(vec)

        elif self.noise_mode == NoiseMode.RANDOMIZE:
            vec = [self._rng.randrange(max(K_CS, 2)) for _ in vec]

        elif self.noise_mode == NoiseMode.STOCHASTIC:
            # Treat integer values as if they were confidence scores in [0, max_val]
            max_val = max(max(abs(v) for v in vec), 1)
            vec = [
                1 if (v / max_val) >= 0.5 else 0
                for v in vec
            ]

        # NONE: no change
        return vec

    def _confidence_to_int_vector(
        self,
        confidence_vector: List[float],
        strategy: str,
    ) -> List[int]:
        """Convert a float confidence vector to an integer selection vector."""
        if strategy == "round":
            return [int(round(c)) for c in confidence_vector]
        elif strategy == "floor":
            return [int(c) for c in confidence_vector]
        elif strategy == "stochastic":
            return [
                1 if self._rng.random() < c else 0
                for c in confidence_vector
            ]
        else:
            raise ValueError(
                f"Unknown rounding_strategy {strategy!r}. "
                "Choose 'round', 'floor', or 'stochastic'."
            )

    def _check_freedom_floor_for_batch(
        self,
        selection_vectors: List[List[int]],
    ) -> None:
        """Check if the batch suppressed participation variance.

        A batch "suppresses variance" if the fraction of non-zero selection
        vectors (i.e. vectors that represent a real vote) falls below
        freedom_floor.  This catches the case where the injector is zeroing
        out so many ballots that the system optimises on silence.
        """
        if not selection_vectors:
            return

        # Retrieve the actual perturbed vectors from the most recent log entries
        recent = self._injection_log[-len(selection_vectors):]
        non_trivial = sum(
            1 for e in recent if any(v != 0 for v in e.perturbed_vector)
        )
        fraction = non_trivial / len(recent) if recent else 1.0

        if fraction < self.freedom_floor:
            raise FreedomFloorViolation(
                participating_fraction=fraction,
                freedom_floor=self.freedom_floor,
                injection_log=[e.as_dict() for e in self._injection_log],
            )

    def _log_event(
        self,
        event_type: str,
        original: List[int],
        perturbed: List[int],
        ballot_id: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append an InjectionEvent to the log."""
        self._event_index += 1
        self._injection_log.append(
            InjectionEvent(
                event_index=self._event_index,
                event_type=event_type,
                original_vector=list(original),
                perturbed_vector=list(perturbed),
                ballot_id=ballot_id,
                metadata=metadata or {},
            )
        )
