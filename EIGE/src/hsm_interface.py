# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/hsm_interface.py — Hardware Security Module Key Provider Interface
===========================================================================

Provides an abstract KeyProvider base class and two concrete implementations:

  SoftwareKeyProvider
      Deterministic key derivation from county_id via SHA-512.  Mirrors the
      existing CountyNode._derive_key() logic exactly so all existing tests
      remain green.  Safe for development, testing, and air-gapped offline
      environments.

  HSMKeyProvider
      Thin wrapper around a PKCS#11 session.  Loads the HMAC key material by
      label inside the HSM; the raw key bytes NEVER leave the hardware
      boundary.  The HSM computes the HMAC and returns only the signature.
      Requires python-pkcs11 (pip install python-pkcs11) and a PKCS#11
      provider library (e.g. SoftHSM2, AWS CloudHSM, Thales Luna).

  MockHSMKeyProvider
      In-memory HSM simulation for unit tests.  Accepts a pre-loaded key
      dict keyed by label and behaves identically to HSMKeyProvider without
      requiring a physical device or PKCS#11 library.

Wiring
------
CountyNode.__init__ accepts an optional ``key_provider`` argument::

    node = CountyNode("WA-047", "King County")                  # software mode
    node = CountyNode("WA-047", "King County",
                      key_provider=HSMKeyProvider(slot=0))      # production mode
    node = CountyNode("WA-047", "King County",
                      key_provider=MockHSMKeyProvider({...}))   # test mode

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import hmac as _hmac
import json
from abc import ABC, abstractmethod
from typing import Optional


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class KeyProvider(ABC):
    """Abstract HMAC key provider for CountyNode telemetry signing.

    Concrete implementations hide all key material from the application
    layer — only the HMAC signature is returned.
    """

    @abstractmethod
    def sign(self, message: bytes) -> bytes:
        """Compute HMAC-SHA512 of ``message`` using the stored key.

        Parameters
        ----------
        message : bytes
            The serialized payload to sign.

        Returns
        -------
        bytes
            64-byte HMAC-SHA512 digest.
        """

    def sign_dict(self, payload: dict) -> str:
        """Convenience: JSON-serialize ``payload`` and return a hex digest.

        Parameters
        ----------
        payload : dict
            Must not contain a key named ``"hmac_signature"`` — that field
            is excluded by convention before signing.

        Returns
        -------
        str
            128-character hex string of the HMAC-SHA512 signature.
        """
        signable = {k: v for k, v in payload.items() if k != "hmac_signature"}
        message = json.dumps(signable, sort_keys=True).encode("utf-8")
        return self.sign(message).hex()


# ---------------------------------------------------------------------------
# Software provider (default / testing)
# ---------------------------------------------------------------------------

class SoftwareKeyProvider(KeyProvider):
    """Deterministic key derivation from county_id — mirrors _derive_key().

    WARNING: The derived key is deterministic and based on a plaintext
    ``county_id``.  This is acceptable for development and offline testing
    only.  In production, replace with HSMKeyProvider.

    Parameters
    ----------
    county_id : str
        Machine identifier for the county, e.g. "WA-047".
    """

    def __init__(self, county_id: str) -> None:
        self._county_id = county_id
        self._key: bytes = self._derive(county_id)

    @staticmethod
    def _derive(county_id: str) -> bytes:
        """Derive a 64-byte key from county_id — matches CountyNode._derive_key()."""
        return hashlib.sha512(
            f"EIGE-v21-{county_id}-hmac-key-placeholder".encode("utf-8")
        ).digest()

    def sign(self, message: bytes) -> bytes:
        return _hmac.new(self._key, message, hashlib.sha512).digest()

    def __repr__(self) -> str:
        return f"SoftwareKeyProvider(county_id={self._county_id!r})"


# ---------------------------------------------------------------------------
# HSM provider (production)
# ---------------------------------------------------------------------------

class HSMKeyProvider(KeyProvider):
    """PKCS#11 HSM key provider.  Key bytes never leave the hardware boundary.

    All HMAC operations are delegated to the HSM via the PKCS#11 C_Sign
    mechanism (CKM_SHA512_HMAC).  Only the 64-byte signature is returned to
    the application layer.

    Parameters
    ----------
    slot : int
        PKCS#11 slot index (often 0 for a single-slot device).
    key_label : str
        Label of the HMAC key object inside the HSM.
    pin : str, optional
        User PIN for the HSM slot.  If not provided, the HSM must already
        have an authenticated session (e.g. via SO PIN or auto-login).
    lib_path : str, optional
        Path to the PKCS#11 shared library (``pkcs11-provider.so`` / ``.dll``).
        If not provided, the provider is resolved via the ``PKCS11_LIB_PATH``
        environment variable or the system default.

    Raises
    ------
    ImportError
        If ``python-pkcs11`` is not installed.
    RuntimeError
        If the HSM slot cannot be opened or the key label is not found.
    """

    def __init__(
        self,
        slot: int = 0,
        key_label: str = "",
        pin: Optional[str] = None,
        lib_path: Optional[str] = None,
    ) -> None:
        try:
            import pkcs11  # type: ignore[import]
            from pkcs11 import Mechanism  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "python-pkcs11 is required for HSMKeyProvider. "
                "Install it with: pip install python-pkcs11"
            ) from exc

        import os
        resolved_lib = lib_path or os.environ.get("PKCS11_LIB_PATH", "")
        if not resolved_lib:
            raise RuntimeError(
                "HSMKeyProvider: no PKCS#11 library path provided. "
                "Set PKCS11_LIB_PATH or pass lib_path=."
            )

        lib = pkcs11.lib(resolved_lib)
        token = list(lib.get_slots(token_present=True))[slot].get_token()
        session = token.open(user_pin=pin)
        keys = list(session.get_objects({pkcs11.Attribute.LABEL: key_label}))
        if not keys:
            raise RuntimeError(
                f"HSMKeyProvider: key label {key_label!r} not found in slot {slot}."
            )
        self._session = session
        self._key = keys[0]
        self._mechanism = Mechanism.SHA512_HMAC

    def sign(self, message: bytes) -> bytes:
        return bytes(self._key.sign(message, mechanism=self._mechanism))

    def __repr__(self) -> str:
        return "HSMKeyProvider(<hardware-bound>)"


# ---------------------------------------------------------------------------
# Mock HSM provider (unit tests)
# ---------------------------------------------------------------------------

class MockHSMKeyProvider(KeyProvider):
    """In-memory HSM simulation for unit tests.

    Accepts a pre-loaded key dict keyed by label and implements the same
    sign() interface as HSMKeyProvider without requiring a physical device
    or PKCS#11 library.

    Parameters
    ----------
    keys : dict[str, bytes], optional
        Mapping of label → raw key bytes.  If not provided, an empty store
        is used (sign() will raise KeyError if called without loading a key).
    active_label : str, optional
        Which key label to use for signing.  If not provided, the first
        loaded key is used.
    """

    def __init__(
        self,
        keys: Optional[dict] = None,
        active_label: Optional[str] = None,
    ) -> None:
        self._keys: dict = dict(keys or {})
        self._active_label = active_label or (next(iter(self._keys), None))

    def load_key(self, label: str, key_bytes: bytes) -> None:
        """Load a key into the mock HSM store."""
        self._keys[label] = key_bytes
        if self._active_label is None:
            self._active_label = label

    def sign(self, message: bytes) -> bytes:
        if not self._active_label or self._active_label not in self._keys:
            raise KeyError(
                f"MockHSMKeyProvider: active label {self._active_label!r} not loaded."
            )
        key = self._keys[self._active_label]
        return _hmac.new(key, message, hashlib.sha512).digest()

    def __repr__(self) -> str:
        labels = list(self._keys.keys())
        return f"MockHSMKeyProvider(labels={labels!r}, active={self._active_label!r})"
