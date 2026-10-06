# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/tee_attestation.py — Trusted Execution Environment Attestation
========================================================================

SECURITY NOTICE (v22, red-team finding F4)
------------------------------------------
v21 silently fell back to a software mock signed with a fixed, published key
and presented SHA-512(quote) as the TDX/SEV "signature".  Neither was
attestation.  As of v22:

* The mock is never selected implicitly.  It requires ``allow_mock=True``
  (or ``EIGE_ALLOW_TEE_MOCK=1``) and refuses ``EIGE_MODE=production``.  Mock
  reports carry no signature and ``verification_status="MOCK_NOT_EVIDENCE"``.
* Hardware reports carry the raw quote/report bytes with
  ``verification_status="RAW_QUOTE_UNVERIFIED"``.  This module does NOT
  verify quotes: that requires validating the Intel DCAP (PCK → Intel SGX
  Root CA) or AMD (VCEK → ASK → ARK) certificate chain plus TCB/collateral
  checks, which must be done by an external verifier such as Intel's QVL or
  AMD's ``snpguest``.  :func:`verify_attestation_report` therefore always
  reports ``verified=False`` with the reason.

Implementations:

  SOFTWARE_MOCK
      Explicit opt-in development stub.  Measurement = SHA-512(nonce +
      platform string).  Not evidence of anything.

  TDX (Intel Trust Domain Extensions)
      Invokes the Intel TDX attestation SDK to obtain a genuine Quote.
      Requires an Intel TDX-capable host and the ``tdx-attest`` library.

  SEV-SNP (AMD Secure Encrypted Virtualization — Secure Nested Paging)
      Invokes the ``sev-guest`` ioctl to obtain an SNP attestation report.
      Requires an AMD EPYC Milan/Genoa host with SNP enabled in the BIOS
      and the ``sev-guest`` kernel module loaded.

Usage::

    report = get_attestation_report(nonce=b"election-cycle-2026")
    assert report.platform in ("TDX", "SEV-SNP", "SOFTWARE_MOCK")

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import os
import struct
from dataclasses import dataclass, field
from typing import Literal, Optional

from eige.config import require_non_production

# Platform type alias
Platform = Literal["TDX", "SEV-SNP", "SOFTWARE_MOCK"]


# ---------------------------------------------------------------------------
# Attestation report dataclass
# ---------------------------------------------------------------------------

@dataclass
class AttestationReport:
    """Portable TEE attestation report.

    Attributes
    ----------
    platform : str
        One of "TDX", "SEV-SNP", or "SOFTWARE_MOCK".
    measurement : bytes
        Platform-specific measurement of the TEE's memory/code image.
        For SOFTWARE_MOCK this is SHA-512(nonce + platform).
        For TDX this is the MRTD (Measurement Register TD).
        For SEV-SNP this is the MEASUREMENT field from the SNP report.
    nonce : bytes
        The nonce supplied by the caller, echoed back in the report for
        freshness verification.
    signature : bytes
        Platform-specific signature over (measurement || nonce).
        For SOFTWARE_MOCK, HMAC-SHA512 with a fixed test key.
        For TDX/SEV-SNP, the hardware-generated signature from the report.
    report_data : bytes
        The full raw report blob (empty for SOFTWARE_MOCK).
    """

    platform: str
    measurement: bytes
    nonce: bytes
    signature: bytes
    report_data: bytes = field(default_factory=bytes)
    verification_status: str = "RAW_QUOTE_UNVERIFIED"

    @property
    def verified(self) -> bool:
        """Always False: this module performs no quote/certificate-chain verification."""
        return False

    def is_mock(self) -> bool:
        """Return True if this is a software mock report (not hardware-attested)."""
        return self.platform == "SOFTWARE_MOCK"

    def verify_nonce(self, expected_nonce: bytes) -> bool:
        """Return True if the echoed nonce matches the expected value."""
        return self.nonce == expected_nonce

    def as_dict(self) -> dict:
        """Serialize to a JSON-safe dict (bytes fields hex-encoded)."""
        return {
            "platform": self.platform,
            "measurement": self.measurement.hex(),
            "nonce": self.nonce.hex(),
            "signature": self.signature.hex(),
            "report_data_len": len(self.report_data),
            "is_mock": self.is_mock(),
            "verified": self.verified,
            "verification_status": self.verification_status,
        }


# ---------------------------------------------------------------------------
# Software mock implementation
# ---------------------------------------------------------------------------

MOCK_ENV_VAR = "EIGE_ALLOW_TEE_MOCK"


class TEEUnavailable(RuntimeError):
    """No hardware TEE is available and the mock was not explicitly allowed."""


def _get_software_mock_report(nonce: bytes) -> AttestationReport:
    """Generate a SOFTWARE_MOCK report (development only, carries no signature)."""
    require_non_production("SOFTWARE_MOCK attestation")
    platform = b"SOFTWARE_MOCK"
    measurement = hashlib.sha512(nonce + platform).digest()
    return AttestationReport(
        platform="SOFTWARE_MOCK",
        measurement=measurement,
        nonce=nonce,
        signature=b"",
        report_data=b"",
        verification_status="MOCK_NOT_EVIDENCE",
    )


# ---------------------------------------------------------------------------
# Intel TDX implementation
# ---------------------------------------------------------------------------

def _get_tdx_report(nonce: bytes) -> AttestationReport:
    """Obtain an Intel TDX attestation quote.

    Requires:
      - An Intel TDX-capable processor
      - The ``tdx-attest`` Python package (pip install tdx-attest)
      - The TDX guest driver (``/dev/tdx_guest``) to be present

    Falls back to SOFTWARE_MOCK if the TDX device is not available.
    """
    try:
        import tdx_attest  # type: ignore[import]
    except ImportError:
        raise RuntimeError(
            "Intel TDX attestation requires the tdx-attest package. "
            "Install it with: pip install tdx-attest"
        )

    if not os.path.exists("/dev/tdx_guest"):
        raise RuntimeError(
            "Intel TDX guest device /dev/tdx_guest not found. "
            "Ensure the TDX guest driver is loaded and this process "
            "runs inside a TDX-protected virtual machine."
        )

    # Pad or truncate nonce to 64 bytes (TDX REPORTDATA size)
    report_data = (nonce + b"\x00" * 64)[:64]
    quote_bytes = tdx_attest.get_quote(report_data)

    # Extract MRTD (bytes 128–176 of the TDX Quote body) as the measurement
    measurement = quote_bytes[128:176] if len(quote_bytes) >= 176 else hashlib.sha512(quote_bytes).digest()
    # The quote's ECDSA signature is embedded in quote_bytes; it is NOT
    # verified here (see module notice).  No synthetic signature is produced.
    signature = b""

    return AttestationReport(
        platform="TDX",
        measurement=measurement,
        nonce=nonce,
        signature=signature,
        report_data=quote_bytes,
    )


# ---------------------------------------------------------------------------
# AMD SEV-SNP implementation
# ---------------------------------------------------------------------------

# SNP ioctl constants (from linux/sev-guest.h)
_SNP_GUEST_REQ_MSG_VERSION = 1
_SNP_IOCTL_BASE = 0x53
_SNP_GET_REPORT = 0
_SEV_GUEST_DEVICE = "/dev/sev-guest"
_SNP_REPORT_REQUEST_SIZE = 96   # struct snp_report_request
_SNP_REPORT_RESPONSE_SIZE = 4000  # struct snp_report_response (max)
_SNP_MEASUREMENT_OFFSET = 0x60  # MEASUREMENT field offset in SNP ATTESTATION_REPORT


def _get_sev_snp_report(nonce: bytes) -> AttestationReport:
    """Obtain an AMD SEV-SNP attestation report via the sev-guest ioctl.

    Requires:
      - An AMD EPYC Milan/Genoa processor with SEV-SNP enabled
      - The ``sev-guest`` kernel module (``/dev/sev-guest`` device present)
      - Root or CAP_SYS_ADMIN capability to open /dev/sev-guest

    Falls back with a RuntimeError if the device is not present.
    """
    import ctypes
    import fcntl

    if not os.path.exists(_SEV_GUEST_DEVICE):
        raise RuntimeError(
            f"AMD SEV-SNP device {_SEV_GUEST_DEVICE} not found. "
            "Ensure the sev-guest kernel module is loaded and this process "
            "runs inside an SEV-SNP protected VM."
        )

    # Build SNP_REPORT_REQ: 64-byte user_data + 4-byte vmpl + padding
    user_data = (nonce + b"\x00" * 64)[:64]
    vmpl = struct.pack("<I", 0)  # VMPL 0 (guest OS)
    padding = b"\x00" * (_SNP_REPORT_REQUEST_SIZE - 68)
    request_buf = ctypes.create_string_buffer(user_data + vmpl + padding)

    response_buf = ctypes.create_string_buffer(_SNP_REPORT_RESPONSE_SIZE)

    # Build ioctl command: _IOWR(base, nr, size)
    _IOC_WRITE = 1
    _IOC_READ = 2
    _IOC_NRBITS = 8
    _IOC_TYPEBITS = 8
    _IOC_SIZEBITS = 14
    _IOC_NRSHIFT = 0
    _IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
    _IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
    _IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

    buf_size = _SNP_REPORT_REQUEST_SIZE + _SNP_REPORT_RESPONSE_SIZE
    ioctl_cmd = (
        ((_IOC_READ | _IOC_WRITE) << _IOC_DIRSHIFT)
        | (_SNP_IOCTL_BASE << _IOC_TYPESHIFT)
        | (_SNP_GET_REPORT << _IOC_NRSHIFT)
        | (buf_size << _IOC_SIZESHIFT)
    )

    combined_buf = ctypes.create_string_buffer(
        bytes(request_buf) + bytes(response_buf)
    )

    with open(_SEV_GUEST_DEVICE, "rb") as fd:
        fcntl.ioctl(fd, ioctl_cmd, combined_buf)

    report_bytes = bytes(combined_buf)[_SNP_REPORT_REQUEST_SIZE:]
    # MEASUREMENT field is at offset 0x60 in the SNP ATTESTATION_REPORT struct
    measurement = report_bytes[_SNP_MEASUREMENT_OFFSET: _SNP_MEASUREMENT_OFFSET + 48]
    if len(measurement) < 48:
        measurement = hashlib.sha512(report_bytes).digest()

    # The report's VCEK signature is embedded in report_bytes; NOT verified here.
    signature = b""

    return AttestationReport(
        platform="SEV-SNP",
        measurement=measurement,
        nonce=nonce,
        signature=signature,
        report_data=report_bytes,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_attestation_report(
    nonce: bytes,
    prefer: Optional[Platform] = None,
    allow_mock: bool = False,
) -> AttestationReport:
    """Obtain a TEE attestation report for the current execution environment.

    Platform selection:
      1. ``prefer="TDX"`` or ``"SEV-SNP"``: attempt that platform; raise on failure.
      2. ``prefer="SOFTWARE_MOCK"``: return the mock, only if mock use is allowed.
      3. ``prefer=None``: try TDX, then SEV-SNP; fall back to the mock only if
         allowed, otherwise raise :class:`TEEUnavailable`.

    Mock use is allowed when ``allow_mock=True`` or ``EIGE_ALLOW_TEE_MOCK=1``,
    and never in production mode.  The returned report is NOT verified; see
    :func:`verify_attestation_report`.
    """
    mock_allowed = allow_mock or os.environ.get(MOCK_ENV_VAR, "") == "1"
    if prefer == "TDX":
        return _get_tdx_report(nonce)
    if prefer == "SEV-SNP":
        return _get_sev_snp_report(nonce)
    if prefer == "SOFTWARE_MOCK":
        if not mock_allowed:
            raise TEEUnavailable(f"SOFTWARE_MOCK requested without allow_mock=True or {MOCK_ENV_VAR}=1")
        return _get_software_mock_report(nonce)

    errors = []
    if os.path.exists("/dev/tdx_guest"):
        try:
            return _get_tdx_report(nonce)
        except Exception as exc:  # pragma: no cover - hardware path
            errors.append(f"TDX: {exc}")
    if os.path.exists(_SEV_GUEST_DEVICE):
        try:
            return _get_sev_snp_report(nonce)
        except Exception as exc:  # pragma: no cover - hardware path
            errors.append(f"SEV-SNP: {exc}")
    if mock_allowed:
        return _get_software_mock_report(nonce)
    raise TEEUnavailable("no hardware TEE available and mock not allowed" + (f" ({'; '.join(errors)})" if errors else ""))


@dataclass(frozen=True)
class AttestationVerification:
    verified: bool
    status: str
    reason: str


def verify_attestation_report(report: AttestationReport, expected_nonce: bytes) -> AttestationVerification:
    """Assess a report honestly.  Never returns ``verified=True`` (no chain verification exists here)."""
    if not report.verify_nonce(expected_nonce):
        return AttestationVerification(False, "NONCE_MISMATCH", "report does not echo the expected nonce")
    if report.is_mock():
        return AttestationVerification(False, "MOCK_NOT_EVIDENCE", "software mock; not hardware attestation")
    return AttestationVerification(
        False,
        "RAW_QUOTE_UNVERIFIED",
        "quote signature and certificate chain were not verified; use an external "
        "verifier (Intel DCAP QVL for TDX, AMD VCEK/ASK/ARK chain for SEV-SNP)",
    )
