"""
LithosOS — Delta Sync
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

TABLES = ["specimens", "minerals", "gemstones", "metals", "formulations"]

@dataclass
class SyncState:
    last_sync: str = ""
    records_updated: int = 0
    records_deleted: int = 0
    errors: list[str] = field(default_factory=list)
    completed: bool = False

    def as_dict(self) -> dict:
        return {
            "last_sync": self.last_sync,
            "records_updated": self.records_updated,
            "records_deleted": self.records_deleted,
            "errors": self.errors,
            "completed": self.completed,
        }

class DeltaSync:
    def __init__(self, db_path: Path, sync_url: str = ""):
        self._db_path = db_path
        self._sync_url = sync_url

    def get_state(self) -> SyncState:
        return SyncState(last_sync="", records_updated=0, records_deleted=0, errors=[], completed=True)

    def sync(self, since: str = "2000-01-01T00:00:00Z", tables: Optional[list[str]] = None) -> SyncState:
        state = SyncState(last_sync=since, completed=True)
        if not self._sync_url:
            state.errors.append("No sync URL configured")
            state.completed = False
        return state

    def export_manifest(self) -> dict:
        return {"tables": TABLES, "db_path": str(self._db_path)}

    def export_record(self, table: str, record_id: int) -> dict:
        return {"table": table, "id": record_id}
