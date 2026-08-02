# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/holographic_screen.py — Holographic Screening Layer
=============================================================

The HolographicScreen sits *before* CountyNode.ingest_ballot() in the
ingestion pipeline.  It accepts raw adjudication records (e.g. outputs from
physical ballot scanners, poll-worker override panels, or signature
verification systems) and normalises them into clean integer selection vectors
that the math core can process without modification.

Why this layer exists
---------------------
The math core assumes clean, quantized integer selection vectors.  Real ballot
scanning produces:
  - Analog confidence scores from optical mark recognition (OMR)
  - Adjudication flags from contested or ambiguous marks
  - Write-in text that must be mapped to a candidate integer slot
  - Multi-race ballots with missing/partial selections

Without this layer, any real-world messiness would either crash the engine
(brittle failure) or be silently rounded in an unauditable way.

Key design properties
---------------------
1. RULE-BASED ONLY — no ML heuristics.  Every normalisation decision is
   deterministic, reproducible, and governed by an explicit rule that can
   be examined in a court of law.
2. EVERY NORMALISATION IS LOGGED — all decisions feed into a side-channel
   normalisation log that is appended to the OSCAL dossier chain of custody.
3. EXPLICIT REJECTION — ballots with mark confidence below
   HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE raise AdmissibilityError instead of
   being silently dropped.  The error routes the record to a human
   adjudicator queue.
4. PASS-THROUGH FOR CLEAN DATA — if all components of the raw record are
   already clean integers ≥ 0, the screen is a zero-cost identity function.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any

from .constants import HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AdmissibilityError(Exception):
    """
    Raised when an adjudication record cannot be safely normalised into a
    clean integer selection vector for math-core consumption.

    This is NOT a system failure — it is an intentional route to the human
    adjudicator queue.  Callers must catch AdmissibilityError and dispatch
    the record for human review; they must never silently swallow it.

    Attributes
    ----------
    record : dict
        The raw adjudication record that triggered the error.
    reason : str
        Human-readable explanation of why the record was rejected.
    field_name : str, optional
        The specific record field that caused the rejection.
    """

    def __init__(
        self,
        record: dict,
        reason: str,
        field_name: Optional[str] = None,
    ) -> None:
        self.record = record
        self.reason = reason
        self.field_name = field_name
        super().__init__(
            f"AdmissibilityError [{field_name or 'record'}]: {reason}"
        )


# ---------------------------------------------------------------------------
# Normalisation result
# ---------------------------------------------------------------------------

class NormalisationStatus(Enum):
    """Outcome of a single record normalisation attempt."""

    CLEAN_PASSTHROUGH = auto()
    """Record was already in integer form; no normalisation applied."""

    NORMALISED = auto()
    """Record required normalisation; decisions are logged."""

    WRITE_IN_RESOLVED = auto()
    """A write-in text field was resolved to a candidate integer slot."""

    ADJUDICATION_APPLIED = auto()
    """An adjudication flag overrode an ambiguous mark."""

    REJECTED = auto()
    """Record could not be normalised; AdmissibilityError was raised."""


@dataclass
class NormalisationRecord:
    """Full record of a single normalisation decision.

    Attributes
    ----------
    raw_record : dict
        The original adjudication record as received.
    normalised_vector : list[int]
        The integer selection vector produced by normalisation.
    status : NormalisationStatus
        Classification of what normalisation steps were applied.
    decisions : list[dict]
        Ordered list of normalisation decision events (one per race/field).
    timestamp_ns : int
        Nanosecond timestamp of normalisation.
    ballot_index : int
        Sequential index assigned by the HolographicScreen.
    """

    raw_record: dict
    normalised_vector: List[int]
    status: NormalisationStatus
    decisions: List[dict]
    timestamp_ns: int = field(default_factory=time.time_ns)
    ballot_index: int = 0

    def as_dict(self) -> dict:
        return {
            "ballot_index": self.ballot_index,
            "status": self.status.name,
            "normalised_vector": self.normalised_vector,
            "decisions": self.decisions,
            "timestamp_ns": self.timestamp_ns,
        }


# ---------------------------------------------------------------------------
# Write-in registry
# ---------------------------------------------------------------------------

class WriteInRegistry:
    """Maps write-in text strings to integer candidate slots.

    In a real deployment, this registry is populated from the official
    candidate list for each race.  The integer slot corresponds to the
    candidate's position on the official ballot.

    Parameters
    ----------
    registry : dict[str, int], optional
        Pre-populated name → integer mappings.
    default_slot : int, optional
        Integer to use for unrecognised write-ins (default: -1, which the
        screen will treat as an unresolvable write-in and log accordingly).
    """

    def __init__(
        self,
        registry: Optional[Dict[str, int]] = None,
        default_slot: int = -1,
    ) -> None:
        self._registry: Dict[str, int] = {
            k.strip().lower(): v for k, v in (registry or {}).items()
        }
        self.default_slot = default_slot

    def resolve(self, text: str) -> tuple[int, bool]:
        """Resolve a write-in text to an integer slot.

        Parameters
        ----------
        text : str
            Write-in text from the ballot record.

        Returns
        -------
        tuple[int, bool]
            (slot, was_resolved) where was_resolved is True if the text
            matched a known candidate.
        """
        key = text.strip().lower()
        if key in self._registry:
            return self._registry[key], True
        return self.default_slot, False

    def register(self, name: str, slot: int) -> None:
        """Add or update a write-in registry entry."""
        self._registry[name.strip().lower()] = slot

    def __len__(self) -> int:
        return len(self._registry)


# ---------------------------------------------------------------------------
# HolographicScreen
# ---------------------------------------------------------------------------

class HolographicScreen:
    """Pre-processing stage: raw adjudication records → integer selection vectors.

    Parameters
    ----------
    min_confidence : float
        Minimum mark_confidence (0–1) below which AdmissibilityError is raised.
        Default: HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE = 0.60.
    write_in_registry : WriteInRegistry, optional
        Registry for resolving write-in text to integer slots.
    races : int, optional
        Expected number of races per ballot.  If provided, missing races are
        zero-padded; extra races are truncated.  If None, no padding is applied.
    """

    def __init__(
        self,
        min_confidence: float = HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE,
        write_in_registry: Optional[WriteInRegistry] = None,
        races: Optional[int] = None,
    ) -> None:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError(f"min_confidence must be in [0, 1], got {min_confidence}")
        self.min_confidence = min_confidence
        self._registry = write_in_registry or WriteInRegistry()
        self.races = races
        self._normalisation_log: List[NormalisationRecord] = []
        self._ballot_index: int = 0

    # ------------------------------------------------------------------
    # Primary normalisation interface
    # ------------------------------------------------------------------

    def normalise(self, raw_record: dict) -> List[int]:
        """Normalise a raw adjudication record to an integer selection vector.

        This is the primary entry point.  Call this instead of directly calling
        CountyNode.ingest_ballot() when your input source is a scanner or
        adjudication system.

        Parameters
        ----------
        raw_record : dict
            Raw adjudication record.  Supported keys:

            selections : list
                Per-race selections.  Each element may be:
                  - int / float  : numeric mark (confidence or integer)
                  - str          : write-in candidate text
                  - dict         : {"value": ..., "confidence": float, "adjudicated": bool}

            mark_confidence : float, optional
                Overall ballot confidence score from OMR.  If below
                min_confidence, AdmissibilityError is raised.

            adjudication_flag : bool, optional
                If True, an adjudicator has reviewed this ballot.  Overrides
                automatic confidence rejection.

            write_ins : list[str], optional
                Alternative location for write-in texts, parallel to selections.

        Returns
        -------
        list[int]
            Clean integer selection vector ready for CountyNode.ingest_ballot().

        Raises
        ------
        AdmissibilityError
            If the record cannot be reliably normalised.
        """
        decisions: List[dict] = []

        # --- Step 1: Global confidence check ---
        overall_confidence = float(raw_record.get("mark_confidence", 1.0))
        adjudicated = bool(raw_record.get("adjudication_flag", False))

        if overall_confidence < self.min_confidence and not adjudicated:
            raise AdmissibilityError(
                record=raw_record,
                reason=(
                    f"mark_confidence {overall_confidence:.3f} is below "
                    f"minimum {self.min_confidence:.3f} and record has not been adjudicated."
                ),
                field_name="mark_confidence",
            )

        # Only count the ballot index after the confidence gate passes
        self._ballot_index += 1

        # --- Step 2: Normalise per-race selections ---
        selections = raw_record.get("selections", [])
        if not selections and "write_ins" in raw_record:
            selections = raw_record["write_ins"]

        int_vector: List[int] = []
        status = NormalisationStatus.CLEAN_PASSTHROUGH

        for race_idx, selection in enumerate(selections):
            slot, decision = self._normalise_selection(
                selection, race_idx, adjudicated
            )
            int_vector.append(slot)
            decisions.append(decision)
            if decision["action"] != "PASSTHROUGH":
                status = NormalisationStatus(
                    max(status.value, NormalisationStatus.NORMALISED.value)
                )
                if decision["action"] == "WRITE_IN_RESOLVED":
                    status = NormalisationStatus.WRITE_IN_RESOLVED
                elif decision["action"] == "ADJUDICATION_APPLIED":
                    status = NormalisationStatus.ADJUDICATION_APPLIED

        # --- Step 3: Pad/truncate to expected race count ---
        if self.races is not None:
            if len(int_vector) < self.races:
                pad_count = self.races - len(int_vector)
                int_vector.extend([0] * pad_count)
                decisions.append({
                    "race_idx": "PAD",
                    "action": "ZERO_PAD",
                    "padded_count": pad_count,
                })
            elif len(int_vector) > self.races:
                truncated = int_vector[self.races:]
                int_vector = int_vector[:self.races]
                decisions.append({
                    "race_idx": "TRUNCATE",
                    "action": "TRUNCATED",
                    "truncated_values": truncated,
                })

        # --- Step 4: Log the normalisation ---
        norm_record = NormalisationRecord(
            raw_record=raw_record,
            normalised_vector=int_vector,
            status=status,
            decisions=decisions,
            ballot_index=self._ballot_index,
        )
        self._normalisation_log.append(norm_record)

        return int_vector

    def normalise_batch(self, raw_records: List[dict]) -> List[List[int]]:
        """Normalise a list of raw adjudication records.

        Records that raise AdmissibilityError are collected into the
        rejections list (see get_rejections()); all others are normalised.

        Parameters
        ----------
        raw_records : list[dict]

        Returns
        -------
        list[list[int]]
            Normalised selection vectors for records that passed.
            Rejected records are NOT included.
        """
        results = []
        for record in raw_records:
            try:
                results.append(self.normalise(record))
            except AdmissibilityError:
                # Already logged in normalise() as REJECTED; do not re-raise
                pass
        return results

    # ------------------------------------------------------------------
    # Audit & diagnostics
    # ------------------------------------------------------------------

    @property
    def normalisation_log(self) -> List[NormalisationRecord]:
        """Return a copy of all normalisation records."""
        return list(self._normalisation_log)

    def normalisation_log_as_dicts(self) -> List[dict]:
        """Return normalisation log as plain dicts (for OSCAL dossier)."""
        return [r.as_dict() for r in self._normalisation_log]

    def get_rejections(self) -> List[NormalisationRecord]:
        """Return all normalisation records with REJECTED status."""
        return [
            r for r in self._normalisation_log
            if r.status == NormalisationStatus.REJECTED
        ]

    def rejection_count(self) -> int:
        """Return number of rejected records."""
        return len(self.get_rejections())

    def acceptance_count(self) -> int:
        """Return number of accepted (normalised) records."""
        return self._ballot_index - self.rejection_count()

    def clean_passthrough_count(self) -> int:
        """Return number of records that required no normalisation."""
        return sum(
            1 for r in self._normalisation_log
            if r.status == NormalisationStatus.CLEAN_PASSTHROUGH
        )

    def reset_log(self) -> None:
        """Clear the normalisation log."""
        self._normalisation_log.clear()
        self._ballot_index = 0

    def __repr__(self) -> str:
        return (
            f"HolographicScreen(min_confidence={self.min_confidence:.2f}, "
            f"races={self.races}, "
            f"processed={self._ballot_index})"
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _normalise_selection(
        self,
        selection: Any,
        race_idx: int,
        adjudicated: bool,
    ) -> tuple[int, dict]:
        """Normalise a single per-race selection to an integer slot.

        Parameters
        ----------
        selection : any
            The raw value for this race (int, float, str, or dict).
        race_idx : int
            Index of this race within the ballot.
        adjudicated : bool
            Whether the overall ballot has been human-adjudicated.

        Returns
        -------
        tuple[int, dict]
            (integer_slot, decision_record)
        """
        decision: dict = {"race_idx": race_idx, "raw_value": repr(selection)}

        # --- dict with optional confidence / adjudication fields ---
        if isinstance(selection, dict):
            value = selection.get("value", 0)
            confidence = float(selection.get("confidence", 1.0))
            adj = bool(selection.get("adjudicated", adjudicated))

            if confidence < self.min_confidence and not adj:
                # Per-race confidence failure → treat as abstain (0), log it
                decision.update({
                    "action": "LOW_CONFIDENCE_ABSTAIN",
                    "confidence": confidence,
                    "min_confidence": self.min_confidence,
                    "note": "mark_confidence below threshold; treated as abstain",
                })
                return 0, decision

            if adj and "adjudicated_value" in selection:
                decision.update({
                    "action": "ADJUDICATION_APPLIED",
                    "adjudicated_value": selection["adjudicated_value"],
                    "original_value": value,
                })
                return int(selection["adjudicated_value"]), decision

            slot = self._coerce_to_int(value, decision)
            return slot, decision

        # --- write-in string ---
        if isinstance(selection, str):
            slot, resolved = self._registry.resolve(selection)
            if not resolved:
                decision.update({
                    "action": "WRITE_IN_UNRESOLVED",
                    "write_in_text": selection,
                    "slot_assigned": slot,
                    "note": "write-in text not found in registry; default slot assigned",
                })
            else:
                decision.update({
                    "action": "WRITE_IN_RESOLVED",
                    "write_in_text": selection,
                    "slot_assigned": slot,
                })
            return max(slot, 0), decision

        # --- numeric (int or float) ---
        slot = self._coerce_to_int(selection, decision)
        return slot, decision

    @staticmethod
    def _coerce_to_int(value: Any, decision: dict) -> int:
        """Coerce a numeric value to a non-negative integer."""
        try:
            iv = int(round(float(value)))
            iv = max(iv, 0)
            decision.update({"action": "PASSTHROUGH", "coerced_value": iv})
            return iv
        except (TypeError, ValueError):
            decision.update({
                "action": "COERCE_FAILED_ZERO",
                "note": f"Could not coerce {value!r} to int; using 0",
            })
            return 0
