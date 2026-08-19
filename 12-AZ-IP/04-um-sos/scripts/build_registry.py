"""
build_registry.py — Build the UM-SOS preregistration registry.

Usage::
    python build_registry.py               # write predictions.json
    python build_registry.py --validate    # validate schema before writing
    python build_registry.py --dry-run     # validate only, no write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))

from src.core.um_sos_registry import write_registry_json, get_registry_entries  # type: ignore

# ---------------------------------------------------------------------------
# JSON Schema for a single registry entry
# ---------------------------------------------------------------------------
ENTRY_SCHEMA = {
    "type": "object",
    "required": ["pillar_id", "prediction", "status"],
    "properties": {
        "pillar_id": {"type": ["string", "integer"]},
        "prediction": {"type": "string", "minLength": 1},
        "status": {"type": "string", "enum": ["PASS", "TENSION", "PENDING", "FALSIFIED"]},
        "sha256": {"type": "string"},
    },
    "additionalProperties": True,
}

REGISTRY_SCHEMA = {
    "type": "array",
    "items": ENTRY_SCHEMA,
    "minItems": 1,
}


def validate_registry(data: list) -> list[str]:
    """Validate registry entries. Returns a list of error messages."""
    errors: list[str] = []
    try:
        import jsonschema  # type: ignore

        try:
            jsonschema.validate(data, REGISTRY_SCHEMA)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        return errors
    except ImportError:
        pass

    # Fallback: manual validation
    if not isinstance(data, list):
        errors.append("Registry must be a JSON array")
        return errors
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            errors.append(f"Entry {i}: must be an object")
            continue
        for req in ("pillar_id", "prediction", "status"):
            if req not in entry:
                errors.append(f"Entry {i}: missing required field '{req}'")
        status = entry.get("status", "")
        if status not in ("PASS", "TENSION", "PENDING", "FALSIFIED"):
            errors.append(f"Entry {i}: invalid status {status!r}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build UM-SOS registry JSON")
    parser.add_argument("--validate", action="store_true",
                        help="Validate schema before writing")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate only; do not write output file")
    parser.add_argument("--out", type=Path,
                        default=root / "10-UM-SOS" / "registry" / "predictions.json",
                        help="Output path")
    args = parser.parse_args()

    out: Path = args.out

    if args.validate or args.dry_run:
        print("Validating registry entries…")
        try:
            entries = get_registry_entries()  # type: ignore[attr-defined]
        except AttributeError:
            # Fallback: read the existing file if get_registry_entries isn't exposed
            if out.exists():
                entries = json.loads(out.read_text())
            else:
                print("No existing registry file to validate.", file=sys.stderr)
                sys.exit(1)

        errors = validate_registry(entries if isinstance(entries, list) else [])
        if errors:
            for err in errors:
                print(f"  ERROR: {err}", file=sys.stderr)
            print(f"{len(errors)} validation error(s) — aborting.", file=sys.stderr)
            sys.exit(1)
        print(f"✓ {len(entries)} entries pass validation")

    if not args.dry_run:
        write_registry_json(out)
        print(f"✓ Written: {out}")

