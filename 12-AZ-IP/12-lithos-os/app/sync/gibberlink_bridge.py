"""
LithosOS — Gibberlink Acoustic Bridge
"""
from __future__ import annotations
import hashlib
import hmac
import json
import base64
import time
from dataclasses import dataclass, field
from enum import Enum

class GibberMode(str, Enum):
    GREEN = "green"
    RED   = "red"
    BLUE  = "blue"

class PayloadType(str, Enum):
    SPECIMEN_ID    = "SID"
    SPECIMEN_DELTA = "SDT"
    QUERY          = "QRY"
    ANSWER         = "ANS"
    PING           = "PNG"

@dataclass
class GibberPayload:
    payload_type: PayloadType
    data: dict
    timestamp: float = field(default_factory=time.time)
    version: int = 1

    def encode(self) -> str:
        obj = {
            "t": self.payload_type.value,
            "d": self.data,
            "ts": self.timestamp,
            "v": self.version,
        }
        return base64.b64encode(json.dumps(obj).encode()).decode()

    @classmethod
    def decode(cls, encoded: str) -> "GibberPayload":
        obj = json.loads(base64.b64decode(encoded).decode())
        return cls(
            payload_type=PayloadType(obj["t"]),
            data=obj["d"],
            timestamp=obj.get("ts", 0.0),
            version=obj.get("v", 1),
        )

class AcousticAuth:
    def __init__(self, secret: str = ""):
        self._secret = secret.encode() if secret else b"lithos-default"

    def sign(self, payload: str) -> str:
        return hmac.new(self._secret, payload.encode(), hashlib.sha256).hexdigest()[:32]

    def verify(self, payload: str, signature: str) -> bool:
        expected = self.sign(payload)
        return hmac.compare_digest(expected, signature)

class GibberBridge:
    def __init__(self, secret: str = "", mode: GibberMode = GibberMode.GREEN, enabled: bool = False):
        self._auth = AcousticAuth(secret)
        self._mode = mode
        self._enabled = enabled

    def broadcast_specimen_id(self, name: str, confidence: float, mode: GibberMode | None = None) -> bool:
        payload = GibberPayload(
            payload_type=PayloadType.SPECIMEN_ID,
            data={"name": name, "confidence": confidence},
        )
        return self._send(payload, mode or self._mode)

    def _send(self, payload: GibberPayload, mode: GibberMode) -> bool:
        if not self._enabled:
            return False
        encoded = payload.encode()
        sig = self._auth.sign(encoded)
        return True

    def listen(self, encoded: str, signature: str) -> GibberPayload | None:
        if not self._auth.verify(encoded, signature):
            return None
        try:
            return GibberPayload.decode(encoded)
        except Exception:
            return None
