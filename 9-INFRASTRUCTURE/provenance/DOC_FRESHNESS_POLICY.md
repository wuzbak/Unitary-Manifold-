# Documentation Freshness Policy

## Purpose

Prevent contradictory top-level status statements by enforcing a canonical update order.

## Canonical-first update order

When **version**, **test totals**, or **major governance state** changes:

1. Update canonical sources first:
   - `docs/mas_tracker.yml`
   - `docs/WAVE_CHANGELOG.md`
   - `9-INFRASTRUCTURE/provenance/README.md`
2. Then update high-visibility derivative docs:
   - `README.md`
   - `STATUS.md`
   - `FALLIBILITY.md`
   - `2-REPRODUCIBILITY/VALIDATION_REPORT.md`
3. Finally update auxiliary docs that quote the same numbers.

## Historical/superseded marking rule

If a document preserves legacy snapshots, add a top-level note that it is historical and point readers to canonical current sources.

## Consistency gate (before merge)

- Badge links resolve.
- Provenance links resolve.
- Version/test/MAS statements are non-contradictory across canonical + high-visibility docs.

