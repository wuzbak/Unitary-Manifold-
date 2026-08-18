"""TerraOS — Android background service."""
from __future__ import annotations
import os
from pathlib import Path


class TerraService:
    SERVICE_NAME = "com.terra.os.TerraService"
    PID_FILE = Path.home() / ".terra" / "service.pid"

    def __init__(self):
        self._running = False

    def start(self) -> bool:
        if self._running:
            return False
        self._running = True
        self.PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.PID_FILE.write_text(str(os.getpid()))
        return True

    def stop(self) -> bool:
        if not self._running:
            return False
        self._running = False
        if self.PID_FILE.exists():
            self.PID_FILE.unlink()
        return True

    @property
    def is_running(self) -> bool:
        return self._running
