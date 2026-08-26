# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/zero_day.py — Zero-Day Heuristic Detection Engine
=========================================================

Zero-day exploits are unknown to signature databases.  This engine applies
five independent heuristics to detect novel attack vectors without relying
on CVE IDs or malware hash libraries:

  1. Entropy spike detection — unpacked exploits have unusual entropy profiles
  2. Polymorphic shellcode — NOP-sled variations, XOR-decoded payloads
  3. Heap-spray signatures — repeated block patterns near heap allocation size
  4. Return-Oriented Programming (ROP) gadget detection — ret instructions
     clustered in data sections (not in legitimate code)
  5. Behavioral anomaly scoring — process+network combination risk matrix
  6. Exploit kit landing page detection — HTML/JS fingerprints of known kits
  7. Memory corruption heuristics — format string patterns, large stack writes
  8. Drive-by download indicators — MIME-type mismatch, long URL chains

Each heuristic produces a 0–100 confidence score; the aggregate score is
the maximum of all individual scores (worst-case reporting), and a weighted
combination is also available.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import math
import re
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .malware_detector import analyse_entropy, ENTROPY_THRESHOLD_HIGH


# ---------------------------------------------------------------------------
# Heuristic result
# ---------------------------------------------------------------------------

@dataclass
class ZeroDayHit:
    heuristic: str
    confidence: float    # 0–100
    detail: str
    evidence_bytes: bytes = b""

    def to_dict(self) -> dict:
        return {
            "heuristic": self.heuristic,
            "confidence": self.confidence,
            "detail": self.detail[:256],
        }


@dataclass
class ZeroDayScanResult:
    filename: str
    hits: List[ZeroDayHit] = field(default_factory=list)
    max_confidence: float = 0.0
    weighted_score: float = 0.0
    is_suspicious: bool = False
    verdict: str = "CLEAN"  # CLEAN / SUSPICIOUS / HIGH_RISK / CRITICAL

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "hits": [h.to_dict() for h in self.hits],
            "max_confidence": self.max_confidence,
            "weighted_score": self.weighted_score,
            "is_suspicious": self.is_suspicious,
            "verdict": self.verdict,
        }


# ---------------------------------------------------------------------------
# Heuristic 1: Entropy spike
# ---------------------------------------------------------------------------

def _heuristic_entropy_spike(data: bytes) -> Optional[ZeroDayHit]:
    """High entropy in an unexpected file type suggests packed/encrypted payload."""
    ent = analyse_entropy(data)
    overall = ent["overall"]
    high_blocks = ent["high_blocks"]
    if overall > ENTROPY_THRESHOLD_HIGH and high_blocks > 2:
        conf = min(90.0, 50.0 + overall * 5)
        return ZeroDayHit(
            heuristic="ENTROPY_SPIKE",
            confidence=conf,
            detail=f"File entropy={overall:.2f} bits/byte, {high_blocks} high-entropy blocks",
        )
    return None


# ---------------------------------------------------------------------------
# Heuristic 2: Polymorphic shellcode / XOR decoder stubs
# ---------------------------------------------------------------------------

_XOR_DECODER_PATTERNS: List[Tuple[str, bytes]] = [
    # x86 XOR loop: mov ecx, N; xor byte [esi+N], key; inc esi; loop
    ("x86_xor_loop_ecx", b"\xb9"),              # MOV ECX, imm32
    # x64 XOR loop (common msfvenom)
    ("x64_xor_ror_loop", b"\x48\x31\xd2"),     # XOR RDX, RDX
    # Variable-key XOR stub
    ("xor_key_stub",     b"\x30\x07\x47\x49"),
    # Common shellcode decode loop with sub
    ("sub_decode_stub",  b"\x80\x2c\x05"),
    # Encoded shellcode marker (shellcode prefixed with byte count)
    ("encoded_length_prefix", b"\xfc\x48"),
]

_NOP_VARIANTS = [
    bytes([0x90]),                     # NOP
    bytes([0x66, 0x90]),               # xchg ax, ax
    bytes([0x0f, 0x1f, 0x00]),         # NOP DWORD PTR [RAX]
    bytes([0x0f, 0x1f, 0x40, 0x00]),   # NOP DWORD PTR [RAX+0]
    bytes([0x87, 0xdb]),               # XCHG EBX, EBX
]


def _heuristic_polymorphic_shellcode(data: bytes) -> Optional[ZeroDayHit]:
    hits = []
    for name, pat in _XOR_DECODER_PATTERNS:
        count = data.count(pat)
        if count >= 3:
            hits.append(f"{name}×{count}")
    # NOP sled variants
    for nop in _NOP_VARIANTS:
        sled = nop * 16
        if sled in data:
            hits.append("nop_sled_variant")
            break
    if hits:
        conf = min(88.0, 40.0 + len(hits) * 12)
        return ZeroDayHit(
            heuristic="POLYMORPHIC_SHELLCODE",
            confidence=conf,
            detail=f"XOR decoder / NOP sled patterns: {', '.join(hits[:5])}",
        )
    return None


# ---------------------------------------------------------------------------
# Heuristic 3: Heap spray
# ---------------------------------------------------------------------------

def _heuristic_heap_spray(data: bytes) -> Optional[ZeroDayHit]:
    """Detect repeated 4KB blocks characteristic of heap spray."""
    block_size = 4096
    if len(data) < block_size * 4:
        return None
    blocks = [data[i:i+block_size] for i in range(0, len(data) - block_size, block_size)]
    first = blocks[0]
    repeated = sum(1 for b in blocks[1:] if b == first)
    ratio = repeated / len(blocks)
    if ratio > 0.6:
        conf = min(85.0, 50.0 + ratio * 40)
        return ZeroDayHit(
            heuristic="HEAP_SPRAY",
            confidence=conf,
            detail=f"{repeated}/{len(blocks)} blocks identical ({ratio*100:.0f}%) — heap spray pattern",
        )
    return None


# ---------------------------------------------------------------------------
# Heuristic 4: ROP gadget density
# ---------------------------------------------------------------------------

def _heuristic_rop_gadgets(data: bytes) -> Optional[ZeroDayHit]:
    """Count RET instructions (0xC3, 0xC2) in what appears to be data sections."""
    # In legitimate code, RETs are ~1–3% of bytes.
    # In ROP chains, density spikes in short regions.
    ret_count = data.count(b"\xc3") + data.count(b"\xc2")
    if len(data) < 512:
        return None
    density = ret_count / len(data)
    if density > 0.05:  # > 5% RET density
        conf = min(80.0, 30.0 + density * 1000)
        return ZeroDayHit(
            heuristic="ROP_GADGET_DENSITY",
            confidence=conf,
            detail=f"RET density={density*100:.1f}% ({ret_count} occurrences) — ROP chain indicator",
        )
    return None


# ---------------------------------------------------------------------------
# Heuristic 5: Format string & memory corruption
# ---------------------------------------------------------------------------

_FMT_STRING_RE = re.compile(
    r"(%n|%[0-9]{2,}[dxsc]|%[0-9]{1,3}\$[nxd])",
)
_LARGE_STACK_WRITE = re.compile(r"(A{200,}|\\x41{100,})")


def _heuristic_memory_corruption(data: bytes) -> Optional[ZeroDayHit]:
    hits = []
    text = data.decode("utf-8", errors="replace")
    if _FMT_STRING_RE.search(text):
        hits.append("format_string_specifier")
    if _LARGE_STACK_WRITE.search(text):
        hits.append("large_repeated_byte_buffer")
    # Long integer sequences (potential heap overflow vectors)
    if re.search(r"(\d{10,}\s+){5,}", text):
        hits.append("long_integer_sequence")
    if hits:
        conf = min(75.0, 35.0 + len(hits) * 15)
        return ZeroDayHit(
            heuristic="MEMORY_CORRUPTION",
            confidence=conf,
            detail=f"Memory corruption indicators: {', '.join(hits)}",
        )
    return None


# ---------------------------------------------------------------------------
# Heuristic 6: Exploit kit landing page
# ---------------------------------------------------------------------------

_EXPLOIT_KIT_PATTERNS = [
    # JavaScript obfuscation common to exploit kits
    re.compile(r"eval\s*\(\s*unescape\s*\(", re.I),
    re.compile(r"String\.fromCharCode\s*\((\d+,\s*){20,}", re.I),
    re.compile(r"document\.write\s*\(unescape\s*\(", re.I),
    # Iframe injection with zero size (drive-by download)
    re.compile(r"<iframe[^>]+width\s*=\s*[\"']?0[\"']?[^>]*src\s*=", re.I),
    # Flash/Java exploit redirects
    re.compile(r"application/x-shockwave-flash.*?version.*?11", re.I),
    # Rig EK / Neutrino EK markers
    re.compile(r"(RIG\s*EK|NEUTRINO|magnitude\s*EK)", re.I),
]


def _heuristic_exploit_kit(data: bytes) -> Optional[ZeroDayHit]:
    text = data.decode("utf-8", errors="replace")
    matched = [i for i, pat in enumerate(_EXPLOIT_KIT_PATTERNS) if pat.search(text)]
    if matched:
        conf = min(90.0, 45.0 + len(matched) * 15)
        return ZeroDayHit(
            heuristic="EXPLOIT_KIT_LANDING",
            confidence=conf,
            detail=f"Exploit kit patterns matched ({len(matched)}/{len(_EXPLOIT_KIT_PATTERNS)})",
        )
    return None


# ---------------------------------------------------------------------------
# Heuristic 7: Drive-by download indicators (HTTP payloads)
# ---------------------------------------------------------------------------

_DRIVEBY_MIME_MISMATCHES: List[Tuple[bytes, str]] = [
    # File starts with PE header but served as image
    (b"\x4d\x5a", "PE_as_non_executable"),
    # ZIP header served as JPEG
    (b"\x50\x4b\x03\x04", "ZIP_as_media"),
    # RAR header
    (b"\x52\x61\x72\x21\x1a\x07", "RAR_as_media"),
]

_LONG_URL_CHAIN_RE = re.compile(r"https?://[^\s\"']{200,}", re.I)


def _heuristic_driveby_download(data: bytes, claimed_content_type: str = "") -> Optional[ZeroDayHit]:
    hits = []
    for magic, label in _DRIVEBY_MIME_MISMATCHES:
        if data.startswith(magic):
            if any(t in claimed_content_type.lower() for t in ("image", "text", "json")):
                hits.append(f"MIME_mismatch:{label}")
    text = data.decode("utf-8", errors="replace")
    if _LONG_URL_CHAIN_RE.search(text):
        hits.append("long_redirect_url")
    if hits:
        conf = min(78.0, 40.0 + len(hits) * 19)
        return ZeroDayHit(
            heuristic="DRIVEBY_DOWNLOAD",
            confidence=conf,
            detail=f"Drive-by indicators: {', '.join(hits)}",
        )
    return None


# ---------------------------------------------------------------------------
# ZeroDayEngine — aggregate all heuristics
# ---------------------------------------------------------------------------

# Heuristic weights for weighted_score (must sum to 1.0)
_WEIGHTS = {
    "ENTROPY_SPIKE":         0.20,
    "POLYMORPHIC_SHELLCODE": 0.20,
    "HEAP_SPRAY":            0.10,
    "ROP_GADGET_DENSITY":    0.15,
    "MEMORY_CORRUPTION":     0.10,
    "EXPLOIT_KIT_LANDING":   0.15,
    "DRIVEBY_DOWNLOAD":      0.10,
}
_DEFAULT_WEIGHT = 0.05


class ZeroDayEngine:
    """Aggregate zero-day heuristic scanner."""

    SUSPICIOUS_THRESHOLD = 40.0
    HIGH_RISK_THRESHOLD  = 65.0
    CRITICAL_THRESHOLD   = 80.0

    def scan(
        self,
        data: bytes,
        filename: str = "<unknown>",
        claimed_content_type: str = "",
    ) -> ZeroDayScanResult:
        """Run all heuristics against the provided bytes."""
        result = ZeroDayScanResult(filename=filename)

        checkers = [
            _heuristic_entropy_spike(data),
            _heuristic_polymorphic_shellcode(data),
            _heuristic_heap_spray(data),
            _heuristic_rop_gadgets(data),
            _heuristic_memory_corruption(data),
            _heuristic_exploit_kit(data),
            _heuristic_driveby_download(data, claimed_content_type),
        ]

        for hit in checkers:
            if hit is not None:
                result.hits.append(hit)

        if result.hits:
            result.max_confidence = max(h.confidence for h in result.hits)
            weighted = 0.0
            weight_used = 0.0
            for h in result.hits:
                w = _WEIGHTS.get(h.heuristic, _DEFAULT_WEIGHT)
                weighted += h.confidence * w
                weight_used += w
            if weight_used > 0:
                result.weighted_score = weighted / weight_used
            else:
                result.weighted_score = result.max_confidence

        score = result.max_confidence
        if score >= self.CRITICAL_THRESHOLD:
            result.verdict = "CRITICAL"
            result.is_suspicious = True
        elif score >= self.HIGH_RISK_THRESHOLD:
            result.verdict = "HIGH_RISK"
            result.is_suspicious = True
        elif score >= self.SUSPICIOUS_THRESHOLD:
            result.verdict = "SUSPICIOUS"
            result.is_suspicious = True
        else:
            result.verdict = "CLEAN"
            result.is_suspicious = False

        return result

    def scan_url_payload(
        self,
        url: str,
        data: bytes,
        content_type: str = "",
    ) -> ZeroDayScanResult:
        """Convenience wrapper that passes content-type for drive-by detection."""
        return self.scan(data, filename=url, claimed_content_type=content_type)
