# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Versioned SM parameter synchronization ledger (DuckDB-first)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class LedgerRecord:
    sprint: str
    parameter: str
    value: float
    unit: str
    source: str
    note: str = ""
    recorded_at: Optional[str] = None

    def to_row(self) -> tuple:
        ts = self.recorded_at or _utc_now_iso()
        return (
            self.sprint,
            self.parameter,
            float(self.value),
            self.unit,
            self.source,
            self.note,
            ts,
        )


class SmParameterLedger:
    """Small DuckDB-backed ledger with strict schema and sprint querying."""

    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path))

    def _connect(self):
        import duckdb  # optional dependency by design

        return duckdb.connect(self.db_path)

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sm_parameter_ledger (
                    sprint VARCHAR NOT NULL,
                    parameter VARCHAR NOT NULL,
                    value DOUBLE NOT NULL,
                    unit VARCHAR NOT NULL,
                    source VARCHAR NOT NULL,
                    note VARCHAR NOT NULL,
                    recorded_at TIMESTAMP NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sm_parameter_ledger_sprint
                ON sm_parameter_ledger(sprint)
                """
            )

    def insert_many(self, records: Iterable[LedgerRecord]) -> int:
        rows = [r.to_row() for r in records]
        if not rows:
            return 0
        self.init_schema()
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO sm_parameter_ledger
                (sprint, parameter, value, unit, source, note, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def latest_by_sprint(self, sprint: str) -> List[Dict[str, object]]:
        self.init_schema()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT sprint, parameter, value, unit, source, note, recorded_at
                FROM sm_parameter_ledger
                WHERE sprint = ?
                ORDER BY recorded_at DESC, parameter ASC
                """,
                [sprint],
            ).fetchall()
        return [
            {
                "sprint": r[0],
                "parameter": r[1],
                "value": float(r[2]),
                "unit": r[3],
                "source": r[4],
                "note": r[5],
                "recorded_at": str(r[6]),
            }
            for r in rows
        ]

