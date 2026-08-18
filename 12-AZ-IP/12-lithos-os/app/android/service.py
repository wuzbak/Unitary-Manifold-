"""
LithosOS — Android Background Service
"""
from __future__ import annotations
import os
import signal
from pathlib import Path

LITHIC_DIR = Path(__file__).parent.parent.parent

class LithosService:
    def __init__(self):
        self._pid_file = LITHIC_DIR / "data" / ".service.pid"

    def start(self) -> bool:
        import subprocess, sys
        try:
            proc = subprocess.Popen(
                [sys.executable, "-m", "lithic.app.main", "--no-launch"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            self._pid_file.parent.mkdir(parents=True, exist_ok=True)
            self._pid_file.write_text(str(proc.pid))
            return True
        except Exception:
            return False

    def stop(self) -> bool:
        if not self._pid_file.exists():
            return False
        try:
            pid = int(self._pid_file.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            self._pid_file.unlink(missing_ok=True)
            return True
        except Exception:
            return False

    def status(self) -> dict:
        if not self._pid_file.exists():
            return {"running": False, "pid": None}
        try:
            pid = int(self._pid_file.read_text().strip())
            os.kill(pid, 0)
            return {"running": True, "pid": pid}
        except Exception:
            return {"running": False, "pid": None}
