"""TerraOS — Delta Sync."""
from __future__ import annotations
from pathlib import Path

TABLES = ["soil_profiles", "water_samples", "amendments", "contaminants"]


class DeltaSync:
    def __init__(self, db_path: Path | None = None, remote_url: str = ""):
        self.db_path = db_path
        self.remote_url = remote_url

    def sync_table(self, table: str, since_ts: str | None = None, batch_size: int = 50) -> int:
        if table not in TABLES:
            return 0
        if not self.db_path or not self.db_path.exists():
            return 0
        from terra.app.db.schema import get_conn
        with get_conn(self.db_path) as conn:
            if since_ts:
                rows = conn.execute(
                    f"SELECT id FROM {table} WHERE updated_at > ? LIMIT ?",
                    (since_ts, batch_size)
                ).fetchall()
            else:
                rows = conn.execute(
                    f"SELECT id FROM {table} LIMIT ?",
                    (batch_size,)
                ).fetchall()
            return len(rows)

    def status(self) -> dict:
        counts: dict[str, int] = {}
        if not self.db_path or not self.db_path.exists():
            return {"status": "no_db", "tables": counts}
        from terra.app.db.schema import get_conn
        with get_conn(self.db_path) as conn:
            for t in TABLES:
                try:
                    n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                    counts[t] = n
                except Exception:
                    counts[t] = 0
        return {"status": "ok", "tables": counts}
