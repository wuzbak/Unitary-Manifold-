"""TerraOS — GibberLink acoustic bridge."""
from __future__ import annotations
import base64
import hashlib
import hmac
from enum import Enum


class PayloadType(Enum):
    PROFILE_UPDATE = "profile_update"
    WATER_ALERT = "water_alert"
    QUERY = "query"
    ANSWER = "answer"
    PING = "ping"


class GibberBridge:
    def __init__(self, enabled: bool = False, secret: str = "terra-default-secret"):
        self.enabled = enabled
        self.secret = secret.encode()

    def encode_payload(self, payload_type: PayloadType, data: dict) -> str:
        import json
        raw = json.dumps({"type": payload_type.value, "data": data}, separators=(",", ":"))
        return base64.b64encode(raw.encode()).decode()

    def decode_payload(self, encoded: str) -> dict:
        import json
        raw = base64.b64decode(encoded.encode()).decode()
        return json.loads(raw)

    def broadcast(self, payload_type: PayloadType, data: dict) -> bool:
        if not self.enabled:
            return False
        _ = self.encode_payload(payload_type, data)
        return True

    def broadcast_profile_update(self, profile_id: int, profile_name: str) -> bool:
        return self.broadcast(PayloadType.PROFILE_UPDATE, {"id": profile_id, "name": profile_name})

    def broadcast_water_alert(self, sample_name: str, issue: str) -> bool:
        return self.broadcast(PayloadType.WATER_ALERT, {"sample": sample_name, "issue": issue})


class AcousticAuth:
    def __init__(self, secret: str = "terra-acoustic-secret"):
        self._secret = secret.encode()

    def sign(self, message: str) -> str:
        sig = hmac.new(self._secret, message.encode(), hashlib.sha256).hexdigest()
        return sig

    def verify(self, message: str, signature: str) -> bool:
        expected = self.sign(message)
        return hmac.compare_digest(expected, signature)
