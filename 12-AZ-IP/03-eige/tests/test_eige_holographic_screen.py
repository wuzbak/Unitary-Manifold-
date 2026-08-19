# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/holographic_screen.py — Phase 2: Holographic Screening Layer"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.holographic_screen import (
    HolographicScreen,
    AdmissibilityError,
    NormalisationRecord,
    NormalisationStatus,
    WriteInRegistry,
)
from EIGE.src.constants import HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def screen():
    return HolographicScreen()


@pytest.fixture
def strict_screen():
    """Screen with very high confidence requirement."""
    return HolographicScreen(min_confidence=0.95)


@pytest.fixture
def registry():
    return WriteInRegistry({"Alice Smith": 5, "Bob Jones": 6})


@pytest.fixture
def screen_with_registry(registry):
    return HolographicScreen(write_in_registry=registry, races=3)


# ---------------------------------------------------------------------------
# WriteInRegistry
# ---------------------------------------------------------------------------

class TestWriteInRegistry:
    def test_resolve_known(self, registry):
        slot, resolved = registry.resolve("Alice Smith")
        assert slot == 5
        assert resolved is True

    def test_resolve_case_insensitive(self, registry):
        slot, resolved = registry.resolve("alice smith")
        assert slot == 5
        assert resolved is True

    def test_resolve_unknown_returns_default(self, registry):
        slot, resolved = registry.resolve("Unknown Candidate")
        assert slot == registry.default_slot
        assert resolved is False

    def test_register_new_entry(self, registry):
        registry.register("Carol White", 7)
        slot, resolved = registry.resolve("Carol White")
        assert slot == 7
        assert resolved is True

    def test_len(self, registry):
        assert len(registry) == 2

    def test_strip_whitespace(self, registry):
        slot, resolved = registry.resolve("  Alice Smith  ")
        assert resolved is True


# ---------------------------------------------------------------------------
# HolographicScreen initialisation
# ---------------------------------------------------------------------------

class TestHolographicScreenInit:
    def test_default_min_confidence(self):
        s = HolographicScreen()
        assert s.min_confidence == HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE

    def test_invalid_confidence_high_raises(self):
        with pytest.raises(ValueError, match="min_confidence"):
            HolographicScreen(min_confidence=1.5)

    def test_invalid_confidence_negative_raises(self):
        with pytest.raises(ValueError, match="min_confidence"):
            HolographicScreen(min_confidence=-0.1)

    def test_repr_contains_confidence(self):
        s = HolographicScreen(min_confidence=0.75)
        assert "0.75" in repr(s)


# ---------------------------------------------------------------------------
# Clean integer passthrough
# ---------------------------------------------------------------------------

class TestCleanPassthrough:
    def test_integer_selections_passthrough(self, screen):
        record = {"selections": [1, 0, 1]}
        vector = screen.normalise(record)
        assert vector == [1, 0, 1]

    def test_passthrough_status(self, screen):
        screen.normalise({"selections": [1, 0]})
        norm = screen.normalisation_log[0]
        assert norm.status == NormalisationStatus.CLEAN_PASSTHROUGH

    def test_empty_selections_returns_empty(self, screen):
        vector = screen.normalise({"selections": []})
        assert vector == []

    def test_float_selections_rounded(self, screen):
        vector = screen.normalise({"selections": [0.9, 0.1, 0.6]})
        assert vector == [1, 0, 1]

    def test_negative_values_clamped_to_zero(self, screen):
        vector = screen.normalise({"selections": [-5, 1]})
        assert vector[0] == 0
        assert vector[1] == 1

    def test_ballot_index_increments(self, screen):
        screen.normalise({"selections": [1, 0]})
        screen.normalise({"selections": [0, 1]})
        logs = screen.normalisation_log
        assert logs[0].ballot_index == 1
        assert logs[1].ballot_index == 2


# ---------------------------------------------------------------------------
# Confidence checks
# ---------------------------------------------------------------------------

class TestConfidenceChecks:
    def test_high_confidence_passes(self, screen):
        record = {"selections": [1, 0], "mark_confidence": 0.99}
        vector = screen.normalise(record)
        assert vector == [1, 0]

    def test_low_confidence_raises_admissibility_error(self, strict_screen):
        record = {"selections": [1, 0], "mark_confidence": 0.50}
        with pytest.raises(AdmissibilityError) as exc_info:
            strict_screen.normalise(record)
        assert "mark_confidence" in str(exc_info.value)

    def test_low_confidence_with_adjudication_flag_passes(self, strict_screen):
        record = {
            "selections": [1, 0],
            "mark_confidence": 0.50,
            "adjudication_flag": True,
        }
        vector = strict_screen.normalise(record)
        assert len(vector) == 2

    def test_admissibility_error_contains_record(self, strict_screen):
        record = {"selections": [1, 0], "mark_confidence": 0.30}
        with pytest.raises(AdmissibilityError) as exc_info:
            strict_screen.normalise(record)
        assert exc_info.value.record is record

    def test_admissibility_error_field_name(self, strict_screen):
        with pytest.raises(AdmissibilityError) as exc_info:
            strict_screen.normalise({"selections": [1], "mark_confidence": 0.10})
        assert exc_info.value.field_name == "mark_confidence"

    def test_per_race_low_confidence_abstains(self, screen):
        """Per-race confidence dict below threshold → treat as abstain (0)."""
        record = {
            "selections": [
                {"value": 1, "confidence": 0.99},   # high conf → passes
                {"value": 1, "confidence": 0.20},   # low conf, not adjudicated
            ]
        }
        vector = screen.normalise(record)
        assert vector[0] == 1
        assert vector[1] == 0  # abstained

    def test_per_race_adjudication_override(self, screen):
        """Per-race adjudicated value overrides the raw value."""
        record = {
            "selections": [
                {
                    "value": 0,
                    "adjudicated": True,
                    "adjudicated_value": 1,
                    "confidence": 0.30,
                }
            ]
        }
        vector = screen.normalise(record)
        assert vector[0] == 1


# ---------------------------------------------------------------------------
# Write-in handling
# ---------------------------------------------------------------------------

class TestWriteIns:
    def test_known_write_in_resolved(self, screen_with_registry):
        record = {"selections": ["Alice Smith", 0, 1]}
        vector = screen_with_registry.normalise(record)
        assert vector[0] == 5

    def test_unknown_write_in_gets_default_slot(self, screen_with_registry):
        record = {"selections": ["Unknown Person", 0, 1]}
        vector = screen_with_registry.normalise(record)
        assert vector[0] == 0  # max(-1, 0) = 0

    def test_write_in_logged_as_resolved(self, screen_with_registry):
        screen_with_registry.normalise({"selections": ["Alice Smith", 0]})
        log = screen_with_registry.normalisation_log[0]
        assert any(
            d.get("action") == "WRITE_IN_RESOLVED"
            for d in log.decisions
        )

    def test_write_in_unresolved_logged(self, screen_with_registry):
        screen_with_registry.normalise({"selections": ["Nobody", 0]})
        log = screen_with_registry.normalisation_log[0]
        assert any(
            d.get("action") == "WRITE_IN_UNRESOLVED"
            for d in log.decisions
        )


# ---------------------------------------------------------------------------
# Race padding / truncation
# ---------------------------------------------------------------------------

class TestRacePadding:
    def test_short_vector_zero_padded(self):
        s = HolographicScreen(races=5)
        vector = s.normalise({"selections": [1, 0]})
        assert len(vector) == 5
        assert vector[2:] == [0, 0, 0]

    def test_long_vector_truncated(self):
        s = HolographicScreen(races=2)
        vector = s.normalise({"selections": [1, 0, 1, 0, 1]})
        assert len(vector) == 2

    def test_exact_length_unchanged(self):
        s = HolographicScreen(races=3)
        vector = s.normalise({"selections": [1, 0, 1]})
        assert len(vector) == 3


# ---------------------------------------------------------------------------
# Batch normalisation
# ---------------------------------------------------------------------------

class TestBatchNormalisation:
    def test_normalise_batch_returns_all_clean(self, screen):
        records = [
            {"selections": [1, 0]},
            {"selections": [0, 1]},
            {"selections": [1, 1]},
        ]
        vectors = screen.normalise_batch(records)
        assert len(vectors) == 3

    def test_normalise_batch_skips_rejected(self):
        s = HolographicScreen(min_confidence=0.95)
        records = [
            {"selections": [1, 0], "mark_confidence": 0.99},
            {"selections": [1, 0], "mark_confidence": 0.10},  # will be rejected
            {"selections": [0, 1], "mark_confidence": 0.99},
        ]
        vectors = s.normalise_batch(records)
        # Only 2 of 3 pass
        assert len(vectors) == 2


# ---------------------------------------------------------------------------
# Audit & diagnostics
# ---------------------------------------------------------------------------

class TestAuditDiagnostics:
    def test_normalisation_log_as_dicts(self, screen):
        screen.normalise({"selections": [1, 0]})
        dicts = screen.normalisation_log_as_dicts()
        assert len(dicts) == 1
        assert "normalised_vector" in dicts[0]

    def test_clean_passthrough_count(self, screen):
        screen.normalise({"selections": [1, 0]})
        screen.normalise({"selections": [0, 1]})
        assert screen.clean_passthrough_count() == 2

    def test_acceptance_count(self, screen):
        screen.normalise({"selections": [1, 0]})
        screen.normalise({"selections": [0, 1]})
        assert screen.acceptance_count() == 2

    def test_rejection_count_after_error(self):
        s = HolographicScreen(min_confidence=0.99)
        try:
            s.normalise({"selections": [1], "mark_confidence": 0.10})
        except AdmissibilityError:
            pass
        # Rejection count stays 0 because AdmissibilityError bubbles up
        # (the rejected record isn't added to the log in normalise())
        assert s.acceptance_count() == 0

    def test_reset_log(self, screen):
        screen.normalise({"selections": [1, 0]})
        screen.reset_log()
        assert len(screen.normalisation_log) == 0
        assert screen._ballot_index == 0


# ---------------------------------------------------------------------------
# Integration: screen → county node
# ---------------------------------------------------------------------------

class TestScreenToCountyNode:
    def test_normalised_vector_can_be_ingested(self):
        from EIGE.src.county_node import CountyNode
        from EIGE.src.metric_closure import ClosureStatus

        s = HolographicScreen()
        node = CountyNode("WA-047", "King County")

        records = [
            {"selections": [1, 0, 1], "mark_confidence": 0.99},
            {"selections": [0, 1, 0], "mark_confidence": 0.85},
            {"selections": [{"value": 1, "confidence": 0.95}, 0, 1]},
        ]
        for raw in records:
            vec = s.normalise(raw)
            node.ingest_ballot(vec)

        assert node.ballot_count() == 3
        result = node.validate_closure()
        assert result.status == ClosureStatus.STABLE
