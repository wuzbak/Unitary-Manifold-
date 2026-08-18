# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/scanner_adapter.py — Physical Ballot Scanner Interface Adapter
=======================================================================

The ScannerAdapter bridges raw OMR (Optical Mark Recognition) output from
physical scanner hardware into the HolographicScreen normalisation layer.

Architecture
------------
  Scanner (USB HID / Serial) → ScannerAdapter → HolographicScreen → CountyNode

The adapter accepts raw scanner protocol dicts (as emitted by USB HID or
serial-port scanner drivers) and maps them to AdjudicationRecord dicts that
HolographicScreen.normalise() can process.

Scanner protocol format
-----------------------
Most optical ballot scanners output per-ballot records in one of two forms:

  OMR_DICT (standard) ::

      {
          "ballot_serial": "2026-WA-047-000001",
          "marks": [
              {"position": 0, "confidence": 0.97},  # race 0, mark present
              {"position": 1, "confidence": 0.88},  # race 1
              ...
          ],
          "write_ins": ["Alice Smith", "", ""],      # parallel to marks
          "page_confidence": 0.95,
          "adjudication_flag": false
      }

  FLAT_CONFIDENCE (legacy) ::

      {
          "id": "B00042",
          "conf_scores": [0.98, 0.91, 0.77],  # one per race
          "selections": [1, 1, 1],             # 0 or 1 per race
      }

MockScanner
-----------
MockScanner emits deterministic OMR records for testing::

    scanner = MockScanner(n_races=3)
    raw = scanner.next_record()   # {"ballot_serial": ..., "marks": [...], ...}

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import enum
import random
import time
import uuid
from typing import Dict, List, Optional, Any

from .holographic_screen import HolographicScreen, AdmissibilityError
from .constants import HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE


# ---------------------------------------------------------------------------
# ScannerFormat enum
# ---------------------------------------------------------------------------

class ScannerFormat(str, enum.Enum):
    """Wire format emitted by a physical ballot scanner.

    OMR_DICT
        Standard format — dict with ``ballot_serial``, ``marks``, ``write_ins``,
        ``page_confidence``, and ``adjudication_flag`` keys.

    FLAT_CONFIDENCE
        Legacy format — dict with ``id``/``sequence``, ``confidence_scores``,
        and optional ``selections`` keys.
    """

    OMR_DICT = "OMR_DICT"
    FLAT_CONFIDENCE = "FLAT_CONFIDENCE"


# ---------------------------------------------------------------------------
# ScannerAdapter
# ---------------------------------------------------------------------------

class ScannerAdapter:
    """Maps raw scanner OMR dicts to HolographicScreen.normalise() input format.

    Parameters
    ----------
    screen : HolographicScreen, optional
        Holographic screening layer.  If not provided, a default instance
        is created with the system-wide min_confidence threshold.
    races : int, optional
        Expected number of races per ballot.  Passed through to HolographicScreen.
    jurisdiction_id : str, optional
        Jurisdiction identifier tag included in processed record metadata.
    num_candidates : int, optional
        Alias for ``races``; number of candidates / races on each ballot.
    """

    def __init__(
        self,
        screen: Optional[HolographicScreen] = None,
        races: Optional[int] = None,
        jurisdiction_id: Optional[str] = None,
        num_candidates: Optional[int] = None,
    ) -> None:
        effective_races = num_candidates if num_candidates is not None else races
        self._screen = screen or HolographicScreen(races=effective_races)
        self.jurisdiction_id = jurisdiction_id or ""
        self._admitted_count: int = 0
        self._rejected_count: int = 0
        self._rejection_log: List[dict] = []
        self._total_processed: int = 0

    # ------------------------------------------------------------------
    # Primary interface
    # ------------------------------------------------------------------

    def process(self, raw_omr: dict) -> dict:
        """Translate and screen a raw OMR record; return a status dict.

        Parameters
        ----------
        raw_omr : dict
            Raw scanner output in OMR_DICT or FLAT_CONFIDENCE format.

        Returns
        -------
        dict
            ``{"status": "ACCEPTED"|"REJECTED"|"QUEUED_FOR_ADJUDICATION",
               "vector": list[int] | None, ...}``
        """
        self._total_processed += 1
        adj_record = self._translate(raw_omr)

        # Records with adjudication_flag go to human review queue
        if adj_record.get("adjudication_flag"):
            self._rejected_count += 1
            self._rejection_log.append({
                "raw_omr": raw_omr,
                "reason": "adjudication_flag set",
                "field_name": "adjudication_flag",
                "timestamp_ns": time.time_ns(),
            })
            return {"status": "QUEUED_FOR_ADJUDICATION", "vector": None,
                    "jurisdiction_id": self.jurisdiction_id}

        try:
            vector = self._screen.normalise(adj_record)
            self._admitted_count += 1
            return {"status": "ACCEPTED", "vector": vector,
                    "jurisdiction_id": self.jurisdiction_id}
        except AdmissibilityError as e:
            self._rejected_count += 1
            self._rejection_log.append({
                "raw_omr": raw_omr,
                "reason": e.reason,
                "field_name": e.field_name,
                "timestamp_ns": time.time_ns(),
            })
            return {"status": "REJECTED", "vector": None,
                    "reason": e.reason,
                    "jurisdiction_id": self.jurisdiction_id}

    def process_batch(self, raw_omr_records: List[dict]) -> List[dict]:
        """Process a list of OMR records; returns a list of status dicts."""
        return [self.process(r) for r in raw_omr_records]

    def screen_omr_record(self, raw_omr: dict) -> Optional[List[int]]:
        """Translate a raw OMR dict and pass it through the holographic screen.

        Parameters
        ----------
        raw_omr : dict
            Raw scanner output dict.  Accepted formats:
            - OMR_DICT (standard): has ``marks`` list + optional ``write_ins``
            - FLAT_CONFIDENCE (legacy): has ``conf_scores`` + ``selections``
            - Any dict compatible with HolographicScreen.normalise() directly

        Returns
        -------
        list[int] or None
            Normalised integer selection vector on success.
            None if AdmissibilityError was raised (record added to rejection log).
        """
        adj_record = self._translate(raw_omr)
        try:
            vector = self._screen.normalise(adj_record)
            self._admitted_count += 1
            return vector
        except AdmissibilityError as e:
            self._rejected_count += 1
            self._rejection_log.append({
                "raw_omr": raw_omr,
                "reason": e.reason,
                "field_name": e.field_name,
                "timestamp_ns": time.time_ns(),
            })
            return None

    def screen_batch(self, raw_omr_records: List[dict]) -> List[List[int]]:
        """Screen a list of OMR records; returns only admitted vectors."""
        results = []
        for record in raw_omr_records:
            vector = self.screen_omr_record(record)
            if vector is not None:
                results.append(vector)
        return results

    # ------------------------------------------------------------------
    # Translation helpers
    # ------------------------------------------------------------------

    def _translate(self, raw_omr: dict) -> dict:
        """Translate a raw OMR dict into HolographicScreen.normalise() format.

        Supports OMR_DICT, FLAT_CONFIDENCE, and pass-through for records
        already in the expected format.
        """
        fmt = raw_omr.get("scanner_format")

        # Explicit format tag
        if fmt == ScannerFormat.FLAT_CONFIDENCE or fmt == ScannerFormat.FLAT_CONFIDENCE.value:
            return self._from_flat_confidence(raw_omr)

        # Standard OMR_DICT format: "marks" key with confidence scores
        if "marks" in raw_omr:
            return self._from_omr_dict(raw_omr)

        # Legacy FLAT_CONFIDENCE format: conf_scores + selections
        if "conf_scores" in raw_omr and "selections" in raw_omr:
            return self._from_flat_confidence(raw_omr)

        # New FLAT_CONFIDENCE with confidence_scores key
        if "confidence_scores" in raw_omr:
            return self._from_confidence_scores(raw_omr)

        # Pass-through: already in AdjudicationRecord format or compatible
        return raw_omr

    @staticmethod
    def _from_omr_dict(raw_omr: dict) -> dict:
        """Translate OMR_DICT format."""
        marks = raw_omr.get("marks", [])
        write_ins = raw_omr.get("write_ins", [])
        page_confidence = float(raw_omr.get("page_confidence", 1.0))
        adjudicated = bool(raw_omr.get("adjudication_flag", False))

        selections = []
        for i, mark in enumerate(marks):
            confidence = float(mark.get("confidence", 1.0))
            position = int(mark.get("position", 0))
            write_in_text = write_ins[i] if i < len(write_ins) else ""

            if write_in_text:
                selections.append(write_in_text)
            else:
                selections.append({
                    "value": position,
                    "confidence": confidence,
                    "adjudicated": adjudicated,
                })

        return {
            "selections": selections,
            "mark_confidence": page_confidence,
            "adjudication_flag": adjudicated,
            "ballot_serial": raw_omr.get("ballot_serial", ""),
        }

    @staticmethod
    def _from_flat_confidence(raw_omr: dict) -> dict:
        """Translate FLAT_CONFIDENCE format."""
        conf_scores = raw_omr.get("conf_scores", [])
        selections = raw_omr.get("selections", [])
        min_confidence = min(conf_scores) if conf_scores else 1.0
        adjudicated = bool(raw_omr.get("adjudication_flag", False))

        normalised_selections = []
        for i, sel in enumerate(selections):
            conf = float(conf_scores[i]) if i < len(conf_scores) else 1.0
            normalised_selections.append({
                "value": int(sel),
                "confidence": conf,
                "adjudicated": adjudicated,
            })

        return {
            "selections": normalised_selections,
            "mark_confidence": min_confidence,
            "adjudication_flag": adjudicated,
        }

    @staticmethod
    def _from_confidence_scores(raw_omr: dict) -> dict:
        """Translate FLAT_CONFIDENCE format with ``confidence_scores`` key."""
        scores = raw_omr.get("confidence_scores", [])
        adjudicated = bool(raw_omr.get("adjudication_flag", False))
        # Highest-scoring candidate wins
        if scores:
            winner = int(max(range(len(scores)), key=lambda i: scores[i]))
            selections = [{"value": winner, "confidence": float(scores[winner]),
                           "adjudicated": adjudicated}]
            min_conf = float(scores[winner])
        else:
            selections = []
            min_conf = 1.0
        return {
            "selections": selections,
            "mark_confidence": min_conf,
            "adjudication_flag": adjudicated,
        }

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def total_processed(self) -> int:
        return self._total_processed

    @property
    def rejected_count(self) -> int:
        return self._rejected_count

    @property
    def rejection_log(self) -> List[dict]:
        return list(self._rejection_log)

    def normalisation_log(self):
        """Delegate to the underlying HolographicScreen's normalisation log."""
        return self._screen.normalisation_log

    def __repr__(self) -> str:
        return (
            f"ScannerAdapter(admitted={self._admitted_count}, "
            f"rejected={self._rejected_count})"
        )


# ---------------------------------------------------------------------------
# MockScanner
# ---------------------------------------------------------------------------

class MockScanner:
    """Deterministic mock ballot scanner for testing.

    Emits OMR_DICT records with configurable confidence scores and optional
    low-confidence / write-in / adjudication scenarios.

    Parameters
    ----------
    n_races : int
        Number of races per ballot (default: 3).
    base_confidence : float
        Default page confidence for emitted records (default: 0.95).
    seed : int
        Seed for the pseudo-random sequence of ballot integers.
    """

    def __init__(
        self,
        n_races: int = 3,
        base_confidence: float = 0.95,
        seed: int = 42,
        num_candidates: Optional[int] = None,
    ) -> None:
        self.n_races = num_candidates if num_candidates is not None else n_races
        self.base_confidence = base_confidence
        self._counter: int = 0
        self._seed = seed
        self._rng = random.Random(seed)

    def next_record(
        self,
        low_confidence: bool = False,
        with_write_in: Optional[str] = None,
        adjudicated: bool = False,
    ) -> dict:
        """Emit the next deterministic OMR_DICT record.

        Parameters
        ----------
        low_confidence : bool
            If True, page_confidence is set below the screen threshold.
        with_write_in : str, optional
            If provided, the first race uses this write-in text.
        adjudicated : bool
            If True, sets adjudication_flag=True (overrides low_confidence).

        Returns
        -------
        dict
            A well-formed OMR_DICT record.
        """
        self._counter += 1
        serial = f"MOCK-{self._counter:06d}-SEED{self._seed}"

        page_conf = 0.30 if low_confidence else self.base_confidence
        marks = []
        write_ins = []

        for race_idx in range(self.n_races):
            conf = self.base_confidence - (race_idx * 0.01)

            if race_idx == 0 and with_write_in:
                marks.append({"position": 0, "confidence": conf})
                write_ins.append(with_write_in)
            else:
                position = self._rng.randint(0, max(1, self.n_races - 1))
                marks.append({"position": position, "confidence": conf})
                write_ins.append("")

        return {
            "ballot_serial": serial,
            "marks": marks,
            "write_ins": write_ins,
            "page_confidence": page_conf,
            "adjudication_flag": adjudicated,
            "scanner_format": ScannerFormat.OMR_DICT,
            "sequence": self._counter,
        }

    def emit_batch(
        self,
        count: int,
        low_confidence_fraction: float = 0.0,
    ) -> List[dict]:
        """Emit ``count`` records, with some fraction having low confidence.

        Parameters
        ----------
        count : int
            Total records to emit.
        low_confidence_fraction : float
            Fraction of records to emit with low page_confidence [0, 1].

        Returns
        -------
        list[dict]
        """
        n_low = int(count * low_confidence_fraction)
        records = []
        for i in range(count):
            low = (i < n_low)
            records.append(self.next_record(low_confidence=low))
        return records

    def reset(self) -> None:
        """Reset counter to zero."""
        self._counter = 0

    def __repr__(self) -> str:
        return (
            f"MockScanner(n_races={self.n_races}, "
            f"base_confidence={self.base_confidence}, "
            f"records_emitted={self._counter})"
        )
