"""TerraOS — Android permission declarations."""
from __future__ import annotations

TERRA_PERMISSIONS = [
    "android.permission.INTERNET",
    "android.permission.ACCESS_NETWORK_STATE",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.WAKE_LOCK",
    "android.permission.RECEIVE_BOOT_COMPLETED",
]

GPS_PERMISSIONS = [
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
]


class AndroidPermissions:
    def __init__(self):
        self._granted: set[str] = set()

    def request(self, permission: str) -> bool:
        if permission in TERRA_PERMISSIONS or permission in GPS_PERMISSIONS:
            self._granted.add(permission)
            return True
        return False

    def is_granted(self, permission: str) -> bool:
        return permission in self._granted

    def list_required(self) -> list[str]:
        return TERRA_PERMISSIONS + GPS_PERMISSIONS
