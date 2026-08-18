"""
LithosOS — Android Permissions
"""
from __future__ import annotations
import os

class AndroidPermissions:
    def __init__(self):
        self._is_android = os.path.exists("/data/data/com.termux")
        self._is_kivy = False
        try:
            from android.permissions import request_permissions  # type: ignore
            self._is_kivy = True
        except ImportError:
            pass

    def request_all(self) -> bool:
        if not self._is_android:
            return True
        perms = ["CAMERA", "INTERNET", "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE"]
        if self._is_kivy:
            try:
                from android.permissions import request_permissions, Permission  # type: ignore
                request_permissions([getattr(Permission, p, p) for p in perms])
                return True
            except Exception:
                pass
        return self._termux_request(perms)

    def _termux_request(self, perms: list[str]) -> bool:
        import subprocess
        try:
            subprocess.run(["termux-open-url", ""], capture_output=True, timeout=2)
            return True
        except Exception:
            return False

    def has_camera(self) -> bool:
        return self._is_android

    def has_internet(self) -> bool:
        return True

    def has_storage(self) -> bool:
        return True
