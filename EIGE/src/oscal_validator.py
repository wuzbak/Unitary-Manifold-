# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/oscal_validator.py — OSCAL 1.5.0 Dossier Schema Validator
====================================================================

Validates OSCAL 1.5.0 component-definition dossiers produced by EIGE
against the bundled JSON Schema (schemas/oscal-1.5.0-component-definition.json).

Primary entry point: ``validate_oscal_schema(dossier: dict) -> ValidationResult``

The validator is wired into ``FederalAuditor.receive_holon_zero_cert()``
as a pre-flight check so that every dossier emitted by the
SentinelLoadBalancer conforms to OSCAL 1.5.0 before being recorded.

NIST SP-800-53 R5 coverage enforced:
  - SI-7   Software and Information Integrity
  - SI-7(1) Integrity Checks
  - SI-7(6) Cryptographic Protection
  - AU-12  Audit Generation
  - AU-12(1) System-Wide Audit Trail

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError as _JSVError
    _HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    _HAS_JSONSCHEMA = False

# ---------------------------------------------------------------------------
# Schema path
# ---------------------------------------------------------------------------

_SCHEMA_PATH = (
    Path(__file__).parent.parent / "schemas" / "oscal-1.5.0-component-definition.json"
)


def _load_schema() -> dict:
    """Load the bundled OSCAL 1.5.0 JSON Schema from disk."""
    with open(_SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Result of an OSCAL dossier schema validation.

    Attributes
    ----------
    valid : bool
        True if the dossier conforms to the OSCAL 1.5.0 schema.
    errors : list[str]
        Human-readable list of validation error messages.  Empty when valid.
    schema_version : str
        Version string of the schema used for validation.
    dossier_uuid : str | None
        UUID extracted from the validated dossier, or None if extraction failed.
    """

    valid: bool
    errors: List[str] = field(default_factory=list)
    schema_version: str = "oscal-1.5.0"
    dossier_uuid: Optional[str] = None

    def __bool__(self) -> bool:
        return self.valid

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "schema_version": self.schema_version,
            "dossier_uuid": self.dossier_uuid,
        }


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class OSCALValidator:
    """Validates OSCAL 1.5.0 component-definition documents.

    Loads the bundled JSON Schema once on instantiation and reuses it
    for all subsequent ``validate()`` calls.

    Parameters
    ----------
    schema_path : Path | str | None
        Override path to the JSON Schema file.  Defaults to the bundled
        schema at ``EIGE/schemas/oscal-1.5.0-component-definition.json``.
    """

    def __init__(self, schema_path: Optional[Any] = None) -> None:
        path = Path(schema_path) if schema_path else _SCHEMA_PATH
        with open(path, encoding="utf-8") as fh:
            self._schema: dict = json.load(fh)
        if _HAS_JSONSCHEMA:
            self._validator = Draft7Validator(self._schema)
        else:
            self._validator = None  # type: ignore[assignment]

    def validate(self, dossier: dict) -> ValidationResult:
        """Validate ``dossier`` against the OSCAL 1.5.0 JSON Schema.

        Parameters
        ----------
        dossier : dict
            A parsed OSCAL component-definition dossier as a Python dict.

        Returns
        -------
        ValidationResult
        """
        # Extract UUID for reporting (best-effort, may be absent on bad input)
        dossier_uuid: Optional[str] = None
        try:
            dossier_uuid = dossier.get("component-definition", {}).get("uuid")
        except Exception:
            pass

        if not _HAS_JSONSCHEMA:
            # Fallback: lightweight structural check without jsonschema
            return self._lightweight_check(dossier, dossier_uuid)

        errors: List[str] = [
            f"{e.json_path}: {e.message}"
            for e in sorted(
                self._validator.iter_errors(dossier),
                key=lambda e: str(e.json_path),
            )
        ]
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            dossier_uuid=dossier_uuid,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _lightweight_check(dossier: dict, dossier_uuid: Optional[str]) -> ValidationResult:
        """Structural check used when jsonschema is not installed."""
        errors: List[str] = []
        if not isinstance(dossier, dict):
            errors.append("Root document must be a JSON object.")
            return ValidationResult(valid=False, errors=errors, dossier_uuid=dossier_uuid)

        cd = dossier.get("component-definition")
        if not isinstance(cd, dict):
            errors.append("Missing required field: component-definition")
            return ValidationResult(valid=False, errors=errors, dossier_uuid=dossier_uuid)

        for required_field in ("uuid", "metadata", "components"):
            if required_field not in cd:
                errors.append(f"component-definition: missing required field '{required_field}'")

        metadata = cd.get("metadata", {})
        if isinstance(metadata, dict):
            for mf in ("title", "last-modified", "version", "oscal-version"):
                if mf not in metadata:
                    errors.append(f"metadata: missing required field '{mf}'")
            oscal_ver = metadata.get("oscal-version", "")
            if isinstance(oscal_ver, str) and not oscal_ver.startswith("1.5."):
                errors.append(
                    f"metadata.oscal-version must start with '1.5.' (got {oscal_ver!r})"
                )

        components = cd.get("components", [])
        if not isinstance(components, list) or len(components) == 0:
            errors.append("component-definition.components must be a non-empty array")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            dossier_uuid=dossier_uuid,
        )


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def validate_oscal_schema(dossier: dict) -> ValidationResult:
    """Validate ``dossier`` against the bundled OSCAL 1.5.0 JSON Schema.

    This is the primary public entry point.  It creates a fresh
    :class:`OSCALValidator` on each call.  For repeated validation in a
    hot path, instantiate :class:`OSCALValidator` once and call
    ``validator.validate(dossier)`` directly.

    Parameters
    ----------
    dossier : dict
        Parsed OSCAL component-definition dossier.

    Returns
    -------
    ValidationResult
        ``.valid`` is True if the dossier conforms to the schema;
        ``.errors`` lists all constraint violations when invalid.
    """
    return OSCALValidator().validate(dossier)
